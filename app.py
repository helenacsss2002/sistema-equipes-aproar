import re
import unicodedata
from datetime import date

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BUILD = "PROTOTIPO-SEM-SUPABASE-2026-08-26"

st.set_page_config(
    page_title="Apontamentos APROAR",
    page_icon="🏗️",
    layout="wide",
)


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
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 14px;
        padding: 12px;
    }

    .modo-prototipo {
        padding: 11px 14px;
        border-radius: 10px;
        background: rgba(245,158,11,.08);
        border: 1px solid rgba(245,158,11,.35);
        margin-top: 8px;
        margin-bottom: 18px;
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
        caractere
        for caractere in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caractere) != "Mn"
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip().upper()


def inferir_frente(funcao):

    funcao = normalizar(funcao)

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

        if any(termo in funcao for termo in termos):
            return frente

    return "OUTROS"


def iniciar_dados():

    # --------------------------------------------------------
    # COLABORADORES
    # --------------------------------------------------------

    if "colaboradores" not in st.session_state:

        st.session_state.colaboradores = pd.DataFrame(
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
                    "frente": "ALVENARIA / PEDREIROS",
                    "ativo": True,
                },
                {
                    "id": 6,
                    "nome": "CARLOS",
                    "funcao": "Pedreiro",
                    "frente": "ALVENARIA / PEDREIROS",
                    "ativo": True,
                },
                {
                    "id": 7,
                    "nome": "MARCOS",
                    "funcao": "Eletricista",
                    "frente": "ELÉTRICA",
                    "ativo": True,
                },
                {
                    "id": 8,
                    "nome": "LUCAS",
                    "funcao": "Encanador",
                    "frente": "HIDRÁULICA",
                    "ativo": True,
                },
                {
                    "id": 9,
                    "nome": "RAFAEL",
                    "funcao": "Servente",
                    "frente": "APOIO / SERVIÇOS GERAIS",
                    "ativo": True,
                },
            ]
        )

    # --------------------------------------------------------
    # OBRAS DE DEMONSTRAÇÃO
    # --------------------------------------------------------

    if "obras" not in st.session_state:

        st.session_state.obras = pd.DataFrame(
            [
                {
                    "id": "obra_2568",
                    "obra": "2568",
                    "titulo": "REPARO NO PAVIMENTO",
                    "unidade": "SENAI BARRA DO CEARÁ",
                },
                {
                    "id": "obra_2577",
                    "obra": "2577",
                    "titulo": "MANUTENÇÃO HIDRÁULICA",
                    "unidade": "SESI CENTRO",
                },
                {
                    "id": "obra_2582",
                    "obra": "2582",
                    "titulo": "COMPLEMENTO INFRA LABORATÓRIO",
                    "unidade": "SENAI HORIZONTE",
                },
            ]
        )

    # --------------------------------------------------------
    # CONVOCAÇÕES
    # --------------------------------------------------------

    if "convocacoes" not in st.session_state:
        st.session_state.convocacoes = []

    # --------------------------------------------------------
    # APONTAMENTOS
    # --------------------------------------------------------

    if "apontamentos" not in st.session_state:
        st.session_state.apontamentos = []

    # --------------------------------------------------------
    # MEDIÇÕES
    # --------------------------------------------------------

    if "medicoes" not in st.session_state:

        st.session_state.medicoes = pd.DataFrame(
            [
                {
                    "id": 1,
                    "competencia": "08/2026",
                    "obra": "2450.1",
                    "servico": "CONSERTAR CERCA ELÉTRICA",
                    "unidade": "SESI CENTRO",
                    "pipe": "1357123706",
                    "origem": "FIEC",
                    "status": "Pendente",
                    "valor_aprovado": 0.0,
                    "resultado": 0.0,
                },
                {
                    "id": 2,
                    "competencia": "08/2026",
                    "obra": "2467",
                    "servico": "MANUTENÇÃO DOS BANHEIROS",
                    "unidade": "SENAI BARRA DO CEARÁ",
                    "pipe": "1377057280",
                    "origem": "FIEC",
                    "status": "Pendente",
                    "valor_aprovado": 0.0,
                    "resultado": 0.0,
                },
                {
                    "id": 3,
                    "competencia": "08/2026",
                    "obra": "—",
                    "servico": "SUBCONTRATAÇÃO / COMPRA DE MATERIAIS",
                    "unidade": "—",
                    "pipe": "1427648041",
                    "origem": "QUARTEIRIZADOS",
                    "status": "Pendente",
                    "valor_aprovado": 0.0,
                    "resultado": 0.0,
                },
            ]
        )


iniciar_dados()


# ============================================================
# CABEÇALHO
# ============================================================

st.title("🏗️ Controle de Equipes e Apontamentos")

st.caption("APROAR Engenharia")


st.markdown(
    f"""
    <div class="modo-prototipo">

    🧪 <b>MODO PROTÓTIPO — SEM SUPABASE</b><br>

    Nenhuma informação está sendo enviada para banco de dados.<br>

    Build:
    <code>{BUILD}</code>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MENU LATERAL
# ============================================================

with st.sidebar:

    st.header("⚙️ Operações")

    engenheiro_atual = st.text_input(
        "Engenheiro / supervisor",
        value=st.session_state.get(
            "engenheiro_atual",
            "",
        ),
    )

    st.session_state.engenheiro_atual = engenheiro_atual

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
        "Restaurar dados de demonstração",
        use_container_width=True,
    ):

        chaves = [
            "colaboradores",
            "obras",
            "convocacoes",
            "apontamentos",
            "medicoes",
        ]

        for chave in chaves:

            st.session_state.pop(
                chave,
                None,
            )

        iniciar_dados()

        st.rerun()


# ============================================================
# VISÃO GERAL
# ============================================================

if menu == "Visão Geral":

    st.subheader(
        "Visão Geral"
    )

    total_colaboradores = len(
        st.session_state.colaboradores
    )

    total_convocados = sum(
        len(convocacao["equipe"])
        for convocacao in st.session_state.convocacoes
    )

    total_pendentes = sum(
        1
        for apontamento in st.session_state.apontamentos
        if apontamento["status"] == "Pendente"
    )

    total_medicoes = len(
        st.session_state.medicoes
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Colaboradores",
        total_colaboradores,
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
        "Itens de medição",
        total_medicoes,
    )

    st.markdown(
        "### Fluxo do sistema"
    )

    st.write(
        "Colaboradores → Convocação por frente → "
        "Apontamento → Medições / Resultados"
    )

    if st.session_state.apontamentos:

        df_pendencias = pd.DataFrame(
            st.session_state.apontamentos
        )

        df_pendencias = df_pendencias[
            df_pendencias["status"]
            == "Pendente"
        ]

        if not df_pendencias.empty:

            st.markdown(
                "### Pendências"
            )

            st.dataframe(
                df_pendencias[
                    [
                        "data",
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
        "A função cadastrada define em qual grupo "
        "a pessoa aparece inicialmente na convocação."
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

                df = st.session_state.colaboradores

                if df.empty:
                    novo_id = 1
                else:
                    novo_id = int(
                        df["id"].max()
                    ) + 1

                novo = pd.DataFrame(
                    [
                        {
                            "id": novo_id,
                            "nome": nome.strip().upper(),
                            "funcao": funcao.strip()
                            or "NÃO INFORMADA",
                            "frente": frente,
                            "ativo": True,
                        }
                    ]
                )

                st.session_state.colaboradores = pd.concat(
                    [
                        df,
                        novo,
                    ],
                    ignore_index=True,
                )

                st.rerun()

    frentes_existentes = sorted(
        st.session_state.colaboradores[
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

    base = st.session_state.colaboradores.copy()

    if filtro != "Todas":

        base = base[
            base["frente"]
            == filtro
        ]

    tabela = base.rename(
        columns={
            "nome": "Nome",
            "funcao": "Função",
            "frente": "Frente",
            "ativo": "Ativo",
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
        "Selecione somente as frentes necessárias "
        "e depois escolha as pessoas de cada uma."
    )

    c1, c2 = st.columns(2)

    data_convocacao = c1.date_input(
        "Data da convocação",
        value=date.today(),
    )

    engenheiro = c2.text_input(
        "Engenheiro responsável",
        value=st.session_state.get(
            "engenheiro_atual",
            "",
        ),
    )

    obras = st.session_state.obras

    obra_map = {}

    for obra in obras.itertuples():

        label = (
            f"OBRA {obra.obra} — "
            f"{obra.titulo} | "
            f"{obra.unidade}"
        )

        obra_map[label] = obra.id

    obra_label = st.selectbox(
        "Obra / serviço",
        list(
            obra_map.keys()
        ),
    )

    obra_id = obra_map[
        obra_label
    ]

    obra_row = obras[
        obras["id"]
        == obra_id
    ].iloc[0]

    st.markdown(
        "### 1. Frentes necessárias"
    )

    frentes_disponiveis = sorted(
        st.session_state.colaboradores[
            "frente"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    frentes_selecionadas = st.multiselect(
        "Escolha somente o que será necessário",
        frentes_disponiveis,
        placeholder=(
            "Ex.: PINTURA, "
            "ELÉTRICA..."
        ),
    )

    equipe = []

    if frentes_selecionadas:

        st.markdown(
            "### 2. Monte a equipe"
        )

        for frente in frentes_selecionadas:

            grupo = (
                st.session_state.colaboradores[
                    (
                        st.session_state.colaboradores[
                            "frente"
                        ]
                        == frente
                    )
                    &
                    (
                        st.session_state.colaboradores[
                            "ativo"
                        ]
                        == True
                    )
                ]
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"#### {frente}"
                )

                st.caption(
                    f"{len(grupo)} "
                    "colaborador(es) disponíveis"
                )

                labels = {}

                for pessoa in grupo.itertuples():

                    label = (
                        f"{pessoa.nome} — "
                        f"{pessoa.funcao}"
                    )

                    labels[
                        label
                    ] = int(
                        pessoa.id
                    )

                selecionados = st.multiselect(
                    "Selecionar colaboradores",
                    list(
                        labels.keys()
                    ),
                    key=f"grupo_{frente}",
                )

                for label in selecionados:

                    colaborador_id = labels[
                        label
                    ]

                    row = grupo[
                        grupo["id"]
                        == colaborador_id
                    ].iloc[0]

                    equipe.append(
                        {
                            "colaborador_id":
                                colaborador_id,

                            "nome":
                                row["nome"],

                            "funcao":
                                row["funcao"],

                            "frente":
                                row["frente"],

                            "tipo":
                                "FIXO",
                        }
                    )

    # --------------------------------------------------------
    # COLABORADOR FORA DA FRENTE
    # --------------------------------------------------------

    with st.expander(
        "↔️ Adicionar colaborador de outra frente"
    ):

        ids_usados = {
            pessoa[
                "colaborador_id"
            ]
            for pessoa in equipe
        }

        restantes = (
            st.session_state.colaboradores[
                ~st.session_state.colaboradores[
                    "id"
                ].isin(
                    ids_usados
                )
            ]
        )

        labels = {}

        for pessoa in restantes.itertuples():

            label = (
                f"{pessoa.nome} — "
                f"{pessoa.funcao} | "
                f"{pessoa.frente}"
            )

            labels[
                label
            ] = int(
                pessoa.id
            )

        outros = st.multiselect(
            "Buscar em toda a base",
            list(
                labels.keys()
            ),
            key="outros_colaboradores",
        )

        for label in outros:

            colaborador_id = labels[
                label
            ]

            row = restantes[
                restantes["id"]
                == colaborador_id
            ].iloc[0]

            equipe.append(
                {
                    "colaborador_id":
                        colaborador_id,

                    "nome":
                        row["nome"],

                    "funcao":
                        row["funcao"],

                    "frente":
                        row["frente"],

                    "tipo":
                        "FIXO",
                }
            )

    # --------------------------------------------------------
    # REMOVE DUPLICADOS
    # --------------------------------------------------------

    equipe_unica = {}

    for pessoa in equipe:

        equipe_unica[
            pessoa["colaborador_id"]
        ] = pessoa

    equipe = list(
        equipe_unica.values()
    )

    # --------------------------------------------------------
    # AJUSTAR FUNÇÃO / FRENTE
    # --------------------------------------------------------

    equipe_final = []

    if equipe:

        st.markdown(
            "### 3. Confira função e frente"
        )

        st.caption(
            "Alterar aqui não altera o cadastro "
            "principal do colaborador."
        )

        for pessoa in equipe:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**{pessoa['nome']}**"
                )

                st.caption(
                    f"Cadastro: "
                    f"{pessoa['funcao']} • "
                    f"{pessoa['frente']}"
                )

                c1, c2 = st.columns(2)

                funcao_dia = c1.text_input(
                    "Função nesta convocação",
                    value=pessoa[
                        "funcao"
                    ],
                    key=(
                        "funcao_"
                        f"{pessoa['colaborador_id']}"
                    ),
                )

                opcoes_frente = list(
                    dict.fromkeys(
                        [
                            pessoa[
                                "frente"
                            ]
                        ]
                        + FRENTES
                    )
                )

                frente_dia = c2.selectbox(
                    "Frente nesta convocação",
                    opcoes_frente,
                    key=(
                        "frente_"
                        f"{pessoa['colaborador_id']}"
                    ),
                )

                equipe_final.append(
                    {
                        **pessoa,
                        "funcao":
                            funcao_dia,
                        "frente":
                            frente_dia,
                    }
                )

    # --------------------------------------------------------
    # AVULSOS
    # --------------------------------------------------------

    st.markdown(
        "### 4. Mão de obra avulsa"
    )

    st.caption(
        "Avulsos pertencem somente a esta convocação "
        "e não entram na base fixa."
    )

    avulsos = st.data_editor(
        pd.DataFrame(
            [
                {
                    "Nome": "",
                    "Função": "",
                    "Frente": "OUTROS",
                }
            ]
        ),
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Frente":
                st.column_config.SelectboxColumn(
                    "Frente",
                    options=FRENTES,
                )
        },
    )

    if st.button(
        "Criar convocação",
        type="primary",
        use_container_width=True,
    ):

        if not engenheiro.strip():

            st.error(
                "Informe o engenheiro responsável."
            )

        else:

            equipe_salvar = list(
                equipe_final
            )

            for _, avulso in avulsos.iterrows():

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

                equipe_salvar.append(
                    {
                        "colaborador_id":
                            None,

                        "nome":
                            nome_avulso.upper(),

                        "funcao":
                            funcao_avulso
                            or "NÃO INFORMADA",

                        "frente":
                            frente_avulso
                            or "OUTROS",

                        "tipo":
                            "AVULSO",
                    }
                )

            if not equipe_salvar:

                st.error(
                    "Selecione pelo menos "
                    "uma pessoa."
                )

            else:

                convocacao_id = (
                    len(
                        st.session_state.convocacoes
                    )
                    + 1
                )

                st.session_state.convocacoes.append(
                    {
                        "id":
                            convocacao_id,

                        "data":
                            str(
                                data_convocacao
                            ),

                        "engenheiro":
                            engenheiro.strip(),

                        "obra":
                            obra_row[
                                "obra"
                            ],

                        "servico":
                            obra_row[
                                "titulo"
                            ],

                        "equipe":
                            equipe_salvar,
                    }
                )

                for pessoa in equipe_salvar:

                    apontamento_id = (
                        len(
                            st.session_state.apontamentos
                        )
                        + 1
                    )

                    st.session_state.apontamentos.append(
                        {
                            "id":
                                apontamento_id,

                            "convocacao_id":
                                convocacao_id,

                            "data":
                                str(
                                    data_convocacao
                                ),

                            "obra":
                                obra_row[
                                    "obra"
                                ],

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
                                "",
                        }
                    )

                st.success(
                    f"Convocação criada com "
                    f"{len(equipe_salvar)} "
                    "pessoa(s)."
                )

                st.rerun()


# ============================================================
# APONTAMENTOS
# ============================================================

elif menu == "Apontamentos":

    st.subheader(
        "Apontamentos"
    )

    if not st.session_state.apontamentos:

        st.info(
            "Ainda não existe nenhuma convocação."
        )

    else:

        df = pd.DataFrame(
            st.session_state.apontamentos
        )

        datas = sorted(
            df[
                "data"
            ].unique().tolist(),
            reverse=True,
        )

        data_selecionada = st.selectbox(
            "Data",
            datas,
        )

        base = df[
            df["data"]
            == data_selecionada
        ]

        total = len(
            base
        )

        pendentes = int(
            (
                base["status"]
                == "Pendente"
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
            - pendentes,
        )

        c3.metric(
            "Pendentes",
            pendentes,
        )

        for frente in base[
            "frente"
        ].unique():

            st.markdown(
                f"### {frente}"
            )

            grupo = base[
                base["frente"]
                == frente
            ]

            for _, row in grupo.iterrows():

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

                    if row["tipo"] == "AVULSO":

                        nome += (
                            " • AVULSO"
                        )

                    st.markdown(
                        nome
                    )

                    st.caption(
                        f"Obra {row['obra']} • "
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
                            STATUS_APONTAMENTO.index(
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
                            st.session_state.apontamentos
                        ):

                            if (
                                item["id"]
                                == apontamento_id
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
        "Nesta fase a sincronização com Trello "
        "está desligada."
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
        "Lista que será usada no Trello: "
        f"**{lista_esperada}**"
    )

    st.button(
        "🔄 Sincronizar com Trello",
        disabled=True,
        help=(
            "Será ativado posteriormente."
        ),
    )

    base = (
        st.session_state.medicoes.copy()
    )

    base = base[
        base[
            "competencia"
        ]
        == competencia
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
            == "FIEC"
        ]

        fora_fiec = base[
            base[
                "origem"
            ]
            != "FIEC"
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
