import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {validateAdminRelocationInput,buildAdminRelocationOperations} from './admin-relocation.js';
import {metadata} from './neon-adapter.js';

globalThis.crypto??=webcrypto;
const requestId='11111111-2222-4333-8444-555555555555';
const req={requestId,convocacaoId:'1',colaboradorId:'1',
 source:{dataServico:'2026-11-03',unidade:'CENTRO',supervisor:'VICTOR',obraId:'1',turno:'Integral'},
 destination:{dataServico:'2026-11-03',unidade:'UNIFOR',supervisor:'JOEL',obraId:'2',turno:'Integral'}};
const current={id:'1',colaborador_id:'1',data:'2026-11-03',turno:'Integral',obra_id:'1',
 engenheiro:'VICTOR',unidade:'CENTRO',observacao:'Turno: Integral ||APROAR_META|| {"convocado_por":"VICTOR"}',
 custos_separados:false,has_point:false,has_services:false};
const works=[{id:'1',unidade:'CENTRO',nome:'SERVIÇO CENTRO'},{id:'2',unidade:'UNIFOR',nome:'SERVIÇO UNIFOR'}];
const args={current,works,conflicts:[],unavailable:false,request:validateAdminRelocationInput(req),
 actor:'CONTROLADORIA',timestamp:'2026-11-03T19:10:00Z'};

test('Transferência administrativa gera apenas UPDATE da convocação e auditoria, nunca DELETE/INSERT de apontamento',()=>{
 const operations=buildAdminRelocationOperations(args);
 assert.deepEqual(operations.map(op=>[op.table,op.action]),[['convocacoes','update'],['auditoria','insert']]);
 assert.equal(operations[0].id,'1');
 assert.equal(operations[0].data.obra_id,'2');
 assert.equal(operations[0].data.engenheiro,'JOEL');
 assert.equal(operations[0].data.turno,'Integral');
 assert.equal(operations[0].data.data,'2026-11-03');
 assert.equal(operations[1].data.acao,'REALOCACAO_ADMINISTRATIVA');
 assert.deepEqual(JSON.parse(JSON.stringify(operations[1].data.antes)),{dataServico:'2026-11-03',unidade:'CENTRO',supervisor:'VICTOR',obraId:'1',turno:'Integral'});
 assert.equal(operations[1].data.depois.unidade,'UNIFOR');
 assert.equal(metadata(operations[0].data.observacao).meta.convocado_por,'VICTOR');
});

test('Realocação recusa apontamento, serviços históricos, conflito de turno e original desatualizado',()=>{
 for(const property of ['has_point','has_services','custos_separados']){
  const changed={...current,[property]:true};
  assert.throws(()=>buildAdminRelocationOperations({...args,current:changed}),/histórico|apontamento/);
 }
 assert.throws(()=>buildAdminRelocationOperations({...args,current:{...current,engenheiro:'FELIPE'}}),/alterada/);
 assert.throws(()=>buildAdminRelocationOperations({...args,current:{...current,obra_id:'2'}}),/alterada/);
 assert.throws(()=>buildAdminRelocationOperations({...args,conflicts:[{turno:'Integral',observacao:'Turno: Integral'}]}),/conflito/);
 assert.throws(()=>buildAdminRelocationOperations({...args,unavailable:true}),/indisponível/);
 assert.throws(()=>buildAdminRelocationOperations({...args,works:works.filter(w=>w.unidade==='CENTRO')}),/Cadastre uma obra/);
});
test('Extra independente não impede realocação da convocação normal',()=>{
 const conflicts=[{turno:'Integral',observacao:'Extra independente ||APROAR_META|| {"extra_avulsa":true}'}];
 assert.equal(buildAdminRelocationOperations({...args,conflicts}).length,2);
});
test('Obra a definir mantém vínculo antigo preservado e escolhe a obra de destino sem inventar serviço',()=>{
 const source={...req.source,obraId:''},destination={...req.destination,obraId:''};
 const original={...current,observacao:'Turno: Integral ||APROAR_META|| {"servico_a_definir":true}'};
 const operations=buildAdminRelocationOperations({...args,current:original,request:validateAdminRelocationInput({...req,source,destination})});
 assert.equal(operations[0].data.obra_id,'2');
 assert.equal(metadata(operations[0].data.observacao).meta.servico_a_definir,true);
 assert.equal(operations[1].data.antes.obraId,'');
 assert.equal(operations[1].data.depois.obraId,'');
});
test('Requisições inválidas e outros responsáveis não são aceitos',()=>{
 for(const body of [
  {...req,convocacaoId:'cv-1'},
  {...req,destination:{...req.destination,supervisor:'DESCONHECIDO'}},
  {...req,destination:{...req.destination,obraId:'javascript:1'}},
  {...req,destination:{...req.destination,dataServico:'2026-02-30'}},
  {...req,destination:{...req.destination,unidade:'https://unidade-ilegal'}},
  {...req,outraCoisa:'sim'}
 ])assert.throws(()=>validateAdminRelocationInput(body));
});

test('Neon grava transferência do colaborador sem duplicar presença e sem modificar colegas',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('COLABORADOR 1','Pintor',150),('COLEGA 2','Servente',120)");
  await pg.exec("INSERT INTO obras(nome,unidade) VALUES('SERVIÇO CENTRO','CENTRO'),('SERVIÇO UNIFOR','UNIFOR')");
  await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
    VALUES(1,1,'2026-11-03','VICTOR','Integral','Turno: Integral ||APROAR_META|| {"convocado_por":"VICTOR"}'),
          (1,2,'2026-11-03','VICTOR','Integral','Turno: Integral')`);
  const ops=buildAdminRelocationOperations(args);
  const version=(await pg.query('SELECT aproar_web_fingerprint() AS version')).rows[0].version;
  const applied=await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb) AS result',[
    version,requestId,'CONTROLADORIA','sha-qa-admin-relocation',JSON.stringify(ops)]);
  assert.ok(applied.rows[0].result);
  const c1=(await pg.query('SELECT obra_id,engenheiro,turno FROM convocacoes WHERE id=1')).rows[0];
  assert.equal(Number(c1.obra_id),2);
  assert.equal(c1.engenheiro,'JOEL');
  const colleague=(await pg.query('SELECT obra_id,engenheiro FROM convocacoes WHERE id=2')).rows[0];
  assert.equal(Number(colleague.obra_id),1);
  assert.equal(colleague.engenheiro,'VICTOR');
  assert.equal((await pg.query('SELECT count(*)::int AS n FROM convocacoes')).rows[0].n,2);
  assert.equal((await pg.query('SELECT count(*)::int AS n FROM apontamentos')).rows[0].n,0);
  assert.equal((await pg.query("SELECT count(*)::int AS n FROM auditoria WHERE acao='REALOCACAO_ADMINISTRATIVA'")).rows[0].n,1);
  assert.equal((await pg.query('SELECT count(*)::int AS n FROM aproar_web_requests WHERE id=$1',[requestId])).rows[0].n,1);
 }finally{await pg.close();}
});
test('Frontend usa rota pontual com requestId, sem chamar salvamento global para transferência sem apontamento',()=>{
 const ui=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
 const worker=fs.readFileSync(new URL('./worker.js',import.meta.url),'utf8');
 const form=ui.slice(ui.indexOf("$('#ae-form').onsubmit=async"),ui.indexOf('const refresh=()=>',ui.indexOf("$('#ae-form').onsubmit=async")));
 assert.match(form,/await saveAdministrativeRelocation\(x,destination\)/);
 const helper=ui.slice(ui.indexOf('async function saveAdministrativeRelocation('),ui.indexOf('function relocateAdminPerson(',ui.indexOf('async function saveAdministrativeRelocation(')));
 assert.match(helper,/\/api\/admin-relocation/);
 assert.match(helper,/\/api\/save-status\?requestId=/);
 assert.match(helper,/const requestId=crypto\.randomUUID\(\)/);
 assert.match(helper,/await restoreOnlineSession\(\)/);
 assert.doesNotMatch(helper,/saveData\(/);
 assert.match(worker,/if\(path==='\/api\/admin-relocation'&&request.method==='POST'\)/);
 assert.match(worker,/session.role!=='CONTROLADORIA'/);
});
