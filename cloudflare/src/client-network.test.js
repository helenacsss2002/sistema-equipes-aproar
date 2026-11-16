import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const source=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=source.indexOf('async function api(path,options={})');
const end=source.indexOf('\n  function applyOnline(',start);
assert(start>=0&&end>start,'Função api não localizada no frontend');
function apiWith(fetchMock){
  return new Function('fetch','setTimeout',source.slice(start,end)+'\nreturn api;')(fetchMock,callback=>callback());
}
const reply=(status,data)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json'}});

test('Retry de salvamento reutiliza body e requestId; confirma só após sucesso',async()=>{
  const attempts=[];
  const api=apiWith(async (_path,options)=>{
    attempts.push(options);
    if(attempts.length===1)throw new TypeError('network disconnected');
    if(attempts.length===2)return reply(502,{error:'Falha temporária do banco'});
    return reply(200,{ok:true,version:'novo'});
  });
  const body=JSON.stringify({requestId:'teste-id-fixo',version:'antiga',state:{}});
  assert.deepEqual(await api('/api/save',{method:'POST',body}),{ok:true,version:'novo'});
  assert.equal(attempts.length,3);
  assert(attempts.every(x=>x.body===body));
});

test('Conflito de versão 409 não é repetido',async()=>{
  let calls=0;
  const api=apiWith(async()=>{calls++;return reply(409,{error:'Versão antiga'});});
  await assert.rejects(api('/api/save',{method:'POST',body:'{}'}),/Versão antiga/);
  assert.equal(calls,1);
});

test('Login recupera um 503 temporário com no máximo uma repetição',async()=>{
  let calls=0;
  const api=apiWith(async()=>++calls===1?reply(503,{error:'Serviço temporariamente indisponível'}):reply(200,{session:{role:'CONTROLADORIA'}}));
  const result=await api('/api/login',{method:'POST',body:'{}'});
  assert.equal(result.session.role,'CONTROLADORIA');
  assert.equal(calls,2);
});

test('Senha errada 401 não gera novas tentativas de login',async()=>{
  let calls=0;
  const api=apiWith(async()=>{calls++;return reply(401,{error:'Senha inválida'});});
  await assert.rejects(api('/api/login',{method:'POST',body:'{}'}),/Senha inválida/);
  assert.equal(calls,1);
});

test('Outros POST nunca têm repetição automática',async()=>{
  let calls=0;
  const api=apiWith(async()=>{calls++;throw new TypeError('offline');});
  await assert.rejects(api('/api/trello/sync',{method:'POST',body:'{}'}),/offline/);
  assert.equal(calls,1);
});

test('Bootstrap recupera erro HTTP 503 transitório',async()=>{
  let calls=0;
  const api=apiWith(async()=>++calls===1?reply(503,{error:'Temporário'}):reply(200,{state:{},version:'v2'}));
  assert.equal((await api('/api/bootstrap')).version,'v2');
  assert.equal(calls,2);
});

test('Quando todas as tentativas falham, informa erro sem afirmar gravação',async()=>{
  let calls=0;
  const api=apiWith(async()=>{calls++;return reply(502,{error:'Banco temporariamente indisponível'});});
  await assert.rejects(api('/api/save',{method:'POST',body:'{}'}),/Banco temporariamente indisponível/);
  assert.equal(calls,4);
});
