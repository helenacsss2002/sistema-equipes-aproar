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
  if(env.APP_ENV!=='producao'||session.role!=='CONTROLADORIA'||deletions.length!==1)return false;
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
