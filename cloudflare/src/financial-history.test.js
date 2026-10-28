import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {financialHistoryEvents} from './financial-history.js';
globalThis.crypto??=webcrypto;

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const ops=fs.readFileSync(new URL('./operations.js',import.meta.url),'utf8');
const financial=fs.readFileSync(new URL('./financial-adjust.js',import.meta.url),'utf8');
const common={
  convocationId:'1751',colaboradorId:'71',dataServico:'2026-10-26',
  supervisor:'VICTOR',actor:'VICTOR',role:'SUPERVISOR',source:'Apontamento',
  timestamp:'2026-10-28T12:00:01.000Z'
};
test('Extra, bonificação e noturno geram trilhas isoladas com autoria, hora e valores',()=>{
 const events=financialHistoryEvents({
  ...common,previous:{valor_extra:0,valor_acordo:25,valor_adicional_noturno:50},
  next:{valor_extra:100,valor_acordo:80,valor_adicional_noturno:0}
 });
 assert.equal(events.length,3);
 const byType=Object.fromEntries(events.map(e=>[e.data.contexto.tipo,e]));
 assert.equal(byType.Extra.data.contexto.operacao,'Inclusão');
 assert.equal(byType.Extra.data.antes.valor,0);
 assert.equal(byType.Extra.data.depois.valor,100);
 assert.equal(byType.Extra.data.contexto.supervisorResponsavel,'VICTOR');
 assert.equal(byType.Extra.data.usuario,'VICTOR');
 assert.equal(byType.Extra.data.ocorrido_em,common.timestamp);
 assert.equal(byType['Bonificação / acordo'].data.contexto.operacao,'Alteração');
 assert.equal(byType['Bonificação / acordo'].data.contexto.valorAnterior,25);
 assert.equal(byType['Bonificação / acordo'].data.contexto.valorNovo,80);
 assert.equal(byType['Adicional noturno'].data.contexto.operacao,'Remoção');
 assert.equal(byType['Adicional noturno'].data.contexto.valorNovo,0);
 assert(events.every(e=>e.table==='auditoria'&&e.action==='insert'&&e.id.startsWith('audit:')));
 assert.equal(new Set(events.map(e=>e.id)).size,3);
});
test('Apontamento sem mudança financeira não duplica eventos, inclusive após repetição',()=>{
 const current={valor_extra:90,valor_acordo:20,valor_adicional_noturno:0};
 assert.equal(financialHistoryEvents({...common,previous:current,next:{...current}}).length,0);
 assert.equal(financialHistoryEvents({...common,previous:undefined,next:{valor_extra:0,valor_acordo:0,valor_adicional_noturno:0}}).length,0);
});
test('Ajuste do Financeiro registra seu próprio usuário e separa supervisor original',()=>{
 const e=financialHistoryEvents({...common,role:'FINANCEIRO',actor:'FINANCEIRO',source:'Ajuste financeiro',
  previous:{valor_acordo:50},next:{valor_acordo:100}});
 assert.equal(e.length,1);
 assert.equal(e[0].data.usuario,'FINANCEIRO');
 assert.equal(e[0].data.contexto.supervisorResponsavel,'VICTOR');
 assert.equal(e[0].data.contexto.valorNovo,100);
 assert.match(financial,/ops\.push\(\.\.\.financialHistoryEvents\(/);
 assert.match(worker,/a\.valor_acordo AS acordo_atual/);
 assert.match(worker,/c\.colaborador_id::text AS colaborador_id/);
});
test('Captura eventos na mesma transação do apontamento normal e extra independente',()=>{
 assert.equal((ops.match(/ops\.push\(\.\.\.financialHistoryEvents\(/g)||[]).length,2);
 assert.match(ops,/source:'Apontamento'/);
 assert.match(ops,/source:'Extra independente'/);
 assert.match(ops,/previous:oldRow,next:values/);
 assert.match(ops,/previous:rawPoint,next:pointData/);
});
test('API de histórico é autenticada, só Financeiro, paginável por período e não confunde datas antigas',()=>{
 const i=worker.indexOf("if(path==='/api/financial-history'&&request.method==='GET')");
 const e=worker.indexOf("if(path==='/api/save-status'",i);
 assert(i>0&&e>i);
 const route=worker.slice(i,e);
 assert.match(route,/session\.role!=='FINANCEIRO'/);
 assert.match(route,/validDate\(inicio\)/);
 assert.match(route,/LANCAMENTO_FINANCEIRO_ITEM/);
 assert.match(route,/CROSS JOIN LATERAL/);
 assert.match(route,/NOT EXISTS/);
 assert.match(route,/auditoria au/);
 assert.match(route,/LIMIT 501/);
 assert.doesNotMatch(route,/UPDATE |DELETE |INSERT INTO /);
});
test('Aba no menu mostra hora exata e diferencia histórico antigo sem autor inventado',()=>{
 assert.match(app,/item\('historico-financeiro','Histórico de registros'/);
 assert.match(app,/'historico-financeiro':renderFinancialHistory/);
 assert.match(app,/function renderFinancialHistory\(\)/);
 assert.match(app,/api\/financial-history\?inicio=/);
 assert.match(app,/timeZone:'America\/Fortaleza'/);
 assert.match(app,/Não comprovado para este valor/);
 assert.match(app,/Legado — sem trilha individual/);
 assert.equal((app.match(/function renderPayments\(\)/g)||[]).length,1);
 assert.equal((app.match(/  initOnline\(\);/g)||[]).length,1);
});
