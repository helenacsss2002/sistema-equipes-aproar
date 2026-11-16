// Não permite gravar sem consentimento explícito e banco de dados correspondente ao ambiente.
export function writesEnabled(env) {
  if (!env || env.WRITES_ENABLED !== 'true') return false;
  let host;
  try {
    host = new URL(env.DATABASE_URL).hostname.toLowerCase();
  } catch {
    return false;
  }
  if (env.APP_ENV === 'homologacao') {
    return Boolean(env.HOMOLOGATION_EXPECTED_HOST) &&
      host === env.HOMOLOGATION_EXPECTED_HOST.trim().toLowerCase();
  }
  if (env.APP_ENV === 'producao') {
    return env.PRODUCTION_WRITE_APPROVED === 'true' &&
      Boolean(env.PRODUCTION_EXPECTED_HOST) &&
      host === env.PRODUCTION_EXPECTED_HOST.trim().toLowerCase();
  }
  return false;
}
