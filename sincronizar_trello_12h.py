import os
import json
import re
import unicodedata
from datetime import datetime, timezone

import requests
import psycopg
from psycopg.rows import dict_row

TRELLO_JSON_URL = "https://trello.com/b/TX8hGvmI.json"
LISTA_PRINCIPAL = "EM EXECUÇÃO"
DATABASE_URL = os.environ["DATABASE_URL"]


def normalizar(texto):
    if not texto:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    ).upper().strip()


def identificar_unidade(texto_bruto):
    texto = unicodedata.normalize(
        "NFKD", str(texto_bruto or "")
    ).encode("ASCII", "ignore").decode("utf-8").upper()

    if "APRL005" in texto or "MARACANAU" in texto:
        return "MARACANAÚ"
    if "APARTAMENTO 701" in texto or "PARTICULAR" in texto:
        return "PARTICULAR"
    if "SEBRAE" in texto:
        return "SEBRAE"
    if "UNIFOR" in texto:
        return "UNIFOR"
    if "IDALYA" in texto or "MATHEUS" in texto:
        return "IDALYA E MATHEUS"
    if "COLISEU" in texto:
        return "COLISEU"
    if "BARRA" in texto:
        return "BARRA DO CEARÁ"
    if "MUSEU" in texto:
        return "MUSEU"
    if "HORIZONTE" in texto:
        return "HORIZONTE"
    if "ESCRITORIO" in texto:
        return "ESCRITÓRIO"
    if (
        "CASA DA INDUSTRIA" in texto
        or "FIEC" in texto
        or " DR " in texto
        or "| SESI DR |" in texto
        or "| SESI DR" in texto
    ):
        return "FIEC"
    if "CENTRO" in texto:
        return "CENTRO"

    partes = str(texto_bruto or "").split("|")
    if len(partes) >= 2:
        return partes[1].strip().upper()
    return "GERAL"


def unidade_do_card(card):
    partes = [
        str(card.get("name") or ""),
        str(card.get("desc") or ""),
    ]
    for label in card.get("labels") or []:
        if isinstance(label, dict):
            partes.append(str(label.get("name") or ""))
    for item in card.get("customFieldItems") or []:
        if isinstance(item, dict):
            partes.append(json.dumps(item, ensure_ascii=False))
    return identificar_unidade(" | ".join(x for x in partes if x))


def main():
    r = requests.get(
        TRELLO_JSON_URL,
        timeout=(10, 45),
        headers={"User-Agent": "APROAR-Trello-Sync/1.0"},
    )
    r.raise_for_status()
    board = r.json()

    listas = board.get("lists") or []
    cards = board.get("cards") or []

    alvo_norm = normalizar(LISTA_PRINCIPAL)
    lista = next(
        (
            x for x in listas
            if not x.get("closed", False)
            and normalizar(x.get("name")) == alvo_norm
        ),
        None,
    )
    if not lista:
        lista = next(
            (
                x for x in listas
                if not x.get("closed", False)
                and alvo_norm in normalizar(x.get("name"))
            ),
            None,
        )
    if not lista:
        raise RuntimeError('Lista "EM EXECUÇÃO" não encontrada.')

    list_id = str(lista.get("id"))
    cards_exec = [
        c for c in cards
        if str(c.get("idList")) == list_id
        and not c.get("closed", False)
    ]

    inseridas = atualizadas = existentes = 0

    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                ALTER TABLE obras
                    ADD COLUMN IF NOT EXISTS trello_card_id TEXT,
                    ADD COLUMN IF NOT EXISTS trello_list_id TEXT,
                    ADD COLUMN IF NOT EXISTS trello_sync_em TIMESTAMPTZ
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_obras_trello_card_id
                ON obras (trello_card_id)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS trello_snapshot (
                    snapshot_id INTEGER PRIMARY KEY,
                    listas JSONB NOT NULL,
                    cards JSONB NOT NULL,
                    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    sincronizado_obras_em TIMESTAMPTZ,
                    ultima_tentativa_obras_em TIMESTAMPTZ,
                    ultimo_resultado_obras JSONB
                )
                """
            )
            cur.execute(
                """
                ALTER TABLE trello_snapshot
                    ADD COLUMN IF NOT EXISTS sincronizado_obras_em TIMESTAMPTZ,
                    ADD COLUMN IF NOT EXISTS ultima_tentativa_obras_em TIMESTAMPTZ,
                    ADD COLUMN IF NOT EXISTS ultimo_resultado_obras JSONB
                """
            )

            cur.execute(
                """
                SELECT id, nome, unidade, trello_card_id, trello_list_id
                  FROM obras
                """
            )
            obras = list(cur.fetchall() or [])

            por_card = {
                str(o.get("trello_card_id") or "").strip(): o
                for o in obras
                if str(o.get("trello_card_id") or "").strip()
            }
            por_nome_unidade = {}
            por_nome = {}
            for o in obras:
                nn = normalizar(o.get("nome"))
                un = normalizar(o.get("unidade"))
                if nn:
                    por_nome_unidade.setdefault((nn, un), []).append(o)
                    por_nome.setdefault(nn, []).append(o)

            for card in cards_exec:
                card_id = str(card.get("id") or "").strip()
                nome = str(card.get("name") or "").strip()
                if not card_id or not nome:
                    continue

                unidade = unidade_do_card(card)
                nn, un = normalizar(nome), normalizar(unidade)
                match = por_card.get(card_id)

                if not match:
                    candidatos = por_nome_unidade.get((nn, un), [])
                    if len(candidatos) == 1:
                        match = candidatos[0]

                if not match:
                    candidatos = por_nome.get(nn, [])
                    if len(candidatos) == 1:
                        match = candidatos[0]

                if match:
                    mudou = (
                        str(match.get("nome") or "").strip() != nome
                        or normalizar(match.get("unidade")) != un
                        or str(match.get("trello_card_id") or "").strip() != card_id
                        or str(match.get("trello_list_id") or "").strip() != list_id
                    )
                    cur.execute(
                        """
                        UPDATE obras
                           SET nome=%s,
                               unidade=%s,
                               trello_card_id=%s,
                               trello_list_id=%s,
                               trello_sync_em=NOW()
                         WHERE id=%s
                        """,
                        (nome, unidade, card_id, list_id, match["id"]),
                    )
                    match.update({
                        "nome": nome,
                        "unidade": unidade,
                        "trello_card_id": card_id,
                        "trello_list_id": list_id,
                    })
                    por_card[card_id] = match
                    if mudou:
                        atualizadas += 1
                    else:
                        existentes += 1
                else:
                    cur.execute(
                        """
                        INSERT INTO obras (
                            nome, unidade, trello_card_id,
                            trello_list_id, trello_sync_em
                        )
                        VALUES (%s,%s,%s,%s,NOW())
                        RETURNING id
                        """,
                        (nome, unidade, card_id, list_id),
                    )
                    novo = cur.fetchone()
                    registro = {
                        "id": novo["id"],
                        "nome": nome,
                        "unidade": unidade,
                        "trello_card_id": card_id,
                        "trello_list_id": list_id,
                    }
                    por_card[card_id] = registro
                    por_nome_unidade.setdefault((nn, un), []).append(registro)
                    por_nome.setdefault(nn, []).append(registro)
                    inseridas += 1

            resultado = {
                "sucesso": True,
                "lista": lista.get("name"),
                "total_cards": len(cards_exec),
                "inseridas": inseridas,
                "atualizadas": atualizadas,
                "existentes": existentes,
                "executado_em": datetime.now(timezone.utc).isoformat(),
            }

            cur.execute(
                """
                INSERT INTO trello_snapshot (
                    snapshot_id, listas, cards, atualizado_em,
                    sincronizado_obras_em,
                    ultima_tentativa_obras_em,
                    ultimo_resultado_obras
                )
                VALUES (
                    1, %s::jsonb, %s::jsonb, NOW(),
                    NOW(), NOW(), %s::jsonb
                )
                ON CONFLICT (snapshot_id) DO UPDATE SET
                    listas=EXCLUDED.listas,
                    cards=EXCLUDED.cards,
                    atualizado_em=NOW(),
                    sincronizado_obras_em=NOW(),
                    ultima_tentativa_obras_em=NOW(),
                    ultimo_resultado_obras=EXCLUDED.ultimo_resultado_obras
                """,
                (
                    json.dumps(listas, ensure_ascii=False),
                    json.dumps(cards, ensure_ascii=False),
                    json.dumps(resultado, ensure_ascii=False),
                ),
            )

        conn.commit()

    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
