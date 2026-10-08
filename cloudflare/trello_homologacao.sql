-- APROAR: estrutura aditiva para importar obras do Trello na HOMOLOGACAO.
-- Executar SOMENTE na branch aproar-homologacao. Nao executar na producao.
BEGIN;
ALTER TABLE obras
 ADD COLUMN IF NOT EXISTS trello_card_id text,
 ADD COLUMN IF NOT EXISTS trello_list_id text,
 ADD COLUMN IF NOT EXISTS trello_sync_em timestamptz,
 ADD COLUMN IF NOT EXISTS trello_unidade_manual boolean NOT NULL DEFAULT false;
CREATE INDEX IF NOT EXISTS idx_obras_trello_card_id ON obras(trello_card_id);
CREATE TABLE IF NOT EXISTS trello_snapshot (
 snapshot_id integer PRIMARY KEY,
 listas jsonb NOT NULL,
 cards jsonb NOT NULL,
 atualizado_em timestamptz NOT NULL DEFAULT now(),
 sincronizado_obras_em timestamptz,
 ultima_tentativa_obras_em timestamptz,
 ultimo_resultado_obras jsonb
);
ALTER TABLE trello_snapshot
 ADD COLUMN IF NOT EXISTS sincronizado_obras_em timestamptz,
 ADD COLUMN IF NOT EXISTS ultima_tentativa_obras_em timestamptz,
 ADD COLUMN IF NOT EXISTS ultimo_resultado_obras jsonb;
COMMIT;
