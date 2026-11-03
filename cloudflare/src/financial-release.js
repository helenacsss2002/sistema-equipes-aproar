// Fluxo de liberação do supervisor: auditado e append-only na tabela auditoria.
// Ciclo do Financeiro: terça-feira a segunda-feira; pagamento terça às 10h (Fortaleza).
export const releaseFields=['Extra','Bonificação','Adicional noturno','Passagem / ajuda de custo','Complemento financeiro'];
// Uma aprovação do FINANCEIRO sobre qualquer uma destas três colunas
// habilita todas as três para o mesmo supervisor, colaborador e data.
// Noturno e complemento permanecem dependentes de autorização específica.
export const financialPaymentBundle=['Extra','Bonificação','Passagem / ajuda de custo'];
export function approvalFields(requested,approver){
 const fields=[...new Set((requested||[]).filter(x=>releaseFields.includes(x)))];
 if(approver!=='FINANCEIRO'||!fields.some(x=>financialPaymentBundle.includes(x)))return fields;
 return [...new Set([...fields,...financialPaymentBundle])];
}
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
   if(e.acao==='LIBERACAO_FINANCEIRA_AUTORIZADA'&&item.status==='Pendente'){item.status='Autorizada';item.approvedBy=e.usuario;item.approvedAt=e.ocorrido_em;item.requestedFields=item.fields.slice();item.fields=approvalFields(item.fields,e.usuario);}
   if(e.acao==='LIBERACAO_FINANCEIRA_NEGADA'&&item.status==='Pendente'){item.status='Negada';item.decisionReason=ctx.reason||'';}
   if(e.acao==='LIBERACAO_FINANCEIRA_UTILIZADA'&&item.status==='Autorizada'){item.status='Utilizada';item.usedAt=e.ocorrido_em;}
  }
 }
 return [...map.values()].reverse();
}
// As autorizações são por colaborador, data e coluna. Quando o Financeiro
// aprova colunas em solicitações separadas, todas podem cobrir um mesmo save.
export function requireApprovedReleases(events,{supervisor,colaboradorId,dataServico,fields},timestamp,usedIds=new Map()){
 if(!afterFinancialDeadline(dataServico,timestamp)||!fields.length)return [];
 const person=String(colaboradorId),requested=[...new Set(fields)];
 const matches=x=>x.supervisor===supervisor&&x.colaboradorId===person&&x.dataServico===dataServico;
 const already=usedIds instanceof Map?[...usedIds.values()].filter(matches):[];
 const covered=new Set(already.flatMap(x=>x.fields||[]));
 const selected=[];
 const authorized=releaseState(events||[]).filter(x=>matches(x)&&x.status==='Autorizada'&&!usedIds.has(x.id));
 for(const grant of authorized){
  if(!(grant.fields||[]).some(f=>requested.includes(f)&&!covered.has(f)))continue;
  selected.push(grant);
  for(const field of grant.fields||[])covered.add(field);
  if(requested.every(f=>covered.has(f)))break;
 }
 const missing=requested.filter(f=>!covered.has(f));
 if(missing.length){
  const permitted=requested.filter(f=>covered.has(f));
  const note=permitted.length?' As seguintes colunas já possuem autorização e NÃO precisam de nova solicitação: '+permitted.join(', ')+'.':'';
  throw Object.assign(new Error('Prazo financeiro encerrado às 10h do dia do pagamento. Solicite liberação SOMENTE para: '+missing.join(', ')+'.'+note),
   {status:403,details:{dataServico,colaboradorId:person,fields:missing,alreadyApproved:permitted,
     limitAt:financialDeadline(dataServico).limitAt}});
 }
 const operations=[];
 for(const grant of selected){
  if(usedIds instanceof Map)usedIds.set(grant.id,{supervisor,colaboradorId:person,dataServico,fields:grant.fields.slice()});
  else usedIds.add(grant.id);
  operations.push({table:'auditoria',action:'insert',id:'audit:'+crypto.randomUUID(),data:{
   entidade:'apontamentos',entidade_id:person,acao:'LIBERACAO_FINANCEIRA_UTILIZADA',usuario:supervisor,ocorrido_em:timestamp,
   contexto:{requestId:grant.id,supervisor,colaboradorId:person,dataServico,
     fields:requested.filter(field=>grant.fields.includes(field)),approvedBy:grant.approvedBy,approvedAt:grant.approvedAt}
  }});
 }
 return operations;
}
// Compatibilidade para usos antigos que solicitam uma única liberação.
export function requireApprovedRelease(events,scope,timestamp,usedIds=new Set()){
 const operations=requireApprovedReleases(events,scope,timestamp,usedIds);
 if(operations.length>1)throw Error('Para múltiplas autorizações, use requireApprovedReleases.');
 return operations[0]||null;
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
