import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
function block(start,end){
 const a=ui.indexOf(start),b=ui.indexOf(end,a+start.length);
 assert.ok(a>=0&&b>a,'Bloco não encontrado: '+start);
 return ui.slice(a,b);
}
function setup(){
 const cards=[],rows=new Map(),toggled=[],p={
   id:'1',nome:'Colaborador QA',funcao:'Eletricista',custo:241.74
 };
 const control=(value)=>({value:String(value),listeners:{},
   addEventListener(event,callback){this.listeners[event]=callback;},
   fire(event){this.listeners[event]?.();}
 });
 const inputs={
  '.row-extra':control('Não'),
  '.row-extra-value':control('R$ 0,00'),
  '.row-noturno':control('50'),
  '.row-status':control('Presente (Integral)'),
  '.row-financeiro-historico':control('120'),
  '.row-acordo':control('5'),
  '.row-ajuda-custo':control('11'),
  '.row-extra-panel':{classList:{toggle(className,enabled){toggled.push([className,enabled]);}}},
  '.row-total':{textContent:''},
  '.service-count':{textContent:''},
  '.add-service':{},
  '.remove-last-service':{},
  '.additional-services':{insertAdjacentHTML(){}}
 };
 const serviceFields={
  '.service-work':{value:'SEBRAE obra'},
  '.service-period':{value:'Noite'}
 };
 const service={querySelector:sel=>serviceFields[sel]};
 inputs['.row-extra-work']={value:'3'};
 inputs['.row-extra-obs']={value:'serviço de extra'};
 inputs['.row-obs']={value:'comprovado'};
 const card={
  dataset:{person:'1',unit:'SEBRAE',financeAdjusted:'false',ajudaCusto:'11',financeiroOriginal:'120'},
  querySelector:sel=>inputs[sel]||null,
  querySelectorAll:sel=>sel==='.allocation-row'?[service]:[]
 };
 const ctx={
  $$:sel=>sel==='.person-card'?[card]:[],
  document:{querySelector:sel=>sel==='[data-person="1"]'?card:null},
  OBRAS:[{id:'3',nome:'SEBRAE obra',unidade:'SEBRAE'}],
  dayCost:()=>241.74,
  roundMoney:n=>Math.round(n*100)/100,
  extraMultiplier:value=>value==='Meia diária'?.5:value==='Diária'?1:value==='Uma e meia diária'?1.5:2,
  colaboradorById:()=>p,
  clean:v=>String(v||'').trim().toUpperCase(),
  presence:status=>status.startsWith('Presente'),
  allocationRow:()=>'<div></div>'
 };
 ctx.globalThis=ctx;
 vm.createContext(ctx);
 vm.runInContext(block('  function bindServiceRows(){','  function readPersonRows(')+block('  function readPersonRows(','  function applyInlineExtras(')+'\nglobalThis.bind=bindServiceRows;globalThis.read=readPersonRows;',ctx);
 return {ctx,inputs,card,toggled};
}
test('Categoria de Extra não predefine valor; supervisor digita o valor e o total é recalculado',()=>{
 const {ctx,inputs,toggled}=setup();
 ctx.bind();
 assert.equal(inputs['.row-extra-value'].value,'R$ 0,00');
 assert.equal(inputs['.row-extra-value'].disabled,true);
 assert.equal(inputs['.row-extra-value'].type,undefined,'Simulador não cria tipo até selecionar extra');
 assert.match(inputs['.row-total'].textContent,/186,00/);
 inputs['.row-extra'].value='Diária';inputs['.row-extra'].onchange();
 assert.equal(inputs['.row-extra-value'].value,'','Selecionar Diária não preenche automaticamente a quantia');
 assert.equal(inputs['.row-extra-value'].disabled,false);
 assert.equal(inputs['.row-extra-value'].type,'number');
 assert.equal(inputs['.row-extra-value'].required,true);
 inputs['.row-extra-value'].value='247.88';inputs['.row-extra-value'].fire('input');
 assert.match(inputs['.row-total'].textContent,/433,88/);
 assert.deepEqual(toggled.at(-1),['hidden',false]);
 inputs['.row-extra'].value='Uma e meia diária';inputs['.row-extra'].onchange();
 assert.equal(inputs['.row-extra-value'].value,'247.88','Escolher 1 e meia diária não altera o valor informado');
 inputs['.row-extra'].value='Duas diárias';inputs['.row-extra'].onchange();
 assert.equal(inputs['.row-extra-value'].value,'247.88','Trocar categoria não reescreve valor digitado');
 inputs['.row-extra-value'].value='312.50';inputs['.row-extra-value'].fire('change');
 assert.match(inputs['.row-total'].textContent,/498,50/);
 inputs['.row-noturno'].value='90';inputs['.row-noturno'].fire('change');
 assert.match(inputs['.row-total'].textContent,/538,50/);
 assert.equal(inputs['.row-financeiro-historico'].value,'120','Valor histórico não é alterado');
 inputs['.row-extra'].value='Não';inputs['.row-extra'].onchange();
 assert.equal(inputs['.row-extra-value'].disabled,true);
 assert.equal(inputs['.row-extra-value'].value,'R$ 0,00');
 assert.equal(inputs['.row-extra-value'].type,'text');
 assert.equal(inputs['.row-extra-value'].required,false);
 assert.match(inputs['.row-total'].textContent,/226,00/);
 inputs['.row-extra'].value='Meia diária';inputs['.row-extra'].onchange();
 assert.equal(inputs['.row-extra-value'].value,'','Ao ativar novamente, precisa digitar novo valor');
 assert.equal(inputs['.row-extra-value'].type,'number');
 assert.equal(inputs['.row-extra-value'].disabled,false);
});
test('Apontamento normal e retroativo enviam categoria e valor informado sem duplicar a presença',()=>{
 const {ctx,inputs}=setup();
 inputs['.row-extra'].value='Duas diárias';
 inputs['.row-extra-value'].value='213.45';
 const [item]=ctx.read(['1']);
 assert.equal(item.extra,'Não');
 assert.equal(item.extraLancamento.enabled,true);
 assert.equal(item.extraLancamento.extra,'Duas diárias');
 assert.equal(item.extraLancamento.valorExtraOriginal,213.45);
 assert.equal(item.extraLancamento.obraId,'3');
 assert.equal(item.extraLancamento.observacao,'serviço de extra');
 assert.equal(item.noturno,50);
 assert.equal(item.financeiro,120);
 assert.equal(item.ajudaCusto,11);
 inputs['.row-extra'].value='Não';
 const [other]=ctx.read(['1']);
 assert.equal(other.extraLancamento.enabled,false);
});
test('Não há funções duplicadas que sobrescrevam Extra e apontamento da equipe',()=>{
 assert.equal((ui.match(/function bindServiceRows\(\)/g)||[]).length,1);
 assert.equal((ui.match(/function readPersonRows\(/g)||[]).length,1);
 assert.match(ui,/field\('Houve extra\?'/);
 assert.match(ui,/APONTAMENTO_EXTRA_OPTIONS = \[\['Não','Não'\],\['Meia diária','Meia Diária'\],\['Diária','Diária'\],\['Uma e meia diária','1 e meia diária'\],\['Duas diárias','Duas diárias'\]\]/);
 assert.doesNotMatch(ui,/class="control row-extra-category"/);
 assert.doesNotMatch(ui,/\['extras','Lançar extra'\]/);
 assert.match(ui,/Valor da Extra \(R\$\)/);
 assert.match(ui,/row-total-summary/);
 assert.match(ui,/data-financeiro-original/);
 assert.doesNotMatch(ui,/class="control row-financeiro"/);
 assert.match(ui,/TOTAL A PAGAR AO COLABORADOR/);
 assert.match(ui,/valorExtraOriginal:enabled\?Number/);
 assert.match(ui,/category=row.querySelector\('\.row-extra'\)/);
 assert.match(ui,/option value="50"/);
 assert.match(ui,/option value="90"/);
 assert.match(html,/row-total-summary/);
 assert.match(html,/app\.js\?v=aproar-observacao-acordo-20261015-1/);
 assert.match(ui,/bindPersonSearch\(\$\('#retro-person-search'\),\(\)=>\$\$\('\.retro-person-list/);
 assert.match(ui,/const ids = \$\$\('input\[name="retro-colab"\]:checked'\)\.map/);
});
