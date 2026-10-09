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
 assert.deepEqual(conf.previews,{},'Cloudflare PR preview builds require a previews block.');
 assert.match(worker,/mayDeleteProduction\(env\)/);
 assert.match(worker,/writes\(env\)/);
});
