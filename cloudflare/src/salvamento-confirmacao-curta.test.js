import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';

const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const begin=app.indexOf('  function saveData(onSuccess=null){');
const end=app.indexOf('  async function submitComplementConfirmation(',begin);
assert(begin>=0&&end>begin,'O fluxo de salvamento deve estar presente');
const saveSource=app.slice(begin,end);

function setup({post,check,bootstrap}){
 const state={obras:[{id:'w1'}],colaboradores:[{id:'a1'}],convocacoes:[],apontamentos:[]};
 const calls=[],alerts=[],ui={render:0,synced:0};
 let resolveDone;const done=new Promise(resolve=>resolveDone=resolve);
 let onlineWritable=true;
 const ctx={
  state,OBRAS:state.obras,COLABORADORES:state.colaboradores,
  onlineVersion:'v1',onlineSession:{role:'SUPERVISOR',user:'EDUARDO'},
  onlineWritable:true,onlineQueued:false,onlineSaving:false,onlineConfirmed:structuredClone(state),onlineMessage:'',
  crypto:webcrypto,AbortController,queueMicrotask,
  setTimeout,clearTimeout,console,
  copy:v=>structuredClone(v),
  document:{querySelector:()=>null},
  lockOnline:()=>{},
  render:()=>{ui.render++;resolveDone();},
  showSaveFeedback:(message,error)=>alerts.push({message,error}),
  showToast:(message,error)=>alerts.push({message,error}),
  toast:(message,error)=>alerts.push({message,error}),
  restoreOnlineSession:async()=>typeof bootstrap==='function'?await bootstrap():({state,version:'v2',session:{role:'SUPERVISOR',user:'EDUARDO'},writesEnabled:true,stage:'producao'}),
  applyOnline:()=>{ui.synced++;},
  $:()=>null,
  perfilAtual:'SUPERVISOR',viewAtual:'apontamento',apontamentoTab:'retroativo',
  retroUnsavedAvulsos:new Map(),
  api:async(path,options)=>{
   calls.push({path,options});
   if(path==='/api/save')return post(path,options);
   if(path.startsWith('/api/save-status'))return check(path,options);
   throw Error('Unexpected endpoint '+path);
  },
 };
 vm.createContext(ctx);
 vm.runInContext(saveSource+'\nglobalThis.runSave=saveData;',ctx,{timeout:2000});
 return {ctx,calls,alerts,ui,done};
}
const wait=()=>new Promise(resolve=>setTimeout(resolve,35));
test('O servidor devolve ACK curto, com leitura do resultado feita em requisição separada',()=>{
 assert.match(worker,/const compactAck=request\.headers\.get\('x-aproar-save-ack'\)==='1'/);
 assert.match(worker,/return compactAck\?json\(\{ok:true,requestId:body\.requestId\}\):json\(\{\.\.\.summary/);
 assert.match(worker,/path==='\/api\/save-status'&&request\.method==='GET'/);
 assert.match(worker,/WHERE id=\$\{requestId\} AND actor=\$\{session\.user\}/);
 assert.match(worker,/if\(!\/\^\[a-f0-9-\]\{36\}\$\/i\.test\(requestId\)\)/);
});

test('Salvamento normal envia um único POST, sincroniza pelo bootstrap e mostra sucesso',async()=>{
 let rid;
 const x=setup({post:async(_path,opts)=>{
   rid=JSON.parse(opts.body).requestId;
   assert.equal(opts.headers['X-APROAR-Save-Ack'],'1');
   return {ok:true,requestId:rid};
 },check:()=>{throw Error('Status desnecessário')}});
 assert.equal(x.ctx.runSave(),true);
 await x.done;
 assert.equal(x.calls.filter(c=>c.path==='/api/save').length,1);
 assert.equal(x.calls.filter(c=>c.path.includes('save-status')).length,0);
 assert.equal(x.ui.synced,1);
 assert(x.alerts.some(a=>/gravado no Neon/.test(a.message)));
});

test('Resposta interrompida após commit é resolvida pelo identificador sem outro POST',async()=>{
 let rid;
 const x=setup({post:async(_path,opts)=>{
   rid=JSON.parse(opts.body).requestId;
   throw Object.assign(Error('Resposta incompleta'),{status:502,nonJson:true});
 },check:async path=>{
   assert.equal(new URL('https://site.local'+path).searchParams.get('requestId'),rid);
   return {confirmed:true,requestId:rid};
 }});
 x.ctx.runSave();await x.done;
 assert.equal(x.calls.filter(c=>c.path==='/api/save').length,1,'Não repetir POST');
 assert.equal(x.calls.filter(c=>c.path.startsWith('/api/save-status')).length,1);
 assert.equal(x.ui.synced,1);
 assert(x.alerts.some(a=>/gravado no Neon/.test(a.message)));
});

test('ACK confirmado, mas bootstrap indisponível não autoriza nova gravação nem acusa perda dos dados',async()=>{
 const x=setup({post:async(_path,opts)=>({ok:true,requestId:JSON.parse(opts.body).requestId}),
 check:()=>({confirmed:false}),bootstrap:async()=>{throw Error('GET indisponível')}});
 x.ctx.runSave();await wait();
 assert.equal(x.calls.filter(c=>c.path==='/api/save').length,1);
 assert.equal(x.ctx.onlineWritable,false);
 assert(x.alerts.some(a=>/foi SALVO/.test(a.message)));
 assert(x.alerts.some(a=>/Não lance novamente/.test(a.message)));
});

test('O banco armazena a requestId depois do commit e permite consultas de confirmação isoladas por usuário',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  const id=webcrypto.randomUUID(),version=(await pg.query('SELECT aproar_web_fingerprint() AS version')).rows[0].version;
  const operation=[{table:'obras',action:'insert',id:'work-test',data:{unidade:'UNIDADE QA',nome:'Servico QA'}}];
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[version,id,'EDUARDO','checksum',JSON.stringify(operation)]);
  const own=await pg.query('SELECT 1 AS saved FROM aproar_web_requests WHERE id=$1 AND actor=$2',[id,'EDUARDO']);
  const other=await pg.query('SELECT 1 AS saved FROM aproar_web_requests WHERE id=$1 AND actor=$2',[id,'SOARES']);
  assert.equal(own.rows.length,1);
  assert.equal(other.rows.length,0);
  assert.equal(Number((await pg.query('SELECT count(*) AS n FROM obras')).rows[0].n),1);
 }finally{await pg.close();}
});

test('Falha temporária 502 recupera gravando com MESMO ID e sem duplicar registros',async()=>{
 let firstPayload=null,attempts=0,checks=0;
 const x=setup({
  post:async(_path,opts)=>{
   attempts++;
   if(!firstPayload)firstPayload=opts.body;
   else assert.equal(opts.body,firstPayload,'Reenvio deve ser byte por byte idêntico');
   if(attempts===1)throw Object.assign(Error('Cloudflare 502'),{status:502,nonJson:true});
   return {ok:true,requestId:JSON.parse(opts.body).requestId};
  },
  check:async(path)=>{checks++;return {confirmed:false,requestId:new URL('https://site.local'+path).searchParams.get('requestId')};}
 });
 x.ctx.runSave();await x.done;
 assert.equal(attempts,2);
 assert.equal(x.calls.filter(c=>c.path==='/api/save').length,2);
 assert.equal(checks,3,'Verifica antes do reenvio');
 assert.equal(x.ui.synced,1);
 assert(x.alerts.some(x=>/gravado no Neon/.test(x.message)));
});

test('Após 3 respostas 502 sem confirmação, nenhum pedido novo é criado automaticamente',async()=>{
 const ids=[];
 const x=setup({
  post:async(_path,opts)=>{ids.push(JSON.parse(opts.body).requestId);throw Object.assign(Error('Cloudflare unavailable'),{status:502,nonJson:true});},
  check:async path=>({confirmed:false,requestId:new URL('https://site.local'+path).searchParams.get('requestId')})
 });
 x.ctx.runSave();
 await x.done;
 assert.equal(ids.length,3,'Tentativas limitadas a três');
 assert.equal(new Set(ids).size,1,'Nunca cria outra operação para a mesma confirmação');
 assert.equal(x.ui.synced,1,'Falha atualiza base para não insistir cegamente');
 assert(x.alerts.some(a=>/Nenhum segundo apontamento foi criado automaticamente/.test(a.message)));
});

test('Reenvio com 409 de versão antiga identifica gravação do envio anterior',async()=>{
 let calls=0,requestId='';
 const x=setup({
  post:async(_path,opts)=>{
   calls++;requestId=JSON.parse(opts.body).requestId;
   if(calls===1)throw Object.assign(Error('Bad gateway'),{status:502});
   throw Object.assign(Error('Versão alterada'),{status:409});
  },
  check:async path=>({confirmed:calls===2,requestId:new URL('https://site.local'+path).searchParams.get('requestId')})
 });
 x.ctx.runSave();await x.done;
 assert.equal(calls,2);
 assert.equal(x.ui.synced,1);
 assert(x.alerts.some(a=>/gravado no Neon/.test(a.message)));
});

test('Falha HTTP não mostra aviso antigo e nunca duplica a gravação ao confirmar o envio',async()=>{
 const original=app;
 assert.doesNotMatch(original,/O servidor interrompeu a resposta do salvamento\. Confira se o valor foi registrado antes de lançar novamente/);
 assert.match(original,/O sistema verificará automaticamente se o apontamento já foi registrado/);
 assert.match(original,/for\(let sendAttempt=0;sendAttempt<2&&!savedOnServer;sendAttempt\+\+\)/);
 assert.match(original,/if\(status===409&&await confirmById\(\)\)/);
 assert.match(original,/const result=reply\?\.state\?reply:await restoreOnlineSession\(\)/);
});
