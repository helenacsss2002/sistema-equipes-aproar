import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const helperStart=app.indexOf('  function financialReleasePeopleFor(');
const helperEnd=app.indexOf('  function renderFinancialReleases(){',helperStart);
assert.ok(helperStart>0&&helperEnd>helperStart,'Consulta pesquisável de colaboradores não encontrada');
const helper=app.slice(helperStart,helperEnd);
const render=app.slice(helperEnd,app.indexOf('  function renderPayments(){',helperEnd));
const sort=(a,b)=>String(a.nome).localeCompare(String(b.nome),'pt-BR',{sensitivity:'base'});
const clean=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim();
function context(){
 const state={convocacoes:[
  {supervisor:'FELIPE',dataServico:'2026-11-03',colaboradores:[71,'23',22]},
  {supervisor:'FELIPE',dataServico:'2026-11-03',colaboradores:['22']},
  {supervisor:'VICTOR',dataServico:'2026-11-03',colaboradores:['88']},
  {supervisor:'FELIPE',dataServico:'2026-11-04',colaboradores:['66']}
 ]};
 const COLABORADORES=[
  {id:'71',nome:'IVONEUDO FERREIRA DA SILVA'},
  {id:'22',nome:'Bruna Oliveira'},
  {id:'23',nome:'Álvaro Silva'},
  {id:'88',nome:'André Victor'},
  {id:'66',nome:'Cleandro'}
 ];
 const ctx={state,COLABORADORES,supervisorAtual:'FELIPE',clean,alphabeticalPeople:people=>[...people].sort(sort)};
 vm.createContext(ctx);
 vm.runInContext(helper+';globalThis.getCandidates=financialReleasePeopleFor;',ctx);
 return ctx;
}
test('Colaboradores do dia e supervisor vêm alfabeticamente, mesmo com IDs numéricos e duplicados',()=>{
 const ctx=context();
 assert.deepEqual(Array.from(ctx.getCandidates('2026-11-03'),p=>p.nome),
  ['Álvaro Silva','Bruna Oliveira','IVONEUDO FERREIRA DA SILVA']);
});
test('Busca instantânea ignora acentos e diferenciais de maiúsculas/minúsculas',()=>{
 const ctx=context();
 assert.deepEqual(Array.from(ctx.getCandidates('2026-11-03','alva'),p=>p.nome),['Álvaro Silva']);
 assert.deepEqual(Array.from(ctx.getCandidates('2026-11-03','oliveira'),p=>p.nome),['Bruna Oliveira']);
 assert.deepEqual(Array.from(ctx.getCandidates('2026-11-03','ivon'),p=>p.nome),['IVONEUDO FERREIRA DA SILVA']);
 assert.deepEqual(Array.from(ctx.getCandidates('2026-11-03','não-existe'),p=>p.nome),[]);
});
test('Datas e supervisores diferentes não permitem selecionar colaboradores indevidos',()=>{
 const ctx=context();
 assert.equal(ctx.getCandidates('2026-11-02').length,0);
 assert.deepEqual(Array.from(ctx.getCandidates('2026-11-03','', 'VICTOR'),p=>p.nome),['André Victor']);
 assert.deepEqual(Array.from(ctx.getCandidates('2026-11-04'),p=>p.nome),['Cleandro']);
});
test('Lista do formulário tem busca em tempo real e explica quando não houve convocação',()=>{
 assert.match(render,/id="fr-person-search" type="search"/);
 assert.match(render,/id="fr-person" aria-label="Selecione o colaborador" required/);
 assert.match(render,/id="fr-person-info" class="help-text" aria-live="polite"/);
 assert.match(render,/\$\('#fr-person-search'\)\.oninput=\(\)=>\{/);
 assert.match(render,/select\.size=search\.value\.trim\(\)\?Math\.min\(8,Math\.max\(2,matches\.length\+1\)\):1/);
 assert.match(render,/Nenhum colaborador convocado por /);
 assert.match(render,/state\.convocacoes\.filter\(c=>c\.supervisor===supervisorAtual&&c\.dataServico<=isoToday\(\)\)/);
 assert.match(render,/String\(p\.id\)===id/);
 assert.match(render,/const all=financialReleasePeopleFor\(date\),matches=financialReleasePeopleFor\(date,search\.value\)/);
 assert.doesNotMatch(render,/ids\.includes\(p\.id\)/);
});
test('Solicitação continua vinculada a data, colaborador e permissões do servidor',()=>{
 const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
 assert.match(worker,/if\(session\.role!=='SUPERVISOR'\)return json/);
 assert.match(worker,/AND c\.data=\$\{parsed\.dataServico\}::date AND c\.engenheiro=\$\{session\.user\}/);
 assert.match(worker,/if\(!matched\)return json\(\{error:'Colaborador ou avulso sem convocação/);
});
