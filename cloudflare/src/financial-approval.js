import {metadata} from './neon-adapter.js';

const invalid=(message,status=400)=>{throw Object.assign(new Error(message),{status});};
const cents=v=>Math.round(Number(v)*100);
const validAmount=v=>typeof v==='number'&&Number.isFinite(v)&&v>0&&v<=10000000;
const approvalKey='aprovacao_complemento_igual_acordo';

export function hasValidComplementApproval(meta,financeiro,acordo){
 const approval=meta?.[approvalKey];
 return Boolean(approval&&approval.aprovadoPor==='FINANCEIRO'&&
  typeof approval.aprovadoEm==='string'&&approval.aprovadoEm.length>=19&&
  typeof approval.justificativa==='string'&&approval.justificativa.trim().length>=10&&
  Number.isFinite(cents(financeiro))&&cents(financeiro)>0&&cents(financeiro)===cents(acordo)&&
  cents(approval.financeiro)===cents(financeiro)&&cents(approval.acordo)===cents(acordo));
}
export function clearObsoleteApproval(meta,financeiro,acordo){
 const next={...meta};
 if(!hasValidComplementApproval(next,financeiro,acordo))delete next[approvalKey];
 return next;
}
export function validateComplementConfirmation(body){
 if(!body||typeof body!=='object'||Array.isArray(body)||
  Object.keys(body).some(k=>!['requestId','version','convocacaoId','financeiro','acordo','justificativa'].includes(k)))
  invalid('Confirmação financeira inválida.');
 if(typeof body.requestId!=='string'||!/^[0-9a-f-]{36}$/i.test(body.requestId)||
  typeof body.version!=='string'||!/^[0-9a-f]{32}$/i.test(body.version))
  invalid('Identificador ou versão de confirmação inválidos.');
 if(!/^[1-9][0-9]{0,17}$/.test(String(body.convocacaoId||'')))
  invalid('Apontamento inválido para confirmação.');
 if(!validAmount(body.financeiro)||!validAmount(body.acordo)||
  cents(body.financeiro)!==cents(body.acordo))
  invalid('Confirme apenas valores complementares positivos e iguais aos acordos.');
 if(typeof body.justificativa!=='string'||body.justificativa.trim().length<10||
  body.justificativa.trim().length>400)
  invalid('Descreva por que são dois pagamentos distintos (mínimo de 10 caracteres, máximo de 400).');
 return {...body,convocacaoId:String(body.convocacaoId),
  financeiro:cents(body.financeiro)/100,acordo:cents(body.acordo)/100,
  justificativa:body.justificativa.trim()};
}
export function buildComplementConfirmationOperations(body,record,actor,timestamp=new Date().toISOString()){
 if(actor!=='FINANCEIRO')invalid('Somente o Financeiro pode confirmar pagamentos complementares.',403);
 if(!record||String(record.convocacao_id)!==body.convocacaoId||!record.apontamento_id)
  invalid('Apontamento não localizado. Atualize os dados.',409);
 if(['Falta','Atestado'].includes(record.status))
  invalid('Não é possível aprovar pagamento de falta ou atestado.');
 if(cents(record.acordo_atual)!==cents(body.acordo)||cents(record.acordo_convocacao)!==cents(body.acordo))
  invalid('O valor do acordo mudou. Atualize a tela antes de confirmar.',409);
 if(cents(record.complemento_atual)!==cents(record.complemento_convocacao))
  invalid('O complemento possui diferenças entre os registros; solicite revisão antes de aprovar.',409);
 const {text,meta}=metadata(record.observacao);
 if(hasValidComplementApproval(meta,body.financeiro,body.acordo))
  invalid('Esses valores já foram confirmados pelo Financeiro.',409);
 const approval={
  aprovadoPor:actor,aprovadoEm:timestamp,justificativa:body.justificativa,
  financeiro:body.financeiro,acordo:body.acordo,convocacaoId:body.convocacaoId
 };
 const nextMeta={...meta,custo_pago:body.financeiro,[approvalKey]:approval};
 return [
  {table:'apontamentos',action:'update',id:String(record.apontamento_id),data:{
   custo_pago:body.financeiro,custo_pago_definido_financeiro:true,atualizado_em:timestamp
  }},
  {table:'convocacoes',action:'update',id:body.convocacaoId,data:{
   custo_pago:body.financeiro,custo_pago_definido_financeiro:true,
   observacao:text+' ||APROAR_META|| '+JSON.stringify(nextMeta)
  }},
  {table:'auditoria',action:'insert',id:'approval:'+crypto.randomUUID(),data:{
   entidade:'apontamentos',entidade_id:String(record.apontamento_id),
   acao:'CONFIRMAR_COMPLEMENTO_DUPLICADO',usuario:actor,ocorrido_em:timestamp,
   contexto:{convocacaoId:body.convocacaoId,financeiro:body.financeiro,acordo:body.acordo,
    justificativa:body.justificativa,aprovadoEm:timestamp}
  }}
 ];
}
