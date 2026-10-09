import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

test('Index HTML references new version of APROAR frontend after Trello UI fix',()=>{
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(html,/src="\/app\.js\?v=aproar-relatorios-combobox-20261009-1"/);
 assert.match(js,/document\.querySelectorAll\('\[data-trello-card\]'\)\.forEach/);
 assert.doesNotMatch(js,/\$\('\[data-trello-card\]'\)\.forEach/);
});
