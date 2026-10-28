import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=app.indexOf("  const DRAFT_PREFIX='aproar:apontamento:rascunho:v1:';");
const end=app.indexOf("  const dayUnsavedDrafts=new Map();",start);
assert(start>0&&end>start,'A persistência base deve estar disponível');

function localHarness(){
 const data=new Map();
 const storage={
  get length(){return data.size;},
  key:i=>[...data.keys()][i]??null,
  getItem:key=>data.get(key)??null,
  setItem:(key,value)=>{data.set(key,String(value));},
  removeItem:key=>{data.delete(key);}
 };
 const context={localStorage:storage,onlineVersion:'neon-v1',Date,console,showToast:()=>{}};
 vm.createContext(context);
 vm.runInContext(app.slice(start,end)+"\nglobalThis.drafts={key:draftKey,store:storeDraft,read:readStoredDraft,clear:clearStoredDraft,logout:clearSupervisorDrafts};",context);
 return {api:context.drafts,context,data};
}
const supervisor='FELIPE',date='2026-10-29',unit='SÃO GONÇALO DO AMARANTE';

test('Rascunho preserva seleções, turno, pesquisa e avulsos após F5',()=>{
 const {api,data}=localHarness(),key=api.key('convocacao',supervisor,date,unit);
 const before={
  supervisor,date,unit,turn:'Tarde',func:'Servente',search:'João',
  selected:['71','72'],referenceDate:'2026-10-28',
  avulsos:[{id:'avulso-qa',nome:'Pessoa avulsa QA',funcao:'Profissional'}],
  avulsoName:'Outro nome parcial',avulsoFunction:'Servente',previousSelected:['71']
 };
 assert.equal(api.store(key,before),true);
 const recovered=api.read(key);
 assert.equal(recovered.version,'neon-v1');
 assert.deepEqual(JSON.parse(JSON.stringify(Object.fromEntries(Object.keys(before).map(k=>[k,recovered[k]])))),before);
 assert.equal(data.size,1);
});

test('Mantém rascunhos isolados por unidade, supervisor, dia e modo',()=>{
 const {api}=localHarness();
 const keys=[
  api.key('convocacao','FELIPE','2026-10-29','CENTRO'),
  api.key('convocacao','FELIPE','2026-10-29',unit),
  api.key('convocacao','FELIPE','2026-10-30','CENTRO'),
  api.key('convocacao','VICTOR','2026-10-29','CENTRO'),
  api.key('normal','FELIPE','2026-10-29','CENTRO')
 ];
 assert.equal(new Set(keys).size,keys.length);
 keys.forEach((k,i)=>api.store(k,{marker:i}));
 assert.deepEqual(keys.map(k=>api.read(k).marker),[0,1,2,3,4]);
 api.clear(keys[1]);
 assert.equal(api.read(keys[1]),null);
 for(const i of [0,2,3,4])assert.equal(api.read(keys[i]).marker,i);
});

test('Mudança da versão exige recuperação explícita antes de editar',()=>{
 const {api,context}=localHarness(),key=api.key('convocacao',supervisor,date,unit);
 api.store(key,{selected:['71'],turn:'Integral'});
 context.onlineVersion='neon-v2';
 assert.equal(api.read(key).version,'neon-v1');
 const code=app.slice(app.indexOf('  function renderUnitConvocacao(){'),app.indexOf('  function operationalRows(',app.indexOf('  function renderUnitConvocacao(){')));
 assert.match(code,/saved\.version===onlineVersion/);
 assert.match(code,/unresolvedConvDraft=saved;form\.inert=true/);
 assert.match(code,/Recuperar rascunho para conferência/);
 assert.match(code,/Descartar rascunho local/);
 assert.match(code,/window\.confirm\('O banco foi atualizado/);
 assert.match(code,/form\.before\(convStatus\)/);
});

test('Campos são salvos automaticamente sem chamadas de gravação ao Neon',()=>{
 const code=app.slice(app.indexOf('  function renderUnitConvocacao(){'),app.indexOf('  function operationalRows(',app.indexOf('  function renderUnitConvocacao(){')));
 for(const needle of [
  'const storeConvDraft=()=>',
  'storeDraft(activeConvKey,data)',
  "form.addEventListener('input'",
  "form.addEventListener('change'",
  'storeConvDraft();unitConvDate=',
  'switchConvDraftUnit()',
  "storeConvDraft();toast('Equipe carregada",
  'avulsoList();storeConvDraft();',
  'storeConvDraft();\n      reviewBox.innerHTML=',
  'selected:[...selected]',
  'previousSelected:',
  'avulsos:avulsoDraft.map'
 ])assert(code.includes(needle),needle);
 const block=code.slice(code.indexOf('const storeConvDraft=()=>'),code.indexOf('const restoreConvDraft='));
 assert.doesNotMatch(block,/saveData\(|api\(|\/api\/save|state\.convocacoes\.push/);
});

test('Revisão não confirma: somente confirmação definitiva e retorno positivo do banco apagam rascunho',()=>{
 const code=app.slice(app.indexOf('  function renderUnitConvocacao(){'),app.indexOf('  function operationalRows(',app.indexOf('  function renderUnitConvocacao(){')));
 const review=code.indexOf('form.onsubmit=e=>'),final=code.indexOf("$('#unit-conv-final').onclick=()=>");
 assert(review>=0&&final>review);
 const preview=code.slice(review,final);
 assert.match(preview,/reviewDraft=draft/);
 assert.match(preview,/reviewBox\.innerHTML=convocationReviewMarkup\(draft\)/);
 assert.doesNotMatch(preview,/state\.convocacoes\.push|saveData\(/);
 const finish=code.slice(final);
 assert.match(finish,/state\.convocacoes\.push/);
 assert.match(finish,/saveData\(\(\)=>\{/);
 assert.match(finish,/clearStoredDraft\(confirmedKey\)/);
 assert.match(finish,/clearStoredDraft\(convLastKey\(supervisorAtual\)\)/);
 assert.match(finish,/if\(!queued\)return/);
});
