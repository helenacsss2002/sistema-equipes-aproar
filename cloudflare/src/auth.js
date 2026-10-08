const encode=v=>btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(v)))).replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');
const decode=v=>JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(v.replaceAll('-','+').replaceAll('_','/')),c=>c.charCodeAt(0))));
const secretKey=env=>env.SESSION_SECRET||env.CONNECTION_CHECK_TOKEN;
const key=async env=>crypto.subtle.importKey('raw',new TextEncoder().encode(secretKey(env)),{name:'HMAC',hash:'SHA-256'},false,['sign','verify']);
export async function equalSecret(a,b){if(!a||!b)return false;const hash=v=>crypto.subtle.digest('SHA-256',new TextEncoder().encode(v));const [x,y]=await Promise.all([hash(a),hash(b)]);const aa=new Uint8Array(x),bb=new Uint8Array(y);let diff=0;for(let i=0;i<aa.length;i++)diff|=aa[i]^bb[i];return diff===0;}
export async function login(body,env){if(!secretKey(env))throw Object.assign(Error('Configure CONNECTION_CHECK_TOKEN ou SESSION_SECRET.'),{status:503});const role=body.role;let pass,user=role;
 if(role==='CONTROLADORIA')pass=env.ADMIN_PASSWORD;
 else if(role==='FINANCEIRO')pass=env.FINANCE_PASSWORD;
 else if(role==='VISUALIZAR')pass=env.VIEWER_PASSWORD;
 else if(role==='SUPERVISOR'){user=String(body.supervisor||'').trim().toUpperCase();if(!['EDUARDO','FELIPE','GABRIEL','JOEL','NETO','SOARES','VICTOR'].includes(user))throw Object.assign(Error('Selecione um supervisor válido.'),{status:401});}
 
if(role==='CONTROLADORIA'||role==='FINANCEIRO'){
  if(typeof pass!=='string'||!pass.length)
    throw Object.assign(
      Error('Senha administrativa não configurada.'),
      {status:503}
    );

  if(!await equalSecret(String(body.password||''),pass))
    throw Object.assign(
      Error('Acesso ou senha inválidos.'),
      {status:401}
    );
}

 const payload=encode({role,user,exp:Math.floor(Date.now()/1000)+8*3600}),signature=new Uint8Array(await crypto.subtle.sign('HMAC',await key(env),new TextEncoder().encode(payload)));
 return {session:{role,user},cookie:`aproar_session=${payload}.${encode([...signature])}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800`};
}
export async function identity(request,env){try{if(!secretKey(env))return null;const token=request.headers.get('cookie')?.match(/(?:^|;\s*)aproar_session=([^;]+)/)?.[1],parts=token?.split('.');if(parts?.length!==2)return null;const verified=await crypto.subtle.verify('HMAC',await key(env),new Uint8Array(decode(parts[1])),new TextEncoder().encode(parts[0]));if(!verified)return null;const p=decode(parts[0]);if(p.exp<=Date.now()/1000||!['CONTROLADORIA','FINANCEIRO','SUPERVISOR','VISUALIZAR'].includes(p.role))return null;return p;}catch{return null;}}
export function sameOrigin(request){return request.headers.get('origin')===new URL(request.url).origin;}
export const logoutCookie='aproar_session=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0';
