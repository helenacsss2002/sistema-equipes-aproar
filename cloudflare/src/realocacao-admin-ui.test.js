import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const begin=app.indexOf('  function relocateAdminPerson(');
const end=app.indexOf('  function removeConvPerson(',begin);
assert.ok(begin>=0&&end>begin,'Realocação segura deve existir no formulário');
const fnSource=app.slice(begin,end)+'\nglobalThis.relocateAdminPerson=relocateAdminPerson;';

function harness(pointed=false){
 const state={convocacoes:[
  {id:'401',supervisor:'EDUARDO',dataServico:'2026-10-14',unidade:'FIEC',obraId:'1',turno:'Integral',colaboradores:['1']},
  {id:'402',supervisor:'VICTOR',dataServico:'2026-10-14',unidade:'FIEC',obraId:'2',turno:'Integral',colaboradores:['2']}
 ],apontamentos:pointed?[{id:'pt1',convocacaoId:'401',dataServico:'2026-10-14',supervisor:'EDUARDO',itens:[{
  colaboradorId:'1',status:'Presente (Integral)',financeiro:50,acordo:10,noturno:0,ajudaCusto:11,servicos:[{obraId:'1',periodo:'Integral'}]
 }]}]:[]};
 const context={state,OBRAS:[{id:'1',unidade:'FIEC'},{id:'2',unidade:'FIEC'},{id:'3',unidade:'SEBRAE'}],
  apForConv:id=>state.apontamentos.find(x=>x.convocacaoId===id),
  presence:status=>status.startsWith('Presente'),now:()=>new Date('2026-10-14T10:00:00Z')};
 context.globalThis=context;vm.createContext(context);
 vm.runInContext(fnSource,context);
 return {...context,entry:{c:state.convocacoes[0],id:'1'},target:{dataServico:'2026-10-14',supervisor:'FELIPE',unidade:'SEBRAE',obraId:'3',turno:'Noite'}};
}

test('Realocação sem apontamento atualiza conv original e preserva as outras convocações',()=>{
 const {state,relocateAdminPerson,entry,target}=harness();
 const original=state.convocacoes[0];
 const result=relocateAdminPerson(entry,target);
 assert.equal(result.ok,true);
 assert.strictEqual(state.convocacoes[0],original);
 assert.equal(state.convocacoes.length,2);
 assert.equal(state.convocacoes[0].id,'401');
 assert.equal(state.convocacoes[0].supervisor,'FELIPE');
 assert.equal(state.convocacoes[0].unidade,'SEBRAE');
 assert.equal(state.convocacoes[0].turno,'Noite');
 assert.equal(state.convocacoes[1].id,'402');
});

test('Mudar unidade de colaborador apontado não exclui a convocação nem os dados financeiros',()=>{
 const {state,relocateAdminPerson,entry,target}=harness(true);
 const before=structuredClone(state);
 const result=relocateAdminPerson(entry,target);
 assert.equal(result.ok,false);
 assert.match(result.message,/histórico financeiro/);
 assert.deepEqual(JSON.parse(JSON.stringify(state)),before);
});

test('Realocação com apontamento para outra obra da mesma unidade preserva ID, data e valores',()=>{
 const {state,relocateAdminPerson,entry,target}=harness(true);
 Object.assign(target,{unidade:'FIEC',obraId:'2',turno:'Integral'});
 const result=relocateAdminPerson(entry,target);
 assert.equal(result.ok,true);
 assert.equal(state.convocacoes[0].id,'401');
 assert.equal(state.apontamentos[0].id,'pt1');
 assert.equal(state.apontamentos[0].convocacaoId,'401');
 assert.equal(state.apontamentos[0].itens[0].financeiro,50);
 assert.equal(state.apontamentos[0].itens[0].acordo,10);
 assert.equal(state.apontamentos[0].itens[0].ajudaCusto,11);
 assert.equal(state.apontamentos[0].itens[0].servicos[0].obraId,'2');
});

test('Formulário administrativo não remove a convocação e cria outra ao salvar realocação',()=>{
 const block=app.slice(app.indexOf('  function renderAdminConv('),app.indexOf('  function removeConvPerson('));
 assert.match(block,/relocateAdminPerson\(x,/);
 assert.doesNotMatch(block,/const newid=uid\('cv'\)/);
 assert.match(block,/if\(!result\.ok\)return toast\(result\.message,true\)/);
});
