import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const begin=app.indexOf('  function temConfirmacaoSemConvocacao(');
const end=app.indexOf('  function previstasSemConvocacao(',begin);
assert(begin>=0&&end>begin,'Regra de pendências não encontrada');

function getPending(state,supervisor='FELIPE',start='2026-10-09',endDate='2026-10-09'){
  const ctx={
    state,
    SUPERVISORES:[supervisor],
    isoToday:()=> '2026-10-28',
    dateLocal:date=>new Date(date+'T12:00:00Z'),
    calendarISO:date=>date.toISOString().slice(0,10)
  };
  vm.createContext(ctx);
  vm.runInContext(app.slice(begin,end)+'\nglobalThis.calculate=diasSemConvocacao;',ctx);
  return ctx.calculate([supervisor],start,endDate);
}

test('Convocação registrada pela Controladoria para Felipe elimina falso dia sem convocação',()=>{
  const dataServico='2026-10-09';
  const state={
    unitOwners:{'SÃO GONÇALO DO AMARANTE':'FELIPE'},
    semConvocacoesUnidade:[],
    convocacoes:[{
      id:'1107',
      supervisor:'FELIPE',
      executor:'CONTROLADORIA',
      dataServico,
      unidade:'SÃO GONÇALO DO AMARANTE',
      colaboradores:['178']
    }]
  };
  assert.equal(getPending(state).length,0,
    'A responsabilidade da convocação é de Felipe mesmo que a Controladoria a tenha lançado');
});

test('Apontamento ou autor da convocação não cria segunda pendência de ausência',()=>{
  const state={
    unitOwners:{'SÃO GONÇALO DO AMARANTE':'FELIPE'},
    semConvocacoesUnidade:[],
    convocacoes:[
      {supervisor:'FELIPE',executor:'CONTROLADORIA',dataServico:'2026-10-09',unidade:'SÃO GONÇALO DO AMARANTE'},
      {supervisor:'FELIPE',executor:'FELIPE',dataServico:'2026-10-09',unidade:'SÃO GONÇALO DO AMARANTE'}
    ]
  };
  assert.equal(getPending(state).length,0);
  assert.match(app,/function completeConv\(c\)/,'Regra de apontamentos é independente da origem da convocação');
});

test('Data sem convocação ou justificativa continua pendente',()=>{
  const state={
    unitOwners:{'SÃO GONÇALO DO AMARANTE':'FELIPE'},
    semConvocacoesUnidade:[],
    convocacoes:[]
  };
  const p=getPending(state);
  assert.equal(p.length,1);
  assert.equal(p[0].dataServico,'2026-10-09');
  assert.equal(p[0].supervisor,'FELIPE');
});

test('Confirmação sem convocação continua justificando ausência de atividade',()=>{
  const date='2026-10-09';
  const state={
    unitOwners:{'SÃO GONÇALO DO AMARANTE':'FELIPE',CENTRO:'FELIPE'},
    semConvocacoesUnidade:[
      {supervisor:'FELIPE',unidade:'SÃO GONÇALO DO AMARANTE',dataServico:date}
    ],
    convocacoes:[]
  };
  assert.equal(getPending(state).length,1,'Confirmação parcial não justifica todas as unidades');
  state.semConvocacoesUnidade.push({supervisor:'FELIPE',unidade:'CENTRO',dataServico:date});
  assert.equal(getPending(state).length,0);
});

test('A data de 09/10 fica concluída sem alterar convocação, autoria, custos ou apontamentos',()=>{
  const body=app.slice(begin,end);
  assert.match(body,/c\.supervisor===supervisor&&c\.dataServico===date/);
  assert.doesNotMatch(body,/\(c\.executor\|\|c\.supervisor\)===supervisor/);
  assert.match(body,/temConfirmacaoSemConvocacao/);
});
