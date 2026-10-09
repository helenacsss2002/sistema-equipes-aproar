import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
test('Production UI shows correct stage and hides dangerous test actions',()=>{
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(html,/id="reset-demo"[^>]*display:none!important/);
 assert.doesNotMatch(ui,/id=\\"portal-reset\\"/);
 assert.match(ui,/onlineStage=result.stage/);
 assert.match(ui,/onlineStage==='producao'/);
 assert.match(ui,/Exclusões em produção estão bloqueadas por segurança/);
});
test('Server cannot enable production writes based on old homologation controls alone',()=>{
 const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
 const conf=JSON.parse(fs.readFileSync(new URL('../wrangler.jsonc',import.meta.url),'utf8'));
 assert.equal(conf.vars.APP_ENV,'producao');
 assert.equal(conf.vars.WRITES_ENABLED,undefined);
 assert.equal(conf.triggers,undefined);
 assert.deepEqual(conf.previews?.vars,{APP_ENV:'homologacao'},'PR preview environment must stay isolated.');
 const root=JSON.parse(fs.readFileSync(new URL('../../wrangler.jsonc',import.meta.url),'utf8'));
 assert.equal(root.name,conf.name,'Root fallback config must target the same validation worker.');
 assert.equal(root.main,'cloudflare/src/worker.js');
 assert.equal(root.assets.directory,'cloudflare/public');
 assert.deepEqual(root.previews,conf.previews);
 assert.deepEqual(root.vars,conf.vars);
 assert.equal(root.triggers,undefined);
 assert.match(worker,/permittedProductionDeletion\(env,session,db,operations\)/);
 assert.match(worker,/writes\(env\)/);
});

test('Connected diagnostics use Neon records rather than legacy local-demo text',()=>{
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(js,/if\(diagnostic&&onlineSession\)/);
 assert.match(js,/p\.textContent='Banco Neon/);
 assert.match(js,/badge\.textContent='Conectado ao banco de '/);
 assert.doesNotMatch(js,/Sem conexão com o banco de produção/);
 assert.doesNotMatch(js,/Demonstração HTML • dados locais/);
});

test('Paulo is available only to Controladoria, never supervisor portal',()=>{
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(js,/const RESPONSAVEIS_CONTROLADORIA=\['PAULO',\.\.\.SUPERVISORES\]/);
 assert.match(js,/id="ac-sup">\$\{options\(RESPONSAVEIS_CONTROLADORIA\)\}/);
 assert.match(js,/id="ae-sup">\$\{options\(RESPONSAVEIS_CONTROLADORIA\)\}/);
 assert.match(js,/id="retro-sup">\$\{options\(RESPONSAVEIS_CONTROLADORIA\)\}/);
 assert.match(js,/const SUPERVISORES = \['EDUARDO', 'FELIPE', 'GABRIEL', 'JOEL', 'NETO', 'SOARES', 'VICTOR'\]/);
 assert.doesNotMatch(js,/const SUPERVISORES = \[[^\]]*'PAULO'/);
});

test('Unit list scrolls independently and work deletion buttons stay on works',()=>{
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(html,/#unit-list\s*\{\s*max-height:\s*300px;\s*overflow:\s*auto;/);
 assert.match(html,/#unit-list\s+th\s*\{\s*position:\s*sticky;/);
 assert.match(ui,/id="obra-list"/);
 assert.match(ui,/const cells=\$\$\('#obra-list table tbody tr'\)/);
 assert.doesNotMatch(ui,/\$\$\('#settings-body table tbody tr'\)/);
});

test('Reload restores a valid server session without logging out',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const init=ui.slice(ui.indexOf('async function initOnline(){'));
 assert.match(init,/enterConnectedSession\(await api\('\/api\/bootstrap'\)\)/);
 assert.doesNotMatch(init,/api\('\/api\/logout'/);
 assert.match(ui,/async function logout\(\).*?api\('\/api\/logout'/s);
 const auth=fs.readFileSync(new URL('./auth.js',import.meta.url),'utf8');
 assert.match(auth,/HttpOnly; Secure; SameSite=Strict; Path=\/; Max-Age=28800/);
});

test('Cadastro permite excluir unidades e selecionar multiplas obras',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(ui,/data-excluir-unidade=/);
 assert.match(ui,/data-excluir-unidade\]'\)\.forEach/);
 assert.match(ui,/id="obra-excluir-selecionadas"/);
 assert.match(ui,/class="obra-bulk-checkbox"/);
 assert.match(ui,/obra-selecionar-disponiveis/);
 assert.match(ui,/works\.length>50/);
 assert.match(ui,/works\.some\(obraTemVinculos\)/);
 assert.match(ui,/OBRAS\.splice\(0,OBRAS\.length,\.\.\.rest\)/);
});

test('Portal do supervisor usa unidades cadastradas no Neon em todos os seletores',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(ui,/function adminUnits\(\)\{return \[\.\.\.new Set\(\[\.\.\.\(state\.units\|\|\[\]\),\.\.\.OBRAS\.map/);
 assert.ok(ui.includes('id="portal-unit" class="control">${options([\'Todas\',...adminUnits()])}'));
 assert.ok(ui.includes('id="unit-conv-unit">${options(adminUnits())}'));
 assert.equal((ui.match(/const unidades = adminUnits\(\);/g)||[]).length,2);
 assert.match(ui,/Esta unidade já está cadastrada, mas ainda não possui obra/);
 assert.match(ui,/if\(portalUnit!==\'Todas\'&&!adminUnits\(\)\.includes\(portalUnit\)\)portalUnit=\'Todas\'/);
});

test('Exclusao de unidade informa vinculos sem apagar historico automaticamente',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(ui,/const linkedWorks=OBRAS\.filter\(o=>o\.unidade===selected\)\.length/);
 assert.match(ui,/const linkedHistory=state\.convocacoes\.some/);
 assert.match(ui,/if\(linkedWorks\|\|linkedHistory\)return showToast/);
 assert.match(ui,/state\.units=state\.units\.filter\(u=>u!==selected\)/);
 assert.match(ui,/Se houver histórico, a exclusão deve permanecer bloqueada/);
});

test('Relatorios permitem buscar a obra sem perder a selecao e sem alterar outros filtros',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 assert.match(ui,/function filterControls\(searchableWork=false\)/);
 assert.match(ui,/id="r-obra-search" type="search"/);
 assert.match(ui,/id="r-obra"><option value="Todas">Todas<\/option>/);
 assert.match(ui,/\+filterControls\(true\)\+'<div class="section report-toolbar">/);
 assert.match(ui,/const matches=query\?OBRAS\.filter\(o=>clean\(o\.nome\+' '\+o\.unidade\)\.includes\(query\)\):OBRAS/);
 assert.match(ui,/select\.value=reportFilters\.obra/);
 assert.match(ui,/workSearch\.oninput=/);
 assert.match(ui,/\['r-sup','r-obra','r-ini','r-fim'\]\.forEach/);
 assert.match(html,/#r-obra-search\s*\{\s*margin-bottom:\s*8px;/);
});

test('Dashboard aceita pesquisar obra por numero, nome ou unidade sem afetar os indicadores',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const dashboard=ui.slice(ui.indexOf('function renderDashboard(){'),ui.indexOf('function renderIndicatorsBase(){'));
 assert.match(dashboard,/\+filterControls\(true\)\+'<div class="section" id="dash-body">/);
 assert.match(dashboard,/bindFilters\(refresh\);refresh\(\)/);
 assert.match(dashboard,/metric\('PRESENÇAS'/);
 assert.match(dashboard,/metric\('FALTAS'/);
 assert.match(dashboard,/metric\('ATESTADOS'/);
 assert.match(dashboard,/metric\('CUSTO TOTAL'/);
 assert.match(ui,/function bindFilters\(refresh\)/);
 assert.match(ui,/const matches=query\?OBRAS\.filter\(o=>clean\(o\.nome\+' '\+o\.unidade\)\.includes\(query\)\):OBRAS/);
 assert.match(ui,/select\.value=reportFilters\.obra/);
 const reports=ui.slice(ui.indexOf('function renderReports(){'),ui.indexOf('function renderDashboard(){'));
 assert.match(reports,/\+filterControls\(true\)\+'<div class="section report-toolbar">/);
});

test('Portal Supervisor remove a data duplicada apenas da aba de convocacao',()=>{
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 assert.ok(js.includes("viewAtual==='convocacao'?'portal-filters-convocacao':''"));
 assert.ok(js.includes("viewAtual==='convocacao'?'':field('Data'"));
 assert.ok(js.includes("const portalDateInput=$('#portal-date');if(portalDateInput)portalDateInput.onchange="));
 assert.match(html,/\.portal-filters\.portal-filters-convocacao\s*\{\s*grid-template-columns:\s*repeat\(2,minmax\(0,1fr\)\)/);
});

test('Convocacao inicia no proximo dia corrido inclusive sabado e domingo e permite alteracao',()=>{
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const conv=js.slice(js.indexOf('function renderUnitConvocacao(){'),js.indexOf('function operationalRows('));
 assert.ok(conv.includes('if(!unitConvDate){const d=dateLocal(isoToday());d.setDate(d.getDate()+1);unitConvDate=calendarISO(d);}'));
 assert.doesNotMatch(conv,/nextBusinessDay\(/);
 assert.ok(conv.includes('id="unit-conv-date" type="date" value="${unitConvDate}" required'));
 assert.ok(conv.includes("$('#unit-conv-date').onchange=()=>{unitConvDate=$('#unit-conv-date').value;render();}"));
 // Verifica a virada real de sexta-feira para sábado e domingo para segunda.
 const following=iso=>{const [y,m,d]=iso.split('-').map(Number);const t=new Date(y,m-1,d,12);t.setDate(t.getDate()+1);return [t.getFullYear(),String(t.getMonth()+1).padStart(2,'0'),String(t.getDate()).padStart(2,'0')].join('-');};
 assert.equal(following('2026-10-09'),'2026-10-10');
 assert.equal(following('2026-10-10'),'2026-10-11');
 assert.equal(following('2026-10-11'),'2026-10-12');
});

test('Pesquisa de obra por texto funciona nos apontamentos normais retroativos e adicionais',()=>{
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 const start=js.indexOf('function allocationRow(');
 const end=js.indexOf('function itemServices(',start);
 const allocation=js.slice(start,end);
 assert.ok(allocation.includes('class="control service-work"'));
 assert.ok(allocation.includes('class="control service-work"'));
 const bind=js.slice(js.indexOf('function bindServiceRows(){'),js.indexOf('function readPersonRows(',start));
 assert.ok(allocation.includes('<datalist id='));
 assert.ok(allocation.includes('listId'));
 assert.ok(js.includes('clean(o.nome)===clean(r.querySelector'));
 assert.ok(allocation.includes('autocomplete="off"'));
 assert.ok(js.includes('?.id||'));
 assert.ok(allocation.includes('placeholder="Selecione ou digite'));
 assert.ok(bind.includes("insertAdjacentHTML('beforeend',allocationRow("));
 assert.ok(html.includes('.service-work { width: 100%; }'));
 assert.ok(js.includes('function renderApontamentoRetroativo()'));
 assert.ok(js.includes('function renderEquipeDia()'));
 assert.ok(js.includes('function renderApontamentoNormal()'));
 assert.ok(js.includes("r.querySelector('.service-work').value"));
});

test('Background claro utiliza imagem original em alta definicao, sem repetir',()=>{
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 const background=fs.readFileSync(new URL('../public/construction-background-hq.webp',import.meta.url));
 assert.match(html,/#app-view \.main-shell\s*\{[^}]*background-image:\s*linear-gradient\(rgba\(255,255,255,\.56\), rgba\(255,255,255,\.56\)\), url\("\/construction-background-hq\.webp\?v=2"\)/s);
 assert.match(html,/background-repeat:\s*no-repeat/);
 assert.match(html,/background-size:\s*cover/);
 assert.match(html,/background-attachment:\s*fixed/);
 assert.equal(background.subarray(0,4).toString(),'RIFF');
 assert.equal(background.subarray(8,12).toString(),'WEBP');
 assert(background.length>40000,'Imagem deve ter qualidade maior que versao comprimida antiga');
 assert.match(html,/#live-status\s*\{\s*display:\s*none/);
});
test('Busca de colaboradores filtra somente a visualizacao e preserva selecoes e formulários',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 assert.match(html,/\.person-search-wrap\s*\{\s*max-width:\s*340px/);
 assert.match(ui,/function bindPersonSearch\(input, cards\)/);
 assert.match(ui,/cards\(\)\.forEach\(card=>\{card\.style\.display=/);
 assert.match(ui,/clean\(card\.textContent\)\.includes\(query\)/);
 assert.match(ui,/id="retro-person-search"/);
 assert.ok(ui.includes("bindPersonSearch($('#retro-person-search'),()=>$('.retro-person-list .check-card'))"));
 assert.match(ui,/id="day-person-search"/);
 assert.ok(ui.includes("bindPersonSearch($('#day-person-search'),()=>$('#day-form .person-card'))"));
 assert.match(ui,/class="control admin-person-search"/);
 assert.ok(ui.includes("bindPersonSearch(form.querySelector('.admin-person-search'),"));
 // Saving still reads all employees, regardless of the search filter.
 assert.match(ui,/readPersonRows\(\[\.\.\.people\.keys\(\)\]\)/);
 assert.match(ui,/\$\$\('input\[name="retro-colab"\]:checked'\)/);
});

test('Só o avatar do Financeiro mostra desenho de dinheiro',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(ui,/perfilAtual==='FINANCEIRO'\)\$\('#sidebar-avatar'\)\.innerHTML=/);
 assert.match(ui,/aria-label="Cédulas e moedas do Financeiro"/);
 assert.match(ui,/perfilAtual==='CONTROLADORIA'\)\$\('#sidebar-avatar'\)\.innerHTML=/);
 assert.match(ui,/else \$\('#sidebar-avatar'\)\.textContent = avatar/);
});


test('Relatorios mostram todas as 13 ou 12 colunas sem barra lateral e rolam verticalmente',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 assert.match(ui,/function configureReportTable\(financial\)/);
 assert.match(ui,/wrap\.classList\.add\('report-vertical-wrap'\)/);
 assert.match(ui,/table\.prepend\(group\)/);
 assert.match(ui,/configureReportTable\(fin\);\$\('#report-day-select'\)\.onchange/);
 assert.doesNotMatch(ui,/enableReportHorizontalScroll/);
 assert.doesNotMatch(ui,/id="report-scroll-next"/);
 assert.doesNotMatch(ui,/id="report-scroll-prev"/);
 const widths=ui.match(/const widths=financial\s*\?\s*\[([\d.,]+)\]\s*:\s*\[([\d.,]+)\]/);
 assert(widths,'Larguras das tabelas financeira e da Controladoria devem existir');
 const financeiro=widths[1].split(',').map(Number);
 const controladoria=widths[2].split(',').map(Number);
 assert.equal(financeiro.length,12);
 assert.equal(controladoria.length,13);
 assert.equal(financeiro.reduce((a,b)=>a+b,0),100);
 assert.equal(controladoria.reduce((a,b)=>a+b,0),100);
 assert.match(html,/#report-body \.report-vertical-wrap\s*\{[^}]*overflow-y:\s*auto;[^}]*overflow-x:\s*hidden;/s);
 assert.match(html,/#report-body \.report-vertical-wrap table\s*\{[^}]*width:\s*100%;[^}]*min-width:\s*0;[^}]*table-layout:\s*fixed;/s);
 assert.match(html,/#report-body \.report-vertical-wrap th,[\s\S]*?white-space:\s*normal;/);
 assert.match(html,/#report-body \.report-vertical-wrap th\s*\{[^}]*position:\s*sticky;/s);
 assert.match(html,/#report-body \.report-vertical-wrap td\s*\{\s*font-size:\s*10\.5px;/);
 assert.doesNotMatch(html,/\.report-scroll-top\s*\{/);
 // Mantém o último valor (Total) e as exportações originais.
 assert.match(ui,/\['Data','Supervisor','Unidade','Obra','Colaborador','Período','Status'/);
 assert.match(ui,/'Periculosidade 30%'/);
 assert.match(ui,/,'Total'\],selected\.map/);
 assert.match(ui,/refresh\(\);bindExports\(\)/);
});
