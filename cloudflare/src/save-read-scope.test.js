import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash, randomUUID} from 'node:crypto';
import {PGlite} from '@electric-sql/pglite';
import {readDatabase} from './data.js';
import {buildOperations} from './operations.js';

const admin = {role:'CONTROLADORIA',user:'CONTROLADORIA'};
const timestamp = '2026-11-16T18:00:00Z';

function driver(pg, reads) {
  const sql = (strings, ...values) => {
    const text = strings.reduce((result, part, index) => result + (index ? '$' + index : '') + part, '');
    return {text, values, then(resolve, reject) {return pg.query(text, values).then(result => result.rows).then(resolve, reject);}};
  };
  sql.transaction = (queries, options) => pg.transaction(async tx => {
    reads.push({queries:queries.map(query => query.text), options});
    const result = [];
    for (const query of queries) result.push((await tx.query(query.text, query.values)).rows);
    return result;
  });
  return sql;
}

async function fixture() {
  const pg = new PGlite();
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec(`
    INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES
      ('PESSOA TESTE','Pintor',200),('COLEGA TESTE','Servente',180);
    INSERT INTO obras(unidade,nome) VALUES('CENTRO','SERVICO TESTE');
    INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,criado_por)
      VALUES(1,1,'2026-11-10','DJOUNE XAVIER','Integral','DJOUNE XAVIER');
    INSERT INTO apontamentos(convocacao_id,data_servico,colaborador_id,engenheiro,status,apontado_por,custo_pago)
      VALUES('1','2026-11-10','1','DJOUNE XAVIER','Presente (Integral)','DJOUNE XAVIER',200);
    INSERT INTO servicos_apontamento(convocacao_id,obra_id,obra_nome_snapshot,unidade_snapshot,periodo,principal)
      VALUES('1','1','SERVICO TESTE','CENTRO','Integral',true);
    INSERT INTO indisponibilidades(colaborador_id,colaborador_nome_snapshot,motivo,inicio,fim,criado_por)
      VALUES('2','COLEGA TESTE','Atestado anterior','2026-11-01','2026-11-02','CONTROLADORIA');
    INSERT INTO auditoria(entidade,entidade_id,acao,usuario,ocorrido_em,antes,depois,contexto)
      VALUES('apontamentos','1','HISTORICO_PRESERVADO','DJOUNE XAVIER','2026-11-10T18:00:00Z',
        '{"valor":150}','{"valor":200}','{"origem":"historico-de-teste","detalhe":"nao-substituir"}');
    UPDATE aproar_web_settings SET data='{"units":["CENTRO"],"unitOwners":{"CENTRO":"DJOUNE XAVIER"},"teamsAutomation":false,"teamsMessage":"","teamsHistory":[]}'::jsonb WHERE id=1;
  `);
  const reads = [];
  return {pg, sql:driver(pg, reads), reads};
}

function normalizeAuditIds(operations) {
  return operations.map(operation => operation.table === 'auditoria'
    ? {...operation,id:'audit:server-generated'} : operation);
}

function rejection(db, next, session) {
  try {buildOperations(db, next, session, timestamp);}
  catch (error) {return {status:error.status,message:error.message};}
  assert.fail('The unauthorized operation was accepted.');
}

test('Pré-leitura sem auditoria mantém operações, autorização, histórico e idempotência da indisponibilidade',async t => {
  const {pg, sql, reads} = await fixture();
  try {
    const full = await readDatabase(sql);
    const lean = await readDatabase(sql,{includeAudit:false});
    const next = structuredClone(full.state);
    next.indisponibilidades.push({id:'new-unavailability',colaboradorId:'1',
      inicio:'2026-11-16',fim:'2026-11-17',motivo:'Atestado médico',obs:'Registro novo de teste'});
    // Browser audit text is not an authorization source or a write operation.
    next.auditoria.push({id:'browser-audit',action:'AUDITORIA_NAO_CONFIAVEL',usuario:'CONTROLADORIA'});
    const fullOperations = buildOperations(full,next,admin,timestamp);
    const leanOperations = buildOperations(lean,next,admin,timestamp);

    await t.test('Não transfere linhas de auditoria e produz as mesmas operações autorizadas',() => {
      assert.equal(full.raw.auditoria.length,1);
      assert.equal(lean.raw.auditoria.length,0);
      assert.equal(lean.state.auditoria.length,0);
      assert.equal(lean.version,full.version);
      const auditQueries = reads[1].queries.filter(query => /FROM auditoria/.test(query));
      assert.equal(auditQueries.length,1);
      assert.match(auditQueries[0],/WHERE false$/);
      assert.deepEqual(reads[1].options,{isolationLevel:'RepeatableRead',readOnly:true});
      assert.deepEqual(normalizeAuditIds(leanOperations),normalizeAuditIds(fullOperations));
      assert.deepEqual(leanOperations.map(operation => [operation.table,operation.action]),
        [['indisponibilidades','insert'],['auditoria','insert']]);
      assert.equal(leanOperations[1].data.acao,'SALVAR');
      assert.equal(leanOperations[1].data.usuario,'CONTROLADORIA');
    });

    await t.test('Supervisor, Financeiro e Visualizar continuam sem autorização para gravar indisponibilidade',() => {
      for (const session of [{role:'SUPERVISOR',user:'DJOUNE XAVIER'},
        {role:'FINANCEIRO',user:'FINANCEIRO'},{role:'VISUALIZAR',user:'VISUALIZAR'}]) {
        const original = rejection(full,next,session);
        const optimized = rejection(lean,next,session);
        assert.equal(optimized.status,403);
        assert.deepEqual(optimized,original);
      }
    });

    await t.test('PGlite grava uma vez, mantém o histórico completo e rejeita reutilização por outro ator',async () => {
      const unchangedTables = ['colaboradores','obras','convocacoes','apontamentos','servicos_apontamento','aproar_web_settings'];
      const snapshots = new Map();
      for (const table of unchangedTables) snapshots.set(table,(await pg.query(`SELECT * FROM ${table} ORDER BY id`)).rows);
      const historicalAudit = (await pg.query('SELECT * FROM auditoria ORDER BY id')).rows;
      const existingUnavailable = (await pg.query('SELECT * FROM indisponibilidades ORDER BY id')).rows;
      const requestId = randomUUID();
      const digest = createHash('sha256').update(JSON.stringify(next)).digest('hex');
      const apply = actor => pg.query('SELECT aproar_web_apply($1,$2,$3,$4,$5::jsonb) AS result',
        [lean.version,requestId,actor,digest,JSON.stringify(leanOperations)]);
      const first = await apply(admin.user);
      const replay = await apply(admin.user);
      assert.deepEqual(replay.rows,first.rows);
      await assert.rejects(apply('DJOUNE XAVIER'),/APROAR_REQUEST_MISMATCH/);

      for (const [table,before] of snapshots) assert.deepEqual((await pg.query(`SELECT * FROM ${table} ORDER BY id`)).rows,before,table);
      const unavailable = (await pg.query('SELECT * FROM indisponibilidades ORDER BY id')).rows;
      assert.equal(unavailable.length,2);
      assert.deepEqual(unavailable[0],existingUnavailable[0]);
      assert.equal(unavailable[1].colaborador_id,'1');
      assert.equal(unavailable[1].motivo,'Atestado médico');
      assert.equal(unavailable[1].criado_por,'CONTROLADORIA');
      const audits = (await pg.query('SELECT * FROM auditoria ORDER BY id')).rows;
      assert.equal(audits.length,2);
      assert.deepEqual(audits[0],historicalAudit[0]);
      assert.equal(audits[1].acao,'SALVAR');
      assert.equal(audits[1].usuario,'CONTROLADORIA');
      assert.equal(audits[1].contexto.operacoes[0].tabela,'indisponibilidades');
      assert.equal((await pg.query('SELECT COUNT(*)::int n FROM aproar_web_requests')).rows[0].n,1);
      const refreshed = await readDatabase(sql);
      assert.equal(refreshed.raw.auditoria.length,2,'A leitura normal continua trazendo o histórico.');
      assert.equal(refreshed.state.indisponibilidades.length,2);
    });
  } finally {await pg.close();}
});
