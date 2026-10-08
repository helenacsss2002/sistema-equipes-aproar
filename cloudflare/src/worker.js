import { neon } from '@neondatabase/serverless';
import { mapNeonData } from './neon-adapter.js';
import { validateConvocacao, validateApontamento, writeConfiguration, convocacaoAtrasada } from './write-validation.js';

const headers = { 'content-type':'application/json; charset=utf-8', 'cache-control':'no-store', 'x-content-type-options':'nosniff' };
const json = (value, status=200) => new Response(JSON.stringify(value), {status, headers});
async function equalSecret(a,b) {
  if (!a || !b) return false;
  const enc = new TextEncoder();
  const [left,right] = await Promise.all([a,b].map(s=>crypto.subtle.digest('SHA-256',enc.encode(s))));
  const x = new Uint8Array(left), y = new Uint8Array(right);
  let delta=0; for(let i=0;i<x.length;i++) delta |= x[i] ^ y[i];
  return delta === 0;
}
const bearer = request => request.headers.get('authorization')?.match(/^Bearer (.+)$/i)?.[1] ?? '';
async function bodyJson(request) {
  const text = await request.text();
  if (text.length > 4096) throw new Error('too-large');
  return JSON.parse(text);
}
const getSql = env => neon(env.DATABASE_URL);

// Every write is isolated behind three deliberate gates: token, enabled flag, exact Neon endpoint host.
async function writeRoute(request, env, route) {
  const cfg = writeConfiguration(env);
  if (!cfg.ok) return json({error:'Gravação de homologação desabilitada.',reason:cfg.reason},503);
  if (!await equalSecret(bearer(request), env.HOMOLOGATION_WRITE_TOKEN)) return json({error:'Não autorizado.'},401);
  if (request.method !== 'POST') return json({error:'Método não permitido.'},405);
  let payload; try {payload=await bodyJson(request);} catch {return json({error:'JSON inválido ou muito grande.'},400);}
  const sql=getSql(env);
  if (route === '/api/homologacao/convocacoes') {
    const validated = validateConvocacao(payload);
    if (!validated.ok) return json({error:validated.error},400);
    const {obraId,colaboradorId,dataServico,engenheiro,turno,observacao}=validated.value;
    const marker=' ||APROAR_META|| ';
    const nota=`Turno: ${turno} | ${observacao}${marker}${JSON.stringify({convocado_em:new Date().toISOString(),convocado_por:'HOMOLOGACAO_CLOUDFLARE',convocacao_atrasada:convocacaoAtrasada(dataServico)})}`;
    try {
      // Advisory lock serializes requests for a collaborator on a date; separate morning/afternoon are valid.
      const output=await sql.transaction([
        sql`SELECT pg_advisory_xact_lock(hashtext(${`aproar-conv-${colaboradorId}-${dataServico}`}))`,
        sql`WITH inserted AS (
          INSERT INTO convocacoes (obra_id,colaborador_id,data,engenheiro,turno,observacao,criado_em,criado_por)
          SELECT o.id,c.id,${dataServico}::date,${engenheiro},${turno},${nota},NOW(),'HOMOLOGACAO_CLOUDFLARE'
          FROM obras o JOIN colaboradores c ON c.id=${colaboradorId}::bigint
          WHERE o.id=${obraId}::bigint
            AND c.ativo IS DISTINCT FROM FALSE
            AND NOT EXISTS (
              SELECT 1 FROM indisponibilidades d WHERE d.colaborador_id::text=c.id::text
                AND d.ativo=TRUE AND ${dataServico}::date BETWEEN d.inicio AND d.fim
            )
            AND NOT EXISTS (
              SELECT 1 FROM convocacoes prev WHERE prev.colaborador_id=c.id AND prev.data=${dataServico}::date
                AND (COALESCE(NULLIF(prev.turno,''),
                     (regexp_match(prev.observacao,'Turno:\\s*(Integral|Manhã|Tarde|Noite)','i'))[1],
                     'Integral')='Integral'
                  OR ${turno}='Integral'
                  OR COALESCE(NULLIF(prev.turno,''),
                     (regexp_match(prev.observacao,'Turno:\\s*(Integral|Manhã|Tarde|Noite)','i'))[1],
                     'Integral')=${turno})
            ) RETURNING id,obra_id,colaborador_id,data,engenheiro,turno
        ), audited AS (
          INSERT INTO auditoria (entidade,entidade_id,acao,usuario,depois,contexto)
          SELECT 'convocacao',id::text,'CRIAR','HOMOLOGACAO_CLOUDFLARE',
            jsonb_build_object('obra_id',obra_id,'colaborador_id',colaborador_id,'data',data,'turno',turno,'engenheiro',engenheiro),
            '{"origem":"cloudflare-homologacao"}'::jsonb
          FROM inserted RETURNING id
        )
        SELECT id::text AS id,(SELECT COUNT(*) FROM audited)::int AS auditorias FROM inserted`
      ],{isolationLevel:'ReadCommitted'});
      const inserted=output[1] ?? [];
      if (!inserted.length) return json({error:'Colaborador ou obra inexistente, indisponibilidade ou conflito de turno. Nenhuma convocação criada.'},409);
      return json({created:true,id:inserted[0].id},201);
    } catch {return json({error:'A gravação falhou; verifique as restrições do banco de homologação.'},502);}
  }
  if (route === '/api/homologacao/apontamentos') {
    const validated = validateApontamento(payload);
    if (!validated.ok) return json({error:validated.error},400);
    const {convocacaoId,status,observacao,periodo}=validated.value;
    try {
      const output=await sql.transaction([
        sql`SELECT pg_advisory_xact_lock(hashtext(${`aproar-apont-${convocacaoId}`}))`,
        sql`WITH origin AS (
          SELECT c.id,c.data,c.obra_id,c.colaborador_id,c.engenheiro,c.turno,o.nome,o.unidade
          FROM convocacoes c JOIN obras o ON o.id=c.obra_id
          WHERE c.id=${convocacaoId}::bigint
            AND c.custos_separados=FALSE
            AND c.status='Presente (Integral)'
            AND position('\"apontado_em\"' in c.observacao)=0
        ), inserted AS (
          INSERT INTO apontamentos
            (convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_extra,observacao,
             apontado_em,apontado_por,retroativo,atualizado_em,custos_separados)
          SELECT origin.id::text,origin.data,origin.colaborador_id::text,origin.engenheiro,
            ${status},0,${observacao},NOW(),'HOMOLOGACAO_CLOUDFLARE',
            CASE WHEN EXTRACT(ISODOW FROM origin.data) IN (6,7) THEN FALSE
                 WHEN (NOW() AT TIME ZONE 'America/Fortaleza')::date <= origin.data THEN FALSE
                 WHEN (NOW() AT TIME ZONE 'America/Fortaleza')::date > origin.data +
                      (CASE WHEN EXTRACT(ISODOW FROM origin.data)=5 THEN 3 ELSE 1 END) THEN TRUE
                 ELSE (NOW() AT TIME ZONE 'America/Fortaleza')::time >= TIME '09:30'
            END,NOW(),TRUE
          FROM origin WHERE NOT EXISTS (
            SELECT 1 FROM apontamentos a WHERE a.convocacao_id=origin.id::text
          ) RETURNING id,convocacao_id,retroativo
        ), mirrored AS (
          UPDATE convocacoes c SET status=${status},custos_separados=TRUE
          FROM inserted i WHERE c.id::text=i.convocacao_id RETURNING c.id
        ), services AS (
          INSERT INTO servicos_apontamento
            (convocacao_id,obra_id,obra_nome_snapshot,unidade_snapshot,periodo,principal)
          SELECT i.convocacao_id,o.obra_id::text,o.nome,o.unidade,
                 COALESCE(${periodo},NULLIF(o.turno,''),'Integral'),TRUE
          FROM origin o JOIN inserted i ON i.convocacao_id=o.id::text RETURNING id
        ), audited AS (
          INSERT INTO auditoria (entidade,entidade_id,acao,usuario,depois,contexto)
          SELECT 'apontamento',i.convocacao_id,'SALVAR','HOMOLOGACAO_CLOUDFLARE',
                 jsonb_build_object('status',${status},'retroativo',i.retroativo),
                 '{"origem":"cloudflare-homologacao"}'::jsonb
          FROM inserted i RETURNING id
        )
        SELECT id::text AS id,retroativo,
               (SELECT COUNT(*) FROM mirrored)::int AS espelhos,
               (SELECT COUNT(*) FROM services)::int AS servicos,
               (SELECT COUNT(*) FROM audited)::int AS auditorias
        FROM inserted`
      ],{isolationLevel:'ReadCommitted'});
      const inserted=output[1] ?? [];
      if (!inserted.length) return json({error:'Convocação inexistente ou já apontada. Nenhum apontamento criado.'},409);
      return json({created:true,id:inserted[0].id,retroativo:inserted[0].retroativo},201);
    } catch {return json({error:'A gravação falhou; verifique as restrições do banco de homologação.'},502);}
  }
  return json({error:'Rota não encontrada.'},404);
}

export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    if (url.pathname==='/api/health' && request.method==='GET') return json({application:'APROAR',stage:'homologation-write-prototype',databaseConfigured:Boolean(env.DATABASE_URL),writesEnabled:writeConfiguration(env).ok});
    const writePath=['/api/homologacao/convocacoes','/api/homologacao/apontamentos'].includes(url.pathname);
    if (writePath) return writeRoute(request,env,url.pathname);
    if (!['/api/check-database','/api/preview-data'].includes(url.pathname)) return json({message:'APROAR: API de homologação. Interface ainda não publicada.'},404);
    if (request.method!=='POST') return json({error:'Método não permitido.'},405);
    if (!env.DATABASE_URL || !env.CONNECTION_CHECK_TOKEN) return json({error:'Configure DATABASE_URL e CONNECTION_CHECK_TOKEN.'},503);
    if (!await equalSecret(bearer(request),env.CONNECTION_CHECK_TOKEN)) return json({error:'Acesso não autorizado.'},401);
    try {
      const sql=getSql(env);
      if (url.pathname==='/api/preview-data') {
        const tables=['colaboradores','obras','convocacoes','apontamentos','servicos_apontamento','indisponibilidades','conflitos_convocacao','auditoria'];
        const results=await sql.transaction([
          sql`SELECT * FROM colaboradores`,sql`SELECT * FROM obras`,sql`SELECT * FROM convocacoes`,
          sql`SELECT * FROM apontamentos`,sql`SELECT * FROM servicos_apontamento`,sql`SELECT * FROM indisponibilidades`,
          sql`SELECT * FROM conflitos_convocacao`,sql`SELECT * FROM auditoria`
        ],{isolationLevel:'RepeatableRead',readOnly:true});
        return json({stage:'read-only-preview',writesEnabled:writeConfiguration(env).ok,data:mapNeonData(Object.fromEntries(tables.map((t,i)=>[t,results[i]])))});
      }
      const columns=await sql`SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('colaboradores','obras','convocacoes','apontamentos','servicos_apontamento')`;
      const expected={colaboradores:['id','nome','funcao','valor_diaria','ativo'],obras:['id','nome','unidade'],convocacoes:['id','obra_id','colaborador_id','data','engenheiro','turno'],apontamentos:['convocacao_id','data_servico','status','custo_pago','valor_extra','valor_acordo','valor_adicional_noturno'],servicos_apontamento:['convocacao_id','obra_id','periodo','principal']};
      const missing=[];for(const [table,fields] of Object.entries(expected))for(const field of fields)if(!columns.some(c=>c.table_name===table&&c.column_name===field))missing.push(table+'.'+field);
      return json({connected:true,schemaCompatible:missing.length===0,missingColumns:missing,writesEnabled:writeConfiguration(env).ok});
    } catch {return json({connected:false,error:'Falha na conexão. Confira a configuração e disponibilidade do Neon.'},502);}
  }
};
