import json
import re
import unicodedata
from datetime import date

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BUILD = "PROTOTIPO-TRELLO-JSON-MANUAL-2026-08-27"

TRELLO_SHORTLINK = "TX8hGvmI"

st.set_page_config(
    page_title="Apontamentos APROAR",
    page_icon="🏗️",
    layout="wide",
)


TRELLO_PUBLIC_URLS = [
    f"https://trello.com/b/{TRELLO_SHORTLINK}.json",
    f"https://trello.com/b/{TRELLO_SHORTLINK}/orcamentos.json",
]


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


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>

        .block-container {
            padding-top: 1.1rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128,128,128,.18);
            border-radius: 12px;
            padding: 10px 12px;
        }

        .proto {
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

        .fonte-ok {
            padding: 9px 12px;
            border-radius: 9px;
            background: rgba(34,197,94,.07);
            border: 1px solid rgba(34,197,94,.25);
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES GERAIS
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

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip().upper()


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

    if partes:

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
    obra,
):

    titulo = (
        str(nome)
        .split("|")[0]
        .strip()
    )

    if obra:

        titulo = re.sub(
            (
                rf"^\s*OBRA\s*[:#-]?\s*"
                rf"{re.escape(obra)}"
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


# ============================================================
# PROCESSAMENTO DO JSON DO TRELLO
# ============================================================

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


def processar_json_trello(
    dados,
):

    if not isinstance(
        dados,
        dict,
    ):

        raise ValueError(
            "O arquivo enviado não parece ser "
            "um JSON de quadro do Trello."
        )


    listas_json = dados.get(
        "lists",
        [],
    )


    cards_json = dados.get(
        "cards",
        [],
    )


    if (
        not isinstance(
            listas_json,
            list,
        )
        or
        not isinstance(
            cards_json,
            list,
        )
    ):

        raise ValueError(
            "O JSON não possui as estruturas "
            "'lists' e 'cards' esperadas."
        )


    nomes_validos = {
        normalizar(
            nome
        )
        for nome in (
            LISTAS_OBRAS_ATIVAS
        )
    }


    listas_validas = {

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

        for lista in listas_json

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


    if not listas_validas:

        raise ValueError(
            "O JSON foi lido, mas não encontrei "
            "as listas 'EM EXECUÇÃO' ou "
            "'APROVADO - AGUARDANDO EXECUÇÃO'."
        )


    obras = []


    for card in cards_json:

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


        if id_lista not in listas_validas:

            continue


        item = parsear_card(
            card,
            listas_validas[
                id_lista
            ],
        )


        if item:

            obras.append(
                item
            )


    df = pd.DataFrame(
        obras,
        columns=[
            "trello_card_id",
            "short_link",
            "nome_trello",
            "obra",
            "titulo",
            "unidade",
            "pipe",
            "lista",
        ],
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


# ============================================================
# TENTATIVA DE LEITURA PÚBLICA
# ============================================================

@st.cache_data(
    ttl=60,
    show_spinner=False,
)
def carregar_trello_publico():

    ultimo_erro = ""


    for url in TRELLO_PUBLIC_URLS:

        try:

            resposta = requests.get(
                url,
                timeout=15,
                allow_redirects=True,
                headers={
                    "User-Agent":
                        "Mozilla/5.0",

                    "Accept":
                        "application/json,text/plain,*/*",
                },
            )


            resposta.raise_for_status()


            dados = resposta.json()


            df = processar_json_trello(
                dados
            )


            return (
                df,
                url,
            )


        except Exception as erro:

            ultimo_erro = str(
                erro
            )


    raise RuntimeError(
        "Não foi possível ler o quadro "
        "publicamente. "
        f"Último erro: {ultimo_erro}"
    )


def tentar_trello_publico(
    forcar=False,
):

    if forcar:

        carregar_trello_publico.clear()


    try:

        df, url = (
            carregar_trello_publico()
        )


        st.session_state.obras_trello = (
            df
        )


        st.session_state.trello_fonte = (
            "LEITURA PÚBLICA"
        )


        st.session_state.trello_ok = (
            True
        )


        st.session_state.trello_erro = (
            ""
        )


        st.session_state.trello_url = (
            url
        )


        return True


    except Exception as erro:

        st.session_state.trello_ok = (
            False
        )


        st.session_state.trello_erro = (
            str(
                erro
            )
        )


        return False


# ============================================================
# DADOS TEMPORÁRIOS
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


    if "trello_fonte" not in st.session_state:

        st.session_state.trello_fonte = ""


    if "medicoes" not in st.session_state:

        st.session_state.medicoes = (
            pd.DataFrame(
                [

                    {
                        "id": 1,
                        "competencia":
                            "08/2026",
                        "obra":
                            "2450.1",
                        "servico":
                            "CONSERTAR CERCA ELÉTRICA",
                        "unidade":
                            "CENTRO",
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
                        "competencia":
                            "08/2026",
                        "obra":
                            "2467",
                        "servico":
                            "MANUTENÇÃO DOS BANHEIROS",
                        "unidade":
                            "BARRA",
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

                ]
            )
        )


def compatibilizar_sessao_antiga():

    for item in st.session_state.get(
        "apontamentos",
        [],
    ):

        item.setdefault(
            "unidade",
            "",
        )

        item.setdefault(
            "obra",
            "",
        )

        item.setdefault(
            "titulo_obra",
            "",
        )

        item.setdefault(
            "trello_card_id",
            "",
        )

        item.setdefault(
            "tipo",
            "FIXO",
        )

        item.setdefault(
            "funcao",
            "",
        )

        item.setdefault(
            "frente",
            "OUTROS",
        )

        item.setdefault(
            "status",
            "Pendente",
        )

        item.setdefault(
            "extra",
            0.0,
        )

        item.setdefault(
            "observacao",
            "",
        )


    for item in st.session_state.get(
        "convocacoes",
        [],
    ):

        item.setdefault(
            "unidade",
            "",
        )

        item.setdefault(
            "obra",
            "",
        )

        item.setdefault(
            "titulo_obra",
            "",
        )

        item.setdefault(
            "trello_card_id",
            "",
        )

        item.setdefault(
            "pipe",
            "",
        )

        item.setdefault(
            "lista_trello",
            "",
        )


iniciar_dados()

compatibilizar_sessao_antiga()


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
    '<div class="proto">'
    '🧪 <b>MODO PROTÓTIPO — SEM SUPABASE</b><br>'
    'O Trello pode ser carregado por JSON exportado manualmente.<br>'
    f'Build: <code>{BUILD}</code>'
    '</div>',
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

            "trello_url",

            "trello_fonte",

        ]


        for chave in chaves:

            st.session_state.pop(
                chave,
                None,
            )


        carregar_trello_publico.clear()


        iniciar_dados()

        compatibilizar_sessao_antiga()


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
            item.get(
                "equipe",
                [],
            )
        )
        for item in (
            st.session_state
            .convocacoes
        )
    )


    total_pendentes = sum(
        1
        for item in (
            st.session_state
            .apontamentos
        )
        if item.get(
            "status"
        )
        ==
        "Pendente"
    )


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "Colaboradores",
        len(
            st.session_state
            .colaboradores
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
        "Obras carregadas",
        len(
            st.session_state
            .obras_trello
        ),
    )


    st.markdown(
        "### Fluxo"
    )


    st.write(
        "JSON/Trello → Unidade + Obra → "
        "Convocação → Apontamento → "
        "Medições / Resultados"
    )


    if not (
        st.session_state
        .obras_trello
        .empty
    ):

        st.caption(
            f"Fonte atual das obras: "
            f"{st.session_state.trello_fonte or 'não informada'}"
        )


    if st.session_state.apontamentos:

        df = pd.DataFrame(
            st.session_state
            .apontamentos
        )


        for coluna in [

            "data",

            "unidade",

            "obra",

            "nome",

            "frente",

            "status",

        ]:

            if coluna not in df.columns:

                df[
                    coluna
                ] = ""


        pendentes = df[
            df[
                "status"
            ]
            ==
            "Pendente"
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


                novo_id = (
                    1
                    if df.empty
                    else int(
                        df[
                            "id"
                        ].max()
                    )
                    +
                    1
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
                                or
                                "NÃO INFORMADA",

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
        +
        frentes_existentes,
    )


    base = (
        st.session_state
        .colaboradores
        .copy()
    )


    if filtro != "Todas":

        base = base[
            base[
                "frente"
            ]
            ==
            filtro
        ]


    base = base.rename(
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
        base[
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
        "Carregue o JSON do Trello, selecione a unidade, "
        "relacione a obra e monte a equipe."
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
    # FONTE DAS OBRAS
    # ========================================================

    with st.container(
        border=True
    ):

        st.markdown(
            "#### Obras do Trello"
        )


        st.caption(
            "Envie o JSON exportado do quadro. "
            "O sistema considera somente "
            "EM EXECUÇÃO e "
            "APROVADO - AGUARDANDO EXECUÇÃO."
        )


        arquivo_json = st.file_uploader(
            "Enviar JSON exportado do Trello",
            type=[
                "json"
            ],
            key="trello_json_upload",
            help=(
                "Exporte o quadro em JSON no Trello "
                "e envie o arquivo aqui."
            ),
        )


        if arquivo_json is not None:

            try:

                dados = json.load(
                    arquivo_json
                )


                df_obras = (
                    processar_json_trello(
                        dados
                    )
                )


                st.session_state.obras_trello = (
                    df_obras
                )


                st.session_state.trello_fonte = (
                    "JSON ENVIADO MANUALMENTE"
                )


                st.session_state.trello_ok = (
                    True
                )


                st.session_state.trello_erro = (
                    ""
                )


                st.success(
                    f"✅ JSON carregado: "
                    f"{len(df_obras)} "
                    "obra(s) válida(s)."
                )


                if not df_obras.empty:

                    sem_unidade = int(
                        (
                            df_obras[
                                "unidade"
                            ]
                            ==
                            ""
                        ).sum()
                    )


                    if sem_unidade:

                        st.warning(
                            f"{sem_unidade} card(s) "
                            "foram lidos, mas a unidade "
                            "não foi identificada "
                            "automaticamente."
                        )


            except Exception as erro:

                st.error(
                    "Não consegui interpretar esse JSON."
                )


                st.caption(
                    str(
                        erro
                    )
                )


        c1, c2 = st.columns(
            [
                2,
                1,
            ]
        )


        with c1:

            if not (
                st.session_state
                .obras_trello
                .empty
            ):

                st.markdown(
                    '<div class="fonte-ok">'
                    f'✅ Obras disponíveis: '
                    f'<b>{len(st.session_state.obras_trello)}</b> '
                    f'• Fonte: '
                    f'{st.session_state.trello_fonte}'
                    '</div>',
                    unsafe_allow_html=True,
                )


            else:

                st.info(
                    "Ainda não há obras carregadas."
                )


        with c2:

            if st.button(
                "Tentar leitura pública",
                use_container_width=True,
            ):

                with st.spinner(
                    "Tentando acessar o quadro..."
                ):

                    tentar_trello_publico(
                        forcar=True
                    )


                st.rerun()


        if (
            not st.session_state.get(
                "trello_ok",
                True,
            )
            and
            st.session_state.get(
                "trello_erro"
            )
        ):

            with st.expander(
                "Erro da tentativa pública"
            ):

                st.write(
                    st.session_state
                    .trello_erro
                )


    # ========================================================
    # DADOS DA CONVOCAÇÃO
    # ========================================================

    with st.container(
        border=True
    ):

        c1, c2, c3 = st.columns(
            [
                1,
                1.15,
                1.6,
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

            obras_unidade = obras_trello[
                obras_trello[
                    "unidade"
                ]
                ==
                unidade
            ].copy()


        c_obra, c_resultado = st.columns(
            [
                1,
                2.2,
            ]
        )


        numero_digitado = c_obra.text_input(
            "Nº da obra",
            placeholder="Ex.: 140",
            key="conv_numero_obra",
            help=(
                "Digite o número da obra. "
                "O sistema procura no JSON carregado."
            ),
        ).strip()


        obra_selecionada = None


        if numero_digitado:

            candidatos = obras_unidade[
                obras_unidade[
                    "obra"
                ]
                .astype(str)
                .str.startswith(
                    numero_digitado,
                    na=False,
                )
            ].copy()


            exatos = candidatos[
                candidatos[
                    "obra"
                ]
                .astype(str)
                ==
                numero_digitado
            ].copy()


            if len(
                exatos
            ) == 1:

                obra_selecionada = (
                    exatos.iloc[
                        0
                    ]
                )


            elif len(
                exatos
            ) > 1:

                opcoes = {

                    (
                        f"OBRA {item.obra} — "
                        f"{item.titulo} | "
                        f"{item.lista}"
                    ):
                    item.trello_card_id

                    for item in (
                        exatos.itertuples()
                    )
                }


                escolha = (
                    c_resultado
                    .selectbox(
                        "Correspondências",
                        list(
                            opcoes.keys()
                        ),
                        key="obra_exata_opcoes",
                    )
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
                        f"OBRA {item.obra} — "
                        f"{item.titulo}"
                    ):
                    item.trello_card_id

                    for item in (
                        candidatos.itertuples()
                    )
                }


                escolha = (
                    c_resultado
                    .selectbox(
                        "Obras encontradas",
                        list(
                            opcoes.keys()
                        ),
                        key="obra_parcial_opcoes",
                    )
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


            elif not obras_trello.empty:

                c_resultado.warning(
                    f"Nenhuma obra "
                    f"'{numero_digitado}' "
                    f"foi encontrada em "
                    f"{unidade}."
                )


        elif not obras_trello.empty:

            c_resultado.caption(
                f"{len(obras_unidade)} "
                f"obra(s) disponível(is) "
                f"em {unidade}."
            )


        if obra_selecionada is not None:

            pipe = str(
                obra_selecionada[
                    "pipe"
                ]
            ).strip()


            pipe_txt = (
                f" • PIPE {pipe}"
                if pipe
                else
                ""
            )


            st.markdown(
                '<div class="obra-ok">'
                f'✅ <b>OBRA '
                f'{obra_selecionada["obra"]}</b> — '
                f'{obra_selecionada["titulo"]}<br>'
                f'{obra_selecionada["unidade"]} • '
                f'{obra_selecionada["lista"]}'
                f'{pipe_txt}'
                '</div>',
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
                colaboradores[
                    "ativo"
                ]
                ==
                True
            ][
                "frente"
            ]
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


        grupo = colaboradores[
            (
                colaboradores[
                    "frente"
                ]
                ==
                frente_escolhida
            )
            &
            (
                colaboradores[
                    "ativo"
                ]
                ==
                True
            )
        ].copy()


        ids_ja_adicionados = {

            item[
                "colaborador_id"
            ]

            for item in (
                st.session_state
                .equipe_rascunho
            )

            if item.get(
                "colaborador_id"
            )
            is not None
        }


        grupo = grupo[
            ~grupo[
                "id"
            ].isin(
                ids_ja_adicionados
            )
        ]


        labels = {

            (
                f"{item.nome} — "
                f"{item.funcao}"
            ):
            int(
                item.id
            )

            for item in (
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
                    labels[
                        label
                    ]
                )


                row = colaboradores[
                    colaboradores[
                        "id"
                    ]
                    ==
                    colaborador_id
                ].iloc[0]


                st.session_state.equipe_rascunho.append(
                    {

                        "colaborador_id":
                            int(
                                colaborador_id
                            ),

                        "nome":
                            row[
                                "nome"
                            ],

                        "funcao_base":
                            row[
                                "funcao"
                            ],

                        "frente_base":
                            row[
                                "frente"
                            ],

                        "funcao_dia":
                            row[
                                "funcao"
                            ],

                        "frente_dia":
                            row[
                                "frente"
                            ],

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
        # MÃO DE OBRA AVULSA
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

                    nome = str(
                        avulso.get(
                            "Nome",
                            "",
                        )
                    ).strip()


                    if not nome:

                        continue


                    funcao = str(
                        avulso.get(
                            "Função",
                            "",
                        )
                    ).strip()


                    frente = str(
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
                                nome.upper(),

                            "funcao_base":
                                "AVULSO",

                            "frente_base":
                                "AVULSO",

                            "funcao_dia":
                                funcao
                                or
                                "NÃO INFORMADA",

                            "frente_dia":
                                frente
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
                        item[
                            "nome"
                        ],

                    "Função base":
                        item[
                            "funcao_base"
                        ],

                    "Função no dia":
                        item[
                            "funcao_dia"
                        ],

                    "Frente no dia":
                        item[
                            "frente_dia"
                        ],

                    "Observação":
                        item.get(
                            "observacao",
                            "",
                        ),

                    "Remover":
                        False,

                }

                for item in (
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
                            "ou a frente for alterada."
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
                row[
                    "Remover"
                ]
            ):

                continue


            original = (
                st.session_state
                .equipe_rascunho[
                    i
                ]
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
                    "Digite e relacione uma obra válida "
                    "do JSON do Trello."
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


            # =================================================
            # OBSERVAÇÃO OBRIGATÓRIA
            # =================================================

            sem_observacao = []


            for pessoa in (
                st.session_state
                .equipe_rascunho
            ):

                mudou_funcao = (

                    pessoa[
                        "tipo"
                    ]
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

                    pessoa[
                        "tipo"
                    ]
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

                    sem_observacao.append(
                        pessoa[
                            "nome"
                        ]
                    )


            if sem_observacao:

                st.error(
                    "Informe uma observação para "
                    "quem foi realocado: "
                    +
                    ", ".join(
                        sem_observacao
                    )
                )

                st.stop()


            # =================================================
            # BLOQUEIO DE DUPLICAÇÃO
            # =================================================

            nomes_chave = sorted(
                [

                    (
                        f"{item['tipo']}|"
                        f"{item['nome']}|"
                        f"{item['funcao_dia']}|"
                        f"{item['frente_dia']}"
                    )

                    for item in (
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

                item.get(
                    "assinatura"
                )
                ==
                assinatura

                for item in (
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


            # =================================================
            # SALVAR CONVOCAÇÃO
            # =================================================

            convocacao_id = (
                len(
                    st.session_state
                    .convocacoes
                )
                +
                1
            )


            equipe_salvar = [

                {

                    "colaborador_id":
                        item[
                            "colaborador_id"
                        ],

                    "nome":
                        item[
                            "nome"
                        ],

                    "funcao":
                        item[
                            "funcao_dia"
                        ],

                    "frente":
                        item[
                            "frente_dia"
                        ],

                    "tipo":
                        item[
                            "tipo"
                        ],

                    "observacao":
                        item[
                            "observacao"
                        ],

                }

                for item in (
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


            # =================================================
            # GERAR APONTAMENTOS
            # =================================================

            for pessoa in equipe_salvar:

                st.session_state.apontamentos.append(
                    {

                        "id":
                            len(
                                st.session_state
                                .apontamentos
                            )
                            +
                            1,

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


            numero_obra = str(
                obra_selecionada[
                    "obra"
                ]
            )


            st.session_state.equipe_rascunho = []


            st.session_state.conv_select_version += 1

            st.session_state.conv_editor_version += 1


            st.session_state.ultima_convocacao_msg = (
                f"✅ Convocação criada: "
                f"{quantidade} pessoa(s) • "
                f"{unidade} • "
                f"OBRA {numero_obra}."
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


        colunas = {

            "data":
                "",

            "unidade":
                "",

            "obra":
                "",

            "titulo_obra":
                "",

            "nome":
                "",

            "tipo":
                "FIXO",

            "funcao":
                "",

            "frente":
                "OUTROS",

            "status":
                "Pendente",

            "extra":
                0.0,

            "observacao":
                "",

        }


        for coluna, padrao in (
            colunas.items()
        ):

            if coluna not in df.columns:

                df[
                    coluna
                ] = padrao


        c1, c2, c3 = st.columns(3)


        datas = sorted(
            df[
                "data"
            ]
            .astype(str)
            .unique()
            .tolist(),
            reverse=True,
        )


        data_selecionada = c1.selectbox(
            "Data",
            datas,
        )


        base_data = df[
            df[
                "data"
            ]
            .astype(str)
            ==
            str(
                data_selecionada
            )
        ].copy()


        unidades_disponiveis = sorted(
            [

                item

                for item in (
                    base_data[
                        "unidade"
                    ]
                    .fillna("")
                    .astype(str)
                    .unique()
                    .tolist()
                )

                if item.strip()

            ]
        )


        if not unidades_disponiveis:

            st.warning(
                "Os apontamentos em memória foram "
                "criados por uma versão antiga. "
                "Clique em 'Restaurar demonstração' "
                "para limpar os testes."
            )

            st.stop()


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
        ].copy()


        obras_disponiveis = sorted(
            [

                item

                for item in (
                    base_unidade[
                        "obra"
                    ]
                    .fillna("")
                    .astype(str)
                    .unique()
                    .tolist()
                )

                if item.strip()

            ]
        )


        if not obras_disponiveis:

            st.warning(
                "Os apontamentos antigos não possuem "
                "número de obra associado."
            )

            st.stop()


        obra_selecionada = c3.selectbox(
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
                obra_selecionada
            )
        ].copy()


        if not base.empty:

            titulo = str(
                base[
                    "titulo_obra"
                ]
                .iloc[0]
            ).strip()


            if titulo:

                st.caption(
                    f"OBRA {obra_selecionada} — "
                    f"{titulo}"
                )


        total = len(
            base
        )


        pendentes = int(
            (
                base[
                    "status"
                ]
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


        st.markdown(
            "### Equipe"
        )


        tabela = base[
            [
                "id",
                "nome",
                "tipo",
                "funcao",
                "frente",
                "status",
                "extra",
                "observacao",
            ]
        ].copy()


        tabela = tabela.rename(
            columns={

                "nome":
                    "Nome",

                "tipo":
                    "Vínculo",

                "funcao":
                    "Função",

                "frente":
                    "Frente",

                "status":
                    "Status",

                "extra":
                    "Extra (R$)",

                "observacao":
                    "Observação",

            }
        )


        editada = st.data_editor(
            tabela,
            use_container_width=True,
            hide_index=True,
            disabled=[
                "id",
                "Nome",
                "Vínculo",
                "Função",
                "Frente",
            ],
            column_config={

                "id":
                    None,

                "Status":
                    st.column_config
                    .SelectboxColumn(
                        "Status",
                        options=(
                            STATUS_APONTAMENTO
                        ),
                    ),

                "Extra (R$)":
                    st.column_config
                    .NumberColumn(
                        "Extra (R$)",
                        min_value=0.0,
                        step=10.0,
                    ),

            },
            key=(
                f"apont_"
                f"{data_selecionada}_"
                f"{unidade_selecionada}_"
                f"{obra_selecionada}"
            ),
        )


        if st.button(
            "Salvar apontamentos",
            type="primary",
            use_container_width=True,
        ):

            por_id = {

                int(
                    row[
                        "id"
                    ]
                ):
                row

                for _, row in (
                    editada.iterrows()
                )
            }


            for item in (
                st.session_state
                .apontamentos
            ):

                item_id = int(
                    item[
                        "id"
                    ]
                )


                if item_id not in por_id:

                    continue


                row = por_id[
                    item_id
                ]


                item[
                    "status"
                ] = str(
                    row[
                        "Status"
                    ]
                )


                if pd.notna(
                    row[
                        "Extra (R$)"
                    ]
                ):

                    item[
                        "extra"
                    ] = float(
                        row[
                            "Extra (R$)"
                        ]
                    )


                else:

                    item[
                        "extra"
                    ] = 0.0


                if pd.notna(
                    row[
                        "Observação"
                    ]
                ):

                    item[
                        "observacao"
                    ] = str(
                        row[
                            "Observação"
                        ]
                    )


                else:

                    item[
                        "observacao"
                    ] = ""


            st.success(
                "✅ Apontamentos salvos."
            )


# ============================================================
# MEDIÇÕES
# ============================================================

elif menu == "Medições":

    st.subheader(
        "Medições e Resultados"
    )


    st.caption(
        "Por enquanto esta tela continua "
        "em modo de protótipo."
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


    lista = (
        f"MEDIÇÃO "
        f"{MESES_PT[int(mes)]} "
        f"{int(ano)}"
    )


    st.info(
        "Lista mensal que será usada "
        f"no Trello: **{lista}**"
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

        st.dataframe(
            base,
            use_container_width=True,
            hide_index=True,
        )
