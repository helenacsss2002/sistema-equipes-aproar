import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
function section(start,end){
 const a=app.indexOf(start),b=app.indexOf(end,a+start.length);
 assert(a>=0&&b>a,'Bloco da aplicação ausente');
 return app.slice(a,b);
}
const finance=section('  function financialEntries(){','  function financialSummaryRows(');
const ctx={
 roundMoney:v=>Math.round((Number(v)+Number.EPSILON)*100)/100,
 presence:status=>!['Falta','Atestado'].includes(status),
 reportFilters:{inicio:'2026-10-15',fim:'2026-10-19',supervisor:'Todos',obra:'Todas'},
 state:{apontamentos:[]},
 currentEntries:[],
 entries:()=>ctx.currentEntries,
};
ctx.globalThis=ctx;vm.createContext(ctx);
vm.runInContext(finance+'\nglobalThis.calcFinance=financialEntries;',ctx);

function row({id='1',date='2026-10-16',supervisor='EDUARDO',extraServico=0,extraAvulsa=false,extraOriginal=0,bonus=0,work='11'}={}){
 return {c:{dataServico:date,supervisor,unidade:'BARRA DO CEARÁ',obraId:work,...(extraAvulsa?{extraAvulsa:true}:{})},
 i:{colaboradorId:id,status:extraAvulsa?'Extra independente':'Presente (Integral)',valorExtraOriginal:extraOriginal},
 p:{id},refs:extraAvulsa?[]:[{colaboradorId:id}],daily:0,extra:extraServico,danger:0,finance:0,night:0,bonus,ajudaCusto:0};
}
test('Valor disponível paga no Financeiro com extra Não sem compor a extra de serviço',()=>{
 ctx.state.apontamentos=[{supervisor:'EDUARDO',dataServico:'2026-10-16',itens:[{colaboradorId:'1',status:'Presente (Integral)',extra:'Não',valorExtraDisponivel:100}]}];
 ctx.currentEntries=[row({bonus:20})];
 const res=ctx.calcFinance();
 assert.equal(res.length,1);
 assert.equal(res[0].extra,100);
 assert.equal(res[0].extraServico,0);
 assert.equal(res[0].bonus,20);
 assert.equal(res[0].extra+res[0].bonus,120);
});
test('Extra confirmada é custo do serviço por categoria, mas Financeiro usa valor azul sem duplicar',()=>{
 ctx.state.apontamentos=[{supervisor:'EDUARDO',dataServico:'2026-10-16',itens:[{colaboradorId:'1',status:'Presente (Integral)',extra:'Não',valorExtraDisponivel:150}]}];
 ctx.currentEntries=[row({bonus:5}),row({extraAvulsa:true,extraServico:241.74,extraOriginal:150})];
 const res=ctx.calcFinance();
 assert.equal(res.length,1);
 assert.equal(res[0].extraServico,241.74);
 assert.equal(res[0].extra,150);
 assert.equal(res[0].bonus,5);
 assert.equal(res[0].extra+res[0].bonus,155,'Não deve pagar duas vezes pela mesma extra');
});
test('Extra independente sem lançamento normal mantém o valor originalmente informado no Financeiro',()=>{
 ctx.state.apontamentos=[];
 ctx.currentEntries=[row({extraAvulsa:true,extraServico:241.74,extraOriginal:92.50})];
 const [res]=ctx.calcFinance();
 assert.equal(res.extra,92.50);
 assert.equal(res.extraServico,241.74);
});
test('Sem pagamento disponível, registros históricos com categoria de extra mantêm valor financeiro',()=>{
 ctx.state.apontamentos=[{supervisor:'EDUARDO',dataServico:'2026-10-16',itens:[{colaboradorId:'1',status:'Presente (Integral)',extra:'Meia diária',valorExtraDisponivel:0}]}];
 ctx.currentEntries=[row({extraServico:120.87})];
 const [res]=ctx.calcFinance();
 assert.equal(res.extra,120.87);
});
test('Relatórios usam fontes financeiras e operacionais separadas em tela, Excel e PDF',()=>{
 const rows=section('  function renderReports(){','  function renderDashboard(){');
 assert.match(rows,/financial\?financialEntries\(\):entries\(\)/);
 const worksheet=section('  function financialWorkbook(){','  function exportReportsExcel(){');
 assert.match(worksheet,/const data=financialEntries\(\)/);
 assert.match(app,/const serviceExtra=roundMoney\(dayCost\(p\)\*extraMultiplier\(x.extra\)\)/);
 assert.match(app,/daily:0,extra:serviceExtra/);
 const bind=section('  function bindServiceRows(){','  function validateAgreementObservations(');
 assert.match(bind,/const extra=moneyValue\('\.row-extra-value'\)/);
 assert.doesNotMatch(bind,/const extra=active\?moneyValue/);
 const control=section('  function controlWorkbook(){','  function indicatorReportData(){');
 assert.match(control,/const data=entries\(\)/);
});

test('Diária do avulso entra no financeiro e preserva os custos operacionais sem duplicação',()=>{
 ctx.state.apontamentos=[{supervisor:'EDUARDO',dataServico:'2026-10-16',itens:[
  {colaboradorId:'a1',status:'Presente (Integral)',extra:'Não',valorExtraDisponivel:0}
 ]}];
 ctx.currentEntries=[{...row({id:'a1',bonus:0}),p:{id:'a1',nome:'Avulso',avulso:'Sim'},daily:241.74}];
 const [result]=ctx.calcFinance();
 assert.equal(result.diariaAvulso,241.74);
 assert.equal(result.extra,241.74,'O custo do avulso compõe o valor a pagar ao financeiro');
 assert.equal(ctx.currentEntries[0].daily,241.74,'Custo do serviço permanece como diária original');
 ctx.state.apontamentos[0].itens[0].valorExtraDisponivel=80;
 assert.equal(ctx.calcFinance()[0].extra,321.74,'Diária do avulso e extra adicional são contabilizadas separadamente');
});
test('Colaborador regular não tem diária adicionada ao financeiro',()=>{
 ctx.state.apontamentos=[{supervisor:'EDUARDO',dataServico:'2026-10-16',itens:[
  {colaboradorId:'1',status:'Presente (Integral)',extra:'Não',valorExtraDisponivel:70}
 ]}];
 ctx.currentEntries=[{...row(),p:{id:'1',avulso:'Não'},daily:200}];
 assert.equal(ctx.calcFinance()[0].extra,70);
});
test('Pagamento avulso não existe para falta ou atestado',()=>{
 ctx.state.apontamentos=[];
 ctx.currentEntries=[{...row({id:'a1'}),p:{id:'a1',avulso:'Sim'},daily:0,i:{colaboradorId:'a1',status:'Falta'}}];
 assert.equal(ctx.calcFinance()[0].extra,0);
});
