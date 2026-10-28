import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const js=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');

function section(first,last){
 const a=js.indexOf(first),b=js.indexOf(last,a+first.length);
 assert(a>=0&&b>a,'Trecho não encontrado: '+first);
 return js.slice(a,b);
}
const retro=section('  function renderApontamentoRetroativo() {','  function renderExtras(){');
const normal=section('function renderEquipeDia(){','  function convocationReviewMarkup(');
const forms=section('  function readPersonRows(','  function applyInlineExtras(');

test('Retroativo adiciona avulso sem apagar fichas e mantém busca, seleção e preenchimentos',()=>{
 assert.match(retro,/id="retro-avulso-name"/);
 assert.match(retro,/avulsoFuncaoSelect\('retro-avulso-funcao'\)/);
 assert.match(retro,/id="retro-avulso-add"/);
 assert.match(retro,/const checked=new Set\(\$\$\('input\[name="retro-colab"\]:checked'\)/);
 assert.match(retro,/checked\.add\(id\)/);
 assert.match(retro,/connectRetroChoices\(\);\s*refreshRows\(\)/);
 assert.match(retro,/if\(!reset\)readPersonRows\(current\)\.forEach\(i=>retroDrafts\.set\(i\.colaboradorId,i\)\)/);
 assert.match(retro,/retroDrafts\.get\(id\)\|\|previousItem\(id\)/);
 assert.match(retro,/personRow\(id,/);
 assert.match(retro,/if\(!saveData\(\(\)=>\{clearStoredDraft\(retroKey\);if\(perfilAtual==='SUPERVISOR'\)clearStoredDraft\(draftKey\('last',supervisorAtual\)\);retroUnsavedAvulsos\.clear\(\);setView\('pendencias'\);\}\)\)return/);
});
test('Inserir avulso no apontamento normal salva um rascunho de cada colaborador antes de redesenhar a tela',()=>{
 const add=section(" $('#day-add-button').onclick=()=>{"," $('#day-form').noValidate=true;");
 const snapshot=section(' const snapshotDayDraft=()=>{',' const extraTypes=');
 assert.match(snapshot,/readPersonRows\(ids,\$\('#day-form'\)\)/);
 assert.match(snapshot,/new Map\(items\.map\(item=>\[item\.colaboradorId,item\]\)\)/);
 assert.match(snapshot,/dayUnsavedDrafts\.set\(dayKey/);
 assert.match(add,/snapshotDayDraft\(\);/);
 assert.doesNotMatch(add,/saveData\(/,'Adicionar avulso ao formulário não deve gravar antes do apontamento');
 assert.match(add,/dayPendingAdds\.set\(id/);
 assert.match(add,/dayUnsavedDrafts\.get\(dayKey\)\?\.items\.set\(id/);
 assert.match(normal,/if\(!saveData\(\(\)=>\{/,'Somente o envio definitivo deve salvar equipe e apontamento');
 assert.match(normal,/dayPendingAdds\.clear\(\)/);
 assert.match(normal,/dayDraft\?\.items\?\.get\(id\)\|\|apForConv/);
 assert.match(normal,/if\(dayDraft\?\.extra\)/);
 assert.match(normal,/\$\('#day-person-search'\)\.value=draft\.search/);
 assert.match(normal,/dayUnsavedDrafts\.delete\(dayKey\)/);
});
test('Campos completos são restaurados, incluindo diária avulsa, serviços, status, extra e valores de pagamento',()=>{
 for(const pattern of [
  /tipoDiariaAvulso:row\.querySelector\('\.row-avulso-diaria'\)/,
  /row\.querySelector\('\.row-status'\)\.value/,
  /row\.querySelector\('\.row-extra-value'\)/,
  /row\.querySelector\('\.row-acordo'\)\.value/,
  /row\.querySelector\('\.row-noturno'\)\.value/,
  /row\.querySelector\('\.row-obs'\)\.value/,
  /row\.querySelector\('\.row-ajuda-custo'\)/,
  /row\.querySelectorAll\('\.allocation-row'\)/
 ])assert.match(forms,pattern);
 assert.match(js,/item\?\.tipoDiariaAvulso\|\|'Diária'/);
 assert.match(js,/extraAmount\?extraAmount\.toFixed\(2\)/);
 assert.match(js,/item\?\.acordo\|\|0/);
});
test('Avulso segue na gravação do apontamento e na apropriação operacional e financeira',()=>{
 assert.match(retro,/COLABORADORES\.push\(novo\)/);
 assert.match(retro,/const itens=readPersonRows\(ids\)/);
 assert.match(retro,/if\(!validServices\(itens,unidade\.value\)\)return/);
 assert.match(normal,/state\.convocacoes\.push\(conv\)/);
 assert.match(normal,/conv\.colaboradores\.push\(id\)/);
 assert.match(js,/p\?\.avulso==='Sim'&&AVULSO_DIARIA_OPTIONS\.includes\(i\.tipoDiariaAvulso\)/);
 assert.match(js,/const diariaAvulso=x\.p\?\.avulso==='Sim'&&presence\(x\.i\.status\)\?roundMoney\(x\.daily\):0/);
 assert.match(js,/entry\.extra=roundMoney\(entry\.extra\+entry\.diariaAvulso\)/);
});
test('Abandonar o retroativo descarta avulsos provisórios e falha de gravação conserva os rascunhos',()=>{
 assert.match(js,/function discardRetroUnsavedAvulsos\(\)/);
 assert.match(js,/if\(view!=='apontamento'&&\!\(perfilAtual==='SUPERVISOR'&&view==='liberacoes-financeiras'\)\)\{/);
 assert.match(js,/discardRetroUnsavedAvulsos\(\)/);
 assert.match(js,/discardDayPendingAdds\(\)/);
 assert.match(js,/restoreDayPendingAdds\(\)/);
 assert.match(js,/if\(b\.dataset\.tab!=='retroativo'\)discardRetroUnsavedAvulsos\(\)/);
 assert.match(js,/if\(preserveRetroDraft\)for\(const \[id,staff\] of retroUnsavedAvulsos\)/);
});

test('Na inclusão normal, avulso e convocados seguem juntos no POST definitivo; falha mantém a equipe local',()=>{
 const add=section(" $('#day-add-button').onclick=()=>{"," $('#day-form').noValidate=true;");
 const submission=section("$('#day-form').onsubmit=e=>{","let unitConvDate='';");
 assert.doesNotMatch(add,/saveData\(/);
 assert.match(add,/conv\.colaboradores\.push\(id\)/);
 assert.match(add,/dayPendingAdds\.set\(id/);
 assert.match(add,/tipoDiariaAvulso:staff\?'Diária'/);
 assert.match(add,/preferredWork/);
 assert.match(submission,/snapshotDayDraft\(\)/);
 assert.match(submission,/dayUnsavedDrafts\.delete\(dayKey\)/);
 assert.match(submission,/dayPendingAdds\.clear\(\)/);
 assert.match(js,/if\(typeof dayPendingAdds!=='undefined'&&dayPendingAdds\.size\)restoreDayPendingAdds\(\)/);
});

test('O X aparece apenas no topo das fichas recém-incluídas; não dispara salvamento no Neon',()=>{
 const normal=section('function renderEquipeDia(){','  function convocationReviewMarkup(');
 const controls=section(" bindServiceRows();bindPersonSearch($('#day-person-search')"," const extraToggle=$('#day-extra-kind')");
 assert.match(controls,/for\(const \[id,pending\] of dayPendingAdds\)/);
 assert.match(controls,/remove\.type='button'/);
 assert.match(controls,/remove\.textContent='×'/);
 assert.match(controls,/remove\.className='day-remove-pending'/);
 assert.match(controls,/position:'absolute',top:'8px',right:'9px'/);
 assert.match(controls,/snapshotDayDraft\(\)/);
 assert.match(controls,/removePendingDayAdd\(id,dayKey\)/);
 assert(controls.indexOf('snapshotDayDraft()')<controls.indexOf('removePendingDayAdd(id,dayKey)'));
 assert.doesNotMatch(controls,/saveData\(/);
 assert.match(normal,/showToast\('Colaborador retirado do formulário/);
});

test('X retira apenas o avulso escolhido, conserva o rascunho dos colegas e não exclui históricos',()=>{
 const code=section('  function removePendingDayAdd(id,dayKey){','  const retroUnsavedAvulsos=new Map();');
 const dayKey='2026-10-22|EDUARDO';
 const saved={id:'hist',nome:'Colega salvo',avulso:'Não'};
 const alice={id:'alice',nome:'Avulso A',avulso:'Sim'};
 const bruno={id:'bruno',nome:'Avulso B',avulso:'Sim'};
 const state={convocacoes:[{id:'cvOriginal',colaboradores:['hist','alice','bruno']}],apontamentos:[],colaboradores:[saved,alice,bruno]};
 const dayPendingAdds=new Map([
  ['alice',{id:'alice',staff:alice,dayKey,convId:'cvOriginal'}],
  ['bruno',{id:'bruno',staff:bruno,dayKey,convId:'cvOriginal'}]
 ]);
 const dayUnsavedDrafts=new Map([[dayKey,{items:new Map([
  ['hist',{status:'Falta',observacao:'Preenchimento mantido'}],
  ['alice',{status:'Presente (Integral)'}],
  ['bruno',{status:'Presente (Integral)'}]
 ]),extra:{person:'',search:'Teste'}}]]);
 const ctx={state,COLABORADORES:state.colaboradores,dayPendingAdds,dayUnsavedDrafts,onlineConfirmed:{convocacoes:[{id:'cvOriginal',colaboradores:['hist']}],colaboradores:[saved]}};
 vm.runInNewContext(code+'\nglobalThis.runRemove=removePendingDayAdd;',ctx);
 assert.equal(ctx.runRemove('alice',dayKey),true);
 assert.deepEqual(state.convocacoes[0].colaboradores,['hist','bruno']);
 assert.deepEqual(ctx.COLABORADORES.map(c=>c.id),['hist','bruno']);
 assert.equal(dayUnsavedDrafts.get(dayKey).items.get('hist').observacao,'Preenchimento mantido');
 assert.equal(dayUnsavedDrafts.get(dayKey).items.has('alice'),false);
 assert.equal(dayUnsavedDrafts.get(dayKey).items.has('bruno'),true);
 assert.equal(dayPendingAdds.has('bruno'),true);
 assert.equal(ctx.runRemove('hist',dayKey),false,'Histórico confirmado não pode ser apagado com X');
 assert.equal(state.convocacoes[0].colaboradores.includes('hist'),true);
});

test('X do único avulso não salvo elimina convocação provisória vazia sem modificar banco',()=>{
 const code=section('  function removePendingDayAdd(id,dayKey){','  const retroUnsavedAvulsos=new Map();');
 const dayKey='2026-10-22|JOEL',p={id:'new1',nome:'Avulso provisório',avulso:'Sim'};
 const state={convocacoes:[{id:'cvProvisorio',colaboradores:['new1']}],apontamentos:[],colaboradores:[p]};
 const ctx={state,COLABORADORES:state.colaboradores,dayPendingAdds:new Map([['new1',{id:'new1',staff:p,dayKey,convId:'cvProvisorio'}]]),dayUnsavedDrafts:new Map([[dayKey,{items:new Map([['new1',{status:'Presente (Integral)'}]]),extra:{person:'new1'}}]]),onlineConfirmed:{convocacoes:[],colaboradores:[]}};
 vm.runInNewContext(code+'\nglobalThis.runRemove=removePendingDayAdd;',ctx);
 assert.equal(ctx.runRemove('new1',dayKey),true);
 assert.equal(state.convocacoes.length,0);
 assert.equal(state.colaboradores.length,0);
 assert.equal(ctx.dayPendingAdds.size,0);
 assert.equal(ctx.dayUnsavedDrafts.get(dayKey).extra.person,'');
});
