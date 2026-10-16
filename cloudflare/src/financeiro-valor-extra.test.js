import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const consolidator=fs.readFileSync(new URL('../public/financeiro-consolidado.js',import.meta.url),'utf8');
const ctx={};ctx.globalThis=ctx;vm.createContext(ctx);vm.runInContext(consolidator,ctx,{timeout:2000});

test('Total a pagar soma extra, adicional noturno, acordos, passagem e valores anteriores uma vez cada',()=>{
 const data=[
  {p:{id:'1',nome:'Ana'},c:{dataServico:'2026-10-13',supervisor:'EDUARDO'},i:{status:'Presente (Integral)'},extra:50,finance:30,night:90,bonus:5,ajudaCusto:11},
  {p:{id:'1',nome:'Ana'},c:{dataServico:'2026-10-14',supervisor:'EDUARDO'},i:{status:'Extra independente'},extra:25,finance:0,night:0,bonus:0,ajudaCusto:0},
  {p:{id:'2',nome:'Beatriz'},c:{dataServico:'2026-10-13',supervisor:'EDUARDO'},i:{status:'Presente (Integral)'},extra:0,finance:0,night:50,bonus:0,ajudaCusto:12}
 ];
 const result=ctx.APROARFinanceConsolidado.summarize(data);
 assert.equal(result.length,2);
 assert.deepEqual(Array.from(result,x=>x.nome),['Ana','Beatriz']);
 assert.equal(result[0].extra,75);
 assert.equal(result[0].finance,30);
 assert.equal(result[0].night,90);
 assert.equal(result[0].total,211);
 assert.equal(result[1].total,62);
 assert.equal(result.reduce((t,x)=>t+x.total,0),273);
});

test('Portal do Supervisor tem um único campo Valor da Extra e total em azul não editável',()=>{
 const person=app.slice(app.indexOf('function personRow('),app.indexOf('function bindServiceRows()'));
 assert.match(person,/field\('Valor da Extra Disponível \(R\$\)'/);
 assert.equal((person.match(/field\('Valor da Extra Disponível \(R\$\)'/g)||[]).length,1);
 assert.match(person,/class="control row-extra-value"[^>]*type="number"[^>]*min="0"[^>]*step="0\.01"/);
 assert.doesNotMatch(person,/class="control row-extra-value"[^>]*placeholder=/,'O campo deve ficar vazio, sem texto de preenchimento');
 assert.doesNotMatch(person,/class="control row-extra-value"[^>]*disabled/);
 const binder=app.slice(app.indexOf('function bindServiceRows()'),app.indexOf('function validateAgreementObservations('));
 assert.match(binder,/extraAmount\.disabled=false/);
 assert.match(binder,/extraAmount\.required=active/);
 assert.doesNotMatch(person,/class="control row-extra-value"[^>]*readonly/);
 assert.match(person,/data-financeiro-original=/);
 assert.doesNotMatch(person,/class="control row-financeiro"/);
 assert.match(person,/TOTAL A PAGAR AO COLABORADOR/);
 assert.match(person,/role="status"/);
 assert.match(html,/#155bc7/);
 assert.match(html,/row-total-summary strong[^\n]+color:#fff/);
});

test('Todos os relatórios financeiros usam Valor da Extra e explicitam valores históricos',()=>{
 for(const [start,end] of [
  ['function exportTable()','function bindExportAction('],
  ['function renderReports()','function renderDashboard()'],
  ['function renderPayments()','function absenceRecords()'],
  ['function reportRowsForExport(','const excelCol='],
  ['function exportFinancialSummaryExcel()','function financialWorkbook()'],
  ['function financialWorkbook()','function exportReportsExcel()'],
  ['async function reportPDF(kind)','async function xlsxRows(']
 ]){
  const a=app.indexOf(start),b=app.indexOf(end,a+start.length);
  assert.ok(a>=0&&b>a,start);
  const area=app.slice(a,b);
  assert.match(area,/Valor da Extra/,start);
  assert.match(area,/Valores (complementares já registrados|anteriores)/,start);
  assert.doesNotMatch(area,/'Financeiro \(R\$\)'/,start);
 }
 assert.match(html,/app\.js\?v=aproar-supervisor-extra-disponivel-20261016-4/);
});
