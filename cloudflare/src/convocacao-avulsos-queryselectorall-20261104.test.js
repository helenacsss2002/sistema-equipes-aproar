import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=app.indexOf('    const avulsoList=()=>{',app.indexOf('  function renderUnitConvocacao(){'));
const end=app.indexOf("    $('#unit-avulso-add').onclick=",start);
assert.ok(start>0&&end>start,'O gerenciador de avulsos deve existir no formulário de convocação');

function harness(){
  const list={innerHTML:''},selected=new Set(['colaborador-1','colaborador-2']);
  const ctx={
    avulsoDraft:[],onlineQueued:false,onlineSaving:false,
    escapeHtml:value=>String(value??'').replaceAll('<','&lt;').replaceAll('>','&gt;'),
    $:selector=>selector==='#unit-avulso-list'?list:null,
    $$:selector=>selector==='#unit-avulso-list [data-remove-avulso]'
      ?ctx.avulsoDraft.map(p=>({dataset:{removeAvulso:p.id},onclick:null}))
      :[],
    toast:(message)=>ctx.messages.push(message),
    storeConvDraft:()=>ctx.stores++,
    stores:0,messages:[],selected,
  };
  vm.createContext(ctx);
  vm.runInContext(app.slice(start,end)+'\nglobalThis.refreshAvulsos=avulsoList;',ctx);
  return {ctx,list,selected};
}

test('A convocação inicializa sem avulsos e instala o formulário sem erro de JavaScript',()=>{
  const {ctx,list}=harness();
  assert.equal(list.innerHTML,'');
  assert.equal(ctx.avulsoDraft.length,0);
  assert.equal(typeof ctx.refreshAvulsos,'function');
  const conv=app.slice(app.indexOf('  function renderUnitConvocacao(){'),app.indexOf('  function operationalRows('));
  assert.match(conv,/form\.onsubmit=e=>/);
  assert.match(conv,/form\.__aproarBound=true;/);
  assert.ok(conv.indexOf('form.__aproarBound=true;')>conv.indexOf('const avulsoList=()=>'));
});

test('Com avulsos, os botões X usam uma lista de elementos e preservam a equipe',()=>{
  const {ctx,list,selected}=harness();
  ctx.avulsoDraft=[
    {id:'a-cleandro',nome:'Cleandro',funcao:'Servente'},
    {id:'a-outro',nome:'Outro Avulso',funcao:'Profissional'}
  ];
  const buttons=[];
  ctx.$$=selector=>{
    if(selector!=='#unit-avulso-list [data-remove-avulso]')return [];
    return ctx.avulsoDraft.map(p=>{
      const button={dataset:{removeAvulso:p.id},onclick:null};buttons.push(button);return button;
    });
  };
  ctx.refreshAvulsos();
  assert.match(list.innerHTML,/Cleandro/);
  assert.equal(buttons.length,2);
  assert.equal(typeof buttons[0].onclick,'function');
  buttons[0].onclick();
  assert.deepEqual(ctx.avulsoDraft.map(p=>p.id),['a-outro']);
  assert.deepEqual([...selected],['colaborador-1','colaborador-2']);
  assert.equal(ctx.stores,1,'Remoção guarda apenas o rascunho, sem gravar o Neon');
  assert.ok(list.innerHTML.includes('Outro Avulso'));
  assert.ok(!list.innerHTML.includes('Cleandro'));
});

test('Nenhum elemento de seleção única pode usar forEach em telas do APROAR',()=>{
  const invalid=[...app.matchAll(/(?<!\$)\$\((?:'[^']*'|"[^"]*")\)\.forEach/g)].map(match=>match[0]);
  assert.deepEqual(invalid,[],'querySelector devolve um único elemento; use $$ para arrays de nós');
});
