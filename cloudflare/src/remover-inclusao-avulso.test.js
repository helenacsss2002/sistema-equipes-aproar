import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PGlite} from '@electric-sql/pglite';
import {webcrypto} from 'node:crypto';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');

test('O apontamento mostra X tanto para inclusao pendente quanto para inclusao salva sem apontamento',()=>{
 const start=app.indexOf('function renderEquipeDia(){');
 const end=app.indexOf("let unitConvDate=",start);
 assert(start>=0&&end>start);
 const src=app.slice(start,end);
 assert.match(src,/for\(const \[id,entry\] of people\)/);
 assert.match(src,/dayPendingAdds\.has\(id\)/);
  assert(src.includes("if(!/^\\d+$/.test(String(c.id))"));
 assert.match(src,/apForConv\(c\.id\)\?\.itens/);
 assert.match(src,/button\.className='day-remove-pending day-remove-saved'/);
 assert.match(src,/dayPendingAdds\.set\(id/);
 assert.match(src,/removePendingDayAdd\(id,dayKey\)/);
 assert.match(src,/snapshotDayDraft\(\)/);
 assert.match(src,/api\('\/api\/unpointed-convocation-remove'/);
 assert.match(src,/\/api\/save-status\?requestId=/);
 assert.match(src,/window\.confirm\('Retirar '/);
 assert.match(src,/applyOnline\(await restoreOnlineSession\(\)\)/);
});

test('Servidor verifica autor, data, vinculos, concorrencia e confirma exclusao com requestId',()=>{
 const start=worker.indexOf("if(path==='/api/unpointed-convocation-remove'");
 const end=worker.indexOf("if(path==='/api/save'",start);
 assert(start>=0&&end>start);
 const route=worker.slice(start,end);
 assert.match(route,/session\.role==='SUPERVISOR'/);
 assert.match(route,/conv\.engenheiro!==session\.user/);
 assert.doesNotMatch(route,/conv\.criado_por!==session\.user/);
 assert.match(route,/String\(conv\.colaborador_id\)!==colaboradorId/);
 assert.match(route,/EXISTS\(SELECT 1 FROM apontamentos/);
 assert.match(route,/EXISTS\(SELECT 1 FROM servicos_apontamento/);
 assert.match(route,/EXISTS\(SELECT 1 FROM conflitos_convocacao/);
 assert.match(route,/if\(conv\.apontado\|\|conv\.servicos\|\|conv\.conflito\)/);
 assert.match(route,/aproar_web_fingerprint/);
 assert.match(route,/aproar_web_apply/);
 assert.match(route,/action:'delete',id/);
 assert.match(route,/REMOVER_INCLUSAO_SEM_APONTAMENTO/);
});

test('Banco exclui apenas convocacao apontamento ausente e registra auditoria com idempotencia',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('AVULSO QA','Pintor',200)");
  await pg.exec("INSERT INTO obras(nome,unidade) VALUES('OBRA QA','MUSEU')");
  await pg.exec("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,criado_por) VALUES(1,1,'2026-10-26','VICTOR','Integral','VICTOR')");
  const version=(await pg.query("SELECT aproar_web_fingerprint() version")).rows[0].version;
  const requestId=webcrypto.randomUUID();
  const ops=[
   {table:'convocacoes',action:'delete',id:'1'},
   {table:'auditoria',action:'insert',id:'audit:'+requestId,
    data:{entidade:'aproar-web',entidade_id:'1',acao:'REMOVER_INCLUSAO_SEM_APONTAMENTO',usuario:'VICTOR',
      ocorrido_em:'2026-10-27T13:40:00Z',contexto:{convocacaoId:'1'}}}
  ];
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',
   [version,requestId,'VICTOR','digest',JSON.stringify(ops)]);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',
   [version,requestId,'VICTOR','digest',JSON.stringify(ops)]);
  assert.equal((await pg.query('SELECT count(*)::int n FROM convocacoes')).rows[0].n,0);
  assert.equal((await pg.query('SELECT count(*)::int n FROM colaboradores')).rows[0].n,1);
  assert.equal((await pg.query('SELECT count(*)::int n FROM auditoria WHERE acao=$1',
   ['REMOVER_INCLUSAO_SEM_APONTAMENTO'])).rows[0].n,1);
 }finally{await pg.close();}
});
