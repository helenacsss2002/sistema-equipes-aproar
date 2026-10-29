import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');

test('Portal do Supervisor tem atalho visível mesmo com sidebar oculta',()=>{
 assert.match(html,/\.supervisor-layout > \.sidebar,\.supervisor-layout \.topbar\s*\{display:none;\}/);
 const start=ui.indexOf('function renderSupervisorHeader()');
 const end=ui.indexOf('  function audit(',start);
 assert(start>0&&end>start);
 const s=ui.slice(start,end);
 assert.match(s,/id="portal-request-extra">Solicitar liberação da extra<\/button>/);
 assert.match(s,/\$\('#portal-request-extra'\\)\.onclick=/);
 assert.match(s,/setView\('liberacoes-financeiras'\\)/);
 assert.match(s,/form\?\.dispatchEvent\(new Event\('change',\{bubbles:true\}\)\)/);
});
test('Supervisor encontra atalho no apontamento normal e não salva apontamento sem clicar no Salvar',()=>{
 const start=ui.indexOf('function renderEquipeDia(){'),end=ui.indexOf('    let unitConvDate=',start);
 assert(start>0&&end>start);
 const s=ui.slice(start,end);
 assert.match(s,/id="day-request-extra">Solicitar liberação da extra/);
 assert.match(s,/\$\('#day-request-extra'\\)\.onclick=\(\)=>\{snapshotDayDraft\(\);setView\('liberacoes-financeiras'\);\}/);
 assert.match(s,/Salvar apontamento do dia/);
 assert.doesNotMatch(s,/\$\('#day-request-extra'\\)\.onclick=[^;]*saveData/);
});
test('Retroativo salva somente rascunho ao abrir solicitação',()=>{
 const start=ui.indexOf('  function renderApontamentoRetroativo()'),end=ui.indexOf('  function renderExtras(){',start);
 assert(start>0&&end>start);
 const s=ui.slice(start,end);
 assert.match(s,/id="retro-request-extra">Solicitar liberação da extra/);
 assert.match(s,/\$\('#retro-request-extra'\\)\.onclick=\(\)=>\{/);
 assert.match(s,/storeRetroDraft\(\);\s*setView\('liberacoes-financeiras'\)/);
 assert.match(s,/Salvar apontamento retroativo/);
});
test('Formulário de solicitação abre na data do serviço do Supervisor',()=>{
 const start=ui.indexOf('  function renderFinancialReleases(){'),end=ui.indexOf('  function renderPayments(){',start);
 assert(start>0&&end>start);
 const s=ui.slice(start,end);
 assert.match(s,/const supervisor=perfilAtual==='SUPERVISOR'/);
 assert.match(s,/const today=supervisor&&/);
 assert.match(s,/portalDate\?portalDate:isoToday\(\)/);
 assert.match(s,/id="fr-date"/);
 assert.match(s,/api\/financial-release\/request/);
 assert.match(s,/api\/financial-release\/decide/);
 assert.match(s,/>Solicitar autorização<\/button>/);
});
