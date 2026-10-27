-- APROAR: extras independentes nao representam uma segunda convocatoria de presenca.
-- Mantem a verificacao de choque de horario para convocacoes normais.
-- Idempotente, sem alterar apontamentos, valores ou historico existentes.
CREATE OR REPLACE FUNCTION public.aproar_validar_sobreposicao_convocacao()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
DECLARE
  novo_turno text;
BEGIN
  novo_turno := aproar_turno_normalizado(NEW.turno, NEW.observacao);
  NEW.turno := novo_turno;

  -- Extras sao registradas em linha propria apenas para contabilidade.
  -- Nao podem bloquear a presenca do dia nem ser bloqueadas por ela.
  IF COALESCE(NEW.observacao, '') LIKE 'Extra independente ||APROAR_META|| %' THEN
    RETURN NEW;
  END IF;

  IF EXISTS(
    SELECT 1 FROM public.convocacoes c
    WHERE c.colaborador_id = NEW.colaborador_id
      AND c.data = NEW.data
      AND (TG_OP = 'INSERT' OR c.id <> NEW.id)
      -- A propria extra nao e convocacao concorrente.
      AND COALESCE(c.observacao, '') NOT LIKE 'Extra independente ||APROAR_META|| %'
      AND (
        aproar_turno_normalizado(c.turno,c.observacao) = novo_turno
        OR (aproar_turno_normalizado(c.turno,c.observacao) = 'Integral' AND novo_turno IN ('Manhã','Tarde'))
        OR (novo_turno = 'Integral' AND aproar_turno_normalizado(c.turno,c.observacao) IN ('Manhã','Tarde'))
      )
  ) THEN
    RAISE EXCEPTION 'APROAR_CONFLITO_TURNO: colaborador já possui convocação em turno sobreposto';
  END IF;
  RETURN NEW;
END
$function$;
