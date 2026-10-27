-- APROAR 2026-10-27: dados de links do SharePoint foram gravados como unidades.
-- Apenas tres obras comprovadas sem apontamentos/custos historicos.
-- Preserva titulo, Trello, IDs, e cria auditoria antes/depois para cada alteracao.
-- A unidade definitiva dessas obras sera escolhida pela Controladoria.
DO $correcao_unidades$
DECLARE
  item public.obras%ROWTYPE;
  expected_name text;
  old_row jsonb;
  updated_row jsonb;
BEGIN
  FOR item IN SELECT * FROM public.obras WHERE id IN (271,290,291) ORDER BY id FOR UPDATE LOOP
    expected_name:=CASE item.id
      WHEN 271 THEN 'OBRA APR4C008 - ALMOXARFIADO GERAL - HOSPITAL SÃO CARLOS'
      WHEN 290 THEN 'OBRA APR4C061 - APTO SOGRO DR. PAULO'
      WHEN 291 THEN 'OBRA APR4C052.3 - CORREÇÃO DA JUNTA DE DILATAÇÃO - ED. IMPERATOR'
    END;
    IF item.nome IS DISTINCT FROM expected_name
      THEN RAISE EXCEPTION 'Obra % alterada: correcao cancelada',item.id; END IF;
    IF item.unidade='NÃO IDENTIFICADA' AND item.trello_unidade_manual THEN CONTINUE; END IF;
    IF item.unidade NOT ILIKE '%sharepoint.com%'
      THEN RAISE EXCEPTION 'Unidade % nao contem link verificado: correcao cancelada',item.id; END IF;
    IF EXISTS(SELECT 1 FROM public.convocacoes WHERE obra_id=item.id)
      OR EXISTS(SELECT 1 FROM public.servicos_apontamento WHERE obra_id=item.id::text)
      OR EXISTS(SELECT 1 FROM public.conflitos_convocacao WHERE unidade_original=item.unidade OR unidade_tentativa=item.unidade)
      THEN RAISE EXCEPTION 'Obra % possui historico: correcao cancelada',item.id; END IF;

    old_row:=to_jsonb(item);
    UPDATE public.obras SET unidade='NÃO IDENTIFICADA',trello_unidade_manual=true
      WHERE id=item.id;
    SELECT to_jsonb(o) INTO updated_row FROM public.obras o WHERE o.id=item.id;
    INSERT INTO public.auditoria(entidade,entidade_id,acao,usuario,ocorrido_em,antes,depois,contexto)
    VALUES('obras',item.id::text,'CORRIGIR_UNIDADE_COM_LINK_NO_LUGAR_DO_NOME',
      'CORRECAO_TECNICA_SOLICITADA',now(),old_row,updated_row,
      jsonb_build_object('origem','Campo unidade preenchido com URL do SharePoint',
       'novaUnidade','NÃO IDENTIFICADA','unidadeDefinitiva','Pendente de escolha pela Controladoria',
       'historicoPreservado',true,'bloquearReatribuicaoAutomaticaTrello',true));
  END LOOP;
  -- Bloqueia novas insercoes ou atualizacoes com URLs no campo unidade,
  -- inclusive sincronizacoes externas; nunca trunca informacoes silenciosamente.
  IF NOT EXISTS (SELECT 1 FROM pg_constraint
    WHERE conrelid='public.obras'::regclass AND conname='aproar_obras_unidade_legivel_chk') THEN
    ALTER TABLE public.obras ADD CONSTRAINT aproar_obras_unidade_legivel_chk
      CHECK (
        char_length(btrim(unidade)) BETWEEN 1 AND 80
        AND unidade !~* '(https?://|www[.]|sharepoint|link[[:space:]]+para[[:space:]]+acesso)'
      );
  END IF;
END
$correcao_unidades$;
