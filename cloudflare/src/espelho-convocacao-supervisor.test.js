import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const markupStart=source.indexOf('  function convocationReviewMarkup(');
const markupEnd=source.indexOf('  function renderUnitConvocacao(){',markupStart);
const handlerStart=source.indexOf("    const form=$('#unit-conv-form'),reviewBox=$('#unit-conv-review')");
const handlerEnd=source.indexOf('\n  }\n\n  function operationalRows(',handlerStart);
assert(markupStart>=0&&markupEnd>markupStart,'Espelho da convocação ausente');
assert(handlerStart>=0&&handlerEnd>handlerStart,'Confirmação definitiva ausente');

function mockElement(value=''){
 const classes=new Set();
 return {
  value,innerHTML:'',disabled:false,
  classList:{add:name=>classes.add(name),remove:name=>classes.delete(name),contains:name=>classes.has(name)},
  scrollIntoView(){},
  classes
 };
}
function setup(){
 const fields=new Map([
  ['#unit-conv-form',mockElement()],['#unit-conv-review',mockElement()],['#unit-no-conv-box',mockElement()],
  ['#unit-conv-date',mockElement('2026-10-21')],['#unit-conv-unit',mockElement('BARRA DO CEARÁ')],
  ['#unit-conv-turn',mockElement('Integral')],['#unit-conv-correct',mockElement()],['#unit-conv-final',mockElement()]
 ]);
 fields.get('#unit-conv-review').classList.add('hidden');
 const people=[{id:'2',nome:'Zé Carlos',funcao:'Pedreiro'},{id:'1',nome:'Ana Maria',funcao:'Servente'}];
 const select=[{value:'2',checked:true},{value:'1',checked:true}];
 const saved=[],messages=[],auditTrail=[];
 const ctx={
  $:selector=>fields.get(selector),$$:selector=>selector==='#unit-conv-people input'?select:[],
  selected:new Set(),avulsoDraft:[],supervisorAtual:'EDUARDO',
  onlineQueued:false,onlineSaving:false,onlineWritable:true,
  state:{convocacoes:[]},OBRAS:[{unidade:'BARRA DO CEARÁ'}],COLABORADORES:people,
  colaboradorById:id=>ctx.COLABORADORES.find(x=>x.id===id),
  alphabeticalPeople:xs=>[...xs].sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR',{sensitivity:'base'})),
  escapeHtml:v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'),
  formatDate:s=>s.split('-').reverse().join('/'),
  blocked:()=>false,temConfirmacaoSemConvocacao:()=>false,refreshNoConv:()=>{},
  overlaps:()=>true,registerConvocationConflicts:()=>{},
  toast:(msg,error=false)=>messages.push({msg,error}),
  now:()=>new Date('2026-10-20T13:00:00Z'),uid:()=> 'cv_test',
  audit:(...args)=>auditTrail.push(args),
  saveData:()=>{saved.push(true);return true;}
 };
 vm.createContext(ctx);
 vm.runInContext(source.slice(markupStart,markupEnd),ctx);
 vm.runInContext(source.slice(handlerStart,handlerEnd)+'\nglobalThis.getReviewDraft=()=>reviewDraft;',ctx);
 return {ctx,fields,select,saved,messages,auditTrail};
}
function review(set){
 set.fields.get('#unit-conv-form').onsubmit({preventDefault(){}});
}

test('Primeiro clique abre espelho com unidade, turno, data, supervisor e nomes em ordem alfabética, sem gravar',()=>{
 const set=setup();review(set);
 const {ctx,fields,saved}=set;
 assert.equal(ctx.state.convocacoes.length,0);
 assert.equal(saved.length,0);
 assert.equal(fields.get('#unit-conv-form').classList.contains('hidden'),true);
 assert.equal(fields.get('#unit-conv-review').classList.contains('hidden'),false);
 assert.equal(fields.get('#unit-no-conv-box').classList.contains('hidden'),true);
 const html=fields.get('#unit-conv-review').innerHTML;
 for(const word of ['Espelho da convocação','21/10/2026','BARRA DO CEARÁ','Integral','EDUARDO','Confirmar convocação definitiva','Voltar e corrigir'])assert(html.includes(word),word);
 assert(html.indexOf('Ana Maria')<html.indexOf('Zé Carlos'),'Colaboradores devem estar em ordem alfabética');
});
test('Voltar e corrigir não grava e preserva colaboradores selecionados',()=>{
 const set=setup();review(set);
 set.fields.get('#unit-conv-correct').onclick();
 assert.equal(set.ctx.state.convocacoes.length,0);
 assert.equal(set.saved.length,0);
 assert.equal(set.fields.get('#unit-conv-form').classList.contains('hidden'),false);
 assert.equal(set.fields.get('#unit-conv-review').classList.contains('hidden'),true);
 assert.deepEqual(set.select.map(x=>x.checked),[true,true]);
 review(set);
 assert.equal(set.saved.length,0);
});
test('Somente confirmação definitiva grava a convocação uma vez, incluindo avulsos revisados',()=>{
 const set=setup();
 set.ctx.avulsoDraft.push({id:'a1',nome:'Bruno Avulso',funcao:'Servente',avulso:'Sim'});
 review(set);
 assert.equal(set.ctx.COLABORADORES.length,2);
 assert(set.fields.get('#unit-conv-review').innerHTML.includes('Bruno Avulso'));
 set.fields.get('#unit-conv-final').onclick();
 assert.equal(set.saved.length,1);
 assert.equal(set.ctx.COLABORADORES.length,3);
 assert.equal(set.ctx.state.convocacoes.length,1);
 const conv=set.ctx.state.convocacoes[0];
 assert.equal(conv.supervisor,'EDUARDO');assert.equal(conv.dataServico,'2026-10-21');
 assert.deepEqual([...conv.colaboradores],['2','1','a1']);
 assert.equal(set.ctx.getReviewDraft(),null);
 set.fields.get('#unit-conv-final').onclick();
 assert.equal(set.saved.length,1,'Segundo clique acidental não cria duplicidade');
});
test('Conflito surgido depois do espelho bloqueia confirmação e não gera convocação',()=>{
 const set=setup();review(set);
 set.ctx.state.convocacoes.push({dataServico:'2026-10-21',colaboradores:['1'],turno:'Integral',unidade:'OUTRA'});
 set.fields.get('#unit-conv-final').onclick();
 assert.equal(set.saved.length,0);
 assert.equal(set.ctx.state.convocacoes.length,1);
 assert.equal(set.fields.get('#unit-conv-form').classList.contains('hidden'),false);
 assert(set.messages.some(x=>x.error&&x.msg.includes('já convocado')));
});
test('Resumo escapa nomes e não grava ao escolher revisar',()=>{
 const set=setup();
 set.ctx.COLABORADORES[0].nome='<script>falso</script>';
 review(set);
 const html=set.fields.get('#unit-conv-review').innerHTML;
 assert(!html.includes('<script>'));
 assert(html.includes('&lt;script&gt;'));
 assert.equal(set.saved.length,0);
});
