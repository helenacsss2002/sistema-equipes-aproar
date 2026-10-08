import { mapNeonData } from './neon-adapter.js';
export const supervisors=['EDUARDO','FELIPE','GABRIEL','JOEL','NETO','SOARES','VICTOR'];
export async function readDatabase(sql){
 const names=['colaboradores','obras','convocacoes','apontamentos','servicos_apontamento','indisponibilidades','conflitos_convocacao','auditoria','engenheiros_teams','cobrancas_teams','settings','version'];
 const result=await sql.transaction([sql`SELECT * FROM colaboradores ORDER BY id`,sql`SELECT * FROM obras ORDER BY id`,sql`SELECT * FROM convocacoes ORDER BY id`,sql`SELECT * FROM apontamentos ORDER BY id`,sql`SELECT * FROM servicos_apontamento ORDER BY id`,sql`SELECT * FROM indisponibilidades ORDER BY id`,sql`SELECT * FROM conflitos_convocacao ORDER BY id`,sql`SELECT * FROM auditoria ORDER BY id`,sql`SELECT * FROM engenheiros_teams ORDER BY engenheiro`,sql`SELECT * FROM cobrancas_teams ORDER BY id`,sql`SELECT data FROM aproar_web_settings WHERE id=1`,sql`SELECT aproar_web_fingerprint() AS version`],{isolationLevel:'RepeatableRead',readOnly:true});
 const raw=Object.fromEntries(names.map((n,i)=>[n,result[i]])),state=mapNeonData(raw);const config=raw.settings[0]?.data||{};
 Object.assign(state,{unitOwners:config.unitOwners||{},teamsAutomation:config.teamsAutomation||false,teamsMessage:config.teamsMessage||'',teamsHistory:[...(raw.cobrancas_teams||[]).map(x=>({id:String(x.id),data:x.enviado_em,supervisor:x.engenheiro,quantidade:x.qtd_pendentes,status:x.status,detalhe:x.mensagem})),...(config.teamsHistory||[])]});
 state.teamsConfig=Object.fromEntries(raw.engenheiros_teams.map(x=>[x.engenheiro,{email:x.email_teams||'',ativo:x.ativo}]));
 return {raw,state,version:raw.version[0].version};
}
export function visibleState(db,session){const state=structuredClone(db.state);if(session.role==='SUPERVISOR'){state.apontamentos=state.apontamentos.filter(a=>a.supervisor===session.user);state.auditoria=state.auditoria.filter(a=>a.usuario===session.user);state.teamsConfig={};state.teamsHistory=[];state.teamsMessage='';}return state;}
