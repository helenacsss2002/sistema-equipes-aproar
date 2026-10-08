-- Execute apenas na branch aproar-homologacao antes de testar a nova versão.
-- Alterações aditivas: nenhuma tabela de registros é apagada ou recriada.
BEGIN;
CREATE TABLE IF NOT EXISTS aproar_web_settings (
 id integer PRIMARY KEY CHECK(id=1), data jsonb NOT NULL DEFAULT '{}'::jsonb
);
INSERT INTO aproar_web_settings(id) VALUES(1) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS aproar_web_requests (
 id text PRIMARY KEY, actor text NOT NULL, payload_hash text NOT NULL,
 result jsonb NOT NULL, criado_em timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE colaboradores ADD COLUMN IF NOT EXISTS categoria_diaria text;
ALTER TABLE colaboradores ADD COLUMN IF NOT EXISTS avulso text;

CREATE OR REPLACE FUNCTION aproar_web_fingerprint() RETURNS text
LANGUAGE sql STABLE AS $$
 SELECT md5(jsonb_build_object(
 'colaboradores',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]') FROM colaboradores t),
 'obras',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]') FROM obras t),
 'convocacoes',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]') FROM convocacoes t),
 'apontamentos',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]') FROM apontamentos t),
 'servicos',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]') FROM servicos_apontamento t),
 'indisponibilidades',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]') FROM indisponibilidades t),
 'conflitos',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY id),'[]') FROM conflitos_convocacao t),
 'teams',(SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY engenheiro),'[]') FROM engenheiros_teams t),
 'settings',(SELECT data FROM aproar_web_settings WHERE id=1))::text)
$$;

CREATE OR REPLACE FUNCTION aproar_web_apply(
 expected text, request_id text, actor_name text, payload_digest text, operations jsonb
) RETURNS jsonb LANGUAGE plpgsql AS $$
DECLARE op jsonb; d jsonb; mapping jsonb := '{}'::jsonb; result jsonb;
 tbl text; key text; ident text; assigned bigint; columns_list text; values_list text; assignments text;
 previous aproar_web_requests%ROWTYPE;
BEGIN
 -- Serializes web writes with the existing Streamlit writes to these tables.
 LOCK TABLE colaboradores,obras,convocacoes,apontamentos,servicos_apontamento,
 indisponibilidades,conflitos_convocacao,engenheiros_teams,aproar_web_settings,
 aproar_web_requests IN SHARE ROW EXCLUSIVE MODE;
 SELECT * INTO previous FROM aproar_web_requests WHERE id=request_id;
 IF FOUND THEN
   IF previous.actor <> actor_name OR previous.payload_hash <> payload_digest THEN
     RAISE EXCEPTION 'APROAR_REQUEST_MISMATCH';
   END IF;
   RETURN previous.result;
 END IF;
 IF expected IS DISTINCT FROM aproar_web_fingerprint() THEN
   RAISE EXCEPTION 'APROAR_STALE';
 END IF;
 FOR op IN SELECT value FROM jsonb_array_elements(operations) LOOP
   tbl:=op->>'table'; d:=coalesce(op->'data','{}'::jsonb); ident:=op->>'id';
   IF tbl NOT IN ('colaboradores','obras','convocacoes','apontamentos','servicos_apontamento',
                 'indisponibilidades','conflitos_convocacao','engenheiros_teams','aproar_web_settings','auditoria') THEN
     RAISE EXCEPTION 'APROAR_TABLE_NOT_ALLOWED';
   END IF;
   -- Resolve IDs allocated earlier in this same transaction.
   FOR key IN SELECT jsonb_object_keys(d) LOOP
     IF key IN ('colaborador_id','obra_id','convocacao_id','convocacao_existente_id') AND mapping ? (d->>key) THEN
       d:=jsonb_set(d,ARRAY[key],to_jsonb(mapping->>(d->>key)));
     END IF;
   END LOOP;
   IF mapping ? ident THEN ident:=mapping->>ident; END IF;
   IF op->>'action'='delete' THEN
     IF tbl IN ('engenheiros_teams','aproar_web_settings','auditoria') THEN RAISE EXCEPTION 'APROAR_DELETE_NOT_ALLOWED'; END IF;
     IF ident !~ '^[0-9]+$' THEN RAISE EXCEPTION 'APROAR_INVALID_ID'; END IF;
     EXECUTE format('DELETE FROM public.%I WHERE id=$1::bigint',tbl) USING ident;
     CONTINUE;
   END IF;
   IF op->>'action' NOT IN ('insert','update') THEN RAISE EXCEPTION 'APROAR_INVALID_ACTION'; END IF;
   d:=d-'id';
   IF EXISTS(SELECT 1 FROM jsonb_object_keys(d) k WHERE k !~ '^[a-z_][a-z0-9_]*$' OR k='id') THEN RAISE EXCEPTION 'APROAR_INVALID_COLUMN'; END IF;
   SELECT string_agg(format('%I',k),',' ORDER BY k),string_agg(format('r.%I',k),',' ORDER BY k),
          string_agg(format('%I=r.%I',k,k),',' ORDER BY k)
   INTO columns_list,values_list,assignments FROM jsonb_object_keys(d) k;
   IF columns_list IS NULL THEN CONTINUE; END IF;
   IF op->>'action'='insert' THEN
     IF tbl IN ('engenheiros_teams','aproar_web_settings') THEN RAISE EXCEPTION 'APROAR_INSERT_NOT_ALLOWED'; END IF;
     EXECUTE format('INSERT INTO public.%I (%s) SELECT %s FROM jsonb_populate_record(NULL::public.%I,$1) r RETURNING id',tbl,columns_list,values_list,tbl)
     INTO assigned USING d;
     mapping:=mapping||jsonb_build_object(op->>'id',assigned::text);
   ELSIF tbl='engenheiros_teams' THEN
     EXECUTE format('INSERT INTO engenheiros_teams(engenheiro,email_teams,ativo,atualizado_em) VALUES($1,$2,$3,now()) ON CONFLICT(engenheiro) DO UPDATE SET email_teams=excluded.email_teams,ativo=excluded.ativo,atualizado_em=now()')
       USING ident,d->>'email_teams',(d->>'ativo')::boolean;
   ELSE
     IF ident !~ '^[0-9]+$' THEN RAISE EXCEPTION 'APROAR_INVALID_ID'; END IF;
     EXECUTE format('UPDATE public.%I t SET %s FROM jsonb_populate_record(NULL::public.%I,$1) r WHERE t.id=$2::bigint',tbl,assignments,tbl) USING d,ident;
   END IF;
 END LOOP;
 -- ID map lets the browser replace temporary keys atomically after a successful save.
 result:=jsonb_build_object('ids',mapping,'version',aproar_web_fingerprint());
 INSERT INTO aproar_web_requests(id,actor,payload_hash,result) VALUES(request_id,actor_name,payload_digest,result);
 RETURN result;
END $$;
COMMIT;
