// Evita apresentar "senha inválida" ou "estrutura do banco" quando o Neon
// suspende o compute por limite do plano. Não revela credenciais, detalhes SQL
// nem permite escrita offline.
export const neonQuotaExceeded=error=>{
  const message=String(error?.message||'');
  const details=String(error?.detail||'');
  return /\bexceeded\s+(?:the\s+)?(?:[\w\s]+\s)?quota\b|\bexceeded\s+(?:the\s+)?(?:[\w\s]+\s)?limit\b|\bHTTP\s+status\s+402\b|\bdata\s+transfer\s+quota\b/i.test(message+' '+details)
    && /\bquota\b|\bneon\b|\bproject\b|\baccount\b|\bHTTP\s+status\s+402\b/i.test(message+' '+details);
};
export const neonQuotaPublicMessage='O banco Neon atingiu o limite de uso do plano e suspendeu as conexões. Não é um erro de senha. O responsável pela conta Neon precisa regularizar a cota ou aguardar a renovação do período. Seus registros existentes não devem ser reenviados enquanto o banco estiver indisponível.';
