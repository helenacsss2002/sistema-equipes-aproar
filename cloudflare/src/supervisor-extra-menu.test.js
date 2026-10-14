import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const first=app.indexOf('  const EXTRA_OPTIONS =');
const definitions=app.slice(first,app.indexOf('  const seedData=',first));
const start=app.indexOf('  function personRow(');
const renderer=app.slice(start,app.indexOf('  function bindServiceRows(){',start));
assert.ok(start>=0 && renderer.includes('Houve extra?'));

function renderPerson(extra=null){
  const ctx={
    perfilAtual:'SUPERVISOR',portalDate:'2026-10-14',supervisorAtual:'EDUARDO',
    STATUS_OPTIONS:['Presente (Integral)','Falta'],
    OBRAS:[{id:'obra1',nome:'Unidade teste',unidade:'FIEC'}],
    colaboradorById:()=>({id:'1',nome:'Pessoa QA',funcao:'Pedreiro',custo:200}),
    itemServices:()=>[{obraId:'obra1',periodo:'Integral'}],
    extraRecordFor:()=>extra,
    dayCost:()=>200,
    extraMultiplier:kind=>kind==='Meia diária'?.5:kind==='Diária'?1:kind==='Uma e meia diária'?1.5:2,
    roundMoney:value=>Math.round(value*100)/100,
    escapeHtml:value=>String(value??''),
    field:(title,input)=>'<label>'+title+input+'</label>',
    allocationRow:()=>'<div class="allocation-row"></div>',
    extraWorkOptions:id=>'<option value="'+id+'">Unidade teste</option>',
    presence:status=>status?.startsWith('Presente')
  };
  ctx.globalThis=ctx;
  vm.createContext(ctx);
  vm.runInContext(definitions+'\n'+renderer+'\nglobalThis.renderPerson=personRow;',ctx,{timeout:1000});
  return ctx.renderPerson('1',null,'FIEC','obra1','2026-10-14','EDUARDO');
}

test('Houve extra? tem apenas quatro opções e Não selecionado em novo apontamento',()=>{
  const html=renderPerson();
  const menu=html.match(/<select class="control row-extra"[^>]*>([\s\S]*?)<\/select>/);
  assert.ok(menu,'Seletor de extra deve existir');
  const list=[...menu[1].matchAll(/<option value="([^"]+)"[^>]*>([^<]+)<\/option>/g)].map(m=>({value:m[1],label:m[2]}));
  assert.deepEqual(list,[
    {value:'Não',label:'Não'},
    {value:'Meia diária',label:'Meia Diária'},
    {value:'Diária',label:'Diária'},
    {value:'Duas diárias',label:'Duas diárias'}
  ]);
  assert.match(menu[1],/<option value="Não" selected>/);
  assert.doesNotMatch(html,/row-extra-category/);
  assert.match(html,/row-extra-value[^>]*readonly value="0\.00"/);
  assert.doesNotMatch(app.slice(app.indexOf('function renderSupervisorHeader()'),app.indexOf('function audit(action')),/\['extras','Lançar extra'\]/);
});

test('Registro histórico de Uma e meia diária não desaparece ao reabrir apontamento',()=>{
  const html=renderPerson({
    extra:'Uma e meia diária',
    obraId:'obra1',
    valorExtraOriginal:300,
    observacao:'Registro anterior'
  });
  const menu=html.match(/<select class="control row-extra"[^>]*>([\s\S]*?)<\/select>/)?.[1];
  assert.ok(menu);
  assert.match(menu,/value="Uma e meia diária" selected>Uma e meia diária \(registro anterior\)<\/option>/);
  assert.match(html,/row-extra-value[^>]*readonly value="300\.00"/);
  assert.match(html,/Registro anterior/);
});
