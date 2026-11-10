import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const operations=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');
const data=fs.readFileSync(new URL('./data.js',import.meta.url),'utf8');
const payStart=app.indexOf('  function renderPayments(){'),payEnd=app.indexOf('  function absenceRecords(){',payStart);
assert.ok(payStart>0&&payEnd>payStart);
const paymentSource=app.slice(payStart,payEnd);

test('Pagamentos aparece somente no menu VISUALIZAR e usa o mesmo renderer que o Financeiro',()=>{
 const nav=app.slice(app.indexOf('  function navConfig()'),app.indexOf('  function sidebarIcon('));
 assert.match(nav,/if\(perfilAtual==='VISUALIZAR'\) return \[[^\n]*item\('financeiro','Pagamentos · somente leitura'/);
 const render=app.slice(app.indexOf('  function render() {'),app.indexOf('  function showLogin()',app.indexOf('  function render() {')));
 assert.match(render,/if\(perfilAtual==='VISUALIZAR'\)\{[\s\S]*pages=\{dashboard:renderDashboard,financeiro:renderPayments/);
 assert.match(nav,/if\(perfilAtual==='FINANCEIRO'\) return \[[^\n]*item\('financeiro','Pagamentos'/);
 assert.match(nav,/return \[item\('inicio','Início'[^\n]*item\('apontamento','Apontamento'/);
});
test('O perfil de visualização recebe todos os apontamentos necessários para conferir o Financeiro',()=>{
 assert.match(data,/export function visibleState\(db,session\)/);
 assert.match(data,/if\(session\.role==='SUPERVISOR'\)\{state\.apontamentos=state\.apontamentos\.filter/);
 assert.doesNotMatch(data,/if\(session\.role==='VISUALIZAR'\)\{state\.apontamentos=state\.apontamentos\.filter/);
});
test('VISUALIZAR não consegue gravar pela API mesmo ao falsificar a tela',()=>{
 assert.match(operations,/if\(session\.role==='VISUALIZAR'\)fail\('Este perfil permite somente visualização\.',403\)/);
 assert.match(app,/async function submitComplementConfirmation\(row,amount,justificativa\)\{/);
 assert.match(app,/onlineSession\?\.role!=='FINANCEIRO'/);
});
test('Pagamentos somente leitura não monta inputs, botões ou confirmações financeiras',()=>{
 assert.match(paymentSource,/const somenteLeitura=perfilAtual==='VISUALIZAR'/);
 assert.match(paymentSource,/somenteLeitura\?\x60<span class="pay-total-display"/);
 assert.match(paymentSource,/somenteLeitura\?'':'<section class="card card-pad section" id="financial-duplicate-review"/);
 assert.match(paymentSource,/if\(somenteLeitura\)return; \/\/ O perfil VISUALIZAR nunca registra callbacks/);
 assert.match(paymentSource,/if\(!somenteLeitura&&perfilAtual!=='FINANCEIRO'\)return setView\('inicio'\)/);
});
test('Conferência oferece mesmos filtros, total e relatórios exportados do Financeiro',()=>{
 assert.match(paymentSource,/financialEntries\(\)\.filter/);
 assert.match(paymentSource,/financialSummaryRows\(e\)/);
 assert.match(paymentSource,/metric\('TOTAL A PAGAR'/);
 assert.match(paymentSource,/cycleControl\(\)\+filterControls\('combined'\)/);
 assert.match(paymentSource,/bindFilters\(\(\)=>\{selectedCycle='custom'/);
 assert.match(paymentSource,/bindExports\(\);bindFinancialSummaryExports\(\)/);
 assert.match(app,/if\(\['FINANCEIRO','VISUALIZAR'\]\.includes\(perfilAtual\)&&viewAtual==='financeiro'\)/);
 assert.match(app,/const finance=perfilAtual==='FINANCEIRO'\|\|\(perfilAtual==='VISUALIZAR'&&viewAtual==='financeiro'\)/);
});
