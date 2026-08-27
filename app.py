import streamlit as st
import pandas as pd
import datetime
import requests

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA & ESTILO (Tema Escuro Aproar)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Controle de Apontamentos - Aproar", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b1329; color: #ffffff; }
    div[data-testid="stSidebar"] { background-color: #070d1d; }
    .stCard {
        background-color: #131c38;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #1e2d5a;
        margin-bottom: 12px;
    }
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
    }
    .stButton > button:hover { background-color: #1d4ed8; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DADOS DE EXEMPLO / SESSION STATE
# -----------------------------------------------------------------------------
if 'colaboradores' not in st.session_state:
    st.session_state.colaboradores = [
        {"id": 1, "nome": "VALDIR SIMAO PEREIRA DA SILVA", "funcao": "PEDREIRO", "unidade": "BARRA DO CEARÁ", "status": "Falta", "horas_extras": 0.0, "obs": "", "custo_dia": 120.0},
        {"id": 2, "nome": "FERNANDO VERÇOSA", "funcao": "PEDREIRO", "unidade": "BARRA DO CEARÁ", "status": "Presente (Integral)", "horas_extras": 0.0, "obs": "", "custo_dia": 240.0},
        {"id": 3, "nome": "IVONEUDO FERREIRA DA SILVA", "funcao": "PEDREIRO", "unidade": "BARRA DO CEARÁ", "status": "Presente (Integral)", "horas_extras": 0.0, "obs": "", "custo_dia": 240.0},
        {"id": 4, "nome": "FRANCISCO ANDERSON FELIX DA SILVA", "funcao": "SERVENTE", "unidade": "FIEC", "status": "Falta", "horas_extras": 0.0, "obs": "Sem justificativa", "custo_dia": 100.0},
        {"id": 5, "nome": "CARLOS ANDRE PESSOA DO NASCIMENTO", "funcao": "CARPINTEIRO", "unidade": "CENTRO", "status": "Atestado", "horas_extras": 0.0, "obs": "Médico", "custo_dia": 180.0},
    ]

# -----------------------------------------------------------------------------
# MENU LATERAL
# -----------------------------------------------------------------------------
st.sidebar.title("APROAR ENGENHARIA")
st.sidebar.caption("CONTROLE DE APONTAMENTOS")

menu = st.sidebar.radio(
    "Navegação",
    ["DASHBOARD", "CONVOCAÇÃO", "APONTAMENTO", "RELATÓRIOS", "INDICADORES", "DISPONIBILIDADE", "CONFIGURAÇÕES"]
)
st.sidebar.caption("APROAR Engenharia © 2026")

# -----------------------------------------------------------------------------
# 1. APONTAMENTO (Com botão de salvar individual)
# -----------------------------------------------------------------------------
if menu == "APONTAMENTO":
    st.title("📋 Apontamento Diário de Colaboradores")
    
    # Filtros Superiores
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        data_apontamento = st.date_input("Data:", datetime.date.today())
    with c2:
        unidade_filtro = st.selectbox("Unidade:", ["TODAS", "BARRA DO CEARÁ", "FIEC", "CENTRO"])
    with c3:
        eng_filtro = st.selectbox("Engenheiro:", ["TODOS", "VICTOR", "EDUARDO"])
    with c4:
        busca_colab = st.text_input("Buscar colaborador:", placeholder="Ex: Valdir...")
    with c5:
        status_filtro = st.selectbox("Status:", ["Todos", "Presente (Integral)", "Falta", "Atestado"])

    st.markdown("---")
    
    # Resumo Rápido
    r1, r2, r3, r4, r5, r6 = st.columns(6)
    r1.metric("TOTAL", len(st.session_state.colaboradores))
    r2.metric("PRES.", sum(1 for c in st.session_state.colaboradores if "Presente" in c['status']))
    r3.metric("ATEST.", sum(1 for c in st.session_state.colaboradores if c['status'] == "Atestado"))
    r4.metric("FALTAS", sum(1 for c in st.session_state.colaboradores if c['status'] == "Falta"))
    r5.metric("EXTRAS", "0")
    r6.metric("CUSTO", "R$ 960,00")

    if st.button("✔ MARCAR TODOS COMO PRESENTES (INTEGRAL)"):
        for colab in st.session_state.colaboradores:
            colab['status'] = "Presente (Integral)"
        st.rerun()

    st.subheader("👷 Engenheiro Responsável: VICTOR")
    st.caption("Unidade: BARRA DO CEARÁ")

    # Lista de Colaboradores com botão de salvar individual
    for colab in st.session_state.colaboradores:
        if unidade_filtro != "TODAS" and colab['unidade'] != unidade_filtro:
            continue
        if busca_colab and busca_colab.lower() not in colab['nome'].lower():
            continue

        with st.container():
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            col_info, col_status, col_extras, col_acao = st.columns([4, 3, 2, 2])
            
            with col_info:
                st.markdown(f"**{colab['nome']}** `<span style='color:#10b981'>{colab['funcao']}</span>` ({data_apontamento})", unsafe_allow_html=True)
                colab['obs'] = st.text_input("Obs...", value=colab['obs'], key=f"obs_{colab['id']}")
            
            with col_status:
                opcoes_status = ["Presente (Integral)", "Falta", "Atestado", "Meio Período"]
                idx = opcoes_status.index(colab['status']) if colab['status'] in opcoes_status else 0
                colab['status'] = st.selectbox("Status Presença", opcoes_status, index=idx, key=f"status_{colab['id']}")
            
            with col_extras:
                colab['horas_extras'] = st.number_input("Horas Extras", value=float(colab['horas_extras']), step=0.5, key=f"he_{colab['id']}")
                st.caption(f"R$ {colab['custo_dia']:.2f}")

            with col_acao:
                st.write("")
                st.write("")
                if st.button("💾 Salvar", key=f"btn_salvar_{colab['id']}"):
                    st.toast(f"Apontamento de {colab['nome']} salvo com sucesso!", icon="✅")
            
            st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CONVOCAÇÃO (Sem Obra/Serviço e com Seleção de Turno)
# -----------------------------------------------------------------------------
elif menu == "CONVOCAÇÃO":
    st.title("📋 CONVOCAÇÃO E GERENCIAMENTO DE EQUIPE")
    
    st.subheader("➕ Nova Convocação")
    
    col1, col2 = st.columns(2)
    with col1:
        eng_resp = st.selectbox("Engenheiro responsável:", ["EDUARDO", "VICTOR", "MARCOS"])
        unidade_conv = st.selectbox("Unidade:", ["BARRA DO CEARÁ", "CENTRO", "FIEC", "MUSEU"])
        funcao_filtro = st.selectbox("Filtrar por Função (Opcional):", ["TODAS", "PEDREIRO", "SERVENTE", "CARPINTEIRO"])

    with col2:
        st.info(f"📅 Data da Convocação: {(datetime.date.today() + datetime.timedelta(days=1)).strftime('%d/%m/%Y')} (Dia seguinte automático)")
        turno_selecionado = st.selectbox("Turno da Convocação:", ["Integral", "Manhã", "Tarde", "Noite"])

    colab_selecionados = st.multiselect(
        "Buscar ou Selecionar Colaboradores:",
        [c['nome'] for c in st.session_state.colaboradores]
    )

    st.markdown("""
    <div style="background-color: #101935; padding: 15px; border-radius: 6px; border: 1px solid #1e2d5a; margin-top: 15px;">
        <h4>Panorama de EDUARDO</h4>
        <p style="color: #a0aec0;">Já escalados por você nesta data: FRANCISCO ANDERSON FELIX DA SILVA, CARLOS ANDRE PESSOA DO NASCIMENTO, JOAO BATISTA MARTINS</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("CONFIRMAR CONVOCAÇÃO", use_container_width=True):
        st.success(f"Convocação confirmada para a Unidade {unidade_conv} no turno {turno_selecionado}!")

# -----------------------------------------------------------------------------
# 3. INDICADORES (Ranking Nominal + Análises Estratégicas)
# -----------------------------------------------------------------------------
elif menu == "INDICADORES":
    st.title("📈 INDICADORES OPERACIONAIS E ABSENTEÍSMO")

    f1, f2, f3 = st.columns(3)
    with f1:
        dt_inicio = st.date_input("Início:", datetime.date(2026, 7, 28))
    with f2:
        dt_fim = st.date_input("Fim:", datetime.date(2026, 8, 27))
    with f3:
        unidade_ind = st.selectbox("Filtrar por Unidade:", ["TODAS AS UNIDADES", "BARRA DO CEARÁ", "FIEC", "CENTRO"])

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("CONVOCAÇÕES TOTAL", "10")
    k2.metric("FALTAS", "2")
    k3.metric("ATESTADOS", "1")
    k4.metric("TAXA DE ABSENTEÍSMO", "30.0%")

    st.markdown("---")

    # Tabela 1: Consolidado por Unidade
    st.subheader("🏢 DETALHAMENTO E CONSOLIDAÇÃO DE FALTAS POR UNIDADE")
    df_unidades = pd.DataFrame([
        {"Unidade": "FIEC", "Convoções": 2, "Faltas": 1, "Atestados": 0, "Total Ausências": 1, "Taxa Absenteísmo (%)": 50.0},
        {"Unidade": "BARRA DO CEARÁ", "Convoções": 7, "Faltas": 1, "Atestados": 1, "Total Ausências": 2, "Taxa Absenteísmo (%)": 28.6},
        {"Unidade": "CENTRO", "Convoções": 1, "Faltas": 0, "Atestados": 0, "Total Ausências": 0, "Taxa Absenteísmo (%)": 0.0},
    ])
    st.dataframe(df_unidades, use_container_width=True)

    # Ranking Nominal de Faltosos
    st.subheader("👤 RANKING NOMINAL DE COLABORADORES MAIS FALTOSOS")
    df_ranking = pd.DataFrame([
        {"Colaborador": "FRANCISCO ANDERSON FELIX DA SILVA", "Função": "SERVENTE", "Unidade": "FIEC", "Faltas Injustificadas": 4, "Atestados": 1, "% Absenteísmo": "41.6%"},
        {"Colaborador": "VALDIR SIMAO PEREIRA DA SILVA", "Função": "PEDREIRO", "Unidade": "BARRA DO CEARÁ", "Faltas Injustificadas": 3, "Atestados": 0, "% Absenteísmo": "25.0%"},
        {"Colaborador": "CARLOS ANDRE PESSOA DO NASCIMENTO", "Função": "CARPINTEIRO", "Unidade": "CENTRO", "Faltas Injustificadas": 1, "Atestados": 2, "% Absenteísmo": "18.2%"},
    ])
    st.dataframe(df_ranking, use_container_width=True)

    # Análises Gráficas e Custos
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.subheader("📅 Ausências por Dia da Semana")
        df_dias = pd.DataFrame({
            "Dia": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"],
            "Faltas": [5, 1, 2, 1, 6, 0]
        })
        st.bar_chart(df_dias.set_index("Dia"))

    with col_a2:
        st.subheader("💰 Custo Estimado do Absenteísmo")
        st.metric("Custo em Diárias Perdidas", "R$ 1.480,00")
        st.metric("Horas Extras p/ Cobertura", "R$ 620,00")
        st.caption("Impacto financeiro acumulado no período selecionado.")

# -----------------------------------------------------------------------------
# 4. CONFIGURAÇÕES (Com Entrada Manual para Busca de Card/Lista no Trello)
# -----------------------------------------------------------------------------
elif menu == "CONFIGURAÇÕES":
    st.title("⚙️ CONFIGURAÇÕES E GERENCIAMENTO")

    st.subheader("🔄 Sincronização com o Trello")
    st.write("Sincronize automaticamente as obras da lista do mês vigente ou selecione manualmente uma lista específica do quadro.")

    col_sync1, col_sync2 = st.columns([1, 2])
    
    with col_sync1:
        if st.button("🚀 SINCRONIZAR MÊS VIGENTE (AUTOMÁTICO)", use_container_width=True):
            st.info("Buscando dados do mês vigente...")

    with col_sync2:
        trello_search_input = st.text_input(
            "Buscar lista/card específico no Trello (para medições de outros meses):",
            placeholder="Digite o nome da lista ou código do card (Ex: Medição Julho/2026)"
        )
        if st.button("🔍 Buscar no Trello"):
            if trello_search_input.strip():
                st.success(f"Buscando no Trello por: '{trello_search_input}'...")
            else:
                st.warning("Por favor, informe o nome da lista ou card para pesquisar.")

    st.markdown("---")
    
    tab_obras, tab_colab, tab_limpeza = st.tabs(["🏗️ Obras", "👷 Colaboradores", "🗑️ Limpeza de Dados"])
    
    with tab_obras:
        st.subheader("Cadastrar Nova Obra")
        st.text_input("Nome da Obra (Ex: 1863, 1383...):")
        st.text_input("Unidade (Ex: CENTRO, MUSEU, FIEC...):")
        if st.button("Cadastrar Obra"):
            st.success("Obra cadastrada com sucesso!")

# -----------------------------------------------------------------------------
# DEMAIS SEÇÕES (PLACEHOLDERS)
# -----------------------------------------------------------------------------
else:
    st.title(f"📍 {menu}")
    st.info(f"Módulo {menu} operacional.")
