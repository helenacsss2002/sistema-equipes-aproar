import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const app=readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=app.indexOf('  async function api(path,options={}){');
const end=app.indexOf('  function applyOnline(',start);
assert(start>=0&&end>start);
const source=app.slice(start,end);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
const pending=()=>new Promise(()=>{});
const response=(status=200,body={ok:true})=>({
 status,ok:status>=200&&status<300,headers:{get:()=> 'application/json'},json:async()=>body
});

function clock(){
 let now=0,nextId=0;
 const timers=new Map();
 return {
  setTimeout(fn,delay){const id=++nextId;timers.set(id,{at:now+delay,fn});return id;},
  clearTimeout(id){timers.delete(id);},
  get pending(){return timers.size;},
  async tick(duration){
   const target=now+duration;
   await flush();
   for(;;){
    const next=[...timers].filter(([,timer])=>timer.at<=target).sort((a,b)=>a[1].at-b[1].at||a[0]-b[0])[0];
    if(!next)break;
    now=next[1].at;timers.delete(next[0]);next[1].fn();await flush();
   }
   now=target;await flush();
  }
 };
}

function trackedController(){
 const controller=new AbortController(),signal=controller.signal,listeners=new Set();
 const add=signal.addEventListener.bind(signal),remove=signal.removeEventListener.bind(signal);
 signal.addEventListener=(type,listener,options)=>{if(type==='abort')listeners.add(listener);return add(type,listener,options);};
 signal.removeEventListener=(type,listener,options)=>{if(type==='abort')listeners.delete(listener);return remove(type,listener,options);};
 return {controller,signal,get listeners(){return listeners.size;}};
}

function harness(fetch){
 const time=clock(),calls=[];
 const context={AbortController,setTimeout:time.setTimeout,clearTimeout:time.clearTimeout,console:{warn(){}},
  fetch:(path,options)=>{calls.push({path,options});return fetch(path,options,calls.length);}};
 vm.createContext(context);
 vm.runInContext(source+'\nglobalThis.call=api;globalThis.restore=restoreOnlineSession;',context);
 return {time,calls,api:context.call,restore:context.restore};
}

function observe(promise){
 let settled=false;
 const result=promise.then(value=>{settled=true;return {value};},error=>{settled=true;return {error};});
 return {result,get settled(){return settled;}};
}

test('Status confirmation has one hard six-second deadline even if fetch ignores abort',async()=>{
 const external=trackedController(),h=harness(pending);
 const result=observe(h.api('/api/save-status?requestId=test',{signal:external.signal,maxAttempts:3}));
 await h.time.tick(5999);
 assert.equal(result.settled,false);
 await h.time.tick(1);
 const {error}=await result.result;
 assert.equal(error.code,'APROAR_TIMEOUT');
 assert.equal(error.status,504);
 assert.equal(h.calls.length,1,'Status checks must not multiply their caller retries');
 assert.equal(h.calls[0].options.signal.aborted,true);
 assert.equal(h.time.pending,0);
 assert.equal(external.listeners,0);
});

test('The same deadline covers response body parsing after headers arrive',async()=>{
 let releaseHeaders;
 const headers=new Promise(resolve=>{releaseHeaders=resolve;});
 const external=trackedController(),h=harness(()=>headers);
 const result=observe(h.api('/api/save-status?requestId=test',{signal:external.signal}));
 await h.time.tick(3000);
 releaseHeaders({...response(),json:pending});
 await flush();
 await h.time.tick(2999);
 assert.equal(result.settled,false);
 await h.time.tick(1);
 assert.equal((await result.result).error.code,'APROAR_TIMEOUT');
 assert.equal(h.calls[0].options.signal.aborted,true);
 assert.equal(h.time.pending,0);
 assert.equal(external.listeners,0);
});

test('Bootstrap has a twelve-second default and explicit limits propagate through restore',async()=>{
 const h=harness(pending);
 const defaultRead=observe(h.api('/api/bootstrap',{maxAttempts:1}));
 await h.time.tick(11999);
 assert.equal(defaultRead.settled,false);
 await h.time.tick(1);
 assert.equal((await defaultRead.result).error.code,'APROAR_TIMEOUT');
 const external=trackedController();
 const restored=observe(h.restore({timeoutMs:50,maxAttempts:1,signal:external.signal}));
 await h.time.tick(50);
 assert.equal((await restored.result).error.code,'APROAR_TIMEOUT');
 assert.equal(h.calls.length,2,'Explicit maxAttempts also prevents a second outer restore cycle');
 assert.equal(h.time.pending,0);
 assert.equal(external.listeners,0);
 for(const call of h.calls){
  assert.equal('timeoutMs' in call.options,false);
  assert.equal('maxAttempts' in call.options,false);
 }
});

test('POST has a thirty-second deadline and is never automatically retried',async()=>{
 const h=harness(pending);
 const result=observe(h.api('/api/save',{method:'POST',body:'{}',maxAttempts:3}));
 await h.time.tick(29999);
 assert.equal(result.settled,false);
 await h.time.tick(1);
 assert.equal((await result.result).error.code,'APROAR_TIMEOUT');
 assert.equal(h.calls.length,1);
 assert.equal(h.calls[0].options.signal.aborted,true);
 assert.equal(h.time.pending,0);
});

test('External cancellation stops a pending fetch and prevents read retries',async()=>{
 const external=trackedController(),h=harness(pending);
 const result=observe(h.api('/api/bootstrap',{signal:external.signal}));
 external.controller.abort();
 await flush();
 assert.equal((await result.result).error.name,'AbortError');
 assert.equal(h.calls[0].options.signal.aborted,true);
 await h.time.tick(60000);
 assert.equal(h.calls.length,1);
 assert.equal(h.time.pending,0);
 assert.equal(external.listeners,0);
});

test('External cancellation also stops pending JSON consumption',async()=>{
 const external=trackedController(),h=harness(async()=>({...response(),json:pending}));
 const result=observe(h.api('/api/bootstrap',{signal:external.signal}));
 await flush();
 external.controller.abort();
 assert.equal((await result.result).error.name,'AbortError');
 assert.equal(h.calls[0].options.signal.aborted,true);
 assert.equal(h.calls.length,1);
 assert.equal(h.time.pending,0);
 assert.equal(external.listeners,0);
});

test('External cancellation removes backoff timers before another attempt',async()=>{
 const external=trackedController(),h=harness(async()=>response(502,{error:'Temporary failure'}));
 const result=observe(h.api('/api/bootstrap',{signal:external.signal}));
 await flush();
 assert.equal(h.calls.length,1);
 assert.equal(h.time.pending,1,'Only retry backoff remains after the failed attempt');
 external.controller.abort();
 assert.equal((await result.result).error.name,'AbortError');
 await h.time.tick(60000);
 assert.equal(h.calls.length,1);
 assert.equal(h.time.pending,0);
 assert.equal(external.listeners,0);
});

test('Restore outer recovery delay is cancellable and cannot restart the session query',async()=>{
 const external=trackedController(),h=harness(async()=>response(502,{error:'Temporary failure'}));
 const result=observe(h.restore({signal:external.signal}));
 await h.time.tick(1200);
 assert.equal(h.calls.length,3);
 assert.equal(h.time.pending,1,'Only the outer recovery delay remains');
 external.controller.abort();
 assert.equal((await result.result).error.name,'AbortError');
 await h.time.tick(60000);
 assert.equal(h.calls.length,3);
 assert.equal(h.time.pending,0);
 assert.equal(external.listeners,0);
});

test('Already cancelled requests never fetch and successful requests clean up their deadline',async()=>{
 const external=trackedController(),h=harness(async()=>response());
 external.controller.abort();
 assert.equal((await observe(h.restore({signal:external.signal})).result).error.name,'AbortError');
 assert.equal(h.calls.length,0);
 const active=trackedController();
 const result=await h.api('/api/bootstrap',{signal:active.signal,timeoutMs:50,maxAttempts:1});
 assert.equal(result.ok,true);
 assert.equal(h.calls[0].options.signal.aborted,false);
 assert.equal(h.time.pending,0);
 assert.equal(active.listeners,0);
});
