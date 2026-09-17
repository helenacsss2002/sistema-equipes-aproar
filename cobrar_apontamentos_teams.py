import os
import sys
import html
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg
from psycopg.rows import dict_row
import requests

TZ = ZoneInfo("America/Fortaleza")
PLACEHOLDER_PREFIX = "A DEFINIR NO APONTAMENTO"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_COBRANCA_WEBHOOK_URL", "").strip()
PORTAL_URL = os.getenv(
    "PORTAL_SUPERVISOR_URL",
    "https://apontamentos-aproar.streamlit.app/?eng",
).strip()

RESPONSAVEIS_UNIDADES = {
    "EDUARDO": [
        "BARRA DO CEARÁ",
    ],
    "SOARES": [
        "HORIZONTE",
        "SEBRAE",
    ],
    "JOEL": [
        "COLISEU",
        "UNIFOR",
    ],
    "GABRIEL": [
        "FIEC",
        "PARANGABA",
        "APARTAMENTO 701",
    ],
    "VICTOR": [
        "CENTRO",
        "MUSEU",
    ],
    "NETO": [
        "MARACANAÚ",
    ],
}

SUPERVISORES_ATIVOS = set(
    RESPONSAVEIS_UNIDADES.keys()
)


def slot_atual() -> str:
    manual = os.getenv("COBRANCA_SLOT", "").strip()
    if manual in {"09:30", "15:00"}:
        return manual

    agora = datetime.now(TZ)
    # O workflow agenda uma execução de manhã e outra à tarde.
    # Mesmo se o GitHub atrasar alguns minutos, a execução continua no slot correto.
    return "09:30" if agora.hour < 12 else "15:00"


def garantir_estrutura(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS engenheiros_teams (
            engenheiro TEXT PRIMARY KEY,
            email_teams TEXT,
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS cobrancas_teams (
            id BIGSERIAL PRIMARY KEY,
            data_execucao DATE NOT NULL,
            horario TEXT NOT NULL,
            engenheiro TEXT NOT NULL,
            email_teams TEXT,
            qtd_pendentes INTEGER NOT NULL DEFAULT 0,
            mensagem TEXT,
            status TEXT NOT NULL DEFAULT 'ENVIADA',
            resposta_http INTEGER,
            enviado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (data_execucao, horario, engenheiro)
        )
        """
    )


def carregar_destinatarios(cur):
    # Gustavo permanece apenas no histórico, nunca em novos envios.
    cur.execute(
        """
        UPDATE engenheiros_teams
           SET ativo = FALSE,
               atualizado_em = NOW()
         WHERE UPPER(engenheiro) = 'GUSTAVO'
        """
    )

    cur.execute(
        """
        SELECT engenheiro, email_teams
        FROM engenheiros_teams
        WHERE ativo = TRUE
          AND COALESCE(TRIM(email_teams), '') <> ''
        ORDER BY engenheiro
        """
    )

    rows = cur.fetchall() or []

    return [
        row
        for row in rows
        if str(
            row["engenheiro"]
            or ""
        ).strip().upper()
        in SUPERVISORES_ATIVOS
    ]


def ja_enviado(cur, hoje, slot, engenheiro):
    cur.execute(
        """
        SELECT status
        FROM cobrancas_teams
        WHERE data_execucao = %s
          AND horario = %s
          AND UPPER(engenheiro) = UPPER(%s)
        LIMIT 1
        """,
        (hoje, slot, engenheiro),
    )
    row = cur.fetchone()
    return bool(row and str(row["status"]).upper() == "ENVIADA")


def carregar_pendentes(cur, engenheiro, hoje):
    """
    Cobra o supervisor responsável oficial pela UNIDADE.

    Isso evita depender de quem criou originalmente a convocação:
    a pendência da Barra vai para Eduardo; UNIFOR vai para Joel etc.
    """
    unidades = RESPONSAVEIS_UNIDADES.get(
        str(engenheiro).strip().upper(),
        [],
    )

    if not unidades:
        return []

    cur.execute(
        """
        SELECT
            c.id,
            c.data,
            c.turno,
            c.engenheiro,
            col.nome AS colaborador,
            o.unidade,
            o.nome AS obra_atual
        FROM convocacoes c
        JOIN colaboradores col
          ON col.id = c.colaborador_id
        JOIN obras o
          ON o.id = c.obra_id
        WHERE c.data < %s
          AND UPPER(COALESCE(o.nome, '')) LIKE UPPER(%s)
          AND UPPER(TRIM(COALESCE(o.unidade, ''))) = ANY(%s)
        ORDER BY
            c.data ASC,
            o.unidade ASC,
            col.nome ASC
        """,
        (
            hoje,
            f"{PLACEHOLDER_PREFIX}%",
            [
                str(u).strip().upper()
                for u in unidades
            ],
        ),
    )

    return cur.fetchall() or []


def montar_mensagem(engenheiro, pendentes, slot):
    grupos = defaultdict(int)
    for item in pendentes:
        grupos[(item["data"], item.get("unidade") or "SEM UNIDADE")] += 1

    linhas = []
    for (data_ref, unidade), qtd in sorted(grupos.items()):
        data_txt = data_ref.strftime("%d/%m")
        sufixo = "colaborador" if qtd == 1 else "colaboradores"
        linhas.append(
            f"• {data_txt} · {html.escape(str(unidade))} · {qtd} {sufixo}"
        )

    max_linhas = 8
    linhas_visiveis = linhas[:max_linhas]
    if len(linhas) > max_linhas:
        linhas_visiveis.append(f"• + {len(linhas) - max_linhas} grupo(s) pendente(s)")

    etapa = "1ª cobrança do dia" if slot == "09:30" else "2ª cobrança do dia"
    total = len(pendentes)
    termo = "apontamento atrasado" if total == 1 else "apontamentos atrasados"

    corpo_linhas = "<br>".join(linhas_visiveis)

    return (
        f"<b>APROAR · Apontamentos pendentes</b><br><br>"
        f"{html.escape(engenheiro.title())}, existem <b>{total} {termo}</b> "
        f"que ainda precisam ser regularizados.<br>"
        f"<span style='color:#6b7280'>{etapa}</span><br><br>"
        f"{corpo_linhas}<br><br>"
        f"Favor regularizar no <b>Portal do Supervisor</b>: "
        f"<a href='{html.escape(PORTAL_URL)}'>abrir apontamentos</a>."
    )


def registrar_resultado(cur, hoje, slot, engenheiro, email, qtd, mensagem, status, http_code):
    cur.execute(
        """
        INSERT INTO cobrancas_teams (
            data_execucao,
            horario,
            engenheiro,
            email_teams,
            qtd_pendentes,
            mensagem,
            status,
            resposta_http,
            enviado_em
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        ON CONFLICT (data_execucao, horario, engenheiro)
        DO UPDATE SET
            email_teams = EXCLUDED.email_teams,
            qtd_pendentes = EXCLUDED.qtd_pendentes,
            mensagem = EXCLUDED.mensagem,
            status = EXCLUDED.status,
            resposta_http = EXCLUDED.resposta_http,
            enviado_em = NOW()
        """,
        (
            hoje,
            slot,
            engenheiro,
            email,
            qtd,
            mensagem,
            status,
            http_code,
        ),
    )


def enviar_teams(email, engenheiro, slot, pendentes):
    mensagem = montar_mensagem(engenheiro, pendentes, slot)
    payload = {
        "recipient": email,
        "engineer": engenheiro,
        "slot": slot,
        "pendingCount": len(pendentes),
        "message": mensagem,
        "portalUrl": PORTAL_URL,
    }

    resposta = requests.post(
        TEAMS_WEBHOOK_URL,
        json=payload,
        timeout=25,
    )

    return resposta.status_code, mensagem, resposta.text[:500]


def main():
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL não configurada.")
    if not TEAMS_WEBHOOK_URL:
        raise SystemExit("TEAMS_COBRANCA_WEBHOOK_URL não configurada.")

    agora = datetime.now(TZ)
    hoje = agora.date()
    slot = slot_atual()

    print(f"[APROAR] Cobrança Teams · {hoje} · {slot}")

    enviados = 0
    sem_pendencia = 0
    pulados = 0
    erros = 0

    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            garantir_estrutura(cur)
            conn.commit()

            destinatarios = carregar_destinatarios(cur)

            if not destinatarios:
                print("Nenhum engenheiro ativo com e-mail Teams configurado.")
                return 0

            for cfg in destinatarios:
                engenheiro = str(cfg["engenheiro"] or "").strip().upper()
                email = str(cfg["email_teams"] or "").strip()

                if ja_enviado(cur, hoje, slot, engenheiro):
                    print(f"- {engenheiro}: cobrança deste horário já enviada; pulando.")
                    pulados += 1
                    continue

                pendentes = carregar_pendentes(cur, engenheiro, hoje)

                if not pendentes:
                    print(f"- {engenheiro}: sem apontamentos atrasados.")
                    sem_pendencia += 1
                    continue

                try:
                    http_code, mensagem, resposta_texto = enviar_teams(
                        email,
                        engenheiro,
                        slot,
                        pendentes,
                    )

                    sucesso = 200 <= http_code < 300
                    status = "ENVIADA" if sucesso else "ERRO"

                    registrar_resultado(
                        cur,
                        hoje,
                        slot,
                        engenheiro,
                        email,
                        len(pendentes),
                        mensagem,
                        status,
                        http_code,
                    )
                    conn.commit()

                    if sucesso:
                        enviados += 1
                        print(
                            f"- {engenheiro}: enviada para {email} "
                            f"({len(pendentes)} pendente(s))."
                        )
                    else:
                        erros += 1
                        print(
                            f"- {engenheiro}: ERRO HTTP {http_code}: {resposta_texto}"
                        )

                except Exception as exc:
                    conn.rollback()
                    erros += 1

                    try:
                        registrar_resultado(
                            cur,
                            hoje,
                            slot,
                            engenheiro,
                            email,
                            len(pendentes),
                            montar_mensagem(engenheiro, pendentes, slot),
                            "ERRO",
                            None,
                        )
                        conn.commit()
                    except Exception:
                        conn.rollback()

                    print(f"- {engenheiro}: falha no envio: {exc}", file=sys.stderr)

    print(
        f"Resumo: {enviados} enviada(s), {sem_pendencia} sem pendência, "
        f"{pulados} já enviada(s), {erros} erro(s)."
    )

    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
