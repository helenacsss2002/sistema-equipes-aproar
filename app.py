import re
import unicodedata
from datetime import date

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BUILD = "PROTOTIPO-TRELLO-PUBLICO-2026-08-26"

st.set_page_config(
    page_title="Apontamentos APROAR",
    page_icon="🏗️",
    layout="wide",
)

TRELLO_PUBLIC_JSON = "https://trello.com/b/TX8hGvmI.json"

LISTAS_OBRAS_ATIVAS = {
    "EM EXECUÇÃO",
    "APROVADO - AGUARDANDO EXECUÇÃO",
}

UNIDADES = [
    "HORIZONTE",
    "CENTRO",
    "BARRA",
    "FIEC",
    "UNIFOR",
    "MUSEU",
    "SEBRAE",
    "COLISEU",
    "ESCRITÓRIO",
    "MARACANAÚ",
]

MESES_PT = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO",
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

STATUS_APONTAMENTO = [
    "Pendente",
    "Presença",
    "Falta",
    "Atestado",
]


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>

        .block-container {
            padding-top: 1.15rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128,128,128,.18);
            border-radius: 14px;
            padding: 11px 13px;
        }

        .modo-prototipo {
            padding: 10px 14px;
            border-radius: 10px;
            background: rgba(245,158,11,.08);
            border: 1px solid rgba(245,158,11,.35);
            margin: 8px 0 16px 0;
        }

        .obra-ok {
            padding: 11px 14px;
            border-radius: 10px;
            background: rgba(34,197,94,.08);
            border: 1px solid rgba(34,197,94,.30);
            margin-top: 8px;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES
# ============================================================

def normalizar(texto):

    texto = "" if texto is None else str(texto)

    texto = "".join(
        c
        for c in unicodedata.normalize(
            "NFD",
            texto,
        )
        if unicodedata.category(c) != "Mn"
    )

    return re.sub(
        r"\s+",
        " ",
        texto,
    ).strip().upper()


def inferir_frente(funcao):

    f = normalizar(funcao)

    regras = [

        (
            ["PINTOR", "PINTURA"],
            "PINTURA",
        ),

        (
            ["PEDREIRO", "ALVENAR"],
            "ALVENARIA / PEDREIROS",
        ),

        (
            ["ELETRIC", "ELETROT", "ELETROMEC"],
            "ELÉTRICA",
        ),

        (
            ["ENCANADOR", "HIDRAUL", "BOMBEIRO"],
            "HIDRÁULICA",
        ),

        (
            ["AZULEJ", "LADRILH", "CERAM", "REVEST"],
            "PISO / REVESTIMENTO",
        ),

        (
            ["GESS", "DRYWALL", "FORRO"],
            "FORRO / GESSO",
        ),

        (
            ["TELHAD", "TELHEIR", "COBERT"],
            "COBERTURA",
        ),

        (
            ["IMPERMEABIL"],
            "IMPERMEABILIZAÇÃO",
        ),

        (
            ["SERRALH", "SOLDADOR"],
            "SERRALHERIA",
        ),

        (
            ["CARPINTEIR", "MARCENEIR"],
            "MARCENARIA / CARPINTARIA",
        ),

        (
            ["MESTRE", "ENCARREG", "SUPERVIS", "LIDER"],
            "GESTÃO DE CAMPO",
        ),

        (
            [
                "SERVENTE",
                "AJUDANTE",
                "AUXILIAR",
                "SERVICOS GERAIS",
            ],
            "APOIO / SERVIÇOS GERAIS",
        ),
    ]

    for termos, frente in regras:

        if any(
            termo in f
            for termo in termos
        ):
            return frente

    return "OUTROS"


def detectar_unidade(texto):

    t = normalizar(texto)

    regras = [

        (
            "MARACANAU",
            "MARACANAÚ",
        ),

        (
            "HORIZONTE",
            "HORIZONTE",
        ),

        (
            "BARRA",
            "BARRA",
        ),

        (
            "CENTRO",
            "CENTRO",
        ),

        (
            "UNIFOR",
            "UNIFOR",
        ),

        (
            "MUSEU",
            "MUSEU",
        ),

        (
            "SEBRAE",
            "SEBRAE",
        ),

        (
            "COLISEU",
            "COLISEU",
        ),

        (
            "ESCRITORIO",
            "ESCRITÓRIO",
        ),

        (
            "FIEC",
            "FIEC",
        ),
    ]

    for termo, unidade in regras:

        if termo in t:

            return unidade

    return ""


def extrair_numero_obra(nome):

    texto = normalizar(nome)

    padroes = [

        r"\bOBRA\s*[:#-]?\s*(\d+(?:\.\d+)?)\b",

        r"^\s*(\d+(?:\.\d+)?)\s*[-|]",

    ]

    for padrao in padroes:

        match = re.search(
            padrao,
            texto,
        )

        if match:

            return match.group(1)

    return ""


def extrair_pipe(nome):

    partes = [
        parte.strip()
        for parte in str(nome).split("|")
    ]

    if len(partes) >= 2:

        match = re.search(
            r"(\d{6,})",
            partes[-1],
        )

        if match:

            return match.group(1)

    match = re.search(
        r"\bPIPE\s*:?\s*(\d+)\b",
        normalizar(nome),
    )

    if match:

        return match.group(1)

    return ""


def extrair_titulo(
    nome,
    numero_obra,
):

    titulo = (
        str(nome)
        .split("|")[0]
        .strip()
    )

    if numero_obra:

        titulo = re.sub(
            (
                rf"^\s*OBRA\s*[:#-]?\s*"
                rf"{re.escape(numero_obra)}"
                rf"\s*[-–—:]*\s*"
            ),
            "",
            titulo,
            flags=re.IGNORECASE,
        )

    return (
        titulo.strip(" -–—:")
        or str(nome).strip()
    )


def parsear_card(
    card,
    nome_lista,
):

    nome = str(
        card.get(
            "name",
            "",
        )
    ).strip()

    obra = extrair_numero_obra(
        nome
    )

    if not obra:

        return None

    partes = [
        parte.strip()
        for parte in nome.split("|")
    ]

    if len(partes) >= 3:

        trecho_unidade = " | ".join(
            partes[1:-1]
        )

    else:

        trecho_unidade = nome

    unidade = (
        detectar_unidade(
            trecho_unidade
        )
        or
        detectar_unidade(
            nome
        )
    )

    return {

        "trello_card_id":
            str(
                card.get(
                    "id",
                    "",
                )
            ),

        "short_link":
            str(
                card.get(
                    "shortLink",
                    "",
                )
            ),

        "nome_trello":
            nome,

        "obra":
            obra,

        "titulo":
            extrair_titulo(
                nome,
                obra,
            ),

        "unidade":
            unidade,

        "pipe":
            extrair_pipe(
                nome
            ),

        "lista":
            nome_lista,

    }


# ============================================================
# TRELLO PÚBLICO
# ============================================================

@st.cache_data(
    ttl=60,
    show_spinner=False,
)
def carregar_obras_trello_publico():

    resposta = requests.get(
        TRELLO_PUBLIC_JSON,
        timeout=15,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/151 Safari/537.36"
            )
        },
    )

    resposta.raise_for_status()

    dados = resposta.json()

    nomes_validos = {
        normalizar(nome)
        for nome in LISTAS_OBRAS_ATIVAS
    }

    listas = {

        str(
            lista.get(
                "id"
            )
        ):
        str(
            lista.get(
                "name",
                "",
            )
        ).strip()

        for lista in dados.get(
            "lists",
            [],
        )

        if (
            not lista.get(
                "closed"
            )
            and
            normalizar(
                lista.get(
                    "name",
                    "",
                )
            )
            in nomes_validos
        )
    }

    obras = []

    for card in dados.get(
        "cards",
        [],
    ):

        if card.get(
            "closed"
        ):

            continue

        id_lista = str(
            card.get(
                "idList",
                "",
            )
        )

        if id_lista not in listas:

            continue

        item = parsear_card(
            card,
            listas[id_lista],
        )

        if item:

            obras.append(
                item
            )

    colunas = [

        "trello_card_id",

        "short_link",

        "nome_trello",

        "obra",

        "titulo",

        "unidade",

        "pipe",

        "lista",

    ]

    df = pd.DataFrame(
        obras,
        columns=colunas,
    )

    if not df.empty:

        df = (
            df
            .drop_duplicates(
                subset=[
                    "trello_card_id"
                ]
            )
            .sort_values(
                [
                    "unidade",
                    "obra",
                    "titulo",
                ],
                kind="stable",
            )
            .reset_index(
                drop=True
            )
        )

    return df


def sincronizar_trello(
    forcar=False,
):

    if forcar:

        carregar_obras_trello_publico.clear()

    try:

        df = (
            carregar_obras_trello_publico()
        )

        st.session_state.obras_trello = (
            df
        )

        st.session_state.trello_ok = (
            True
        )

        st.session_state.trello_erro = (
            ""
        )

        return True

    except Exception as erro:

        st.session_state.trello_ok = (
            False
        )

        st.session_state.trello_erro = (
            f"{type(erro).__name__}: "
            f"{erro}"
        )

        return False


# ============================================================
# DADOS DE TESTE
# ============================================================

def iniciar_dados():

    if "colaboradores" not in st.session_state:

        st.session_state.colaboradores = (
            pd.DataFrame(
                [

                    {
                        "id": 1,
                        "nome": "FRANCISCO",
                        "funcao": "Pintor",
                        "frente": "PINTURA",
                        "ativo": True,
                    },

                    {
                        "id": 2,
                        "nome": "JOÃO",
                        "funcao": "Pintor",
                        "frente": "PINTURA",
                        "ativo": True,
                    },

                    {
                        "id": 3,
                        "nome": "JOCA",
                        "funcao": "Pintor",
                        "frente": "PINTURA",
                        "ativo": True,
                    },

                    {
                        "id": 4,
                        "nome": "JOSÉ",
                        "funcao": "Pintor",
                        "frente": "PINTURA",
                        "ativo": True,
                    },

                    {
                        "id": 5,
                        "nome": "PEDRO",
                        "funcao": "Pedreiro",
                        "frente":
                            "ALVENARIA / PEDREIROS",
                        "ativo": True,
                    },

                    {
                        "id": 6,
                        "nome": "CARLOS",
                        "funcao": "Pedreiro",
                        "frente":
                            "ALVENARIA / PEDREIROS",
                        "ativo": True,
                    },

                    {
                        "id": 7,
                        "nome": "MARCOS",
                        "funcao":
                            "Eletricista",
                        "frente":
                            "ELÉTRICA",
                        "ativo": True,
                    },

                    {
                        "id": 8,
                        "nome": "LUCAS",
                        "funcao":
                            "Encanador",
                        "frente":
                            "HIDRÁULICA",
                        "ativo": True,
                    },

                    {
                        "id": 9,
                        "nome": "RAFAEL",
                        "funcao":
                            "Servente",
                        "frente":
                            "APOIO / SERVIÇOS GERAIS",
                        "ativo": True,
                    },

                ]
            )
        )

    if "convocacoes" not in st.session_state:

        st.session_state.convocacoes = []

    if "apontamentos" not in st.session_state:

        st.session_state.apontamentos = []

    if "equipe_rascunho" not in st.session_state:

        st.session_state.equipe_rascunho = []

    if "conv_select_version" not in st.session_state:

        st.session_state.conv_select_version = 0

    if "conv_editor_version" not in st.session_state:

        st.session_state.conv_editor_version = 0

    if "avulso_version" not in st.session_state:

        st.session_state.avulso_version = 0

    if "obras_trello" not in st.session_state:

        st.session_state.obras_trello = (
            pd.DataFrame(
                columns=[
                    "trello_card_id",
                    "short_link",
                    "nome_trello",
                    "obra",
                    "titulo",
                    "unidade",
                    "pipe",
                    "lista",
                ]
            )
        )

    if "medicoes" not in st.session_state:

        st.session_state.medicoes = (
            pd.DataFrame(
                [

                    {
                        "id": 1,
                        "competencia": "08/2026",
                        "obra": "2450.1",
                        "servico":
                            "CONSERTAR CERCA ELÉTRICA",
                        "unidade": "CENTRO",
                        "pipe":
                            "1357123706",
                        "origem":
                            "FIEC",
                        "status":
                            "Pendente",
                        "valor_aprovado":
                            0.0,
                        "resultado":
                            0.0,
                    },

                    {
                        "id": 2,
                        "competencia": "08/2026",
                        "obra": "2467",
                        "servico":
                            "MANUTENÇÃO DOS BANHEIROS",
                        "unidade": "BARRA",
                        "pipe":
                            "1377057280",
                        "origem":
                            "FIEC",
                        "status":
                            "Pendente",
                        "valor_aprovado":
                            0.0,
                        "resultado":
                            0.0,
                    },

                    {
                        "id": 3,
                        "competencia": "08/2026",
                        "obra": "—",
                        "servico":
                            "SUBCONTRATAÇÃO / COMPRA DE MATERIAIS",
                        "unidade": "—",
                        "pipe":
                            "1427648041",
                        "origem":
                            "QUARTEIRIZADOS",
                        "status":
                            "Pendente",
                        "valor_aprovado":
                            0.0,
                        "resultado":
                            0.0,
                    },

                ]
            )
        )


iniciar_dados()


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🏗️ Controle de Equipes e Apontamentos"
)

st.caption(
    "APROAR Engenharia"
)

st.markdown(
    f"""
    <div class="modo-prototipo">

        🧪 <b>MODO PROTÓTIPO — SEM SUPABASE</b><br>

        Tentativa de leitura do quadro público
        do Trello sem token.<br>

        Build:
        <code>{BUILD}</code>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MENU
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Operações"
    )

    engenheiro_atual = st.text_input(
        "Engenheiro / supervisor",
        value=st.session_state.get(
            "engenheiro_atual",
            "",
        ),
    )

    st.session_state.engenheiro_atual = (
        engenheiro_atual
    )

    menu = st.radio(
        "Menu",
        [
            "Visão Geral",
            "Colaboradores",
            "Convocação",
            "Apontamentos",
            "Medições",
        ],
    )

    st.divider()

    st.caption(
        f"Build: {BUILD}"
    )

    if st.button(
        "Restaurar demonstração",
        use_container_width=True,
    ):

        chaves = [

            "colaboradores",

            "convocacoes",

            "apontamentos",

            "medicoes",

            "equipe_rascunho",

            "ultima_convocacao_msg",

            "conv_select_version",

            "conv_editor_version",

            "avulso_version",

            "obras_trello",

            "trello_ok",

            "trello_erro",

            "trello_sync_inicial",

        ]

        for chave in chaves:

            st.session_state.pop(
                chave,
                None,
            )

        carregar_obras_trello_publico.clear()

        iniciar_dados()

        st.rerun()


# ============================================================
# VISÃO GERAL
# ============================================================

if menu == "Visão Geral":

    st.subheader(
        "Visão Geral"
    )

    total_convocados = sum(
        len(
            convocacao["equipe"]
        )
        for convocacao in (
            st.session_state.convocacoes
        )
    )

    total_pendentes = sum(
        1
        for apontamento in (
            st.session_state.apontamentos
        )
        if apontamento["status"]
        == "Pendente"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Colaboradores",
        len(
            st.session_state.colaboradores
        ),
    )

    c2.metric(
        "Convocados",
        total_convocados,
    )

    c3.metric(
        "Apontamentos pendentes",
        total_pendentes,
    )

    c4.metric(
        "Obras ativas do Trello",
        len(
            st.session_state.obras_trello
        ),
    )

    st.markdown(
        "### Fluxo"
    )

    st.write(
        "Trello → Unidade/Obra → "
        "Convocação por frente → "
        "Apontamento → "
        "Medições / Resultados"
    )

    if st.session_state.apontamentos:

        df = pd.DataFrame(
            st.session_state.apontamentos
        )

        pendentes = df[
            df["status"]
            == "Pendente"
        ]

        if not pendentes.empty:

            st.markdown(
                "### Pendências"
            )

            st.dataframe(
                pendentes[
                    [
                        "data",
                        "unidade",
                        "obra",
                        "nome",
                        "frente",
                        "status",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# COLABORADORES
# ============================================================

elif menu == "Colaboradores":

    st.subheader(
        "Colaboradores"
    )

    st.caption(
        "A função cadastrada define em qual frente "
        "o colaborador aparece inicialmente."
    )

    with st.expander(
        "➕ Adicionar colaborador"
    ):

        c1, c2 = st.columns(2)

        nome = c1.text_input(
            "Nome"
        )

        funcao = c2.text_input(
            "Função / cargo"
        )

        frente_sugerida = inferir_frente(
            funcao
        )

        frente = st.selectbox(
            "Frente principal",
            FRENTES,
            index=FRENTES.index(
                frente_sugerida
            ),
        )

        if st.button(
            "Adicionar colaborador"
        ):

            if not nome.strip():

                st.error(
                    "Informe o nome."
                )

            else:

                df = (
                    st.session_state
                    .colaboradores
                )

                if df.empty:

                    novo_id = 1

                else:

                    novo_id = (
                        int(
                            df["id"].max()
                        )
                        + 1
                    )

                novo = pd.DataFrame(
                    [
                        {
                            "id":
                                novo_id,

                            "nome":
                                nome
                                .strip()
                                .upper(),

                            "funcao":
                                funcao.strip()
                                or "NÃO INFORMADA",

                            "frente":
                                frente,

                            "ativo":
                                True,
                        }
                    ]
                )

                st.session_state.colaboradores = (
                    pd.concat(
                        [
                            df,
                            novo,
                        ],
                        ignore_index=True,
                    )
                )

                st.rerun()

    frentes_existentes = sorted(
        st.session_state
        .colaboradores[
            "frente"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    filtro = st.selectbox(
        "Filtrar por frente",
        [
            "Todas"
        ]
        + frentes_existentes,
    )

    base = (
        st.session_state
        .colaboradores
        .copy()
    )

    if filtro != "Todas":

        base = base[
            base["frente"]
            == filtro
        ]

    tabela = base.rename(
        columns={

            "nome":
                "Nome",

            "funcao":
                "Função",

            "frente":
                "Frente",

            "ativo":
                "Ativo",

        }
    )

    st.dataframe(
        tabela[
            [
                "Nome",
                "Função",
                "Frente",
                "Ativo",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# CONVOCAÇÃO
# ============================================================

elif menu == "Convocação":

    st.subheader(
        "Nova convocação"
    )

    st.caption(
        "Escolha a unidade, informe o número "
        "da obra e monte a equipe."
    )

    if (
        "ultima_convocacao_msg"
        in st.session_state
    ):

        st.success(
            st.session_state.pop(
                "ultima_convocacao_msg"
            )
        )


    # ========================================================
    # SINCRONIZAÇÃO TRELLO
    # ========================================================

    if (
        "trello_sync_inicial"
        not in st.session_state
    ):

        st.session_state.trello_sync_inicial = (
            True
        )

        with st.spinner(
            "Lendo obras do Trello..."
        ):

            sincronizar_trello()


    coluna_sync, coluna_botao = st.columns(
        [
            4,
            1,
        ]
    )


    with coluna_sync:

        if st.session_state.get(
            "trello_ok"
        ):

            obras_lidas = (
                st.session_state
                .obras_trello
            )

            if obras_lidas.empty:

                sem_unidade = 0

            else:

                sem_unidade = int(
                    (
                        obras_lidas[
                            "unidade"
                        ]
                        == ""
                    ).sum()
                )

            st.success(
                f"Trello sincronizado: "
                f"{len(obras_lidas)} obra(s) "
                "nas listas permitidas."
            )

            if sem_unidade:

                st.caption(
                    f"{sem_unidade} card(s) foram "
                    "lidos, mas a unidade não pôde "
                    "ser identificada pelo nome."
                )

        else:

            st.error(
                "Não foi possível ler o quadro "
                "público do Trello."
            )

            if st.session_state.get(
                "trello_erro"
            ):

                with st.expander(
                    "Ver erro"
                ):

                    st.code(
                        st.session_state
                        .trello_erro
                    )


    with coluna_botao:

        if st.button(
            "🔄 Atualizar",
            use_container_width=True,
        ):

            with st.spinner(
                "Atualizando Trello..."
            ):

                sincronizar_trello(
                    forcar=True
                )

            st.rerun()


    # ========================================================
    # DADOS DA CONVOCAÇÃO
    # ========================================================

    with st.container(
        border=True
    ):

        c1, c2, c3 = st.columns(
            [
                1,
                1.1,
                1.5,
            ]
        )

        data_convocacao = c1.date_input(
            "Data",
            value=date.today(),
            key="conv_data",
        )

        unidade = c2.selectbox(
            "Unidade",
            UNIDADES,
            key="conv_unidade",
        )

        engenheiro = c3.text_input(
            "Engenheiro responsável",
            value=st.session_state.get(
                "engenheiro_atual",
                "",
            ),
            key="conv_engenheiro",
        )


        # ====================================================
        # BUSCA DA OBRA
        # ====================================================

        obras_trello = (
            st.session_state
            .obras_trello
            .copy()
        )

        if obras_trello.empty:

            obras_unidade = (
                obras_trello
            )

        else:

            obras_unidade = (
                obras_trello[
                    obras_trello[
                        "unidade"
                    ]
                    ==
                    unidade
                ]
                .copy()
            )


        numero_digitado = st.text_input(
            "Nº da obra",
            placeholder="Ex.: 140",
            key="conv_numero_obra",
            help=(
                "A busca considera somente cards "
                "em EM EXECUÇÃO ou "
                "APROVADO - AGUARDANDO EXECUÇÃO."
            ),
        ).strip()


        obra_selecionada = None


        if numero_digitado:

            candidatos = (
                obras_unidade[
                    obras_unidade[
                        "obra"
                    ]
                    .astype(str)
                    .str.startswith(
                        numero_digitado,
                        na=False,
                    )
                ]
                .copy()
            )


            exatos = (
                candidatos[
                    candidatos[
                        "obra"
                    ]
                    .astype(str)
                    ==
                    numero_digitado
                ]
                .copy()
            )


            if len(exatos) == 1:

                obra_selecionada = (
                    exatos.iloc[0]
                )


            elif len(exatos) > 1:

                opcoes = {

                    (
                        f"OBRA {r.obra} — "
                        f"{r.titulo} | "
                        f"{r.lista}"
                    ):
                    r.trello_card_id

                    for r in (
                        exatos.itertuples()
                    )
                }


                escolha = st.selectbox(
                    "Selecione a obra",
                    list(
                        opcoes.keys()
                    ),
                )


                obra_selecionada = (
                    exatos[
                        exatos[
                            "trello_card_id"
                        ]
                        ==
                        opcoes[
                            escolha
                        ]
                    ]
                    .iloc[0]
                )


            elif not candidatos.empty:

                opcoes = {

                    (
                        f"OBRA {r.obra} — "
                        f"{r.titulo}"
                    ):
                    r.trello_card_id

                    for r in (
                        candidatos.itertuples()
                    )
                }


                escolha = st.selectbox(
                    "Obras encontradas",
                    list(
                        opcoes.keys()
                    ),
                    key="conv_obra_resultados",
                )


                obra_selecionada = (
                    candidatos[
                        candidatos[
                            "trello_card_id"
                        ]
                        ==
                        opcoes[
                            escolha
                        ]
                    ]
                    .iloc[0]
                )


            elif st.session_state.get(
                "trello_ok"
            ):

                st.warning(
                    f"Nenhuma obra iniciada por "
                    f"'{numero_digitado}' foi "
                    f"encontrada em {unidade}."
                )


        elif st.session_state.get(
            "trello_ok"
        ):

            st.caption(
                f"{len(obras_unidade)} obra(s) "
                f"disponível(is) em {unidade} "
                "nas duas listas permitidas."
            )


        if obra_selecionada is not None:

            if obra_selecionada[
                "pipe"
            ]:

                pipe_txt = (
                    " • PIPE "
                    f"{obra_selecionada['pipe']}"
                )

            else:

                pipe_txt = ""


            st.markdown(
                f"""
                <div class="obra-ok">

                    ✅ <b>OBRA
                    {obra_selecionada['obra']}</b>
                    —
                    {obra_selecionada['titulo']}
                    <br>

                    {obra_selecionada['unidade']}
                    •
                    {obra_selecionada['lista']}
                    {pipe_txt}

                </div>
                """,
                unsafe_allow_html=True,
            )


    # ========================================================
    # MONTAR EQUIPE
    # ========================================================

    st.markdown(
        "### Montar equipe"
    )


    with st.container(
        border=True
    ):

        colaboradores = (
            st.session_state
            .colaboradores
            .copy()
        )


        frentes_disponiveis = sorted(
            colaboradores[
                colaboradores["ativo"]
                == True
            ]["frente"]
            .dropna()
            .unique()
            .tolist()
        )


        c1, c2 = st.columns(
            [
                1,
                2,
            ]
        )


        frente_escolhida = c1.selectbox(
            "Frente",
            frentes_disponiveis,
            key="conv_frente_escolhida",
        )


        grupo = (
            colaboradores[
                (
                    colaboradores["frente"]
                    == frente_escolhida
                )
                &
                (
                    colaboradores["ativo"]
                    == True
                )
            ]
        )


        ids_ja_adicionados = {

            pessoa["colaborador_id"]

            for pessoa in (
                st.session_state
                .equipe_rascunho
            )

            if pessoa.get(
                "colaborador_id"
            )
            is not None
        }


        grupo = grupo[
            ~grupo["id"].isin(
                ids_ja_adicionados
            )
        ]


        labels = {

            (
                f"{pessoa.nome} — "
                f"{pessoa.funcao}"
            ):
            int(
                pessoa.id
            )

            for pessoa in (
                grupo.itertuples()
            )
        }


        mao_obra = c2.multiselect(
            "Mão de obra disponível",
            list(
                labels.keys()
            ),
            key=(
                "conv_mao_obra_"
                f"{st.session_state.conv_select_version}"
            ),
            placeholder=(
                "Selecione uma ou mais pessoas..."
            ),
        )


        if st.button(
            "＋ Adicionar à equipe",
            use_container_width=True,
            disabled=not mao_obra,
        ):

            for label in mao_obra:

                colaborador_id = (
                    labels[label]
                )


                row = (
                    colaboradores[
                        colaboradores["id"]
                        ==
                        colaborador_id
                    ]
                    .iloc[0]
                )


                st.session_state.equipe_rascunho.append(
                    {

                        "colaborador_id":
                            int(
                                colaborador_id
                            ),

                        "nome":
                            row["nome"],

                        "funcao_base":
                            row["funcao"],

                        "frente_base":
                            row["frente"],

                        "funcao_dia":
                            row["funcao"],

                        "frente_dia":
                            row["frente"],

                        "observacao":
                            "",

                        "tipo":
                            "FIXO",

                    }
                )


            st.session_state.conv_select_version += 1

            st.session_state.conv_editor_version += 1

            st.rerun()


        # ====================================================
        # AVULSOS
        # ====================================================

        with st.expander(
            "＋ Mão de obra avulsa"
        ):

            avulsos = st.data_editor(
                pd.DataFrame(
                    [
                        {
                            "Nome":
                                "",

                            "Função":
                                "",

                            "Frente":
                                frente_escolhida,
                        }
                    ]
                ),
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Frente":
                        st.column_config
                        .SelectboxColumn(
                            "Frente",
                            options=FRENTES,
                        )
                },
                key=(
                    "conv_avulsos_"
                    f"{st.session_state.avulso_version}"
                ),
            )


            if st.button(
                "Adicionar avulso(s)",
                use_container_width=True,
            ):

                adicionados = 0


                for _, avulso in (
                    avulsos.iterrows()
                ):

                    nome_avulso = str(
                        avulso.get(
                            "Nome",
                            "",
                        )
                    ).strip()


                    if not nome_avulso:

                        continue


                    funcao_avulso = str(
                        avulso.get(
                            "Função",
                            "",
                        )
                    ).strip()


                    frente_avulso = str(
                        avulso.get(
                            "Frente",
                            "",
                        )
                    ).strip()


                    st.session_state.equipe_rascunho.append(
                        {

                            "colaborador_id":
                                None,

                            "nome":
                                nome_avulso.upper(),

                            "funcao_base":
                                "AVULSO",

                            "frente_base":
                                "AVULSO",

                            "funcao_dia":
                                funcao_avulso
                                or
                                "NÃO INFORMADA",

                            "frente_dia":
                                frente_avulso
                                or
                                frente_escolhida,

                            "observacao":
                                "",

                            "tipo":
                                "AVULSO",

                        }
                    )


                    adicionados += 1


                if adicionados:

                    st.session_state.avulso_version += 1

                    st.session_state.conv_editor_version += 1

                    st.rerun()


    # ========================================================
    # EQUIPE MONTADA
    # ========================================================

    if (
        st.session_state
        .equipe_rascunho
    ):

        st.markdown(
            "### Equipe montada"
        )


        equipe_df = pd.DataFrame(
            [

                {

                    "Nome":
                        pessoa["nome"],

                    "Função base":
                        pessoa["funcao_base"],

                    "Função no dia":
                        pessoa["funcao_dia"],

                    "Frente no dia":
                        pessoa["frente_dia"],

                    "Observação":
                        pessoa.get(
                            "observacao",
                            "",
                        ),

                    "Remover":
                        False,

                }

                for pessoa in (
                    st.session_state
                    .equipe_rascunho
                )
            ]
        )


        equipe_editada = st.data_editor(
            equipe_df,
            use_container_width=True,
            hide_index=True,
            disabled=[
                "Nome",
                "Função base",
            ],
            column_config={

                "Frente no dia":
                    st.column_config
                    .SelectboxColumn(
                        "Frente no dia",
                        options=FRENTES,
                    ),

                "Observação":
                    st.column_config
                    .TextColumn(
                        "Observação",
                        help=(
                            "Obrigatória se a função "
                            "ou a frente do colaborador "
                            "fixo for alterada."
                        ),
                    ),

                "Remover":
                    st.column_config
                    .CheckboxColumn(
                        "Remover",
                        default=False,
                    ),

            },
            key=(
                "conv_equipe_editor_"
                f"{st.session_state.conv_editor_version}"
            ),
        )


        nova_equipe = []


        for i, row in (
            equipe_editada.iterrows()
        ):

            if bool(
                row["Remover"]
            ):

                continue


            original = (
                st.session_state
                .equipe_rascunho[i]
                .copy()
            )


            original[
                "funcao_dia"
            ] = (
                str(
                    row[
                        "Função no dia"
                    ]
                ).strip()
                or
                original[
                    "funcao_dia"
                ]
            )


            original[
                "frente_dia"
            ] = (
                str(
                    row[
                        "Frente no dia"
                    ]
                ).strip()
                or
                original[
                    "frente_dia"
                ]
            )


            original[
                "observacao"
            ] = str(
                row[
                    "Observação"
                ]
            ).strip()


            nova_equipe.append(
                original
            )


        if (
            len(
                nova_equipe
            )
            !=
            len(
                st.session_state
                .equipe_rascunho
            )
        ):

            st.session_state.equipe_rascunho = (
                nova_equipe
            )

            st.session_state.conv_editor_version += 1

            st.rerun()


        st.session_state.equipe_rascunho = (
            nova_equipe
        )


        # ====================================================
        # BOTÕES
        # ====================================================

        c1, c2 = st.columns(2)


        if c1.button(
            "Limpar equipe",
            use_container_width=True,
        ):

            st.session_state.equipe_rascunho = []

            st.session_state.conv_select_version += 1

            st.session_state.conv_editor_version += 1

            st.rerun()


        salvar = c2.button(
            "Criar convocação",
            type="primary",
            use_container_width=True,
        )


        if salvar:

            if not engenheiro.strip():

                st.error(
                    "Informe o engenheiro responsável."
                )

                st.stop()


            if obra_selecionada is None:

                st.error(
                    "Informe e relacione uma obra válida do Trello."
                )

                st.stop()


            if not (
                st.session_state
                .equipe_rascunho
            ):

                st.error(
                    "Adicione pelo menos uma pessoa."
                )

                st.stop()


            # ================================================
            # REALOCAÇÃO
            # ================================================

            realocacoes_sem_obs = []


            for pessoa in (
                st.session_state
                .equipe_rascunho
            ):

                mudou_funcao = (
                    pessoa["tipo"]
                    ==
                    "FIXO"
                    and
                    normalizar(
                        pessoa[
                            "funcao_dia"
                        ]
                    )
                    !=
                    normalizar(
                        pessoa[
                            "funcao_base"
                        ]
                    )
                )


                mudou_frente = (
                    pessoa["tipo"]
                    ==
                    "FIXO"
                    and
                    normalizar(
                        pessoa[
                            "frente_dia"
                        ]
                    )
                    !=
                    normalizar(
                        pessoa[
                            "frente_base"
                        ]
                    )
                )


                if (
                    (
                        mudou_funcao
                        or
                        mudou_frente
                    )
                    and
                    not pessoa[
                        "observacao"
                    ].strip()
                ):

                    realocacoes_sem_obs.append(
                        pessoa[
                            "nome"
                        ]
                    )


            if realocacoes_sem_obs:

                st.error(
                    "Informe uma observação "
                    "para quem foi realocado: "
                    +
                    ", ".join(
                        realocacoes_sem_obs
                    )
                )

                st.stop()


            # ================================================
            # BLOQUEAR DUPLICAÇÃO
            # ================================================

            nomes_chave = sorted(
                [

                    (
                        f"{p['tipo']}|"
                        f"{p['nome']}|"
                        f"{p['funcao_dia']}|"
                        f"{p['frente_dia']}"
                    )

                    for p in (
                        st.session_state
                        .equipe_rascunho
                    )
                ]
            )


            assinatura = (

                str(
                    data_convocacao
                ),

                unidade,

                str(
                    obra_selecionada[
                        "trello_card_id"
                    ]
                ),

                engenheiro
                .strip()
                .upper(),

                tuple(
                    nomes_chave
                ),

            )


            duplicada = any(

                convocacao.get(
                    "assinatura"
                )
                ==
                assinatura

                for convocacao in (
                    st.session_state
                    .convocacoes
                )
            )


            if duplicada:

                st.warning(
                    "Essa convocação já foi criada. "
                    "A duplicação foi bloqueada."
                )

                st.stop()


            # ================================================
            # SALVAR CONVOCAÇÃO
            # ================================================

            convocacao_id = (
                len(
                    st.session_state
                    .convocacoes
                )
                + 1
            )


            equipe_salvar = [

                {

                    "colaborador_id":
                        pessoa[
                            "colaborador_id"
                        ],

                    "nome":
                        pessoa[
                            "nome"
                        ],

                    "funcao":
                        pessoa[
                            "funcao_dia"
                        ],

                    "frente":
                        pessoa[
                            "frente_dia"
                        ],

                    "tipo":
                        pessoa[
                            "tipo"
                        ],

                    "observacao":
                        pessoa[
                            "observacao"
                        ],

                }

                for pessoa in (
                    st.session_state
                    .equipe_rascunho
                )
            ]


            st.session_state.convocacoes.append(
                {

                    "id":
                        convocacao_id,

                    "data":
                        str(
                            data_convocacao
                        ),

                    "unidade":
                        unidade,

                    "engenheiro":
                        engenheiro.strip(),

                    "trello_card_id":
                        str(
                            obra_selecionada[
                                "trello_card_id"
                            ]
                        ),

                    "obra":
                        str(
                            obra_selecionada[
                                "obra"
                            ]
                        ),

                    "titulo_obra":
                        str(
                            obra_selecionada[
                                "titulo"
                            ]
                        ),

                    "pipe":
                        str(
                            obra_selecionada[
                                "pipe"
                            ]
                        ),

                    "lista_trello":
                        str(
                            obra_selecionada[
                                "lista"
                            ]
                        ),

                    "equipe":
                        equipe_salvar,

                    "assinatura":
                        assinatura,

                }
            )


            # ================================================
            # GERAR APONTAMENTOS
            # ================================================

            for pessoa in equipe_salvar:

                st.session_state.apontamentos.append(
                    {

                        "id":
                            len(
                                st.session_state
                                .apontamentos
                            )
                            + 1,

                        "convocacao_id":
                            convocacao_id,

                        "data":
                            str(
                                data_convocacao
                            ),

                        "unidade":
                            unidade,

                        "obra":
                            str(
                                obra_selecionada[
                                    "obra"
                                ]
                            ),

                        "titulo_obra":
                            str(
                                obra_selecionada[
                                    "titulo"
                                ]
                            ),

                        "trello_card_id":
                            str(
                                obra_selecionada[
                                    "trello_card_id"
                                ]
                            ),

                        "nome":
                            pessoa[
                                "nome"
                            ],

                        "tipo":
                            pessoa[
                                "tipo"
                            ],

                        "funcao":
                            pessoa[
                                "funcao"
                            ],

                        "frente":
                            pessoa[
                                "frente"
                            ],

                        "status":
                            "Pendente",

                        "extra":
                            0.0,

                        "observacao":
                            pessoa[
                                "observacao"
                            ],

                    }
                )


            quantidade = len(
                equipe_salvar
            )


            numero_salvo = str(
                obra_selecionada[
                    "obra"
                ]
            )


            st.session_state.equipe_rascunho = []

            st.session_state.conv_select_version += 1

            st.session_state.conv_editor_version += 1


            st.session_state.ultima_convocacao_msg = (
                "✅ Convocação criada: "
                f"{quantidade} pessoa(s) • "
                f"{unidade} • "
                f"OBRA {numero_salvo}."
            )


            st.rerun()


    else:

        st.info(
            "Selecione uma frente e "
            "adicione a mão de obra."
        )


# ============================================================
# APONTAMENTOS
# ============================================================

elif menu == "Apontamentos":

    st.subheader(
        "Apontamentos"
    )


    if not (
        st.session_state
        .apontamentos
    ):

        st.info(
            "Ainda não existe nenhuma convocação."
        )


    else:

        df = pd.DataFrame(
            st.session_state
            .apontamentos
        )


        c1, c2, c3 = st.columns(3)


        datas = sorted(
            df[
                "data"
            ]
            .unique()
            .tolist(),
            reverse=True,
        )


        data_selecionada = c1.selectbox(
            "Data",
            datas,
        )


        base_data = df[
            df["data"]
            ==
            data_selecionada
        ]


        unidades_disponiveis = sorted(
            base_data[
                "unidade"
            ]
            .unique()
            .tolist()
        )


        unidade_selecionada = c2.selectbox(
            "Unidade",
            unidades_disponiveis,
        )


        base_unidade = base_data[
            base_data[
                "unidade"
            ]
            ==
            unidade_selecionada
        ]


        obras_disponiveis = sorted(
            base_unidade[
                "obra"
            ]
            .astype(str)
            .unique()
            .tolist()
        )


        obra_filtro = c3.selectbox(
            "Obra",
            obras_disponiveis,
        )


        base = base_unidade[
            base_unidade[
                "obra"
            ]
            .astype(str)
            ==
            str(
                obra_filtro
            )
        ]


        if not base.empty:

            st.caption(
                f"OBRA {obra_filtro} — "
                f"{base['titulo_obra'].iloc[0]}"
            )


        total = len(
            base
        )


        pendentes = int(
            (
                base["status"]
                ==
                "Pendente"
            ).sum()
        )


        c1, c2, c3 = st.columns(3)


        c1.metric(
            "Convocados",
            total,
        )


        c2.metric(
            "Apontados",
            total
            -
            pendentes,
        )


        c3.metric(
            "Pendentes",
            pendentes,
        )


        for frente in (
            base[
                "frente"
            ].unique()
        ):

            st.markdown(
                f"### {frente}"
            )


            grupo = base[
                base[
                    "frente"
                ]
                ==
                frente
            ]


            for _, row in (
                grupo.iterrows()
            ):

                apontamento_id = int(
                    row[
                        "id"
                    ]
                )


                with st.container(
                    border=True
                ):

                    nome = (
                        f"**{row['nome']}**"
                    )


                    if (
                        row[
                            "tipo"
                        ]
                        ==
                        "AVULSO"
                    ):

                        nome += (
                            " • AVULSO"
                        )


                    st.markdown(
                        nome
                    )


                    st.caption(
                        f"{row['unidade']} • "
                        f"OBRA {row['obra']} • "
                        f"{row['funcao']}"
                    )


                    c1, c2, c3 = st.columns(
                        [
                            1.2,
                            1,
                            2,
                        ]
                    )


                    status = c1.selectbox(
                        "Status",
                        STATUS_APONTAMENTO,
                        index=(
                            STATUS_APONTAMENTO
                            .index(
                                row[
                                    "status"
                                ]
                            )
                        ),
                        key=(
                            "status_"
                            f"{apontamento_id}"
                        ),
                    )


                    extra = c2.number_input(
                        "Extra (R$)",
                        min_value=0.0,
                        value=float(
                            row[
                                "extra"
                            ]
                        ),
                        step=10.0,
                        key=(
                            "extra_"
                            f"{apontamento_id}"
                        ),
                    )


                    observacao = c3.text_input(
                        "Observação",
                        value=row[
                            "observacao"
                        ],
                        key=(
                            "obs_"
                            f"{apontamento_id}"
                        ),
                    )


                    if st.button(
                        "Salvar apontamento",
                        key=(
                            "salvar_"
                            f"{apontamento_id}"
                        ),
                    ):

                        for item in (
                            st.session_state
                            .apontamentos
                        ):

                            if (
                                item[
                                    "id"
                                ]
                                ==
                                apontamento_id
                            ):

                                item[
                                    "status"
                                ] = status

                                item[
                                    "extra"
                                ] = extra

                                item[
                                    "observacao"
                                ] = observacao

                                break


                        st.rerun()


# ============================================================
# MEDIÇÕES
# ============================================================

elif menu == "Medições":

    st.subheader(
        "Medições e Resultados"
    )


    st.caption(
        "Nesta etapa estamos validando "
        "convocação e apontamento. "
        "A sincronização mensal de medições "
        "será ligada depois."
    )


    c1, c2 = st.columns(2)


    mes = c1.selectbox(
        "Mês de competência",
        list(
            MESES_PT.keys()
        ),
        index=7,
        format_func=lambda x:
            MESES_PT[
                x
            ].title(),
    )


    ano = c2.number_input(
        "Ano",
        min_value=2024,
        max_value=2100,
        value=2026,
        step=1,
    )


    competencia = (
        f"{int(mes):02d}/"
        f"{int(ano)}"
    )


    lista_esperada = (
        f"MEDIÇÃO "
        f"{MESES_PT[int(mes)]} "
        f"{int(ano)}"
    )


    st.info(
        "Lista mensal que será usada "
        "no Trello: "
        f"**{lista_esperada}**"
    )


    base = (
        st.session_state
        .medicoes
        .copy()
    )


    base = base[
        base[
            "competencia"
        ]
        ==
        competencia
    ]


    if base.empty:

        st.warning(
            "Não existem dados de demonstração "
            "para esta competência."
        )


    else:

        fiec = base[
            base[
                "origem"
            ]
            ==
            "FIEC"
        ]


        fora_fiec = base[
            base[
                "origem"
            ]
            !=
            "FIEC"
        ]


        c1, c2, c3 = st.columns(3)


        c1.metric(
            "Total",
            len(
                base
            ),
        )


        c2.metric(
            "FIEC",
            len(
                fiec
            ),
        )


        c3.metric(
            "Fora FIEC",
            len(
                fora_fiec
            ),
        )


        tab1, tab2, tab3 = st.tabs(
            [
                "🏭 FIEC",
                "↗️ Fora FIEC",
                "📋 Todos",
            ]
        )


        with tab1:

            st.dataframe(
                fiec,
                use_container_width=True,
                hide_index=True,
            )


        with tab2:

            st.dataframe(
                fora_fiec,
                use_container_width=True,
                hide_index=True,
            )


        with tab3:

            st.dataframe(
                base,
                use_container_width=True,
                hide_index=True,
            )
