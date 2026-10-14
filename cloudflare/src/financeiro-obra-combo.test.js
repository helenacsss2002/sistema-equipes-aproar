import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const filterCode=source.slice(source.indexOf('function filterControls(searchableWork=false)'),source.indexOf('function filteredConvs(){'));
const workNumber=source.match(/function financialWorkNumber\(id\)\{[^\n]+\}/)?.[0];
assert.ok(filterCode.includes('function bindFilters(refresh)'));
assert.ok(workNumber,'Extrator de número de obra deve existir');

function setup(works){
  const controls=new Map();
  for(const id of ['r-sup','r-obra','r-obra-combo','r-obra-search','r-ini','r-fim','r-period']){
    controls.set(id,{value:'',onchange:null,oninput:null,onblur:null,onkeydown:null,dispatchEvent(event){this.onchange?.(event);}});
  }
  // No navegador, os campos de data já são inicializados pelo HTML do filtro.
  controls.get('r-ini').value='2026-10-06';
  controls.get('r-fim').value='2026-10-12';
  let refreshed=0;
  const context={
    OBRAS:works,
    SUPERVISORES:['EDUARDO','FELIPE'],
    reportFilters:{inicio:'2026-10-06',fim:'2026-10-12',supervisor:'Todos',obra:'Todas'},
    obraById:id=>works.find(o=>o.id===id),
    $:selector=>controls.get(selector.slice(1))||null,
    Event:class Event{constructor(type){this.type=type;}},
    clean:value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim(),
    escapeHtml:value=>String(value??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])),
    field:(_name,inner)=>inner,
    options:()=>'<option></option>',
    isoToday:()=> '2026-10-14',
    dateLocal:value=>new Date(value+'T12:00:00')
  };
  vm.createContext(context);
  vm.runInContext(workNumber+'\n'+filterCode+'\nglobalThis.filterControls=filterControls;globalThis.bindFilters=bindFilters;',context);
  context.bindFilters(()=>{refreshed++;});
  return {controls,context,get refreshed(){return refreshed;},combo:controls.get('r-obra-combo')};
}

test('Financeiro > Pagamentos apresenta somente um campo editável de obra/serviço',()=>{
 const payments=source.slice(source.indexOf('function renderPayments(){'),source.indexOf('function absenceRecords(){'));
 assert.ok(payments.includes("cycleControl()+filterControls('combined')"),'Usa o mesmo campo único da Controladoria');
 const {context}=setup([{id:'1',nome:'OBRA 145 - Fachada',unidade:'FIEC'}]);
 const html=context.filterControls('combined');
 assert.match(html,/id="r-obra-combo"[^>]+list="r-obra-choices"/);
 assert.match(html,/id="r-obra" type="hidden"/);
 assert.match(html,/datalist id="r-obra-choices"/);
 assert.doesNotMatch(html,/id="r-obra-search"/);
 assert.doesNotMatch(html,/<select[^>]+id="r-obra"/);
});

test('Digitar número único filtra obra no mesmo campo e preserva período/supervisor',()=>{
 const {combo,context,controls,refreshed:initial} = setup([
  {id:'1',nome:'OBRA 145 - Fachada',unidade:'FIEC'},
  {id:'2',nome:'OBRA 221 - Cobertura',unidade:'SEBRAE'}
 ]);
 combo.value='145';
 combo.oninput({type:'input'});
 assert.equal(context.reportFilters.obra,'Todas','Não escolher obra antes de terminar de digitar');
 combo.onchange();
 assert.equal(context.reportFilters.obra,'1');
 assert.equal(controls.get('r-obra').value,'1');
 assert.equal(combo.value,'OBRA 145 - Fachada | FIEC');
 assert.equal(context.reportFilters.inicio,'2026-10-06');
 assert.equal(context.reportFilters.fim,'2026-10-12');
 assert.equal(context.reportFilters.supervisor,'Todos');
});

test('Dropdown mantém seleção por nome e unidade; texto inválido não altera filtro',()=>{
 const {combo,context}=setup([
  {id:'1',nome:'OBRA 145 - Fachada',unidade:'FIEC'},
  {id:'2',nome:'OBRA 221 - Cobertura',unidade:'SEBRAE'}
 ]);
 combo.value='OBRA 221 - Cobertura | SEBRAE';
 combo.oninput({type:'input'});
 assert.equal(context.reportFilters.obra,'2');
 combo.value='999999';
 combo.onblur();
 assert.equal(context.reportFilters.obra,'2');
 assert.equal(combo.value,'OBRA 221 - Cobertura | SEBRAE');
 combo.value='Todas';
 combo.onchange();
 assert.equal(context.reportFilters.obra,'Todas');
});

test('Números duplicados não escolhem uma obra arbitrariamente',()=>{
 const {combo,context}=setup([
  {id:'1',nome:'OBRA 145 - Fachada',unidade:'FIEC'},
  {id:'2',nome:'OBRA 145 - Cobertura',unidade:'SEBRAE'}
 ]);
 combo.value='145';
 combo.onchange();
 assert.equal(context.reportFilters.obra,'Todas');
 combo.onblur();
 assert.equal(combo.value,'Todas');
 combo.value='OBRA 145 - Cobertura | SEBRAE';
 combo.onchange();
 assert.equal(context.reportFilters.obra,'2');
});
