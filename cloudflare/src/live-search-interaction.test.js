import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const a=app.indexOf('  function wireLiveSuggestions('),b=app.indexOf('  function bindServiceRows(){',a);
assert(a>=0&&b>a,'O componente de pesquisa ao digitar deve existir');
const code=app.slice(a,b);

function createInput(){
 const hooks={};
 const input={
  value:'',dataset:{},attributes:{},removed:[],
  parentElement:{classes:new Set(),classList:{add(){}},appendChild(node){this.menu=node;}},
  addEventListener(type,fn){(hooks[type]??=[]).push(fn);},
  setAttribute(k,v){this.attributes[k]=v;},
  removeAttribute(k){this.removed.push(k);},
  focus(){},
  fire(type,evt={}){for(const fn of hooks[type]||[])fn(evt);}
 };
 return input;
}
function makeMenu(){
 const menu={hidden:true,html:'',buttons:[],attributes:{},className:'',
  setAttribute(k,v){this.attributes[k]=v;},
  querySelectorAll(){return this.buttons;}
 };
 Object.defineProperty(menu,'innerHTML',{
  get(){return this.html;},
  set(v){
   this.html=v;this.buttons=[];
   for(const match of v.matchAll(/data-live-choice="(\d+)"/g)){
    const callbacks={};
    this.buttons.push({
     dataset:{liveChoice:match[1]},attrs:{},classList:{toggle(){}},
     setAttribute(k,x){this.attrs[k]=x;},
     addEventListener(type,fn){callbacks[type]=fn;},
     fire(type,e={preventDefault(){}}){callbacks[type]?.(e);}
    });
   }
  }
 });
 return menu;
}
function setup(){
 const input=createInput();
 const menu=makeMenu();
 const ctx={
  document:{createElement:()=>menu},
  clean:s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim(),
  escapeHtml:s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))
 };
 ctx.globalThis=ctx;vm.createContext(ctx);
 vm.runInContext(code+'\nglobalThis.wireLiveSuggestions=wireLiveSuggestions;',ctx);
 return {ctx,input,menu};
}
const works=[{id:'a',label:'OBRA 2402 - REFORMA AUTOMOTIVA | BARRA DO CEARÁ'},{id:'b',label:'OBRA 199 - MUSEU'},{id:'c',label:'OBRA 300 - Unifor'}];

test('Pesquisar digita caractere por caractere, abre resultados e preserva o texto e cursor',()=>{
 const {ctx,input,menu}=setup(),picked=[];
 ctx.wireLiveSuggestions(input,()=>works,item=>picked.push(item.id));
 input.value='Ob';input.fire('input');
 assert.equal(input.value,'Ob');assert.equal(input.attributes['aria-expanded'],'true');
 assert.equal(menu.buttons.length,3);
 input.value='obra 2402';input.fire('input');
 assert.equal(input.value,'obra 2402','Não pode substituir o que a pessoa ainda está escrevendo');
 assert.equal(menu.buttons.length,1,'Filtra imediatamente sem usar Tab');
 assert.match(menu.html,/BARRA DO CEARÁ/);
 assert(input.removed.includes('list'),'Não depende do datalist nativo que pode travar a digitação');
 assert.equal(picked.length,0,'Não seleciona obra sem pedido explícito');
 input.fire('keydown',{key:'ArrowDown',preventDefault(){}});
 input.fire('keydown',{key:'Enter',preventDefault(){}});
 assert.equal(input.value,works[0].label);
 assert.deepEqual(picked,['a']);
 assert.equal(menu.hidden,true);
});
test('Busca sem resultados mantém o termo; seleção via clique não apaga o que foi escolhido',()=>{
 const {ctx,input,menu}=setup(),picked=[];
 ctx.wireLiveSuggestions(input,()=>works,x=>picked.push(x.id));
 input.value='qualquer coisa';input.fire('input');
 assert.equal(input.value,'qualquer coisa');
 assert.match(menu.html,/Nenhum resultado/);
 input.value='museu';input.fire('input');
 assert.equal(menu.buttons.length,1);
 menu.buttons[0].fire('mousedown');
 menu.buttons[0].fire('click');
 assert.equal(input.value,'OBRA 199 - MUSEU');
 assert.deepEqual(picked,['b']);
 input.fire('blur');assert.equal(menu.hidden,true);
});
test('Campos de serviços normais e retroativos ligam buscas vivas, inclusive obras adicionais',()=>{
 const block=app.slice(app.indexOf('  function bindServiceRows(){'),app.indexOf('  function validateAgreementObservations('));
 assert.match(block,/\.person-card \.service-work/);
 assert.match(block,/wireLiveSuggestions\(input,/);
 assert.match(block,/wireLiveSuggestions\(added,/);
 assert.match(app,/wireLiveSuggestions\(workCombo,/);
 assert.match(app,/bindServiceRows\(\);/);
 assert.match(html,/\.live-search-host:focus-within/);
 assert.match(html,/\.live-search-suggestions\[hidden\]/);
 assert.match(html,/caret-color:#174fa4/);
});
