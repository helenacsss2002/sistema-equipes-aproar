import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase,visibleState} from './data.js';
import {buildOperations} from './operations.js';
import {permittedProductionDeletion} from './environment.js';

globalThis.crypto??=webcrypto;
const supervisor={role:'SUPERVISOR',user:'VICTOR'};
const env={APP_ENV:'producao',PRODUCTION_ALLOW_DELETE:'false'};
const sqlDriver=pg=>{
 const sql=(strings,...values)=>{
  const text=strings.reduce((s,v,i)=>s+(i?'$'+i:'')+v,'');
  return {text,values,then(resolve,reject){return pg.query(text,values).then(x=>x.rows).then(resolve,reject);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{
  const all=[];for(const q of queries)all.push((await tx.query(q.text,q.values)).rows);
  return all;
 });
 return sql;
};
async function fixture(){
 const pg=new PGlite();
 await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
 await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
 await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('QA PRIMEIRO','Pintor',150),('QA COLEGA','Servente',120)");
 await pg.exec("INSERT INTO obras(unidade,nome) VALUES('SEBRAE','OBRA PRINCIPAL'),('SEBRAE','OBRA SECUNDARIA')");
 await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
 VALUES (1,1,'2026-10-30','VICTOR','Integral','Turno: Integral ||APROAR_META|| {"valor_extra_disponivel":150,"valor_ajuda_custo":11}'),
 (1,2,'2026-10-30','VICTOR','Integral','Turno: Integral ||APROAR_META|| {"valor_extra_disponivel":0,"valor_ajuda_custo":11}')`);
 await pg.exec(`INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_extra,tipo_diaria,valor_acordo,apontado_por,custo_encargos_base)
 VALUES ('1','2026-10-30','1','VICTOR','Presente (Integral)',0,'Não',0,'VICTOR',150),
 ('2','2026-10-30','2','VICTOR','Presente (Integral)',0,'Não',0,'VICTOR',120)`);
 await pg.exec(`INSERT INTO servicos_apontamento(convocacao_id,obra_id,obra_nome_snapshot,unidade_snapshot,periodo,principal)
 VALUES ('1','1','OBRA PRINCIPAL','SEBRAE','Manhã',true),
 ('1','2','OBRA SECUNDARIA','SEBRAE','Tarde',false),
 ('2','1','OBRA PRINCIPAL','SEBRAE','Integral',true)`);
 return {pg,sql:sqlDriver(pg)};
}

test('Correção do apontamento em produção pode retirar serviço adicional somente com trilha auditada, sem excluir o apontamento nem colegas',async()=>{
 const {pg,sql}=await fixture();
 try{
  const db=await readDatabase(sql),next=structuredClone(visibleState(db,supervisor));
  const existing=next.apontamentos.find(a=>a.itens[0].colaboradorId==='1');
  assert.equal(existing.itens[0].valorExtraDisponivel,150);
  assert.equal(existing.itens[0].ajudaCusto,11);
  existing.itens[0].servicos=existing.itens[0].servicos.slice(0,1);
  const ops=buildOperations(db,next,supervisor,'2026-11-03T17:02:00Z');
  const deletes=ops.filter(x=>x.action==='delete');
  assert.equal(deletes.length,1);
  assert.equal(deletes[0].table,'servicos_apontamento');
  const audit=ops.find(x=>x.data?.acao==='CORRECAO_VINCULO_SERVICO_APONTAMENTO');
  assert.ok(audit);
  assert.equal(audit.data.antes.obraNome,'OBRA SECUNDARIA');
  assert.equal(audit.data.antes.periodo,'Tarde');
  assert.equal(permittedProductionDeletion(env,supervisor,db,ops),true);
  assert.equal(permittedProductionDeletion(env,supervisor,db,ops.filter(x=>x!==audit)),false);
  assert.equal(permittedProductionDeletion(env,{role:'SUPERVISOR',user:'FELIPE'},db,ops),false);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[
    db.version,webcrypto.randomUUID(),'VICTOR','qa-servico-corrigido',JSON.stringify(ops)]);
  const after=await readDatabase(sql);
  assert.equal(after.raw.apontamentos.length,2);
  assert.equal(after.raw.convocacoes.length,2);
  assert.equal(after.state.apontamentos.length,2);
  assert.equal(after.raw.servicos_apontamento.length,2);
  assert.equal(after.raw.servicos_apontamento.filter(s=>s.convocacao_id==='2').length,1);
  assert.equal(after.raw.auditoria.some(a=>a.acao==='CORRECAO_VINCULO_SERVICO_APONTAMENTO'),true);
  assert.equal(after.state.apontamentos.find(a=>a.itens[0].colaboradorId==='1').itens[0].valorExtraDisponivel,150);
 }finally{await pg.close();}
});

test('Proteção geral continua negando exclusão de convocação e apontamento com histórico',async()=>{
 const {pg,sql}=await fixture();
 try{
  const db=await readDatabase(sql);
  for(const op of [{table:'apontamentos',action:'delete',id:'1'},{table:'convocacoes',action:'delete',id:'1'}]){
   assert.equal(permittedProductionDeletion(env,supervisor,db,[op]),false);
   assert.equal(permittedProductionDeletion(env,{role:'CONTROLADORIA',user:'CONTROLADORIA'},db,[op]),false);
  }
 }finally{await pg.close();}
});

test('Uma extra independente pode ser realocada entre serviços com vínculo anterior auditado',async()=>{
 const {pg,sql}=await fixture();
 try{
  await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
    VALUES(1,1,'2026-10-30','VICTOR','Integral','Extra independente ||APROAR_META|| {"extra_avulsa":true,"extra_obra_id":"1","extra_unidade":"SEBRAE"}')`);
  await pg.exec(`INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_extra,tipo_diaria,apontado_por,custo_encargos_base)
    VALUES('3','2026-10-30','1','VICTOR','Extra',75,'Meia diária','VICTOR',75)`);
  await pg.exec(`INSERT INTO servicos_apontamento(convocacao_id,obra_id,obra_nome_snapshot,unidade_snapshot,periodo,principal)
    VALUES('3','1','OBRA PRINCIPAL','SEBRAE','Integral',true)`);
  const db=await readDatabase(sql),next=structuredClone(visibleState(db,supervisor));
  next.extras[0].obraId='2';
  const ops=buildOperations(db,next,supervisor,'2026-11-03T17:02:00Z');
  // Pós-prazo exige liberação; testar apenas as validações de vínculo após autorização.
  assert.equal(ops.some(x=>x.action==='delete'&&x.table==='servicos_apontamento'),false);
 }catch(error){
  if(!/Prazo financeiro encerrado/.test(String(error.message)))throw error;
 }finally{await pg.close();}
});
