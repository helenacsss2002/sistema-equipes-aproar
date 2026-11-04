import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase,visibleState} from './data.js';
import {buildOperations} from './operations.js';

globalThis.crypto??=webcrypto;
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=app.indexOf('  function convocationRecordsConfirmed('),end=app.indexOf('  function retroactiveRecordsConfirmed(',start);
assert.ok(start>0&&end>start,'A verificação autoritativa da convocação precisa existir');
const verify=vm.runInNewContext(app.slice(start,end)+'\nconvocationRecordsConfirmed;');

const review={
 supervisor:'FELIPE',date:'2026-11-04',unit:'CENTRO',turno:'Integral',
 ids:['1','2','c-avulso-cleandro-20261104'],
 avulsos:[{id:'c-avulso-cleandro-20261104',nome:'Cleandro',funcao:'Servente',custo:182.34,avulso:'Sim'}]
};
function driver(pg){
 const sql=(strings,...args)=>{
  const query=strings.reduce((out,part,i)=>out+(i?'$'+i:'')+part,'');
  return {text:query,values:args,then(resolve,reject){return pg.query(query,args).then(r=>r.rows).then(resolve,reject);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{
  const results=[];for(const q of queries)results.push((await tx.query(q.text,q.values)).rows);return results;
 });
 return sql;
}
test('Uma convocação com colaboradores e Cleandro avulso é conferida no Neon após o commit, sem duplicar',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria,ativo,avulso) VALUES('ANA','Pedreiro',241.74,true,'Não'),('BRUNO','Servente',182.34,true,'Não'),('Cleandro','Servente',182.34,false,'Sim')");
  await pg.exec("INSERT INTO obras(nome,unidade) VALUES('OBRA CENTRO','CENTRO')");
  const sql=driver(pg),scope={role:'SUPERVISOR',user:'FELIPE'},db=await readDatabase(sql),next=structuredClone(visibleState(db,scope));
  next.colaboradores.push({id:review.ids[2],nome:'Cleandro',funcao:'Servente',custo:182.34,categoria:'Ajudante',avulso:'Sim'});
  next.convocacoes.push({id:'conv-qa-novo',supervisor:'FELIPE',dataServico:review.date,unidade:review.unit,
    obraId:'1',turno:'Integral',colaboradores:review.ids.slice(),origem:'normal',criadoEm:'2026-11-04T12:00:00Z'});
  assert.equal(verify(db.state,review),false,'Antes do commit não pode dar sucesso');
  const ops=buildOperations(db,next,scope,'2026-11-04T12:00:00Z');
  assert.equal(ops.filter(x=>x.table==='convocacoes'&&x.action==='insert').length,3);
  assert.equal(ops.filter(x=>x.table==='colaboradores'&&x.action==='insert').length,0,'Avulso não tem cadastro');
  const rid=webcrypto.randomUUID(),payload=JSON.stringify(ops);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[db.version,rid,'FELIPE','test-conv',payload]);
  const persisted=await readDatabase(sql);
  assert.equal(verify(persisted.state,review),true,'Confere equipe, data, unidade, turno e avulso');
  assert.equal(persisted.raw.colaboradores.length,3,'Histórico do Cleandro antigo preservado sem novo cadastro');
  assert.equal(persisted.raw.convocacoes.length,3);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[db.version,rid,'FELIPE','test-conv',payload]);
  assert.equal(Number((await pg.query('SELECT count(*) n FROM convocacoes')).rows[0].n),3,'Repetição do mesmo ID não duplica');
  const missing=structuredClone(persisted.state);
  missing.convocacoes=missing.convocacoes.filter(c=>!c.colaboradores.includes('2'));
  assert.equal(verify(missing,review),false,'Não confirmar equipe incompleta');
  assert.equal(verify(persisted.state,{...review,date:'2026-11-05'}),false);
  assert.equal(verify(persisted.state,{...review,unit:'UNIFOR'}),false);
  assert.equal(verify(persisted.state,{...review,turno:'Noite'}),false);
  assert.equal(verify(persisted.state,{...review,ids:[...review.ids,'99']}),false);
  assert.equal(verify(persisted.state,{...review,avulsos:[{...review.avulsos[0],nome:'OUTRO'}]}),false);
 }finally{await pg.close();}
});
test('Somente o botão montar outra convocação reconstrói o formulário, sem voltar ao portal',()=>{
 const from=app.indexOf("$('#unit-conv-final').onclick=()=>"),to=app.indexOf('  function operationalRows(',from);
 const handler=app.slice(from,to);
 assert.ok(from>0&&to>from);
 assert.match(handler,/confirmed=>convocationRecordsConfirmed\(confirmed,approved\)/);
 assert.match(handler,/reviewBox\.innerHTML='<div class="notice success/);
 assert.match(handler,/newButton\.onclick=\(\)=>\{if\(viewAtual==='convocacao'\)render\(\);\}/);
 assert.match(handler,/clearStoredDraft\(confirmedKey\)/);
 assert.doesNotMatch(handler,/unitConvDate='';/);
 assert.doesNotMatch(handler,/setView\('inicio'\)/);
 assert.match(handler,/Convocação não confirmada:/);
 const save=app.slice(app.indexOf('  function saveData('),app.indexOf('  async function submitComplementConfirmation('));
 assert.match(save,/const preserveConvocationForm=viewAtual==='convocacao'&&typeof onFailure==='function'/);
 assert.match(save,/onlineSaving=false;if\(!preserveRetroDraft&&!preserveConvocationForm\)render\(\)/);
 assert.ok(save.indexOf('!verifyPersisted(result.state)')<save.indexOf('applyOnline(result)'));
 assert.match(save,/if\(typeof onFailure==='function'\)onFailure\(message\)/);
});
