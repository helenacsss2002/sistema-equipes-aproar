// APROAR homologacao: pure input validation, no database access.
export const TURNOS = Object.freeze(['Integral', 'Manhã', 'Tarde', 'Noite']);
export const STATUS = Object.freeze([
  'Presente (Integral)', 'Presente (Só Manhã)', 'Presente (Só Tarde)',
  'Saída Antecipada', 'Falta', 'Atestado'
]);
const positiveId = x => typeof x === 'string' || typeof x === 'number'
  ? /^(?:[1-9][0-9]{0,17})$/.test(String(x)) : false;
const cleanText = (x, limit) => typeof x === 'string' && x.length <= limit && !/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/.test(x)
  ? x.trim() : null;
export function isoDay(date) {
  if (typeof date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(date)) return false;
  const d = new Date(`${date}T00:00:00.000Z`);
  return Number.isFinite(d.valueOf()) && d.toISOString().slice(0, 10) === date;
}
export function turnosSeSobrepoem(a, b) {
  return a === 'Integral' || b === 'Integral' || a === b;
}
export function validateConvocacao(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return { ok:false, error:'Payload inválido.' };
  if (Object.keys(input).some(k => !['obraId','colaboradorId','dataServico','engenheiro','turno','observacao'].includes(k))) return { ok:false, error:'Campos não suportados na convocação.' };
  const obraId = String(input.obraId ?? '');
  const colaboradorId = String(input.colaboradorId ?? '');
  const engenheiro = cleanText(input.engenheiro, 100);
  const observacao = input.observacao == null ? '' : cleanText(input.observacao, 500);
  if (!positiveId(obraId) || !positiveId(colaboradorId)) return { ok:false, error:'ID da obra ou do colaborador inválido.' };
  if (!isoDay(input.dataServico)) return { ok:false, error:'Data de serviço inválida.' };
  if (!engenheiro) return { ok:false, error:'Supervisor inválido.' };
  if (!TURNOS.includes(input.turno)) return { ok:false, error:'Turno inválido.' };
  if (observacao === null || observacao.includes(' ||APROAR_META|| ')) return { ok:false, error:'Observação inválida ou com marcador reservado.' };
  return { ok:true, value: {obraId, colaboradorId, dataServico:input.dataServico, engenheiro, turno:input.turno, observacao} };
}
export function validateApontamento(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return { ok:false, error:'Payload inválido.' };
  if (Object.keys(input).some(k => !['convocacaoId','status','observacao','periodo'].includes(k))) return { ok:false, error:'Campos não suportados no apontamento.' };
  const convocacaoId = String(input.convocacaoId ?? '');
  const observacao = input.observacao == null ? '' : cleanText(input.observacao, 500);
  if (!positiveId(convocacaoId)) return { ok:false, error:'ID da convocação inválido.' };
  if (!STATUS.includes(input.status)) return { ok:false, error:'Status inválido.' };
  if (observacao === null) return { ok:false, error:'Observação inválida.' };
  if (input.periodo !== undefined && !TURNOS.includes(input.periodo)) return { ok:false, error:'Período inválido.' };
  if (input.servicos !== undefined || input.valoresFinanceiros !== undefined || input.valorExtra !== undefined)
    return { ok:false, error:'Serviços adicionais e valores financeiros ainda não são suportados nesta etapa.' };
  return { ok:true, value: {convocacaoId, status:input.status, observacao, periodo:input.periodo ?? null} };
}

export function convocacaoAtrasada(dataServico, agora = new Date()) {
  if (!isoDay(dataServico)) return false;
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone:'America/Fortaleza',year:'numeric',month:'2-digit',day:'2-digit',
    hour:'2-digit',minute:'2-digit',hourCycle:'h23'
  }).formatToParts(agora).filter(p=>p.type!=='literal').map(p=>[p.type,p.value]));
  const localDay=`${parts.year}-${parts.month}-${parts.day}`;
  const day=new Date(`${localDay}T00:00:00Z`);
  const weekday=day.getUTCDay();
  const serviceWeekday=new Date(`${dataServico}T00:00:00Z`).getUTCDay();
  if (weekday===0 || weekday===6 || serviceWeekday===0 || serviceWeekday===6) return false;
  if (`${parts.hour}:${parts.minute}`<'16:00') return false;
  day.setUTCDate(day.getUTCDate()+(weekday===5?3:1));
  return day.toISOString().slice(0,10)===dataServico;
}

// Same weekend / Monday 09:30 rule as app.py; timezone is ALWAYS Fortaleza.
export function apontamentoRetroativo(dataServico, agora = new Date()) {
  if (!isoDay(dataServico)) return false;
  const service = new Date(`${dataServico}T00:00:00Z`);
  const weekday = service.getUTCDay();
  if (weekday === 0 || weekday === 6) return false;
  const limit = new Date(service);
  limit.setUTCDate(limit.getUTCDate() + (weekday === 5 ? 3 : 1));
  const deadlineDay = limit.toISOString().slice(0, 10);
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone:'America/Fortaleza', year:'numeric',month:'2-digit',day:'2-digit',
    hour:'2-digit',minute:'2-digit',hourCycle:'h23'
  }).formatToParts(agora).filter(p => p.type !== 'literal').map(p => [p.type,p.value]));
  const localDay = `${parts.year}-${parts.month}-${parts.day}`;
  if (localDay < deadlineDay) return false;
  if (localDay > deadlineDay) return true;
  return `${parts.hour}:${parts.minute}` >= '09:30';
}
export function writeConfiguration(env) {
  if (env?.ENABLE_HOMOLOGATION_WRITES !== 'true') return { ok:false, reason:'disabled' };
  if (!env.HOMOLOGATION_WRITE_TOKEN || String(env.HOMOLOGATION_WRITE_TOKEN).length < 32)
    return { ok:false, reason:'write-token-missing' };
  if (!env.HOMOLOGATION_EXPECTED_HOST || !env.DATABASE_URL)
    return { ok:false, reason:'expected-host-missing' };
  try {
    const url = new URL(env.DATABASE_URL);
    if (!['postgresql:', 'postgres:'].includes(url.protocol) ||
        url.hostname.toLowerCase() !== env.HOMOLOGATION_EXPECTED_HOST.toLowerCase() ||
        !/^ep-[a-z0-9-]+\./.test(url.hostname)) return { ok:false, reason:'database-host-mismatch' };
  } catch {return { ok:false, reason:'invalid-database-url' };}
  return { ok:true };
}
