import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');

function storageHarness(){
 const begin=app.indexOf("  const DRAFT_PREFIX='aproar:apontamento:rascunho:v1:';");
 const end=app.indexOf('  const dayUnsavedDrafts=new Map();',begin);
 assert(begin>0&&end>begin);
 const data=new Map();
 const localStorage={
  get length(){return data.size;},key(i){return [...data.keys()][i]??null;},
  setItem(k,v){data.set(k,v);},getItem:k=>data.get(k)??null,removeItem:k=>data.delete(k)
 };
 const ctx={localStorage,Date,console,onlineVersion:'v1',showToast:()=>{}};
 vm.createContext(ctx);
 vm.runInContext(app.slice(begin,end)+"\nglobalThis.drafts={key:draftKey,store:storeDraft,read:readStoredDraft,clear:clearStoredDraft,clearSupervisor:clearSupervisorDrafts};",ctx);
 return {api:ctx.drafts,ctx,data};
}
test('O rascunho local sobrevive F5 e preserva duas fichas, extras e avulsos',()=>{
 const {api,data}=storageHarness(),key=api.key('normal','FELIPE','2026-10-28','CENTRO');
 const rows=[{colaboradorId:'71',status:'Presente (Integral)',acordo:50,noturno:90,ajudaCusto:11,servicos:[{obraId:'154',periodo:'Integral'}],extraLancamento:{enabled:true,extra:'Diária',valorExtraOriginal:130,obraId:'154'}},{colaboradorId:'170',status:'Falta',acordo:0}];
 assert.equal(api.store(key,{items:rows,extra:{amount:'130',obs:'Urgente'},pending:[{id:'170',dayKey:'2026-10-28|FELIPE',selectedUnit:'CENTRO'}]}),true);
 assert.deepEqual(JSON.parse(JSON.stringify(api.read(key).items)),rows);
 assert.equal(api.read(key).extra.obs,'Urgente');
 assert.equal(api.read(key).pending[0].id,'170');
 assert.equal(data.size,1);
});
test('Cada supervisor e data tem rascunho isolado; logout apaga apenas o supervisor',()=>{
 const {api}=storageHarness();
 const keys=[api.key('normal','FELIPE','2026-10-28','CENTRO'),api.key('normal','VICTOR','2026-10-28','CENTRO'),api.key('normal','FELIPE','2026-10-27','CENTRO'),api.key('retroativo','FELIPE')];
 assert.equal(new Set(keys).size,4);
 keys.forEach((k,i)=>api.store(k,{marker:i}));
 assert.deepEqual(keys.map(k=>api.read(k).marker),[0,1,2,3]);
 api.clearSupervisor('FELIPE');
 assert.equal(api.read(keys[1]).marker,1);
 for(const k of [keys[0],keys[2],keys[3]])assert.equal(api.read(k),null);
});
test('Rascunhos expirados são descartados e o sistema identifica versão diferente',()=>{
 const {api,data,ctx}=storageHarness(),key=api.key('retroativo','EDUARDO');
 api.store(key,{items:[]});
 assert.equal(api.read(key).version,'v1');
 ctx.onlineVersion='v2';
 assert.notEqual(api.read(key).version,ctx.onlineVersion);
 const obj=JSON.parse(data.get(key));obj.savedAt=Date.now()-46*86400000;data.set(key,JSON.stringify(obj));
 assert.equal(api.read(key),null);
});
test('Apontamento normal guarda a cada tecla/mudança e restaura apenas a versão correta',()=>{
 const start=app.indexOf('function renderEquipeDia(){'),end=app.indexOf('    let unitConvDate=',start),s=app.slice(start,end);
 assert(start>0&&end>start);
 for(const fragment of ['readStoredDraft(storageKey)','restoreDayPendingAdds()',"body.addEventListener('input',dayCapture)","body.addEventListener('change',dayCapture)",'persistDayDraftFromMemory()','clearStoredDraft(storageKey)','id="day-draft-status"','newName:',"savedLocal.version!==onlineVersion"])assert(s.includes(fragment),fragment);
 assert(s.includes('Recuperar rascunho para conferência'));
});
test('Retroativo guarda os campos, seleção e avulsos sem apagar os demais',()=>{
 const start=app.indexOf('  function renderApontamentoRetroativo()'),end=app.indexOf('  function renderExtras(){',start),s=app.slice(start,end);
 assert(start>0&&end>start);
 for(const fragment of ["draftKey('retroativo'","readStoredDraft(retroKey)",'items:[...retroDrafts.values()]','avulsos:[...retroUnsavedAvulsos.values()]','recoverRetroDraft(persistedRetro)',"addEventListener('input',storeRetroDraft)","addEventListener('change',storeRetroDraft)",'clearStoredDraft(retroKey)'])assert(s.includes(fragment),fragment);
});
test('Logout remove cache da conta; o apontamento só apaga rascunho após sucesso',()=>{
 assert(app.includes('if(supervisorAtual)clearSupervisorDrafts(supervisorAtual)'));
 assert(app.includes('dayUnsavedDrafts.delete(dayKey);\n      clearStoredDraft(storageKey);'));
 assert(app.includes("clearStoredDraft(retroKey);retroUnsavedAvulsos.clear();"));
});
