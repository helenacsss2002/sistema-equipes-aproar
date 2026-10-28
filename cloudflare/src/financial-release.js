// Fluxo de liberação do supervisor: auditado e append-only na tabela auditoria.
// Ciclo do Financeiro: terça-feira a segunda-feira; pagamento terça às 10h (Fortaleza).
export const releaseFields=['Extra','Bonificação','Adicional noturno','Passagem / ajuda de custo','Complemento financeiro'];
export const releaseActions=['SOLICITACAO_LIBERACAO_FINANCEIRA','LIBERACAO_FINANCEIRA_AUTORIZADA','LIBERACAO_FINANCEIRA_NEGADA','LIBERACAO_FINANCEIRA_UTILIZADA'];
const day=v=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(String(v)))throw Error('Data inválida.');const d=new Date(String(v)+'T12:00:00Z');if(!Number.isFinite(d.valueOf())||d.toISOString().slice(0,10)!==v)throw Error('Data inválida.');return d;};
export function financialDeadline(serviceDate){
 const d=day(serviceDate);
 const sinceTuesday=(d.getUTCDay()+5)%7;
 const start=new Date(d);start.setUTCDate(start.getUTCDate()-sinceTuesday);
 const pay=new Date(start);pay.setUTCDate(pay.getUTCDate()+7);
 const payment=pay.toISOString().slice(0,10);
 // Fortaleza não utiliza horário de verão. 10:00 -03 equivale a 13:00 UTC.
 return {start:start.toISOString().slice(0,10),end:new Date(pay.valueOf()-86400000).toISOString().slice(0,10),
   payment,limitAt:payment+'T10:00:00-03:00'};
}
export const afterFinancialDeadline=(serviceDate,timestamp)=>new Date(timestamp).getTime()>new Date(financialDeadline(serviceDate).limitAt).getTime();
export function validRequest(input){
 if(!input||typeof input!=='object'||!/^\d{1,18}$/.test(String(input.colaboradorId||'')))throw Error('Colaborador inválido.');
 day(input.dataServico);
 if(!Array.isArray(input.fields)||input.fields.length===0||input.fields.length>releaseFields.length||new Set(input.fields).size!==input.fields.length||input.fields.some(x=>!releaseFields.includes(x)))throw Error('Selecione as colunas que precisam de liberação.');
 if(typeof input.reason!=='string'||input.reason.trim().length<10||input.reason.trim().length>600)throw Error('Informe o motivo da solicitação (10 a 600 caracteres).');
 return {colaboradorId:String(input.colaboradorId),dataServico:input.dataServico,fields:input.fields.slice(),reason:input.reason.trim()};
}
export function releaseState(events){
 const map=new Map();
 for(const e of events){
  const ctx=e.contexto||{},rid=ctx.requestId;
  if(!rid)continue;
  if(e.acao==='SOLICITACAO_LIBERACAO_FINANCEIRA'){
   map.set(rid,{id:rid,supervisor:ctx.supervisor,colaboradorId:String(ctx.colaboradorId||''),colaborador:ctx.colaborador||'',dataServico:ctx.dataServico,fields:ctx.fields||[],reason:ctx.reason,createdAt:e.ocorrido_em,status:'Pendente',approvedBy:null,approvedAt:null,usedAt:null,decisionReason:null});
  }else if(map.has(rid)){
   const item=map.get(rid);
   if(e.acao==='LIBERACAO_FINANCEIRA_AUTORIZADA'&&item.status==='Pendente'){item.status='Autorizada';item.approvedBy=e.usuario;item.approvedAt=e.ocorrido_em;}
   if(e.acao==='LIBERACAO_FINANCEIRA_NEGADA'&&item.status==='Pendente'){item.status='Negada';item.decisionReason=ctx.reason||'';}
   if(e.acao==='LIBERACAO_FINANCEIRA_UTILIZADA'&&item.status==='Autorizada'){item.status='Utilizada';item.usedAt=e.ocorrido_em;}
  }
 }
 return [...map.values()].reverse();
}
export function requireApprovedRelease(events,{supervisor,colaboradorId,dataServico,fields},timestamp,usedIds=new Set()){
 if(!afterFinancialDeadline(dataServico,timestamp)||!fields.length)return null;
 const requests=releaseState(events||[]);
 const valid=requests.find(x=>x.status==='Autorizada'&&x.supervisor===supervisor&&x.colaboradorId===String(colaboradorId)&&x.dataServico===dataServico&&!usedIds.has(x.id)&&fields.every(f=>x.fields.includes(f)));
 if(!valid)throw Object.assign(new Error('Prazo financeiro encerrado às 10h do dia do pagamento. Solicite liberação à Controladoria ou ao Financeiro para alterar: '+fields.join(', ')+'.'),{status:403,details:{dataServico,fields,limitAt:financialDeadline(dataServico).limitAt}});
 usedIds.add(valid.id);
 return {table:'auditoria',action:'insert',id:'audit:'+crypto.randomUUID(),data:{
  entidade:'apontamentos',entidade_id:String(colaboradorId),acao:'LIBERACAO_FINANCEIRA_UTILIZADA',usuario:supervisor,ocorrido_em:timestamp,
  contexto:{requestId:valid.id,supervisor,colaboradorId:String(colaboradorId),dataServico,fields,approvedBy:valid.approvedBy,approvedAt:valid.approvedAt}
 }};
}
export function changedFinancialFields(current,next){
 const n=v=>Math.round((Number(v)||0)*100)/100;
 const result=[];
 if(String(next?.extra||'Não')!==String(current?.extra||'Não')||n(next?.valorExtraOriginal)!==n(current?.valorExtraOriginal)||n(next?.valorExtraDisponivel)!==n(current?.valorExtraDisponivel))result.push('Extra');
 if(n(next?.acordo)!==n(current?.acordo))result.push('Bonificação');
 if(n(next?.noturno)!==n(current?.noturno))result.push('Adicional noturno');
 if(n(next?.ajudaCusto)!==n(current?.ajudaCusto))result.push('Passagem / ajuda de custo');
 if(n(next?.financeiro)!==n(current?.financeiro))result.push('Complemento financeiro');
 return result;
}
