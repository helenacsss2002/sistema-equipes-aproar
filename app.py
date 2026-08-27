import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import json
from fpdf import FPDF
import unicodedata
import re

# --- CONFIGURAÇÕES DA PÁGINA & TEMA APROAR ---
st.set_page_config(page_title="APROAR - Gestão de Obras", page_icon="👷", layout="centered")

# CSS para o tema escuro APROAR e visibilidade perfeita dos inputs
st.markdown("""
    <style>
    .stApp {
        background-color: #0C102B;
        color: #F8FAFC;
    }
    h1, h2, h3, h4, p, label, .stMarkdown, span {
        color: #F8FAFC !important;
    }
    div[data-baseweb="select"] > div, 
    div[data-baseweb="base-input"] > div, 
    div[data-baseweb="input"] > div,
    input, textarea, div[role="combobox"] {
        background-color: #161B3D !important;
        color: #FFFFFF !important;
        border-color: #2D3568 !important;
    }
    ul[data-baseweb="menu"], div[data-baseweb="popover"] {
        background-color: #161B3D !important;
        color: #FFFFFF !important;
    }
    li[role="option"] {
        background-color: #161B3D !important;
        color: #FFFFFF !important;
    }
    li[role="option"]:hover {
        background-color: #2563EB !important;
    }
    div[data-baseweb="tag"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    .stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1D4ED8 !important;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #0C102B !important;
        font-weight: bold;
    }
    .streamlit-expanderHeader {
        background-color: #161B3D !important;
        border-radius: 6px;
    }
    hr {
        border-color: #2D3568 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"Erro de credenciais: {e}")
    st.stop()

# --- FUNÇÕES DE LIMPEZA E PADRONIZAÇÃO ---
def identificar_unidade(nome_card):
    if not nome_card: return "GERAL"
    texto = unicodedata.normalize('NFKD', str(nome_card)).encode('ASCII', 'ignore').decode('utf-8').upper()
    
    if "APRL005" in texto or "MARACANAU" in texto: return "MARACANAÚ"
    if "SEBRAE" in texto: return "SEBRAE"
    if "UNIFOR" in texto: return "UNIFOR"
    if "IDALYA" in texto or "MATHEUS" in texto: return "IDALYA E MATHEUS"
    if "COLISEU" in texto: return "COLISEU"
    if "BARRA" in texto: return "BARRA DO CEARÁ"
    if "MUSEU" in texto: return "MUSEU"
    if "HORIZONTE" in texto: return "HORIZONTE"
    if "ESCRITORIO" in texto: return "ESCRITÓRIO"
    if "CASA DA INDUSTRIA" in texto or "FIEC" in texto or " DR " in texto or "| SESI DR |" in texto or "| SESI DR" in texto: return "FIEC"
    if "CENTRO" in texto: return "CENTRO"
    
    partes = str(nome_card).split('|')
    if len(partes) >= 2:
        return partes[1].strip().upper()
    return "GERAL"

def limpar_funcao(texto):
    if not texto or str(texto).upper() == 'NAN': return "INDEFINIDA"
    texto_limpo = str(texto).upper().strip()
    texto_limpo = re.sub(r'^\d+\s*-\s*', '', texto_limpo)
    texto_limpo = unicodedata.normalize('NFKD', texto_limpo).encode('ASCII', 'ignore').decode('utf-8')
    return texto_limpo

def get_cor_funcao(funcao):
    cores = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛"]
    hash_num = sum(ord(c) for c in str(funcao))
    return cores[hash_num % len(cores)]

def to_latin(texto):
    if not texto: return ""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# --- BUSCA DE DADOS ---
def buscar_obras():
    try: return supabase.table("obras").select("*").execute().data
    except Exception: return []

def buscar_colaboradores():
    try: return supabase.table("colaboradores").select("*").eq("ativo", True).execute().data
    except Exception: return []

obras = buscar_obras()
colaboradores = buscar_colaboradores()

dict_colaboradores = {c['id']: c for c in colaboradores} if colaboradores else {}
dict_obras = {o['id']: o for o in obras} if obras else {}

ENGENHEIROS = ["EDUARDO", "GABRIEL", "GUSTAVO", "JOEL", "NETO", "PAULO", "SOARES", "VICTOR"]

# --- VERIFICAÇÃO DE MODO (CAMPO vs ADM) ---
parametros_url = st.query_params
modo_campo = parametros_url.get("modo") == "campo"

if modo_campo:
    # VISÃO ESSENCIAL DO ENGENHEIRO NO CELULAR
    st.title("👷 APROAR - Campo")
    tab_apontamento_campo, tab_convocacao_campo = st.tabs(["✅ Apontamento de Hoje", "📋 Convocação para Amanhã"])
    
    # --- ABA APONTAMENTO CAMPO ---
    with tab_apontamento_campo:
        engenheiro_apont = st.selectbox("Seu Nome (Engenheiro):", ENGENHEIROS, key="eng_apont_c")
        data_apont = datetime.date.today()
        st.write(f"📅 Data: {data_apont.strftime('%d/%m/%Y')}")
        
        try:
            convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", data_apont.isoformat()).execute().data
        except:
            convocacoes_hoje = []

        if convocacoes_hoje:
            for conv in convocacoes_hoje:
                conv['dados_obra'] = dict_obras.get(conv['obra_id'], {"unidade": "Desconhecida", "nome": "Desconhecida"})
                
            unidades_convocadas = sorted(list(set([c['dados_obra']['unidade'] for c in convocacoes_hoje])))
            unidade_filtro = st.selectbox("Unidade:", unidades_convocadas, key="f_u_c")
            
            obras_convocadas = sorted(list(set([c['dados_obra']['nome'] for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro])))
            obra_filtro = st.selectbox("Obra:", obras_convocadas, key="f_o_c")
            
            convocacoes_render = [c for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro and c['dados_obra']['nome'] == obra_filtro]
            
            st.info("💡 Suas marcações salvam instantaneamente. Pode parar e continuar quando quiser.")
            opcoes_status = ["Presente", "Falta", "Atestado", "Extra"]
            
            for conv in convocacoes_render:
                c_id = conv['id']
                dados_colab = dict_colaboradores.get(conv['colaborador_id'], {"nome": "Desconhecido", "funcao": "-"})
                nome = dados_colab['nome']
                funcao = dados_colab['funcao']
                status_atual = conv.get("status", "Presente")
                idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                
                st.markdown(f"**{nome}** (`{funcao}`)")
                status_sel = st.radio("Status", opcoes_status, index=idx, key=f"st_{c_id}", horizontal=True, label_visibility="collapsed")
                if status_sel != status_atual:
                    supabase.table("convocacoes").update({"status": status_sel}).eq("id", c_id).execute()
                
                with st.expander("💸 Extra / Observação"):
                    val_atual = float(conv.get("valor_extra") or 0.0)
                    obs_atual = conv.get("observacao") or ""
                    val_extra = st.number_input("Extra (R$)", value=val_atual, step=10.0, key=f"v_{c_id}")
                    obs = st.text_input("Justificativa", value=obs_atual, key=f"o_{c_id}")
                    if st.button("Salvar Detalhes", key=f"btn_{c_id}"):
                        supabase.table("convocacoes").update({"valor_extra": val_extra, "observacao": obs}).eq("id", c_id).execute()
                        st.success("Salvo!")
                st.divider()
        else:
            st.warning("Nenhuma equipe convocada por você para hoje.")

    # --- ABA CONVOCAÇÃO CAMPO ---
    with tab_convocacao_campo:
        if obras and colaboradores:
            engenheiro_conv = st.selectbox("Seu Nome:", ENGENHEIROS, key="eng_c_conv")
            amanha = datetime.date.today() + datetime.timedelta(days=1)
            st.write(f"📅 Convocando para: {amanha.strftime('%d/%m/%Y')}")
            
            unidades_unicas = sorted(list(set([o['unidade'] for o in obras])))
            unidade_selecionada = st.selectbox("Unidade:", unidades_unicas, key="u_c_sel")
            
            obras_da_unidade = {o['nome']: o['id'] for o in obras if o['unidade'] == unidade_selecionada}
            obra_selecionada = st.selectbox("Obra:", list(obras_da_unidade.keys()), key="o_c_sel")

            funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
            frente_selecionada = st.selectbox("Função:", funcoes_disponiveis, key="f_c_sel")

            colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
            opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}
            equipe_selecionada = st.multiselect("Colaboradores:", list(opcoes_colaboradores.keys()), key="eq_c_sel")

            if st.button("Convocação Rápida", type="primary", use_container_width=True):
                if not equipe_selecionada:
                    st.warning("Selecione alguém.")
                else:
                    obra_id = obras_da_unidade[obra_selecionada]
                    dados_insercao = [{
                        "obra_id": obra_id, "colaborador_id": opcoes_colaboradores[nome],
                        "data": amanha.isoformat(), "engenheiro": engenheiro_conv,
                        "status": "Presente", "valor_extra": 0, "observacao": ""
                    } for nome in equipe_selecionada]
                    try:
                        supabase.table("convocacoes").insert(dados_insercao).execute()
                        st.success("✅ Convocado com sucesso!")
                    except:
                        st.error("Erro: Colaborador já possui convocação neste dia.")
        else:
            st.info("Aguardando cadastro de obras/colaboradores pela administração.")

else:
    # VISÃO COMPLETA DO ADMINISTRATIVO (PAINEL GERAL)
    st.title("👷 APROAR - Painel Administrativo")
    tab_convocacao, tab_apontamento, tab_relatorios, tab_indicadores, tab_config = st.tabs([
        "📋 Convocação", "✅ Apontamento", "📊 Relatório", "📈 Indicadores", "⚙️ Config"
    ])

    # ==========================================
    # ABA 1: CONVOCAÇÃO (ADM)
    # ==========================================
    with tab_convocacao:
        if obras and colaboradores:
            st.markdown("### Informações da Demanda")
            col_eng, col_data = st.columns(2)
            with col_eng:
                engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv")
            with col_data:
                amanha = datetime.date.today() + datetime.timedelta(days=1)
                data_conv = st.date_input("Data da Obra/Serviço:", value=amanha, format="DD/MM/YYYY")

            unidades_unicas = sorted(list(set([o['unidade'] for o in obras])))
            col_u, col_o = st.columns(2)
            with col_u:
                unidade_selecionada = st.selectbox("Unidade:", unidades_unicas)
            obras_da_unidade = {o['nome']: o['id'] for o in obras if o['unidade'] == unidade_selecionada}
            with col_o:
                obra_selecionada = st.selectbox("Obra/Serviço:", list(obras_da_unidade.keys()))

            st.markdown("### Montar Equipe")
            funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
            frente_selecionada = st.selectbox("Frente de Trabalho:", funcoes_disponiveis)
            colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
            opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}
            equipe_selecionada = st.multiselect("Selecione os colaboradores para esta frente:", list(opcoes_colaboradores.keys()))

            if st.button("Confirmar Convocação", type="primary", use_container_width=True):
                if not equipe_selecionada:
                    st.warning("⚠️ Selecione pelo menos um colaborador.")
                else:
                    obra_id = obras_da_unidade[obra_selecionada]
                    dados_insercao = [{
                        "obra_id": obra_id, "colaborador_id": opcoes_colaboradores[nome],
                        "data": data_conv.isoformat(), "engenheiro": engenheiro_conv,
                        "status": "Presente", "valor_extra": 0, "observacao": ""
                    } for nome in equipe_selecionada]
                    try:
                        supabase.table("convocacoes").insert(dados_insercao).execute()
                        st.success(f"✅ Equipe convocada com sucesso para {data_conv.strftime('%d/%m/%Y')}!")
                    except:
                        st.error("❌ Erro: Colaborador já convocado para outra obra neste dia.")
        else:
            st.info("Cadastre obras (JSON) e colaboradores (Excel) na aba Configurações.")

    # ==========================================
    # ABA 2: APONTAMENTOS (ADM)
    # ==========================================
    with tab_apontamento:
        st.markdown("### Apontamento Diário (Administrativo)")
        col_eng_ap, col_data_ap = st.columns(2)
        with col_eng_ap:
            engenheiro_apont = st.selectbox("Engenheiro:", ENGENHEIROS, key="eng_apont")
        with col_data_ap:
            data_apont = st.date_input("Data do Apontamento:", value=datetime.date.today(), format="DD/MM/YYYY")
        
        try:
            convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", data_apont.isoformat()).execute().data
        except:
            convocacoes_hoje = []

        if convocacoes_hoje:
            for conv in convocacoes_hoje:
                conv['dados_obra'] = dict_obras.get(conv['obra_id'], {"unidade": "Desconhecida", "nome": "Desconhecida"})
                
            unidades_convocadas = sorted(list(set([c['dados_obra']['unidade'] for c in convocacoes_hoje])))
            col_ua, col_oa = st.columns(2)
            with col_ua:
                unidade_filtro = st.selectbox("Unidade Convocada:", unidades_convocadas, key="filtro_u_apont")
            obras_convocadas = sorted(list(set([c['dados_obra']['nome'] for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro])))
            with col_oa:
                obra_filtro = st.selectbox("Obra Convocada:", obras_convocadas, key="filtro_o_apont")
            
            convocacoes_render = [c for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro and c['dados_obra']['nome'] == obra_filtro]
            opcoes_status = ["Presente", "Falta", "Atestado", "Extra"]
            
            with st.form("form_apontamentos_extras"):
                dados_para_atualizar = {}
                for conv in convocacoes_render:
                    c_id = conv['id']
                    dados_colab = dict_colaboradores.get(conv['colaborador_id'], {"nome": "Desconhecido", "funcao": "-"})
                    nome = dados_colab['nome']
                    funcao = dados_colab['funcao']
                    cor = get_cor_funcao(funcao)
                    status_atual = conv.get("status", "Presente")
                    idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                    
                    st.markdown(f"**{nome}** &nbsp; {cor} `{funcao}`")
                    status_sel = st.radio("Status", opcoes_status, index=idx, key=f"status_{c_id}", horizontal=True, label_visibility="collapsed")
                    if status_sel != status_atual:
                        supabase.table("convocacoes").update({"status": status_sel}).eq("id", c_id).execute()
                    
                    with st.expander("💸 Inserir Extra ou Observação"):
                        val_atual = float(conv.get("valor_extra") or 0.0)
                        obs_atual = conv.get("observacao") or ""
                        val_extra = st.number_input("Bonificação / Extra (R$)", value=val_atual, step=10.0, key=f"val_{c_id}")
                        obs = st.text_input("Justificativa / Acordo", value=obs_atual, key=f"obs_{c_id}")
                    
                    dados_para_atualizar[c_id] = {"valor_extra": val_extra, "observacao": obs}
                    st.divider()
                
                if st.form_submit_button("💾 Salvar Extras e Observações", type="primary", use_container_width=True):
                    try:
                        for c_id, d in dados_para_atualizar.items():
                            supabase.table("convocacoes").update(d).eq("id", c_id).execute()
                        st.success("✅ Salvo com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: {e}")
        else:
            st.warning(f"Nenhuma equipe convocada para {data_apont.strftime('%d/%m/%Y')}.")

    # ==========================================
    # ABA 3: RELATÓRIOS (ADM)
    # ==========================================
    with tab_relatorios:
        st.markdown("### 📊 Relatório de Custos por Período")
        col_rel_eng, _ = st.columns(2)
        with col_rel_eng:
            opcoes_relatorio = ["TODOS OS ENGENHEIROS"] + ENGENHEIROS
            eng_relatorio = st.selectbox("Engenheiro:", opcoes_relatorio, key="eng_rel")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_inicio_rel = st.date_input("Data Inicial:", value=datetime.date.today(), format="DD/MM/YYYY", key="data_ini")
        with col_d2:
            data_fim_rel = st.date_input("Data Final:", value=datetime.date.today(), format="DD/MM/YYYY", key="data_fim")
        
        if st.button("Gerar PDF de Relatório Consolidado", type="primary"):
            try:
                if data_inicio_rel > data_fim_rel:
                    st.error("❌ A data inicial não pode ser maior que a data final.")
                else:
                    query = supabase.table("convocacoes").select("*").gte("data", data_inicio_rel.isoformat()).lte("data", data_fim_rel.isoformat())
                    if eng_relatorio != "TODOS OS ENGENHEIROS":
                        query = query.eq("engenheiro", eng_relatorio)
                    dados_relatorio = query.execute().data
                    
                    if not dados_relatorio:
                        st.warning("Sem dados no período.")
                    else:
                        agrupado_eng = {}
                        for row in dados_relatorio:
                            eng = row.get('engenheiro', 'NÃO IDENTIFICADO')
                            ob = row['obra_id']
                            if eng not in agrupado_eng: agrupado_eng[eng] = {}
                            if ob not in agrupado_eng[eng]: agrupado_eng[eng][ob] = []
                            agrupado_eng[eng][ob].append(row)

                        pdf = FPDF(orientation='L')
                        for eng, obras_eng in agrupado_eng.items():
                            pdf.add_page()
                            pdf.set_font("Arial", 'B', 15)
                            pdf.cell(0, 10, txt=to_latin("APROAR ENGENHARIA - RELATÓRIO DE CUSTOS"), ln=True, align='C')
                            pdf.set_font("Arial", size=10)
                            pdf.cell(0, 8, txt=to_latin(f"Período: {data_inicio_rel.strftime('%d/%m/%Y')} a {data_fim_rel.strftime('%d/%m/%Y')} | Engenheiro: {eng}"), ln=True, align='C')
                            pdf.ln(5)
                            
                            custo_total_engenheiro = 0.0
                            for o_id, apontamentos in obras_eng.items():
                                dados_ob = dict_obras.get(o_id, {"nome": "N/A", "unidade": "N/A"})
                                pdf.set_font("Arial", 'B', 11)
                                pdf.set_fill_color(220, 220, 220)
                                pdf.cell(0, 8, txt=to_latin(f"Unidade: {dados_ob['unidade']} | Obra: {dados_ob['nome']}"), ln=True, fill=True)
                                
                                pdf.set_font("Arial", 'B', 9)
                                pdf.cell(25, 7, to_latin("Data"), border=1, align='C')
                                pdf.cell(65, 7, to_latin("Colaborador"), border=1)
                                pdf.cell(50, 7, to_latin("Função"), border=1)
                                pdf.cell(22, 7, to_latin("Status"), border=1, align='C')
                                pdf.cell(28, 7, to_latin("Diária (R$)"), border=1, align='C')
                                pdf.cell(28, 7, to_latin("Extra (R$)"), border=1, align='C')
                                pdf.cell(61, 7, to_latin("Observação"), border=1, ln=True)
                                
                                pdf.set_font("Arial", '', 9)
                                custo_total_obra = 0.0
                                for row in apontamentos:
                                    colab = dict_colaboradores.get(row['colaborador_id'], {})
                                    nome = colab.get('nome', 'N/A')
                                    funcao = colab.get('funcao', 'N/A')
                                    status = row.get('status', 'Presente')
                                    extra = float(row.get('valor_extra', 0) or 0)
                                    obs = row.get('observacao', '')
                                    diaria_base = float(colab.get('valor_diaria') or 240.0) if status in ["Presente", "Extra"] else 0.0
                                    custo_total_obra += (diaria_base + extra)
                                    
                                    pdf.cell(25, 7, to_latin(row.get('data', '')), border=1, align='C')
                                    pdf.cell(65, 7, to_latin(nome[:28]), border=1)
                                    pdf.cell(50, 7, to_latin(funcao[:20]), border=1)
                                    pdf.cell(22, 7, to_latin(status), border=1, align='C')
                                    pdf.cell(28, 7, to_latin(f"R$ {diaria_base:.2f}"), border=1, align='C')
                                    pdf.cell(28, 7, to_latin(f"R$ {extra:.2f}"), border=1, align='C')
                                    pdf.cell(61, 7, to_latin(obs[:30]), border=1, ln=True)
                                
                                pdf.set_font("Arial", 'B', 9)
                                pdf.set_fill_color(245, 245, 245)
                                pdf.cell(218, 7, to_latin("CUSTO TOTAL DA OBRA:"), border=1, align='R', fill=True)
                                pdf.cell(61, 7, to_latin(f"R$ {custo_total_obra:.2f}"), border=1, align='C', fill=True, ln=True)
                                pdf.ln(5)
                                custo_total_engenheiro += custo_total_obra
                            pdf.set_font("Arial", 'B', 10)
                            pdf.cell(0, 8, to_latin(f"CUSTO TOTAL GERAL ({eng}): R$ {custo_total_engenheiro:.2f}"), ln=True, align='R')
                        
                        pdf_bytes = pdf.output(dest='S').encode('latin1')
                        st.download_button("📥 Baixar Relatório PDF Consolidado", data=pdf_bytes, file_name="Relatorio_Custos_Aproar.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ==========================================
    # ABA 4: INDICADORES (ADM)
    # ==========================================
    with tab_indicadores:
        st.markdown("### 📈 Painel Administrativo de Indicadores")
        try:
            all_conv = supabase.table("convocacoes").select("*").execute().data
            if all_conv:
                df_conv = pd.DataFrame(all_conv)
                df_conv['nome_colab'] = df_conv['colaborador_id'].map(lambda cid: dict_colaboradores.get(cid, {}).get('nome', 'Desconhecido'))
                df_conv['funcao_colab'] = df_conv['colaborador_id'].map(lambda cid: dict_colaboradores.get(cid, {}).get('funcao', 'Desconhecido'))

                taxa_assiduidade = (len(df_conv[df_conv['status'].isin(['Presente', 'Extra'])]) / len(df_conv) * 100) if len(df_conv) > 0 else 0.0
                st.metric("✅ Taxa de Assiduidade Geral", value=f"{taxa_assiduidade:.1f}%")
                st.divider()

                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1:
                    st.markdown("#### ❌ Top 10 Faltas")
                    df_f = df_conv[df_conv['status'] == 'Falta']
                    if not df_f.empty:
                        st.dataframe(df_f.groupby(['nome_colab', 'funcao_colab']).size().reset_index(name='Total').sort_values(by='Total', ascending=False).head(10).rename(columns={'nome_colab':'Colaborador', 'funcao_colab':'Função'}), hide_index=True, use_container_width=True)
                with col_i2:
                    st.markdown("#### 🩺 Top 10 Atestados")
                    df_a = df_conv[df_conv['status'] == 'Atestado']
                    if not df_a.empty:
                        st.dataframe(df_a.groupby(['nome_colab', 'funcao_colab']).size().reset_index(name='Total').sort_values(by='Total', ascending=False).head(10).rename(columns={'nome_colab':'Colaborador', 'funcao_colab':'Função'}), hide_index=True, use_container_width=True)
                with col_i3:
                    st.markdown("#### ✅ Top 10 Mais Presentes")
                    df_p = df_conv[df_conv['status'].isin(['Presente', 'Extra'])]
                    if not df_p.empty:
                        st.dataframe(df_p.groupby(['nome_colab', 'funcao_colab']).size().reset_index(name='Total').sort_values(by='Total', ascending=False).head(10).rename(columns={'nome_colab':'Colaborador', 'funcao_colab':'Função'}), hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")

    # ==========================================
    # ABA 5: CONFIGURAÇÕES (ADM)
    # ==========================================
    with tab_config:
        st.markdown("### 📋 Sincronizar Obras (Trello JSON)")
        arquivo_json = st.file_uploader("JSON do Trello", type=["json"])
        if arquivo_json and st.button("🔄 Importar Obras"):
            trello_data = json.load(arquivo_json)
            list_id = next((lst['id'] for lst in trello_data.get('lists', []) if lst.get('name', '').upper() == 'EM EXECUÇÃO'), None)
            if list_id:
                cards = [c for c in trello_data.get('cards', []) if c.get('idList') == list_id]
                novas_obras = [{"unidade": identificar_unidade(c.get('name', '')), "nome": c.get('name', '').split('|')[0].strip()} for c in cards]
                existentes = {f"{o['unidade']} - {o['nome']}" for o in supabase.table("obras").select("unidade, nome").execute().data}
                inserir = [o for o in novas_obras if f"{o['unidade']} - {o['nome']}" not in existentes]
                if inserir:
                    supabase.table("obras").insert(inserir).execute()
                    st.success(f"🎉 {len(inserir)} obras importadas!")
                    st.rerun()

        st.divider()
        st.markdown("### 📥 Sincronizar Colaboradores (Excel)")
        arquivo_excel = st.file_uploader("Planilha Excel", type=["xlsx"])
        if arquivo_excel and st.button("🔄 Importar Colaboradores"):
            xls = pd.ExcelFile(arquivo_excel)
            df = pd.read_excel(xls, sheet_name="Base de dados" if "Base de dados" in xls.sheet_names else xls.sheet_names[0])
            existentes = {c['nome'] for c in colaboradores}
            novos = [{"nome": str(r.get('NOME', '')).strip(), "funcao": limpar_funcao(str(r.get('FUNÇÃO', ''))), "valor_diaria": float(r.get('VALOR DIÁRIA (R$)', 240) or 240), "ativo": True} for _, r in df.iterrows() if str(r.get('NOME', '')).strip() and str(r.get('NOME', '')).strip() not in existentes]
            if novos:
                supabase.table("colaboradores").insert(novos).execute()
                st.success(f"🎉 {len(novos)} colaboradores importados!")
                st.rerun()
