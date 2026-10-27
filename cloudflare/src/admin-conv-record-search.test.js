import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const begin=ui.indexOf('  function wireLiveSuggestions('),end=ui.indexOf('  function bindServiceRows(){',begin);
assert(begin>=0&&end>begin,'Busca em tempo real deve continuar disponível');

test('Correcao administrativa pesquisa colaborador e mantem indice da convocacao ate escolha explicita',()=>{
 const start=ui.indexOf('  function renderAdminConv(edit){');
 const stop=ui.indexOf('  function relocateAdminPerson(',start);
 assert(start>0&&stop>start);
 const block=ui.slice(start,stop);
 assert.match(block,/type="search" id="ae-record-search"/);
 assert.match(block,/placeholder="Digite o nome do colaborador/);
 assert.match(block,/id="ae-record" hidden tabindex="-1" aria-hidden="true"/);
 assert.match(block,/wireLiveSuggestions\(searchInput,\(\)=>rows\.map/);
 assert.match(block,/searchText:\[x\.p\?\.funcao\|\|''\,x\.c\.dataServico,x\.c\.id\]/);
 assert.match(block,/select\.value='';\$\('#ae-record-selected'\)\.textContent=/);
 assert.match(block,/const selected=\$\('#ae-record'\)\.value,x=selected===''?\s*null:rows\[Number\(selected\)\]/);
 assert.match(block,/syncRecordSearch\(choice\.id\)/);
 assert.match(block,/syncRecordSearch\(rows\.length\?0:''\)/);
 assert.match(block,/\$\('#ae-date'\)\.onchange=refresh/);
 assert.match(block,/\$\('#ae-form'\)\.onsubmit=/);
 assert.match(block,/\$\('#ae-delete-bulk'\)\.onclick=/);
 assert.match(css,/\.ae-record-search-wrap \.live-search-option \{[^}]*white-space:normal/);
});

test('Pesquisar nomes acentuados localiza apenas convocacoes correspondentes e diferencia unidades',()=>{
 const ctx={
  obraById:id=>({1:{nome:'SERVIÇO CENTRO'},2:{nome:'MANUTENÇÃO SÃO GONÇALO'}}[id]),
  clean:x=>String(x||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim(),
  escapeHtml:x=>String(x||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])),
  document:{createElement:()=>menu}
 };
 const s=ui.indexOf('const recordLabel=x=>[',ui.indexOf('  function renderAdminConv(edit){'));
 const e=ui.indexOf(';const renderEditor=',s);
 assert(s>=0&&e>s);
 vm.createContext(ctx);
 vm.runInContext('globalThis.recordLabel=x=>'+ui.slice(s+'const recordLabel=x=>'.length,e)+';',ctx);
 const rows=[
  {id:'71',p:{nome:'IVONEUDO FERREIRA DA SILVA',funcao:'Pintor'},c:{dataServico:'2026-10-26',unidade:'CENTRO',turno:'Integral',supervisor:'VICTOR',obraId:'1',id:'1751'}},
  {id:'72',p:{nome:'FRANCISCO FERNANDO SOUZA DUARTE (ÍNDIO)'},c:{dataServico:'2026-10-27',unidade:'SÃO GONÇALO DO AMARANTE',turno:'Integral',supervisor:'FELIPE',obraId:'2',id:'1752'}},
  {id:'73',p:{nome:'FRANCISCO FERNANDO SOUZA DUARTE (ÍNDIO)'},c:{dataServico:'2026-10-27',unidade:'CENTRO',turno:'Tarde',supervisor:'VICTOR',obraId:'1',id:'1753'}}
 ];
 const callbacks={},input={
  value:'',dataset:{},attrs:{},
  parentElement:{classList:{add(){}},appendChild(el){this.menu=el;}},
  addEventListener(type,fn){(callbacks[type]??=[]).push(fn);},
  setAttribute(k,v){this.attrs[k]=v;},removeAttribute(){},focus(){},
  fire(type,extra={}){for(const f of callbacks[type]||[])f(extra);}
 };
 const menu={hidden:true,buttons:[],setAttribute(){},querySelectorAll(){return this.buttons;}};
 Object.defineProperty(menu,'innerHTML',{set(markup){
  this.markup=markup;this.buttons=[];
  for(const match of markup.matchAll(/data-live-choice="(\d+)"/g)){
   const callbacks={};
   this.buttons.push({dataset:{liveChoice:match[1]},classList:{toggle(){}},setAttribute(){},
    addEventListener(type,fn){callbacks[type]=fn;},fire(type){callbacks[type]?.({preventDefault(){}});}});
  }
 },get(){return this.markup;}});
 vm.runInContext(ui.slice(begin,end)+'\nglobalThis.bind=wireLiveSuggestions;',ctx);
 let selected=null;
 ctx.bind(input,()=>rows.map((x,index)=>({id:String(index),label:ctx.recordLabel(x),searchText:x.c.id})),choice=>{selected=rows[Number(choice.id)];});
 input.value='francisco';input.fire('input');
 assert.equal(input.value,'francisco','Digitacao nao deve travar nem trocar texto');
 assert.equal(menu.buttons.length,2,'Pessoas com duas convocacoes seguem distinguiveis');
 assert.match(menu.markup,/SÃO GONÇALO DO AMARANTE/);
 assert.match(menu.markup,/CENTRO/);
 input.value='indio';input.fire('input');
 assert.equal(menu.buttons.length,2,'Pesquisa ignora acentos');
 input.value='ivoneudo';input.fire('input');
 assert.equal(menu.buttons.length,1);
 assert.equal(selected,null,'Nao seleciona automaticamente uma pessoa');
 menu.buttons[0].fire('click');
 assert.equal(selected.id,'71');
 assert.equal(selected.c.unidade,'CENTRO');
 assert.equal(selected.c.supervisor,'VICTOR');
});
