import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {neonQuotaExceeded,neonQuotaPublicMessage} from './neon-quota.js';
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const auth=fs.readFileSync(new URL('./auth.js',import.meta.url),'utf8');
test('Identifica limite do Neon',()=>{
  assert.equal(neonQuotaExceeded(new Error('Your account or project has exceeded the quota. Upgrade your plan to increase limits.')),true);
  assert.equal(neonQuotaExceeded(new Error('Server error (HTTP status 402)')),true);
  assert.equal(neonQuotaExceeded(new Error('Your project has exceeded the data transfer quota.')),true);
  assert.equal(neonQuotaExceeded(new Error('Senha incorreta')),false);
});
test('Resposta clara sem detalhes internos',()=>{
  assert.match(neonQuotaPublicMessage,/limite de uso/);
  assert.match(worker,/NEON_QUOTA_EXCEEDED/);
  assert.match(auth,/neonQuotaExceeded\(error\)/);
  assert.match(auth,/neonQuotaPublicMessage/);
});