import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
test('Retro form remains mounted on rejected save and backend state is refreshed',()=>{
 assert.match(app,/const preserveRetroDraft=Boolean\(document\.querySelector\('#form-retro'\)/);
 assert.match(app,/onlineSaving=false;if\(!preserveRetroDraft\)render\(\);showSaveFeedback\(message,true\)/);
 assert.match(app,/applyOnline\(await restoreOnlineSession\(\)\)/);
});
test('Neon backend errors identify support code without exposing internal SQL messages',()=>{
 assert.match(worker,/APROAR save rejected/);
 assert.match(worker,/Referência técnica DB-/);
 assert.match(worker,/e\.code==='57014'/);
});
