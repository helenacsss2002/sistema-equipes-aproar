import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PGlite} from '@electric-sql/pglite';

const migration=fs.readFileSync(new URL('../migracao_extra_independente_sem_conflito_turno_20261027.sql',import.meta.url),'utf8');
const trigger=`CREATE TRIGGER trg_aproar_validar_sobreposicao
  BEFORE INSERT OR UPDATE OF colaborador_id, data, turno, observacao
  ON public.convocacoes FOR EACH ROW
  EXECUTE FUNCTION public.aproar_validar_sobreposicao_convocacao()`;
const setup=async()=>{
  const pg=new PGlite();
  await pg.exec(fs.readFileSync(new URL('./fixture-schema.sql',import.meta.url),'utf8'));
  await pg.exec(fs.readFileSync(new URL('../migracao_homologacao.sql',import.meta.url),'utf8'));
  await pg.exec(`
    CREATE OR REPLACE FUNCTION public.aproar_turno_normalizado(p_turno text,p_observacao text)
    RETURNS text LANGUAGE plpgsql IMMUTABLE AS $$
    DECLARE t text;
    BEGIN
      t:=COALESCE(NULLIF(btrim(p_turno),''),'');
      IF t<>'' THEN
        IF lower(t) IN ('manhã','manha') THEN RETURN 'Manhã'; END IF;
        IF lower(t)='tarde' THEN RETURN 'Tarde'; END IF;
        IF lower(t)='noite' THEN RETURN 'Noite'; END IF;
        RETURN 'Integral';
      END IF;
      IF COALESCE(p_observacao,'') ILIKE '%Turno: Manhã%' THEN RETURN 'Manhã'; END IF;
      IF COALESCE(p_observacao,'') ILIKE '%Turno: Tarde%' THEN RETURN 'Tarde'; END IF;
      IF COALESCE(p_observacao,'') ILIKE '%Turno: Noite%' THEN RETURN 'Noite'; END IF;
      RETURN 'Integral';
    END $$;
  `);
  await pg.exec(migration);
  await pg.exec(trigger);
  await pg.exec("INSERT INTO colaboradores(nome,funcao,valor_diaria) VALUES('PESSOA NORMAL','Pintor',200),('PESSOA JA COM EXTRA','Pintor',200)");
  await pg.exec("INSERT INTO obras(unidade,nome) VALUES('MUSEU','QA SOBREPOSICAO EXTRA')");
  return pg;
};
const normal=person=>`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
 VALUES(1,${person},'2026-10-27','VICTOR','Integral','Turno: Integral')`;
const extra=person=>`INSERT INTO convocacoes(obra_id,colaborador_id,data,engenheiro,turno,observacao)
 VALUES(1,${person},'2026-10-27','VICTOR','Integral','Extra independente ||APROAR_META|| {"extra_avulsa":true}')`;

test('Extra registrada depois de apontamento normal nao cria choque de turno',async()=>{
  const pg=await setup();
  try {
    await pg.exec(normal(1));
    await pg.exec(extra(1));
    const result=await pg.query('SELECT id,status,observacao FROM convocacoes ORDER BY id');
    assert.equal(result.rows.length,2);
    assert.match(result.rows[1].observacao,/extra_avulsa/);
    // Emissao do mesmo apontamento historico nao gera uma nova presenca.
    assert.equal(result.rows.filter(x=>!x.observacao.startsWith('Extra independente')).length,1);
  }finally{await pg.close();}
});

test('Extra ja existente nao impede convocacao normal real',async()=>{
  const pg=await setup();
  try {
    await pg.exec(extra(2));
    await pg.exec(normal(2));
    assert.equal((await pg.query('SELECT COUNT(*)::int n FROM convocacoes')).rows[0].n,2);
  }finally{await pg.close();}
});

test('Continua bloqueado criar segunda convocacao real no mesmo turno',async()=>{
  const pg=await setup();
  try {
    await pg.exec(normal(1));
    await pg.exec(extra(1));
    await assert.rejects(pg.exec(normal(1)),/APROAR_CONFLITO_TURNO/);
    assert.equal((await pg.query('SELECT COUNT(*)::int n FROM convocacoes')).rows[0].n,2);
  }finally{await pg.close();}
});

test('Migracao pode ser reaplicada sem apagar extras nem alterar historico',async()=>{
  const pg=await setup();
  try {
    await pg.exec(normal(1));
    await pg.exec(extra(1));
    await pg.exec(migration);
    const result=await pg.query('SELECT COUNT(*)::int n FROM convocacoes');
    assert.equal(result.rows[0].n,2);
    await pg.exec("UPDATE convocacoes SET observacao=observacao || ' ' WHERE id=2");
    assert.equal((await pg.query('SELECT COUNT(*)::int n FROM convocacoes')).rows[0].n,2);
  }finally{await pg.close();}
});
