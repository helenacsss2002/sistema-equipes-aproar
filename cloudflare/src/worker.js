import { neon } from '@neondatabase/serverless';
import { mapNeonData } from './neon-adapter.js';
const headers = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' };
const json = (data, status = 200) => new Response(JSON.stringify(data), { status, headers });
async function equalSecret(a,b) {
  if (!a || !b) return false;
  const enc=new TextEncoder(),hash=x=>crypto.subtle.digest('SHA-256',enc.encode(x));
  const [x,y]=await Promise.all([hash(a),hash(b)]);const aa=new Uint8Array(x),bb=new Uint8Array(y);let diff=0;for(let i=0;i<aa.length;i++)diff|=aa[i]^bb[i];return diff===0;
}
export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    if(url.pathname==='/api/health'&&request.method==='GET')return json({application:'APROAR',stage:'connection-check',databaseConfigured:Boolean(env.DATABASE_URL),writesEnabled:false});
    if(!['/api/check-database','/api/preview-data'].includes(url.pathname))return json({message:'Integração APROAR em preparação. Esta versão somente verifica a conexão; ainda não disponibiliza a plataforma.'},404);
    if(request.method!=='POST')return json({error:'Método não permitido.'},405);
    if(!env.DATABASE_URL||!env.CONNECTION_CHECK_TOKEN)return json({error:'Configure DATABASE_URL e CONNECTION_CHECK_TOKEN nos segredos do Worker.'},503);
    if(!await equalSecret(request.headers.get('authorization')?.replace(/^Bearer /,''),env.CONNECTION_CHECK_TOKEN))return json({error:'Acesso não autorizado.'},401);
    try {
      const sql=neon(env.DATABASE_URL);
      if(url.pathname==='/api/preview-data'){
        const tables=['colaboradores','obras','convocacoes','apontamentos','servicos_apontamento','indisponibilidades','conflitos_convocacao','auditoria'];
        // One consistent, read-only snapshot. The caller cannot choose SQL or table names.
        const results=await sql.transaction([sql`SELECT * FROM colaboradores`,sql`SELECT * FROM obras`,sql`SELECT * FROM convocacoes`,sql`SELECT * FROM apontamentos`,sql`SELECT * FROM servicos_apontamento`,sql`SELECT * FROM indisponibilidades`,sql`SELECT * FROM conflitos_convocacao`,sql`SELECT * FROM auditoria`],{isolationLevel:'RepeatableRead',readOnly:true});
        return json({stage:'read-only-preview',writesEnabled:false,data:mapNeonData(Object.fromEntries(tables.map((t,i)=>[t,results[i]])))});
      }
      const columns=await sql`SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('colaboradores','obras','convocacoes','apontamentos','servicos_apontamento')`;
      const expected={colaboradores:['id','nome','funcao','valor_diaria','ativo'],obras:['id','nome','unidade'],convocacoes:['id','obra_id','colaborador_id','data','engenheiro','turno'],apontamentos:['convocacao_id','data_servico','status','custo_pago','valor_extra','valor_acordo','valor_adicional_noturno'],servicos_apontamento:['convocacao_id','obra_id','periodo','principal']};
      const missing=[];for(const [table,fields] of Object.entries(expected))for(const field of fields)if(!columns.some(c=>c.table_name===table&&c.column_name===field))missing.push(table+'.'+field);
      return json({connected:true,schemaCompatible:missing.length===0,missingColumns:missing,writesEnabled:false});
    }catch{return json({connected:false,error:'Falha na conexão. Confira o segredo DATABASE_URL e a disponibilidade do Neon.'},502);}
  }
};
