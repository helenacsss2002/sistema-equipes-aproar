import test from 'node:test';
import assert from 'node:assert/strict';
import {writes,writeControls,stage,mayDeleteProduction} from './environment.js';
const base={APP_ENV:'producao',DATABASE_URL:'postgresql://test:password@ep-production.neon.tech/neondb',PRODUCTION_EXPECTED_HOST:'ep-production.neon.tech'};
test('Production is always read-only until two explicit write switches are enabled',()=>{
 assert.equal(writes(base),false);
 assert.equal(writes({...base,WRITES_ENABLED:'true'}),false);
 assert.equal(writes({...base,PRODUCTION_WRITE_APPROVED:'true'}),false);
 assert.equal(writes({...base,WRITES_ENABLED:'true',PRODUCTION_WRITE_APPROVED:'true'}),true);
});
test('Expected Neon hostname is required and must match exactly',()=>{
 const b={...base,WRITES_ENABLED:'true',PRODUCTION_WRITE_APPROVED:'true'};
 assert.equal(writes({...b,PRODUCTION_EXPECTED_HOST:undefined}),false);
 assert.equal(writes({...b,PRODUCTION_EXPECTED_HOST:'ep-other.neon.tech'}),false);
 assert.equal(writes({...b,DATABASE_URL:'not a URL'}),false);
 assert.equal(writes({...b,PRODUCTION_EXPECTED_HOST:'EP-PRODUCTION.NEON.TECH'}),true);
});
test('Unknown stage cannot write and production deletes default to blocked',()=>{
 const b={...base,WRITES_ENABLED:'true',PRODUCTION_WRITE_APPROVED:'true'};
 assert.equal(writes({...b,APP_ENV:'unknown'}),false);
 assert.equal(stage({...b,APP_ENV:'producao'}),'producao');
 assert.equal(mayDeleteProduction(b),false);
 assert.equal(mayDeleteProduction({...b,PRODUCTION_ALLOW_DELETE:'true'}),true);
});
test('Homologation retains its existing guarded write behavior',()=>{
 const b={APP_ENV:'homologacao',DATABASE_URL:'postgresql://test:password@ep-test.neon.tech/neondb',
 HOMOLOGATION_EXPECTED_HOST:'ep-test.neon.tech'};
 assert.equal(writes(b),false);
 assert.equal(writes({...b,WRITES_ENABLED:'true'}),true);
 assert.equal(writeControls({...b,WRITES_ENABLED:'true'}).approved,true);
 assert.equal(mayDeleteProduction(b),true);
});
