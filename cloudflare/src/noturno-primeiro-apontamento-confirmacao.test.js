import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=ui.indexOf('  function nightChangesToVerify(previous,next){');
const end=ui.indexOf('  function saveData(onSuccess=null){',start);
assert(start>=0&&end>start);
const ctx={};vm.createContext(ctx);
vm.runInContext(ui.slice(start,end)+'\nglobalThis.helpers={changes:nightChangesToVerify,match:nightValuesMatch}',ctx);
const {changes,match}=ctx.helpers;
const point=(night)=>({apontamentos:[{convocacaoId:'22',itens:[{colaboradorId:'31',noturno:night}]}]});

test('Primeiro apontamento do colaborador no SEBRAE verifica o valor exato 50/90',()=>{
 for(const value of [50,90]){
  const before={convocacoes:[{id:'22'}],apontamentos:[]};
  const wanted=changes(before,point(value));
  assert.equal(wanted.length,1);
  assert.equal(wanted[0].expected,value);
  assert.equal(match(point(0),wanted),false,'Não aceitar confirmação se o Neon não registrar o valor');
  assert.equal(match(point(90===value?50:90),wanted),false);
  assert.equal(match(point(value),wanted),true);
 }
});

test('Primeiro apontamento de zero e convocação criada no mesmo envio não geram falso erro de confirmação',()=>{
 assert.equal(changes({convocacoes:[{id:'22'}],apontamentos:[]},point(0)).length,0);
 assert.equal(changes({convocacoes:[],apontamentos:[]},point(90)).length,0);
});

test('Alteração de adicional 90 para 0 ou 50 nunca é confirmada com valor divergente',()=>{
 for(const value of [0,50]){
  const wanted=changes(point(90),point(value));
  assert.equal(wanted.length,1);
  assert.equal(match(point(90),wanted),false);
  assert.equal(match(point(value),wanted),true);
 }
});

test('Controladoria pode escolher valor em apontamento previamente ajustado pelo Financeiro sem afrouxar permissão do Supervisor',()=>{
 const start=ui.indexOf('  function personRow('),end=ui.indexOf('  // Busca viva independente',start);
 const body=ui.slice(start,end);
 assert.match(body,/String\(unit\|\|''\)\.trim\(\)\.toUpperCase\(\)==='SEBRAE'/);
 assert.match(body,/perfilAtual!=='SUPERVISOR'\|\|!item\?\.financeAdjusted\|\|isApprovedFinancial/);
 const defaultContext={
  colaboradorById:()=>({nome:'TESTE SEBRAE',funcao:'Pedreiro',avulso:'Não'}),
  itemServices:()=>[{obraId:'1',periodo:'Integral'}],extraRecordFor:()=>null,
  EXTRA_OPTIONS:['Não'],APONTAMENTO_EXTRA_OPTIONS:[['Não','Não']],
  STATUS_OPTIONS:['Presente (Integral)'],
  OBRAS:[{id:'1',nome:'SEBRAE',unidade:'SEBRAE'}],
  obraById:()=>({id:'1',nome:'SEBRAE',unidade:'SEBRAE'}),
  field:(_label,html)=>html,
  allocationRow:()=>'',extraWorkSearchMarkup:()=>'',roundMoney:n=>Math.round(n*100)/100,
  escapeHtml:x=>String(x??''),presence:x=>x.startsWith('Presente'),
  clean:s=>String(s).toUpperCase(),isApprovedFinancial:()=>false,
  perfilAtual:'CONTROLADORIA',portalDate:'2026-09-12',supervisorAtual:'SOARES'
 };
 const build=(role,allowed=false)=>{
  const env={...defaultContext,perfilAtual:role,isApprovedFinancial:()=>allowed};
  vm.createContext(env);
  vm.runInContext(body+'\nglobalThis.row=personRow;',env);
  return env.row('31',{noturno:50,financeAdjusted:true,status:'Presente (Integral)'},'SEBRAE','1');
 };
 const select=html=>html.match(/<select class="control row-noturno"[^>]*>/)?.[0]||'';
 assert.doesNotMatch(select(build('CONTROLADORIA')),/disabled/);
 assert.doesNotMatch(select(build('FINANCEIRO')),/disabled/);
 assert.match(select(build('SUPERVISOR')),/disabled/);
 assert.doesNotMatch(select(build('SUPERVISOR',true)),/disabled/);
 assert.match(build('CONTROLADORIA'),/<option value="50" selected>/);
});

test('Salvamento final continua dependendo do botão e da confirmação do servidor',()=>{
 assert.match(ui,/const pendingNightChanges=nightChangesToVerify\(onlineConfirmed,state\)/);
 assert.match(ui,/nightValuesMatch\(result.state,pendingNightChanges\)/);
 assert.match(ui,/O adicional noturno selecionado não corresponde ao valor retornado pelo Neon/);
 assert.match(ui,/if\(typeof onSuccess==='function'\)/);
});
