import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase,visibleState} from './data.js';
import {buildOperations} from './operations.js';
import {metadata} from './neon-adapter.js';

globalThis.crypto??=webcrypto;
const supervisor={role:'SUPERVISOR',user:'VICTOR'};
const driver=pg=>{
 const sql=(strings,...values)=>{
  const text=strings.reduce((out,s,i)=>out+(i?'$'+i:'')+s,'');
  return {text,values,then(a,b){return pg.query(text,values).then(r=>r.rows).then(a,b);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{
  const result=[];for(const q of queries)result.push((await tx.query(q.text,q.values)).rows);return result;
 });
 return sql;
};
async function fixture(){
 const pg=new PGlite();
 await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
 await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
 await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('COLABORADOR QA','Pintor',150)");
 await pg.exec("INSERT INTO obras(unidade,nome) VALUES('SEBRAE','OBRA QA')");
 await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
 VALUES (1,1,'2026-10-30','VICTOR','Integral','Turno: Integral ||APROAR_META|| {"valor_ajuda_custo":11}'),
 (1,1,'2026-10-30','VICTOR','Integral','Extra independente ||APROAR_META|| {"extra_avulsa":true,"extra_obra_id":"1","extra_unidade":"SEBRAE"}')`);
 await pg.exec(`INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_extra,tipo_diaria,valor_adicional_noturno,custo_pago_definido_financeiro,apontado_por,apontado_em,custo_encargos_base)
 VALUES ('1','2026-10-30','1','VICTOR','Presente (Integral)',0,'Não',50,true,'VICTOR','2026-10-30T20:00:00Z',150),
 ('2','2026-10-30','1','VICTOR','Extra',75,'Meia diária',0,false,'VICTOR','2026-10-30T20:00:00Z',75)`);
 await pg.exec(`INSERT INTO servicos_apontamento(convocacao_id,obra_id,unidade_snapshot,obra_nome_snapshot,periodo,principal)
 VALUES ('1','1','SEBRAE','OBRA QA','Integral',true),('2','1','SEBRAE','OBRA QA','Integral',true)`);
 return {pg,sql:driver(pg)};
}

test('Correção da extra em 30/10 antes das 10h cancela valor sem excluir convocação, serviço ou apontamento',async()=>{
 const {pg,sql}=await fixture();
 try{
  const db=await readDatabase(sql),next=structuredClone(visibleState(db,supervisor));
  assert.equal(next.extras.length,1);
  next.extras[0].cancelada=true;
  next.extras[0].motivoCancelamento='Colaborador não fez extra nesse dia';
  const ops=buildOperations(db,next,supervisor,'2026-11-03T12:59:00Z');
  assert.equal(ops.some(x=>x.action==='delete'),false);
  assert.equal(ops.filter(x=>x.data?.acao==='LIBERACAO_FINANCEIRA_UTILIZADA').length,0);
  assert.equal(ops.filter(x=>x.data?.acao==='CANCELAMENTO_EXTRA_INDEVIDA').length,1);
  const requestId=webcrypto.randomUUID();
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[db.version,requestId,'VICTOR','qa-cancelamento',JSON.stringify(ops)]);
  const updated=await readDatabase(sql);
  assert.equal(updated.state.extras.length,0);
  assert.equal(updated.raw.convocacoes.length,2);
  assert.equal(updated.raw.apontamentos.length,2);
  assert.equal(updated.raw.servicos_apontamento.length,2);
  assert.equal(Number(updated.raw.apontamentos.find(a=>String(a.convocacao_id)==='2').valor_extra),0);
  const extraConv=updated.raw.convocacoes.find(c=>String(c.id)==='2');
  assert.equal(metadata(extraConv.observacao).meta.extra_cancelada,true);
  assert.equal(Number(metadata(extraConv.observacao).meta.extra_valor_original),75);
 }finally{await pg.close();}
});

test('Após 10h, cancelamento de extra continua exigindo autorização; omissão não apaga registros',async()=>{
 const {pg,sql}=await fixture();
 try{
  const db=await readDatabase(sql),next=structuredClone(visibleState(db,supervisor));
  const omitted=structuredClone(next);omitted.extras=[];
  assert.equal(buildOperations(db,omitted,supervisor,'2026-11-03T12:59:00Z').some(x=>x.action==='delete'),false);
  next.extras[0].cancelada=true;
  next.extras[0].motivoCancelamento='Colaborador não fez extra nesse dia';
  assert.throws(()=>buildOperations(db,next,supervisor,'2026-11-03T13:00:01Z'),/Prazo financeiro encerrado/);
  assert.equal((await pg.query('SELECT count(*)::int AS n FROM apontamentos')).rows[0].n,2);
 }finally{await pg.close();}
});

test('Ajuste do Financeiro não impede correção de passagem e noturno antes das 10h',async()=>{
 const {pg,sql}=await fixture();
 try{
  const db=await readDatabase(sql),next=structuredClone(visibleState(db,supervisor));
  assert.equal(next.apontamentos.length,1);
  next.apontamentos[0].itens[0].ajudaCusto=25;
  next.apontamentos[0].itens[0].noturno=90;
  const before=buildOperations(db,next,supervisor,'2026-11-03T12:59:00Z');
  assert.equal(before.some(x=>x.action==='delete'),false);
  const point=before.find(x=>x.table==='apontamentos'&&x.action==='update');
  assert.equal(Number(point?.data?.valor_adicional_noturno),90);
  const conv=before.find(x=>x.table==='convocacoes'&&x.action==='update');
  assert.equal(metadata(conv?.data?.observacao).meta.valor_ajuda_custo,25);
  assert.throws(()=>buildOperations(db,next,supervisor,'2026-11-03T13:00:01Z'),/Prazo financeiro encerrado/);
 }finally{await pg.close();}
});

test('Formulário de correção exige motivo e usa trava com prazo, não apenas financeAdjusted',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(ui,/motivoCancelamento:reason/);
 assert.match(ui,/isFinancialEditingLocked\(serviceDate,item\)/);
 assert.match(ui,/function isFinancialEditingLocked\(date,item\)/);
});
