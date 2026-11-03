import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const begin=app.indexOf('function renderEquipeDia()');
const end=app.indexOf('function renderEquipeConvocacao()',begin);
const day=app.slice(begin,end<0?begin+35000:end);

test('A edição de extra autorizada não envia fichas confirmadas dos colegas que não foram alteradas',()=>{
 assert.ok(begin>0);
 assert.match(day,/const dayTouchedIds=new Set\(/);
 assert.match(day,/const allItems=readPersonRows\(\[\.\.\.people\.keys\(\)\]\)/);
 assert.match(day,/const items=allItems\.filter\(i=>dayTouchedIds\.has\(i\.colaboradorId\)/);
 assert.match(day,/const extraBatch=items\.slice\(\)/);
 assert.match(day,/const selected=items\.filter\(i=>c\.colaboradores\.includes\(i\.colaboradorId\)\)/);
});

test('Rascunhos preservam as fichas modificadas mesmo após atualizar o navegador',()=>{
 assert.match(day,/dirtyIds:\[\.\.\.dayTouchedIds\]/);
 assert.match(day,/dirtyIds:draft\.dirtyIds\|\|\[\]/);
 assert.match(day,/dirtyIds:Array\.isArray\(stored\.dirtyIds\)/);
 assert.match(day,/oldDraftChanged\(/);
 assert.match(day,/dayTouchedIds\.add\(card\.dataset\.person\)/);
});

test('Marcar todos como presentes é uma ação explícita, não uma alteração acidental',()=>{
 assert.match(day,/dayTouchedIds\.add\(card\.dataset\.person\)/);
 assert.match(day,/day-all-present/);
 assert.match(day,/Nenhuma alteração pendente para salvar/);
});
