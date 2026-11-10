import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const helperStart=app.indexOf('  function splitMoneyExactly(');
const end=app.indexOf('  function financialSummaryRows(',helperStart);
assert.ok(helperStart>0&&end>helperStart,'Rateio monetário e financeiro não encontrados');
const source=app.slice(helperStart,end);

const roundMoney=v=>Math.round((Number(v)+Number.EPSILON)*100)/100;
function fixture({servicos=3,passagem=11,acordo=0,noturno=0}={}){
  const person={id:'65',nome:'JOAO BATISTA MARTINS',avulso:null,valorDiaria:247.88};
  const item={
    colaboradorId:'65',status:'Presente (Integral)',ajudaCusto:passagem,acordo,
    noturno,financeiro:0,extra:'Não',valorExtraDisponivel:250
  };
  const c={id:'2241',dataServico:'2026-11-02',supervisor:'EDUARDO',obraId:'298',unidade:'SENAI',turno:'Integral'};
  const ss=Array.from({length:servicos},(_,i)=>({obraId:String(298+i),periodo:'Integral'}));
  const works=new Map(ss.map(s=>[s.obraId,{id:s.obraId,unidade:noturno?'SEBRAE':'SENAI'}]));
  const ctx={
    state:{convocacoes:[c],extras:[],apontamentos:[{dataServico:c.dataServico,supervisor:c.supervisor,itens:[item]}]},
    reportFilters:{inicio:'2026-11-02',fim:'2026-11-08',supervisor:'Todos',obra:'Todas'},
    selectedCycle:'custom',onlineSaving:false,onlineQueued:false,locked:false,saveCalls:0,
    saveFinancialUpdates:refs=>{ctx.saveCalls++;ctx.saved=refs;},
    showToast:message=>{throw Error('Unexpected toast: '+message)},
    roundMoney,clean:v=>String(v).toUpperCase(),
    apForConv:id=>id==='2241'?{itens:[item]}:null,
    colaboradorById:id=>id==='65'?person:null,
    serviceList:()=>ss,
    obraById:id=>works.get(String(id))||{unidade:'SENAI'},
    presence:status=>status?.startsWith('Presente'),
    periodBlocks:()=>({integral:1}),presenceBlocks:()=>({integral:1}),
    nocturnal:()=>noturno,dayCost:p=>p.valorDiaria,
    extraMultiplier:()=>0,dangerEligible:()=>false,
    financialCycle:()=>({pagamento:'2026-11-10'}),
    financialCycleReference:()=> '2026-11-08'
  };
  vm.createContext(ctx);
  vm.runInContext(source+'\nglobalThis.makeEntries=entries;globalThis.makeFinance=financialEntries;globalThis.split=splitMoneyExactly;',ctx);
  const adjustmentStart=app.indexOf('  function adjustPayment(');
  const adjustmentEnd=app.indexOf('  function financialCycle(',adjustmentStart);
  vm.runInContext(app.slice(adjustmentStart,adjustmentEnd)+'\nglobalThis.adjust=adjustPayment;',ctx);
  return ctx;
}
test('João Batista 02/11: 3 obras com passagem de R$ 11 geram exatamente R$ 11,00 no Financeiro',()=>{
 const ctx=fixture();
 const services=Array.from(ctx.makeEntries());
 assert.equal(services.length,3);
 assert.deepEqual(services.map(s=>s.ajudaCusto),[3.67,3.67,3.66]);
 assert.equal(roundMoney(services.reduce((acc,s)=>acc+s.ajudaCusto,0)),11);
 const financial=Array.from(ctx.makeFinance());
 assert.equal(financial.length,1);
 assert.equal(financial[0].extra,250);
 assert.equal(roundMoney(financial[0].ajudaCusto),11);
 assert.equal(roundMoney(financial[0].extra+financial[0].ajudaCusto),261);
});
test('Alterar R$ 11,01 para R$ 11,00 não recria o centavo ao atualizar a tela',()=>{
 const ctx=fixture({passagem:11.01});
 assert.equal(roundMoney(ctx.makeFinance()[0].ajudaCusto),11.01);
 ctx.adjust(ctx.makeFinance()[0],'ajudaCusto','11');
 assert.equal(ctx.saveCalls,1);
 assert.equal(ctx.saved.length,1,'Só um apontamento original deve ser salvo, independentemente das obras');
 assert.equal(ctx.saved[0].ajudaCusto,11);
 assert.equal(roundMoney(ctx.makeFinance()[0].ajudaCusto),11);
});
test('Rateio conserva todos os centavos em números variáveis de obras',()=>{
 const ctx=fixture();
 for(const n of [1,2,3,4,5,7,10,13]){
  for(const amount of [0,0.01,0.02,1,10,11,11.01,21,182.34,250.01]){
   const values=Array.from(ctx.split(amount,n));
   assert.equal(values.length,n);
   assert.equal(roundMoney(values.reduce((acc,v)=>acc+v,0)),amount,amount+' em '+n+' serviços');
  }
 }
});
test('Bonificação e adicional noturno também não podem gerar centavos fictícios',()=>{
 const ctx=fixture({servicos:3,passagem:11,acordo:10,noturno:20});
 const service=Array.from(ctx.makeEntries()),financial=Array.from(ctx.makeFinance())[0];
 assert.equal(roundMoney(service.reduce((sum,r)=>sum+r.ajudaCusto,0)),11);
 assert.equal(roundMoney(service.reduce((sum,r)=>sum+r.bonus,0)),10);
 assert.equal(roundMoney(service.reduce((sum,r)=>sum+r.night,0)),20);
 assert.equal(roundMoney(financial.ajudaCusto),11);
 assert.equal(roundMoney(financial.bonus),10);
 assert.equal(roundMoney(financial.night),20);
});
test('O custo cadastral do serviço permanece intacto, independente da passagem',()=>{
 const ctx=fixture();
 const service=Array.from(ctx.makeEntries());
 assert.equal(roundMoney(service.reduce((sum,r)=>sum+r.daily,0)),247.88);
 assert.equal(ctx.makeFinance()[0].extra,250);
});
