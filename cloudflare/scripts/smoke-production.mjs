// Verificação após o deploy. Nenhuma senha, cookie ou gravação é utilizada.
// O GitHub Action falha se o worker responder HTML no lugar de JSON.
const origin=process.env.APROAR_SMOKE_ORIGIN||'https://sistema-equipes-aproar.helenacsss2002.workers.dev';
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));

async function probe(path,expected,check){
 let message='';
 for(let attempt=0;attempt<5;attempt++){
  try{
   const response=await fetch(origin+path,{
    method:'GET',
    headers:{'Accept':'application/json, text/html'},
    redirect:'manual',
    signal:AbortSignal.timeout(15000)
   });
   const contentType=response.headers.get('content-type')||'';
   const body=await response.text();
   if(response.status!==expected)throw Error('HTTP '+response.status+' em vez de '+expected);
   check(body,contentType);
   console.log('OK '+path+' HTTP '+response.status);
   return;
  }catch(err){
   message=String(err?.message||err);
   console.warn('Tentativa '+(attempt+1)+' falhou em '+path+': '+message.slice(0,150));
   if(attempt<4)await pause(1200*(attempt+1));
  }
 }
 throw Error('APROAR indisponível em '+path+': '+message);
}
const ensureJSON=(str,type)=>{
 if(!type.includes('application/json'))throw Error('Servidor respondeu tipo de conteúdo inválido: '+type);
 try{return JSON.parse(str);}catch{throw Error('JSON incompleto/inválido');}
};
await probe('/api/health',200,(body,type)=>{
 const x=ensureJSON(body,type);
 if(x.application!=='APROAR')throw Error('Resposta de outro aplicativo');
 if(!x.databaseConfigured)throw Error('DATABASE_URL ausente no Worker publicado');
});
await probe('/api/bootstrap',401,(body,type)=>{
 const x=ensureJSON(body,type);
 if(!x.error)throw Error('Bootstrap sem cookie deveria exigir login e retornar JSON');
});
await probe('/?i=1',200,(body,type)=>{
 if(!type.includes('text/html')||!body.includes('APROAR')||!body.includes('app.js?v='))
  throw Error('Interface da produção está ausente ou incompleta');
});
await probe('/app.js',200,(body,type)=>{
 if(!body.includes('async function restoreOnlineSession()')||!body.includes('APROAR read retry'))
  throw Error('JavaScript novo ainda não foi publicado');
});
console.log('APROAR smoke de produção: API JSON, sessão, HTML e JavaScript verificados.');
