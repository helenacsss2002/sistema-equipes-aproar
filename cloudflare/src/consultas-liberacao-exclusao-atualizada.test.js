import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');

test('Somente visualizar tem acesso adicional permanente a consultas, sem remover menu atual',()=>{
 const start=ui.indexOf('  function render() {'),end=ui.indexOf('  function showLogin() {',start);
 const code=ui.slice(start,end);
 assert.match(code,/const pages=\{dashboard:renderDashboard,relatorios:renderReports,indicadores:renderIndicators,conflitos:renderConflitos,disponibilidade:renderDisponibilidade,indisponibilidade:renderIndisponibilidade\}/);
 assert.match(code,/class="viewer-query-tabs"/);
 assert.match(code,/data-viewer-query/);
 for(const view of ['conflitos','disponibilidade','indisponibilidade'])assert(code.includes("['"+view+"'"),view);
 assert.match(code,/setView\(btn\.dataset\.viewerQuery\)/);
 assert.match(ui,/if\(perfilAtual==='VISUALIZAR'\) return \[item\('dashboard'/);
});
test('Supervisor vê solicitação financeira também como botão acima dos filtros',()=>{
 assert.match(ui,/id="portal-request-release"/);
 assert.match(ui,/Solicitar liberação financeira/);
 assert.match(ui,/releaseShortcut\.onclick=\(\)=>setView\('liberacoes-financeiras'\)/);
 assert.match(ui,/\['liberacoes-financeiras','Solicitar liberação'\]/);
});
test('Supervisor pode corrigir inclusão sem apontamento da sua própria equipe ainda que criada pela Controladoria',()=>{
 assert.match(ui,/if\(perfilAtual==='SUPERVISOR'&&c\.supervisor!==supervisorAtual\)continue/);
 assert.match(ui,/api\('\/api\/unpointed-convocation-remove'/);
 assert.match(ui,/colaboradorId:String\(id\),requestId/);
 const start=worker.indexOf("if(path==='/api/unpointed-convocation-remove'"),end=worker.indexOf("if(path==='/api/save'",start);
 const route=worker.slice(start,end);
 assert.match(route,/conv\.engenheiro!==session\.user/);
 assert.doesNotMatch(route,/conv\.criado_por!==session\.user/);
 assert.match(route,/String\(conv\.colaborador_id\)!==colaboradorId/);
 assert.match(route,/if\(conv\.apontado\|\|conv\.servicos\|\|conv\.conflito\)/);
 assert.match(route,/aproar_web_apply/);
 assert.match(route,/criadoPor:conv\.criado_por/);
});
test('Aviso mantém proteção para apontamentos confirmados e não libera exclusão de histórico',()=>{
 assert.match(worker,/Este colaborador já possui apontamento ou histórico vinculado/);
 assert.match(worker,/REMOVER_INCLUSAO_SEM_APONTAMENTO/);
 assert.doesNotMatch(worker.slice(worker.indexOf("if(path==='/api/unpointed-convocation-remove'"),worker.indexOf("if(path==='/api/save'")) ,/table:'apontamentos',action:'delete'/);
});
