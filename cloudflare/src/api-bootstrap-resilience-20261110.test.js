import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const workflow=fs.readFileSync(new URL('../../.github/workflows/aproar-cloudflare-production.yml',import.meta.url),'utf8');
const smoke=fs.readFileSync(new URL('../scripts/smoke-production.mjs',import.meta.url),'utf8');
const start=app.indexOf('  async function api(path,options={}){');
const end=app.indexOf('  function applyOnline(',start);
assert.ok(start>=0&&end>start,'Funções de conexão ausentes');
const source=app.slice(start,end);
const mockResponse=(status,contentType,body)=>({
 status,ok:status>=200&&status<300,
 headers:{get:key=>key.toLowerCase()==='content-type'?contentType:null},
 json:async()=>JSON.parse(body)
});
const htmlError=()=>mockResponse(502,'text/html','<html>Cloudflare temporarily unavailable</html>');
const jsonOk=()=>mockResponse(200,'application/json','{"session":{"role":"FINANCEIRO"},"state":{"apontamentos":[]},"version":"v1"}');

function harness(responses){
 let calls=0,delays=0;
 const ctx={
  fetch:async()=>{calls++;const value=responses[Math.min(calls-1,responses.length-1)];if(value instanceof Error)throw value;return value;},
  console:{warn(){}},
  setTimeout:fn=>{delays++;fn();}
 };
 vm.createContext(ctx);
 vm.runInContext(source+'\nglobalThis.aproarApi=api;globalThis.restore=restoreOnlineSession;',ctx);
 return {...ctx,get calls(){return calls;},get delays(){return delays;}};
}

test('Recupera automaticamente bootstrap de erro HTML/502 sem novo login',async()=>{
 const ctx=harness([htmlError(),jsonOk()]);
 const result=await ctx.aproarApi('/api/bootstrap');
 assert.equal(result.session.role,'FINANCEIRO');
 assert.equal(ctx.calls,2);
 assert.equal(ctx.delays,1);
});
test('Recupera erro de rede temporário ao fazer apenas leitura',async()=>{
 const ctx=harness([new TypeError('temporary network failure'),jsonOk()]);
 assert.equal((await ctx.restore()).session.role,'FINANCEIRO');
 assert.equal(ctx.calls,2);
});
test('Não repete automaticamente login POST quando perde resposta (evita múltiplas senhas/cookies)',async()=>{
 const ctx=harness([htmlError(),jsonOk()]);
 await assert.rejects(ctx.aproarApi('/api/login',{method:'POST',body:'{}'}),/página inválida/);
 assert.equal(ctx.calls,1);
 assert.equal(ctx.delays,0);
});
test('Não repete gravação POST quando recebe página de erro 502',async()=>{
 const ctx=harness([htmlError(),jsonOk()]);
 await assert.rejects(ctx.aproarApi('/api/save',{method:'POST',body:'{}'}),/registrado/);
 assert.equal(ctx.calls,1);
});
test('Respostas 401 de sessão expirada são respeitadas sem repetição de solicitações',async()=>{
 const ctx=harness([mockResponse(401,'application/json','{"error":"Faça login."}'),jsonOk()]);
 await assert.rejects(ctx.restore(),err=>err.status===401);
 assert.equal(ctx.calls,1);
});
test('Não insiste em consultas quando Neon esgota cota; erro é preservado',async()=>{
 const ctx=harness([mockResponse(503,'application/json','{"error":"Limite do Neon.","code":"NEON_QUOTA_EXCEEDED"}'),jsonOk()]);
 await assert.rejects(ctx.restore(),err=>err.code==='NEON_QUOTA_EXCEEDED');
 assert.equal(ctx.calls,1);
});
test('Respostas inválidas persistentes só geram até seis leituras, sem loop infinito',async()=>{
 const ctx=harness([htmlError()]);
 await assert.rejects(ctx.restore(),/página inválida/);
 assert.equal(ctx.calls,6);
});
test('Login autenticado permite refazer somente bootstrap sem reenviar a senha',()=>{
 const init=app.slice(app.indexOf('  async function initOnline(){'));
 assert.match(init,/pendingLoginBootstrapRole!==loginRole/);
 assert.match(init,/pendingLoginBootstrapRole=loginRole/);
 assert.match(init,/enterConnectedSession\(await restoreOnlineSession\(\)\)/);
 assert.match(app,/function chooseLogin\(role\)\{pendingLoginBootstrapRole='';/);
});
test('Publicação valida API real e assets diretamente na URL principal',()=>{
 assert.match(workflow,/name: Verify production API and assets after deploy/);
 assert.match(workflow,/run: node scripts\/smoke-production\.mjs/);
 assert.match(smoke,/\/api\/health/);
 assert.match(smoke,/\/api\/bootstrap/);
 assert.match(smoke,/\/app\.js/);
 assert.match(smoke,/databaseConfigured/);
});
