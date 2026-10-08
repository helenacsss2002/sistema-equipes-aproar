// Adapter for the existing Neon schema. Database identifiers stay unchanged.
const isoDate=v=>v instanceof Date?v.toISOString().slice(0,10):String(v).slice(0,10);
const id=v=>String(v??'');
const amount=v=>Number.isFinite(Number(v))?Number(v):0;
const marker=' ||APROAR_META|| ';
export function metadata(observation){const [text,...rest]=String(observation||'').split(marker);let meta={};if(rest.length){try{meta=JSON.parse(rest.join(marker));}catch{}}return {text,meta};}
const extraLabel=(value,base)=>{const ratio=base>0?amount(value)/base:0;return ratio===0?'Não':Math.abs(ratio-.5)<.02?'Meia diária':Math.abs(ratio-1)<.02?'Diária':Math.abs(ratio-1.5)<.02?'Uma e meia diária':Math.abs(ratio-2)<.02?'Duas diárias':'Valor específico';};
export function mapNeonData(db){
  const colaboradores=(db.colaboradores||[]).map(p=>({id:id(p.id),nome:p.nome,funcao:p.funcao,custo:amount(p.valor_diaria),moradia:p.local_moradia||'',inativo:p.ativo===false,categoria:p.categoria_diaria||'',avulso:p.avulso||'Não'}));
  const obras=(db.obras||[]).map(o=>({id:id(o.id),nome:o.nome,unidade:o.unidade}));
  const people=new Map(colaboradores.map(p=>[p.id,p])),works=new Map(obras.map(o=>[o.id,o]));
  const pointed=new Map((db.apontamentos||[]).map(a=>[id(a.convocacao_id),a]));
  const services=new Map();for(const s of db.servicos_apontamento||[]){const key=id(s.convocacao_id);if(!services.has(key))services.set(key,[]);services.get(key).push(s);}
  const convocacoes=[],apontamentos=[],warnings=[];
  for(const c of db.convocacoes||[]){
    const key=id(c.id),person=id(c.colaborador_id),work=id(c.obra_id),{text,meta}=metadata(c.observacao),turno=c.turno||text.match(/Turno:\s*(Integral|Manhã|Tarde|Noite)/i)?.[1]||'Integral';
    convocacoes.push({id:key,supervisor:c.engenheiro,dataServico:isoDate(c.data),unidade:works.get(work)?.unidade||'',obraId:meta.servico_a_definir?'':work,turno,colaboradores:[person],criadoEm:c.criado_em||meta.convocado_em||null,executor:c.criado_por||meta.convocado_por||c.engenheiro,origem:'neon'});
    // The initial presence status of a convocation is NOT an attendance entry.
    const a=pointed.get(key);if(!a&&!meta.apontado_em&&c.custos_separados!==true)continue;
    const source=a||c,raw=services.get(key)||[],additional=meta.servicos_adicionais||[];
    const mapped=raw.length?raw.map(s=>({obraId:id(s.obra_id)||obras.find(o=>o.nome===s.obra_nome_snapshot)?.id||'',periodo:s.periodo||turno})): [{obraId:work,periodo:meta.periodo_principal||turno},...additional.map(s=>({obraId:id(s.obra_id)||obras.find(o=>o.nome===s.servico)?.id||'',periodo:s.periodo||turno}))];
    if(mapped.some(s=>!s.obraId))warnings.push({code:'UNMAPPED_SERVICE',convocacaoId:key});
    const cost=people.get(person)?.custo||0,extra=amount(source.valor_extra),savedType=['Não','Meia diária','Diária','Uma e meia diária','Duas diárias'].includes(source.tipo_diaria)?source.tipo_diaria:null;if(extra&&extraLabel(extra,cost)==='Valor específico')warnings.push({code:'NONSTANDARD_EXTRA',convocacaoId:key,value:extra});
    apontamentos.push({id:a?id(a.id):'legacy-'+key,convocacaoId:key,supervisor:c.engenheiro,dataServico:isoDate(c.data),apontadoEm:a?.apontado_em||meta.apontado_em||null,executor:a?.apontado_por||meta.apontado_por||c.engenheiro,retroativo:a?.retroativo||meta.apontamento_atrasado||false,itens:[{colaboradorId:person,status:source.status==='Extra'?'Presente (Integral)':source.status,extra:savedType||extraLabel(extra,cost),valorExtraOriginal:extra,observacao:a?.observacao||text.replace(/^Turno:[^|]+\|?\s*/,''),financeiro:amount(source.custo_pago??meta.custo_pago),financeAdjusted:source.custo_pago_definido_financeiro===true,noturno:amount(source.valor_adicional_noturno??meta.valor_adicional_noturno),acordo:amount(source.valor_acordo??meta.valor_acordo),tipoDiariaOriginal:source.tipo_diaria,servicos:mapped,custoEncargosOriginal:source.custo_encargos_base}]});
  }
  return {colaboradores,obras,convocacoes,apontamentos,warnings,
    indisponibilidades:(db.indisponibilidades||[]).filter(x=>x.ativo).map(x=>({id:id(x.id),colaboradorId:id(x.colaborador_id),motivo:x.motivo,inicio:isoDate(x.inicio),fim:isoDate(x.fim),observacao:x.observacao||'',obs:x.observacao||''})),
    conflitosTentados:(db.conflitos_convocacao||[]).map(x=>({id:id(x.id),colaboradorId:id(x.colaborador_id),colaboradorNome:x.colaborador_nome_snapshot,dataServico:isoDate(x.data),supervisor:x.engenheiro_tentativa,unidade:x.unidade_tentativa,turno:x.turno_tentativa,supervisorExistente:x.engenheiro_original,unidadeExistente:x.unidade_original,turnoExistente:x.turno_original,convocacaoExistenteId:id(x.convocacao_existente_id),data:x.criado_em,resolvido:x.resolvido,conferidoEm:x.resolvido_em})),
    auditoria:(db.auditoria||[]).map(x=>({id:id(x.id),data:x.ocorrido_em,usuario:x.usuario,action:x.acao,ref:x.entidade+' '+(x.entidade_id||'')}))};
}
