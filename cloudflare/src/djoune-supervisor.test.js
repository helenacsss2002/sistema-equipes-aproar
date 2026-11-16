import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {PGlite} from '@electric-sql/pglite';
import {login,identity} from './auth.js';
import {readDatabase,visibleState} from './data.js';
import {buildOperations} from './operations.js';

const supervisor='DJOUNE XAVIER';
const env={SESSION_SECRET:'test-only-djoune-session-signing-secret',DJOUNE_XAVIER_PASSWORD:'test-only-djoune-password'};
const now='2026-11-16T12:00:00Z';
const serviceDate='2026-11-16';
const eduardo={role:'SUPERVISOR',user:'EDUARDO'};
const finance={role:'FINANCEIRO',user:'FINANCEIRO'};
const status=(code)=>error=>error.status===code;

test('Djoune authenticates only with his Cloudflare secret and receives a signed supervisor session',async()=>{
 let sqlCalls=0;
 const sql=async()=>{sqlCalls++;throw Error('Djoune must not use bcrypt fallback');};
 const result=await login({role:'SUPERVISOR',supervisor:' djoune xavier ',password:env.DJOUNE_XAVIER_PASSWORD},env,sql);
 assert.deepEqual(result.session,{role:'SUPERVISOR',user:supervisor});
 assert.match(result.cookie,/HttpOnly; Secure; SameSite=Strict/);
 const cookie=result.cookie.split(';')[0];
 const claims=await identity(new Request('https://aproar.test/api/bootstrap',{headers:{cookie}}),env);
 assert.equal(claims.user,supervisor);
 assert.equal(claims.role,'SUPERVISOR');
 assert.equal(claims.supervisorPasswordAuth,true);
 assert(claims.exp>Date.now()/1000);
 assert.equal(await identity(new Request('https://aproar.test/api/bootstrap',{
  headers:{cookie:cookie.replace('aproar_session=','aproar_session=x')}
 }),env),null);
 assert.equal(sqlCalls,0);
});

test('Missing or incorrect Djoune passwords fail closed without consulting Neon credentials',async()=>{
 let sqlCalls=0;
 const sql=async()=>{sqlCalls++;return [{password_matches:true}];};
 for(const password of [undefined,'','wrong-password'])
  await assert.rejects(login({role:'SUPERVISOR',supervisor,password},env,sql),status(401));
 for(const secret of [undefined,''])
  await assert.rejects(login({role:'SUPERVISOR',supervisor,password:env.DJOUNE_XAVIER_PASSWORD},
   {...env,DJOUNE_XAVIER_PASSWORD:secret},sql),status(503));
 assert.equal(sqlCalls,0,'A database credential must never bypass the dedicated secret');
});

test('Existing supervisors retain their individual Neon verification and cannot use the Djoune secret',async()=>{
 const calls=[];
 const oldPassword='test-only-eduardo-existing-key';
 const sql=async(strings,...values)=>{
  calls.push({query:strings.join('?'),values});
  return [{password_matches:values[0]===oldPassword&&values[1]==='EDUARDO'}];
 };
 await assert.rejects(login({role:'SUPERVISOR',supervisor:'EDUARDO',password:env.DJOUNE_XAVIER_PASSWORD},env,sql),status(401));
 const result=await login({role:'SUPERVISOR',supervisor:'EDUARDO',password:oldPassword},env,sql);
 assert.equal(result.session.user,'EDUARDO');
 assert.equal(calls.length,2);
 assert(calls.every(call=>call.query.includes('password_hash_bcrypt=public.crypt(')&&call.values[1]==='EDUARDO'));
 await assert.rejects(login({role:'SUPERVISOR',supervisor:'EDUARDO',password:env.DJOUNE_XAVIER_PASSWORD},env),status(401));
});

function driver(pg){
 const sql=(strings,...values)=>{
  const text=strings.reduce((query,part,index)=>query+(index?'$'+index:'')+part,'');
  return {text,values,then(resolve,reject){return pg.query(text,values).then(result=>result.rows).then(resolve,reject);}};
 };
 sql.transaction=queries=>pg.transaction(async tx=>{
  const results=[];
  for(const query of queries)results.push((await tx.query(query.text,query.values)).rows);
  return results;
 });
 return sql;
}

async function fixture(){
 const pg=new PGlite();
 await pg.exec(readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
 await pg.exec(readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
 await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('Pessoa Centro','Pedreiro',200),('Pessoa Museu','Eletricista',250),('Pessoa Eduardo','Pintor',210); INSERT INTO obras(unidade,nome) VALUES('CENTRO','Serviço Centro'),('MUSEU','Serviço Museu'),('FIEC','Serviço Eduardo'); INSERT INTO engenheiros_teams(engenheiro,email_teams) VALUES('EDUARDO','eduardo@example.test');");
 const settings={units:['CENTRO','MUSEU','FIEC'],unitOwners:{CENTRO:supervisor,MUSEU:supervisor,FIEC:'EDUARDO'},
  teamsAutomation:true,teamsMessage:'Mensagem existente de terceiros',teamsHistory:[],preservedExternalSetting:{enabled:true}};
 await pg.query('UPDATE aproar_web_settings SET data=$1::jsonb WHERE id=1',[JSON.stringify(settings)]);
 return {pg,sql:driver(pg)};
}

async function save(sql,next,session){
 const before=await readDatabase(sql);
 const operations=buildOperations(before,next,session,now);
 await sql`SELECT aproar_web_apply(${before.version},${crypto.randomUUID()},${session.user},${'test-only-digest'},${JSON.stringify(operations)}::jsonb)`;
 return readDatabase(sql);
}

function addConvocation(state,{id,user,unit,person}){
 state.convocacoes.push({id,supervisor:user,dataServico:serviceDate,unidade:unit,obraId:'',turno:'Integral',colaboradores:[person]});
}

function addAttendance(state,convocation,workId){
 state.apontamentos.push({id:'draft-ap-'+convocation.id,convocacaoId:convocation.id,supervisor:convocation.supervisor,
  dataServico:serviceDate,retroativo:false,itens:[{colaboradorId:convocation.colaboradores[0],status:'Presente (Integral)',
   extra:'Não',financeiro:0,noturno:0,acordo:0,ajudaCusto:0,valorExtraDisponivel:0,observacao:'Apontamento preservado',
   servicos:[{obraId:workId,periodo:'Integral'}]}]});
}

test('Djoune convokes and points Centro and Museu after reload while preserving third-party data and permissions',async()=>{
 const {pg,sql}=await fixture();
 try{
  const authenticated=await login({role:'SUPERVISOR',supervisor,password:env.DJOUNE_XAVIER_PASSWORD},env);
  const actor=await identity(new Request('https://aproar.test/api/bootstrap',{
   headers:{cookie:authenticated.cookie.split(';')[0]}
  }),env);
  let db=await readDatabase(sql),next=visibleState(db,eduardo);
  addConvocation(next,{id:'existing-eduardo',user:'EDUARDO',unit:'FIEC',person:'3'});
  addAttendance(next,next.convocacoes[0],'3');
  db=await save(sql,next,eduardo);
  next=visibleState(db,finance);
  next.apontamentos[0].itens[0].financeiro=83.45;
  db=await save(sql,next,finance);
  const existing={
   convocacoes:structuredClone(db.raw.convocacoes),apontamentos:structuredClone(db.raw.apontamentos),
   services:structuredClone(db.raw.servicos_apontamento),colaboradores:structuredClone(db.raw.colaboradores),
   obras:structuredClone(db.raw.obras),settings:structuredClone(db.raw.settings),teams:structuredClone(db.raw.engenheiros_teams)
  };

  next=visibleState(db,actor);
  assert.deepEqual(Object.entries(next.unitOwners).filter(([,owner])=>owner===actor.user).map(([unit])=>unit).sort(),['CENTRO','MUSEU']);
  assert.equal(next.apontamentos.length,0,'Other supervisors attendance stays outside Djoune bootstrap');
  addConvocation(next,{id:'draft-centro',user:supervisor,unit:'CENTRO',person:'1'});
  addConvocation(next,{id:'draft-museu',user:supervisor,unit:'MUSEU',person:'2'});
  await save(sql,next,actor);

  // Rebuild the form state from persisted IDs, as a refreshed browser does.
  db=await readDatabase(sql);
  next=visibleState(db,actor);
  const ownConvocations=next.convocacoes.filter(record=>record.supervisor===supervisor);
  assert.equal(ownConvocations.length,2);
  assert(ownConvocations.every(record=>/^\d+$/.test(record.id)));
  for(const convocation of ownConvocations)
   addAttendance(next,convocation,convocation.unidade==='CENTRO'?'1':'2');
  await save(sql,next,actor);

  db=await readDatabase(sql);
  const own=visibleState(db,actor);
  assert.equal(own.apontamentos.length,2);
  assert.deepEqual(own.apontamentos.map(record=>record.supervisor),[supervisor,supervisor]);
  const ownIds=new Set(ownConvocations.map(record=>record.id));
  assert(db.raw.convocacoes.filter(record=>ownIds.has(String(record.id))).every(record=>record.engenheiro===supervisor&&record.criado_por===supervisor));
  assert(db.raw.apontamentos.filter(record=>ownIds.has(String(record.convocacao_id))).every(record=>record.engenheiro===supervisor&&record.apontado_por===supervisor));
  assert.deepEqual(db.raw.servicos_apontamento.filter(record=>ownIds.has(String(record.convocacao_id))).map(record=>record.unidade_snapshot).sort(),['CENTRO','MUSEU']);

  next=visibleState(db,actor);
  next.convocacoes.find(record=>record.supervisor==='EDUARDO').turno='Manhã';
  assert.throws(()=>buildOperations(db,next,actor,now),error=>error.status===403&&/própria equipe|outro supervisor/.test(error.message));
  next=visibleState(db,actor);
  const foreign=structuredClone(db.state.apontamentos.find(record=>record.supervisor==='EDUARDO'));
  foreign.itens[0].observacao='Tentativa de alterar terceiro';
  foreign.itens[0].financeiro=1;
  next.apontamentos.push(foreign);
  assert.throws(()=>buildOperations(db,next,actor,now),error=>error.status===403);
  next=visibleState(db,actor);
  next.unitOwners.FIEC=supervisor;
  assert.throws(()=>buildOperations(db,next,actor,now),error=>error.status===403&&/configurações/.test(error.message));

  // Financial updates retain Djoune authorship; operational corrections retain the approved value.
  next=visibleState(db,finance);
  const target=next.apontamentos.find(record=>record.supervisor===supervisor);
  target.itens[0].financeiro=175.25;
  db=await save(sql,next,finance);
  next=visibleState(db,actor);
  const correction=next.apontamentos.find(record=>record.convocacaoId===target.convocacaoId);
  correction.itens[0].financeiro=1;
  correction.itens[0].observacao='Correção operacional de Djoune';
  db=await save(sql,next,actor);
  const corrected=db.state.apontamentos.find(record=>record.convocacaoId===target.convocacaoId);
  assert.equal(corrected.itens[0].financeiro,175.25);
  assert.equal(corrected.executor,supervisor);
  assert.equal(corrected.itens[0].observacao,'Correção operacional de Djoune');
  assert.deepEqual(db.raw.convocacoes.filter(record=>record.engenheiro==='EDUARDO'),existing.convocacoes);
  assert.deepEqual(db.raw.apontamentos.filter(record=>record.engenheiro==='EDUARDO'),existing.apontamentos);
  assert.deepEqual(db.raw.servicos_apontamento.filter(record=>!ownIds.has(String(record.convocacao_id))),existing.services);
  assert.deepEqual(db.raw.colaboradores,existing.colaboradores);
  assert.deepEqual(db.raw.obras,existing.obras);
  assert.deepEqual(db.raw.settings,existing.settings);
  assert.deepEqual(db.raw.engenheiros_teams,existing.teams);
 }finally{await pg.close();}
});
