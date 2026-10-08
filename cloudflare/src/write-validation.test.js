import test from 'node:test';
import assert from 'node:assert/strict';
import { isoDay, turnosSeSobrepoem, validateConvocacao, validateApontamento,
         apontamentoRetroativo, writeConfiguration, convocacaoAtrasada } from './write-validation.js';

test('rejects invalid and impossible dates',()=>{
  assert.equal(isoDay('2026-02-30'),false);
  assert.equal(isoDay('2026-10-09'),true);
  assert.equal(isoDay('09/10/2026'),false);
});
test('turnos: morning/afternoon coexist but integral overlaps',()=>{
  assert.equal(turnosSeSobrepoem('Manhã','Tarde'),false);
  assert.equal(turnosSeSobrepoem('Manhã','Manhã'),true);
  assert.equal(turnosSeSobrepoem('Manhã','Integral'),true);
  assert.equal(turnosSeSobrepoem('Noite','Tarde'),false);
});
test('convocation IDs and obligatory fields are validated',()=>{
  const p={obraId:1,colaboradorId:2,dataServico:'2026-10-09',engenheiro:'SUPERVISOR',turno:'Manhã'};
  assert.equal(validateConvocacao(p).ok,true);
  assert.equal(validateConvocacao({...p,colaboradorId:'1 OR 1=1'}).ok,false);
  assert.equal(validateConvocacao({...p,turno:'Qualquer'}).ok,false);
});
test('attendance refuses finance and unsupported multi-service payloads',()=>{
  assert.equal(validateApontamento({convocacaoId:7,status:'Falta'}).ok,true);
  assert.equal(validateApontamento({convocacaoId:7,status:'Falta',valorExtra:80}).ok,false);
  assert.equal(validateApontamento({convocacaoId:7,status:'Falta',servicos:[]}).ok,false);
});
test('Friday attendance is due Monday at 09:30 Fortaleza; weekends never late',()=>{
  assert.equal(apontamentoRetroativo('2026-10-09',new Date('2026-10-12T12:29:00Z')),false); // Monday 09:29
  assert.equal(apontamentoRetroativo('2026-10-09',new Date('2026-10-12T12:30:00Z')),true);
  assert.equal(apontamentoRetroativo('2026-10-10',new Date('2026-10-20T16:00:00Z')),false);
  assert.equal(apontamentoRetroativo('2026-10-12',new Date('2026-10-13T12:30:00Z')),true);
});
test('write gates fail closed: disabled or wrong host',()=>{
  const env={ENABLE_HOMOLOGATION_WRITES:'true',HOMOLOGATION_WRITE_TOKEN:'x'.repeat(40),DATABASE_URL:'postgresql://user:pass@ep-demo.sa-east-1.aws.neon.tech/db',HOMOLOGATION_EXPECTED_HOST:'ep-demo.sa-east-1.aws.neon.tech'};
  assert.equal(writeConfiguration(env).ok,true);
  assert.equal(writeConfiguration({...env,ENABLE_HOMOLOGATION_WRITES:'false'}).ok,false);
  assert.equal(writeConfiguration({...env,HOMOLOGATION_EXPECTED_HOST:'ep-main.sa-east-1.aws.neon.tech'}).ok,false);
  assert.equal(writeConfiguration({...env,HOMOLOGATION_WRITE_TOKEN:''}).ok,false);
});

test('late convocations: Friday after 16:00 for Monday; weekends ignored',()=>{
  assert.equal(convocacaoAtrasada('2026-10-12',new Date('2026-10-09T18:59:00Z')),false); // 15:59 Fortaleza
  assert.equal(convocacaoAtrasada('2026-10-12',new Date('2026-10-09T19:00:00Z')),true);
  assert.equal(convocacaoAtrasada('2026-10-12',new Date('2026-10-11T19:00:00Z')),false);
});
test('blank optional observations are supported',()=>{
  assert.equal(validateConvocacao({obraId:1,colaboradorId:2,dataServico:'2026-10-09',engenheiro:'X',turno:'Tarde',observacao:''}).ok,true);
  assert.equal(validateApontamento({convocacaoId:7,status:'Falta',observacao:''}).ok,true);
});

test('rejects reserved metadata delimiters and unsupported payload fields',()=>{
  const c={obraId:1,colaboradorId:2,dataServico:'2026-10-09',engenheiro:'SUPERVISOR',turno:'Manhã'};
  assert.equal(validateConvocacao({...c,observacao:'teste ||APROAR_META|| {}'}).ok,false);
  assert.equal(validateConvocacao({...c,custoPago:99}).ok,false);
  assert.equal(validateApontamento({convocacaoId:7,status:'Falta',custoPago:99}).ok,false);
});
