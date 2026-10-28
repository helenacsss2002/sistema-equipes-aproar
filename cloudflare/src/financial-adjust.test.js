import test from 'node:test';
import assert from 'node:assert/strict';
import {validateFinancialPayload,buildFinancialOperations} from './financial-adjust.js';
import {metadata} from './neon-adapter.js';
import fs from 'node:fs';
import {PGlite} from '@electric-sql/pglite';

const payload=(changes=[{convocacaoId:'15',financeiro:120,noturno:0,acordo:10,ajudaCusto:11}])=>({requestId:'ffffffff-ffff-4fff-8fff-ffffffffffff',version:'a'.repeat(32),changes});
const row={convocacao_id:'15',apontamento_id:'40',colaborador_id:'30',data_servico:'2026-10-13',supervisor_responsavel:'VICTOR',status:'Presente (Integral)',acordo_atual:0,noturno_atual:0,has_sebrae:false,observacao:'Turno: Integral | Obs: Mantida ||APROAR_META|| '+JSON.stringify({outra_chave:'intacta',valor_ajuda_custo:3})};
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
  assert.equal(ops.length,4);
  assert.deepEqual(ops.map(o=>o.table),['apontamentos','auditoria','convocacoes','auditoria']);
  assert.equal(ops[1].data.acao,'LANCAMENTO_FINANCEIRO_ITEM');
  assert.equal(ops[1].data.contexto.tipo,'Bonificação / acordo');
  assert.equal(ops[1].data.contexto.valorNovo,10);
  assert.equal(ops[1].data.contexto.supervisorResponsavel,'VICTOR');
  assert.equal(ops[0].id,'40');
  assert.equal(ops[0].data.custo_pago,120);
  assert.equal(ops[0].data.valor_acordo,10);
  assert.equal(ops[0].data.custo_pago_definido_financeiro,true);
  assert.equal(ops[0].data.status,undefined);
  assert.equal(ops[2].id,'15');
  const parsed=metadata(ops[2].data.observacao);
  assert.equal(parsed.meta.outra_chave,'intacta');
  assert.equal(parsed.meta.valor_ajuda_custo,11);
  assert.equal(parsed.text,'Turno: Integral | Obs: Mantida');
  assert.equal(ops[3].data.usuario,'FINANCEIRO');
  assert.equal(ops[3].data.contexto.operacoes.length,3);
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

test('Financial delta applies atomically to the real fixture and replay does not duplicate audit',async()=>{
  const pg=new PGlite();
  try{
    await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
    await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
    await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('QA','Eletricista',241.74); INSERT INTO obras(unidade,nome) VALUES('FIEC','Teste');");
    await pg.exec("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,observacao) VALUES(1,1,'2026-10-13','VICTOR','Turno: Integral ||APROAR_META|| {\"outra_chave\":\"intacta\"}');");
    await pg.exec("INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,custo_pago) VALUES('1','2026-10-13','1','VICTOR','Presente (Integral)',120);");
    const version=(await pg.query('SELECT aproar_web_fingerprint() AS v')).rows[0].v;
    const changes=validateFinancialPayload(payload([{convocacaoId:'1',financeiro:130,noturno:0,acordo:25,ajudaCusto:11}])).changes;
    const current=(await pg.query("SELECT c.id::text AS convocacao_id,c.observacao,a.id::text AS apontamento_id,a.status,c.colaborador_id::text AS colaborador_id,c.data::text AS data_servico,c.engenheiro AS supervisor_responsavel,a.valor_acordo AS acordo_atual,a.valor_adicional_noturno AS noturno_atual,false AS has_sebrae FROM apontamentos a JOIN convocacoes c ON c.id::text=a.convocacao_id")).rows;
    const ops=buildFinancialOperations(changes,current,'FINANCEIRO');
    const rid=crypto.randomUUID(),params=[version,rid,'FINANCEIRO','stable-sha',JSON.stringify(ops)];
    const applied=await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb) AS result',params);
    assert.notEqual(applied.rows[0].result.version,version);
    const reread=(await pg.query("SELECT a.custo_pago,a.valor_acordo,a.custo_pago_definido_financeiro,c.observacao FROM apontamentos a JOIN convocacoes c ON c.id::text=a.convocacao_id")).rows[0];
    assert.equal(Number(reread.custo_pago),130);
    assert.equal(Number(reread.valor_acordo),25);
    assert.equal(reread.custo_pago_definido_financeiro,true);
    assert.equal(metadata(reread.observacao).meta.valor_ajuda_custo,11);
    assert.equal(metadata(reread.observacao).meta.outra_chave,'intacta');
    await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
    assert.equal((await pg.query('SELECT count(*)::int AS n FROM auditoria')).rows[0].n,2);
    assert.equal((await pg.query("SELECT count(*)::int AS n FROM auditoria WHERE acao='LANCAMENTO_FINANCEIRO_ITEM'")).rows[0].n,1,'Reenvio com mesmo requestId não duplica lançamentos');
    await assert.rejects(pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[version,crypto.randomUUID(),'FINANCEIRO','other',JSON.stringify(ops)]),/APROAR_STALE/);
  }finally{await pg.close();}
});
