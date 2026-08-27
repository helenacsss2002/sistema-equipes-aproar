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
        (
            ["SERVENTE", "AJUDANTE", "AUXILIAR", "SERVICOS GERAIS"],
            "APOIO / SERVIÇOS GERAIS",
        ),
    ]

    for termos, frente in regras:
        if any(termo in funcao for termo in termos):
            return frente

    return "OUTROS"


def iniciar_dados():
    if "colaboradores" not in st.session_state:
        st.session_state.colaboradores = pd.DataFrame(
            [
                {"id": 1, "nome": "FRANCISCO", "funcao": "Pintor", "frente": "PINTURA", "ativo": True},
                {"id": 2, "nome": "JOÃO", "funcao": "Pintor", "frente": "PINTURA", "ativo": True},
                {"id": 3, "nome": "JOCA", "funcao": "Pintor", "frente": "PINTURA", "ativo": True},
                {"id": 4, "nome": "JOSÉ", "funcao": "Pintor", "frente": "PINTURA", "ativo": True},
                {"id": 5, "nome": "PEDRO", "funcao": "Pedreiro", "frente": "ALVENARIA / PEDREIROS", "ativo": True},
                {"id": 6, "nome": "CARLOS", "funcao": "Pedreiro", "frente": "ALVENARIA / PEDREIROS", "ativo": True},
                {"id": 7, "nome": "MARCOS", "funcao": "Eletricista", "frente": "ELÉTRICA", "ativo": True},
                {"id": 8, "nome": "LUCAS", "funcao": "Encanador", "frente": "HIDRÁULICA", "ativo": True},
                {"id": 9, "nome": "RAFAEL", "funcao": "Servente", "frente": "APOIO / SERVIÇOS GERAIS", "ativo": True},
            ]
        )

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

    if "convocacoes" not in st.session_state:
        st.session_state.convocacoes = []

    if "apontamentos" not in st.session_state:
        st.session_state.apontamentos = []

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

    if "equipe_rascunho" not in st.session_state:
        st.session_state.equipe_rascunho = []

    if "conv_select_version" not in st.session_state:
        st.session_state.conv_select_version = 0


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
        Build: <code>{BUILD}</code>
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
        value=st.session_state.get("engenheiro_atual", ""),
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

    st.caption(f"Build: {BUILD}")

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
            "equipe_rascunho",
            "ultima_convocacao_msg",
            "conv_select_version",
        ]

        for chave in chaves:
            st.session_state.pop(chave, None)

        iniciar_dados()
        st.rerun()


# ============================================================
# VISÃO GERAL
# ============================================================

if menu == "Visão Geral":
    st.subheader("Visão Geral")

    total_colaboradores = len(st.session_state.colaboradores)

    total_convocados = sum(
        len(convocacao["equipe"])
        for convocacao in st.session_state.convocacoes
    )

    total_pendentes = sum(
        1
        for apontamento in st.session_state.apontamentos
        if apontamento["status"] == "Pendente"
    )

    total_medicoes = len(st.session_state.medicoes)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Colaboradores", total_colaboradores)
    c2.metric("Convocados", total_convocados)
    c3.metric("Apontamentos pendentes", total_pendentes)
    c4.metric("Itens de medição", total_medicoes)

    st.markdown("### Fluxo do sistema")

    st.write(
        "Colaboradores → Convocação por frente → "
        "Apontamento → Medições / Resultados"
    )

    if st.session_state.apontamentos:
        df_pendencias = pd.DataFrame(
            st.session_state.apontamentos
        )

        df_pendencias = df_pendencias[
            df_pendencias["status"] == "Pendente"
        ]

        if not df_pendencias.empty:
            st.markdown("### Pendências")

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
    st.subheader("Colaboradores")

    st.caption(
        "A função cadastrada define em qual grupo "
        "a pessoa aparece inicialmente na convocação."
    )

    with st.expander("➕ Adicionar colaborador"):
        c1, c2 = st.columns(2)

        nome = c1.text_input("Nome")
        funcao = c2.text_input("Função / cargo")

        frente_sugerida = inferir_frente(funcao)

        frente = st.selectbox(
            "Frente principal",
            FRENTES,
            index=FRENTES.index(frente_sugerida),
        )

        if st.button("Adicionar colaborador"):
            if not nome.strip():
                st.error("Informe o nome.")

            else:
                df = st.session_state.colaboradores

                novo_id = (
                    1
                    if df.empty
                    else int(df["id"].max()) + 1
                )

                novo = pd.DataFrame(
                    [
                        {
                            "id": novo_id,
                            "nome": nome.strip().upper(),
                            "funcao": funcao.strip() or "NÃO INFORMADA",
                            "frente": frente,
                            "ativo": True,
                        }
                    ]
                )

                st.session_state.colaboradores = pd.concat(
                    [df, novo],
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
        ["Todas"] + frentes_existentes,
    )

    base = st.session_state.colaboradores.copy()

    if filtro != "Todas":
        base = base[
            base["frente"] == filtro
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
    st.subheader("Nova convocação")
    st.caption(
        "Escolha a frente, selecione a mão de obra e monte a equipe."
    )

    if "ultima_convocacao_msg" in st.session_state:
        st.success(
            st.session_state.pop("ultima_convocacao_msg")
        )

    # --------------------------------------------------------
    # DADOS PRINCIPAIS
    # --------------------------------------------------------

    with st.container(border=True):
        c1, c2 = st.columns(2)

        data_convocacao = c1.date_input(
            "Data",
            value=date.today(),
            key="conv_data",
        )

        engenheiro = c2.text_input(
            "Engenheiro responsável",
            value=st.session_state.get(
                "engenheiro_atual",
                "",
            ),
            key="conv_engenheiro",
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
            list(obra_map.keys()),
            key="conv_obra",
        )

        obra_id = obra_map[obra_label]

        obra_row = obras[
            obras["id"] == obra_id
        ].iloc[0]

    # --------------------------------------------------------
    # BLOCO ÚNICO PARA MONTAR EQUIPE
    # --------------------------------------------------------

    st.markdown("### Montar equipe")

    with st.container(border=True):
        colaboradores = st.session_state.colaboradores.copy()

        frentes_disponiveis = sorted(
            colaboradores[
                colaboradores["ativo"] == True
            ]["frente"]
            .dropna()
            .unique()
            .tolist()
        )

        c1, c2 = st.columns([1, 2])

        frente_escolhida = c1.selectbox(
            "Frente",
            frentes_disponiveis,
            key="conv_frente_escolhida",
        )

        grupo = colaboradores[
            (
                colaboradores["frente"] == frente_escolhida
            )
            &
            (
                colaboradores["ativo"] == True
            )
        ]

        ids_ja_adicionados = {
            item["colaborador_id"]
            for item in st.session_state.equipe_rascunho
            if item.get("colaborador_id") is not None
        }

        grupo = grupo[
            ~grupo["id"].isin(ids_ja_adicionados)
        ]

        labels = {
            f"{r.nome} — {r.funcao}": int(r.id)
            for r in grupo.itertuples()
        }

        select_key = (
            "conv_mao_obra_"
            f"{st.session_state.conv_select_version}"
        )

        mao_obra = c2.multiselect(
            "Mão de obra disponível",
            list(labels.keys()),
            key=select_key,
            placeholder="Selecione uma ou mais pessoas...",
        )

        if st.button(
            "＋ Adicionar à equipe",
            use_container_width=True,
            disabled=not mao_obra,
        ):
            for label in mao_obra:
                colaborador_id = labels[label]

                row = colaboradores[
                    colaboradores["id"] == colaborador_id
                ].iloc[0]

                st.session_state.equipe_rascunho.append(
                    {
                        "colaborador_id": int(colaborador_id),
                        "nome": row["nome"],
                        "funcao_base": row["funcao"],
                        "frente_base": row["frente"],
                        "funcao_dia": row["funcao"],
                        "frente_dia": row["frente"],
                        "observacao": "",
                        "tipo": "FIXO",
                    }
                )

            st.session_state.conv_select_version += 1
            st.rerun()

        # ----------------------------------------------------
        # AVULSOS
        # ----------------------------------------------------

        with st.expander("＋ Mão de obra avulsa"):
            avulsos = st.data_editor(
                pd.DataFrame(
                    [
                        {
                            "Nome": "",
                            "Função": "",
                            "Frente": frente_escolhida,
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
                key="conv_avulsos",
            )

            if st.button(
                "Adicionar avulso(s)",
                use_container_width=True,
            ):
                adicionados = 0

                for _, avulso in avulsos.iterrows():
                    nome_avulso = str(
                        avulso.get("Nome", "")
                    ).strip()

                    if not nome_avulso:
                        continue

                    funcao_avulso = str(
                        avulso.get("Função", "")
                    ).strip()

                    if not funcao_avulso:
                        funcao_avulso = "NÃO INFORMADA"

                    frente_avulso = str(
                        avulso.get("Frente", "")
                    ).strip()

                    if not frente_avulso:
                        frente_avulso = frente_escolhida

                    st.session_state.equipe_rascunho.append(
                        {
                            "colaborador_id": None,
                            "nome": nome_avulso.upper(),
                            "funcao_base": "AVULSO",
                            "frente_base": "AVULSO",
                            "funcao_dia": funcao_avulso,
                            "frente_dia": frente_avulso,
                            "observacao": "",
                            "tipo": "AVULSO",
                        }
                    )

                    adicionados += 1

                if adicionados:
                    st.rerun()

    # --------------------------------------------------------
    # EQUIPE MONTADA
    # --------------------------------------------------------

    if st.session_state.equipe_rascunho:
        st.markdown("### Equipe montada")

        equipe_df = pd.DataFrame(
            [
                {
                    "Nome": item["nome"],
                    "Função base": item["funcao_base"],
                    "Função no dia": item["funcao_dia"],
                    "Frente no dia": item["frente_dia"],
                    "Observação": item.get("observacao", ""),
                    "Remover": False,
                }
                for item in st.session_state.equipe_rascunho
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
                    st.column_config.SelectboxColumn(
                        "Frente no dia",
                        options=FRENTES,
                    ),
                "Observação":
                    st.column_config.TextColumn(
                        "Observação",
                        help=(
                            "Obrigatória quando a função "
                            "ou a frente do colaborador fixo "
                            "for alterada."
                        ),
                    ),
                "Remover":
                    st.column_config.CheckboxColumn(
                        "Remover",
                        default=False,
                    ),
            },
            key="conv_equipe_editor",
        )

        nova_equipe = []

        for i, row in equipe_editada.iterrows():
            if bool(row["Remover"]):
                continue

            original = (
                st.session_state
                .equipe_rascunho[i]
                .copy()
            )

            original["funcao_dia"] = (
                str(row["Função no dia"]).strip()
                or original["funcao_dia"]
            )

            original["frente_dia"] = (
                str(row["Frente no dia"]).strip()
                or original["frente_dia"]
            )

            original["observacao"] = str(
                row["Observação"]
            ).strip()

            nova_equipe.append(original)

        if (
            len(nova_equipe)
            != len(st.session_state.equipe_rascunho)
        ):
            st.session_state.equipe_rascunho = nova_equipe
            st.rerun()

        st.session_state.equipe_rascunho = nova_equipe

        c1, c2 = st.columns(2)

        if c1.button(
            "Limpar equipe",
            use_container_width=True,
        ):
            st.session_state.equipe_rascunho = []
            st.session_state.conv_select_version += 1
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

            if not st.session_state.equipe_rascunho:
                st.error(
                    "Adicione pelo menos uma pessoa."
                )
                st.stop()

            # ------------------------------------------------
            # OBSERVAÇÃO OBRIGATÓRIA EM REALOCAÇÃO
            # ------------------------------------------------

            realocacoes_sem_obs = []

            for pessoa in st.session_state.equipe_rascunho:
                mudou_funcao = (
                    pessoa["tipo"] == "FIXO"
                    and
                    normalizar(
                        pessoa["funcao_dia"]
                    )
                    !=
                    normalizar(
                        pessoa["funcao_base"]
                    )
                )

                mudou_frente = (
                    pessoa["tipo"] == "FIXO"
                    and
                    normalizar(
                        pessoa["frente_dia"]
                    )
                    !=
                    normalizar(
                        pessoa["frente_base"]
                    )
                )

                if (
                    (mudou_funcao or mudou_frente)
                    and
                    not pessoa["observacao"].strip()
                ):
                    realocacoes_sem_obs.append(
                        pessoa["nome"]
                    )

            if realocacoes_sem_obs:
                st.error(
                    "Informe uma observação para "
                    "quem foi realocado: "
                    + ", ".join(realocacoes_sem_obs)
                )
                st.stop()

            # ------------------------------------------------
            # ASSINATURA PARA IMPEDIR DUPLICIDADE
            # ------------------------------------------------

            nomes_chave = sorted(
                [
                    (
                        f"{p['tipo']}|"
                        f"{p['nome']}|"
                        f"{p['funcao_dia']}|"
                        f"{p['frente_dia']}"
                    )
                    for p in st.session_state.equipe_rascunho
                ]
            )

            assinatura = (
                str(data_convocacao),
                str(obra_row["obra"]),
                engenheiro.strip().upper(),
                tuple(nomes_chave),
            )

            duplicada = any(
                convocacao.get("assinatura") == assinatura
                for convocacao in st.session_state.convocacoes
            )

            if duplicada:
                st.warning(
                    "Essa convocação já foi criada. "
                    "A duplicação foi bloqueada."
                )
                st.stop()

            # ------------------------------------------------
            # SALVA CONVOCAÇÃO
            # ------------------------------------------------

            convocacao_id = (
                len(st.session_state.convocacoes) + 1
            )

            equipe_salvar = []

            for pessoa in st.session_state.equipe_rascunho:
                equipe_salvar.append(
                    {
                        "colaborador_id":
                            pessoa["colaborador_id"],
                        "nome":
                            pessoa["nome"],
                        "funcao":
                            pessoa["funcao_dia"],
                        "frente":
                            pessoa["frente_dia"],
                        "tipo":
                            pessoa["tipo"],
                        "observacao":
                            pessoa["observacao"],
                    }
                )

            st.session_state.convocacoes.append(
                {
                    "id": convocacao_id,
                    "data": str(data_convocacao),
                    "engenheiro": engenheiro.strip(),
                    "obra": obra_row["obra"],
                    "servico": obra_row["titulo"],
                    "equipe": equipe_salvar,
                    "assinatura": assinatura,
                }
            )

            # ------------------------------------------------
            # GERA APONTAMENTOS
            # ------------------------------------------------

            for pessoa in equipe_salvar:
                apontamento_id = (
                    len(st.session_state.apontamentos) + 1
                )

                st.session_state.apontamentos.append(
                    {
                        "id": apontamento_id,
                        "convocacao_id": convocacao_id,
                        "data": str(data_convocacao),
                        "obra": obra_row["obra"],
                        "nome": pessoa["nome"],
                        "tipo": pessoa["tipo"],
                        "funcao": pessoa["funcao"],
                        "frente": pessoa["frente"],
                        "status": "Pendente",
                        "extra": 0.0,
                        "observacao": pessoa["observacao"],
                    }
                )

            quantidade = len(equipe_salvar)

            st.session_state.equipe_rascunho = []
            st.session_state.conv_select_version += 1

            st.session_state.ultima_convocacao_msg = (
                "✅ Convocação criada com sucesso para "
                f"{quantidade} pessoa(s). "
                f"Obra {obra_row['obra']}."
            )

            st.rerun()

    else:
        st.info(
            "Selecione uma frente e adicione a mão de obra."
        )


# ============================================================
# APONTAMENTOS
# ============================================================

elif menu == "Apontamentos":
    st.subheader("Apontamentos")

    if not st.session_state.apontamentos:
        st.info(
            "Ainda não existe nenhuma convocação."
        )

    else:
        df = pd.DataFrame(
            st.session_state.apontamentos
        )

        datas = sorted(
            df["data"].unique().tolist(),
            reverse=True,
        )

        data_selecionada = st.selectbox(
            "Data",
            datas,
        )

        base = df[
            df["data"] == data_selecionada
        ]

        total = len(base)

        pendentes = int(
            (
                base["status"] == "Pendente"
            ).sum()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Convocados",
            total,
        )

        c2.metric(
            "Apontados",
            total - pendentes,
        )

        c3.metric(
            "Pendentes",
            pendentes,
        )

        for frente in base["frente"].unique():
            st.markdown(f"### {frente}")

            grupo = base[
                base["frente"] == frente
            ]

            for _, row in grupo.iterrows():
                apontamento_id = int(
                    row["id"]
                )

                with st.container(border=True):
                    nome = f"**{row['nome']}**"

                    if row["tipo"] == "AVULSO":
                        nome += " • AVULSO"

                    st.markdown(nome)

                    st.caption(
                        f"Obra {row['obra']} • "
                        f"{row['funcao']}"
                    )

                    c1, c2, c3 = st.columns(
                        [1.2, 1, 2]
                    )

                    status = c1.selectbox(
                        "Status",
                        STATUS_APONTAMENTO,
                        index=STATUS_APONTAMENTO.index(
                            row["status"]
                        ),
                        key=f"status_{apontamento_id}",
                    )

                    extra = c2.number_input(
                        "Extra (R$)",
                        min_value=0.0,
                        value=float(
                            row["extra"]
                        ),
                        step=10.0,
                        key=f"extra_{apontamento_id}",
                    )

                    observacao = c3.text_input(
                        "Observação",
                        value=row["observacao"],
                        key=f"obs_{apontamento_id}",
                    )

                    if st.button(
                        "Salvar apontamento",
                        key=f"salvar_{apontamento_id}",
                    ):
                        for item in st.session_state.apontamentos:
                            if item["id"] == apontamento_id:
                                item["status"] = status
                                item["extra"] = extra
                                item["observacao"] = observacao
                                break

                        st.rerun()


# ============================================================
# MEDIÇÕES
# ============================================================

elif menu == "Medições":
    st.subheader("Medições e Resultados")

    st.caption(
        "Nesta fase a sincronização com Trello "
        "está desligada."
    )

    c1, c2 = st.columns(2)

    mes = c1.selectbox(
        "Mês de competência",
        list(MESES_PT.keys()),
        index=7,
        format_func=lambda x:
            MESES_PT[x].title(),
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
        help="Será ativado posteriormente.",
    )

    base = st.session_state.medicoes.copy()

    base = base[
        base["competencia"] == competencia
    ]

    if base.empty:
        st.warning(
            "Não existem dados de demonstração "
            "para esta competência."
        )

    else:
        fiec = base[
            base["origem"] == "FIEC"
        ]

        fora_fiec = base[
            base["origem"] != "FIEC"
        ]

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total",
            len(base),
        )

        c2.metric(
            "FIEC",
            len(fiec),
        )

        c3.metric(
            "Fora FIEC",
            len(fora_fiec),
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
