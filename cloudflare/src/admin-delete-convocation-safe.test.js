import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PGlite} from '@electric-sql/pglite';
import {webcrypto} from 'node:crypto';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const admin=app.slice(app.indexOf('  function renderAdminConv('),app.indexOf('  function relocateAdminPerson('));
const remover=app.slice(app.indexOf('  async function removeUnpointedAdminConvocation('),app.indexOf('  function renderApontamentoNormal(){'));

test('Exclusão individual usa a rota pontual, não /api/save nem a remoção de apontamentos',()=>{
 const start=admin.indexOf("$('#ae-delete').onclick=async()=>{");
 const end=admin.indexOf("$('#ae-form').onsubmit=",start);
 assert(start>0&&end>start,'A exclusão individual administrativa deve existir');
 const handler=admin.slice(start,end);
 assert.match(handler,/apForConv\(x\.c\.id\)\?\.itens\.some/);
 assert.match(handler,/await removeUnpointedAdminConvocation\(x\.c\.id,x\.id,\{editMode:true\}\)/);
 assert.doesNotMatch(handler,/removeConvPerson|saveData\(|state\.apontamentos\.splice/);
 assert.match(remover,/api\('\/api\/convocation-remove'/);
 assert.match(remover,/renderAdminConv\(true\)/);
});

test('Exclusão múltipla faz uma transação auditada por colaborador e avisa sobre falhas parciais',()=>{
 const start=admin.indexOf("$('#ae-delete-bulk').onclick=async()=>{");
 const end=admin.indexOf('};refresh();}',start);
 assert(start>0&&end>start);
 const block=admin.slice(start,end);
 assert.match(block,/if\(!\$\('#ae-confirm-bulk'\)\.checked\)/);
 assert.match(block,/selected\.find\(x=>apForConv\(x\.c\.id\)\?\.itens\.some/);
 assert.match(block,/for\(const x of selected\)/);
 assert.match(block,/skipConfirm:true,deferRender:true,silent:true/);
 assert.match(block,/if\(!result\)break/);
 assert.match(block,/completed\+' de '\+selected\.length/);
 assert.doesNotMatch(block,/saveData\(|removeConvPerson\(/);
});

test('Rota /api/convocation-remove restringe perfil e mantém apontamentos e serviços protegidos',()=>{
 const start=worker.indexOf("if(path==='/api/convocation-remove'&&request.method==='POST')");
 const end=worker.indexOf("if(path==='/api/unpointed-convocation-remove'",start);
 assert(start>0&&end>start);
 const route=worker.slice(start,end);
 assert.match(route,/session\.role!=='CONTROLADORIA'/);
 assert.match(route,/sameOrigin\(request\)/);
 assert.match(route,/has_point/);
 assert.match(route,/has_services/);
 assert.match(route,/has_conflict/);
 assert.match(route,/meta\.apontado_em/);
 assert.match(route,/acao:'REMOVER_INCLUSAO_SEM_APONTAMENTO'/);
 assert.match(route,/applyCatalogRegistration/);
 assert.match(route,/previous\.length/);
});

test('Remoção confirmada exclui só a convocação sem apontamento, preserva outra presença e o cadastro',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('COLABORADOR TESTE','Pintor',200)");
  await pg.exec("INSERT INTO obras(nome,unidade) VALUES('SERVICO QA','CENTRO')");
  await pg.exec("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,criado_por) VALUES (1,1,'2026-10-26','VICTOR','Integral','CONTROLADORIA'),(1,1,'2026-10-27','VICTOR','Integral','CONTROLADORIA')");
  await pg.exec("INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,apontado_por) VALUES('2','2026-10-27','1','VICTOR','Presente (Integral)','VICTOR')");
  const version=(await pg.query('SELECT aproar_web_fingerprint() AS version')).rows[0].version;
  const requestId=webcrypto.randomUUID();
  const ops=[
   {table:'convocacoes',action:'delete',id:'1'},
   {table:'auditoria',action:'insert',id:'audit:'+requestId,data:{
    entidade:'convocacoes',entidade_id:'1',acao:'REMOVER_INCLUSAO_SEM_APONTAMENTO',
    usuario:'CONTROLADORIA',ocorrido_em:'2026-10-28T15:00:00Z',contexto:{colaboradorId:'1'}
   }}
  ];
  for(let i=0;i<2;i++)await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[version,requestId,'CONTROLADORIA','digest',JSON.stringify(ops)]);
  assert.equal((await pg.query('SELECT COUNT(*)::int n FROM convocacoes')).rows[0].n,1);
  assert.equal((await pg.query("SELECT COUNT(*)::int n FROM apontamentos WHERE convocacao_id='2'")).rows[0].n,1);
  assert.equal((await pg.query('SELECT COUNT(*)::int n FROM colaboradores')).rows[0].n,1);
  assert.equal((await pg.query("SELECT COUNT(*)::int n FROM auditoria WHERE acao='REMOVER_INCLUSAO_SEM_APONTAMENTO'")).rows[0].n,1);
 }finally{await pg.close();}
});
