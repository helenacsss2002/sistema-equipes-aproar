import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {financialDeadline,afterFinancialDeadline} from './financial-release.js';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const a=app.indexOf('  function financialCycle(ref=isoToday(),offset=0){');
const b=app.indexOf('  function reminder(',a);
const source=app.slice(a,b);
assert.ok(a>0&&b>a,'Regra de apresentação do ciclo financeiro precisa existir');

function context(time='2026-11-10T11:59:59Z'){
 const ctx={
  now:()=>new Date(time),
  isoToday:()=>time.slice(0,10),
  dateLocal:v=>new Date(v+'T12:00:00'),
  calendarISO:d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')
 };
 vm.createContext(ctx);
 vm.runInContext(source+'\nglobalThis.cycle=financialCycle;globalThis.anchor=financialCycleReference;',ctx);
 return ctx;
}
test('O painel do Financeiro acompanha domingo a segunda com pagamento terça seguinte',()=>{
 const ctx=context();
 const cycle=ctx.cycle('2026-11-09');
 assert.equal(cycle.inicio,'2026-11-01');
 assert.equal(cycle.fim,'2026-11-09');
 assert.equal(cycle.pagamento,'2026-11-10');
 assert.equal(ctx.cycle('2026-11-10').inicio,'2026-11-08');
 assert.equal(ctx.cycle('2026-11-10').fim,'2026-11-16');
});
test('Terça até 10h abre por padrão o ciclo ainda não pago; depois mostra a semana seguinte',()=>{
 const before=context('2026-11-10T12:59:59Z');
 assert.equal(before.anchor(),'2026-11-09');
 assert.equal(before.cycle(before.anchor()).pagamento,'2026-11-10');
 const at=context('2026-11-10T13:00:00Z');
 assert.equal(at.anchor(),'2026-11-09');
 const after=context('2026-11-10T13:00:01Z');
 assert.equal(after.anchor(),'2026-11-10');
 assert.equal(after.cycle(after.anchor()).pagamento,'2026-11-17');
});
test('A tela e o servidor compartilham a terça de pagamento e hora de corte',()=>{
 const ctx=context();
 for(const date of ['2026-10-20','2026-10-26','2026-11-01','2026-11-02','2026-11-08','2026-11-09','2026-11-10']){
  const server=financialDeadline(date),ui=ctx.cycle(date);
  assert.equal(server.start,ui.inicio,date);
  assert.equal(server.end,ui.fim,date);
  assert.equal(server.payment,ui.pagamento,date);
 }
 assert.equal(afterFinancialDeadline('2026-11-09','2026-11-10T12:59:59Z'),false);
 assert.equal(afterFinancialDeadline('2026-11-09','2026-11-10T13:00:01Z'),true);
});
test('A tela só permite edição financeira sem autorização antes do prazo, mesmo sem ajuste prévio',()=>{
 assert.match(app,/function isFinancialEditingLocked\(date,item\)\{return now\(\)>new Date\(financialCycle\(date\)\.pagamento\+'T10:00:00-03:00'\);\}/);
 assert.doesNotMatch(app,/Boolean\(item\?\.financeAdjusted\)&&now\(\)/);
});
test('Datas sobrepostas em dois visores financeiros não são pagas duas vezes',()=>{
 const src=app.slice(app.indexOf('  function financialEntries(){'),app.indexOf('  function financialSummaryRows('));
 assert.match(src,/const paymentCycle=typeof selectedCycle==='string'/);
 assert.match(src,/financialCycle\(x\.c\.dataServico\)\.pagamento!==paymentCycle\)continue/);
 assert.match(app,/financialCycle\(financialCycleReference\(\),Number\(selectedCycle\)\)/);
});

test('Passagem e noturno vencidos são bloqueados na interface, mesmo sem ajuste financeiro anterior',()=>{
 const from=app.indexOf('  function personRow('),to=app.indexOf('  function wireLiveSuggestions(',from);
 const person=app.slice(from,to);
 assert.match(person,/isFinancialEditingLocked\(serviceDate,item\)&&!isApprovedFinancial\(serviceDate,cid,'Passagem \/ ajuda de custo'\)/);
 assert.match(person,/!isFinancialEditingLocked\(serviceDate,item\)\|\|isApprovedFinancial\(serviceDate,cid,'Adicional noturno'\)/);
 assert.doesNotMatch(person,/item\?\.financeAdjusted&&isFinancialEditingLocked\(/);
});
