// Explicit environment and hostname checks. Production also requires separate approval.
export const stage=env=>env.APP_ENV==='producao'?'producao':'homologacao';
export function writeControls(env){
  const production=env.APP_ENV==='producao';
  const homologation=env.APP_ENV==='homologacao';
  const expectedHost=production?env.PRODUCTION_EXPECTED_HOST:env.HOMOLOGATION_EXPECTED_HOST;
  let configuredHost='';
  try{configuredHost=new URL(env.DATABASE_URL).hostname.toLowerCase();}catch{}
  const hostMatches=Boolean(configuredHost&&expectedHost&&configuredHost===String(expectedHost).trim().toLowerCase());
  const enabled=env.WRITES_ENABLED==='true';
  const approved=!production||env.PRODUCTION_WRITE_APPROVED==='true';
  return {production,homologation,hostMatches,hostConfigured:Boolean(expectedHost),enabled,approved,
    writesEnabled:Boolean((production||homologation)&&enabled&&approved&&hostMatches)};
}
export const writes=env=>writeControls(env).writesEnabled;
export const mayDeleteProduction=env=>env.APP_ENV!=='producao'||env.PRODUCTION_ALLOW_DELETE==='true';

/**
 * Controladoria may remove one accidental, unpointed convocation at a time in
 * production. Never loosen the global production deletion switch for bulk,
 * attended, linked, or other record types.
 */
export function permittedProductionDeletion(env,session,db,operations){
  if(mayDeleteProduction(env))return true;
  const deletions=operations.filter(op=>op.action==='delete');
  if(!deletions.length)return true;
  if(env.APP_ENV!=='producao')return false;
  // Correções de serviços não são exclusões de convocação ou apontamento.
  // Em produção, só aceitar vínculos antigos substituídos em uma transação
  // com auditoria integral e com ambos os registros principais preservados.
  if(deletions.every(op=>op.table==='servicos_apontamento')){
    if(!['SUPERVISOR','CONTROLADORIA'].includes(session.role)||deletions.length>100)return false;
    const ids=new Set(),oldServices=new Map(db.raw.servicos_apontamento.map(x=>[String(x.id),x]));
    const affected=new Set();
    for(const op of deletions){
      if(ids.has(String(op.id)))return false;
      ids.add(String(op.id));
      const old=oldServices.get(String(op.id));
      if(!old)return false;
      const convId=String(old.convocacao_id);
      const conv=db.raw.convocacoes.find(c=>String(c.id)===convId);
      if(!conv||session.role==='SUPERVISOR'&&conv.engenheiro!==session.user)return false;
      const pointed=operations.some(x=>x.table==='apontamentos'&&['insert','update'].includes(x.action)&&
        String(x.data?.convocacao_id)===convId);
      const convUpdated=operations.some(x=>x.table==='convocacoes'&&x.action==='update'&&String(x.id)===convId);
      if(!pointed||!convUpdated)return false;
      const audit=operations.find(x=>x.table==='auditoria'&&x.action==='insert'&&
        x.data?.acao==='CORRECAO_VINCULO_SERVICO_APONTAMENTO'&&
        String(x.data?.contexto?.servicoId)===String(op.id)&&
        String(x.data?.contexto?.convocacaoId)===convId&&
        String(x.data?.antes?.obraId)===String(old.obra_id||'')&&
        String(x.data?.antes?.periodo||'')===String(old.periodo||'')&&
        String(x.data?.antes?.unidade||'')===String(old.unidade_snapshot||'')&&
        String(x.data?.usuario)===session.user);
      if(!audit)return false;
      affected.add(convId);
    }
    for(const convId of affected){
      const pointOp=operations.find(x=>x.table==='apontamentos'&&['insert','update'].includes(x.action)&&
        String(x.data?.convocacao_id)===convId);
      const persisted=db.raw.servicos_apontamento.filter(x=>String(x.convocacao_id)===convId&&!ids.has(String(x.id))).length;
      const incoming=operations.filter(x=>x.table==='servicos_apontamento'&&x.action==='insert'&&
        String(x.data?.convocacao_id)===convId).length;
      if(!['Falta','Atestado'].includes(pointOp?.data?.status)&&persisted+incoming<1)return false;
    }
    return true;
  }
  if(session.role!=='CONTROLADORIA')return false;
  // A group of unlinked works can be deleted in one atomic Controladoria save.
  // Never extend this bulk permission to convocations or other record types.
  const safeWork=id=>{
    if(!/^[0-9]+$/.test(id)||!db.raw.obras.some(o=>String(o.id)===id))return false;
    if(db.raw.convocacoes.some(c=>String(c.obra_id)===id))return false;
    if(db.raw.servicos_apontamento.some(s=>String(s.obra_id)===id))return false;
    if(db.state.apontamentos.some(a=>a.itens.some(i=>i.servicos?.some(s=>String(s.obraId)===id))))return false;
    return true;
  };
  if(deletions.every(op=>op.table==='obras')){
    const unique=new Set(deletions.map(op=>op.id));
    return deletions.length<=50&&unique.size===deletions.length&&deletions.every(op=>safeWork(op.id));
  }
  if(deletions.length!==1)return false;
  const op=deletions[0];
  if(op.table!=='convocacoes'||!/^[0-9]+$/.test(op.id))return false;
  const existing=db.raw.convocacoes.find(c=>String(c.id)===op.id);
  if(!existing)return false;
  if(db.raw.apontamentos.some(a=>String(a.convocacao_id)===op.id))return false;
  if(db.raw.servicos_apontamento.some(s=>String(s.convocacao_id)===op.id))return false;
  if(db.state.apontamentos.some(a=>String(a.convocacaoId)===op.id))return false;
  if(db.raw.conflitos_convocacao.some(c=>String(c.convocacao_existente_id)===op.id))return false;
  return true;
}
