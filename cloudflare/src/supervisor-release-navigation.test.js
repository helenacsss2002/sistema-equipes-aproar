import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');

test('Portal do Supervisor mostra Solicitar liberação na barra visível de abas, não apenas no menu lateral oculto',()=>{
 const start=js.indexOf('  function renderSupervisorHeader(){');
 const end=js.indexOf('  function audit(',start);
 assert(start>0&&end>start);
 const portal=js.slice(start,end);
 assert.match(portal,/\['apontamento','Apontamentos'\]/);
 assert.match(portal,/\['convocacao','Convocação'\]/);
 assert.match(portal,/\['disponibilidade','Disponibilidade'\]/);
 assert.match(portal,/\['liberacoes-financeiras','Solicitar liberação'\]/);
 assert.match(portal,/data-portal-view="\$\{v\}"/);
 assert.match(portal,/\$\$\(\'\[data-portal-view\]\'\)\.forEach\(b=>b\.onclick=\(\)=>setView\(b\.dataset\.portalView\)\)/);
 assert.match(css,/\.supervisor-layout \.portal-tabs\s*\{\s*grid-template-columns:repeat\(4,minmax\(0,1fr\)\)/);
 assert.match(css,/@media\(max-width:600px\)\s*\{\s*\.supervisor-layout \.portal-tabs\s*\{grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);
});

test('Clicar em solicitar liberação mantém inclusões não confirmadas do apontamento',()=>{
 const start=js.indexOf('  function setView(view) {'),end=js.indexOf('  function render() {',start);
 const code=js.slice(start,end);
 assert.match(code,/view!=='apontamento'&&!\(perfilAtual==='SUPERVISOR'&&view==='liberacoes-financeiras'\)/);
 assert.match(code,/viewAtual = permitidas.includes\(view\) \? view : 'inicio'/);
 assert.match(code,/renderNav\(\)/);
 assert.match(code,/render\(\)/);
});

test('Tela de solicitação continua disponível apenas para supervisor e mantém aprovação restrita',()=>{
 const start=js.indexOf('  function renderFinancialReleases(){');
 const end=js.indexOf('  function renderPayments(){',start);
 const view=js.slice(start,end);
 assert.match(view,/const supervisor=perfilAtual==='SUPERVISOR'/);
 assert.match(view,/canApprove=\['CONTROLADORIA','FINANCEIRO'\]\.includes\(perfilAtual\)/);
 assert.match(view,/api\/financial-release\/request/);
 assert.match(view,/api\/financial-release\/decide/);
 assert.match(view,/id="fr-form"/);
 assert.match(view,/Solicitar autorização/);
 assert.match(js,/'liberacoes-financeiras':renderFinancialReleases/);
});
