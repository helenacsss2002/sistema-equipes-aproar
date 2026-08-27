# SISTEMA DE EQUIPES, APONTAMENTOS E MEDIÇÕES — APROAR
# Projeto oficial: Streamlit + Supabase/PostgreSQL + Trello

import io
import re
import time
import unicodedata
from datetime import date, datetime
from calendar import month_name

import pandas as pd
import psycopg2
import requests
import streamlit as st


st.set_page_config(
    page_title="Equipes e Medições | APROAR",
    page_icon="🏗️",
    layout="wide",
)

FUSO_LABEL = "America/Fortaleza"
INTERVALO_TRELLO_SEGUNDOS = 120

MESES_PT = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO",
}

FRENTES = [
    "PINTURA",
    "ALVENARIA / PEDREIROS",
    "ELÉTRICA",
    "HIDRÁULICA",
    "PISO / REVESTIMENTO",
    "FORRO / GESSO",
    "COBERTURA",
    "IMPERMEABILIZAÇÃO",
    "SERRALHERIA",
    "MARCENARIA / CARPINTARIA",
    "APOIO / SERVIÇOS GERAIS",
    "GESTÃO DE CAMPO",
    "OUTROS",
]

STATUS_APONTAMENTO = ["Pendente", "Presença", "Falta", "Atestado"]


# ============================================================
# UTILIDADES
# ============================================================

def normalizar(txt):
    txt = "" if txt is None else str(txt)
    txt = "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", txt).strip().upper()


def inferir_frente(funcao):
    f = normalizar(funcao)
    regras = [
        (["PINTOR", "PINTURA"], "PINTURA"),
        (["PEDREIRO", "ALVENAR"], "ALVENARIA / PEDREIROS"),
        (["ELETRIC", "ELETROT", "ELETROMEC"], "ELÉTRICA"),
        (["ENCANADOR", "HIDRAUL", "BOMBEIRO"], "HIDRÁULICA"),
        (["AZULEJ", "LADRILH", "CERAM", "REVEST"], "PISO / REVESTIMENTO"),
        (["GESS", "DRYWALL", "FORRO"], "FORRO / GESSO"),
        (["TELHAD", "TELHEIR", "COBERT"], "COBERTURA"),
        (["IMPERMEABIL"], "IMPERMEABILIZAÇÃO"),
        (["SERRALH", "SOLDADOR"], "SERRALHERIA"),
        (["CARPINTEIR", "MARCENEIR"], "MARCENARIA / CARPINTARIA"),
        (["MESTRE", "ENCARREG", "SUPERVIS", "LIDER"], "GESTÃO DE CAMPO"),
        (["SERVENTE", "AJUDANTE", "AUXILIAR", "SERVICOS GERAIS"], "APOIO / SERVIÇOS GERAIS"),
    ]
    for termos, frente in regras:
        if any(t in f for t in termos):
            return frente
    return "OUTROS"


def competencia_date(ano, mes):
    return date(int(ano), int(mes), 1)


def nome_lista_medicao(ano, mes):
    return f"MEDIÇÃO {MESES_PT[int(mes)]} {int(ano)}"


def dinheiro(v):
    try:
        return f"R$ {float(v or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


# ============================================================
# SUPABASE / POSTGRESQL
# ============================================================

def db_config():
    try:
        c = st.secrets["connections"]["postgresql"]
        return {
            "host": c["host"],
            "port": int(c.get("port", 6543)),
            "dbname": c.get("database", "postgres"),
            "user": c["username"],
            "password": c["password"],
            "sslmode": c.get("sslmode", "require"),
            "connect_timeout": 12,
        }
    except Exception:
        return None


def db_available():
    return db_config() is not None


def get_conn():
    cfg = db_config()
    if not cfg:
        raise RuntimeError("Supabase ainda não configurado nos Secrets.")
    return psycopg2.connect(**cfg)


def query_df(sql, params=None):
    with get_conn() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def query_one(sql, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()


def execute(sql, params=None, fetchone=False):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone() if fetchone else None
        conn.commit()
        return row


def execute_many(sql, rows):
    with get_conn() as conn:
        with conn.cursor() as cur:
            for row in rows:
                cur.execute(sql, row)
        conn.commit()


def tabelas_ok():
    if not db_available():
        return False
    try:
        row = query_one("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema='public'
              AND table_name IN (
                'colaboradores','obras_trello','convocacoes',
                'convocacao_itens','apontamentos','medicoes','medicao_itens'
              )
        """)
        return bool(row and row[0] == 7)
    except Exception:
        return False


# ============================================================
# TRELLO
# ============================================================

def trello_config():
    try:
        c = st.secrets["trello"]
        return {
            "key": c["key"],
            "token": c["token"],
            "board_id": c.get("board_id", "67503e37f48a3a5c8500025e"),
        }
    except Exception:
        return None


def trello_get(endpoint, params=None):
    cfg = trello_config()
    if not cfg:
        raise RuntimeError("Trello ainda não configurado nos Secrets.")
    p = {"key": cfg["key"], "token": cfg["token"]}
    p.update(params or {})
    r = requests.get(
        f"https://api.trello.com/1/{endpoint.lstrip('/')}",
        params=p,
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def parse_card_name(nome):
    original = str(nome or "").strip()

    # Padrão principal:
    # OBRA 2450.1 - SERVIÇO | UNIDADE | PIPE
    m = re.match(
        r"^\s*OBRA\s+([A-Za-z0-9.\-]+)\s*-\s*(.*?)\s*\|\s*(.*?)\s*\|\s*([0-9]+)\s*$",
        original,
        flags=re.I,
    )
    if m:
        return {
            "numero_obra": m.group(1).strip(),
            "titulo": m.group(2).strip(),
            "unidade": m.group(3).strip(),
            "pipe": m.group(4).strip(),
        }

    # Tenta extrair obra e PIPE mesmo em exceções.
    obra = None
    pipe = None
    mo = re.search(r"\bOBRA\s+([A-Za-z0-9.\-]+)", original, flags=re.I)
    mp = re.search(r"\bPIPE\s*:?\s*([0-9]+)", original, flags=re.I)
    if not mp:
        final = re.search(r"\|\s*([0-9]{7,})\s*$", original)
        mp = final

    if mo:
        obra = mo.group(1).strip()
    if mp:
        pipe = mp.group(1).strip()

    partes = [p.strip() for p in original.split("|")]
    titulo = original
    unidade = None

    if len(partes) >= 2:
        titulo = partes[0]
        if titulo.upper().startswith("OBRA") and " - " in titulo:
            titulo = titulo.split(" - ", 1)[1].strip()
        if len(partes) >= 3:
            unidade = partes[-2] if not partes[-2].upper().startswith("PIPE") else None

    return {
        "numero_obra": obra,
        "titulo": titulo,
        "unidade": unidade,
        "pipe": pipe,
    }


def classificar_origem(labels, nome):
    texto = " ".join([str(x.get("name", "")) for x in labels or []] + [str(nome)])
    t = normalizar(texto)

    if "QUARTEIR" in t or "SUBCONTRAT" in t or "TERCEIROS X APROAR" in t:
        return "QUARTEIRIZADOS"
    if "UNIFOR" in t:
        return "UNIFOR"
    if "NOVOS CLIENTES" in t or "NOVO CLIENTE" in t:
        return "NOVOS CLIENTES"
    if "HOSPITAL SAO CARLOS" in t:
        return "HOSPITAL SÃO CARLOS"
    if "FIEC" in t or any(x in t for x in ["SESI", "SENAI", "IEL", "CASA DA INDUSTRIA", "MUSEU DA INDUSTRIA"]):
        return "FIEC"
    return "OUTROS"


def sincronizar_quadro_trello():
    """Espelha todos os cartões abertos do quadro no Supabase."""
    cfg = trello_config()
    if not cfg:
        raise RuntimeError("Configure [trello] nos Secrets.")

    listas = trello_get(
        f"boards/{cfg['board_id']}/lists",
        {"filter": "open", "fields": "id,name"},
    )
    lista_map = {x["id"]: x["name"] for x in listas}

    cards = trello_get(
        f"boards/{cfg['board_id']}/cards",
        {
            "filter": "open",
            "fields": "id,name,idList,url,shortLink,dateLastActivity,desc",
            "labels": "all",
        },
    )

    agora = datetime.now()
    with get_conn() as conn:
        with conn.cursor() as cur:
            for card in cards:
                p = parse_card_name(card.get("name"))
                labels = card.get("labels") or []
                labels_txt = ", ".join([x.get("name", "") for x in labels if x.get("name")])
                cur.execute(
                    """
                    INSERT INTO obras_trello (
                        trello_card_id, nome_original, numero_obra, titulo, unidade, pipe,
                        lista_trello, origem, etiquetas, url_trello,
                        data_atividade_trello, sincronizado_em, ativo
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)
                    ON CONFLICT (trello_card_id) DO UPDATE SET
                        nome_original=EXCLUDED.nome_original,
                        numero_obra=EXCLUDED.numero_obra,
                        titulo=EXCLUDED.titulo,
                        unidade=EXCLUDED.unidade,
                        pipe=EXCLUDED.pipe,
                        lista_trello=EXCLUDED.lista_trello,
                        origem=EXCLUDED.origem,
                        etiquetas=EXCLUDED.etiquetas,
                        url_trello=EXCLUDED.url_trello,
                        data_atividade_trello=EXCLUDED.data_atividade_trello,
                        sincronizado_em=EXCLUDED.sincronizado_em,
                        ativo=TRUE
                    """,
                    (
                        card["id"],
                        card.get("name"),
                        p["numero_obra"],
                        p["titulo"],
                        p["unidade"],
                        p["pipe"],
                        lista_map.get(card.get("idList")),
                        classificar_origem(labels, card.get("name")),
                        labels_txt,
                        card.get("url"),
                        card.get("dateLastActivity"),
                        agora,
                    ),
                )
        conn.commit()
    return len(cards)


def sincronizar_medicao(ano, mes):
    """Sincroniza apenas a lista mensal e preserva histórico por competência."""
    cfg = trello_config()
    if not cfg:
        raise RuntimeError("Configure [trello] nos Secrets.")

    alvo = nome_lista_medicao(ano, mes)
    comp = competencia_date(ano, mes)

    listas = trello_get(
        f"boards/{cfg['board_id']}/lists",
        {"filter": "open", "fields": "id,name"},
    )

    lista = next((x for x in listas if normalizar(x["name"]) == normalizar(alvo)), None)
    if not lista:
        raise RuntimeError(f"Lista '{alvo}' não encontrada no Trello.")

    cards = trello_get(
        f"lists/{lista['id']}/cards",
        {
            "filter": "open",
            "fields": "id,name,url,shortLink,dateLastActivity,desc",
            "labels": "all",
        },
    )

    agora = datetime.now()

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Cabeçalho da competência
            cur.execute(
                """
                INSERT INTO medicoes (competencia, nome_lista_trello, ultima_sincronizacao)
                VALUES (%s,%s,%s)
                ON CONFLICT (competencia) DO UPDATE SET
                    nome_lista_trello=EXCLUDED.nome_lista_trello,
                    ultima_sincronizacao=EXCLUDED.ultima_sincronizacao
                RETURNING id
                """,
                (comp, alvo, agora),
            )
            medicao_id = cur.fetchone()[0]

            # Primeiro marca os antigos como ausentes. Os atuais voltam para TRUE.
            cur.execute(
                "UPDATE medicao_itens SET presente_na_lista=FALSE WHERE medicao_id=%s",
                (medicao_id,),
            )

            for card in cards:
                p = parse_card_name(card.get("name"))
                labels = card.get("labels") or []
                origem = classificar_origem(labels, card.get("name"))
                labels_txt = ", ".join([x.get("name", "") for x in labels if x.get("name")])

                # Atualiza também o espelho geral de obras.
                cur.execute(
                    """
                    INSERT INTO obras_trello (
                        trello_card_id, nome_original, numero_obra, titulo, unidade, pipe,
                        lista_trello, origem, etiquetas, url_trello,
                        data_atividade_trello, sincronizado_em, ativo
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)
                    ON CONFLICT (trello_card_id) DO UPDATE SET
                        nome_original=EXCLUDED.nome_original,
                        numero_obra=EXCLUDED.numero_obra,
                        titulo=EXCLUDED.titulo,
                        unidade=EXCLUDED.unidade,
                        pipe=EXCLUDED.pipe,
                        lista_trello=EXCLUDED.lista_trello,
                        origem=EXCLUDED.origem,
                        etiquetas=EXCLUDED.etiquetas,
                        url_trello=EXCLUDED.url_trello,
                        data_atividade_trello=EXCLUDED.data_atividade_trello,
                        sincronizado_em=EXCLUDED.sincronizado_em,
                        ativo=TRUE
                    """,
                    (
                        card["id"], card.get("name"), p["numero_obra"], p["titulo"],
                        p["unidade"], p["pipe"], alvo, origem, labels_txt,
                        card.get("url"), card.get("dateLastActivity"), agora,
                    ),
                )

                cur.execute(
                    """
                    INSERT INTO medicao_itens (
                        medicao_id, trello_card_id, nome_original, numero_obra, titulo,
                        unidade, pipe, origem, etiquetas, url_trello,
                        presente_na_lista, sincronizado_em
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE,%s)
                    ON CONFLICT (medicao_id, trello_card_id) DO UPDATE SET
                        nome_original=EXCLUDED.nome_original,
                        numero_obra=EXCLUDED.numero_obra,
                        titulo=EXCLUDED.titulo,
                        unidade=EXCLUDED.unidade,
                        pipe=EXCLUDED.pipe,
                        origem=EXCLUDED.origem,
                        etiquetas=EXCLUDED.etiquetas,
                        url_trello=EXCLUDED.url_trello,
                        presente_na_lista=TRUE,
                        sincronizado_em=EXCLUDED.sincronizado_em
                    """,
                    (
                        medicao_id, card["id"], card.get("name"), p["numero_obra"],
                        p["titulo"], p["unidade"], p["pipe"], origem,
                        labels_txt, card.get("url"), agora,
                    ),
                )

        conn.commit()

    return len(cards), alvo


# ============================================================
# COLABORADORES
# ============================================================

def ler_planilha(upload):
    raw = upload.getvalue()
    nome = upload.name.lower()
    if nome.endswith(".xls"):
        return pd.read_excel(io.BytesIO(raw), engine="xlrd")
    if nome.endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(raw), engine="openpyxl")
    return pd.read_csv(io.BytesIO(raw), sep=None, engine="python")


def importar_colaboradores(df, col_nome, col_funcao):
    novos = atualizados = ignorados = 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            for _, r in df.iterrows():
                nome = r.get(col_nome)
                funcao = r.get(col_funcao)
                if pd.isna(nome) or not str(nome).strip():
                    ignorados += 1
                    continue
                nome = str(nome).strip().upper()
                funcao = "NÃO INFORMADA" if pd.isna(funcao) else str(funcao).strip()
                frente = inferir_frente(funcao)

                cur.execute("SELECT id FROM colaboradores WHERE nome=%s", (nome,))
                existe = cur.fetchone()
                if existe:
                    cur.execute(
                        """
                        UPDATE colaboradores
                        SET funcao_base=%s, frente_base=%s, ativo=TRUE, atualizado_em=NOW()
                        WHERE id=%s
                        """,
                        (funcao, frente, existe[0]),
                    )
                    atualizados += 1
                else:
                    cur.execute(
                        """
                        INSERT INTO colaboradores (nome, funcao_base, frente_base, ativo)
                        VALUES (%s,%s,%s,TRUE)
                        """,
                        (nome, funcao, frente),
                    )
                    novos += 1
        conn.commit()
    return novos, atualizados, ignorados


# ============================================================
# INTERFACE
# ============================================================

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.25rem; padding-bottom: 2rem;}
      div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 12px;
        padding: 10px 12px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏗️ Controle de Equipes e Medições")
st.caption("APROAR Engenharia • banco em nuvem • Trello sincronizado")


# ============================================================
# TELA DE CONFIGURAÇÃO
# ============================================================

if not db_available():
    st.error("O Supabase ainda não está configurado nos Secrets deste app.")
    st.code(
        """[connections.postgresql]
dialect = "postgresql"
host = "SEU_HOST_DO_TRANSACTION_POOLER"
port = "6543"
database = "postgres"
username = "SEU_USUARIO"
password = "SUA_SENHA"
sslmode = "require"

[trello]
key = "SUA_TRELLO_KEY"
token = "SEU_TRELLO_TOKEN"
board_id = "67503e37f48a3a5c8500025e"
""",
        language="toml",
    )
    st.stop()

if not tabelas_ok():
    st.error("O banco está conectado, mas as tabelas do projeto ainda não existem.")
    st.info("Abra o SQL Editor do Supabase e execute o arquivo `schema.sql` deste projeto.")
    st.stop()


# ============================================================
# SINCRONIZAÇÃO LEVE EM BACKGROUND
# ============================================================

if "_trello_sync_ts" not in st.session_state:
    st.session_state["_trello_sync_ts"] = time.time()
    st.session_state["_trello_sync_status"] = "Aguardando primeiro ciclo"

if trello_config() and hasattr(st, "fragment"):
    @st.fragment(run_every="30s")
    def _trello_background():
        decorrido = time.time() - st.session_state.get("_trello_sync_ts", 0)
        if decorrido >= INTERVALO_TRELLO_SEGUNDOS:
            try:
                qtd = sincronizar_quadro_trello()
                st.session_state["_trello_sync_ts"] = time.time()
                st.session_state["_trello_sync_status"] = (
                    f"{qtd} cartões • {datetime.now().strftime('%H:%M:%S')}"
                )
            except Exception as exc:
                # Falha externa não derruba o restante do sistema.
                st.session_state["_trello_sync_status"] = f"Falha Trello: {type(exc).__name__}"
    _trello_background()


with st.sidebar:
    st.header("⚙️ Operações")
    usuario = st.text_input(
        "Engenheiro / supervisor",
        value=st.session_state.get("usuario", ""),
        placeholder="Nome do responsável",
    )
    st.session_state["usuario"] = usuario

    menu = st.radio(
        "Menu",
        ["Visão Geral", "Colaboradores", "Convocação", "Apontamentos", "Medições"],
    )

    st.divider()
    st.caption("🔄 Trello")
    st.caption(st.session_state.get("_trello_sync_status", "Não sincronizado"))

    if trello_config():
        if st.button("Sincronizar Trello agora", use_container_width=True):
            try:
                with st.spinner("Sincronizando quadro..."):
                    qtd = sincronizar_quadro_trello()
                st.session_state["_trello_sync_ts"] = time.time()
                st.session_state["_trello_sync_status"] = (
                    f"{qtd} cartões • {datetime.now().strftime('%H:%M:%S')}"
                )
                st.success(f"{qtd} cartões sincronizados.")
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao sincronizar: {exc}")
    else:
        st.warning("Credenciais Trello ainda não configuradas.")


# ============================================================
# VISÃO GERAL
# ============================================================

if menu == "Visão Geral":
    st.subheader("Visão Geral")

    c1 = query_one("SELECT COUNT(*) FROM colaboradores WHERE ativo=TRUE")[0]
    c2 = query_one("""
        SELECT COUNT(*) FROM apontamentos WHERE status='Pendente'
    """)[0]
    c3 = query_one("""
        SELECT COUNT(*) FROM obras_trello WHERE ativo=TRUE
    """)[0]
    c4 = query_one("""
        SELECT COUNT(*) FROM medicao_itens mi
        JOIN medicoes m ON m.id=mi.medicao_id
        WHERE m.competencia=date_trunc('month', CURRENT_DATE)::date
          AND mi.presente_na_lista=TRUE
    """)[0]

    a, b, c, d = st.columns(4)
    a.metric("Colaboradores ativos", c1)
    b.metric("Apontamentos pendentes", c2)
    c.metric("Cartões/obras Trello", c3)
    d.metric("Medição do mês atual", c4)

    st.markdown("### Pendências de apontamento")
    pend = query_df(
        """
        SELECT
          cv.data AS "Data",
          COALESCE(o.numero_obra,'—') AS "Obra",
          ci.nome_exibicao AS "Colaborador",
          ci.frente AS "Frente",
          a.status AS "Status",
          cv.engenheiro AS "Engenheiro"
        FROM apontamentos a
        JOIN convocacao_itens ci ON ci.id=a.convocacao_item_id
        JOIN convocacoes cv ON cv.id=ci.convocacao_id
        LEFT JOIN obras_trello o ON o.trello_card_id=cv.trello_card_id
        WHERE a.status='Pendente'
        ORDER BY cv.data DESC, ci.frente, ci.nome_exibicao
        LIMIT 100
        """
    )
    if pend.empty:
        st.info("Sem apontamentos pendentes.")
    else:
        st.dataframe(pend, use_container_width=True, hide_index=True)


# ============================================================
# COLABORADORES
# ============================================================

elif menu == "Colaboradores":
    st.subheader("Colaboradores")
    st.caption("A função da base define o agrupamento inicial da convocação.")

    with st.expander("📥 Importar base de empregados", expanded=True):
        arq = st.file_uploader("Empregados (.xls, .xlsx ou .csv)", type=["xls", "xlsx", "csv"])
        if arq:
            try:
                df = ler_planilha(arq)
                st.dataframe(df.head(10), use_container_width=True, hide_index=True)
                colunas = list(df.columns)
                a, b = st.columns(2)
                cn = a.selectbox("Coluna do nome", colunas)
                cf = b.selectbox("Coluna da função/cargo", colunas)
                if st.button("Importar / atualizar base", type="primary"):
                    n, u, i = importar_colaboradores(df, cn, cf)
                    st.success(f"{n} novos • {u} atualizados • {i} ignorados")
                    st.rerun()
            except Exception as exc:
                st.error(f"Não consegui ler essa planilha: {exc}")

    base = query_df(
        """
        SELECT id, nome AS "Nome", funcao_base AS "Função",
               frente_base AS "Frente", ativo AS "Ativo"
        FROM colaboradores
        ORDER BY frente_base, nome
        """
    )
    st.dataframe(base, use_container_width=True, hide_index=True)


# ============================================================
# CONVOCAÇÃO
# ============================================================

elif menu == "Convocação":
    st.subheader("Nova convocação")
    st.caption("Escolha somente as frentes necessárias e monte cada equipe.")

    obras = query_df(
        """
        SELECT trello_card_id, numero_obra, titulo, unidade, lista_trello
        FROM obras_trello
        WHERE ativo=TRUE
          AND (
            UPPER(COALESCE(lista_trello,'')) LIKE '%EXECU%'
            OR UPPER(COALESCE(lista_trello,'')) LIKE '%AGUARDANDO EXECU%'
          )
        ORDER BY unidade, numero_obra, titulo
        """
    )

    if obras.empty:
        st.warning("Ainda não há obras em execução sincronizadas do Trello.")
    else:
        data_conv = st.date_input("Data", value=date.today())
        engenheiro = st.text_input(
            "Engenheiro responsável",
            value=st.session_state.get("usuario", ""),
        )

        obra_labels = {}
        for r in obras.itertuples():
            label = f"OBRA {r.numero_obra or '—'} — {r.titulo} | {r.unidade or '—'}"
            obra_labels[label] = r.trello_card_id
        obra_sel = st.selectbox("Obra / serviço", list(obra_labels))
        trello_card_id = obra_labels[obra_sel]

        colaboradores = query_df(
            """
            SELECT id, nome, funcao_base, frente_base
            FROM colaboradores
            WHERE ativo=TRUE
            ORDER BY frente_base, nome
            """
        )

        frentes_disp = colaboradores["frente_base"].dropna().unique().tolist()
        frentes_sel = st.multiselect(
            "Frentes necessárias",
            frentes_disp,
            placeholder="Ex.: PINTURA, ELÉTRICA...",
        )

        equipe = []
        for frente in frentes_sel:
            grupo = colaboradores[colaboradores["frente_base"] == frente]
            with st.container(border=True):
                st.markdown(f"#### {frente}")
                labels = {
                    f"{r.nome} — {r.funcao_base}": (int(r.id), r.nome, r.funcao_base)
                    for r in grupo.itertuples()
                }
                esc = st.multiselect(
                    "Selecionar colaboradores",
                    list(labels),
                    key=f"conv_{frente}",
                )
                for x in esc:
                    cid, nome, funcao = labels[x]
                    equipe.append({
                        "colaborador_id": cid,
                        "nome": nome,
                        "funcao": funcao,
                        "frente": frente,
                    })

        st.markdown("### Realocação")
        st.caption("Se alguém trabalhar fora da função/frente habitual, ajuste somente nesta convocação.")
        equipe_editada = []
        for item in equipe:
            with st.container(border=True):
                st.markdown(f"**{item['nome']}**")
                c1, c2 = st.columns(2)
                func = c1.text_input(
                    "Função nesta convocação",
                    value=item["funcao"],
                    key=f"func_{item['colaborador_id']}",
                )
                frente = c2.selectbox(
                    "Frente nesta convocação",
                    list(dict.fromkeys([item["frente"]] + FRENTES)),
                    key=f"fr_{item['colaborador_id']}",
                )
                equipe_editada.append({**item, "funcao": func, "frente": frente})

        st.markdown("### Avulsos")
        avulsos = st.data_editor(
            pd.DataFrame([{"Nome": "", "Função": "", "Frente": "OUTROS"}]),
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Frente": st.column_config.SelectboxColumn("Frente", options=FRENTES)
            },
        )

        if st.button("Criar convocação", type="primary", use_container_width=True):
            if not engenheiro.strip():
                st.error("Informe o engenheiro.")
            else:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO convocacoes (data, trello_card_id, engenheiro)
                            VALUES (%s,%s,%s)
                            RETURNING id
                            """,
                            (data_conv, trello_card_id, engenheiro.strip()),
                        )
                        conv_id = cur.fetchone()[0]

                        total = 0
                        for item in equipe_editada:
                            cur.execute(
                                """
                                INSERT INTO convocacao_itens (
                                    convocacao_id, colaborador_id, nome_exibicao,
                                    tipo_vinculo, funcao_executada, frente
                                )
                                VALUES (%s,%s,%s,'FIXO',%s,%s)
                                RETURNING id
                                """,
                                (
                                    conv_id, item["colaborador_id"], item["nome"],
                                    item["funcao"], item["frente"],
                                ),
                            )
                            item_id = cur.fetchone()[0]
                            cur.execute(
                                """
                                INSERT INTO apontamentos (convocacao_item_id, status)
                                VALUES (%s,'Pendente')
                                """,
                                (item_id,),
                            )
                            total += 1

                        for _, r in avulsos.iterrows():
                            nome = str(r.get("Nome", "")).strip()
                            if not nome:
                                continue
                            func = str(r.get("Função", "")).strip() or "NÃO INFORMADA"
                            frente = str(r.get("Frente", "")).strip() or inferir_frente(func)
                            cur.execute(
                                """
                                INSERT INTO convocacao_itens (
                                    convocacao_id, colaborador_id, nome_exibicao,
                                    tipo_vinculo, funcao_executada, frente
                                )
                                VALUES (%s,NULL,%s,'AVULSO',%s,%s)
                                RETURNING id
                                """,
                                (conv_id, nome.upper(), func, frente),
                            )
                            item_id = cur.fetchone()[0]
                            cur.execute(
                                """
                                INSERT INTO apontamentos (convocacao_item_id, status)
                                VALUES (%s,'Pendente')
                                """,
                                (item_id,),
                            )
                            total += 1

                    conn.commit()

                st.success(f"Convocação criada para {total} pessoa(s).")
                st.rerun()


# ============================================================
# APONTAMENTOS
# ============================================================

elif menu == "Apontamentos":
    st.subheader("Apontamentos")

    datas = query_df(
        "SELECT DISTINCT data FROM convocacoes ORDER BY data DESC LIMIT 60"
    )
    if datas.empty:
        st.info("Ainda não há convocações.")
    else:
        data_sel = st.selectbox("Data", datas["data"].tolist())

        base = query_df(
            """
            SELECT
              a.id AS apontamento_id,
              cv.id AS convocacao_id,
              COALESCE(o.numero_obra,'—') AS obra,
              o.titulo,
              ci.nome_exibicao,
              ci.tipo_vinculo,
              ci.funcao_executada,
              ci.frente,
              a.status,
              a.extra_valor,
              a.observacao
            FROM apontamentos a
            JOIN convocacao_itens ci ON ci.id=a.convocacao_item_id
            JOIN convocacoes cv ON cv.id=ci.convocacao_id
            LEFT JOIN obras_trello o ON o.trello_card_id=cv.trello_card_id
            WHERE cv.data=%s
            ORDER BY ci.frente, ci.nome_exibicao
            """,
            (data_sel,),
        )

        total = len(base)
        pend = int((base["status"] == "Pendente").sum())
        a, b, c = st.columns(3)
        a.metric("Convocados", total)
        b.metric("Apontados", total - pend)
        c.metric("Pendentes", pend)

        for frente in base["frente"].fillna("SEM FRENTE").unique():
            st.markdown(f"### {frente}")
            for r in base[base["frente"].fillna("SEM FRENTE") == frente].itertuples():
                with st.container(border=True):
                    st.markdown(
                        f"**{r.nome_exibicao}**"
                        + (" • AVULSO" if r.tipo_vinculo == "AVULSO" else "")
                    )
                    st.caption(f"Obra {r.obra} • {r.funcao_executada}")

                    c1, c2, c3 = st.columns([1.2, 1, 2])
                    status = c1.selectbox(
                        "Status",
                        STATUS_APONTAMENTO,
                        index=STATUS_APONTAMENTO.index(r.status),
                        key=f"st_{r.apontamento_id}",
                    )
                    extra = c2.number_input(
                        "Extra (R$)",
                        min_value=0.0,
                        step=10.0,
                        value=float(r.extra_valor or 0),
                        key=f"ex_{r.apontamento_id}",
                    )
                    obs = c3.text_input(
                        "Observação",
                        value=r.observacao or "",
                        key=f"ob_{r.apontamento_id}",
                    )

                    if st.button("Salvar", key=f"sv_{r.apontamento_id}"):
                        execute(
                            """
                            UPDATE apontamentos
                            SET status=%s, extra_valor=%s, observacao=%s, atualizado_em=NOW()
                            WHERE id=%s
                            """,
                            (status, extra, obs, int(r.apontamento_id)),
                        )
                        st.rerun()


# ============================================================
# MEDIÇÕES
# ============================================================

elif menu == "Medições":
    st.subheader("Medições e Resultados")
    st.caption("A competência vem da lista mensal do Trello. Ex.: em 05/09, fechar Agosto/2026.")

    hoje = date.today()
    mes_padrao = hoje.month - 1 or 12
    ano_padrao = hoje.year if hoje.month > 1 else hoje.year - 1

    c1, c2 = st.columns(2)
    mes = c1.selectbox(
        "Mês de competência",
        list(MESES_PT.keys()),
        index=list(MESES_PT.keys()).index(mes_padrao),
        format_func=lambda x: MESES_PT[x].title(),
    )
    ano = c2.number_input("Ano", min_value=2024, max_value=2100, value=ano_padrao, step=1)

    alvo = nome_lista_medicao(ano, mes)
    st.info(f"Lista esperada no Trello: **{alvo}**")

    if st.button("🔄 Sincronizar esta medição com Trello", type="primary"):
        if not trello_config():
            st.error("Configure as credenciais do Trello nos Secrets.")
        else:
            try:
                with st.spinner(f"Lendo {alvo}..."):
                    qtd, lista = sincronizar_medicao(int(ano), int(mes))
                st.success(f"{qtd} cartões sincronizados de {lista}.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    comp = competencia_date(ano, mes)
    itens = query_df(
        """
        SELECT
          mi.id,
          mi.numero_obra AS "Obra",
          mi.titulo AS "Serviço",
          mi.unidade AS "Unidade",
          mi.pipe AS "PIPE",
          mi.origem AS "Origem",
          mi.status_medicao AS "Status",
          mi.valor_orcamento AS "Valor orçamento",
          mi.valor_aprovado AS "Valor aprovado",
          mi.resultado AS "Resultado",
          mi.percentual AS "Percentual",
          mi.observacao AS "Observação",
          mi.url_trello AS "Trello",
          mi.presente_na_lista AS "Na lista atual"
        FROM medicao_itens mi
        JOIN medicoes m ON m.id=mi.medicao_id
        WHERE m.competencia=%s
        ORDER BY mi.origem, mi.numero_obra NULLS LAST, mi.titulo
        """,
        (comp,),
    )

    if itens.empty:
        st.warning("Essa competência ainda não foi sincronizada.")
    else:
        ativos = itens[itens["Na lista atual"] == True].copy()
        fiec = ativos[ativos["Origem"] == "FIEC"].copy()
        fora = ativos[ativos["Origem"] != "FIEC"].copy()

        a, b, c = st.columns(3)
        a.metric("Cartões na competência", len(ativos))
        b.metric("Medição FIEC", len(fiec))
        c.metric("Resultados fora FIEC", len(fora))

        tab1, tab2, tab3 = st.tabs(["🏭 FIEC", "↗️ Fora FIEC", "📋 Todos"])

        with tab1:
            st.dataframe(fiec, use_container_width=True, hide_index=True)

        with tab2:
            st.dataframe(fora, use_container_width=True, hide_index=True)

        with tab3:
            st.dataframe(itens, use_container_width=True, hide_index=True)

        st.markdown("### Lançar / ajustar resultado")
        opcoes = {
            f"{r['Origem']} | OBRA {r['Obra'] or '—'} | {r['Serviço']}": int(r["id"])
            for _, r in ativos.iterrows()
        }
        escolha = st.selectbox("Cartão", list(opcoes))
        item_id = opcoes[escolha]
        atual = ativos[ativos["id"] == item_id].iloc[0]

        c1, c2, c3 = st.columns(3)
        valor_orc = c1.number_input(
            "Valor orçamento",
            min_value=0.0,
            value=float(atual["Valor orçamento"] or 0),
            step=100.0,
        )
        valor_apr = c2.number_input(
            "Valor aprovado",
            min_value=0.0,
            value=float(atual["Valor aprovado"] or 0),
            step=100.0,
        )
        resultado = c3.number_input(
            "Resultado",
            value=float(atual["Resultado"] or 0),
            step=100.0,
        )

        status = st.selectbox(
            "Status da medição",
            ["Pendente", "Em preenchimento", "Conferido", "Fechado"],
            index=["Pendente", "Em preenchimento", "Conferido", "Fechado"].index(
                atual["Status"] if atual["Status"] in
                ["Pendente", "Em preenchimento", "Conferido", "Fechado"]
                else "Pendente"
            ),
        )
        obs = st.text_area("Observação", value=atual["Observação"] or "")

        percentual = (resultado / valor_apr * 100) if valor_apr else 0
        st.metric("Percentual calculado", f"{percentual:.2f}%")

        if st.button("Salvar resultado", type="primary"):
            execute(
                """
                UPDATE medicao_itens
                SET valor_orcamento=%s,
                    valor_aprovado=%s,
                    resultado=%s,
                    percentual=%s,
                    status_medicao=%s,
                    observacao=%s,
                    atualizado_em=NOW()
                WHERE id=%s
                """,
                (
                    valor_orc, valor_apr, resultado, percentual,
                    status, obs, item_id,
                ),
            )
            st.success("Resultado salvo.")
            st.rerun()
