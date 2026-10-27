// Nome de unidade deve ser uma designacao curta, nunca uma URL
// ou campo de observacao de card vindo de integracao externa.
export function isSafeUnitName(value){
 return typeof value==='string'
   && value.trim().length>0
   && value.trim().length<=80
   && !/(?:https?:\/\/|www\.|sharepoint|link\s+para\s+acesso)/i.test(value);
}
