import test from 'node:test';
import assert from 'node:assert/strict';
import {login,identity} from './auth.js';

const env={SESSION_SECRET:'test-only-session-signing-secret'};
const credentials={EDUARDO:'TEST-KEY-EDUARDO',FELIPE:'TEST-KEY-FELIPE'};
const sql=async(strings,...values)=>{const [input,user]=values;return credentials[user]?[{password_matches:input===credentials[user]}]:[];};
const status=fn=>assert.rejects(fn,error=>error.status===401);

test('Supervisor login requires a key and rejects missing or incorrect keys',async()=>{
 await status(()=>login({role:'SUPERVISOR',supervisor:'EDUARDO'},env,sql));
 await status(()=>login({role:'SUPERVISOR',supervisor:'EDUARDO',password:'WRONG-KEY'},env,sql));
});

test('Each supervisor key only authenticates the corresponding supervisor and creates a signed session',async()=>{
 await status(()=>login({role:'SUPERVISOR',supervisor:'FELIPE',password:'TEST-KEY-EDUARDO'},env,sql));
 const result=await login({role:'SUPERVISOR',supervisor:'EDUARDO',password:'TEST-KEY-EDUARDO'},env,sql);
 assert.deepEqual(result.session,{role:'SUPERVISOR',user:'EDUARDO'});
 assert.match(result.cookie,/HttpOnly/);
 const request=new Request('https://aproar.test/api/bootstrap',{headers:{cookie:result.cookie.split(';')[0]}});
 const session=await identity(request,env);
 assert.equal(session?.user,'EDUARDO');
 assert.equal(session?.supervisorPasswordAuth,true);
});

test('Supervisor sessions issued before individual keys are rejected',async()=>{
 const encode=value=>Buffer.from(JSON.stringify(value)).toString('base64url');
 const payload=encode({role:'SUPERVISOR',user:'EDUARDO',exp:Math.floor(Date.now()/1000)+3600});
 const signingKey=await crypto.subtle.importKey('raw',new TextEncoder().encode(env.SESSION_SECRET),{name:'HMAC',hash:'SHA-256'},false,['sign']);
 const signature=new Uint8Array(await crypto.subtle.sign('HMAC',signingKey,new TextEncoder().encode(payload)));
 const request=new Request('https://aproar.test/api/bootstrap',{headers:{cookie:'aproar_session='+payload+'.'+encode([...signature])}});
 assert.equal(await identity(request,env),null);
});
