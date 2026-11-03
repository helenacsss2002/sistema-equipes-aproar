import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const begin=app.indexOf('  async function refreshFinancialReleaseInputs(');
const end=app.indexOf('  function cycleControl()',begin);
assert.ok(begin>0&&end>begin);
const helper=app.slice(begin,end);

async function simulate(requests){
 const passage={readOnly:true,title:''},night={disabled:true},noticeState={value:null};
 const card={dataset:{person:'71',financeAdjusted:'true',unit:'SEBRAE'},
  querySelector(selector){
   if(selector==='.row-ajuda-custo')return passage;
   if(selector==='.row-noturno')return night;
   if(selector==='.finance-approved-bundle')return noticeState.value;
   if(selector==='.person-name')return {insertAdjacentElement(_,element){noticeState.value=element;}};
   return null;
  }};
 const form={isConnected:true,querySelectorAll(selector){assert.equal(selector,'.person-card');return [card]}};
 const ctx={perfilAtual:'SUPERVISOR',supervisorAtual:'VICTOR',
  financeReleaseRequests:[],
  api:async url=>{assert.equal(url,'/api/financial-release');return {requests}},
  isApprovedFinancial:(date,id,type)=>ctx.financeReleaseRequests.some(x=>x.status==='Autorizada'&&
    x.supervisor==='VICTOR'&&x.colaboradorId==='71'&&x.dataServico===date&&x.fields.includes(type)),
  isFinancialEditingLocked:()=>true,
  document:{createElement:()=>({className:'',textContent:''})},
  console:{warn:()=>{}}
 };
 vm.createContext(ctx);
 vm.runInContext(helper+'\nglobalThis.testRefresh=refreshFinancialReleaseInputs;',ctx);
 await ctx.testRefresh(form,'2026-10-31','VICTOR');
 return {passage,night,notice:noticeState.value};
}

test('Aprovação Financeiro das três colunas desbloqueia passagem ao abrir apontamento, sem liberar noturno',async()=>{
 const r=await simulate([{status:'Autorizada',supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-31',
  fields:['Extra','Bonificação','Passagem / ajuda de custo']}]);
 assert.equal(r.passage.readOnly,false);
 assert.equal(r.night.disabled,true);
 assert.match(r.notice.textContent,/Extra, Bonificações e Passagens/);
});

test('Solicitação pendente, utilizada ou autorização de outro colaborador não desbloqueia',async()=>{
 for(const req of [
  {status:'Pendente',supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-31',fields:['Extra','Bonificação','Passagem / ajuda de custo']},
  {status:'Utilizada',supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-31',fields:['Extra','Bonificação','Passagem / ajuda de custo']},
  {status:'Autorizada',supervisor:'VICTOR',colaboradorId:'72',dataServico:'2026-10-31',fields:['Extra','Bonificação','Passagem / ajuda de custo']}
 ]){
  const r=await simulate([req]);
  assert.equal(r.passage.readOnly,true);
  assert.equal(r.night.disabled,true);
  assert.equal(r.notice,null);
 }
});

test('Apontamento normal e retroativo consultam autorização ao abrir a ficha',()=>{
 assert.match(app,/refreshFinancialReleaseInputs\(\$\('#day-form'\),portalDate,supervisorAtual\)/);
 assert.match(app,/refreshFinancialReleaseInputs\(\$\('#form-retro'\),retroDate,retroSupervisor\)/);
 assert.match(app,/autorização do Financeiro para Extra, Bonificação ou Passagem/);
 assert.match(app,/Esta aprovação liberará Extra, Bonificações e Passagens/);
});
