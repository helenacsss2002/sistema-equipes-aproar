import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const api=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const loader=fs.readFileSync(new URL('./data.js',import.meta.url),'utf8');
const begin=app.indexOf('  function temConfirmacaoSemConvocacao(');
const end=app.indexOf('  function previstasSemConvocacao(',begin);
assert(begin>=0&&end>begin);

function pending(state,supervisors=['FELIPE'],start='2026-09-29',endDate='2026-09-30'){
  const ctx={state,SUPERVISORES:supervisors,isoToday:()=> '2026-10-29',
    dateLocal:date=>new Date(date+'T12:00:00Z'),
    calendarISO:date=>date.toISOString().slice(0,10)};
  vm.createContext(ctx);
  vm.runInContext(app.slice(begin,end)+'\nglobalThis.pending=diasSemConvocacao;',ctx);
  return [...ctx.pending(supervisors,start,endDate)].map(x=>x.supervisor+'|'+x.dataServico);
}
const empty=()=>({convocacoes:[],semConvocacoesUnidade:[],dispensasPendenciaConvocacao:[],unitOwners:{'SÃO GONÇALO DO AMARANTE':'FELIPE'}});

test('sem dispensa as datas continuam pendentes como antes',()=>{
  assert.deepEqual(pending(empty()),['FELIPE|2026-09-29','FELIPE|2026-09-30']);
});
test('dispensa somente o supervisor e a data escolhidos',()=>{
  const state=empty();
  state.dispensasPendenciaConvocacao.push({supervisor:'FELIPE',dataServico:'2026-09-29',motivo:'Caso excepcional'});
  assert.deepEqual(pending(state),['FELIPE|2026-09-30']);
  assert.deepEqual(pending(state,['FELIPE','EDUARDO'],'2026-09-29','2026-09-29'),['EDUARDO|2026-09-29']);
});
test('reativar a pendencia restaura o calculo automatico',()=>{
  const state=empty();
  state.dispensasPendenciaConvocacao.push({supervisor:'FELIPE',dataServico:'2026-09-29'});
  assert.deepEqual(pending(state,['FELIPE'],'2026-09-29','2026-09-29'),[]);
  state.dispensasPendenciaConvocacao=[];
  assert.deepEqual(pending(state,['FELIPE'],'2026-09-29','2026-09-29'),['FELIPE|2026-09-29']);
});
test('convocacao e justificativa automatica continuam prevalecendo',()=>{
  const state=empty();
  state.convocacoes.push({supervisor:'FELIPE',dataServico:'2026-09-29',unidade:'SÃO GONÇALO DO AMARANTE'});
  state.semConvocacoesUnidade.push({supervisor:'FELIPE',dataServico:'2026-09-30',unidade:'SÃO GONÇALO DO AMARANTE'});
  assert.deepEqual(pending(state),[]);
});
test('interface de dispensa so aparece na Controladoria',()=>{
  assert.match(app,/function renderIndicatorManualPanel\(missing,inicio,fim\)\{\s*if\(perfilAtual!=='CONTROLADORIA'\)return '';/);
  assert.match(app,/renderIndicatorManualPanel\(missing,reportFilters\.inicio,reportFilters\.fim\)/);
  assert.match(app,/bindIndicatorManualPanel\(missing,reportFilters\.inicio,reportFilters\.fim\)/);
});
test('servidor exige perfil Controladoria, origem valida e grava auditoria',()=>{
  const start=api.indexOf("if(path==='/api/indicator-dismissal'");
  const end=api.indexOf('   // Remocao pontual e auditada',start);
  assert(start>=0&&end>start);
  const route=api.slice(start,end);
  assert.match(route,/session\.role!=='CONTROLADORIA'/);
  assert.match(route,/sameOrigin\(request\)/);
  assert.match(route,/writes\(env\)/);
  assert.match(route,/DISPENSAR_PENDENCIA_MANUAL/);
  assert.match(route,/REATIVAR_PENDENCIA_MANUAL/);
  assert.match(route,/applyCatalogRegistration/);
  assert.match(route,/aproar_web_settings/);
  assert.doesNotMatch(route,/action:'delete'/);
  assert.doesNotMatch(route,/table:'(?:convocacoes|apontamentos|servicos_apontamento)'/);
  assert.match(loader,/dispensasPendenciaConvocacao:Array\.isArray\(config\.dispensasPendenciaConvocacao\)/);
});
