import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
function helper(start,end){
 const a=js.indexOf(start),b=js.indexOf(end,a+start.length);
 assert(a>=0&&b>a,'Funções de convocação não encontradas');
 return js.slice(a,b);
}
test('Tomorrow default uses next calendar day, including Saturdays',()=>{
 const start=js.indexOf('  function tomorrowISO()'),end=js.indexOf('\n',start);
 assert(start>=0&&end>start);
 const ctx={isoToday:()=> '2026-10-16',dateLocal:iso=>new Date(iso+'T12:00:00Z'),calendarISO:d=>d.toISOString().slice(0,10)};
 vm.runInNewContext(js.slice(start,end)+'\nglobalThis.getTomorrow=tomorrowISO;',ctx);
 assert.equal(ctx.getTomorrow(),'2026-10-17');
 ctx.isoToday=()=> '2026-10-17';assert.equal(ctx.getTomorrow(),'2026-10-18');
 assert.match(js,/let adminConvDate=tomorrowISO\(\)/);
 assert.match(js,/id="wp-data"[^\n]*value="\$\{tomorrowISO\(\)\}"/);
});
test('Justified unit-day does not appear in missing convocations for responsible supervisor',()=>{
 const ctx={state:{convocacoes:[],semConvocacoesUnidade:[],unitOwners:{FIEC:'JOEL'}},
  isoToday:()=> '2026-10-16',SUPERVISORES:['JOEL'],
  dateLocal:iso=>new Date(iso+'T12:00:00Z'),calendarISO:d=>d.toISOString().slice(0,10)};
 vm.createContext(ctx);
 vm.runInContext(helper('  function temConfirmacaoSemConvocacao(','  function previstasSemConvocacao()')+'\nglobalThis.missing=diasSemConvocacao;',ctx);
 const missing=()=>ctx.missing(['JOEL'],'2026-10-15','2026-10-15');
 assert.equal(missing().length,1);
 ctx.state.semConvocacoesUnidade.push({supervisor:'JOEL',unidade:'FIEC',dataServico:'2026-10-15'});
 assert.equal(missing().length,0);
 ctx.state.unitOwners.SEBRAE='JOEL';
 assert.equal(missing().length,1,'Outro local sob responsabilidade continua pendente');
 ctx.state.semConvocacoesUnidade.push({supervisor:'JOEL',unidade:'SEBRAE',dataServico:'2026-10-15'});
 assert.equal(missing().length,0);
 ctx.state.semConvocacoesUnidade=[];
 ctx.state.convocacoes.push({supervisor:'JOEL',dataServico:'2026-10-15',unidade:'FIEC',executor:'JOEL'});
 assert.equal(missing().length,0,'Convocação real continua contando como lançamento');
});
test('Supervisor has confirm and undo actions without deleting existing records',()=>{
 assert.match(js,/id="unit-no-conv-button"/);
 assert.match(js,/Desfazer confirmação sem convocação/);
 assert.match(js,/temConfirmacaoSemConvocacao\(supervisorAtual,unit,date\)/);
 assert.match(js,/state\.semConvocacoesUnidade=marked\?/);
 assert.match(js,/if\(!saveData\(\)\)return/);
});
