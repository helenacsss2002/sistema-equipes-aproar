import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase,visibleState} from './data.js';
import {buildOperations} from './operations.js';
import {metadata} from './neon-adapter.js';

globalThis.crypto??=webcrypto;
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const isolateStart=app.indexOf(' const isolateFinancialFields=item=>{');
const isolateEnd=app.indexOf(' const snapshotDayDraft=()=>{',isolateStart);
assert.ok(isolateStart>0&&isolateEnd>isolateStart);
const isolation=app.slice(isolateStart,isolateEnd);

function scopeFinancial(item,baseline,fields){
 const ctx={dayFinancialEdits:new Map([['1',new Set(fields)]]),savedItem:id=>id==='1'?baseline:null};
 vm.createContext(ctx);
 vm.runInContext(isolation+'\nglobalThis.isolateFinancialFields=isolateFinancialFields;',ctx);
 return ctx.isolateFinancialFields(structuredClone(item));
}

test('Extra previamente autorizada: UI preserva bonificações, passagens, noturno e complemento não editados',()=>{
 const saved={colaboradorId:'1',extra:'Não',valorExtraOriginal:0,valorExtraDisponivel:75,
  acordo:25,ajudaCusto:11,noturno:90,financeiro:50};
 const item={colaboradorId:'1',extra:'Não',valorExtraOriginal:0,valorExtraDisponivel:150,
  acordo:0,ajudaCusto:0,noturno:0,financeiro:0,
  extraLancamento:{enabled:true,extra:'Diária',valorExtraOriginal:150,obraId:'1'}};
 const result=scopeFinancial(item,saved,['Extra']);
 assert.equal(result.valorExtraDisponivel,150);
 assert.equal(result.acordo,25);
 assert.equal(result.ajudaCusto,11);
 assert.equal(result.noturno,90);
 assert.equal(result.financeiro,50);
 assert.ok(result.extraLancamento);
});

test('Ao editar outra coluna, UI não recria extra independente nem pede autorização nova de Extra',()=>{
 const saved={colaboradorId:'1',extra:'Meia diária',valorExtraOriginal:100,
  valorExtraDisponivel:75,acordo:25,ajudaCusto:11,noturno:0,financeiro:50};
 const item={colaboradorId:'1',extra:'Não',valorExtraOriginal:0,valorExtraDisponivel:200,
  acordo:25,ajudaCusto:22,noturno:0,financeiro:0,
  extraLancamento:{enabled:true,extra:'Meia diária',valorExtraOriginal:100,obraId:'1'}};
 const result=scopeFinancial(item,saved,['Passagem / ajuda de custo']);
 assert.equal(result.extra,'Meia diária');
 assert.equal(result.valorExtraOriginal,100);
 assert.equal(result.valorExtraDisponivel,75);
 assert.equal(result.ajudaCusto,22);
 assert.equal(result.financeiro,50);
 assert.equal(Object.hasOwn(result,'extraLancamento'),false);
 assert.match(app,/items\.filter\(item=>item\.extraLancamento&&typeof item\.extraLancamento\.enabled==='boolean'\)/);
});

test('Campos editados pelo supervisor são isolados e persistem no rascunho mesmo após F5',()=>{
 assert.match(app,/markFinancial\(card\.dataset\.person,event\.target\)/);
 assert.match(app,/dirtyFinancial:Object\.fromEntries/);
 assert.match(app,/dirtyFinancial:draft\.dirtyFinancial\|\|\{\}/);
 assert.match(app,/dirtyFinancial:stored\.dirtyFinancial\|\|null/);
 assert.match(app,/\.map\(isolateFinancialFields\)/);
 assert.match(app,/const legacyExtra=/);
});

const supervisor={role:'SUPERVISOR',user:'JOEL'};
const driver=pg=>{
 const sql=(strings,...values)=>{
  const text=strings.reduce((out,s,i)=>out+(i?'$'+i:'')+s,'');
  return {text,values,then(resolve,reject){return pg.query(text,values).then(r=>r.rows).then(resolve,reject);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{
  const out=[];for(const q of queries)out.push((await tx.query(q.text,q.values)).rows);
  return out;
 });
 return sql;
};

test('Autorização Extra já aprovada salva apenas Extra sem mudar valores financeiros históricos e só é consumida após gravar',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('COLABORADOR COM EXTRA','Pintor',150),('COLEGA PRESERVADO','Servente',120)");
  await pg.exec("INSERT INTO obras(unidade,nome) VALUES('CENTRO','OBRA TESTE')");
  await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
    VALUES(1,1,'2026-10-31','JOEL','Integral','Turno: Integral ||APROAR_META|| {"valor_extra_disponivel":75,"valor_ajuda_custo":11}'),
          (1,2,'2026-10-31','JOEL','Integral','Turno: Integral ||APROAR_META|| {"valor_extra_disponivel":0,"valor_ajuda_custo":0}')`);
  await pg.exec(`INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_extra,tipo_diaria,custo_pago,valor_acordo,valor_adicional_noturno,custo_pago_definido_financeiro,apontado_por,custo_encargos_base)
    VALUES('1','2026-10-31','1','JOEL','Presente (Integral)',0,'Não',50,25,90,true,'JOEL',150),
          ('2','2026-10-31','2','JOEL','Presente (Integral)',0,'Não',0,0,0,false,'JOEL',120)`);
  await pg.exec(`INSERT INTO servicos_apontamento(convocacao_id,obra_id,unidade_snapshot,obra_nome_snapshot,periodo,principal)
    VALUES('1','1','CENTRO','OBRA TESTE','Integral',true),('2','1','CENTRO','OBRA TESTE','Integral',true)`);
  const sql=driver(pg),db=await readDatabase(sql);
  const next=structuredClone(visibleState(db,supervisor));
  const person=next.apontamentos.find(a=>a.itens[0].colaboradorId==='1').itens[0];
  person.valorExtraDisponivel=150;
  const releaseId='11111111-2222-4333-8444-555555555555',ts='2026-11-03T18:20:00Z';
  db.releaseEvents=[
   {acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'JOEL',ocorrido_em:'2026-11-03T18:01:00Z',
    contexto:{requestId:releaseId,supervisor:'JOEL',colaboradorId:'1',dataServico:'2026-10-31',fields:['Extra'],reason:'Ajuste autorizado pelo financeiro'}},
   {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:'FINANCEIRO',ocorrido_em:'2026-11-03T18:02:00Z',contexto:{requestId:releaseId}}
  ];
  const ops=buildOperations(db,next,supervisor,ts);
  assert.equal(ops.filter(o=>o.data?.acao==='LIBERACAO_FINANCEIRA_UTILIZADA').length,1);
  assert.equal(ops.filter(o=>o.action==='delete').length,0);
  assert.equal(ops.filter(o=>o.table==='apontamentos'&&o.action==='update').length,1);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',
    [db.version,webcrypto.randomUUID(),'JOEL','qa-financeiro-autorizado',JSON.stringify(ops)]);
  const after=await readDatabase(sql);
  assert.equal(after.raw.apontamentos.length,2);
  assert.equal(after.raw.convocacoes.length,2);
  const persisted=after.raw.apontamentos.find(a=>a.convocacao_id==='1');
  assert.equal(Number(persisted.custo_pago),50);
  assert.equal(Number(persisted.valor_acordo),25);
  assert.equal(Number(persisted.valor_adicional_noturno),90);
  const conv=after.raw.convocacoes.find(c=>String(c.id)==='1');
  assert.equal(metadata(conv.observacao).meta.valor_extra_disponivel,150);
  assert.equal(metadata(conv.observacao).meta.valor_ajuda_custo,11);
  const colleague=after.raw.apontamentos.find(a=>a.convocacao_id==='2');
  assert.equal(Number(colleague.valor_extra),0);
  assert.equal((await pg.query("SELECT count(*)::int n FROM auditoria WHERE acao='LIBERACAO_FINANCEIRA_UTILIZADA'")).rows[0].n,1);
 }finally{await pg.close();}
});
