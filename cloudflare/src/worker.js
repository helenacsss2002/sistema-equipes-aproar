import { neon } from '@neondatabase/serverless';
import {mapNeonData,metadata} from './neon-adapter.js';
import {readDatabase,visibleState,supervisors} from './data.js';
import {buildOperations} from './operations.js';
import {validateFinancialPayload,buildFinancialOperations} from './financial-adjust.js';
import {validateComplementConfirmation,buildComplementConfirmationOperations} from './financial-approval.js';
import {login,identity,sameOrigin,equalSecret,logoutCookie} from './auth.js';
import {writes,writeControls,stage,permittedProductionDeletion} from './environment.js';
import {consultarTrello,sincronizarTrello,unidadeCard} from './trello.js';
const common={'cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'same-origin'};
const json=(data,status=200,extra={})=>new Response(JSON.stringify(data),{status,headers:{...common,'content-type':'application/json; charset=utf-8',...extra}});
const sha=async v=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(v)))].map(x=>x.toString(16).padStart(2,'0')).join('');
const failedLogins=new Map();
// Cadastros independentes: obtenha a versao no servidor, sem depender da tela.
// Em caso de edicao simultanea, reavalie os dados e tente novamente apenas
// a transacao atomica/idempotente (mesmo requestId, nunca dupla inclusao).
async function applyCatalogRegistration(sql,requestId,actor,digest,operationsForCurrentState){
 for(let attempt=0;attempt<3;attempt++){
  const current=await sql`SELECT aproar_web_fingerprint() AS version`;
  const operations=await operationsForCurrentState();
  try{
   const applied=await sql`SELECT aproar_web_apply(${current[0].version},${requestId},${actor},${digest},${JSON.stringify(operations)}::jsonb) AS result`;
   return applied[0].result;
  }catch(error){
   if(!String(error?.message||'').includes('APROAR_STALE')||attempt===2)throw error;
  }
 }
}
function limit(request){const ip=request.headers.get('cf-connecting-ip')||'unknown',time=Date.now(),entry=failedLogins.get(ip);if(entry&&entry.until>time&&entry.n>=10)return false;if(!entry||entry.until<time)failedLogins.set(ip,{n:0,until:time+60000});failedLogins.get(ip).n++;if(failedLogins.size>5000)failedLogins.clear();return true;}
async function bodyJSON(request){if(Number(request.headers.get('content-length')||0)>8e6)throw Object.assign(Error('Dados muito grandes. Divida a operação.'),{status:413});const text=await request.text();if(text.length>8e6)throw Object.assign(Error('Dados muito grandes.'),{status:413});try{return JSON.parse(text);}catch{throw Object.assign(Error('Requisição inválida.'),{status:400});}}
function summary(db,session,env){return {state:visibleState(db,session),version:db.version,session:{role:session.role,user:session.user},supervisors,writesEnabled:writes(env),stage:stage(env)};}
export default {async fetch(request,env){const url=new URL(request.url),path=url.pathname;let loginStage='request',session=null;
 try{
  if(path==='/api/health'&&request.method==='GET')return json({application:'APROAR',stage:stage(env),databaseConfigured:Boolean(env.DATABASE_URL),writesEnabled:writes(env)});
  if(path==='/api/login'&&request.method==='POST'){loginStage='check-origin';if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);loginStage='rate-limit';if(!limit(request))return json({error:'Muitas tentativas. Aguarde um minuto.'},429);loginStage='parse-request';const body=await bodyJSON(request);let authSql=null;if(body.role==='SUPERVISOR'){loginStage='check-database-config';if(!env.DATABASE_URL)return json({error:'Banco não configurado para validar a chave do supervisor.'},503);loginStage='create-database-client';authSql=neon(env.DATABASE_URL);}loginStage='authenticate';const result=await login(body,env,authSql);loginStage='format-response';return json({session:result.session},200,{'set-cookie':result.cookie});}
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
   session=await identity(request,env);
   if(!session)return json({error:'Faça login para acessar a plataforma.'},401);
   if(path==='/api/homologacao/diagnostico'&&request.method==='GET'){
    if(session.role!=='CONTROLADORIA')return json({error:'Diagnóstico restrito à Controladoria.'},403);
    const controls=writeControls(env);
    return json({
     bancoConfigurado:Boolean(env.DATABASE_URL),
     enderecoBancoValido:controls.hostMatches||Boolean(env.DATABASE_URL),
     ambienteHomologacao:controls.homologation,
     ambienteProducao:controls.production,
     gravacaoHabilitadaNaCloudflare:controls.enabled,
     aprovacaoProducao:controls.approved,
     hostEsperadoConfigurado:controls.hostConfigured,
     hostConfere:controls.hostMatches,
     writesEnabled:controls.writesEnabled
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
   // Avoid retrieving multi-year audit logs for users who do not view them.
   const readOptions=session.role==='FINANCEIRO'?{includeAudit:false}:session.role==='SUPERVISOR'?{auditUser:session.user}:{};
   if(path==='/api/bootstrap'&&request.method==='GET')return json(summary(await readDatabase(sql,readOptions),session,env));
   // Read-only acknowledgement: disambiguates a write whose HTTP response was lost.
   // Confirm only operations belonging to this authenticated user, never infer from a global version.
   if(path==='/api/save-status'&&request.method==='GET'){
    const requestId=url.searchParams.get('requestId')||'';
    if(!/^[a-f0-9-]{36}$/i.test(requestId))return json({error:'Identificador de salvamento inválido.'},400);
    const rows=await sql`SELECT 1 AS saved FROM aproar_web_requests WHERE id=${requestId} AND actor=${session.user} LIMIT 1`;
    return json({confirmed:rows.length>0,requestId});
   }
   if(path==='/api/financial-confirm-duplicate'&&request.method==='POST'){
    if(session.role!=='FINANCEIRO')return json({error:'Somente o Financeiro pode confirmar pagamentos distintos.'},403);
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);
    if(!writes(env))return json({error:'Gravação não autorizada neste ambiente.'},403);
    const body=validateComplementConfirmation(await bodyJSON(request));
    const rows=await sql`SELECT c.id::text AS convocacao_id,c.observacao,
     c.custo_pago AS complemento_convocacao,c.valor_acordo AS acordo_convocacao,
     a.id::text AS apontamento_id,a.status,
     a.custo_pago AS complemento_atual,a.valor_acordo AS acordo_atual
     FROM convocacoes c JOIN apontamentos a ON a.convocacao_id=c.id::text
     WHERE c.id::text=${body.convocacaoId}`;
    const operations=buildComplementConfirmationOperations(body,rows[0],session.user);
    const digest=await sha(JSON.stringify(body));
    const applied=await sql`SELECT aproar_web_apply(${body.version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb) AS result`;
    return json({ok:true,version:applied[0].result.version});
   }
   if(path==='/api/financial-adjust'&&request.method==='POST'){
    if(session.role!=='FINANCEIRO')return json({error:'Somente o Financeiro pode lançar pagamentos e passagens.'},403);
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);
    if(!writes(env))return json({error:'Gravação não autorizada neste ambiente.'},403);
    const body=validateFinancialPayload(await bodyJSON(request));
    const ids=body.changes.map(change=>change.convocacaoId).join(',');
    // Read only the attendance rows being adjusted. No full-state parse or serialization.
    const rows=await sql`SELECT c.id::text AS convocacao_id,c.observacao,a.id::text AS apontamento_id,a.status,
      a.valor_adicional_noturno AS noturno_atual,
      (coalesce(upper(o.unidade),'')='SEBRAE' OR EXISTS(
        SELECT 1 FROM servicos_apontamento s JOIN obras so ON so.id::text=s.obra_id
        WHERE s.convocacao_id=a.convocacao_id AND upper(so.unidade)='SEBRAE'
      )) AS has_sebrae
      FROM convocacoes c JOIN apontamentos a ON a.convocacao_id=c.id::text
      LEFT JOIN obras o ON o.id=c.obra_id
      WHERE a.convocacao_id=ANY(string_to_array(${ids},','))`;
    const operations=buildFinancialOperations(body.changes,rows,session.user);
    const digest=await sha(JSON.stringify(body));
    const applied=await sql`SELECT aproar_web_apply(${body.version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb) AS result`;
    return json({ok:true,version:applied[0].result.version});
   }
   // Cadastro enxuto de unidade: não retransmite convocações e apontamentos.
   if(path==='/api/unit-register'&&request.method==='POST'){
    if(session.role!=='CONTROLADORIA')return json({error:'Somente a Controladoria pode cadastrar unidades.'},403);
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);
    if(!writes(env))return json({error:'Gravação não autorizada neste ambiente.'},403);
    const body=await bodyJSON(request);
    if(!body||typeof body!=='object'||Array.isArray(body)
       ||typeof body.name!=='string'||typeof body.version!=='string'
       ||!/^[a-f0-9-]{36}$/i.test(body.requestId||''))
      return json({error:'Dados do cadastro de unidade inválidos.'},400);
    const name=body.name.trim().replace(/\s+/g,' ').toUpperCase();
    if(!name||name.length>200||/[<>]/.test(name))
      return json({error:'Informe um nome de unidade válido, com até 200 caracteres.'},400);
    const digest=await sha(JSON.stringify(body));
    const previous=await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${body.requestId}`;
    if(previous.length){
      if(previous[0].actor!==session.user||previous[0].payload_hash!==digest)
        return json({error:'Identificador de requisição reutilizado.'},409);
      return json({ok:true,requestId:body.requestId,replayed:true});
    }
    const result=await applyCatalogRegistration(sql,body.requestId,session.user,digest,async()=>{
     const [settings,works]=await Promise.all([
       sql`SELECT data FROM aproar_web_settings WHERE id=1`,
       sql`SELECT DISTINCT unidade FROM obras`
     ]);
     if(!settings.length)throw Object.assign(Error('Configuração de unidades indisponível no banco.'),{status:503});
     const config=settings[0]?.data||{};
     const configured=Array.isArray(config.units)?config.units:[];
     const normalize=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().trim();
     if([...configured,...works.map(x=>x.unidade)].some(u=>normalize(u)===normalize(name)))
       throw Object.assign(Error('Esta unidade já está cadastrada.'),{status:409});
     if(configured.length>=500)throw Object.assign(Error('Limite de unidades cadastradas atingido.'),{status:400});
     // Preserva todas as outras configurações; não reenvia apontamentos.
     return [
       {table:'aproar_web_settings',action:'update',id:'1',data:{data:{...config,units:[...configured,name]}}},
       {table:'auditoria',action:'insert',id:'audit:'+body.requestId,data:{
         entidade:'aproar-web',entidade_id:null,acao:'CADASTRAR_UNIDADE',usuario:session.user,
         ocorrido_em:new Date().toISOString(),contexto:{nome:name}
       }}
     ];
    });
    return json({ok:true,requestId:body.requestId,name,version:result.version});
   }
   // Cadastro específico de obra: evita enviar todas as equipes e apontamentos no POST.
   if(path==='/api/work-register'&&request.method==='POST'){
    if(session.role!=='CONTROLADORIA')return json({error:'Somente a Controladoria pode cadastrar obras.'},403);
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);
    if(!writes(env))return json({error:'Gravação não autorizada neste ambiente.'},403);
    const body=await bodyJSON(request);
    if(!body||typeof body!=='object'||Array.isArray(body)
      ||typeof body.name!=='string'||typeof body.unit!=='string'
      ||!/^[a-f0-9-]{36}$/i.test(body.requestId||''))
      return json({error:'Dados do cadastro de obra inválidos.'},400);
    const name=body.name.trim().replace(/\s+/g,' ');
    const unit=body.unit.trim().replace(/\s+/g,' ').toUpperCase();
    if(!name||name.length>220||/[<>]/.test(name)||!unit||unit.length>200||/[<>]/.test(unit))
      return json({error:'Informe obra e unidade válidas (até 220 e 200 caracteres).'},400);
    const digest=await sha(JSON.stringify(body));
    const key='work:'+body.requestId;
    const previous=await sql`SELECT actor,payload_hash,result FROM aproar_web_requests WHERE id=${body.requestId}`;
    if(previous.length){
      if(previous[0].actor!==session.user||previous[0].payload_hash!==digest)
        return json({error:'Identificador de requisição reutilizado.'},409);
      return json({ok:true,requestId:body.requestId,replayed:true,
        obraId:previous[0].result?.ids?.[key],version:previous[0].result?.version});
    }
    const result=await applyCatalogRegistration(sql,body.requestId,session.user,digest,async()=>{
      const [matches,settings,units]=await Promise.all([
        sql`SELECT id,unidade FROM obras WHERE upper(trim(nome))=upper(trim(${name})) LIMIT 1`,
        sql`SELECT data FROM aproar_web_settings WHERE id=1`,
        sql`SELECT DISTINCT unidade FROM obras`
      ]);
      if(matches.length)throw Object.assign(Error('Já existe uma obra ou serviço com esse nome na unidade '+matches[0].unidade+'.'),{status:409});
      const configured=Array.isArray(settings[0]?.data?.units)?settings[0].data.units:[];
      if(![...configured,...units.map(x=>x.unidade)].includes(unit))
        throw Object.assign(Error('Unidade não cadastrada. Cadastre a unidade antes da obra.'),{status:400});
      return [
        {table:'obras',action:'insert',id:key,data:{nome:name,unidade:unit,trello_unidade_manual:true}},
        {table:'auditoria',action:'insert',id:'audit:'+body.requestId,data:{
          entidade:'aproar-web',entidade_id:null,acao:'CADASTRAR_OBRA',usuario:session.user,
          ocorrido_em:new Date().toISOString(),contexto:{nome:name,unidade:unit}
        }}
      ];
    });
    return json({ok:true,requestId:body.requestId,obraId:result.ids?.[key],version:result.version});
   }
   // Remocao pontual e auditada de uma inclusao sem apontamento.
   // Nao retransmite equipes, nao remove o cadastro do colaborador e nao apaga historico.
   if(path==='/api/convocation-remove'&&request.method==='POST'){
    if(session.role!=='CONTROLADORIA')return json({error:'Somente a Controladoria pode remover uma inclusão de convocação.'},403);
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);
    if(!writes(env))return json({error:'Gravação não autorizada neste ambiente.'},403);
    const body=await bodyJSON(request);
    if(!body||typeof body!=='object'||Array.isArray(body)
       ||Object.keys(body).some(k=>!['requestId','convocacaoId','colaboradorId'].includes(k))
       ||!/^[a-f0-9-]{36}$/i.test(body.requestId||'')
       ||!/^[0-9]+$/.test(String(body.convocacaoId||''))
       ||!/^[0-9]+$/.test(String(body.colaboradorId||'')))
      return json({error:'Identificação da inclusão a remover inválida.'},400);
    const digest=await sha(JSON.stringify(body));
    const previous=await sql`SELECT actor,payload_hash,result FROM aproar_web_requests WHERE id=${body.requestId}`;
    if(previous.length){
      if(previous[0].actor!==session.user||previous[0].payload_hash!==digest)
        return json({error:'Identificador de requisição reutilizado.'},409);
      return json({ok:true,requestId:body.requestId,replayed:true});
    }
    await applyCatalogRegistration(sql,body.requestId,session.user,digest,async()=>{
      const rows=await sql`
        SELECT c.id::text AS id,c.colaborador_id::text AS colaborador_id,
               c.observacao,c.custos_separados,
               EXISTS(SELECT 1 FROM apontamentos a WHERE a.convocacao_id=c.id::text) AS has_point,
               EXISTS(SELECT 1 FROM servicos_apontamento s WHERE s.convocacao_id=c.id::text) AS has_services,
               EXISTS(SELECT 1 FROM conflitos_convocacao f WHERE f.convocacao_existente_id=c.id::text) AS has_conflict
        FROM convocacoes c WHERE c.id::text=${String(body.convocacaoId)} LIMIT 1`;
      const current=rows[0];
      if(!current)return Promise.reject(Object.assign(Error('Inclusão não encontrada. Atualize a página e confira a equipe.'),{status:409}));
      if(current.colaborador_id!==String(body.colaboradorId))
        throw Object.assign(Error('A inclusão selecionada não corresponde ao colaborador. Atualize a página.'),{status:409});
      const meta=metadata(current.observacao).meta;
      if(current.has_point||current.has_services||current.has_conflict||current.custos_separados===true||meta.apontado_em)
        throw Object.assign(Error('Este colaborador já possui apontamento ou histórico vinculado. A remoção automática foi bloqueada.'),{status:409});
      return [
        {table:'convocacoes',action:'delete',id:String(body.convocacaoId)},
        {table:'auditoria',action:'insert',id:'audit:'+body.requestId,data:{
          entidade:'convocacoes',entidade_id:String(body.convocacaoId),
          acao:'REMOVER_INCLUSAO_SEM_APONTAMENTO',usuario:session.user,
          ocorrido_em:new Date().toISOString(),
          contexto:{colaboradorId:String(body.colaboradorId),motivo:'Inclusão acidental corrigida na Controladoria'}
        }}
      ];
    });
    return json({ok:true,requestId:body.requestId});
   }
   if(path==='/api/save'&&request.method==='POST'){
    if(!sameOrigin(request))return json({error:'Origem não autorizada.'},403);if(!writes(env))return json({error:'Gravação desativada ou sem autorização específica para este ambiente.'},403);
    const compactAck=request.headers.get('x-aproar-save-ack')==='1';
    const body=await bodyJSON(request);if(!/^[a-f0-9-]{36}$/i.test(body.requestId||'')||typeof body.version!=='string')return json({error:'Identificador de requisição inválido.'},400);
    const digest=await sha(JSON.stringify(body)),previous=await sql`SELECT actor,payload_hash FROM aproar_web_requests WHERE id=${body.requestId}`;
    if(previous.length){if(previous[0].actor!==session.user||previous[0].payload_hash!==digest)return json({error:'Identificador de requisição reutilizado.'},409);return compactAck?json({ok:true,requestId:body.requestId,replayed:true}):json({...summary(await readDatabase(sql,readOptions),session,env),ok:true,replayed:true});}
    const db=await readDatabase(sql,readOptions);if(body.version!==db.version)return json({error:'Outro usuário atualizou os dados. Suas alterações não foram gravadas; recarregue e confira os registros.'},409);
    const operations=buildOperations(db,body.state,session);
    if(!permittedProductionDeletion(env,session,db,operations))return json({error:'A Controladoria pode excluir uma convocação sem apontamento por vez ou até 50 obras sem vínculos. Registros com histórico devem ser preservados.'},403);
    // Work deletions run after dependent records, never before them.
    operations.sort((a,b)=>(a.table==='obras'&&a.action==='delete'?1:0)-(b.table==='obras'&&b.action==='delete'?1:0));
    if(operations.length)await sql`SELECT aproar_web_apply(${body.version},${body.requestId},${session.user},${digest},${JSON.stringify(operations)}::jsonb)`;
    // No second full database read inside the POST for modern clients.
    // Old open tabs continue receiving the legacy response until they refresh.
    return compactAck?json({ok:true,requestId:body.requestId}):json({...summary(await readDatabase(sql,readOptions),session,env),ok:true});
   }
   return json({error:'Rota não encontrada.'},404);
  }
  if(request.method!=='GET'&&request.method!=='HEAD')return json({error:'Método não permitido.'},405);
  if(env.ASSETS){const response=await env.ASSETS.fetch(request);const headers=new Headers(response.headers);for(const [k,v] of Object.entries(common))headers.set(k,v);headers.set('content-security-policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");return new Response(response.body,{status:response.status,headers});}
  return json({message:'Interface ainda não publicada.'},404);
 }catch(e){
  if(path==='/api/login'){console.error('APROAR login failure',JSON.stringify({stage:loginStage,type:String(e?.name||'Error').slice(0,60),code:String(e?.code||'none').slice(0,60),status:Number(e?.status||0)}));if(e.status)return json({error:e.message,...(e.details?{details:e.details}:{})},e.status);return json({error:'Falha interna no login. Etapa: '+loginStage+'. Consulte o registro do Worker.'},502);}
  if(path.startsWith('/api/trello/')){
   console.error('APROAR Trello route failure', JSON.stringify({
    route:path, type:String(e?.name||'Error').slice(0,80),
    code:String(e?.code||'none').slice(0,80),
    detail:String(e?.message||'No error message').slice(0,320)
   }));
  }
  if(path==='/api/save')console.error('APROAR save rejected',JSON.stringify({
   code:String(e?.code||'unknown').slice(0,32),
   name:String(e?.name||'Error').slice(0,60),
   reason:String(e?.message||'').slice(0,320),
   actorRole:session?.role||'unknown',
   route:path
  }));
  if(e.status)return json({error:e.message,...(e.details?{details:e.details}:{})},e.status);
  const message=String(e.message||'');
  if(message.includes('APROAR_CONFLITO_TURNO'))return json({error:'Há outra convocação no mesmo turno para um dos colaboradores. Confira a data antes de regularizar o apontamento.'},409);
  if(e.code==='57014'||e.code==='55P03')return json({error:'O banco está ocupado ou excedeu o tempo permitido. Confira o histórico antes de tentar novamente.'},503);if(message.includes('APROAR_STALE'))return json({error:'Os dados mudaram durante a gravação. Nenhuma alteração foi salva. Atualize e tente novamente.'},409);
  if(message.includes('APROAR_REQUEST_MISMATCH'))return json({error:'Requisição repetida com conteúdo diferente.'},409);
  if(e.code==='23505')return json({error:'Já existe um registro equivalente. Atualize os dados e confira antes de repetir.'},409);
  if(e.code==='23503')return json({error:'Este registro está vinculado ao histórico e não pode ser excluído.'},409);
  if(e.code==='42883'||e.code==='42P01')return json({error:'Estrutura do banco incompleta: confira a migração de banco correspondente ao ambiente.'},503);
  if(path==='/api/save'){
   const diagnosis=/^[0-9A-Z]{5}$/.test(String(e?.code||''))?String(e.code):'INDEFINIDO';
   return json({error:'O banco não confirmou o salvamento. Referência técnica DB-'+diagnosis+'. O formulário foi preservado: confira as pendências antes de tentar novamente.'},502);
  }
  return json({error:'Não foi possível concluir a operação. Confira a conexão e a estrutura do banco.'},502);
 }
},
 async scheduled(event,env,ctx){
  // A rotina depende de autorização explícita e de Cron Trigger configurado no ambiente.
  if(env.TRELLO_AUTO_SYNC_ENABLED!=='true'||!writes(env))return;
  ctx.waitUntil((async()=>{try{const sql=neon(env.DATABASE_URL);const r=await sql`SELECT sincronizado_obras_em,ultima_tentativa_obras_em FROM trello_snapshot WHERE snapshot_id=1`;const last=r[0]?.sincronizado_obras_em||r[0]?.ultima_tentativa_obras_em;
   if(last&&Date.now()-new Date(last).getTime()<11.5*60*60*1000)return;
   await sincronizarTrello(sql);
  }catch(e){console.error('Falha na sincronização Trello:',String(e?.message||e));}})());
 }
};
