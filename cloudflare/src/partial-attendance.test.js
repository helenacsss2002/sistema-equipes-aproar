import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

test('Normal attendance can save a single worker without completing the team',()=>{
 const code=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const start=code.indexOf('function renderEquipeDia(){');
 const end=code.indexOf('let unitConvDate=',start);
 assert.ok(start>=0&&end>start);
 const ui=code.slice(start,end);
 assert.ok(ui.includes('Salvar somente este'));
 assert.ok(ui.includes("$$('[data-save-person]').forEach"));
 assert.ok(ui.includes('const ready=entries.filter'));
 assert.ok(ui.includes('const selectedIds=new Set'));
 assert.ok(ui.includes('const pending=entries.length-ready.length'));
 assert.ok(!ui.includes("for(const i of items)if(!validServices([i],people.get(i.colaboradorId).conv.unidade))return;for(const c of convs)"));
});