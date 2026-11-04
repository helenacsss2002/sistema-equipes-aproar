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
const beg=app.indexOf('  function retroactiveRecordsConfirmed(');
const end=app.indexOf('  function saveData(',beg);
assert.ok(beg>0&&end>beg);
const confirmed=vm.runInNewContext(app.slice(beg,end)+'\nretroactiveRecordsConfirmed;');
const scope={role:'SUPERVISOR',user:'JOEL'};
function sqlDriver(pg){
 const sql=(strings,...values)=>{
  const text=strings.reduce((out,chunk,index)=>out+(index?'$'+index:'')+chunk,'');
  return {text,values,then(resolve,reject){return pg.query(text,values).then(r=>r.rows).then(resolve,reject);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{
  const results=[];for(const q of queries)results.push((await tx.query(q.text,q.values)).rows);return results;
 });
 return sql;
}
const target={colaboradorId:'171',dataServico:'2026-11-02',unidade:'UNIFOR',
 supervisor:'JOEL',turno:'Integral',status:'Presente (Integral)',
 servicos:[{obraId:'1',periodo:'Integral'}],valorExtraDisponivel:0,acordo:0,ajudaCusto:0,noturno:0};
function newRetro(next){
 next.convocacoes.push({id:'retro-carlinhos-20261102',supervisor:'JOEL',dataServico:'2026-11-02',
  unidade:'UNIFOR',obraId:'1',turno:'Integral',colaboradores:['171'],origem:'retroativo'});
 next.apontamentos.push({id:'ap-retro-carlinhos-20261102',convocacaoId:'retro-carlinhos-20261102',
  supervisor:'JOEL',dataServico:'2026-11-02',retroativo:true,
  itens:[{colaboradorId:'171',status:'Presente (Integral)',extra:'Não',
   valorExtraDisponivel:0,financeiro:0,noturno:0,acordo:0,ajudaCusto:0,
   observacao:'Apontamento retroativo QA',servicos:[{obraId:'1',periodo:'Integral'}]}]});
}
test('Retroativo de Carlinhos em 02/11 sem convocação anterior grava apontamento e preserva 01/11',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(id,nome,funcao,valor_diaria) VALUES(171,'FRANCISCO CARLOS DE FREITAS DA SILVA (CARLINHOS)','Pedreiro',150),(172,'OUTRO COLEGA','Servente',120)");
  await pg.exec("INSERT INTO obras(nome,unidade) VALUES('OBRA UNIFOR','UNIFOR'),('OBRA CENTRO','CENTRO')");
  await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
    VALUES(1,171,'2026-11-01','JOEL','Integral','Turno: Integral'),
          (2,172,'2026-11-02','VICTOR','Integral','Turno: Integral')`);
  await pg.exec(`INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,tipo_diaria,apontado_por,retroativo,custo_encargos_base)
    VALUES('1','2026-11-01','171','JOEL','Presente (Integral)','Não','JOEL',false,150)`);
  await pg.exec(`INSERT INTO servicos_apontamento(convocacao_id,obra_id,unidade_snapshot,obra_nome_snapshot,periodo,principal)
    VALUES('1','1','UNIFOR','OBRA UNIFOR','Integral',true)`);
  const sql=sqlDriver(pg),db=await readDatabase(sql),next=structuredClone(visibleState(db,scope));
  assert.equal(confirmed(next,[target]),false);
  newRetro(next);
  const ops=buildOperations(db,next,scope,'2026-11-03T19:00:00Z');
  assert.equal(ops.filter(o=>o.table==='convocacoes'&&o.action==='insert').length,1);
  assert.equal(ops.filter(o=>o.table==='apontamentos'&&o.action==='insert').length,1);
  assert.equal(ops.some(o=>o.action==='delete'),false);
  const requestId=webcrypto.randomUUID();
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[
   db.version,requestId,'JOEL','qa-retro',JSON.stringify(ops)]);
  const after=await readDatabase(sql);
  assert.equal(confirmed(after.state,[target]),true);
  const points=after.state.apontamentos.filter(a=>a.itens.some(i=>i.colaboradorId==='171'));
  assert.equal(points.length,2);
  assert.deepEqual(points.map(p=>p.dataServico).sort(),['2026-11-01','2026-11-02']);
  assert.equal(points.find(p=>p.dataServico==='2026-11-02').retroativo,true);
  assert.equal(after.raw.convocacoes.filter(c=>String(c.colaborador_id)==='172').length,1);
  assert.equal((await pg.query('SELECT count(*)::int n FROM apontamentos')).rows[0].n,2);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[
   db.version,requestId,'JOEL','qa-retro',JSON.stringify(ops)]);
  assert.equal((await pg.query('SELECT count(*)::int n FROM apontamentos')).rows[0].n,2);
 }finally{await pg.close();}
});
test('Não confirmar redirecionamento quando falta Carlinhos, a data está errada ou o campo persistido difere',()=>{
 const state={convocacoes:[{id:'2228',supervisor:'JOEL',dataServico:'2026-11-01',
  unidade:'UNIFOR',turno:'Integral',colaboradores:['171']}],apontamentos:[{
  convocacaoId:'2228',dataServico:'2026-11-01',itens:[{colaboradorId:'171',
   status:'Presente (Integral)',servicos:[{obraId:'1',periodo:'Integral'}]}]}]};
 assert.equal(confirmed(state,[target]),false);
 const day={...state.convocacoes[0],id:'2229',dataServico:'2026-11-02'};
 state.convocacoes.push(day);
 state.apontamentos.push({...state.apontamentos[0],convocacaoId:'2229',dataServico:'2026-11-02'});
 assert.equal(confirmed(state,[target]),true);
 assert.equal(confirmed(state,[{...target,status:'Falta'}]),false);
 assert.equal(confirmed(state,[{...target,ajudaCusto:11}]),false);
 assert.equal(confirmed(state,[{...target,servicos:[{obraId:'2',periodo:'Integral'}]}]),false);
 assert.equal(confirmed(state,[target,{...target,colaboradorId:'999'}]),false);
});
test('A interface mantém o retroativo até confirmação de Neon; nunca mostra sucesso antes do POST',()=>{
 const begin=app.indexOf("$('#form-retro').onsubmit");
 const finish=app.indexOf('  function renderExtras()',begin);
 const handler=app.slice(begin,finish);
 assert.match(handler,/storeRetroDraft\(\)/);
 assert.match(handler,/const expected=itens\.map/);
 assert.match(handler,/saveData\(\(\)=>\{/);
 assert.match(handler,/confirmed=>retroactiveRecordsConfirmed\(confirmed,expected\)/);
 assert.match(handler,/clearStoredDraft\(retroKey\)/);
 assert.match(handler,/setView\('pendencias'\)/);
 assert.doesNotMatch(handler,/;toast\(savedMessage\)/);
 assert.ok(handler.indexOf("clearStoredDraft(retroKey)")>handler.indexOf("saveData(()=>"));
 const save=app.slice(app.indexOf('  function saveData('),app.indexOf('  async function submitComplementConfirmation('));
 assert.match(save,/!verifyPersisted\(result\.state\)/);
 assert.ok(save.indexOf('!verifyPersisted(result.state)')<save.indexOf('applyOnline(result)'));
 assert.match(save,/if\(typeof onFailure==='function'\)onFailure\(message\)/);
 assert.match(save,/if\(!preserveRetroDraft&&!preserveConvocationForm\)render\(\)/);
});
