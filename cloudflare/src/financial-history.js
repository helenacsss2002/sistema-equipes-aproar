// Auditoria individual de valores pagos: cada mudança preserva valor anterior e novo
// dentro da mesma transação atômica do apontamento que o originou.
const fields=[
  {column:'valor_extra',type:'Extra'},
  {column:'valor_acordo',type:'Bonificação / acordo'},
  {column:'valor_adicional_noturno',type:'Adicional noturno'}
];
const value=n=>Math.round((Number(n)||0)*100)/100;
export function financialHistoryEvents({convocationId,colaboradorId,dataServico,supervisor,actor,role,source,timestamp,previous,next}){
  const events=[];
  for(const f of fields){
    const before=value(previous?.[f.column]),after=value(next?.[f.column]);
    if(before===after)continue;
    events.push({
      table:'auditoria',action:'insert',id:'audit:'+crypto.randomUUID(),
      data:{
        entidade:'apontamentos',
        entidade_id:String(convocationId),
        acao:'LANCAMENTO_FINANCEIRO_ITEM',
        usuario:actor,
        ocorrido_em:timestamp,
        antes:{valor:before},depois:{valor:after},
        contexto:{
          versao:1,convocacaoId:String(convocationId),colaboradorId:String(colaboradorId),
          dataServico:String(dataServico),supervisorResponsavel:String(supervisor||''),
          usuarioResponsavel:String(actor),perfil:String(role),origem:String(source),
          tipo:f.type,campo:f.column,valorAnterior:before,valorNovo:after,
          operacao:before===0&&after>0?'Inclusão':after===0?'Remoção':'Alteração'
        }
      }
    });
  }
  return events;
}
