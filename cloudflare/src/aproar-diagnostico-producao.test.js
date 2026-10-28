import test from 'node:test';
import assert from 'node:assert/strict';

const base='https://sistema-equipes-aproar.helenacsss2002.workers.dev';
test('Diagnostico remoto emergencial do APROAR publicado',async t=>{
 const rows=[];
 for(const path of ['/api/health','/','/app.js','/api/bootstrap']){
   const url=base+path;
   try{
     const started=Date.now();
     const r=await fetch(url,{signal:AbortSignal.timeout(16000),headers:{'cache-control':'no-cache'}});
     const body=await r.text();
     const row={path,status:r.status,ms:Date.now()-started,contentType:r.headers.get('content-type'),bytes:body.length,head:body.slice(0,280)};
     rows.push(row);
     t.diagnostic(JSON.stringify(row));
   }catch(error){
     const row={path,error:String(error?.message||error),cause:String(error?.cause||'')};
     rows.push(row);
     t.diagnostic(JSON.stringify(row));
   }
 }
 const health=rows.find(x=>x.path==='/api/health');
 assert.equal(health?.status,200,'Worker não responde corretamente em /api/health');
 const home=rows.find(x=>x.path==='/');
 assert.equal(home?.status,200,'Página inicial do sistema não retorna HTTP 200');
 assert.match(home.head,/<!doctype html/i,'O sistema não está servindo HTML válido');
 const js=rows.find(x=>x.path==='/app.js');
 assert.equal(js?.status,200,'O script do aplicativo não está sendo servido');
 const bootstrap=rows.find(x=>x.path==='/api/bootstrap');
 assert.equal(bootstrap?.status,401,'Rota privada deve continuar protegida por login');
});
