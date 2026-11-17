// Read-only release gate. Cloudflare responses and source stay in process memory.
// The token is supplied only to this process by GitHub Actions; never print it.
import {createHash} from 'node:crypto';
import {readdir, readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const WORKER = 'sistema-equipes-aproar';
const ORIGIN = 'https://sistema-equipes-aproar.helenacsss2002.workers.dev';
const apiRoot = 'https://api.cloudflare.com/client/v4';
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const emit = value => console.log(JSON.stringify(value));
class AuditError extends Error {}
const ensure = (value, message) => {if (!value) throw new AuditError(message);};
const etag = value => typeof value === 'string' ? value.replace(/^W\//, '').replace(/^"|"$/g, '') : '';

async function files(directory, prefix = '') {
  const result = [];
  for (const item of await readdir(directory, {withFileTypes: true})) {
    ensure(!item.isSymbolicLink(), 'A local audit input contains a symbolic link.');
    const name = prefix + item.name;
    if (item.isDirectory()) result.push(...await files(path.join(directory, item.name), name + '/'));
    else if (item.isFile()) result.push(name);
  }
  return result.sort();
}

export async function auditProduction(options = {}) {
  const token = process.env.CLOUDFLARE_API_TOKEN;
  const account = process.env.CLOUDFLARE_ACCOUNT_ID;
  const baselineRoot = options.baselineRoot || process.env.APROAR_BASELINE_ROOT;
  const bundleRoot = options.bundleRoot || process.env.APROAR_BASELINE_BUNDLE;
  const baselineSha = options.baselineSha || process.env.APROAR_BASELINE_SHA;
  ensure(token && account, 'Cloudflare repository credentials are unavailable.');
  ensure(/^[a-f0-9]{32}$/i.test(account), 'Cloudflare account ID is invalid.');
  ensure(baselineRoot && bundleRoot && typeof baselineSha === 'string' && /^[a-f0-9]{40}$/i.test(baselineSha),
    'An explicit 40-character production baseline SHA was not supplied.');

  // This is the only authenticated transport. No caller can choose a method or host.
  async function api(suffix, kind = 'json') {
    ensure(/^\/(?:deployments|versions\/[a-f0-9-]+|settings|content\/v2)$/.test(suffix),
      'Unsupported read-only Cloudflare endpoint.');
    let response;
    try {
      response = await fetch(`${apiRoot}/accounts/${account}/workers/scripts/${WORKER}${suffix}`, {
        method: 'GET', redirect: 'error', signal: AbortSignal.timeout(30000),
        headers: {Authorization: `Bearer ${token}`, Accept: kind === 'json' ? 'application/json' : '*/*'}
      });
    } catch {throw new AuditError(`Cloudflare GET ${suffix} could not be completed.`);}
    ensure(response.ok, `Cloudflare GET ${suffix} returned HTTP ${response.status}.`);
    if (kind !== 'json') return response;
    let envelope;
    try {envelope = await response.json();} catch {throw new AuditError(`Cloudflare GET ${suffix} returned invalid JSON.`);}
    ensure(envelope.success === true && envelope.result, `Cloudflare GET ${suffix} was unsuccessful.`);
    return envelope.result;
  }

  function activeDeployment(result) {
    const deployment = result.deployments?.[0];
    ensure(deployment?.id && Array.isArray(deployment.versions), 'No current deployment was returned.');
    ensure(deployment.versions.length === 1 && deployment.versions[0].percentage === 100,
      'Production uses multiple versions or partial traffic; comparison is incomplete.');
    const version = deployment.versions[0].version_id;
    ensure(/^[a-f0-9-]{36}$/i.test(version), 'Active Worker version ID is invalid.');
    return {deployment: deployment.id, version};
  }

  const active = activeDeployment(await api('/deployments'));
  emit({baseline: baselineSha.toLowerCase(), activeVersion: active.version});
  const version = await api(`/versions/${active.version}`);
  const settings = await api('/settings');
  ensure(version.id === active.version, 'Version metadata does not match the active deployment.');
  const bindings = version.resources?.bindings;
  ensure(Array.isArray(bindings), 'Active-version bindings were not returned as an array.');
  const settingBindings = settings.bindings;
  ensure(Array.isArray(settingBindings), 'Current Worker bindings were not returned as an array.');
  // Values may include private configuration. Never serialize either collection.
  const activeBindings = new Map(bindings.map(binding => [binding.name, binding]));
  const currentBindings = new Map(settingBindings.map(binding => [binding.name, binding]));
  const hasSecret = (collection, name) => collection.get(name)?.type === 'secret_text';
  const plainValue = name => {
    const binding = activeBindings.get(name);
    return binding?.type === 'plain_text' ? binding.text : undefined;
  };
  const checks = {
    djouneSecretActive: hasSecret(activeBindings, 'DJOUNE_XAVIER_PASSWORD'),
    djouneSecretCurrent: hasSecret(currentBindings, 'DJOUNE_XAVIER_PASSWORD'),
    databaseSecret: hasSecret(activeBindings, 'DATABASE_URL'),
    sessionSecret: hasSecret(activeBindings, 'SESSION_SECRET') || hasSecret(activeBindings, 'CONNECTION_CHECK_TOKEN'),
    adminSecret: hasSecret(activeBindings, 'ADMIN_PASSWORD'),
    financeSecret: hasSecret(activeBindings, 'FINANCE_PASSWORD'),
    productionEnvironment: plainValue('APP_ENV') === 'producao',
    writesEnabled: plainValue('WRITES_ENABLED') === 'true',
    productionWriteApproved: plainValue('PRODUCTION_WRITE_APPROVED') === 'true',
    expectedDatabaseHostConfigured: typeof plainValue('PRODUCTION_EXPECTED_HOST') === 'string' &&
      plainValue('PRODUCTION_EXPECTED_HOST').trim().length > 0,
    assetsBinding: activeBindings.get('ASSETS')?.type === 'assets',
    compatibilityDate: version.resources?.script_runtime?.compatibility_date === '2026-10-08',
    compatibilityFlags: (version.resources?.script_runtime?.compatibility_flags || []).length === 0
  };
  emit({secretNames: bindings.filter(binding => binding.type === 'secret_text').map(binding => binding.name).sort(), checks});
  ensure(Object.values(checks).every(Boolean), 'A required secret or production configuration check failed.');

  const content = await api('/content/v2', 'content');
  const contentEtag = etag(content.headers.get('etag'));
  const activeEtag = etag(version.resources?.script?.etag);
  // content/v2 may describe the latest upload. An ETag match to the version
  // carrying 100% traffic is mandatory before treating it as active source.
  const contentChecks = {
    contentEtagPresent: Boolean(contentEtag), activeEtagPresent: Boolean(activeEtag),
    contentIsActiveVersion: Boolean(contentEtag && activeEtag && contentEtag === activeEtag),
    multipartContent: content.headers.get('content-type')?.startsWith('multipart/') === true
  };
  emit({checks: contentChecks});
  ensure(Object.values(contentChecks).every(Boolean), 'Cannot prove content/v2 is the active Worker version.');

  let form;
  try {form = await content.formData();} catch {throw new AuditError('Worker multipart content could not be parsed.');}
  const remoteModules = new Map();
  for (const [field, value] of form.entries()) {
    // Some API variants include upload metadata. It is never a source module.
    if (field === 'metadata') continue;
    const name = typeof value === 'string' ? field : value.name || field;
    ensure(/^[a-zA-Z0-9_./@+-]+$/.test(name) && !name.split('/').includes('..'), 'Worker returned an invalid module name.');
    ensure(!remoteModules.has(name), 'Worker returned duplicate modules.');
    remoteModules.set(name, typeof value === 'string' ? Buffer.from(value) : Buffer.from(await value.arrayBuffer()));
  }
  const localModules = (await files(bundleRoot)).filter(name => name !== 'README.md' && !name.endsWith('.map'));
  ensure(localModules.length > 0, 'The baseline dry-run bundle is empty.');
  ensure(JSON.stringify([...remoteModules.keys()].sort()) === JSON.stringify(localModules), 'Production module inventory differs from the baseline.');
  const entrypoint = content.headers.get('cf-entrypoint');
  ensure(entrypoint && remoteModules.has(entrypoint), 'The Worker entrypoint cannot be verified.');
  let modulesMatch = true;
  for (const name of localModules) {
    const baselineHash = sha256(await readFile(path.join(bundleRoot, name)));
    const productionHash = sha256(remoteModules.get(name));
    const matches = baselineHash === productionHash;
    emit({module: name, baselineHash, productionHash, matches});
    modulesMatch &&= matches;
  }
  ensure(modulesMatch, 'Production Worker bytes differ from the fixed GitHub baseline.');

  const publicRoot = path.join(baselineRoot, 'cloudflare/public');
  let assetsMatch = true;
  for (const name of await files(publicRoot)) {
    // Credentials are deliberately absent from this independent public request.
    const pathname = name.split('/').map(encodeURIComponent).join('/');
    let response;
    try {
      response = await fetch(`${ORIGIN}/${pathname}`, {
        method: 'GET', redirect: 'follow', signal: AbortSignal.timeout(30000),
        headers: {'Cache-Control': 'no-cache', 'Accept-Encoding': 'identity'}
      });
    } catch {throw new AuditError('A public asset could not be downloaded.');}
    ensure(response.ok && new URL(response.url).origin === ORIGIN, 'A public asset returned an unexpected response.');
    const baselineHash = sha256(await readFile(path.join(publicRoot, name)));
    const productionHash = sha256(Buffer.from(await response.arrayBuffer()));
    const matches = baselineHash === productionHash;
    emit({asset: name, baselineHash, productionHash, matches});
    assetsMatch &&= matches;
  }
  ensure(assetsMatch, 'A production asset differs from the fixed GitHub baseline.');

  const healthResponse = await fetch(`${ORIGIN}/api/health`, {method: 'GET', redirect: 'error', signal: AbortSignal.timeout(30000)});
  ensure(healthResponse.ok, 'Production health check failed.');
  const health = await healthResponse.json();
  const healthChecks = {application: health.application === 'APROAR', production: health.stage === 'producao',
    databaseConfigured: health.databaseConfigured === true, writesEnabled: health.writesEnabled === true};
  emit({checks: healthChecks});
  ensure(Object.values(healthChecks).every(Boolean), 'Production health configuration differs from expectations.');
  const after = activeDeployment(await api('/deployments'));
  ensure(after.deployment === active.deployment && after.version === active.version,
    'The active deployment changed during the audit; repeat comparison.');
  emit({checks: {activeDeploymentStable: true, backendMatchesBaseline: true, allBaselineAssetsMatch: true},
    activeVersion: active.version,
    limits: 'Checks every baseline asset; the public API does not enumerate extra remote assets. Secret values are not retrieved or tested. No remote source or settings are persisted.'});
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const names = new Map([['--baseline-root', 'baselineRoot'], ['--bundle-root', 'bundleRoot'], ['--baseline-sha', 'baselineSha']]);
  const options = {};
  let valid = true;
  for (let index = 2; index < process.argv.length; index += 2) {
    const name = names.get(process.argv[index]), value = process.argv[index + 1];
    if (!name || !value || options[name]) {valid = false; break;}
    options[name] = value;
  }
  const operation = valid ? auditProduction(options) : Promise.reject(new AuditError('Unsupported audit arguments.'));
  operation.catch(error => {
    // Only our controlled errors are printable. Unexpected errors could contain
    // HTTP bodies, headers, bindings or source, so their messages are suppressed.
    console.error(error instanceof AuditError ? error.message : 'Production audit failed; sensitive diagnostic details were suppressed.');
    process.exitCode = 1;
  });
}
