-- Migração aditiva e reversível de compatibilidade para avulsos eventuais.
-- Nenhuma linha é apagada nem alterada; mantém a FK para colaboradores cadastrados.
-- Para avulsos, colaborador_id fica NULL e os dados do lançamento permanecem
-- como snapshot versionado em convocacoes.observacao (APROAR_META.avulso_eventual).
-- apontamentos.colaborador_id é text e recebe o ID virtual único do lançamento.
BEGIN;
ALTER TABLE public.convocacoes ALTER COLUMN colaborador_id DROP NOT NULL;
COMMIT;
