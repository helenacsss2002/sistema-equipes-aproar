import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {financialDeadline,afterFinancialDeadline,validRequest,requireApprovedRelease,releaseState,changedFinancialFields} from './financial-release.js';

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
test('Autorização do Financeiro libera apenas o colaborador/data/campos solicitados e apenas uma vez',()=>{
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
 assert.match(operations,/requireApprovedRelease\(db\.releaseEvents,\{supervisor:session\.user,colaboradorId:pid/);
 assert.match(operations,/requireApprovedRelease\(db\.releaseEvents,\{supervisor:session\.user,colaboradorId:personId/);
 assert.match(operations,/requireApprovedRelease\(db\.releaseEvents,\{supervisor:session\.user,colaboradorId:old\.colaboradorId/);
 assert.match(operations,/releaseUses=new Set\(\)/);
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
