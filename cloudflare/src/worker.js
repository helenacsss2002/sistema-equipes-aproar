import { neon } from '@neondatabase/serverless';
import {mapNeonData} from './neon-adapter.js';
import {readDatabase,visibleState,supervisors} from './data.js';
import {buildOperations} from './operations.js';
import {login,identity,sameOrigin,equalSecret,logoutCookie} from './auth.js';
import {consultarTrello,sincronizarTrello,unidadeCard} from './trello.js';
const common={'cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'same-origin'};
const json=(data,status=200,extra={})=>new Response(JSON.stringify(data),{status,headers:{...common,'content-type':'application/json; charset=utf-8',...extra}});
const sha=async v=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(v)))].map(x=>x.toString(16).padStart(2,'0')).join('');
const writes=env=>{try{return env.WRITES_ENABLED==='true'&&env.APP_ENV==='homologacao'&&Boolean(env.HOMOLOGATION_EXPECTED_HOST)&&new URL(env.DATABASE_URL).hostname.toLowerCase()===env.HOMOLOGATION_EXPECTED_HOST.toLowerCase();}catch{return false;}};
const failedLogins=new Map();
function limit(request){const ip=request.headers.get('cf-connecting-ip')||'unknown',time=Date.now(),entry=failedLogins.get(ip);if(entry&&entry.until>time&&entry.n>=10)return false;if(!entry||entry.until<time)failedLogins.set(ip,{n:0,until:time+60000});failedLogins.get(ip).n++;if(failedLogins.size>5000)failedLogins.clear();return true;}
async function bodyJSON(request){if(Number(request.headers.get('content-length')||0)>8e6)throw Object.assign(Error('Dados muito grandes. Divida a operação.'),{status:413});const text=await request.text();if(text.length>8e6)throw Object.assign(Error('Dados muito grandes.'),{status:413});try{return JSON.parse(text);}catch{throw Object.assign(Error('Requisição inválida.'),{status:400});}}
function summary(db,session,env){return {state:visibleState(db,session),version:db.version,session:{role:session.role,user:session.user},supervisors,writesEnabled:writes(env)};}
export default {async fetch(request,env){const url=new URL(request.url),path=url.pathname;
 try{
  if(path==='/api/health'&&request.method==='GET')return json({application:'APROAR',stage:'homologacao',databaseConfigured:Boolean(env.DATABASE_URL),writesEnabled:writes(env)});
  if(path==='/api/login'&&request.method==='POST'){if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);if(!limit(request))return json({error:'Muitas tentativas. Aguarde um minuto.'},429);const result=await login(await bodyJSON(request),env);return json({session:result.session},200,{'set-cookie':result.cookie});}
  if(path==='/api/logout'&&request.method==='POST'){if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);return json({ok:true},200,{'set-cookie':logoutCookie});}
  if(path==='/api/check-database'||path==='/api/preview-data'){
   if(request.method!=='POST')return json({error:'Método não permitido.'},405);
   if(!env.DATABASE_URL||!env.CONNECTION_CHECK_TOKEN)return json({error:'Configure DATABASE_URL e CONNECTION_CHECK_TOKEN.'},503);
   if(!await equalSecret(request.headers.get('authorization')?.replace(/^Bearer /,''),env.CONNECTION_CHECK_TOKEN))return json({error:'Acesso não autorizado.'},401);
   const sql=neon(env.DATABASE_URL);if(path==='/api/preview-data'){const db=await readDatabase(sql);return json({writesEnabled:false,data:db.state});}
   const columns=await sql`SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('colaboradores','obras','convocacoes','apontamentos','servicos_apontamento')`;
   const expected={colaboradores:['id','nome','funcao','valor_diaria','ativo'],obras:['id','nome','unidade'],convocacoes:['id','obra_id','colaborador_id','data','engenheiro','turno'],apontamentos:['convocacao_id','data_servico','status','custo_pago','valor_extra','valor_acordo','valor_adicional_noturno'],servicos_apontamento:['convocacao_id','obra_id','periodo','principal']},missing=[];
   for(const [table,fields] of Object.entries(expected))for(const f of fields)if(!columns.some(c=>c.table_name===table&&c.column_name===f))missing.push(table+'.'+f);
   return json({connected:true,schemaCompatible:!missing.length,missingColumns:missing,writesEnabled:writes(env)});
  }
  if(path.startsWith('/api/')){
   const session=await identity(request,env);
   if(!session)return json({error:'Faça login para acessar a plataforma.'},401);
   if(path==='/api/homologacao/diagnostico'&&request.method==='GET'){
    if(session.role!=='CONTROLADORIA')return json({error:'Diagnóstico restrito à Controladoria.'},403);
    let dbHost='';
    try{dbHost=new URL(env.DATABASE_URL).hostname.toLowerCase();}catch{}
    return json({
     bancoConfigurado:Boolean(env.DATABASE_URL),
     enderecoBancoValido:Boolean(dbHost),
     ambienteHomologacao:env.APP_ENV==='homologacao',
     gravacaoHabilitadaNaCloudflare:env.WRITES_ENABLED==='true',
     hostEsperadoConfigurado:Boolean(env.HOMOLOGATION_EXPECTED_HOST),
     hostConfere:Boolean(dbHost&&env.HOMOLOGATION_EXPECTED_HOST&&dbHost===env.HOMOLOGATION_EXPECTED_HOST.toLowerCase()),
     writesEnabled:writes(env)
    });
   }
   if(!env.DATABASE_URL)return json({error:'Banco não configurado.'},503);
   const sql=neon(env.DATABASE_URL);
   if(path==='/api/trello/lists'&&request.method==='GET'){
    if(session.role!=='CONTROLADORIA')return json({error:'Somente a Controladoria pode consultar as listas do Trello.'},403);
    const board=await consultarTrello();
    return json({lists:board.lists,cards:board.cards.map(c=>({id:c.id,idList:c.idList,name:c.name,unidade:unidadeCard(c)}))});
   }
   if(path==='/api/trello/sync'&&request.method==='POST'){
    if(session.role!=='CONTROLADORIA')return json({error:'Somente a Controladoria pode sincronizar o Trello.'},403);
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);
    if(!writes(env))return json({error:'Sincronização bloqueada: confirme o ambiente, o hostname do Neon e a autorização de gravação.'},403);
    const payload=await bodyJSON(request);
    if(!payload||typeof payload!=='object'||Object.keys(payload).some(x=>!['listId','cardId'].includes(x)))return json({error:'Solicitação de sincronização inválida.'},400);
    for(const field of ['listId','cardId'])if(payload[field]!=null&&(typeof payload[field]!=='string'||payload[field].length>128))return json({error:'Identificador do Trello inválido.'},400);
    const result=await sincronizarTrello(sql,{listId:payload.listId,cardId:payload.cardId});
    return json({ok:true,...result});
   }
   if(path==='/api/bootstrap'&&request.method==='GET')return json(summary(await readDatabase(sql),session,env));
   if(path==='/api/save'&&request.method==='POST'){
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);if(!writes(env))return json({error:'Gravação desativada. Configure APP_ENV=homologacao e WRITES_ENABLED=true para a branch de testes.'},403);
    const body=await bodyJSON(request);if(!/^[a-f0-9-]{36}$/i.test(body.requestId||'')||typeof body.version!=='string')return json({error:'Identificador de requisição inválido.'},400);
    const digest=await sha(JSON.stringify(body)),previous=await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${body.requestId}`;
    if(previous.length){if(previous[0].actor!==session.user||previous[0].payload_hash!==digest)return json({error:'Identificador de requisição reutilizado.'},409);return json({...summary(await readDatabase(sql),session,env),ok:true,replayed:true});}
    const db=await readDatabase(sql);if(body.version!==db.version)return json({error:'Outro usuário atualizou os dados. Suas alterações não foram gravadas; recarregue e confira os registros.'},409);
    const operations=buildOperations(db,body.state,session);
    // Work deletions run after dependent records, never before them.
    operations.sort((a,b)=>(a.table==='obras'&&a.action==='delete'?1:0)-(b.table==='obras'&&b.action==='delete'?1:0));
    if(operations.length)await sql`SELECT aproar_web_apply(${body.version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb)`;
    return json({...summary(await readDatabase(sql),session,env),ok:true});
   }
   return json({error:'Rota não encontrada.'},404);
  }
  if(request.method!=='GET'&&request.method!=='HEAD')return json({error:'Método não permitido.'},405);
  if(env.ASSETS){const response=await env.ASSETS.fetch(request);const headers=new Headers(response.headers);for(const [k,v] of Object.entries(common))headers.set(k,v);headers.set('content-security-policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");return new Response(response.body,{status:response.status,headers});}
  return json({message:'Interface ainda não publicada.'},404);
 }catch(e){
  if(path.startsWith('/api/trello/')){
   console.error('APROAR Trello route failure', JSON.stringify({
    route:path, type:String(e?.name||'Error').slice(0,80),
    code:String(e?.code||'none').slice(0,80),
    detail:String(e?.message||'No error message').slice(0,320)
   }));
  }
  if(e.status)return json({error:e.message,...(e.details?{details:e.details}:{})},e.status);
  const message=String(e.message||'');if(message.includes('APROAR_STALE'))return json({error:'Os dados mudaram durante a gravação. Nenhuma alteração foi salva. Atualize e tente novamente.'},409);
  if(message.includes('APROAR_REQUEST_MISMATCH'))return json({error:'Requisição repetida com conteúdo diferente.'},409);
  if(e.code==='23505')return json({error:'Já existe um registro equivalente. Atualize os dados e confira antes de repetir.'},409);
  if(e.code==='23503')return json({error:'Este registro está vinculado ao histórico e não pode ser excluído.'},409);
  if(e.code==='42883'||e.code==='42P01')return json({error:'Execute migracao_homologacao.sql na branch de testes antes de abrir a nova plataforma.'},503);
  return json({error:'Não foi possível concluir a operação. Confira a conexão e a estrutura da branch de homologação.'},502);
 }
},
 async scheduled(event,env,ctx){
  // Somente ativar depois de validar a leitura real do Trello e as gravacoes no Neon de homologacao.
  if(env.TRELLO_AUTO_SYNC_ENABLED!=='true'||!writes(env))return;
  ctx.waitUntil((async()=>{try{const sql=neon(env.DATABASE_URL);const r=await sql`SELECT sincronizado_obras_em,ultima_tentativa_obras_em FROM trello_snapshot WHERE snapshot_id=1`;const last=r[0]?.sincronizado_obras_em||r[0]?.ultima_tentativa_obras_em;
   if(last&&Date.now()-new Date(last).getTime()<11.5*60*60*1000)return;
   await sincronizarTrello(sql);
  }catch(e){console.error('Falha na sincronização Trello:',String(e?.message||e));}})());
 }
};
