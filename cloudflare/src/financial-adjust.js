import {metadata} from './neon-adapter.js';
import {hasValidComplementApproval,clearObsoleteApproval} from './financial-approval.js';

const moneyFields=['financeiro','noturno','acordo','ajudaCusto'];
const invalid=(message,status=400)=>{throw Object.assign(new Error(message),{status});};
const rounded=value=>Math.round(value*100)/100;

// Only explicit financial values and existing attendance IDs can be modified.
export function validateFinancialPayload(body){
  if(!body||typeof body!=='object'||Array.isArray(body)||Object.keys(body).some(k=>!['requestId','version','changes'].includes(k)))invalid('Solicitação financeira inválida.');
  if(typeof body.requestId!=='string'||!/^[0-9a-f-]{36}$/i.test(body.requestId)||typeof body.version!=='string'||!/^[0-9a-f]{32}$/i.test(body.version))invalid('Identificador ou versão da gravação inválidos.');
  if(!Array.isArray(body.changes)||!body.changes.length||body.changes.length>30)invalid('Selecione até 30 apontamentos por lançamento.');
  const seen=new Set();
  const changes=body.changes.map(item=>{
    if(!item||typeof item!=='object'||Array.isArray(item)||Object.keys(item).some(k=>!['convocacaoId',...moneyFields].includes(k)))invalid('Campos financeiros inválidos.');
    const id=String(item.convocacaoId||'');
    if(!/^[1-9][0-9]{0,17}$/.test(id)||seen.has(id))invalid('Apontamento ausente ou duplicado.');
    seen.add(id);
    const next={convocacaoId:id};
    for(const key of moneyFields){
      if(typeof item[key]!=='number'||!Number.isFinite(item[key])||item[key]<0||item[key]>10000000)invalid('Informe valores financeiros válidos.');
      next[key]=rounded(item[key]);
    }
    return next;
  });
  return {...body,changes};
}

export function buildFinancialOperations(changes,rows,actor,timestamp=new Date().toISOString()){
  const rowByConv=new Map(rows.map(row=>[String(row.convocacao_id),row]));
  const ops=[];
  for(const entry of changes){
    const record=rowByConv.get(entry.convocacaoId);
    if(!record)invalid('Apontamento não encontrado. Atualize a página.',409);
    if(['Falta','Atestado'].includes(record.status))invalid('Não é permitido lançar valores para falta ou atestado.');
    if(!record.has_sebrae&&entry.noturno>0&&Math.abs(Number(record.noturno_atual||0)-entry.noturno)>0.005)invalid('Adicional noturno disponível somente para o SEBRAE.');
    const {text,meta}=metadata(record.observacao);
    if(entry.financeiro>0&&entry.acordo>0&&rounded(entry.financeiro)===rounded(entry.acordo)&&!hasValidComplementApproval(meta,entry.financeiro,entry.acordo))invalid('Valor complementar igual ao acordo exige confirmação explícita no Portal Financeiro.');
    const financial={custo_pago:entry.financeiro,valor_acordo:entry.acordo,valor_adicional_noturno:entry.noturno,custo_pago_definido_financeiro:true,custos_separados:true,migracao_sebrae_noturno_v2:true};
    const nextMeta={...clearObsoleteApproval(meta,entry.financeiro,entry.acordo),custo_pago:entry.financeiro,valor_acordo:entry.acordo,valor_adicional_noturno:entry.noturno,valor_ajuda_custo:entry.ajudaCusto,custos_separados:true};
    ops.push({table:'apontamentos',action:'update',id:String(record.apontamento_id),data:{...financial,atualizado_em:timestamp}});
    ops.push({table:'convocacoes',action:'update',id:entry.convocacaoId,data:{...financial,observacao:text+' ||APROAR_META|| '+JSON.stringify(nextMeta)}});
  }
  ops.push({table:'auditoria',action:'insert',id:'audit:'+crypto.randomUUID(),data:{entidade:'aproar-web',entidade_id:null,acao:'SALVAR',usuario:actor,ocorrido_em:timestamp,contexto:{perfil:'FINANCEIRO',operacoes:ops.map(op=>({tabela:op.table,acao:op.action,id:op.id}))}}});
  return ops;
}
