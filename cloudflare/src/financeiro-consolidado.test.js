import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const ctx={};
ctx.globalThis=ctx;
runInNewContext(readFileSync(new URL('../public/financeiro-consolidado.js',import.meta.url),'utf8'),ctx);
const summarize=ctx.APROARFinanceConsolidado.summarize;
const row=(id,nome,date,supervisor,values={})=>({
  p:{id,nome,funcao:'Pedreiro'},c:{dataServico:date,supervisor,unidade:'FIEC'},
  i:{status:'Presente (Integral)'},finance:0,night:0,bonus:0,ajudaCusto:0,...values
});

test('Consolidado financeiro agrupa por colaborador e ordena alfabeticamente com acentos',()=>{
 const rows=[
   row('2','Zélia','2026-10-13','FELIPE',{finance:100,ajudaCusto:12}),
   row('1','Álvaro','2026-10-12','EDUARDO',{finance:120,night:15,bonus:10,ajudaCusto:11}),
   row('1','Álvaro','2026-10-13','FELIPE',{finance:120,bonus:5,ajudaCusto:25}),
   row('1','Álvaro','2026-10-13','FELIPE',{finance:0,night:7,ajudaCusto:0})
 ];
 const rowsOut=summarize(rows);
 assert.deepEqual(Array.from(rowsOut,x=>x.nome),['Álvaro','Zélia']);
 const a=rowsOut[0];
 assert.equal(a.dias,2);assert.equal(a.supervisores,'EDUARDO, FELIPE');
 assert.equal(a.finance,240);assert.equal(a.night,22);assert.equal(a.bonus,15);assert.equal(a.ajudaCusto,36);
 assert.equal(a.total,313);
 assert.equal(rowsOut[1].total,112);
});

test('Não soma falta, atestado nem linhas sem pagamento, e não mistura IDs iguais em nomes diferentes',()=>{
 const rows=[
   {...row('10','Ana','2026-10-13','SOARES',{finance:100}),i:{status:'Falta'}},
   {...row('10','Ana','2026-10-13','SOARES',{finance:100}),i:{status:'Atestado'}},
   row('10','Ana','2026-10-13','SOARES',{finance:0}),
   row('11','Ana','2026-10-13','SOARES',{finance:31.2}),
   row('12','Ana','2026-10-13','VICTOR',{finance:2})
 ];
 const out=summarize(rows);
 assert.equal(out.length,2);
 assert.deepEqual(Array.from(out,x=>x.id),['11','12']);
 assert.deepEqual(Array.from(out,x=>x.total),[31.2,2]);
});

test('Soma passagens separadamente do financeiro e preserva casas decimais',()=>{
 const out=summarize([
   row('1','Maria','2026-10-13','VICTOR',{finance:100.11,ajudaCusto:10.52}),
   row('1','Maria','2026-10-14','VICTOR',{finance:50.22,ajudaCusto:12.34})
 ])[0];
 assert.equal(out.finance,150.33);assert.equal(out.ajudaCusto,22.86);assert.equal(out.total,173.19);
});

test('Extras independentes entram no consolidado e no total a pagar',()=>{
 const out=summarize([
  row('20','João','2026-10-13','EDUARDO',{extra:120}),
  row('20','João','2026-10-14','EDUARDO',{extra:60,finance:100})
  ])[0];
 assert.equal(out.extra,180);
 assert.equal(out.finance,100);
 assert.equal(out.total,280);
});
