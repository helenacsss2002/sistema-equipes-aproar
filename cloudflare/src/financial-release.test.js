import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {financialDeadline,afterFinancialDeadline,validRequest,requireApprovedRelease,requireApprovedReleases,releaseState,changedFinancialFields,approvalFields,financialPaymentBundle} from './financial-release.js';

globalThis.crypto??=webcrypto;
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const operations=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');
const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');

test('Ciclo terça a segunda vence terça seguinte às 10h, horário de Fortaleza',()=>{
 const dates=['2026-10-20','2026-10-21','2026-10-26'];
 for(const date of dates){
  assert.deepEqual(financialDeadline(date),{start:'2026-10-20',end:'2026-10-26',payment:'2026-10-27',limitAt:'2026-10-27T10:00:00-03:00'});
  assert.equal(afterFinancialDeadline(date,'2026-10-27T12:59:59.999Z'),false);
  assert.equal(afterFinancialDeadline(date,'2026-10-27T13:00:00.000Z'),false);
  assert.equal(afterFinancialDeadline(date,'2026-10-27T13:00:01.000Z'),true);
 }
 assert.equal(financialDeadline('2026-10-27').payment,'2026-11-03');
 assert.equal(financialDeadline('2026-11-02').payment,'2026-11-03');
});
const timestamp='2026-10-27T13:01:00.000Z';
const requestId='11111111-1111-4111-8111-111111111111';
const ctx={requestId,supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26',
 fields:['Extra','Bonificação','Passagem / ajuda de custo'],reason:'Correção de pagamento comprovada'};
const events=[
 {acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'VICTOR',ocorrido_em:'2026-10-27T13:00:02Z',contexto:ctx},
 {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:'FINANCEIRO',ocorrido_em:'2026-10-27T13:00:10Z',contexto:{requestId}}
];
test('Autorização do Financeiro libera pacote de pagamento apenas no mesmo colaborador e data, uma vez',()=>{
 assert.equal(releaseState(events)[0].status,'Autorizada');
 const consumed=new Set();
 const params={supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26',fields:['Extra','Bonificação']};
 const op=requireApprovedRelease(events,params,timestamp,consumed);
 assert.equal(op.data.acao,'LIBERACAO_FINANCEIRA_UTILIZADA');
 assert.equal(op.data.contexto.approvedBy,'FINANCEIRO');
 assert.equal(op.data.usuario,'VICTOR');
 assert.equal(op.data.contexto.requestId,requestId);
 assert.throws(()=>requireApprovedRelease(events,params,timestamp,consumed),/Prazo financeiro encerrado/);
 assert.throws(()=>requireApprovedRelease(events,{...params,colaboradorId:'72'},timestamp),/Prazo financeiro encerrado/);
 assert.throws(()=>requireApprovedRelease(events,{...params,supervisor:'FELIPE'},timestamp),/Prazo financeiro encerrado/);
 assert.throws(()=>requireApprovedRelease(events,{...params,fields:['Adicional noturno']},timestamp),/Prazo financeiro encerrado/);
 assert.equal(requireApprovedRelease([],params,'2026-10-27T12:59:00Z'),null);
});
test('Uma autorização no mesmo salvamento pode cobrir extra e apontamento do mesmo colaborador uma única vez',()=>{
 const used=new Map(),params={supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26',fields:['Extra']};
 const first=requireApprovedRelease(events,params,timestamp,used);
 const second=requireApprovedRelease(events,params,timestamp,used);
 assert.equal(first.data.acao,'LIBERACAO_FINANCEIRA_UTILIZADA');
 assert.equal(second,null);
 assert.equal(used.size,1);
 const consumed=[...events,{acao:'LIBERACAO_FINANCEIRA_UTILIZADA',usuario:'VICTOR',ocorrido_em:timestamp,contexto:{requestId}}];
 assert.throws(()=>requireApprovedRelease(consumed,params,timestamp,new Map()),/Solicite liberação/);
});
test('Liberações independentes de Extra e Bonificação cobrem um salvamento único, sem solicitar novamente',()=>{
 const extraId='22222222-2222-4222-8222-222222222222';
 const bonusId='33333333-3333-4333-8333-333333333333';
 const scope={supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26'};
 const grants=[
  {acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'VICTOR',ocorrido_em:'2026-10-27T13:00:01Z',contexto:{requestId:extraId,...scope,fields:['Extra']}},
  {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:'FINANCEIRO',ocorrido_em:'2026-10-27T13:00:02Z',contexto:{requestId:extraId}},
  {acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'VICTOR',ocorrido_em:'2026-10-27T13:00:03Z',contexto:{requestId:bonusId,...scope,fields:['Bonificação']}},
  {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:'FINANCEIRO',ocorrido_em:'2026-10-27T13:00:04Z',contexto:{requestId:bonusId}}
 ];
 const used=new Map();
 const operations=requireApprovedReleases(grants,{...scope,fields:['Extra','Bonificação']},timestamp,used);
 assert.equal(operations.length,1);
 assert.equal(used.size,1);
 assert.ok([extraId,bonusId].includes(operations[0].data.contexto.requestId));
 assert.deepEqual(requireApprovedReleases(grants,{...scope,fields:['Extra']},timestamp,used),[]);
 assert.equal(used.size,1);
 assert.throws(()=>requireApprovedReleases(grants,{...scope,fields:['Adicional noturno','Extra']},timestamp,used),
  e=>e.status===403&&e.details.fields.length===1&&e.details.fields[0]==='Adicional noturno'&&
   e.details.alreadyApproved.includes('Extra')&&/SOMENTE para: Adicional noturno/.test(e.message));
 const consumed=[...grants,...operations.map(o=>({acao:o.data.acao,usuario:o.data.usuario,ocorrido_em:timestamp,contexto:o.data.contexto}))];
 const secondSave=requireApprovedReleases(consumed,{...scope,fields:['Extra']},timestamp,new Map());
 assert.equal(secondSave.length,1); // Cada aprovação independente ainda vale para seu próprio salvamento.
 const consumedAll=[...consumed,...secondSave.map(op=>({acao:op.data.acao,usuario:op.data.usuario,ocorrido_em:timestamp,contexto:op.data.contexto}))];
 assert.throws(()=>requireApprovedReleases(consumedAll,{...scope,fields:['Extra']},timestamp,new Map()),/Solicite liberação/);
});
test('Financeiro amplia automaticamente Extra, Bonificação e Passagem no mesmo pedido',()=>{
 const bundle=['Extra','Bonificação','Passagem / ajuda de custo'];
 assert.deepEqual(financialPaymentBundle,bundle);
 assert.deepEqual(approvalFields(['Extra'],'FINANCEIRO'),bundle);
 assert.deepEqual(approvalFields(['Bonificação'],'FINANCEIRO'),['Bonificação','Extra','Passagem / ajuda de custo']);
 assert.deepEqual(approvalFields(['Passagem / ajuda de custo'],'FINANCEIRO'),['Passagem / ajuda de custo','Extra','Bonificação']);
 assert.deepEqual(approvalFields(['Extra','Adicional noturno'],'FINANCEIRO'),['Extra','Adicional noturno','Bonificação','Passagem / ajuda de custo']);
 assert.deepEqual(approvalFields(['Adicional noturno'],'FINANCEIRO'),['Adicional noturno']);
 assert.deepEqual(approvalFields(['Extra'],'CONTROLADORIA'),['Extra']);
 assert.deepEqual(approvalFields(['Complemento financeiro'],'FINANCEIRO'),['Complemento financeiro']);
 const id='44444444-4444-4444-8444-444444444444',scope={supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26'};
 const request=[{acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'VICTOR',ocorrido_em:'2026-10-27T13:00:01Z',
  contexto:{requestId:id,...scope,fields:['Extra'],reason:'Ajuste de lançamento'}},
  {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:'FINANCEIRO',ocorrido_em:'2026-10-27T13:00:02Z',contexto:{requestId:id}}];
 const state=releaseState(request)[0];
 assert.deepEqual(state.requestedFields,['Extra']);
 assert.deepEqual(state.fields,bundle);
 const used=new Map();
 const actions=requireApprovedReleases(request,{...scope,fields:bundle},timestamp,used);
 assert.equal(actions.length,1);
 assert.equal(actions[0].data.contexto.requestId,id);
 assert.deepEqual(new Set(actions[0].data.contexto.fields),new Set(bundle));
 assert.deepEqual(requireApprovedReleases(request,{...scope,fields:['Passagem / ajuda de custo']},timestamp,used),[]);
 assert.throws(()=>requireApprovedReleases(request,{...scope,fields:['Adicional noturno']},timestamp,used),/Adicional noturno/);
 assert.throws(()=>requireApprovedReleases(request,{...scope,colaboradorId:'72',fields:['Extra']},timestamp,new Map()),/Solicite liberação/);
 const persisted=[...request,...actions.map(o=>({acao:o.data.acao,usuario:o.data.usuario,
  ocorrido_em:timestamp,contexto:o.data.contexto}))];
 assert.equal(releaseState(persisted)[0].status,'Utilizada');
 assert.throws(()=>requireApprovedReleases(persisted,{...scope,fields:['Extra']},timestamp,new Map()),/Solicite liberação/);
});
test('Aprovado pela Controladoria mantém escopo original; aprovação de noturno isolado não libera pacote',()=>{
 const id='55555555-5555-4555-8555-555555555555',scope={supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26'};
 for(const [approver,fields] of [['CONTROLADORIA',['Extra']],['FINANCEIRO',['Adicional noturno']]]){
  const events=[{acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'VICTOR',ocorrido_em:'2026-10-27T13:00:01Z',
   contexto:{requestId:id,...scope,fields,reason:'Correção operacional'}},
   {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:approver,ocorrido_em:'2026-10-27T13:00:03Z',contexto:{requestId:id}}];
  assert.throws(()=>requireApprovedReleases(events,{...scope,fields:['Passagem / ajuda de custo']},timestamp,new Map()),/Solicite liberação/);
 }
});
test('Liberação de outro colaborador, outra data ou outro supervisor nunca é aproveitada',()=>{
 const same={supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26',fields:['Extra']};
 const used=new Map();
 for(const changed of [{colaboradorId:'72'},{dataServico:'2026-10-25'},{supervisor:'FELIPE'}]){
  assert.throws(()=>requireApprovedReleases(events,{...same,...changed},timestamp,used),/Solicite liberação/);
 }
 assert.equal(used.size,0);
});
test('Solicitação negada ou consumida não pode mais ser utilizada',()=>{
 for(const action of ['LIBERACAO_FINANCEIRA_NEGADA','LIBERACAO_FINANCEIRA_UTILIZADA']){
  const event={acao:action,usuario:'FINANCEIRO',ocorrido_em:'2026-10-27T13:00:25Z',contexto:{requestId}};
  const e=action==='LIBERACAO_FINANCEIRA_NEGADA'?[events[0],event]:[...events,event];
  const state=releaseState(e)[0];
  assert.notEqual(state.status,'Autorizada');
  assert.throws(()=>requireApprovedRelease(e,{supervisor:'VICTOR',colaboradorId:'71',dataServico:'2026-10-26',fields:['Extra']},timestamp),/Solicite liberação/);
 }
});
test('Mudanças de extra, bonificação, passagem, noturno e complemento são detectadas separadamente',()=>{
 const current={extra:'Não',valorExtraOriginal:0,valorExtraDisponivel:0,acordo:0,noturno:0,ajudaCusto:0,financeiro:0};
 const next={...current,extra:'Diária',valorExtraOriginal:200,valorExtraDisponivel:200,acordo:90,noturno:50,ajudaCusto:11,financeiro:80};
 assert.deepEqual(changedFinancialFields(current,next),['Extra','Bonificação','Adicional noturno','Passagem / ajuda de custo','Complemento financeiro']);
 assert.deepEqual(changedFinancialFields(current,{...current}),[]);
});
test('Solicitações exigem justificativa e campos válidos',()=>{
 const valid={colaboradorId:'71',dataServico:'2026-10-26',fields:['Extra','Bonificação'],reason:'Apontamento precisa de correção'};
 assert.deepEqual(validRequest(valid),valid);
 assert.throws(()=>validRequest({...valid,reason:'x'}),/motivo/);
 assert.throws(()=>validRequest({...valid,fields:['Extra','Extra']}),/colunas/);
 assert.throws(()=>validRequest({...valid,fields:['Tudo']}),/colunas/);
});
test('Bloqueio ocorre em todas as rotas de salvamento do supervisor, com consumo atômico',()=>{
 assert.match(operations,/requireApprovedReleases\(db\.releaseEvents,\{supervisor:session\.user,colaboradorId:pid/);
 assert.match(operations,/requireApprovedReleases\(db\.releaseEvents,\{supervisor:session\.user,colaboradorId:personId/);
 assert.match(operations,/requireApprovedReleases\(db\.releaseEvents,\{supervisor:session\.user,colaboradorId:old\.colaboradorId/);
 assert.match(operations,/releaseUses=new Map\(\)/);
 assert.match(worker,/if\(path==='\/api\/financial-release\/request'/);
 assert.match(worker,/if\(path==='\/api\/financial-release\/decide'/);
 assert.match(worker,/if\(path==='\/api\/financial-release'&&request\.method==='GET'\)/);
 assert.match(worker,/session\.role!=='SUPERVISOR'/);
 assert.match(worker,/\['CONTROLADORIA','FINANCEIRO'\]\.includes\(session\.role\)/);
 assert.match(worker,/db\.releaseEvents=await sql/);
 assert.match(worker,/const operations=buildOperations\(db,body\.state,session\)/);
 assert.match(worker,/aproar_web_apply/);
});
test('Supervisor solicita e Controladoria ou Financeiro aprova no menu',()=>{
 assert.match(ui,/item\('liberacoes-financeiras','Solicitar liberação'/);
 assert.match(ui,/item\('liberacoes-financeiras','Autorizações financeiras'/);
 assert.match(ui,/function renderFinancialReleases\(\)/);
 assert.match(ui,/api\/financial-release\/request/);
 assert.match(ui,/api\/financial-release\/decide/);
 assert.match(ui,/isApprovedFinancial\(serviceDate,cid,'Adicional noturno'\)/);
 assert.match(ui,/isApprovedFinancial\(serviceDate,cid,'Passagem \/ ajuda de custo'\)/);
});
