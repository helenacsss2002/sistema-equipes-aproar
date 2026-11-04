import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase,visibleState} from './data.js';
import {buildOperations} from './operations.js';
import {metadata} from './neon-adapter.js';

globalThis.crypto??=webcrypto;
const supervisor={role:'SUPERVISOR',user:'JOEL'};
function driver(pg){
 const sql=(strings,...vals)=>{
  const query=strings.reduce((acc,p,i)=>acc+(i?'$'+i:'')+p,'');
  return {text:query,values:vals,then(a,b){return pg.query(query,vals).then(r=>r.rows).then(a,b);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{
  const result=[];for(const q of queries)result.push((await tx.query(q.text,q.values)).rows);return result;
 });
 return sql;
}
async function fixture(){
 const pg=new PGlite();
 await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
 await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
 await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria,ativo,avulso) VALUES('Cleandro','Servente',182.34,false,'Sim'),('ANA CADASTRADA','Pedreiro',241.74,true,'Não')");
 await pg.exec("INSERT INTO obras(nome,unidade) VALUES('OBRA CENTRO','CENTRO'),('OBRA UNIFOR','UNIFOR')");
 return {pg,sql:driver(pg)};
}
const guest=(id,nome='Cleandro')=>({
 id,nome,funcao:'Servente',custo:182.34, categoria:'Ajudante',avulso:'Sim'
});
function addEvent(state,{id,date,unit='CENTRO',point=false,name='Cleandro'}){
 state.colaboradores.push(guest(id,name));
 const workId=unit==='CENTRO'?'1':'2';
 const cid='conv-'+id+'-'+date;
 state.convocacoes.push({id:cid,dataServico:date,unidade:unit,obraId:workId,
   supervisor:'JOEL',turno:'Integral',colaboradores:[id],origem:point?'retroativo':'normal'});
 if(point)state.apontamentos.push({id:'ap-'+cid,convocacaoId:cid,supervisor:'JOEL',
  dataServico:date,retroativo:true,itens:[{
   colaboradorId:id,status:'Presente (Integral)',extra:'Não',tipoDiariaAvulso:'Diária',
   valorExtraDisponivel:0,financeiro:0,noturno:0,acordo:0,ajudaCusto:11,
   servicos:[{obraId:workId,periodo:'Integral'}]
  }]});
}
test('Cleandro avulso entra manualmente na convocação sem novo cadastro, e não reaproveita o Cleandro inativo',async()=>{
 const {pg,sql}=await fixture();
 try{
  const db=await readDatabase(sql),next=structuredClone(visibleState(db,supervisor));
  addEvent(next,{id:'avulso-cleandro-11-04',date:'2026-11-04'});
  const ops=buildOperations(db,next,supervisor,'2026-11-04T17:00:00Z');
  assert.equal(ops.filter(x=>x.table==='colaboradores'&&x.action==='insert').length,0);
  const conv=ops.find(x=>x.table==='convocacoes'&&x.action==='insert');
  assert.equal(conv.data.colaborador_id,null);
  assert.equal(metadata(conv.data.observacao).meta.avulso_eventual.nome,'Cleandro');
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[
   db.version,webcrypto.randomUUID(),'JOEL','avulso-convocacao',JSON.stringify(ops)]);
  const after=await readDatabase(sql);
  assert.equal(after.raw.colaboradores.length,2);
  assert.equal(after.raw.colaboradores.find(x=>x.nome==='Cleandro').ativo,false);
  assert.equal(after.raw.convocacoes.length,1);
  assert.equal(after.raw.convocacoes[0].colaborador_id,null);
  const person=after.state.colaboradores.find(x=>x.id==='avulso-cleandro-11-04');
  assert.equal(person?.nome,'Cleandro');
  assert.equal(person?.avulsoRegistro,true);
  assert.equal(person?.custo,182.34);
  assert.equal(person?.inativo,true); // Não entra no catálogo permanente.
  assert.deepEqual(after.state.convocacoes[0].colaboradores,['avulso-cleandro-11-04']);
 }finally{await pg.close();}
});

test('Avulso de mesmo nome em outro dia é novo lançamento; retroativo registra custo sem cadastro',async()=>{
 const {pg,sql}=await fixture();
 try{
  let db=await readDatabase(sql),next=structuredClone(visibleState(db,supervisor));
  addEvent(next,{id:'avulso-cleandro-11-03',date:'2026-11-03',point:true});
  const ops=buildOperations(db,next,supervisor,'2026-11-04T17:00:00Z');
  assert.equal(ops.filter(x=>x.table==='colaboradores').length,0);
  assert.equal(ops.filter(x=>x.table==='apontamentos'&&x.action==='insert').length,1);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[
   db.version,webcrypto.randomUUID(),'JOEL','avulso-retro',JSON.stringify(ops)]);
  db=await readDatabase(sql);
  assert.equal(db.raw.colaboradores.length,2);
  assert.equal(db.raw.apontamentos.length,1);
  assert.equal(db.raw.apontamentos[0].colaborador_id,'avulso-cleandro-11-03');
  assert.equal(db.state.apontamentos[0].itens[0].tipoDiariaAvulso,'Diária');
  assert.equal(db.state.apontamentos[0].itens[0].ajudaCusto,11);
  assert.equal(Number(db.raw.apontamentos[0].custo_encargos_base),182.34);
  next=structuredClone(visibleState(db,supervisor));
  addEvent(next,{id:'avulso-cleandro-11-04',date:'2026-11-04',point:false});
  const nextOps=buildOperations(db,next,supervisor,'2026-11-04T17:00:00Z');
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[
   db.version,webcrypto.randomUUID(),'JOEL','avulso-outro-dia',JSON.stringify(nextOps)]);
  const after=await readDatabase(sql);
  assert.equal(after.raw.colaboradores.length,2);
  assert.equal(after.raw.convocacoes.length,2);
  assert.equal(after.state.colaboradores.filter(x=>x.nome==='Cleandro'&&x.avulsoRegistro).length,2);
  assert.equal(after.raw.apontamentos.length,1);
 }finally{await pg.close();}
});

test('Não criar ficha de avulso via cadastro e não duplicar mesmo nome no mesmo turno',async()=>{
 const {pg,sql}=await fixture();
 try{
  const db=await readDatabase(sql),state=structuredClone(visibleState(db,supervisor));
  state.colaboradores.push(guest('avulso-isolado'));
  assert.throws(()=>buildOperations(db,state,supervisor,'2026-11-04T17:00:00Z'),/só pode ser incluído manualmente/);
  state.colaboradores.pop();
  addEvent(state,{id:'avulso-a',date:'2026-11-04'});
  addEvent(state,{id:'avulso-b',date:'2026-11-04',unit:'UNIFOR'});
  assert.throws(()=>buildOperations(db,state,supervisor,'2026-11-04T17:00:00Z'),/mesmo dia e turno/);
 }finally{await pg.close();}
});

test('Botão X remove somente avulso ainda não confirmado e preserva rascunho',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(ui,/Adicionar pessoas que não estão na lista/);
 assert.match(ui,/data-remove-avulso/);
 assert.match(ui,/avulsoDraft=avulsoDraft\.filter\(x=>x\.id!==button\.dataset\.removeAvulso\)/);
 assert.match(ui,/avulsoList\(\);storeConvDraft\(\)/);
 assert.doesNotMatch(ui,/já está cadastrado\. Selecione esse nome na lista do retroativo/);
 assert.match(ui,/c\.avulso!=='Sim'&&!c\.avulsoRegistro/);
 assert.doesNotMatch(ui,/id="colab-avulso"/); // Cadastro não oferece opção de criar avulso permanente.
});

test('Esquema novo é aditivo e mantém a FK para colaboradores cadastrados',()=>{
 const sql=fs.readFileSync(new URL('../migracao_avulsos_eventuais_20261104.sql',import.meta.url),'utf8');
 assert.match(sql,/ALTER TABLE public\.convocacoes ALTER COLUMN colaborador_id DROP NOT NULL/);
 assert.doesNotMatch(sql,/DELETE FROM|DROP TABLE|TRUNCATE/i);
 const source=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');
 assert.match(source,/colaborador_id:isEventAvulso\(person\)\?null:pid/);
 assert.match(source,/avulso_eventual/);
});
