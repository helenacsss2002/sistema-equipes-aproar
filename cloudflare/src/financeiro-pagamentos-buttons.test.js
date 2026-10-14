import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
function extract(start,end){
  const a=app.indexOf(start),b=app.indexOf(end,a+start.length);
  assert.ok(a>=0&&b>a,'Trecho ausente: '+start);
  return app.slice(a,b);
}
const code=[
  extract('  function bindExportAction(button,action){','  function renderConvCompletaBase(){'),
  extract('  function renderPayments(){','  function absenceRecords(){'),
  'globalThis.openPayments=renderPayments;'
].join('\n');

test('Pagamentos vincula todos os cinco botões de exportação após montar o detalhamento',async()=>{
  const calls=[],inputs=[{dataset:{index:'0',field:'ajudaCusto'},value:'11'}],buttons={};
  for(const id of ['export-csv','export-excel','export-pdf','export-fin-summary-excel','export-fin-summary-pdf']){
    buttons['#'+id]={textContent:id,disabled:false,onclick:null};
  }
  const nodes={
    '#main-content':{innerHTML:''},
    '#pay-body':{innerHTML:''},
    '#financial-cycle':{value:'custom',onchange:null},
    ...buttons
  };
  const row={
    c:{dataServico:'2026-10-13'},
    p:{nome:'Álvaro QA',id:'1'},
    i:{status:'Presente (Integral)'},
    finance:100,night:0,bonus:0,ajudaCusto:11,
    units:new Set(['FIEC'])
  };
  const ctx={
    $:query=>query==='.pay-input'?inputs[0]:nodes[query]||null,
    $$:query=>query==='.pay-input'?inputs:[],
    selectedCycle:'custom',
    reportFilters:{inicio:'2026-10-13',fim:'2026-10-13',obra:'Todas',supervisor:'Todos'},
    perfilAtual:'FINANCEIRO',viewAtual:'pagamentos',
    head:()=>'<h2>Pagamentos</h2>',
    cycleControl:()=>'<div>Ciclo de teste</div>',
    filterControls:()=>'<div>Filtros</div>',
    exportButtons:()=>'<div>Exportações</div>',
    financialEntries:()=>[row],
    financialSummaryRows:()=>[{nome:'Álvaro QA',total:111}],
    table:()=>'<table></table>',metric:()=>'<div>Total</div>',
    money:x=>'R$ '+x,formatDate:s=>s,escapeHtml:s=>String(s||''),
    bindFilters:()=>{},financialCycle:()=>({pagamento:'2026-10-14'}),isoToday:()=> '2026-10-14',
    exportTable:()=>calls.push('csv'),
    exportReportsExcel:()=>calls.push('excel'),
    exportVisibleWorkbook:()=>calls.push('excel-alternativo'),
    reportPDF:kind=>calls.push(kind==='financial-consolidated'?'pdf-consolidado':'pdf'),
    exportFinancialSummaryExcel:()=>calls.push('excel-consolidado'),
    adjustPayment:()=>calls.push('ajuste'),
    showToast:message=>{throw new Error(message)},
    console
  };
  ctx.globalThis=ctx;
  vm.createContext(ctx);
  vm.runInContext(code,ctx,{timeout:1000});
  assert.doesNotThrow(()=>ctx.openPayments(),'A tela deve abrir sem TypeError antes de vincular os botões');
  assert.equal(typeof inputs[0].onchange,'function','Campos financeiros devem permanecer editáveis');
  for(const btn of Object.values(buttons))assert.equal(typeof btn.onclick,'function',btn.textContent+' sem evento de clique');
  for(const id of ['export-csv','export-excel','export-pdf','export-fin-summary-excel','export-fin-summary-pdf']){
    await buttons['#'+id].onclick();
  }
  assert.deepEqual(calls,['csv','excel','pdf','excel-consolidado','pdf-consolidado']);
});

test('Índice HTML força atualização do app.js para quem já abriu o Financeiro',()=>{
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 assert.match(html,/src="\/app\.js\?v=[^"]+"/);
 assert.match(app,/\$\$\('\.pay-input'\)\.forEach/);
 assert.doesNotMatch(app,/(?<!\$)\$\('\.pay-input'\)\.forEach/);
});
