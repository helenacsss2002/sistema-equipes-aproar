import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const helperStart=app.indexOf("  const SUPERVISOR_VIEW_KEY_PREFIX=");
const helperEnd=app.indexOf("  let retroDateSelected=",helperStart);
assert.ok(helperStart>0&&helperEnd>helperStart,'Persistência da aba precisa existir');

function harness(){
  const data=new Map();
  const sessionStorage={
    setItem:(key,value)=>data.set(key,String(value)),
    getItem:key=>data.get(key)??null,
    removeItem:key=>data.delete(key)
  };
  const context={sessionStorage,perfilAtual:'SUPERVISOR',supervisorAtual:'FELIPE',viewAtual:'convocacao'};
  vm.createContext(context);
  vm.runInContext(app.slice(helperStart,helperEnd)+
    '\nglobalThis.viewState={saveSupervisorView,restoredSupervisorView};',context);
  return {context,storage:data,api:context.viewState};
}
test('Ao atualizar a página, supervisor retorna à Convocação, não a Apontamentos',()=>{
  const {context,api}=harness();
  api.saveSupervisorView();
  context.viewAtual='apontamento';
  assert.equal(api.restoredSupervisorView(),'convocacao');
  const other=harness();other.context.supervisorAtual='VICTOR';
  assert.equal(other.api.restoredSupervisorView(),'apontamento');
});
test('A aba é isolada por supervisor e não substitui uma nova sessão',()=>{
  const {context,api,storage}=harness();
  api.saveSupervisorView('convocacao');
  context.supervisorAtual='EDUARDO';
  assert.equal(api.restoredSupervisorView(),'apontamento');
  api.saveSupervisorView('disponibilidade');
  assert.equal(storage.size,2);
  context.supervisorAtual='FELIPE';
  assert.equal(api.restoredSupervisorView(),'convocacao');
  context.perfilAtual='CONTROLADORIA';
  assert.equal(api.restoredSupervisorView(),'apontamento');
  api.saveSupervisorView('convocacao');
  assert.equal(storage.size,2);
});
test('Inicialização reabre aba salva; pageshow não causa reload; logout limpa a preferência',()=>{
  const set=app.slice(app.indexOf('  function setView('),app.indexOf('  function render()'));
  const online=app.slice(app.indexOf('  function enterConnectedSession('),app.indexOf('  async function initOnline('));
  const logout=app.slice(app.indexOf('  async function logout('),app.indexOf('  const renderLocal=render;'));
  assert.match(set,/saveSupervisorView\(viewAtual\)/);
  assert.match(online,/restoredSupervisorView\(\)/);
  assert.match(logout,/removeItem\(supervisorViewStorageKey\(supervisorAtual\)\)/);
  assert.doesNotMatch(app,/window\.location\.reload\(\)/);
  assert.match(app,/window\.addEventListener\('pagehide',\(\)=>saveSupervisorView\(\)\)/);
  assert.match(html,/app\.js\?v=aproar-convocacao-sem-reload-20261104-11/);
});
test('Recarregamento recupera os nomes, turno e avulsos sem confirmar automaticamente',()=>{
  const code=app.slice(app.indexOf('  function renderUnitConvocacao()'),app.indexOf('  function operationalRows('));
  assert.match(code,/const saved=readStoredDraft\(activeConvKey\)/);
  assert.match(code,/if\(restoreConvDraft\(saved\)\)\{/);
  assert.match(code,/saved\.version!==onlineVersion/);
  assert.match(code,/storeDraft\(activeConvKey,data\)/);
  assert.match(code,/form\.addEventListener\('input'/);
  assert.match(code,/form\.addEventListener\('change'/);
  const review=code.indexOf('form.onsubmit=e=>'),confirm=code.indexOf("$('#unit-conv-final').onclick=()=>");
  assert.ok(review>0&&confirm>review);
  assert.doesNotMatch(code.slice(review,confirm),/state\.convocacoes\.push/);
  assert.match(code.slice(confirm),/confirmed=>convocationRecordsConfirmed\(confirmed,approved\)/);
  assert.doesNotMatch(code.slice(confirm),/setView\('inicio'\)/);
});

// O navegador nunca pode enviar a Convocação por GET, mesmo quando um erro
// impede a montagem de componentes auxiliares ou a recuperação do rascunho.
test('Falha na montagem não provoca recarregamento ou saída da Convocação',()=>{
  const conv=app.slice(app.indexOf('  function renderUnitConvocacao(){'),app.indexOf('  function operationalRows('));
  const init=app.slice(app.indexOf('  async function initOnline(){'));
  assert.match(conv,/<form id="unit-conv-form"[^>]*onsubmit="return false;"/);
  assert.match(init,/document\\.addEventListener\\('submit',event=>\\{/);
  assert.match(init,/event\\.preventDefault\\(\\)/);
  assert.match(init,/event\\.target\\.id==='unit-conv-form'/);
  assert.match(init,/addEventListener\\('submit',[\\s\\S]+,true\\)/);
  const handler=conv.indexOf('form.onsubmit=e=>');
  const restore=conv.lastIndexOf('try{loadConvDraft();}');
  assert.ok(handler>0&&restore>handler,'Somente recuperar rascunho depois de instalar o submit seguro');
  assert.match(conv,/form\\.dataset\\.aproarBound='1'/);
  assert.match(conv,/catch\\(draftError\\)/);
});
