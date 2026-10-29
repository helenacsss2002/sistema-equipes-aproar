import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
function segment(start,end){
 const i=ui.indexOf(start),j=ui.indexOf(end,i+start.length);
 assert(i>=0&&j>i,'Trecho nao encontrado: '+start);
 return ui.slice(i,j);
}
const navSrc=segment('  function navConfig() {','  function sidebarIcon(');
const renderSrc=segment('  function render() {','  function showLogin() {');
const indisSrc=segment('  function renderIndisponibilidade(){','  function registerConvocationConflicts(');
const conflitosSrc=segment('  function renderConflitos(){','  function renderWhatsAppBase(){');
const dispSrc=segment('  function renderDisponibilidade(){','  function renderIndisponibilidade(){');

function menu(role){
 const ctx={perfilAtual:role};vm.createContext(ctx);
 vm.runInContext(navSrc+';globalThis.getMenu=navConfig;',ctx);
 return JSON.parse(JSON.stringify(ctx.getMenu())).map(x=>x.view);
}

test('Somente visualizar inclui tres abas sem retirar Dashboard, Relatorios e Indicadores',()=>{
 assert.deepEqual(menu('VISUALIZAR'),[
  'dashboard','relatorios','indicadores','conflitos','disponibilidade','indisponibilidade'
 ]);
});
test('Menus existentes da Controladoria, Supervisor e Financeiro foram preservados',()=>{
 for(const view of ['conflitos','disponibilidade','indisponibilidade','apontamento','convocacao'])
  assert(menu('CONTROLADORIA').includes(view),view);
 for(const view of ['apontamento','convocacao','disponibilidade','pendencias'])
  assert(menu('SUPERVISOR').includes(view),view);
 for(const view of ['financeiro','historico-financeiro','relatorios'])
  assert(menu('FINANCEIRO').includes(view),view);
});
test('Rota VISUALIZAR abre cada uma das tres paginas',()=>{
 assert.match(renderSrc,/perfilAtual==='VISUALIZAR'/);
 for(const view of ['conflitos:renderConflitos','disponibilidade:renderDisponibilidade','indisponibilidade:renderIndisponibilidade'])
  assert(renderSrc.includes(view),view);
});
test('Indisponibilidade mostra tabela sem formulario ou botoes para excluir no perfil leitor',()=>{
 const target={innerHTML:''};
 const ctx={
  perfilAtual:'VISUALIZAR',
  state:{indisponibilidades:[{id:'1',colaboradorId:'10',motivo:'Atestado',inicio:'2026-10-25',fim:'2026-10-27',obs:'Teste'}]},
  $:()=>target,
  head:(title,subtitle)=>'<h1>'+title+'</h1><p>'+subtitle+'</p>',
  table:(headers,rows)=>'<table>'+headers.join('|')+'|'+rows.flat().join('|')+'</table>',
  escapeHtml:x=>String(x??''),formatDate:x=>x,
  colaboradorById:()=>({nome:'FUNCIONARIO EXEMPLO'})
 };
 vm.createContext(ctx);vm.runInContext(indisSrc+';renderIndisponibilidade();',ctx);
 assert.match(target.innerHTML,/FUNCIONARIO EXEMPLO/);
 assert.match(target.innerHTML,/Atestado/);
 assert.match(target.innerHTML,/Acesso somente para visualizar/);
 assert.doesNotMatch(target.innerHTML,/ind-form|data-remove-ind|Registrar indisponibilidade|Excluir/);
});
test('Conflitos mostra ocorrencias sem conferir ou abrir edicao em perfil leitor',()=>{
 const target={innerHTML:''};
 const ctx={
  perfilAtual:'VISUALIZAR',
  convocationConflictRows:()=>[{key:'22',dataServico:'2026-10-09',colaboradorNome:'COLABORADOR TESTE',supervisor:'FELIPE',unidade:'CENTRO',turno:'Integral',supervisorExistente:'VICTOR',unidadeExistente:'MUSEU',turnoExistente:'Integral',data:'2026-10-09T12:00:00Z',resolvido:false}],
  $:()=>target,
  head:(t,d)=>'<h1>'+t+'</h1><p>'+d+'</p>',metric:(t,v)=>'<p>'+t+': '+v+'</p>',
  table:(cols,rows)=>'<table>'+cols.join('|')+'|'+rows.flat().join('|')+'</table>',
  formatDate:x=>x,formatDateTime:x=>x,escapeHtml:x=>String(x??''),
  colaboradorById:()=>({nome:'COLABORADOR TESTE'})
 };
 vm.createContext(ctx);vm.runInContext(conflitosSrc+';renderConflitos();',ctx);
 assert.match(target.innerHTML,/COLABORADOR TESTE/);
 assert.match(target.innerHTML,/Conflitos pendentes: 1/);
 assert.match(target.innerHTML,/Acesso somente para visualizar/);
 assert.doesNotMatch(target.innerHTML,/conf-edit|data-resolve-conflict|Marcar como conferido|Abrir convocações|<button/);
});
test('Disponibilidade filtra e consulta sem alterar dados',()=>{
 assert.match(dispSrc,/id="disp-data"/);
 assert.match(dispSrc,/id="disp-turno"/);
 assert.match(dispSrc,/data-availability/);
 assert.doesNotMatch(dispSrc,/saveData\(|state\.indisponibilidades\.push\(|state\.convocacoes\.push\(/);
});
test('Servidor continua negando gravacoes de VISUALIZAR',()=>{
 const src=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');
 assert.match(src,/if\(session\.role==='VISUALIZAR'\)fail\('Este perfil permite somente visualização\.',403\)/);
});
