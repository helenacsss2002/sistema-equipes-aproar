import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {PGlite} from '@electric-sql/pglite';
import {readDatabase,visibleState} from './data.js';import {buildOperations} from './operations.js';import {permittedProductionDeletion} from './environment.js';import {login,identity,sameOrigin} from './auth.js';
const actor={role:'SUPERVISOR',user:'EDUARDO'},admin={role:'CONTROLADORIA',user:'CONTROLADORIA'},finance={role:'FINANCEIRO',user:'FINANCEIRO'},now='2026-10-08T12:00:00Z';
function driver(pg){const sql=(strings,...values)=>{const text=strings.reduce((t,s,i)=>t+(i?'$'+i:'')+s,'');return {text,values,then(a,b){return pg.query(text,values).then(r=>r.rows).then(a,b);}};};sql.transaction=queries=>pg.transaction(async tx=>{const result=[];for(const q of queries)result.push((await tx.query(q.text,q.values)).rows);return result;});return sql;}
async function fixture(){const pg=new PGlite();await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('Pessoa QA','Eletricista',241.74); INSERT INTO obras(unidade,nome) VALUES('FIEC','Serviço 1'),('FIEC','Serviço 2'),('SEBRAE','Serviço noturno');");return {pg,sql:driver(pg)};}
async function save(sql,next,session,version){const before=await readDatabase(sql),ops=buildOperations(before,next,session,now);const rid=crypto.randomUUID();await sql`SELECT aproar_web_apply(${version||before.version},${rid},${session.user},${'digest'},${JSON.stringify(ops)}::jsonb)`;return {after:await readDatabase(sql),rid,ops};}
function conv(state){state.convocacoes.push({id:'draft-conv',supervisor:'EDUARDO',dataServico:'2026-10-07',unidade:'FIEC',obraId:'',turno:'Integral',colaboradores:['1']});}
function attendance(state,id){state.apontamentos.push({id:'draft-ap',convocacaoId:id,supervisor:'EDUARDO',dataServico:'2026-10-07',retroativo:true,itens:[{colaboradorId:'1',status:'Presente (Integral)',extra:'Meia diária',financeiro:120,noturno:0,acordo:20,observacao:'Teste',servicos:[{obraId:'1',periodo:'Manhã'},{obraId:'2',periodo:'Tarde'}]}]});}
test('Convocação da tarde com outro supervisor e unidade é aceita após apontamento da manhã já gravado',async()=>{
 const {pg,sql}=await fixture();
 try{
  let db=await readDatabase(sql),morning=structuredClone(db.state);
  conv(morning);morning.convocacoes[0].turno='Manhã';
  morning.convocacoes[0].supervisor='EDUARDO';
  attendance(morning,'draft-conv');
  morning.apontamentos[0].itens[0].status='Presente (Só Manhã)';
  morning.apontamentos[0].itens[0].servicos=[{obraId:'1',periodo:'Manhã'}];
  db=(await save(sql,morning,actor)).after;
  assert.equal(db.state.convocacoes.length,1);
  assert.equal(db.state.apontamentos.length,1);
  assert.equal(db.state.convocacoes[0].turno,'Manhã');
  const afternoon=structuredClone(db.state);
  afternoon.convocacoes.push({id:'conv-tarde-qa',supervisor:'JOEL',dataServico:'2026-10-07',unidade:'SEBRAE',obraId:'',turno:'Tarde',colaboradores:['1']});
  db=(await save(sql,afternoon,admin)).after;
  const all=db.state.convocacoes.filter(c=>c.dataServico==='2026-10-07'&&c.colaboradores.includes('1'));
  assert.equal(all.length,2,'Dois registros independentes no mesmo dia');
  assert.deepEqual(all.map(c=>c.turno).sort(),['Manhã','Tarde']);
  assert.equal(db.state.apontamentos.length,1,'A manhã apontada continua intacta; a tarde aguarda confirmação');
  const follow=structuredClone(db.state),newConv=follow.convocacoes.find(c=>c.turno==='Tarde');
  follow.apontamentos.push({id:'ap-tarde-qa',convocacaoId:newConv.id,supervisor:'JOEL',dataServico:'2026-10-07',retroativo:true,itens:[{colaboradorId:'1',status:'Presente (Só Tarde)',extra:'Não',financeiro:0,noturno:0,acordo:0,observacao:'',servicos:[{obraId:'3',periodo:'Tarde'}]}]});
  db=(await save(sql,follow,admin)).after;
  assert.equal(db.state.apontamentos.length,2);
  assert.equal(db.raw.apontamentos.length,2);
  assert.equal(db.raw.apontamentos.filter(a=>String(a.colaborador_id)==='1'&&new Date(a.data_servico).toISOString().slice(0,10)==='2026-10-07').length,2);
  assert.equal(new Set(db.raw.apontamentos.map(a=>a.convocacao_id)).size,2);
 }finally{await pg.close();}
});

test('Registros já apontados no turno da manhã não bloqueiam tarde, mas impedem uma segunda manhã',async()=>{
 const {pg,sql}=await fixture();
 try{
  let db=await readDatabase(sql),morning=structuredClone(db.state);
  conv(morning);morning.convocacoes[0].turno='Manhã';attendance(morning,'draft-conv');
  morning.apontamentos[0].itens[0].status='Presente (Só Manhã)';
  morning.apontamentos[0].itens[0].servicos=[{obraId:'1',periodo:'Manhã'}];
  db=(await save(sql,morning,actor)).after;
  const next=structuredClone(db.state),second={id:'other-qa',supervisor:'JOEL',dataServico:'2026-10-07',unidade:'SEBRAE',obraId:'',turno:'Tarde',colaboradores:['1']};
  next.convocacoes.push(second);
  assert.doesNotThrow(()=>buildOperations(db,next,admin,now));
  next.convocacoes[1].turno='Manhã';
  assert.throws(()=>buildOperations(db,next,admin,now),/Conflito/);
  next.convocacoes[1].turno='Integral';
  assert.throws(()=>buildOperations(db,next,admin,now),/Conflito/);
 }finally{await pg.close();}
});


import vm from 'node:vm';
const app=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const begin=app.indexOf("$('#admin-conv-form').onsubmit=async e=>");
const end=app.indexOf('    }else{body.innerHTML=',begin);
assert(begin>0&&end>begin);
const handler=app.slice(begin,end);
const line=name=>app.slice(app.indexOf('  function '+name+'('),app.indexOf('\n',app.indexOf('  function '+name+'(')));
function uiHarness({freshTurn='Manhã',nextTurn='Tarde',failure=null,pending=null}={}){
 const notices=[],calls=[],writes=[],callbacks=[];
 const fieldValues={'ac-date':'2026-10-07','ac-turn':nextTurn,'ac-unit':'SEBRAE','ac-sup':'JOEL','ac-name':'','ac-role':'','ac-loose':''};
 const elements=new Map(Object.entries(fieldValues).map(([id,value])=>['#'+id,{value,checked:false}]));
 const button={disabled:false},form={dataset:{},isConnected:true,querySelector:()=>button};
 const holder={onsubmit:null};elements.set('#admin-conv-form',holder);
 const staff={id:'1',nome:'Pessoa QA',funcao:'Eletricista',inativo:false};
 const existing={id:'1',supervisor:'EDUARDO',dataServico:'2026-10-07',unidade:'FIEC',obraId:'1',turno:'Integral',colaboradores:['1']};
 const state={convocacoes:[existing],apontamentos:[],indisponibilidades:[]};
 const fresh={...structuredClone(state),convocacoes:[{...existing,turno:freshTurn}]};
 const ctx={state,OBRAS:[{id:'1',nome:'Obra principal',unidade:'FIEC'},{id:'3',nome:'Obra da tarde',unidade:'SEBRAE'}],COLABORADORES:[staff],
  onlineSaving:false,onlineQueued:false,pendingSaveRecovery:pending,onlineWritable:true,onlineSession:{role:'CONTROLADORIA',user:'CONTROLADORIA'},
  selected:new Set(['1']),adminConvDate:'',
  $:selector=>elements.get(selector),$$:()=>[],
  toast:(message,error)=>notices.push({message,error}),showToast:(message,error)=>notices.push({message,error}),
  api:async path=>{calls.push(path);if(failure)throw failure;return {state:fresh};},
  applyOnline:result=>{ctx.state=structuredClone(result.state);},
  clean:value=>String(value).trim().toUpperCase(),colaboradorById:id=>ctx.COLABORADORES.find(person=>person.id===id),
  registerConvocationConflicts:(...args)=>calls.push({conflict:args}),uid:()=> 'new-draft',now:()=>new Date('2026-10-07T12:00:00Z'),
  audit:()=>{},saveData:(onSuccess)=>{writes.push(structuredClone(ctx.state));callbacks.push(onSuccess);return true;},
  renderAdminConv:()=>calls.push('render-admin'),
 };
 vm.createContext(ctx);vm.runInContext(line('blocked')+'\n'+line('overlaps')+'\n'+handler,ctx);
 return {ctx,calls,writes,notices,callbacks,form,button,submit:()=>holder.onsubmit({preventDefault(){},currentTarget:form})};
}

test('Controladoria consulta o estado atual antes de validar a tarde e só mostra sucesso após a gravação',async()=>{
 const x=uiHarness();await x.submit();
 assert.equal(x.calls[0],'/api/bootstrap');assert.equal(x.writes.length,1);
 assert.deepEqual(Array.from(x.writes[0].convocacoes,c=>c.turno),['Manhã','Tarde']);
 assert.equal(x.notices.some(n=>/confirmada/.test(n.message)),false);
 x.callbacks[0]();assert(x.notices.some(n=>/Convocação confirmada/.test(n.message)));
 assert.equal(x.form.dataset.submitting,'false');assert.equal(x.button.disabled,false);
});
test('Consulta falha ou envio pendente preservam o formulário sem enviar nova convocação',async()=>{
 const x=uiHarness({failure:new Error('Consulta indisponível')});await x.submit();
 assert.equal(x.writes.length,0);assert(x.notices.some(n=>/Nenhuma convocação foi enviada/.test(n.message)));
 assert.equal(x.form.dataset.submitting,'false');assert.equal(x.button.disabled,false);
 const pending=uiHarness({pending:{}});await pending.submit();assert.equal(pending.calls.length,0);assert.equal(pending.writes.length,0);
});
test('Turno realmente ocupado continua bloqueado com identificação da equipe existente',async()=>{
 const x=uiHarness({freshTurn:'Manhã',nextTurn:'Manhã'});await x.submit();
 assert.equal(x.writes.length,0);assert(x.calls.some(c=>typeof c==='object'&&c.conflict));
 assert(x.notices.some(n=>/Turnos sobrepostos/.test(n.message)&&/EDUARDO/.test(n.message)&&/FIEC/.test(n.message)));
});
