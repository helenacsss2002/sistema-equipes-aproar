import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PGlite} from '@electric-sql/pglite';
import {metadata} from './neon-adapter.js';
import {readDatabase} from './data.js';
import {buildOperations} from './operations.js';
import {buildFinancialOperations} from './financial-adjust.js';
import {validateComplementConfirmation,buildComplementConfirmationOperations,hasValidComplementApproval,clearObsoleteApproval} from './financial-approval.js';

const time='2026-10-20T14:00:00Z';
const source={requestId:'ffffffff-ffff-4fff-8fff-ffffffffffff',version:'a'.repeat(32),
 convocacaoId:'1',financeiro:90,acordo:90,justificativa:'Complemento independente referente ao deslocamento.'};
const record={
 convocacao_id:'1',apontamento_id:'1',status:'Presente (Integral)',acordo_atual:90,acordo_convocacao:90,
 complemento_atual:0,complemento_convocacao:0,
 observacao:'Turno: Integral ||APROAR_META|| '+JSON.stringify({valor_ajuda_custo:11,periodo_principal:'Integral'})};
function driver(pg){
 const sql=(strings,...values)=>{const text=strings.reduce((t,s,i)=>t+(i?'$'+i:'')+s,'');return {
  text,values,then(a,b){return pg.query(text,values).then(r=>r.rows).then(a,b)}
 };};
 sql.transaction=queries=>pg.transaction(async tx=>{const rows=[];for(const q of queries)rows.push((await tx.query(q.text,q.values)).rows);return rows;});
 return sql;
}

test('Confirmação exige valores iguais, justificativa e identificador válido',()=>{
 assert.equal(validateComplementConfirmation(source).financeiro,90);
 assert.throws(()=>validateComplementConfirmation({...source,financeiro:80}),/iguais/);
 assert.throws(()=>validateComplementConfirmation({...source,justificativa:'curto'}),/Descreva/);
 assert.throws(()=>validateComplementConfirmation({...source,role:'FINANCEIRO'}),/inválida/);
 assert.throws(()=>validateComplementConfirmation({...source,convocacaoId:'2 OR 1=1'}),/Apontamento inválido/);
 assert.throws(()=>validateComplementConfirmation({...source,acordo:0}),/iguais/);
});
test('Apenas Financeiro pode aprovar, preservando o acordo e as observações',()=>{
 const body=validateComplementConfirmation(source);
 assert.throws(()=>buildComplementConfirmationOperations(body,record,'SUPERVISOR'),/Somente o Financeiro/);
 assert.throws(()=>buildComplementConfirmationOperations(body,{...record,acordo_atual:100},'FINANCEIRO'),/mudou/);
 assert.throws(()=>buildComplementConfirmationOperations(body,{...record,status:'Falta'},'FINANCEIRO'),/falta ou atestado/);
 const ops=buildComplementConfirmationOperations(body,record,'FINANCEIRO',time);
 assert.equal(ops.length,3);
 assert.deepEqual(ops.map(x=>x.table),['apontamentos','convocacoes','auditoria']);
 assert.equal(ops[0].data.custo_pago,90);
 assert.equal(ops[0].data.valor_acordo,undefined,'A confirmação não muda o acordo');
 assert.equal(ops[1].data.custo_pago,90);
 const parsed=metadata(ops[1].data.observacao);
 assert.equal(parsed.meta.valor_ajuda_custo,11);
 assert.equal(parsed.meta.aprovacao_complemento_igual_acordo.justificativa,source.justificativa);
 assert(hasValidComplementApproval(parsed.meta,90,90));
 assert(!hasValidComplementApproval(parsed.meta,100,100));
 assert.deepEqual(clearObsoleteApproval(parsed.meta,0,90).aprovacao_complemento_igual_acordo,undefined);
 assert.equal(ops[2].data.acao,'CONFIRMAR_COMPLEMENTO_DUPLICADO');
 assert.equal(ops[2].data.contexto.justificativa,source.justificativa);
});

test('Confirmar valores iguais grava um evento auditável e permite atualização posterior, sem reaprovação implícita',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('Pessoa QA','Servente',182.34); INSERT INTO obras(unidade,nome) VALUES('SEBRAE','Teste');");
  await pg.query("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,observacao,valor_acordo) VALUES(1,1,$1,$2,$3,90)",['2026-10-13','SOARES','Turno: Integral ||APROAR_META|| '+JSON.stringify({valor_ajuda_custo:11})]);
  await pg.exec("INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_acordo,custo_pago) VALUES('1','2026-10-13','1','SOARES','Presente (Integral)',90,0);");
  const sql=driver(pg),version=(await pg.query('SELECT aproar_web_fingerprint() AS version')).rows[0].version;
  const current=(await pg.query("SELECT c.id::text AS convocacao_id,c.observacao,c.custo_pago AS complemento_convocacao,c.valor_acordo AS acordo_convocacao,a.id::text AS apontamento_id,a.status,a.custo_pago AS complemento_atual,a.valor_acordo AS acordo_atual FROM convocacoes c JOIN apontamentos a ON a.convocacao_id=c.id::text")).rows[0];
  const body=validateComplementConfirmation({...source,version});
  const ops=buildComplementConfirmationOperations(body,current,'FINANCEIRO',time);
  const params=[version,body.requestId,'FINANCEIRO','sha',JSON.stringify(ops)];
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
  const check=(await pg.query("SELECT a.custo_pago,a.valor_acordo,a.custo_pago_definido_financeiro,c.observacao FROM apontamentos a JOIN convocacoes c ON c.id::text=a.convocacao_id")).rows[0];
  assert.equal(Number(check.custo_pago),90);
  assert.equal(Number(check.valor_acordo),90);
  assert.equal(check.custo_pago_definido_financeiro,true);
  assert(hasValidComplementApproval(metadata(check.observacao).meta,90,90));
  let db=await readDatabase(sql);
  const next=structuredClone(db.state);
  assert.equal(next.apontamentos[0].itens[0].confirmacaoComplemento.justificativa,source.justificativa);
  next.apontamentos[0].itens[0].noturno=50;
  assert.doesNotThrow(()=>buildOperations(db,next,{role:'FINANCEIRO',user:'FINANCEIRO'},time));
  next.apontamentos[0].itens[0].acordo=100;
  assert.doesNotThrow(()=>buildOperations(db,next,{role:'FINANCEIRO',user:'FINANCEIRO'},time),'Mudança que desfaz a igualdade é permitida e revoga aprovação');
  const finOps=buildFinancialOperations([{convocacaoId:'1',financeiro:90,acordo:90,noturno:0,ajudaCusto:11}],
   [{convocacao_id:'1',apontamento_id:'1',colaborador_id:'1',data_servico:'2026-10-13',supervisor_responsavel:'SOARES',status:'Presente (Integral)',acordo_atual:90,noturno_atual:0,has_sebrae:true,observacao:check.observacao}],
   'FINANCEIRO');
  assert.equal(finOps.length,3);
  assert.throws(()=>buildFinancialOperations([{convocacaoId:'1',financeiro:100,acordo:100,noturno:0,ajudaCusto:11}],
   [{convocacao_id:'1',apontamento_id:'1',colaborador_id:'1',data_servico:'2026-10-13',supervisor_responsavel:'SOARES',status:'Presente (Integral)',acordo_atual:90,noturno_atual:0,has_sebrae:true,observacao:check.observacao}],
   'FINANCEIRO'),/confirmação explícita/);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
  const audits=(await pg.query("SELECT acao,usuario,contexto FROM auditoria WHERE acao='CONFIRMAR_COMPLEMENTO_DUPLICADO'")).rows;
  assert.equal(audits.length,1,'Repetir a mesma requisição não cria aprovações extras');
  assert.equal(audits[0].usuario,'FINANCEIRO');
  assert.equal(audits[0].contexto.financeiro,90);
 }finally{await pg.close();}
});

test('Confirmação aparece na tela sem ser confundida com edição de pagamentos',()=>{
 const frontend=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const server=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
 assert.match(frontend,/id="financial-duplicate-review"/);
 assert.match(frontend,/confirm-finance-duplicate/);
 assert.match(frontend,/id="approve-reason-/);
 assert.match(frontend,/api\/financial-confirm-duplicate/);
 assert.match(server,/session.role!=='FINANCEIRO'/);
 assert.match(server,/buildComplementConfirmationOperations/);
});
