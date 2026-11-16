import test from 'node:test';
import assert from 'node:assert/strict';
import {writesEnabled} from './deploy-guards.js';

const db = 'postgresql://app:secret@production-host.neon.tech/neondb';
test('Producao exige aprovação explícita, flag de escrita e host correto', () => {
  const base = {APP_ENV:'producao', DATABASE_URL:db, WRITES_ENABLED:'true', PRODUCTION_EXPECTED_HOST:'production-host.neon.tech'};
  assert.equal(writesEnabled(base), false);
  assert.equal(writesEnabled({...base, PRODUCTION_WRITE_APPROVED:'true'}), true);
  assert.equal(writesEnabled({...base, PRODUCTION_WRITE_APPROVED:'true', PRODUCTION_EXPECTED_HOST:'outro.neon.tech'}), false);
  assert.equal(writesEnabled({...base, PRODUCTION_WRITE_APPROVED:'true', WRITES_ENABLED:'false'}), false);
});
test('Homologacao continua exigindo host próprio e bloqueia ambientes desconhecidos', () => {
  const base = {APP_ENV:'homologacao', DATABASE_URL:db, WRITES_ENABLED:'true', HOMOLOGATION_EXPECTED_HOST:'production-host.neon.tech'};
  assert.equal(writesEnabled(base), true);
  assert.equal(writesEnabled({...base, HOMOLOGATION_EXPECTED_HOST:'outro.neon.tech'}), false);
  assert.equal(writesEnabled({...base, APP_ENV:'local'}), false);
  assert.equal(writesEnabled({...base, DATABASE_URL:'invalido'}), false);
});
