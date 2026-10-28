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
