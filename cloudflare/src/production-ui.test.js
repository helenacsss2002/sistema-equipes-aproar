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


test('Relatorios mostram todas as colunas com rolagem horizontal acessivel no topo',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 assert.match(ui,/function enableReportHorizontalScroll\(\)/);
 assert.match(ui,/wrap\.classList\.add\('report-table-wrap'\)/);
 assert.match(ui,/id="report-scroll-top"/);
 assert.match(ui,/id="report-scroll-prev"/);
 assert.match(ui,/id="report-scroll-next"/);
 assert.match(ui,/wrap\.scrollWidth>wrap\.clientWidth\+2/);
 assert.match(ui,/bar\.onscroll=\(\)=>/);
 assert.match(ui,/wrap\.onscroll=\(\)=>/);
 assert.match(ui,/enableReportHorizontalScroll\(\);\$\('#report-day-select'\)\.onchange/);
 assert.match(html,/#report-body \.report-table-wrap\s*\{[^}]*overflow-x:\s*auto/);
 assert.match(html,/#report-body \.report-table-wrap table\s*\{[^}]*width:\s*max-content/);
 assert.match(html, /\.report-scroll-top\s*\{[^}]*overflow-x:\s*auto/);
 // The report still contains the rightmost Total column and original export actions.
 assert.match(ui,/\['Data','Supervisor','Unidade','Obra','Colaborador','Período','Status'/);
 assert.match(ui,/'Periculosidade 30%'/);
 assert.match(ui,/,'Total'\],selected\.map/);
 assert.match(ui,/refresh\(\);bindExports\(\)/);
});
