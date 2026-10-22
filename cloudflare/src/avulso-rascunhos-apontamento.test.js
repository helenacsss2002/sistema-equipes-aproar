import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

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
 assert.match(retro,/if\(!saveData\(\(\)=>\{retroUnsavedAvulsos\.clear\(\);setView\('pendencias'\);\}\)\)return/);
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
 assert.match(js,/if\(view!=='apontamento'\)\{/);
 assert.match(js,/discardRetroUnsavedAvulsos\(\)/);
 assert.match(js,/discardDayPendingAdds\(\)/);
 assert.match(js,/restoreDayPendingAdds\(\)/);
 assert.match(js,/if\(b\.dataset\.tab!=='retroativo'\)discardRetroUnsavedAvulsos\(\)/);
 assert.match(js,/if\(preserveRetroDraft\)for\(const \[id,staff\] of retroUnsavedAvulsos\)/);
});

test('Na inclusão normal, avulso e convocados seguem juntos no POST definitivo; falha mantém a equipe local',()=>{
 const add=section(" $('#day-add-button').onclick=()=>{"," $('#day-form').noValidate=true;");
 const submission=section(" $('#day-form').onsubmit=e=>{","     let unitConvDate='';");
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
