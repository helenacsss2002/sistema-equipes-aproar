import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';

const app=readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const start=app.indexOf('  async function api(path,options={}){');
const end=app.indexOf('  async function submitComplementConfirmation(',start);
assert(start>=0&&end>start);
const source=app.slice(start,end);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
const pending=()=>new Promise(()=>{});
const response=(status,body)=>({status,ok:status>=200&&status<300,
 headers:{get:()=> 'application/json'},json:async()=>body});

function clock(){
 let now=0,nextId=0;
 const timers=new Map();
 return {
  setTimeout(fn,delay){const id=++nextId;timers.set(id,{at:now+delay,fn});return id;},
  clearTimeout(id){timers.delete(id);},
  get now(){return now;},get pending(){return timers.size;},
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

function element(tag='div'){
 const classes=new Set();
 return {tag,style:{},children:[],inert:false,value:'draft typed in the form',
  classList:{toggle(name,force){if(force)classes.add(name);else classes.delete(name);},contains(name){return classes.has(name);}},
  setAttribute(){},appendChild(child){this.children.push(child);return child;},
  set textContent(value){this.text=value;this.children=[];},get textContent(){return this.text||'';}};
}

function harness(fetch,{view='indisponibilidade'}={}){
 const time=clock(),calls=[],messages=[],ui={renders:0,successes:0,failures:[],unlockedAt:[]};
 const nodes=new Map([['#app-view',element()],['#online-saving',element()],['#draft-form',element('form')]]);
 const document={createElement:element,querySelector:selector=>nodes.get(selector)||null,
  body:{appendChild(node){if(node.id)nodes.set('#'+node.id,node);}}};
 const base={obras:[{id:'1',nome:'Serviço Centro',unidade:'CENTRO'}],colaboradores:[{id:'1',nome:'Pessoa QA'}],
  convocacoes:[],apontamentos:[],indisponibilidades:[]};
 const state=structuredClone(base);
 state.indisponibilidades.push({id:'draft-indisponibilidade',colaboradorId:'1',motivo:'Férias',inicio:'2026-11-16',fim:'2026-11-20',obs:'Não perder observação digitada'});
 const context={state,OBRAS:state.obras,COLABORADORES:state.colaboradores,
  onlineVersion:'v1',onlineSession:{role:'CONTROLADORIA',user:'CONTROLADORIA'},onlineWritable:true,
  onlineQueued:false,onlineSaving:false,onlineConfirmed:structuredClone(base),onlineMessage:'',onlineStage:'producao',
  perfilAtual:'CONTROLADORIA',supervisorAtual:'',viewAtual:view,apontamentoTab:'retroativo',retroUnsavedAvulsos:new Map(),
  crypto:webcrypto,AbortController,queueMicrotask,setTimeout:time.setTimeout,clearTimeout:time.clearTimeout,
  console:{warn(){},error(){}},copy:value=>structuredClone(value),document,$:document.querySelector,
  showToast:(message,error)=>messages.push({message,error}),
  render:()=>{ui.renders++;nodes.get('#draft-form').value='';},
  fetch:(path,options)=>{calls.push({path,options});return fetch(path,options,calls.length);}};
 vm.createContext(context);
 vm.runInContext(source+`\nconst originalLock=lockOnline;lockOnline=locked=>{originalLock(locked);if(!locked)recordUnlock();};
  globalThis.save=saveData;
  globalThis.snapshot=()=>({state,onlineWritable,onlineSaving,onlineQueued,pending:Boolean(pendingSaveRecovery)});
  globalThis.clearFeedbackTimer=()=>clearTimeout(showSaveFeedback._timer);`,
  Object.assign(context,{recordUnlock:()=>ui.unlockedAt.push(time.now)}));
 const bootstrap=()=>{
  const sent=calls.find(call=>call.path==='/api/save');
  return response(200,{state:JSON.parse(sent.options.body).state,version:'v2',session:{role:'CONTROLADORIA',user:'CONTROLADORIA'},writesEnabled:true,stage:'producao'});
 };
 const confirmed=path=>response(200,{confirmed:true,requestId:new URL('https://aproar.test'+path).searchParams.get('requestId')});
 const unconfirmed=path=>response(200,{confirmed:false,requestId:new URL('https://aproar.test'+path).searchParams.get('requestId')});
 const assertUnlocked=()=>{
  assert.equal(nodes.get('#app-view').inert,false);
  assert.equal(nodes.get('#online-saving').classList.contains('hidden'),true);
  assert.equal(context.snapshot().onlineSaving,false);
  assert.equal(context.snapshot().onlineQueued,false);
 };
 return {time,calls,messages,ui,context,bootstrap,confirmed,unconfirmed,assertUnlocked,
  later:(ms,value)=>new Promise(resolve=>time.setTimeout(()=>resolve(value),ms)),
  get form(){return nodes.get('#draft-form');},
  save({verify=null}={}){return context.save(()=>{ui.successes++;},verify,message=>ui.failures.push(message));},
  recover(){
   const button=nodes.get('#online-save-feedback')?.children.find(child=>child.tag==='button');
   assert(button,'Pending confirmation must offer a recovery button');button.onclick();
  },
  cleanFeedback(){context.clearFeedbackTimer();assert.equal(time.pending,0,'No operation deadlines or retry timers remain');}
 };
}

test('502 plus pending status queries releases the overlay and preserves the unavailable form',async()=>{
 let mode='uncertain',h;
 h=harness((path)=>{
  if(path==='/api/save')return response(502,{error:'Temporary Cloudflare failure'});
  if(path.startsWith('/api/save-status'))return mode==='uncertain'?pending():h.confirmed(path);
  if(path==='/api/bootstrap')return h.bootstrap();
  throw Error(path);
 });
 const draft=structuredClone(h.context.state);
 assert.equal(h.save(),true);
 await h.time.tick(30000);
 h.assertUnlocked();
 assert.equal(h.context.snapshot().onlineWritable,false);
 assert.equal(h.context.snapshot().pending,true);
 assert.deepEqual(h.context.snapshot().state,draft);
 assert.equal(h.form.value,'draft typed in the form');
 assert.equal(h.ui.renders,0);
 assert.equal(h.ui.successes,0);
 assert.equal(h.ui.failures.length,1);
 const before=h.calls.length;
 assert.equal(h.save(),false,'An uncertain write blocks every new save');
 assert.equal(h.calls.length,before);
 mode='confirmed';h.recover();await h.time.tick(0);
 h.assertUnlocked();
 assert.equal(h.context.snapshot().pending,false);
 assert.equal(h.context.snapshot().onlineWritable,true);
 assert.equal(h.ui.successes,1);
 assert.equal(h.calls.filter(call=>call.path==='/api/save').length,2,'Recovery first confirms the old request without a new POST');
 h.cleanFeedback();
});

test('An acknowledged save with pending bootstrap stays read-only and recovery performs no further POST',async()=>{
 let mode='pending',h;
 h=harness((path,options)=>{
  if(path==='/api/save')return response(200,{ok:true,requestId:JSON.parse(options.body).requestId});
  if(path==='/api/bootstrap')return mode==='pending'?pending():h.bootstrap();
  throw Error('An acknowledged operation needs only bootstrap: '+path);
 });
 h.save();await h.time.tick(10000);
 h.assertUnlocked();
 assert.equal(h.context.snapshot().onlineWritable,false);
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.ui.failures.length,1);
 assert.match(h.ui.failures[0],/banco confirmou a gravação/);
 assert.equal(h.form.value,'draft typed in the form');
 mode='ready';h.recover();await h.time.tick(0);
 h.assertUnlocked();
 assert.equal(h.calls.filter(call=>call.path==='/api/save').length,1);
 assert.equal(h.calls.filter(call=>call.path.startsWith('/api/save-status')).length,0);
 assert.equal(h.context.snapshot().onlineWritable,true);
 assert.equal(h.context.snapshot().pending,false);
 assert.equal(h.ui.successes,1);
 h.cleanFeedback();
});

test('A pending POST JSON body is bounded and commit confirmation avoids a duplicate POST',async()=>{
 let h;
 h=harness(path=>{
  if(path==='/api/save')return {...response(200,{}),json:pending};
  if(path.startsWith('/api/save-status'))return h.confirmed(path);
  if(path==='/api/bootstrap')return h.bootstrap();
  throw Error(path);
 });
 h.save();await h.time.tick(19999);
 assert.equal(h.context.snapshot().onlineSaving,true);
 await h.time.tick(1);
 h.assertUnlocked();
 assert.equal(h.calls.filter(call=>call.path==='/api/save').length,1);
 assert.equal(h.ui.successes,1);
 assert.equal(h.context.snapshot().onlineWritable,true);
 h.cleanFeedback();
});

test('The global forty-five-second budget cancels pending POST/status phases and leaves a recoverable draft',async()=>{
 const h=harness(pending);
 h.save();await h.time.tick(44999);
 assert.equal(h.context.snapshot().onlineSaving,true);
 await h.time.tick(1);
 h.assertUnlocked();
 assert.deepEqual(h.ui.unlockedAt,[45000]);
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.context.snapshot().onlineWritable,false);
 assert.equal(h.ui.successes,0);
 assert.equal(h.form.value,'draft typed in the form');
 assert(h.calls.every(call=>call.options.signal.aborted));
 h.cleanFeedback();
});

test('The global budget also interrupts status backoff at exactly forty-five seconds',async()=>{
 let h,posts=0,checks=0;
 h=harness(path=>{
  if(path==='/api/save'){
   posts++;
   return h.later(posts===1?19000:6000,response(502,{error:'Delayed gateway failure'}));
  }
  if(path.startsWith('/api/save-status')){
   checks++;
   return checks===4?h.unconfirmed(path):pending();
  }
  throw Error(path);
 });
 h.save();await h.time.tick(44999);
 assert.equal(h.context.snapshot().onlineSaving,true);
 await h.time.tick(1);
 h.assertUnlocked();
 assert.deepEqual(h.ui.unlockedAt,[45000]);
 assert.equal(checks,5,'The sixth status check must not begin after cancellation');
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.context.snapshot().onlineWritable,false);
 h.cleanFeedback();
});

test('Pending confirmation blocks alternate write routes and new save IDs before fetch',async()=>{
 let h;
 h=harness((path,options)=>{
  if(path==='/api/save')return response(200,{ok:true,requestId:JSON.parse(options.body).requestId});
  if(path==='/api/bootstrap')return pending();
  throw Error(path);
 });
 h.save();await h.time.tick(10000);h.assertUnlocked();
 const calls=h.calls.length;
 const original=JSON.parse(h.calls[0].options.body);
 for(const [path,body] of [
  ['/api/financial-adjust',JSON.stringify({amount:100})],
  ['/api/save',JSON.stringify({...original,requestId:webcrypto.randomUUID()})],
  ['/api/save',JSON.stringify({...original,state:{...original.state,indisponibilidades:[]}})]
 ])await assert.rejects(h.context.api(path,{method:'POST',body}),error=>error.status===409&&error.code==='APROAR_PENDING_SAVE');
 assert.equal(h.calls.length,calls);
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.context.snapshot().onlineWritable,false);
 assert.equal(h.form.value,'draft typed in the form');
 h.cleanFeedback();
});

test('Recovery checks the existing ID and resends exactly the original payload if still absent',async()=>{
 let mode='uncertain',h;
 h=harness((path,options)=>{
  if(path==='/api/save')return mode==='uncertain'?response(502,{error:'No acknowledgement'}):response(200,{ok:true,requestId:JSON.parse(options.body).requestId});
  if(path.startsWith('/api/save-status'))return h.unconfirmed(path);
  if(path==='/api/bootstrap')return h.bootstrap();
  throw Error(path);
 });
 h.save();await h.time.tick(6000);h.assertUnlocked();
 const original=h.calls.filter(call=>call.path==='/api/save').map(call=>call.options.body);
 assert.equal(original.length,2);
 assert.equal(original[0],original[1]);
 const firstRequestId=JSON.parse(original[0]).requestId;
 const before=h.calls.length;
 mode='recovery';h.recover();await h.time.tick(2100);
 h.assertUnlocked();
 const recovery=h.calls.slice(before);
 assert(recovery[0].path.startsWith('/api/save-status'));
 const posts=h.calls.filter(call=>call.path==='/api/save');
 assert.equal(posts.length,3);
 assert(posts.every(call=>call.options.body===original[0]));
 assert(recovery.filter(call=>call.path.startsWith('/api/save-status')).every(call=>new URL('https://aproar.test'+call.path).searchParams.get('requestId')===firstRequestId));
 assert.equal(h.context.snapshot().onlineWritable,true);
 assert.equal(h.context.snapshot().pending,false);
 assert.equal(h.ui.successes,1);
 h.cleanFeedback();
});

test('A failed participant verification calls its failure panel without dismantling the form',async()=>{
 let h;
 h=harness((path,options)=>{
  if(path==='/api/save')return response(200,{ok:true,requestId:JSON.parse(options.body).requestId});
  if(path==='/api/bootstrap')return h.bootstrap();
  throw Error(path);
 },{view:'convocacao'});
 h.save({verify:()=>false});await h.time.tick(0);
 h.assertUnlocked();
 assert.equal(h.ui.failures.length,1);
 assert.match(h.ui.failures[0],/espelho permanece aberto/);
 assert.equal(h.ui.renders,0);
 assert.equal(h.ui.successes,0);
 assert.equal(h.form.value,'draft typed in the form');
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.context.snapshot().onlineWritable,false);
 h.cleanFeedback();
});

for(const denial of [{status:401},{status:403},{status:503,code:'NEON_QUOTA_EXCEEDED'}]){
 test('An ambiguous POST followed by status '+denial.status+' retains its receipt through recovery and reauthentication',async()=>{
  let mode='denied',h;
  h=harness(path=>{
   if(path==='/api/save')return response(502,{error:'Gateway failed after a possible commit'});
   if(path.startsWith('/api/save-status'))return mode==='ready'?h.confirmed(path):response(denial.status,{error:'Status unavailable',code:denial.code});
   if(path==='/api/bootstrap')return h.bootstrap();
   throw Error(path);
  });
  h.save();await h.time.tick(0);h.assertUnlocked();
  const firstPayload=h.calls[0].options.body,firstId=JSON.parse(firstPayload).requestId;
  assert.equal(h.context.snapshot().pending,true);
  assert.equal(h.context.snapshot().onlineWritable,false);
  assert.equal(h.ui.successes,0);
  assert.equal(h.form.value,'draft typed in the form');
  assert.equal(h.save(),false,'A failed status lookup must not allow a new save ID');
  h.recover();await h.time.tick(0);h.assertUnlocked();
  assert.equal(h.context.snapshot().pending,true,'Recovery denial must retain the original receipt too');
  assert.equal(h.context.snapshot().onlineWritable,false);
  mode='ready';h.recover();await h.time.tick(0);h.assertUnlocked();
  const posts=h.calls.filter(call=>call.path==='/api/save');
  assert.equal(posts.length,1,'Status confirmation after reauthentication cannot resend an already committed operation');
  assert.equal(posts[0].options.body,firstPayload);
  assert(h.calls.filter(call=>call.path.startsWith('/api/save-status')).every(call=>new URL('https://aproar.test'+call.path).searchParams.get('requestId')===firstId));
  assert.equal(h.context.snapshot().pending,false);
  assert.equal(h.context.snapshot().onlineWritable,true);
  assert.equal(h.ui.successes,1);
  h.cleanFeedback();
 });
}

for(const status of [400,401,403]){
 test('An initial definitive POST '+status+' does not leave an uncertain receipt',async()=>{
  let h;
  h=harness(path=>{
   if(path==='/api/save')return response(status,{error:'Definitive request rejection'});
   if(path==='/api/bootstrap')return response(200,{state:structuredClone(h.context.onlineConfirmed),version:'v2',
    session:{role:'CONTROLADORIA',user:'CONTROLADORIA'},writesEnabled:true,stage:'producao'});
   throw Error('A definitive rejection does not need status polling: '+path);
  });
  h.save();await h.time.tick(0);h.assertUnlocked();
  assert.equal(h.context.snapshot().pending,false);
  assert.equal(h.context.snapshot().onlineWritable,true);
  assert.equal(h.context.snapshot().state.indisponibilidades.length,0);
  assert.equal(h.calls.filter(call=>call.path==='/api/save').length,1);
  assert.equal(h.ui.failures.length,1);
  assert.equal(h.ui.successes,0);
  assert.equal(h.form.value,'draft typed in the form');
  h.cleanFeedback();
 });
}

test('A retry rejected with 409 and three valid absent-ID checks safely reconciles the authoritative base',async()=>{
 let posts=0,h;
 h=harness(path=>{
  if(path==='/api/save')return response(++posts===1?502:409,{error:'Stale version; no changes applied'});
  if(path.startsWith('/api/save-status'))return h.unconfirmed(path);
  if(path==='/api/bootstrap')return response(200,{state:structuredClone(h.context.onlineConfirmed),version:'v2',
   session:{role:'CONTROLADORIA',user:'CONTROLADORIA'},writesEnabled:true,stage:'producao'});
  throw Error(path);
 });
 h.save();await h.time.tick(6000);h.assertUnlocked();
 assert.equal(posts,2);
 assert.equal(h.calls.filter(call=>call.path.startsWith('/api/save-status')).length,6);
 assert.equal(h.context.snapshot().pending,false);
 assert.equal(h.context.snapshot().onlineWritable,true);
 assert.equal(h.context.snapshot().state.indisponibilidades.length,0);
 assert.equal(h.ui.successes,0);
 assert.equal(h.ui.failures.length,1);
 assert.match(h.ui.failures[0],/Stale version/);
 h.cleanFeedback();
});

test('A retry 409 cannot discard the receipt when its status checks fail instead of confirming absence',async()=>{
 let posts=0,checks=0,h;
 h=harness(path=>{
  if(path==='/api/save')return response(++posts===1?502:409,{error:'Version changed'});
  if(path.startsWith('/api/save-status'))return ++checks<=3?h.unconfirmed(path):response(502,{error:'Status response lost'});
  throw Error('An unresolved write must not replace its draft with bootstrap: '+path);
 });
 h.save();await h.time.tick(6000);h.assertUnlocked();
 assert.equal(posts,2);
 assert.equal(checks,6);
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.context.snapshot().onlineWritable,false);
 assert.equal(h.ui.successes,0);
 assert.equal(h.form.value,'draft typed in the form');
 h.cleanFeedback();
});

test('A direct Neon quota response stops POST retries and retains a receipt for later confirmation',async()=>{
 let mode='quota',h;
 h=harness(path=>{
  if(path==='/api/save')return response(503,{error:'Neon quota exceeded',code:'NEON_QUOTA_EXCEEDED'});
  if(path.startsWith('/api/save-status'))return mode==='quota'?response(503,{error:'Quota',code:'NEON_QUOTA_EXCEEDED'}):h.confirmed(path);
  if(path==='/api/bootstrap')return h.bootstrap();
  throw Error(path);
 });
 h.save();await h.time.tick(0);h.assertUnlocked();
 assert.equal(h.calls.length,1,'A quota response must not start another POST or status retry sequence');
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.context.snapshot().onlineWritable,false);
 h.recover();await h.time.tick(0);h.assertUnlocked();
 assert.equal(h.calls.filter(call=>call.path==='/api/save').length,1);
 assert.equal(h.context.snapshot().pending,true);
 mode='ready';h.recover();await h.time.tick(0);h.assertUnlocked();
 assert.equal(h.calls.filter(call=>call.path==='/api/save').length,1);
 assert.equal(h.context.snapshot().pending,false);
 assert.equal(h.context.snapshot().onlineWritable,true);
 h.cleanFeedback();
});

test('An HTML 409 cannot serve as a definitive version rejection after an ambiguous POST',async()=>{
 let posts=0,h;
 h=harness(path=>{
  if(path==='/api/save')return ++posts===1?response(502,{error:'Gateway failure'}):{
   ...response(409,{}),headers:{get:()=> 'text/html'}
  };
  if(path.startsWith('/api/save-status'))return h.unconfirmed(path);
  throw Error('A malformed rejection must not discard the receipt: '+path);
 });
 h.save();await h.time.tick(6000);h.assertUnlocked();
 assert.equal(posts,2);
 assert.equal(h.context.snapshot().pending,true);
 assert.equal(h.context.snapshot().onlineWritable,false);
 assert.equal(h.form.value,'draft typed in the form');
 h.cleanFeedback();
});
