import test from 'node:test';
import assert from 'node:assert/strict';
import {validateFinancialPayload,buildFinancialOperations} from './financial-adjust.js';
import {metadata} from './neon-adapter.js';

const payload=(changes=[{convocacaoId:'15',financeiro:120,noturno:0,acordo:10,ajudaCusto:11}])=>({requestId:'ffffffff-ffff-4fff-8fff-ffffffffffff',version:'a'.repeat(32),changes});
const row={convocacao_id:'15',apontamento_id:'40',status:'Presente (Integral)',noturno_atual:0,has_sebrae:false,observacao:'Turno: Integral | Obs: Mantida ||APROAR_META|| '+JSON.stringify({outra_chave:'intacta',valor_ajuda_custo:3})};
test('Financial update accepts editable amounts while rejecting extra fields or duplicates',()=>{
  const b=validateFinancialPayload(payload());assert.equal(b.changes[0].ajudaCusto,11);
  assert.throws(()=>validateFinancialPayload(payload([{...payload().changes[0],supervisor:'VICTOR'}])),/Campos financeiros/);
  assert.throws(()=>validateFinancialPayload(payload([payload().changes[0],payload().changes[0]])),/duplicado/);
  assert.throws(()=>validateFinancialPayload(payload([{...payload().changes[0],ajudaCusto:-1}])),/válidos/);
  assert.throws(()=>validateFinancialPayload({...payload(),version:'invalid'}),/versão/);
});
test('Atomic financial operations update only selected rows and preserve existing attendance metadata',()=>{
  const ch=validateFinancialPayload(payload()).changes;
  const ops=buildFinancialOperations(ch,[row],'FINANCEIRO','2026-10-13T12:00:00.000Z');
  assert.equal(ops.length,3);
  assert.deepEqual(ops.map(o=>o.table),['apontamentos','convocacoes','auditoria']);
  assert.equal(ops[0].id,'40');
  assert.equal(ops[0].data.custo_pago,120);
  assert.equal(ops[0].data.valor_acordo,10);
  assert.equal(ops[0].data.custo_pago_definido_financeiro,true);
  assert.equal(ops[0].data.status,undefined);
  assert.equal(ops[1].id,'15');
  const parsed=metadata(ops[1].data.observacao);
  assert.equal(parsed.meta.outra_chave,'intacta');
  assert.equal(parsed.meta.valor_ajuda_custo,11);
  assert.equal(parsed.text,'Turno: Integral | Obs: Mantida');
  assert.equal(ops[2].data.usuario,'FINANCEIRO');
  assert.equal(ops[2].data.contexto.operacoes.length,2);
});
test('Financial update forbids absent attendance, absence payments and SEBRAE-only night additions',()=>{
  const ch=validateFinancialPayload(payload()).changes;
  assert.throws(()=>buildFinancialOperations(ch,[],'FINANCEIRO'),/não encontrado/);
  assert.throws(()=>buildFinancialOperations(ch,[{...row,status:'Falta'}],'FINANCEIRO'),/falta ou atestado/);
  assert.throws(()=>buildFinancialOperations([{...ch[0],noturno:90}],[row],'FINANCEIRO'),/SEBRAE/);
  assert.doesNotThrow(()=>buildFinancialOperations([{...ch[0],noturno:90}],[{...row,has_sebrae:true}],'FINANCEIRO'));
});
test('Financial adjustment preserves preexisting noturno outside SEBRAE unless changed',()=>{
  const ch=validateFinancialPayload(payload()).changes;
  assert.doesNotThrow(()=>buildFinancialOperations([{...ch[0],noturno:90}],[{...row,noturno_atual:90}],'FINANCEIRO'));
});
