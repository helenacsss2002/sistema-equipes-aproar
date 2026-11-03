import {metadata} from './neon-adapter.js';
import {supervisors} from './data.js';
import {isSafeUnitName} from './unit-label.js';

const fail=(message,status=409)=>{throw Object.assign(new Error(message),{status});};
const cleanDate=value=>{
 const date=String(value instanceof Date?value.toISOString().slice(0,10):value||'').slice(0,10);
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||Number.isNaN(Date.parse(date+'T12:00:00Z')))fail('Informe uma data válida para a transferência.',400);
 return date;
};
const validTurn=turn=>['Integral','Manhã','Tarde','Noite'].includes(turn);
const overlap=(a,b)=>a===b||(a==='Integral'&&['Manhã','Tarde'].includes(b))||(b==='Integral'&&['Manhã','Tarde'].includes(a));
const same=(a,b)=>String(a??'')===String(b??'');

export function validateAdminRelocationInput(body){
 if(!body||typeof body!=='object'||Array.isArray(body)||
    Object.keys(body).some(k=>!['requestId','convocacaoId','colaboradorId','source','destination'].includes(k))||
    !/^[a-f0-9-]{36}$/i.test(body.requestId||'')||
    !/^\d+$/.test(String(body.convocacaoId||''))||
    !/^\d+$/.test(String(body.colaboradorId||'')))fail('Identificação da transferência inválida.',400);
 const s=body.source,d=body.destination;
 if(!s||!d||typeof s!=='object'||typeof d!=='object'||Array.isArray(s)||Array.isArray(d)||
    Object.keys(s).some(k=>!['dataServico','unidade','supervisor','obraId','turno'].includes(k))||
    Object.keys(d).some(k=>!['dataServico','unidade','supervisor','obraId','turno'].includes(k))||
    !isSafeUnitName(d.unidade)||!validTurn(d.turno)||!validTurn(s.turno)||
    ![...supervisors,'PAULO'].includes(d.supervisor)||!s.supervisor||
    !/^\d*$/.test(String(d.obraId??''))||!/^\d*$/.test(String(s.obraId??'')))
    fail('Unidade, obra, responsável ou turno inválido para a transferência.',400);
 return {requestId:body.requestId,convocacaoId:String(body.convocacaoId),
   colaboradorId:String(body.colaboradorId),
   source:{...s,dataServico:cleanDate(s.dataServico),obraId:String(s.obraId||'')},
   destination:{...d,dataServico:cleanDate(d.dataServico),obraId:String(d.obraId||'')}};
}

export function buildAdminRelocationOperations({current,works=[],conflicts=[],unavailable=false,request,actor,timestamp}){
 const {source,destination:d,convocacaoId,colaboradorId,requestId}=request;
 if(!current)fail('Convocação não encontrada. Recarregue e confira o registro.');
 if(!same(current.id,convocacaoId)||!same(current.colaborador_id,colaboradorId))
  fail('O colaborador não corresponde à convocação selecionada.');
 const currentDate=cleanDate(current.data);
 const unit=String(current.unidade||'');
 const meta=metadata(current.observacao).meta;
 const visibleSourceWork=meta.servico_a_definir?'':String(current.obra_id||'');
 if(!same(currentDate,source.dataServico)||!same(unit,source.unidade)||
   !same(current.engenheiro,source.supervisor)||!same(current.turno||'Integral',source.turno)||
   !same(visibleSourceWork,source.obraId))
  fail('Esta convocação foi alterada por outra pessoa. Atualize os dados antes de transferir.');
 if(current.has_point||current.has_services||current.custos_separados===true||meta.apontado_em)
  fail('A convocação possui apontamento ou vínculo histórico. A transferência automática foi bloqueada; solicite conferência à Controladoria.');
 if(unavailable)fail('Este colaborador está indisponível na data de destino.');
 if(conflicts.some(c=>overlap(c.turno||'Integral',d.turno)))
  fail('A transferência geraria conflito: colaborador já convocado em turno sobreposto na data de destino.');
 const available=works.filter(w=>w.unidade===d.unidade);
 if(!available.length)fail('Cadastre uma obra na unidade de destino antes de transferir.');
 const chosen=d.obraId?available.find(w=>same(w.id,d.obraId)):available[0];
 if(!chosen)fail('A obra não pertence à unidade de destino.');
 const assigned=Boolean(d.obraId);
 const oldObs=metadata(current.observacao);
 const previousLabel=String(oldObs.text||'').trim();
 const description=/Turno:\s*(Integral|Manhã|Tarde|Noite)/i.test(previousLabel)
  ?previousLabel.replace(/Turno:\s*(Integral|Manhã|Tarde|Noite)/i,'Turno: '+d.turno)
  :'Turno: '+d.turno+(previousLabel?' | '+previousLabel:'');
 const newMeta={...oldObs.meta,servico_a_definir:!assigned,
   realocado_por:actor,realocado_em:timestamp};
 const oldValues={dataServico:currentDate,unidade:unit,supervisor:current.engenheiro,
   obraId:visibleSourceWork,turno:current.turno||'Integral'};
 const newValues={dataServico:d.dataServico,unidade:d.unidade,supervisor:d.supervisor,
   obraId:assigned?String(chosen.id):'',turno:d.turno};
 if(Object.keys(oldValues).every(k=>same(oldValues[k],newValues[k])))
  fail('Não há alterações para salvar nesta transferência.',400);
 return [
  {table:'convocacoes',action:'update',id:convocacaoId,
   data:{obra_id:String(chosen.id),data:d.dataServico,engenheiro:d.supervisor,turno:d.turno,
    observacao:description+' ||APROAR_META|| '+JSON.stringify(newMeta)}},
  {table:'auditoria',action:'insert',id:'audit:'+requestId,
   data:{entidade:'convocacoes',entidade_id:convocacaoId,acao:'REALOCACAO_ADMINISTRATIVA',
    usuario:actor,ocorrido_em:timestamp,antes:oldValues,depois:newValues,
    contexto:{convocacaoId,colaboradorId,motivo:'Transferência de funcionário entre equipes/unidades'}}}
 ];
}
