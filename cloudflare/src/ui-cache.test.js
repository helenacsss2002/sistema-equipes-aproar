import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

test('Index HTML references versioned APROAR frontend with Trello fix',()=>{
 const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
 const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 assert.match(html,/src="\/app\.js\?v=[a-z0-9-]+"/i);
 assert.match(js,/document\.querySelectorAll\('\[data-trello-card\]'\)\.forEach/);
 assert.doesNotMatch(js,/\$\('\[data-trello-card\]'\)\.forEach/);
});
