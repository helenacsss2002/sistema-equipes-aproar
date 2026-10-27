import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';

const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');

test('O X da Controladoria aparece por colaborador sem apontamento, nunca em ficha confirmada',()=>{
 const admin=ui.slice(ui.indexOf('  function renderApontamentoNormal(){'),ui.indexOf('  let serviceListSeq=',ui.indexOf('  function renderApontamentoNormal(){')));
 assert.match(admin,/class="admin-person-entry"/);
 assert.match(admin,/data-admin-remove-conv="/);
 assert.match(admin,/data-admin-remove-person="/);
 assert.match(admin,/\$\{!apontado\?/);
 assert.match(admin,/\?\.itens\.some\(i=>String\(i\.colaboradorId\)===String\(cid\)\)/);
 assert.match(admin,/button\.onclick=\(\)=>removeUnpointedAdminConvocation/);
 assert.match(admin,/class="admin-remove-unpointed"/);
 assert.match(admin,/type="button"/);
 assert.match(html,/#ap-equipe \.admin-remove-unpointed/);
 assert.match(html,/#ap-equipe \.admin-person-entry \.person-name \{padding-right:58px;/);
});

test('Remover acidental preserva rascunhos dos outros e verifica a confirmação antes de nova tentativa',()=>{
 const start=ui.indexOf('  async function removeUnpointedAdminConvocation('),end=ui.indexOf('  function renderApontamentoNormal(){',start);
 const code=ui.slice(start,end);
 assert(start>=0&&end>start);
 assert.match(code,/onlineSession\?\.role!=='CONTROLADORIA'/);
 assert.match(code,/apForConv\(convocationId\)\?\.itens\.some/);
 assert.match(code,/window\.confirm\(/);
 assert.match(code,/captureAdminApDrafts\(\)/);
 assert.match(code,/api\('\/api\/convocation-remove'/);
 assert.match(code,/api\('\/api\/save-status\?requestId='/);
 assert.match(code,/if\(saved\)onlineWritable=false/);
 assert.match(code,/adminApDrafts\.delete\(String\(convocationId\)\)/);
 assert.doesNotMatch(code,/state\.colaboradores\s*=/);
 assert.doesNotMatch(code,/saveData\(/);
 const preserve=ui.slice(ui.indexOf('  function captureAdminApDrafts(){'),start);
 assert.match(preserve,/\$\$\('#ap-equipe form\[data-admin-conv\]'\)/);
 assert.match(preserve,/readPersonRows\(ids,form\)/);
 assert.match(ui,/adminApDrafts\.get\(String\(conv\.id\)\)\?\.get\(String\(cid\)\)/);
});

test('Rota remove somente a convocação individual, com autorização, checagens e auditoria',()=>{
 const begin=worker.indexOf("if(path==='/api/convocation-remove'&&request.method==='POST')");
 const end=worker.indexOf("if(path==='/api/save'&&request.method==='POST')",begin);
 assert(begin>0&&end>begin);
 const route=worker.slice(begin,end);
 assert.match(route,/session\.role!=='CONTROLADORIA'/);
 assert.match(route,/!sameOrigin\(request\)/);
 assert.match(route,/!writes\(env\)/);
 assert.match(route,/colaborador_id::text AS colaborador_id/);
 assert.match(route,/has_point/);
 assert.match(route,/has_services/);
 assert.match(route,/has_conflict/);
 assert.match(route,/current\.custos_separados===true/);
 assert.match(route,/meta\.apontado_em/);
 assert.match(route,/current\.colaborador_id!==String\(body\.colaboradorId\)/);
 assert.match(route,/applyCatalogRegistration\(sql,body\.requestId,session\.user,digest/);
 assert.match(route,/table:'convocacoes',action:'delete',id:String\(body\.convocacaoId\)/);
 assert.match(route,/acao:'REMOVER_INCLUSAO_SEM_APONTAMENTO'/);
 assert.doesNotMatch(route,/table:'colaboradores'/);
 assert.doesNotMatch(route,/table:'apontamentos',action:'delete'/);
 assert.doesNotMatch(route,/readDatabase\(/);
});

test('Transação confirma somente um participante; outras convocações, colaborador e histórico permanecem',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('Carlos QA','Pintor',220),('Colega QA','Pintor',220); INSERT INTO obras(nome,unidade) VALUES('Obra QA','MUSEU');");
  await pg.exec("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao) VALUES(1,1,'2026-10-26','VICTOR','Integral','Turno: Integral'),(1,2,'2026-10-26','VICTOR','Integral','Turno: Integral');");
  await pg.exec("INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status) VALUES('2','2026-10-26','2','VICTOR','Presente (Integral)');");
  const version=(await pg.query('SELECT aproar_web_fingerprint() AS version')).rows[0].version;
  const requestId=webcrypto.randomUUID();
  const ops=[
   {table:'convocacoes',action:'delete',id:'1'},
   {table:'auditoria',action:'insert',id:'audit:'+requestId,data:{
     entidade:'convocacoes',entidade_id:'1',acao:'REMOVER_INCLUSAO_SEM_APONTAMENTO',
     usuario:'CONTROLADORIA',ocorrido_em:'2026-10-27T13:30:00Z',
     contexto:{colaboradorId:'1',motivo:'Inclusão acidental'}
   }}
  ];
  const params=[version,requestId,'CONTROLADORIA','hash',JSON.stringify(ops)];
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
  const counts=(await pg.query("SELECT (SELECT count(*)::int FROM colaboradores) colaboradores,(SELECT count(*)::int FROM convocacoes) convocacoes,(SELECT count(*)::int FROM apontamentos) apontamentos,(SELECT count(*)::int FROM auditoria WHERE acao='REMOVER_INCLUSAO_SEM_APONTAMENTO') auditorias")).rows[0];
  assert.deepEqual(counts,{colaboradores:2,convocacoes:1,apontamentos:1,auditorias:1});
  assert.equal(String((await pg.query('SELECT colaborador_id FROM convocacoes')).rows[0].colaborador_id),'2');
  assert.equal((await pg.query('SELECT colaborador_id FROM apontamentos')).rows[0].colaborador_id,'2');
 }finally{await pg.close();}
});
