import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import json
from fpdf import FPDF
import unicodedata
import re
import os

# --- CONFIGURAÇÕES DA PÁGINA & TEMA APROAR (WIDE - CLARO) ---
st.set_page_config(page_title="APROAR - Controle de Presenças", page_icon="👷", layout="wide")

# CSS Moderno com Fundo Branco e Azul APROAR
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #0F172A;
    }
    h1, h2, h3, h4, p, label, .stMarkdown, span {
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    /* Sidebar Clara e Moderna */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0;
        padding-top: 15px;
    }
    /* Inputs e Selects Limpos */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="base-input"] > div, 
    div[data-baseweb="input"] > div,
    input, textarea, div[role="combobox"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
        border-radius: 8px !important;
    }
    ul[data-baseweb="menu"], div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    li[role="option"]:hover {
        background-color: #DBEAFE !important;
        color: #1D4ED8 !important;
    }
    div[data-baseweb="tag"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    /* Botões Principais no Azul APROAR */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
    }
    /* Containers com Efeito de Elevação Suave */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 16px;
    }
    .streamlit-expanderHeader {
        background-color: #F1F5F9 !important;
        border-radius: 8px;
    }
    hr {
        border-color: #E2E8F0 !important;
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

def normalizar(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').upper().strip()

def get_cor_funcao(funcao):
    cores = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛"]
    hash_num = sum(ord(c) for c in str(funcao))
    return cores[hash_num % len(cores)]

def calcular_diaria_proporcional(status, valor_diaria_base):
    diaria = float(valor_diaria_base or 240.0)
    if status in ["Presente (Integral)", "Presente", "Extra"]:
        return diaria
    elif status in ["Presente (Só Manhã)", "Presente (Só Tarde)", "Saída Antecipada"]:
        return diaria / 2.0
    return 0.0

def to_latin(texto):
    if not texto: return ""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# --- BUSCA DE DADOS ---
def buscar_obras():
    try: return supabase.table("obras").select("*").execute().data
    except Exception: return []

def buscar_colaboradores():
    try: 
        res = supabase.table("colaboradores").select("*").execute().data
        return res if res else []
    except Exception: 
        return []

obras = buscar_obras()
colaboradores = buscar_colaboradores()

dict_colaboradores = {c['id']: c for c in colaboradores} if colaboradores else {}
dict_obras = {o['id']: o for o in obras} if obras else {}

ENGENHEIROS = ["EDUARDO", "GABRIEL", "GUSTAVO", "JOEL", "NETO", "PAULO", "SOARES", "VICTOR"]

# --- FUNÇÃO AUXILIAR PARA RENDERIZAR A ABA DE DISPONIBILIDADE ---
def render_aba_disponibilidade(key_suffix=""):
    st.markdown("### 👥 Disponibilidade de Equipe por Função")
    st.write("Consulte quem já está convocado e quem está disponível para a data selecionada.")
    
    data_disp = st.date_input("Data de referência:", value=datetime.date.today() + datetime.timedelta(days=1), format="DD/MM/YYYY", key=f"data_disp_{key_suffix}")
    
    try:
        convs_disp = supabase.table("convocacoes").select("*").eq("data", data_disp.isoformat()).execute().data
    except:
        convs_disp = []
        
    ids_ocupados = {c['colaborador_id'] for c in convs_disp}
    funcoes = sorted(list(set([c['funcao'] for c in colaboradores])))
    
    if not funcoes:
        st.info("Nenhum colaborador cadastrado.")
        return

    st.markdown("---")
    for func in funcoes:
        with st.container(border=True):
            st.markdown(f"#### 🔹 {func}")
            colabs_func = [c for c in colaboradores if c['funcao'] == func]
            ocupados_func = [c for c in colabs_func if c['id'] in ids_ocupados]
            disponiveis_func = [c for c in colabs_func if c['id'] not in ids_ocupados]
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**🔴 Convocados ({len(ocupados_func)})**")
                if ocupados_func:
                    for oc in ocupados_func:
                        conv_info = next((item for item in convs_disp if item['colaborador_id'] == oc['id']), None)
                        obra_nome = "Obra"
                        if conv_info:
                            ob_inf = dict_obras.get(conv_info['obra_id'], {})
                            obra_nome = f"{ob_inf.get('unidade','')} - {ob_inf.get('nome','')}"
                        st.markdown(f"• {oc['nome']} <br><small style='color:#64748B;'>({obra_nome})</small>", unsafe_allow_html=True)
                else:
                    st.caption("Nenhum.")
                    
            with c2:
                st.markdown(f"**🟢 Disponíveis ({len(disponiveis_func)})**")
                if disponiveis_func:
                    for disp in disponiveis_func:
                        st.markdown(f"• {disp['nome']}")
                else:
                    st.caption("Nenhum disponível.")

# --- VERIFICAÇÃO DE MODO (CAMPO vs ADM) ---
parametros_url = st.query_params
modo_campo = parametros_url.get("modo") == "campo"

if modo_campo:
    st.markdown("### 📲 Acesso Rápido - Campo")
    tab_apontamento_campo, tab_convocacao_campo, tab_disp_campo = st.tabs([
        "✅ Apontamento", "📋 Convocação", "👥 Disponibilidade"
    ])
    
    with tab_apontamento_campo:
        engenheiro_apont = st.selectbox("Seu Nome:", ENGENHEIROS, key="eng_apont_c")
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
            
            if st.button("✅ Marcar Todos como Presentes"):
                for c in convocacoes_render:
                    supabase.table("convocacoes").update({"status": "Presente (Integral)"}).eq("id", c['id']).execute()
                st.success("Atualizado!")
                st.rerun()

            opcoes_status = ["Presente (Integral)", "Presente (Só Manhã)", "Presente (Só Tarde)", "Saída Antecipada", "Falta", "Atestado", "Extra"]
            for conv in convocacoes_render:
                with st.container(border=True):
                    c_id = conv['id']
                    dados_colab = dict_colaboradores.get(conv['colaborador_id'], {"nome": "Desconhecido", "funcao": "-"})
                    nome = dados_colab['nome']
                    funcao = dados_colab['funcao']
                    status_atual = conv.get("status", "Presente (Integral)")
                    idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                    
                    st.markdown(f"**{nome}** (`{funcao}`)")
                    status_sel = st.selectbox("Status", opcoes_status, index=idx, key=f"st_{c_id}")
                    if status_sel != status_atual:
                        supabase.table("convocacoes").update({"status": status_sel}).eq("id", c_id).execute()
                        st.rerun()
                    
                    with st.expander("💸 Extra / Obs"):
                        val_atual = float(conv.get("valor_extra") or 0.0)
                        obs_atual = conv.get("observacao") or ""
                        val_extra = st.number_input("Extra (R$)", value=val_atual, step=10.0, key=f"v_{c_id}")
                        obs = st.text_input("Obs / Justificativa", value=obs_atual, key=f"o_{c_id}")
                        if st.button("Salvar", key=f"btn_{c_id}"):
                            supabase.table("convocacoes").update({"valor_extra": val_extra, "observacao": obs}).eq("id", c_id).execute()
                            st.success("Salvo!")
        else:
            st.warning("Nenhuma equipe convocada para hoje.")

    with tab_convocacao_campo:
        if obras and colaboradores:
            engenheiro_conv = st.selectbox("Seu Nome:", ENGENHEIROS, key="eng_c_conv")
            amanha = datetime.date.today() + datetime.timedelta(days=1)
            data_conv = st.date_input("Data:", value=amanha, format="DD/MM/YYYY", key="d_c_campo")
            
            unidades_unicas = sorted(list(set([o['unidade'] for o in obras])))
            unidade_selecionada = st.selectbox("Unidade:", unidades_unicas, key="u_c_sel")
            
            obras_da_unidade = {o['nome']: o['id'] for o in obras if o['unidade'] == unidade_selecionada}
            obra_selecionada = st.selectbox("Obra:", list(obras_da_unidade.keys()), key="o_c_sel")

            turno_conv = st.selectbox("Turno / Período:", ["Integral", "Manhã", "Tarde"], key="turno_c_sel")
            funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
            frente_selecionada = st.selectbox("Função:", funcoes_disponiveis, key="f_c_sel")

            colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
            opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}
            
            equipe_selecionada = st.multiselect("Colaboradores:", list(opcoes_colaboradores.keys()), key="eq_c_sel")

            with st.container(border=True):
                st.markdown(f"#### 👁️ Panorama ({data_conv.strftime('%d/%m/%Y')})")
                try:
                    convs_eng_data = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_conv).eq("data", data_conv.isoformat()).execute().data
                except:
                    convs_eng_data = []
                
                ids_ja_alocados_eng = {c['colaborador_id'] for c in convs_eng_data}
                nomes_ja_alocados = [dict_colaboradores.get(cid, {}).get('nome', '') for cid in ids_ja_alocados_eng]
                if nomes_ja_alocados:
                    st.caption("Já escalados hoje: " + ", ".join(nomes_ja_alocados))
                else:
                    st.caption("Nenhum escalado.")

            if st.button("Confirmar Convocação", type="primary", use_container_width=True):
                if not equipe_selecionada:
                    st.warning("Selecione alguém.")
                else:
                    obra_id = obras_da_unidade[obra_selecionada]
                    sucessos = 0
                    for nome in equipe_selecionada:
                        c_id = opcoes_colaboradores[nome]
                        supabase.table("convocacoes").insert({
                            "obra_id": obra_id,
                            "colaborador_id": c_id,
                            "data": data_conv.isoformat(),
                            "engenheiro": engenheiro_conv,
                            "status": "Presente (Integral)",
                            "valor_extra": 0,
                            "observacao": f"Turno: {turno_conv}"
                        }).execute()
                        sucessos += 1
                    st.success(f"✅ {sucessos} colaborador(es) convocado(s) para o turno {turno_conv}!")
                    st.rerun()
        else:
            st.info("Cadastre obras e colaboradores na administração.")

    with tab_disp_campo:
        render_aba_disponibilidade("campo")

else:
    # ==========================================
    # PAINEL ADMINISTRATIVO (FUNDO BRANCO)
    # ==========================================
    
    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "🎛️ Dashboard"

    # --- MENU LATERAL (SIDEBAR) ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #0F172A; letter-spacing: 2px;'>APROAR</h2>", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        
        itens_menu = ["🎛️ Dashboard", "📋 Convocação", "✅ Apontamento", "📊 Relatórios", "📈 Indicadores", "👥 Disponibilidade", "⚙️ Configurações"]
        
        for item in itens_menu:
            if st.button(item, key=f"btn_nav_{item}", use_container_width=True):
                st.session_state.menu_ativo = item
                st.rerun()

        st.markdown("---")
        st.caption("APROAR Engenharia © 2026")

    menu_escolhido = st.session_state.menu_ativo

    # --- CONTEÚDO PRINCIPAL ---

    # 1. DASHBOARD
    if menu_escolhido == "🎛️ Dashboard":
        st.markdown("## 🎛️ Dashboard e Auditoria de Presenças")
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            data_filtro_dash = st.date_input("Data:", value=datetime.date.today(), format="DD/MM/YYYY", key="d_dash")
        with col_f2:
            unidades_cadastradas = sorted(list(set([o['unidade'] for o in obras]))) if obras else []
            unidade_dash = st.selectbox("Unidade:", ["TODAS"] + unidades_cadastradas, key="u_dash")
        with col_f3:
            busca_colab = st.text_input("Buscar colaborador:", placeholder="Ex: Erivaldo...", key="busca_colab_dash")
        with col_f4:
            status_filtro_dash = st.selectbox("Status:", ["Todos", "Presente (Integral)", "Presente (Só Manhã)", "Presente (Só Tarde)", "Saída Antecipada", "Falta", "Atestado", "Extra"], key="st_dash")

        try:
            if busca_colab:
                query_dash = supabase.table("convocacoes").select("*")
            else:
                query_dash = supabase.table("convocacoes").select("*").eq("data", data_filtro_dash.isoformat())

            if unidade_dash != "TODAS":
                obras_ids_unidade = [o['id'] for o in obras if o['unidade'] == unidade_dash]
                if obras_ids_unidade:
                    query_dash = query_dash.in_("obra_id", obras_ids_unidade)
                else:
                    query_dash = query_dash.eq("obra_id", "00000000-0000-0000-0000-000000000000")
            convs_dash = query_dash.execute().data
        except:
            convs_dash = []

        lista_processada = []
        for c in convs_dash:
            ob = dict_obras.get(c['obra_id'], {"unidade": "GERAL", "nome": "Desconhecida"})
            colab = dict_colaboradores.get(c['colaborador_id'], {"nome": "Desconhecido", "funcao": "-", "valor_diaria": 240.0})
            
            if busca_colab:
                if normalizar(busca_colab) not in normalizar(colab['nome']):
                    continue

            status_item = c.get('status', 'Presente (Integral)')
            if status_filtro_dash != "Todos" and status_item != status_filtro_dash:
                continue

            diaria_calc = calcular_diaria_proporcional(status_item, colab.get('valor_diaria'))
            extra = float(c.get('valor_extra') or 0.0)
            
            lista_processada.append({
                "id": c['id'],
                "data_item": c.get('data', ''),
                "engenheiro": c.get('engenheiro', 'N/A'),
                "unidade": ob['unidade'],
                "obra_nome": ob['nome'],
                "colab_nome": colab['nome'],
                "colab_funcao": colab['funcao'],
                "status": status_item,
                "valor_extra": extra,
                "observacao": c.get('observacao', ''),
                "custo": diaria_calc + extra
            })

        total_conv = len(lista_processada)
        total_pres = len([x for x in lista_processada if "Presente" in x['status'] or x['status'] == 'Extra'])
        total_atest = len([x for x in lista_processada if x['status'] == 'Atestado'])
        total_falt = len([x for x in lista_processada if x['status'] == 'Falta'])
        total_extra_st = len([x for x in lista_processada if x['status'] == 'Extra'])
        custo_geral_dia = sum([x['custo'] for x in lista_processada])

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("TOTAL", total_conv)
        m2.metric("PRES.", total_pres)
        m3.metric("ATEST.", total_atest)
        m4.metric("FALTAS", total_falt)
        m5.metric("EXTRAS", total_extra_st)
        m6.metric("CUSTO", f"R$ {custo_geral_dia:.0f}")

        st.markdown("---")

        if not lista_processada:
            st.info("Nenhum registro encontrado.")
        else:
            if st.button("✅ Marcar Todos como Presentes (Integral)"):
                for item in lista_processada:
                    supabase.table("convocacoes").update({"status": "Presente (Integral)"}).eq("id", item['id']).execute()
                st.success("Atualizado!")
                st.rerun()

            df_view = pd.DataFrame(lista_processada)
            for obra_n in df_view['obra_nome'].unique():
                subset = df_view[df_view['obra_nome'] == obra_n]
                unidade_nome = subset.iloc[0]['unidade']
                eng_resp = subset.iloc[0]['engenheiro']
                
                with st.container(border=True):
                    st.markdown(f"**{unidade_nome}** — *{obra_n}* &nbsp;|&nbsp; Eng: `{eng_resp}`")
                    for idx, row in subset.iterrows():
                        c_id = row['id']
                        c1, c2, c3 = st.columns([3, 2, 2])
                        with c1:
                            st.markdown(f"{row['colab_nome']} &nbsp; `{row['colab_funcao']}` &nbsp; <small style='color:#64748B;'>({row['data_item']})</small>", unsafe_allow_html=True)
                            obs_val = st.text_input("Obs", value=row['observacao'], placeholder="Obs...", key=f"obs_{c_id}", label_visibility="collapsed")
                            if obs_val != row['observacao']:
                                supabase.table("convocacoes").update({"observacao": obs_val}).eq("id", c_id).execute()
                        with c2:
                            opcoes_st = ["Presente (Integral)", "Presente (Só Manhã)", "Presente (Só Tarde)", "Saída Antecipada", "Falta", "Atestado", "Extra"]
                            st_atual = row['status']
                            idx_st = opcoes_st.index(st_atual) if st_atual in opcoes_st else 0
                            novo_st = st.selectbox("Status", opcoes_st, index=idx_st, key=f"st_{c_id}", label_visibility="collapsed")
                            if novo_st != st_atual:
                                supabase.table("convocacoes").update({"status": novo_st}).eq("id", c_id).execute()
                                st.rerun()
                        with c3:
                            extra_val = st.number_input("Extra", value=float(row['valor_extra']), step=10.0, key=f"ext_{c_id}", label_visibility="collapsed")
                            if extra_val != float(row['valor_extra']):
                                supabase.table("convocacoes").update({"valor_extra": extra_val}).eq("id", c_id).execute()
                            st.caption(f"R$ {row['custo']:.2f}")
                        st.divider()

    # 2. CONVOCAÇÃO
    elif menu_escolhido == "📋 Convocação":
        st.markdown("## 📋 Nova Convocação de Equipe")
        if obras and colaboradores:
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

            turno_conv_adm = st.selectbox("Turno / Período:", ["Integral", "Manhã", "Tarde"], key="turno_conv_adm")
            funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
            frente_selecionada = st.selectbox("Frente de Trabalho (Função):", funcoes_disponiveis)

            colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
            opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}
            equipe_selecionada = st.multiselect("Selecione os colaboradores:", list(opcoes_colaboradores.keys()))

            with st.container(border=True):
                st.markdown(f"**Panorama de {engenheiro_conv} ({data_conv.strftime('%d/%m/%Y')})**")
                try:
                    convs_eng_data = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_conv).eq("data", data_conv.isoformat()).execute().data
                except:
                    convs_eng_data = []
                ids_ja_alocados_eng = {c['colaborador_id'] for c in convs_eng_data}
                nomes_ja_alocados = [dict_colaboradores.get(cid, {}).get('nome', '') for cid in ids_ja_alocados_eng]
                if nomes_ja_alocados:
                    st.caption("Já escalados hoje: " + ", ".join(nomes_ja_alocados))
                else:
                    st.caption("Nenhum escalado ainda.")

            if st.button("Confirmar Convocação", type="primary", use_container_width=True):
                if not equipe_selecionada:
                    st.warning("Selecione alguém.")
                else:
                    obra_id = obras_da_unidade[obra_selecionada]
                    sucessos = 0
                    for nome in equipe_selecionada:
                        c_id = opcoes_colaboradores[nome]
                        supabase.table("convocacoes").insert({
                            "obra_id": obra_id,
                            "colaborador_id": c_id,
                            "data": data_conv.isoformat(),
                            "engenheiro": engenheiro_conv,
                            "status": "Presente (Integral)",
                            "valor_extra": 0,
                            "observacao": f"Turno: {turno_conv_adm}"
                        }).execute()
                        sucessos += 1
                    st.success(f"✅ {sucessos} colaborador(es) convocado(s) para o turno {turno_conv_adm}!")
                    st.rerun()
        else:
            st.info("Cadastre obras e colaboradores na aba Configurações.")

    # 3. APONTAMENTO
    elif menu_escolhido == "✅ Apontamento":
        st.markdown("## ✅ Apontamento Diário de Campo")
        col_eng_ap, col_data_ap = st.columns(2)
        with col_eng_ap:
            engenheiro_apont = st.selectbox("Engenheiro:", ENGENHEIROS, key="eng_apont_adm")
        with col_data_ap:
            data_apont = st.date_input("Data do Apontamento:", value=datetime.date.today(), format="DD/MM/YYYY", key="dt_apont_adm")
        
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
                unidade_filtro = st.selectbox("Unidade:", unidades_convocadas, key="filtro_u_apont_adm")
            obras_convocadas = sorted(list(set([c['dados_obra']['nome'] for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro])))
            with col_oa:
                obra_filtro = st.selectbox("Obra:", obras_convocadas, key="filtro_o_apont_adm")
            
            convocacoes_render = [c for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro and c['dados_obra']['nome'] == obra_filtro]
            
            if st.button("✅ Marcar Todos como Presentes", key="btn_all_present_adm"):
                for c in convocacoes_render:
                    supabase.table("convocacoes").update({"status": "Presente (Integral)"}).eq("id", c['id']).execute()
                st.success("Atualizado!")
                st.rerun()

            opcoes_status = ["Presente (Integral)", "Presente (Só Manhã)", "Presente (Só Tarde)", "Saída Antecipada", "Falta", "Atestado", "Extra"]
            for conv in convocacoes_render:
                with st.container(border=True):
                    c_id = conv['id']
                    dados_colab = dict_colaboradores.get(conv['colaborador_id'], {"nome": "Desconhecido", "funcao": "-"})
                    nome = dados_colab['nome']
                    funcao = dados_colab['funcao']
                    cor = get_cor_funcao(funcao)
                    status_atual = conv.get("status", "Presente (Integral)")
                    idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                    
                    st.markdown(f"**{nome}** &nbsp; {cor} `{funcao}`")
                    status_sel = st.selectbox("Status", opcoes_status, index=idx, key=f"status_adm_{c_id}")
                    if status_sel != status_atual:
                        supabase.table("convocacoes").update({"status": status_sel}).eq("id", c_id).execute()
                        st.rerun()
                    
                    with st.expander("💸 Extra / Obs"):
                        val_atual = float(conv.get("valor_extra") or 0.0)
                        obs_atual = conv.get("observacao") or ""
                        val_extra = st.number_input("Extra (R$)", value=val_atual, step=10.0, key=f"val_adm_{c_id}")
                        obs = st.text_input("Obs / Justificativa", value=obs_atual, key=f"obs_adm_field_{c_id}")
                        if st.button("Salvar Detalhes", key=f"btn_save_adm_{c_id}"):
                            supabase.table("convocacoes").update({"valor_extra": val_extra, "observacao": obs}).eq("id", c_id).execute()
                            st.success("Salvo!")
        else:
            st.warning("Nenhuma equipe convocada para este engenheiro nesta data.")

    # 4. RELATÓRIOS
    elif menu_escolhido == "📊 Relatórios":
        st.markdown("## 📊 Relatório de Custos e Fechamento")
        col_rel_eng, _ = st.columns(2)
        with col_rel_eng:
            eng_relatorio = st.selectbox("Engenheiro:", ["TODOS OS ENGENHEIROS"] + ENGENHEIROS, key="eng_rel")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_inicio_rel = st.date_input("Início:", value=datetime.date.today(), format="DD/MM/YYYY", key="data_ini")
        with col_d2:
            data_fim_rel = st.date_input("Fim:", value=datetime.date.today(), format="DD/MM/YYYY", key="data_fim")
        
        if st.button("Gerar PDF", type="primary"):
            try:
                if data_inicio_rel > data_fim_rel:
                    st.error("Data inicial maior que a final.")
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
                            pdf.set_font("Arial", 'B', 14)
                            pdf.cell(0, 10, txt=to_latin("APROAR - RELATÓRIO DE CUSTOS"), ln=True, align='C')
                            pdf.set_font("Arial", size=10)
                            pdf.cell(0, 8, txt=to_latin(f"Período: {data_inicio_rel.strftime('%d/%m/%Y')} a {data_fim_rel.strftime('%d/%m/%Y')} | Eng: {eng}"), ln=True, align='C')
                            pdf.ln(5)
                            
                            custo_total_engenheiro = 0.0
                            for o_id, apontamentos in obras_eng.items():
                                dados_ob = dict_obras.get(o_id, {"nome": "N/A", "unidade": "N/A"})
                                pdf.set_font("Arial", 'B', 10)
                                pdf.set_fill_color(220, 220, 220)
                                pdf.cell(0, 7, txt=to_latin(f"Unidade: {dados_ob['unidade']} | Obra: {dados_ob['nome']}"), ln=True, fill=True)
                                
                                pdf.set_font("Arial", 'B', 9)
                                pdf.cell(25, 6, to_latin("Data"), border=1, align='C')
                                pdf.cell(65, 6, to_latin("Colaborador"), border=1)
                                pdf.cell(50, 6, to_latin("Função"), border=1)
                                pdf.cell(32, 6, to_latin("Status"), border=1, align='C')
                                pdf.cell(24, 6, to_latin("Diária"), border=1, align='C')
                                pdf.cell(24, 6, to_latin("Extra"), border=1, align='C')
                                pdf.cell(51, 6, to_latin("Obs"), border=1, ln=True)
                                
                                pdf.set_font("Arial", '', 8)
                                custo_total_obra = 0.0
                                for row in apontamentos:
                                    colab = dict_colaboradores.get(row['colaborador_id'], {})
                                    nome = colab.get('nome', 'N/A')
                                    funcao = colab.get('funcao', 'N/A')
                                    status = row.get('status', 'Presente (Integral)')
                                    extra = float(row.get('valor_extra', 0) or 0)
                                    obs = row.get('observacao', '')
                                    diaria_base = calcular_diaria_proporcional(status, colab.get('valor_diaria'))
                                    custo_total_obra += (diaria_base + extra)
                                    
                                    pdf.cell(25, 6, to_latin(row.get('data', '')), border=1, align='C')
                                    pdf.cell(65, 6, to_latin(nome[:28]), border=1)
                                    pdf.cell(50, 6, to_latin(funcao[:20]), border=1)
                                    pdf.cell(32, 6, to_latin(status[:14]), border=1, align='C')
                                    pdf.cell(24, 6, to_latin(f"R$ {diaria_base:.2f}"), border=1, align='C')
                                    pdf.cell(24, 6, to_latin(f"R$ {extra:.2f}"), border=1, align='C')
                                    pdf.cell(51, 6, to_latin(obs[:25]), border=1, ln=True)
                                
                                pdf.set_font("Arial", 'B', 9)
                                pdf.set_fill_color(245, 245, 245)
                                pdf.cell(224, 6, to_latin("TOTAL DA OBRA:"), border=1, align='R', fill=True)
                                pdf.cell(53, 6, to_latin(f"R$ {custo_total_obra:.2f}"), border=1, align='C', fill=True, ln=True)
                                pdf.ln(4)
                                custo_total_engenheiro += custo_total_obra
                            pdf.set_font("Arial", 'B', 10)
                            pdf.cell(0, 7, to_latin(f"TOTAL GERAL ({eng}): R$ {custo_total_engenheiro:.2f}"), ln=True, align='R')
                        
                        pdf_bytes = pdf.output(dest='S').encode('latin1')
                        st.download_button("📥 Baixar Relatório PDF", data=pdf_bytes, file_name="Relatorio_Custos_Aproar.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Erro: {e}")

    # 5. INDICADORES
    elif menu_escolhido == "📈 Indicadores":
        st.markdown("## 📈 Indicadores de Desempenho")
        try:
            all_conv = supabase.table("convocacoes").select("*").execute().data
            if not all_conv:
                st.info("Nenhum dado registrado para gerar indicadores.")
            else:
                df_conv = pd.DataFrame(all_conv)
                df_conv['nome_colab'] = df_conv['colaborador_id'].map(lambda cid: dict_colaboradores.get(cid, {}).get('nome', 'Desconhecido'))
                df_conv['funcao_colab'] = df_conv['colaborador_id'].map(lambda cid: dict_colaboradores.get(cid, {}).get('funcao', 'Desconhecido'))

                taxa_assiduidade = (len(df_conv[df_conv['status'].isin(['Presente (Integral)', 'Presente (Só Manhã)', 'Presente (Só Tarde)', 'Extra'])]) / len(df_conv) * 100) if len(df_conv) > 0 else 0.0
                st.metric("Taxa de Assiduidade Geral", value=f"{taxa_assiduidade:.1f}%")
                st.markdown("---")

                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1:
                    st.markdown("**Top 10 Faltas**")
                    df_f = df_conv[df_conv['status'] == 'Falta']
                    if not df_f.empty:
                        st.dataframe(df_f.groupby(['nome_colab', 'funcao_colab']).size().reset_index(name='Total').sort_values(by='Total', ascending=False).head(10).rename(columns={'nome_colab':'Colaborador', 'funcao_colab':'Função'}), hide_index=True, use_container_width=True)
                    else:
                        st.caption("Sem faltas.")
                with col_i2:
                    st.markdown("**Top 10 Atestados**")
                    df_a = df_conv[df_conv['status'] == 'Atestado']
                    if not df_a.empty:
                        st.dataframe(df_a.groupby(['nome_colab', 'funcao_colab']).size().reset_index(name='Total').sort_values(by='Total', ascending=False).head(10).rename(columns={'nome_colab':'Colaborador', 'funcao_colab':'Função'}), hide_index=True, use_container_width=True)
                    else:
                        st.caption("Sem atestados.")
                with col_i3:
                    st.markdown("**Top 10 Mais Presentes**")
                    df_p = df_conv[df_conv['status'].isin(['Presente (Integral)', 'Presente (Só Manhã)', 'Presente (Só Tarde)', 'Extra'])]
                    if not df_p.empty:
                        st.dataframe(df_p.groupby(['nome_colab', 'funcao_colab']).size().reset_index(name='Total').sort_values(by='Total', ascending=False).head(10).rename(columns={'nome_colab':'Colaborador', 'funcao_colab':'Função'}), hide_index=True, use_container_width=True)
                    else:
                        st.caption("Sem presenças.")
        except Exception as e:
            st.error(f"Erro ao carregar indicadores: {e}")

    # 6. DISPONIBILIDADE
    elif menu_escolhido == "👥 Disponibilidade":
        render_aba_disponibilidade("adm")

    # 7. CONFIGURAÇÕES
    elif menu_escolhido == "⚙️ Configurações":
        st.markdown("## ⚙️ Sincronização e Manutenção")
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
                    st.success("Obras importadas!")
                    st.rerun()

        st.divider()
        arquivo_excel = st.file_uploader("Planilha Excel de Colaboradores", type=["xlsx"])
        if arquivo_excel and st.button("🔄 Importar Colaboradores"):
            xls = pd.ExcelFile(arquivo_excel)
            df = pd.read_excel(xls, sheet_name="Base de dados" if "Base de dados" in xls.sheet_names else xls.sheet_names[0])
            existentes = {c['nome'] for c in colaboradores}
            novos = [{"nome": str(r.get('NOME', '')).strip(), "funcao": limpar_funcao(str(r.get('FUNÇÃO', ''))), "valor_diaria": float(r.get('VALOR DIÁRIA (R$)', 240) or 240), "ativo": True} for _, r in df.iterrows() if str(r.get('NOME', '')).strip() and str(r.get('NOME', '')).strip() not in existentes]
            if novos:
                supabase.table("colaboradores").insert(novos).execute()
                st.success("Colaboradores importados!")
                st.rerun()

        st.divider()
        if st.button("🗑️ Apagar Todas as Convocações", type="secondary"):
            try:
                res = supabase.table("convocacoes").select("id").execute()
                if res.data:
                    for item in res.data:
                        supabase.table("convocacoes").delete().eq("id", item['id']).execute()
                    st.success("Convocações apagadas!")
                    st.rerun()
                else:
                    st.info("Nenhuma convocação encontrada.")
            except Exception as e:
                st.error(f"Erro: {e}")
