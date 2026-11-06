import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const consolidator=fs.readFileSync(new URL('../public/financeiro-consolidado.js',import.meta.url),'utf8');
const start=app.indexOf('  function financialEntries(){');
const end=app.indexOf('  function financialSummaryRows(',start);
assert.ok(start>0&&end>start,'Cálculo financeiro compartilhado não encontrado');
const originalFn=app.slice(start,end);

function mock({id='218',nome='LUCAS GOMES GONZAGA',avulso='Sim',daily=241.74,
 available=150,extraLabel='Não',passagem=0,finance=0,bonus=0,night=0,date='2026-11-02',
 extraServico=0,extraAvulsa=false,extraOriginal=0}={}){
 const ctx={
  roundMoney:v=>Math.round((Number(v)+Number.EPSILON)*100)/100,
  presence:status=>!['Falta','Atestado'].includes(status),
  reportFilters:{inicio:'2026-10-01',fim:'2026-11-06',supervisor:'Todos',obra:'Todas'},
  state:{apontamentos:[{dataServico:date,supervisor:'EDUARDO',itens:[{
    colaboradorId:id,status:'Presente (Integral)',valorExtraDisponivel:available,extra:extraLabel
  }]}]},
  rows:[],
  entries:()=>ctx.rows
 };
 ctx.rows=[{
  c:{dataServico:date,supervisor:'EDUARDO',obraId:'298',unidade:'BARRA DO CEARÁ'},
  p:{id,nome,avulso,funcao:'Profissional'},
  i:{colaboradorId:id,status:'Presente (Integral)',extra:extraLabel,valorExtraOriginal:0},
  daily,extra:extraServico,danger:0,finance,night,bonus,ajudaCusto:passagem,
  refs:[{colaboradorId:id}]
 }];
 if(extraAvulsa)ctx.rows.push({
  ...ctx.rows[0],c:{...ctx.rows[0].c,extraAvulsa:true},
  i:{colaboradorId:id,status:'Extra independente',valorExtraOriginal:extraOriginal},
  daily:0,extra:extraOriginal,finance:0,night:0,bonus:0,ajudaCusto:0,refs:[]
 });
 ctx.globalThis=ctx;
 vm.createContext(ctx);
 vm.runInContext(consolidator,ctx,{timeout:2000});
 vm.runInContext(originalFn+'\nglobalThis.compute=financialEntries;',ctx,{timeout:2000});
 return ctx;
}
test('02/11 Lucas: 150 informado e extra Não => pagar apenas R$ 150, não R$ 391,74',()=>{
 const ctx=mock();
 const [row]=ctx.compute();
 assert.equal(row.diariaAvulso,241.74,'Diária cadastral ainda existe apenas para custo operacional');
 assert.equal(row.daily,241.74);
 assert.equal(row.extra,150,'Não acrescentar a diária cadastral ao valor informado');
 const [summary]=ctx.APROARFinanceConsolidado.summarize(ctx.compute());
 assert.equal(summary.total,150);
 assert.equal(summary.extra,150);
});
test('Avulsos de dias anteriores: passagem continua somada uma única vez',()=>{
 const ctx=mock({nome:'NORMANDO',date:'2026-11-01',passagem:21});
 const [summary]=ctx.APROARFinanceConsolidado.summarize(ctx.compute());
 assert.equal(summary.extra,150);
 assert.equal(summary.ajudaCusto,21);
 assert.equal(summary.total,171);
});
test('Avulso sem valor no quadro azul não recebe diária automaticamente no Financeiro',()=>{
 const ctx=mock({available:0,daily:120.87});
 assert.equal(ctx.compute()[0].extra,0);
 assert.equal(ctx.compute()[0].daily,120.87,'O custo operacional mantém meia diária');
});
test('Extra expressamente confirmada mantém Financeiro igual ao quadro azul, sem adicionar diária',()=>{
 const ctx=mock({available:80,extraLabel:'Meia diária'});
 const [row]=ctx.compute();
 assert.equal(row.extra,80);
 assert.equal(row.daily,241.74);
});
test('Extra independente registrada com valor disponível igual não é duplicada',()=>{
 const ctx=mock({available:150,extraAvulsa:true,extraOriginal:150});
 assert.equal(ctx.compute()[0].extra,150);
});
test('Colaborador regular recebe apenas o valor disponível, sem diária cadastral',()=>{
 const ctx=mock({avulso:'Não',available:100,daily:307.02});
 assert.equal(ctx.compute()[0].extra,100);
});
test('Complementos e adicionais legítimos são preservados, sem alterar custos operacionais',()=>{
 const ctx=mock({available:150,finance:20,bonus:25,night:10,passagem:11});
 const [row]=ctx.compute();
 assert.equal(row.extra,150);
 assert.equal(row.finance,20);
 assert.equal(row.bonus,25);
 assert.equal(row.night,10);
 assert.equal(row.ajudaCusto,11);
 const [summary]=ctx.APROARFinanceConsolidado.summarize(ctx.compute());
 assert.equal(summary.total,216);
});
test('Todas as saídas do Financeiro dependem do mesmo cálculo corrigido',()=>{
 const pay=app.slice(app.indexOf('  function renderPayments()'),app.indexOf('  function absenceRecords()'));
 const excel=app.slice(app.indexOf('  function financialWorkbook()'),app.indexOf('  function exportReportsExcel()'));
 assert.match(pay,/financialEntries\(\)/);
 assert.match(excel,/financialEntries\(\)/);
 assert.match(app,/function financialSummaryRows\(rows=financialEntries\(\)\)/);
});

test('Valor independente já registrado prevalece igual ao cartão azul do supervisor',()=>{
 const ctx=mock({available:80,extraLabel:'Meia diária',extraAvulsa:true,extraOriginal:95});
 assert.equal(ctx.compute()[0].extra,95);
 const [summary]=ctx.APROARFinanceConsolidado.summarize(ctx.compute());
 assert.equal(summary.total,95);
});
test('Sem valor no cartão azul nem extra independente, custo de serviço não gera pagamento para colaborador regular',()=>{
 const ctx=mock({avulso:'Não',available:0,daily:182.34,extraServico:91.17});
 assert.equal(ctx.compute()[0].extra,0);
 assert.equal(ctx.compute()[0].daily,182.34);
 assert.equal(ctx.compute()[0].extraServico,91.17);
});
test('Custo avulso de ajudante R$ 182,34 fica no serviço; quadro azul R$ 150,00 fica no Financeiro',()=>{
 const ctx=mock({daily:182.34,available:150,passagem:11});
 const [result]=ctx.compute();
 assert.equal(result.daily,182.34);
 assert.equal(result.extra,150);
 const [summary]=ctx.APROARFinanceConsolidado.summarize(ctx.compute());
 assert.equal(summary.total,161);
});
