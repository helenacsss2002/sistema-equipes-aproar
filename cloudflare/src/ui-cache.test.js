import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

test('Index HTML references new version of APROAR frontend after Trello UI fix',()=>{
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(html,/src="\/app\.js\?v=trello-ui-fix-20261008-2"/);
 assert.match(js,/document\.querySelectorAll\('\[data-trello-card\]'\)\.forEach/);
 assert.doesNotMatch(js,/\$\('\[data-trello-card\]'\)\.forEach/);
});

test('Apontamento normal e retroativo listam serviços de todas as unidades',()=>{
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(js,/const unidades=\[\.\.\.new Set\(OBRAS\.map\(o=>o\.unidade\)\)\]/);
 assert.match(js,/\<optgroup label=/);
 assert.match(js,/Selecione o serviço \(qualquer unidade\)/);
 assert.doesNotMatch(js,/OBRAS\.filter\(o=>o\.unidade===unit\)/);
 assert.match(js,/function validServices\(items\)/);
 assert.match(js,/!obraById\(x\.obraId\)/);
 assert.match(js,/const updateNoturno=/);
});
