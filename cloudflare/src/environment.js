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
