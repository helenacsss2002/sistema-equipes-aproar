import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';

const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');

test('Erros de salvamento podem ser tratados sem falha adicional por sessao fora de escopo',()=>{
 assert.match(worker,/let loginStage='request',session=null;/);
 assert.match(worker,/session=await identity\(request,env\)/);
 assert.doesNotMatch(worker,/const session=await identity\(request,env\)/);
 assert.match(worker,/if\(path==='\/api\/save'\)console\.error\('APROAR save rejected'/);
});

test('Obras novas usam somente rota atomica e nao enviam convocacoes e apontamentos',()=>{
 assert.match(worker,/path==='\/api\/work-register'/);
 assert.match(worker,/session\.role!=='CONTROLADORIA'\)return json/);
 assert.match(worker,/table:'obras',action:'insert',id:key/);
 assert.match(worker,/actor!==session\.user\|\|previous\[0\]\.payload_hash!==digest/);
 assert.match(app,/workForm\.onsubmit=async e=>/);
 assert.match(app,/api\('\/api\/work-register'/);
 assert.match(app,/if\(workForm\.dataset\.editingObra\)return formSubmit\(e\)/);
 assert.match(app,/api\('\/api\/save-status\?requestId='/);
 assert.match(app,/const message=saved\s*\?'A obra foi SALVA no banco/);
});

test('Unidade e obra consultam versao atual no servidor e usam tentativa atomica controlada',()=>{
 assert.match(worker,/async function applyCatalogRegistration\(/);
 assert.match(worker,/current=await sql`SELECT aproar_web_fingerprint\(\) AS version`/);
 assert.match(worker,/includes\('APROAR_STALE'\)\|\|attempt===2/);
 assert.equal((worker.match(/await applyCatalogRegistration\(/g)||[]).length,2);
});

function driver(pg){
 return (parts,...args)=>{
  const sql=parts.reduce((text,part,i)=>text+(i?'$'+i:'')+part,'');
  return pg.query(sql,args).then(result=>result.rows);
 };
}

test('Cadastro atomico supera conflito de versao e repete requestId sem duplicar obra',async()=>{
 const begin=worker.indexOf('async function applyCatalogRegistration(');
 const end=worker.indexOf('function limit(request)',begin);
 assert(begin>=0&&end>begin);
 const ctx={};
 vm.createContext(ctx);
 vm.runInContext(worker.slice(begin,end)+'\nglobalThis.register=applyCatalogRegistration;',ctx);
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  const sql=driver(pg),id=webcrypto.randomUUID();
  const key='work:'+id,ops=[{table:'obras',action:'insert',id:key,data:{nome:'OBRA REGISTRO QA',unidade:'QA'}}];
  let attempts=0;
  const build=async()=>{
   attempts++;
   if(attempts===1)await pg.exec("INSERT INTO obras(nome,unidade) VALUES('OPERACAO CONCORRENTE','QA')");
   return ops;
  };
  const result=await ctx.register(sql,id,'CONTROLADORIA','hash-qa',build);
  assert.equal(attempts,2,'deve recalcular a versao apos alteracao concorrente');
  assert.match(result.ids[key],/^[0-9]+$/);
  await ctx.register(sql,id,'CONTROLADORIA','hash-qa',async()=>ops);
  const total=await pg.query("SELECT count(*)::int AS total FROM obras WHERE nome='OBRA REGISTRO QA'");
  assert.equal(total.rows[0].total,1,'a mesma requisicao jamais duplica o cadastro');
 }finally{await pg.close();}
});
