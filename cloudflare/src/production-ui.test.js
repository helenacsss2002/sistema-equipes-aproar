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
