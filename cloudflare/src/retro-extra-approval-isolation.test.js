import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=app.indexOf('      const itens=readPersonRows(ids);');
const end=app.indexOf("      if(!validateAgreementObservations(itens,");
assert.ok(start>=0&&end>start);
const block=app.slice(start,end);

const baseline={colaboradorId:'1',status:'Presente (Integral)',extra:'Não',
  valorExtraOriginal:0,valorExtraDisponivel:75,acordo:20,ajudaCusto:11,
  noturno:90,financeiro:50,servicos:[{obraId:'1',periodo:'Integral'}]};
function runRetro(edited,dirty=[],saved=baseline){
 const ctx={
  ids:['1'],readPersonRows:()=>[structuredClone(edited)],
  perfilAtual:'SUPERVISOR',dataServico:'2026-10-30',
  responsavel:'JOEL',unidade:{value:'CENTRO'},
  $:selector=>selector==='#retro-turno'?{value:'Integral'}:null,
  state:{convocacoes:[{id:'1',dataServico:'2026-10-30',supervisor:'JOEL',
    unidade:'CENTRO',turno:'Integral',colaboradores:['1']}]},
  apForConv:id=>saved&&id==='1'?{itens:[saved]}:null,
  retroFinancialEdits:new Map([['1',new Set(dirty)]])
 };
 vm.createContext(ctx);
 vm.runInContext(block+'\nglobalThis.output=itens;',ctx);
 return ctx.output[0];
}

test('Extra liberada retroativa não altera passagem, noturno, bonificação nem complemento',()=>{
 const changed={...baseline,valorExtraDisponivel:150,acordo:0,ajudaCusto:0,noturno:0,financeiro:0,
  extraLancamento:{enabled:true,extra:'Diária',valorExtraOriginal:150,obraId:'1'}};
 const item=runRetro(changed,['Extra']);
 assert.equal(item.valorExtraDisponivel,150);
 assert.equal(item.acordo,20);
 assert.equal(item.ajudaCusto,11);
 assert.equal(item.noturno,90);
 assert.equal(item.financeiro,50);
 assert.equal(item.extraLancamento.enabled,true);
});

test('Retroativo sem edição da extra não recria nem cancela extra antiga ao salvar observação',()=>{
 const displayed={...baseline,observacao:'Ajuste operacional',valorExtraDisponivel:200,
  extraLancamento:{enabled:true,extra:'Diária',valorExtraOriginal:200,obraId:'1'}};
 const item=runRetro(displayed,[]);
 assert.equal(item.valorExtraDisponivel,75);
 assert.equal(item.extra,'Não');
 assert.equal(Object.hasOwn(item,'extraLancamento'),false);
 assert.equal(item.observacao,'Ajuste operacional');
});

test('Extra nova sem apontamento confirmado continua exigindo autorização financeira conforme prazo',()=>{
 const changed={...baseline,valorExtraDisponivel:150,extraLancamento:{enabled:true,extra:'Diária',valorExtraOriginal:150,obraId:'1'}};
 const item=runRetro(changed,['Extra'],null);
 assert.equal(item.valorExtraDisponivel,150);
 assert.equal(item.extraLancamento.enabled,true);
});

test('Rascunhos e eventos retroativos mantêm intenção por campo e colaborador',()=>{
 assert.match(app,/const retroFinancialEdits=new Map\(\)/);
 assert.match(app,/dirtyFinancial:Object\.fromEntries\(\[\.\.\.retroFinancialEdits\]/);
 assert.match(app,/if\(!stored\.dirtyFinancial\)for\(const \[id,item\] of retroDrafts\)/);
 assert.match(app,/retroFinancialEdits\.get\(String\(item\.colaboradorId\)\)\|\|new Set\(\)/);
 assert.match(app,/if\(!edited\.has\('Extra'\)\)/);
 assert.match(app,/delete item\.extraLancamento/);
 assert.match(app,/\['row-extra','row-extra-value','row-extra-work'/);
});
