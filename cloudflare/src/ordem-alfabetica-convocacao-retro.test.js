import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=source.indexOf('  const comparePersonNames=');
const end=source.indexOf('  function loadData()',start);
assert(start>=0&&end>start,'Funções de ordenação de colaboradores devem existir');
const helpers=source.slice(start,end);

function createSort(people){
 const ctx={colaboradorById:id=>people.find(p=>String(p.id)===String(id))};
 vm.createContext(ctx);
 vm.runInContext(helpers+'\nglobalThis.orderPeople=alphabeticalPeople;globalThis.orderIds=alphabeticalPersonIds;',ctx);
 return ctx;
}
test('Colaboradores aparecem em ordem alfabética em português, incluindo acentos e nomes repetidos',()=>{
 const people=[{id:'30',nome:'ZÉ ROBERTO'},{id:'12',nome:'ÁLVARO LIMA'},
  {id:'9',nome:'ANA SILVA'},{id:'7',nome:'Bruna'},{id:'2',nome:'Ana Silva'}];
 const ctx=createSort(people),snapshot=people.map(p=>p.id);
 const out=ctx.orderPeople(people).map(p=>p.id);
 assert.deepEqual(Array.from(out),['12','2','9','7','30']);
 assert.deepEqual(people.map(p=>p.id),snapshot,'Lista original não deve ser modificada');
 assert.deepEqual(Array.from(ctx.orderIds(['30','7','9','12','2'])),['12','2','9','7','30']);
});
test('Convocação de supervisores e controladoria mantém busca por nome e ordena os resultados filtrados',()=>{
 assert.match(source,/alphabeticalPeople\(COLABORADORES\.filter\(c=>!c\.inativo&&c\.nome\.toLowerCase\(\)\.includes\(term\)/);
 assert.match(source,/alphabeticalPeople\(COLABORADORES\.filter\(c=>!c\.inativo&&clean\(c\.nome\+' '\+c\.funcao\)\.includes\(term\)/);
 assert.match(source,/\$\('#unit-conv-search'\)\.oninput=refresh/);
 assert.match(source,/\$\('#ac-search'\)\.oninput=people/);
 assert.match(source,/selected\.has\(c\.id\)\?'checked'/);
 assert.match(source,/alphabeticalPersonIds\(\[\.\.\.new Set\(source\.flatMap\(c=>c\.colaboradores\)\)\]\)/);
});
test('Apontamento retroativo preserva busca e selecionados e mostra fichas em ordem alfabética',()=>{
 const retro=source.slice(source.indexOf('  function renderApontamentoRetroativo()'),source.indexOf('  function renderPendencias()'));
 assert.match(retro,/class="checkbox-grid retro-person-list">\$\{alphabeticalPeople\(COLABORADORES\.filter\(c=>!c\.inativo\)\)/);
 assert.match(retro,/bindPersonSearch\(\$\('#retro-person-search'\)/);
 assert.match(retro,/alphabeticalPersonIds\(\$\$\('input\[name="retro-colab"\]:checked'\)/);
 assert.match(retro,/retroDrafts\.get\(id\)\|\|previousItem\(id\)/);
 assert.match(retro,/g\.ids\.has\(input\.value\)/);
});
test('Listas de convocados e correção administrativa são ordenadas sem alterar os IDs do banco',()=>{
 assert.match(source,/existing\.flatMap\(c=>c\.colaboradores\.map\(id=>\(\{c,id\}\)\)\)\.sort/);
 assert.match(source,/rows=operationalRows\(state\.convocacoes\.filter\(c=>c\.dataServico===adminEditDate\)\)\.sort/);
 assert.match(source,/alphabeticalPersonIds\(conv\.colaboradores\)\.map\(cid=>\{/);
  assert.match(source,/personRow\(cid,item,conv\.unidade/);
 assert.match(source,/const selected=new Set\(\)/);
});
