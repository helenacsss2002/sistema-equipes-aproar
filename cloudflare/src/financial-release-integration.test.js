import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase} from './data.js';
import {buildOperations} from './operations.js';

const supervisor={role:'SUPERVISOR',user:'VICTOR'};
const driver=pg=>{
 const sql=(strings,...values)=>{const text=strings.reduce((out,s,i)=>out+(i?'$'+i:'')+s,'');return {text,values,then(a,b){return pg.query(text,values).then(r=>r.rows).then(a,b);}}};
 sql.transaction=queries=>pg.transaction(async tx=>{const result=[];for(const q of queries)result.push((await tx.query(q.text,q.values)).rows);return result;});return sql;
};

test('Apontamento mantém valor e presença; pós-prazo só altera bonificação com aprovação e consumo atômico',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('QA VICTOR','Pintor',200)");
  await pg.exec("INSERT INTO obras(unidade,nome) VALUES('CENTRO','QA SERVIÇO')");
  await pg.exec("INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao) VALUES(1,1,'2026-10-26','VICTOR','Integral','Turno: Integral')");
  await pg.exec("INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_acordo,apontado_por,apontado_em,custo_encargos_base) VALUES('1','2026-10-26','1','VICTOR','Presente (Integral)',30,'VICTOR','2026-10-26T20:00:00Z',200)");
  await pg.exec("INSERT INTO servicos_apontamento(convocacao_id,obra_id,unidade_snapshot,obra_nome_snapshot,periodo,principal) VALUES('1','1','CENTRO','QA SERVIÇO','Integral',true)");
  const sql=driver(pg),db=await readDatabase(sql);
  const next=structuredClone(db.state);
  next.apontamentos[0].itens[0].acordo=60;
  const timestamp='2026-10-27T13:10:00Z';
  assert.throws(()=>buildOperations(db,next,supervisor,timestamp),/Prazo financeiro encerrado/);
  assert.equal((await pg.query('SELECT valor_acordo FROM apontamentos WHERE id=1')).rows[0].valor_acordo,'30');
  const requestId='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
  db.releaseEvents=[
   {acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'VICTOR',ocorrido_em:'2026-10-27T13:01:00Z',contexto:{requestId,supervisor:'VICTOR',colaboradorId:'1',dataServico:'2026-10-26',fields:['Bonificação'],reason:'Correção testada'}},
   {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:'FINANCEIRO',ocorrido_em:'2026-10-27T13:02:00Z',contexto:{requestId}}
  ];
  const ops=buildOperations(db,next,supervisor,timestamp);
  assert.equal(ops.filter(x=>x.table==='auditoria'&&x.data.acao==='LIBERACAO_FINANCEIRA_UTILIZADA').length,1);
  const txId=crypto.randomUUID();
  const params=[db.version,txId,'VICTOR','fixed-sha',JSON.stringify(ops)];
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',params);
  const saved=(await pg.query('SELECT valor_acordo,status FROM apontamentos WHERE id=1')).rows[0];
  assert.equal(Number(saved.valor_acordo),60);
  assert.equal(saved.status,'Presente (Integral)');
  assert.equal((await pg.query("SELECT count(*)::int AS n FROM auditoria WHERE acao='LIBERACAO_FINANCEIRA_UTILIZADA'")).rows[0].n,1);
  const updated=await readDatabase(sql);
  updated.releaseEvents=[...db.releaseEvents,...(await pg.query("SELECT acao,usuario,ocorrido_em,contexto FROM auditoria WHERE acao='LIBERACAO_FINANCEIRA_UTILIZADA'")).rows];
  const newer=structuredClone(updated.state);newer.apontamentos[0].itens[0].acordo=80;
  assert.throws(()=>buildOperations(updated,newer,supervisor,'2026-10-27T13:15:00Z'),/Solicite liberação/);
  assert.equal((await pg.query("SELECT count(*)::int AS n FROM apontamentos")).rows[0].n,1);
 }finally{await pg.close();}
});

test('Uma autorização do Financeiro cobre Extra, Bonificação e Passagem no Neon sem afetar os colegas',async()=>{
 const pg=new PGlite();
 try{
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('QA EXTRA AUTORIZADA','Pintor',200),('QA COLEGA INTACTO','Servente',150)");
  await pg.exec("INSERT INTO obras(unidade,nome) VALUES('CENTRO','QA SERVIÇO')");
  await pg.exec(`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
    VALUES(1,1,'2026-10-30','VICTOR','Integral','Turno: Integral'),
          (1,2,'2026-10-30','VICTOR','Integral','Turno: Integral')`);
  await pg.exec(`INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,valor_acordo,apontado_por,apontado_em,custo_encargos_base)
    VALUES('1','2026-10-30','1','VICTOR','Presente (Integral)',0,'VICTOR','2026-10-30T20:00:00Z',200),
          ('2','2026-10-30','2','VICTOR','Presente (Integral)',0,'VICTOR','2026-10-30T20:00:00Z',150)`);
  await pg.exec(`INSERT INTO servicos_apontamento(convocacao_id,obra_id,unidade_snapshot,obra_nome_snapshot,periodo,principal)
    VALUES('1','1','CENTRO','QA SERVIÇO','Integral',true),('2','1','CENTRO','QA SERVIÇO','Integral',true)`);
  const sql=driver(pg),db=await readDatabase(sql),next=structuredClone(db.state);
  const person=next.apontamentos.find(a=>a.itens[0].colaboradorId==='1').itens[0];
  person.valorExtraDisponivel=100;
  person.acordo=50;
  person.ajudaCusto=11;
  const scope={supervisor:'VICTOR',colaboradorId:'1',dataServico:'2026-10-30'};
  const grantIds=['77777777-7777-4777-8777-777777777777'];
  const events=grantIds.flatMap(id=>[
   {acao:'SOLICITACAO_LIBERACAO_FINANCEIRA',usuario:'VICTOR',ocorrido_em:'2026-11-03T13:00:01Z',
    contexto:{requestId:id,...scope,fields:['Extra'],reason:'Revisão já liberada pelo Financeiro'}},
   {acao:'LIBERACAO_FINANCEIRA_AUTORIZADA',usuario:'FINANCEIRO',ocorrido_em:'2026-11-03T13:00:02Z',
    contexto:{requestId:id,...scope}}
  ]);
  db.releaseEvents=events;
  const ts='2026-11-03T17:15:00Z',ops=buildOperations(db,next,supervisor,ts);
  const used=ops.filter(o=>o.data?.acao==='LIBERACAO_FINANCEIRA_UTILIZADA');
  assert.equal(used.length,1);
  assert.deepEqual(new Set(used.map(o=>o.data.contexto.requestId)),new Set(grantIds));
  assert.deepEqual(new Set(used[0].data.contexto.fields),new Set(['Extra','Bonificação','Passagem / ajuda de custo']));
  const pointed=ops.filter(o=>o.table==='apontamentos'&&o.action==='update');
  assert.equal(pointed.length,1);
  assert.equal(pointed[0].data.colaborador_id,'1');
  assert.equal(ops.some(o=>o.action==='delete'),false);
  const requestId=crypto.randomUUID();
  await pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb)',[db.version,requestId,'VICTOR','qa-aprovado-correto',JSON.stringify(ops)]);
  const after=await readDatabase(sql);
  assert.equal(after.raw.convocacoes.length,2);
  assert.equal(after.raw.apontamentos.length,2);
  const corrected=after.state.apontamentos.find(a=>a.itens[0].colaboradorId==='1').itens[0];
  const colleague=after.state.apontamentos.find(a=>a.itens[0].colaboradorId==='2').itens[0];
  assert.equal(corrected.valorExtraDisponivel,100);
  assert.equal(corrected.acordo,50);
  assert.equal(corrected.ajudaCusto,11);
  assert.equal(colleague.valorExtraDisponivel,0);
  assert.equal(colleague.acordo,0);
  after.releaseEvents=[...events,...used.map(o=>({acao:o.data.acao,usuario:o.data.usuario,
    ocorrido_em:ts,contexto:o.data.contexto}))];
  const nextSave=structuredClone(after.state);
  nextSave.apontamentos.find(a=>a.itens[0].colaboradorId==='1').itens[0].acordo=70;
  assert.throws(()=>buildOperations(after,nextSave,supervisor,'2026-11-03T17:16:00Z'),/Solicite liberação/);
 }finally{await pg.close();}
});
