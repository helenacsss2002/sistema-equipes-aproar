import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const operations=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');

test('Adicional noturno selecionado (0, 50, 90) é preservado em tela e relatório',()=>{
 const found=app.match(/  function nocturnal\(i,c\)\{[^\n]+\}/);
 assert(found,'Função de adicional noturno não encontrada');
 const ctx={presence:s=>s.startsWith('Presente'),hasSebrae:()=>true,roundMoney:v=>Math.round(v*100)/100};
 vm.runInNewContext(found[0]+'; globalThis.calc=nocturnal;',ctx);
 for(const value of [0,50,90]){
  assert.equal(ctx.calc({status:'Presente (Integral)',noturno:value},{}),value);
 }
 assert.equal(ctx.calc({status:'Falta',noturno:90},{}),0);
 assert.match(app,/item&&Number\.isFinite\(Number\(item\.noturno\)\)\?Number\(item\.noturno\):90/);
 assert.doesNotMatch(app,/else if\(card\.dataset\.unit==='SEBRAE'&&Number\(night\.value\)===0\)/);
 assert.match(operations,/const night=isPresent&&hasSebrae\?Number\(i\.noturno\?\?0\):0/);
 assert.doesNotMatch(operations,/Math\.max\(90,Number\(i\.noturno\)/);
});

test('Valor de acordo é somado uma só vez quando não existe complemento independente',()=>{
 const total=(extra,historic,night,bonus,cost)=>extra+historic+night+bonus+cost;
 assert.equal(total(0,0,90,76.43,0),166.43);
 assert.equal(total(0,0,50,76.43,0),126.43);
 assert.equal(total(0,0,0,76.43,0),76.43);
 assert.match(app,/Number\(card\.dataset\.financeiroOriginal\)\|\|0/);
 assert.match(app,/moneyValue\('\.row-acordo'\)/);
});
