import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const obras=[
  {id:'28',unidade:'SENAI CENTRO',nome:'OBRA 2308.1 - SUBSTITUIÇÃO DE TAMPA DE CANALETA'},
  {id:'83',unidade:'SENAI CENTRO',nome:'PORTA DE VIDRO DANIFICADA | 1333933753'},
  {id:'101',unidade:'SESI BARRA DO CEARÁ',nome:'ADEQUAÇÃO NA COBERTURA | 1469425072'}
];
function simpleContext(){
 return {
  OBRAS:obras,
  obraById:id=>obras.find(x=>String(x.id)===String(id)),
  clean:v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim(),
  escapeHtml:v=>String(v).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))
 };
}
function makeInput(){
 const listeners={};
 const input={
  value:'',dataset:{},title:'',attrs:{},
  parentElement:{classList:{add(){}},appendChild(el){this.menu=el;}},
  addEventListener(type,fn){(listeners[type]??=[]).push(fn);},
  setAttribute(k,v){this.attrs[k]=v;},
  removeAttribute(){},
  focus(){},
  fire(type,evt={}){for(const fn of listeners[type]||[])fn(evt);}
  dispatchEvent(evt){this.fire(evt.type,evt);return true;},
 };
 return input;
}
function makeMenu(){
 const menu={
  hidden:true,buttons:[],
  setAttribute(){},
  querySelectorAll(){return this.buttons;}
 };
 Object.defineProperty(menu,'innerHTML',{get(){return this.html;},set(s){
  this.html=s;this.buttons=[];
  for(const match of s.matchAll(/data-live-choice="(\d+)"/g)){
   const handlers={};
   this.buttons.push({
    dataset:{liveChoice:match[1]},classList:{toggle(){}},setAttribute(){},
    addEventListener(type,fn){handlers[type]=fn;},
    fire(type){handlers[type]?.({preventDefault(){}});}
   });
  }
 }});
 return menu;
}
function setup(){
 const input=makeInput(),menu=makeMenu(),select={value:'28'},full={textContent:''};
 const card={querySelector:q=>({
  '.row-extra-work-search':input,
  '.row-extra-work':select,
  '.extra-work-full-label':full
 })[q]||null};
 const ctx={...simpleContext(),Event:class Event{constructor(type,options){this.type=type;this.bubbles=options?.bubbles;}},document:{createElement:()=>menu}};
 vm.createContext(ctx);
 const begin=app.indexOf('  function wireLiveSuggestions('),end=app.indexOf('  function bindServiceRows(){',begin);
 assert(begin>=0&&end>begin);
 vm.runInContext(app.slice(begin,end)+'\nglobalThis.bind=bindExtraWorkSearch;',ctx);
 ctx.bind(card);
 return {input,menu,select,full};
}

test('O campo da extra substitui a lista nativa por input com pesquisa e ID oculto',()=>{
 const ctx=simpleContext();vm.createContext(ctx);
 const begin=app.indexOf('function extraWorkOptions('),end=app.indexOf('  function extraRecordFor(',begin);
 assert(begin>=0&&end>begin);
 vm.runInContext(app.slice(begin,end)+'\nglobalThis.make=extraWorkSearchMarkup;',ctx);
 const markup=ctx.make('83');
 assert.match(markup,/class="control row-extra-work-search"/);
 assert.match(markup,/placeholder="Digite o número ou nome do serviço"/);
 assert.match(markup,/class="row-extra-work"[^>]*hidden/);
 assert.match(markup,/value="83" selected/);
 assert.match(markup,/1333933753/);
 assert.match(app,/field\('Obra \/ Serviço da extra',extraWorkSearchMarkup\(workId\)\)/);
});

test('A busca filtra em tempo real pelo numero final do serviço e preserva o ID correto',()=>{
 const {input,menu,select,full}=setup();
 assert.match(full.textContent,/2308\.1/,'serviço inicialmente associado continua visível');
 input.value='1333933753';input.fire('input');
 assert.equal(input.value,'1333933753','digitar não deve congelar ou substituir o texto');
 assert.equal(select.value,'','digitar não confirma silenciosamente o serviço anterior');
 assert.equal(menu.buttons.length,1);
 assert.match(menu.html,/PORTA DE VIDRO DANIFICADA/);
 assert.match(menu.html,/1333933753/);
 menu.buttons[0].fire('click');
 assert.equal(select.value,'83','gravar deve usar o ID do registro escolhido, não o número digitado');
 assert.match(input.value,/1333933753/);
 assert.match(full.textContent,/1333933753/,'texto inteiro do resultado escolhido permanece visível');
 assert.equal(input.attrs['aria-expanded'],'false');
});

test('Pesquisa também encontra número inicial e ID da obra, sem criar seleção sem clique',()=>{
 const {input,menu,select,full}=setup();
 input.value='2308.1';input.fire('input');
 assert.equal(menu.buttons.length,1);
 assert.match(menu.html,/OBRA 2308\.1/);
 input.value='101';input.fire('input');
 assert.equal(menu.buttons.length,1,'o identificador interno também pode localizar o serviço');
 assert.equal(select.value,'','não escolher automaticamente');
 menu.buttons[0].fire('click');
 assert.equal(select.value,'101');
 input.value='NÃO EXISTE';input.fire('input');
 assert.equal(select.value,'');
 assert.match(full.textContent,/Selecione um resultado/);
 assert.match(menu.html,/Nenhum resultado/);
});

test('Resultados longos quebram linhas para mostrar o número sem corte',()=>{
 assert.match(html,/\.extra-work-search-wrap \.live-search-option\s*\{[^}]*white-space:normal/);
 assert.match(html,/\.extra-work-full-label\s*\{[^}]*overflow-wrap:anywhere/);
 assert.match(html,/\.extra-work-search-wrap \.live-search-suggestions\s*\{[^}]*max-height:300px/);
 assert.match(app,/obraId:row\.querySelector\('\.row-extra-work'\)\?\.value\|\|''/);
});
