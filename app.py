import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
json = pd.io.json  # Compatibilidade
import json
from fpdf import FPDF
import unicodedata
import re
import os
import io
import requests
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# --- CONFIGURAÇÕES DA PÁGINA & TEMA APROAR (WIDE - ESCURO / COMPACTO) ---
st.set_page_config(page_title="APROAR - Controle de Presenças", page_icon="👷", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    h1, h2, h3, h4, p, label, .stMarkdown, span {
        color: #F8FAFC !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155;
        width: 240px !important;
        min-width: 240px !important;
        padding-top: 15px;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-left: 15px;
        padding-right: 15px;
    }
    div[data-baseweb="select"] > div, 
    div[data-baseweb="base-input"] > div, 
    div[data-baseweb="input"] > div,
    input, textarea, div[role="combobox"] {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border-color: #334155 !important;
        border-radius: 8px !important;
    }
    ul[data-baseweb="menu"], div[data-baseweb="popover"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
    }
    li[role="option"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
    }
    li[role="option"]:hover {
        background-color: #334155 !important;
        color: #60A5FA !important;
    }
    div[data-baseweb="tag"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 16px;
    }
    .streamlit-expanderHeader {
        background-color: #334155 !important;
        border-radius: 8px;
    }
    hr {
        border-color: #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MESES EM PORTUGUÊS ---
MESES_PT = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
}

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

# --- SINCRONIZAÇÃO COM TRELLO (MÊS VIGENTE OU SELEÇÃO MANUAL) ---
def obter_listas_trello():
    url_trello = "https://trello.com/b/TX8hGvmI.json"
    try:
        resp = requests.get(url_trello, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('lists', []), data.get('cards', [])
    except Exception:
        pass
    return [], []

def executar_sincronizacao_trello(id_lista_target=None):
    lists, cards = obter_listas_trello()
    if not lists:
        return False, "Erro ao acessar o quadro público do Trello."
    
    id_lista_execucao = id_lista_target
    nome_lista_alvo = ""
    
    # Caso nenhuma lista seja explicitamente selecionada, busca a do mês vigente (ex: "MEDIÇÃO AGOSTO 2026")
    if not id_lista_execucao:
        hoje = datetime.date.today()
        mes_vigente = MESES_PT.get(hoje.month, "")
        ano_vigente = str(hoje.year)
        termo_busca = f"MEDICAO {mes_vigente} {ano_vigente}"
        
        for lst in lists:
            nome_norm = normalizar(lst.get('name', ''))
            if termo_busca in nome_norm or "EM EXECUCAO" in nome_norm:
                id_lista_execucao = lst.get('id')
                nome_lista_alvo = lst.get('name')
                break
    else:
        for lst in lists:
            if lst.get('id') == id_lista_execucao:
                nome_lista_alvo = lst.get('name')
                break

    if not id_lista_execucao:
        return False, "Nenhuma lista do mês vigente ou de execução foi encontrada no Trello."
    
    cards_execucao = [c for c in cards if c.get('idList') == id_lista_execucao and not c.get('closed', False)]
    obras_atuais = buscar_obras()
    nomes_cadastrados = {normalizar(o['nome']) for o in obras_atuais}
    
    novas_inseridas = 0
    for card in cards_execucao:
        nome_card = card.get('name', '').strip()
        if not nome_card: continue
        
        unidade_card = identificar_unidade(nome_card)
        if normalizar(nome_card) not in nomes_cadastrados:
            supabase.table("obras").insert({
                "unidade": unidade_card,
                "nome": nome_card
            }).execute()
            novas_inseridas += 1
            nomes_cadastrados.add(normalizar(nome_card))
            
    st.cache_data.clear()
    return True, f"Sincronização de '{nome_lista_alvo}' realizada com sucesso! {novas_inseridas} nova(s) obra(s) adicionada(s)."

# --- BUSCA DE DADOS COM CACHE ---
@st.cache_data(ttl=30)
def buscar_obras():
    try: return supabase.table("obras").select("*").execute().data
    except Exception: return []

@st.cache_data(ttl=30)
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
    st.markdown("### 👥 DISPONIBILIDADE DE EQUIPE POR FUNÇÃO")
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
            st.markdown(f"#### 🔹 {func.upper()}")
            colabs_func = [c for c in colaboradores if c['funcao'] == func]
            ocupados_func = [c for c in colabs_func if c['id'] in ids_ocupados]
            disponiveis_func = [c for c in colabs_func if c['id'] not in ids_ocupados]
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**🔴 CONVOCADOS ({len(ocupados_func)})**")
                if ocupados_func:
                    for oc in ocupados_func:
                        conv_info = next((item for item in convs_disp if item['colaborador_id'] == oc['id']), None)
                        obra_nome = "Obra"
                        eng_resp = ""
                        if conv_info:
                            ob_inf = dict_obras.get(conv_info['obra_id'], {})
                            obra_nome = f"{ob_inf.get('unidade','')} - {ob_inf.get('nome','')}"
                            eng_resp = f" (Eng: {conv_info.get('engenheiro', 'N/A')})"
                        st.markdown(f"• {oc['nome']} <br><small style='color:#94A3B8;'>({obra_nome}{eng_resp})</small>", unsafe_allow_html=True)
                else:
                    st.caption("Nenhum.")
                    
            with c2:
                st.markdown(f"**🟢 DISPONÍVEIS ({len(disponiveis_func)})**")
                if disponiveis_func:
                    for disp in disponiveis_func:
                        st.markdown(f"• {disp['nome']}")
                else:
                    st.caption("Nenhum disponível.")

# --- VERIFICAÇÃO DE MODO (CAMPO/ENGENHEIRO VIA ?eng OU ?modo=campo) ---
parametros_url = st.query_params
modo_campo = "eng" in parametros_url or parametros_url.get("modo") in ["campo", "eng"]

if modo_campo:
    st.markdown("### 📲 ACESSO ENGENHEIRO DE CAMPO")
    tab_apontamento_campo, tab_convocacao_campo, tab_disp_campo = st.tabs([
        "✅ APONTAMENTO", "📋 CONVOCAÇÃO", "👥 DISPONIBILIDADE"
    ])
    
    with tab_apontamento_campo:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            engenheiro_apont = st.selectbox("Seu Nome (Engenheiro):", ENGENHEIROS, key="eng_apont_c")
            data_apont = st.date_input("Data do Apontamento:", value=datetime.date.today(), format="DD/MM/YYYY", key="dt_apont_c")
        
        try:
            convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", data_apont.isoformat()).execute().data
        except:
            convocacoes_hoje = []

        if convocacoes_hoje:
            for conv in convocacoes_hoje:
                conv['dados_obra'] = dict_obras.get(conv['obra_id'], {"unidade": "Desconhecida", "nome": "Desconhecida"})
                
            unidades_convocadas = sorted(list(set([c['dados_obra']['unidade'] for c in convocacoes_hoje])))
            with col_c2:
                unidade_filtro = st.selectbox("Unidade:", ["TODAS"] + unidades_convocadas, key="f_u_c")
                obras_convocadas = sorted(list(set([c['dados_obra']['nome'] for c in convocacoes_hoje if unidade_filtro == "TODAS" or c['dados_obra']['unidade'] == unidade_filtro])))
                obra_filtro = st.selectbox("Obra / Serviço:", ["TODAS"] + obras_convocadas, key="f_o_c")
            
            convocacoes_render = [
                c for c in convocacoes_hoje 
                if (unidade_filtro == "TODAS" or c['dados_obra']['unidade'] == unidade_filtro)
                and (obra_filtro == "TODAS" or c['dados_obra']['nome'] == obra_filtro)
            ]
            
            if st.button("✅ MARCAR TODOS COMO PRESENTES", key="btn_all_pres_campo"):
                for c in convocacoes_render:
                    supabase.table("convocacoes").update({"status": "Presente (Integral)"}).eq("id", c['id']).execute()
                st.success("Todos marcados como Presente (Integral)!")
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
                        val_extra = st.number_input("Horas Extras / Valor (R$)", value=val_atual, step=10.0, key=f"v_{c_id}")
                        obs = st.text_input("Obs / Justificativa", value=obs_atual, key=f"o_{c_id}")
                        if st.button("Salvar", key=f"btn_{c_id}"):
                            supabase.table("convocacoes").update({"valor_extra": val_extra, "observacao": obs}).eq("id", c_id).execute()
                            st.success("Salvo!")
        else:
            st.warning("Nenhuma equipe convocada para este engenheiro na data selecionada.")

    with tab_convocacao_campo:
        if obras and colaboradores:
            engenheiro_conv = st.selectbox("Seu Nome (Engenheiro):", ENGENHEIROS, key="eng_c_conv")
            data_conv_auto = datetime.date.today() + datetime.timedelta(days=1)
            st.info(f"📅 **Data de Convocação Automática:** {data_conv_auto.strftime('%d/%m/%Y')} (Dia seguinte)")
            st.write("⏱️ **Turno Fixo:** `Integral`")

            unidades_unicas = sorted(list(set([o['unidade'] for o in obras])))
            unidade_selecionada = st.selectbox("Unidade:", unidades_unicas, key="u_c_sel")
            
            obras_da_unidade = {o['nome']: o['id'] for o in obras if o['unidade'] == unidade_selecionada}
            obra_selecionada = st.selectbox("Obra / Serviço:", list(obras_da_unidade.keys()), key="o_c_sel")

            funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
            filtro_funcao = st.selectbox("Filtrar por Função (Opcional):", ["TODAS"] + funcoes_disponiveis, key="f_c_sel_campo")

            if filtro_funcao != "TODAS":
                colabs_filtrados = [c for c in colaboradores if c['funcao'] == filtro_funcao]
            else:
                colabs_filtrados = colaboradores

            mapa_colab_opcoes = {f"{c['nome']}  ({c['funcao']})": c['id'] for c in colabs_filtrados}
            equipe_selecionada = st.multiselect("Buscar / Selecionar Colaboradores:", list(mapa_colab_opcoes.keys()), key="eq_c_sel_campo")

            if st.button("CONFIRMAR CONVOCAÇÃO", type="primary", use_container_width=True, key="btn_conv_campo"):
                if not equipe_selecionada:
                    st.warning("Selecione pelo menos um colaborador.")
                else:
                    obra_id = obras_da_unidade[obra_selecionada]
                    sucessos = 0
                    for label_colab in equipe_selecionada:
                        c_id = mapa_colab_opcoes[label_colab]
                        supabase.table("convocacoes").insert({
                            "obra_id": obra_id,
                            "colaborador_id": c_id,
                            "data": data_conv_auto.isoformat(),
                            "engenheiro": engenheiro_conv,
                            "status": "Presente (Integral)",
                            "valor_extra": 0,
                            "observacao": "Turno: Integral"
                        }).execute()
                        sucessos += 1
                    st.success(f"✅ {sucessos} colaborador(es) convocado(s) para o turno Integral!")
                    st.rerun()
        else:
            st.info("Cadastre obras e colaboradores na administração.")

    with tab_disp_campo:
        render_aba_disponibilidade("campo")

else:
    # ==========================================
    # PAINEL ADMINISTRATIVO (TEMA ESCURO)
    # ==========================================
    
    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "🎛️ DASHBOARD"

    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #FFFFFF; letter-spacing: 2px;'>APROAR</h2>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; font-size: 10px; color: #94A3B8; letter-spacing: 1.5px; margin-top: -5px; margin-bottom: 20px; font-weight: 700;'>CONTROLE DE APONTAMENTOS</p>", unsafe_allow_html=True)
        
        itens_menu = [
            "🎛️ DASHBOARD", 
            "📋 CONVOCAÇÃO", 
            "✅ APONTAMENTO", 
            "📊 RELATÓRIOS", 
            "📈 INDICADORES", 
            "👥 DISPONIBILIDADE", 
            "⚙️ CONFIGURAÇÕES"
        ]
        
        for item in itens_menu:
            if st.button(item, key=f"btn_nav_{item}", use_container_width=True):
                st.session_state.menu_ativo = item
                st.rerun()

        st.markdown("---")
        st.caption("APROAR Engenharia © 2026")

    menu_escolhido = st.session_state.menu_ativo

    # --- 1. DASHBOARD ---
    if menu_escolhido == "🎛️ DASHBOARD":
        st.markdown("## 🎛️ DASHBOARD E AUDITORIA DE PRESENÇAS")
        
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        with col_f1:
            data_filtro_dash = st.date_input("Data:", value=datetime.date.today(), format="DD/MM/YYYY", key="d_dash")
        with col_f2:
            unidades_cadastradas = sorted(list(set([o['unidade'] for o in obras]))) if obras else []
            unidade_dash = st.selectbox("Unidade:", ["TODAS"] + unidades_cadastradas, key="u_dash")
        with col_f3:
            eng_dash_filtro = st.selectbox("Engenheiro:", ["TODOS"] + ENGENHEIROS, key="eng_dash_f")
        with col_f4:
            busca_colab = st.text_input("Buscar colaborador:", placeholder="Ex: Erivaldo...", key="busca_colab_dash")
        with col_f5:
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
            
            if eng_dash_filtro != "TODOS":
                query_dash = query_dash.eq("engenheiro", eng_dash_filtro)

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
            st.info("Nenhum registro encontrado para os filtros selecionados.")
        else:
            if st.button("✅ MARCAR TODOS COMO PRESENTES (INTEGRAL)"):
                for item in lista_processada:
                    supabase.table("convocacoes").update({"status": "Presente (Integral)"}).eq("id", item['id']).execute()
                st.success("Atualizado!")
                st.rerun()

            df_view = pd.DataFrame(lista_processada)
            for eng_resp in df_view['engenheiro'].unique():
                df_eng = df_view[df_view['engenheiro'] == eng_resp]
                st.markdown(f"### 👷 Engenheiro Responsável: `{eng_resp}`")
                
                for obra_n in df_eng['obra_nome'].unique():
                    subset = df_eng[df_eng['obra_nome'] == obra_n]
                    unidade_nome = subset.iloc[0]['unidade']
                    
                    with st.container(border=True):
                        st.markdown(f"**Unidade:** {unidade_nome} &nbsp;|&nbsp; **Obra:** {obra_n}")
                        for idx, row in subset.iterrows():
                            c_id = row['id']
                            c1, c2, c3 = st.columns([3, 2, 2])
                            with c1:
                                st.markdown(f"{row['colab_nome']} &nbsp; `{row['colab_funcao']}` &nbsp; <small style='color:#94A3B8;'>({row['data_item']})</small>", unsafe_allow_html=True)
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

    # --- 2. CONVOCAÇÃO ---
    elif menu_escolhido == "📋 CONVOCAÇÃO":
        st.markdown("## 📋 CONVOCAÇÃO E GERENCIAMENTO DE EQUIPE")
        tab_nova_conv, tab_corrigir_conv = st.tabs(["➕ Nova Convocação", "✏️ Correção / Reatribuição Administrativa"])

        with tab_nova_conv:
            if obras and colaboradores:
                col_eng, col_info = st.columns(2)
                with col_eng:
                    engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv_adm")
                with col_info:
                    data_conv_auto = datetime.date.today() + datetime.timedelta(days=1)
                    st.info(f"📅 **Data da Convocação:** {data_conv_auto.strftime('%d/%m/%Y')} (Dia seguinte automático)")
                    st.write("⏱️ **Turno Fixo:** `Integral`")

                unidades_unicas = sorted(list(set([o['unidade'] for o in obras])))
                col_u, col_o = st.columns(2)
                with col_u:
                    unidade_selecionada = st.selectbox("Unidade:", unidades_unicas, key="u_adm_sel")
                obras_da_unidade = {o['nome']: o['id'] for o in obras if o['unidade'] == unidade_selecionada}
                with col_o:
                    obra_selecionada = st.selectbox("Obra / Serviço:", list(obras_da_unidade.keys()), key="o_adm_sel")

                funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
                filtro_funcao_adm = st.selectbox("Filtrar por Função (Opcional):", ["TODAS"] + funcoes_disponiveis, key="f_adm_sel")

                if filtro_funcao_adm != "TODAS":
                    colabs_filtrados_adm = [c for c in colaboradores if c['funcao'] == filtro_funcao_adm]
                else:
                    colabs_filtrados_adm = colaboradores

                mapa_colab_adm = {f"{c['nome']}  ({c['funcao']})": c['id'] for c in colabs_filtrados_adm}
                equipe_selecionada = st.multiselect("Buscar ou Selecionar Colaboradores:", list(mapa_colab_adm.keys()), key="eq_adm_sel")

                with st.container(border=True):
                    st.markdown(f"**Panorama de {engenheiro_conv} ({data_conv_auto.strftime('%d/%m/%Y')})**")
                    try:
                        convs_eng_data = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_conv).eq("data", data_conv_auto.isoformat()).execute().data
                    except:
                        convs_eng_data = []
                    ids_ja_alocados_eng = {c['colaborador_id'] for c in convs_eng_data}
                    nomes_ja_alocados = [dict_colaboradores.get(cid, {}).get('nome', '') for cid in ids_ja_alocados_eng]
                    if nomes_ja_alocados:
                        st.caption("Já escalados por você nesta data: " + ", ".join(nomes_ja_alocados))
                    else:
                        st.caption("Nenhum escalado por você ainda para amanhã.")

                if st.button("CONFIRMAR CONVOCAÇÃO", type="primary", use_container_width=True, key="btn_confirm_conv_adm"):
                    if not equipe_selecionada:
                        st.warning("Selecione pelo menos um colaborador.")
                    else:
                        obra_id = obras_da_unidade[obra_selecionada]
                        sucessos = 0
                        for label_colab in equipe_selecionada:
                            c_id = mapa_colab_adm[label_colab]
                            supabase.table("convocacoes").insert({
                                "obra_id": obra_id,
                                "colaborador_id": c_id,
                                "data": data_conv_auto.isoformat(),
                                "engenheiro": engenheiro_conv,
                                "status": "Presente (Integral)",
                                "valor_extra": 0,
                                "observacao": "Turno: Integral"
                            }).execute()
                            sucessos += 1
                        st.success(f"✅ {sucessos} colaborador(es) convocado(s) para o turno Integral!")
                        st.rerun()
            else:
                st.info("Cadastre obras e colaboradores na aba Configurações.")

        with tab_corrigir_conv:
            st.markdown("### ✏️ Correção Administrativa de Unidade / Obra")
            st.write("Corrija divergências de planejamento ou erros de convocação reatribuindo convocações existentes.")
            
            c_corr1, c_corr2 = st.columns(2)
            with c_corr1:
                data_corr = st.date_input("Data da Convocação para Corrigir:", value=datetime.date.today() + datetime.timedelta(days=1), format="DD/MM/YYYY", key="d_corr")
            
            try:
                convs_existentes = supabase.table("convocacoes").select("*").eq("data", data_corr.isoformat()).execute().data
            except:
                convs_existentes = []

            if not convs_existentes:
                st.info("Nenhuma convocação encontrada nesta data para correção.")
            else:
                mapa_convs_corr = {}
                for item in convs_existentes:
                    colab_inf = dict_colaboradores.get(item['colaborador_id'], {})
                    obra_inf = dict_obras.get(item['obra_id'], {})
                    rotulo = f"{colab_inf.get('nome','N/A')} - Atual: [{obra_inf.get('unidade','N/A')}] {obra_inf.get('nome','N/A')} (Eng: {item.get('engenheiro','')})"
                    mapa_convs_corr[rotulo] = item

                with c_corr2:
                    conv_selecionada_rotulo = st.selectbox("Selecione a Convocação a ser Corrigida:", list(mapa_convs_corr.keys()), key="conv_sel_corr")

                registro_corr = mapa_convs_corr[conv_selecionada_rotulo]
                
                c_dest1, c_dest2, c_dest3 = st.columns(3)
                with c_dest1:
                    unidades_disponiveis = sorted(list(set([o['unidade'] for o in obras])))
                    nova_unidade_corr = st.selectbox("Nova Unidade:", unidades_disponiveis, key="u_dest_corr")
                with c_dest2:
                    obras_nova_u = {o['nome']: o['id'] for o in obras if o['unidade'] == nova_unidade_corr}
                    nova_obra_corr = st.selectbox("Nova Obra / Serviço:", list(obras_nova_u.keys()), key="o_dest_corr")
                with c_dest3:
                    novo_eng_corr = st.selectbox("Engenheiro Responsável:", ENGENHEIROS, index=ENGENHEIROS.index(registro_corr.get('engenheiro', ENGENHEIROS[0])) if registro_corr.get('engenheiro') in ENGENHEIROS else 0, key="eng_dest_corr")

                if st.button("SALVAR CORREÇÃO DE CONVOCAÇÃO", type="primary"):
                    nova_obra_id = obras_nova_u[nova_obra_corr]
                    supabase.table("convocacoes").update({
                        "obra_id": nova_obra_id,
                        "engenheiro": novo_eng_corr
                    }).eq("id", registro_corr['id']).execute()
                    st.success("✅ Convocação corrigida e reatribuída com sucesso!")
                    st.rerun()

    # --- 3. APONTAMENTO ---
    elif menu_escolhido == "✅ APONTAMENTO":
        st.markdown("## ✅ APONTAMENTO DIÁRIO DE CAMPO")
        
        c_ap1, c_ap2, c_ap3, c_ap4 = st.columns(4)
        with c_ap1:
            engenheiro_apont = st.selectbox("Engenheiro:", ENGENHEIROS, key="eng_apont_adm_main")
        with c_ap2:
            data_apont = st.date_input("Data do Apontamento:", value=datetime.date.today(), format="DD/MM/YYYY", key="dt_apont_adm_main")
        
        try:
            convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", data_apont.isoformat()).execute().data
        except:
            convocacoes_hoje = []

        if convocacoes_hoje:
            for conv in convocacoes_hoje:
                conv['dados_obra'] = dict_obras.get(conv['obra_id'], {"unidade": "Desconhecida", "nome": "Desconhecida"})
                
            unidades_convocadas = sorted(list(set([c['dados_obra']['unidade'] for c in convocacoes_hoje])))
            with c_ap3:
                unidade_filtro = st.selectbox("Unidade:", ["TODAS"] + unidades_convocadas, key="filtro_u_apont_adm_main")
            obras_convocadas = sorted(list(set([c['dados_obra']['nome'] for c in convocacoes_hoje if unidade_filtro == "TODAS" or c['dados_obra']['unidade'] == unidade_filtro])))
            with c_ap4:
                obra_filtro = st.selectbox("Obra / Serviço:", ["TODAS"] + obras_convocadas, key="filtro_o_apont_adm_main")
            
            convocacoes_render = [
                c for c in convocacoes_hoje 
                if (unidade_filtro == "TODAS" or c['dados_obra']['unidade'] == unidade_filtro)
                and (obra_filtro == "TODAS" or c['dados_obra']['nome'] == obra_filtro)
            ]
            
            if st.button("✅ MARCAR TODOS COMO PRESENTES", key="btn_all_present_adm_main"):
                for c in convocacoes_render:
                    supabase.table("convocacoes").update({"status": "Presente (Integral)"}).eq("id", c['id']).execute()
                st.success("Todos marcados como Presente (Integral)!")
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
                    
                    st.markdown(f"**{nome}** &nbsp; {cor} `{funcao}` &nbsp; <small style='color:#94A3B8;'>[{conv['dados_obra']['unidade']} - {conv['dados_obra']['nome']}]</small>", unsafe_allow_html=True)
                    status_sel = st.selectbox("Status", opcoes_status, index=idx, key=f"status_adm_{c_id}")
                    if status_sel != status_atual:
                        supabase.table("convocacoes").update({"status": status_sel}).eq("id", c_id).execute()
                        st.rerun()
                    
                    with st.expander("💸 Extra / Obs"):
                        val_atual = float(conv.get("valor_extra") or 0.0)
                        obs_atual = conv.get("observacao") or ""
                        val_extra = st.number_input("Horas Extras / Valor (R$)", value=val_atual, step=10.0, key=f"val_adm_{c_id}")
                        obs = st.text_input("Obs / Justificativa", value=obs_atual, key=f"obs_adm_field_{c_id}")
                        if st.button("Salvar Detalhes", key=f"btn_save_adm_{c_id}"):
                            supabase.table("convocacoes").update({"valor_extra": val_extra, "observacao": obs}).eq("id", c_id).execute()
                            st.success("Salvo!")
        else:
            st.warning("Nenhuma equipe convocada para os filtros selecionados.")

    # --- 4. RELATÓRIOS ---
    elif menu_escolhido == "📊 RELATÓRIOS":
        st.markdown("## 📊 RELATÓRIO DE CUSTOS E FECHAMENTO")
        
        # Filtro de Periodicidade
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            periodicidade = st.selectbox("Periodicidade:", ["Personalizado", "Diário", "Semanal", "Mensal"], key="rel_periodo")
        
        hoje = datetime.date.today()
        if periodicidade == "Diário":
            dt_inicio_def = hoje
            dt_fim_def = hoje
        elif periodicidade == "Semanal":
            dt_inicio_def = hoje - datetime.timedelta(days=7)
            dt_fim_def = hoje
        elif periodicidade == "Mensal":
            dt_inicio_def = hoje.replace(day=1)
            dt_fim_def = hoje
        else:
            dt_inicio_def = hoje
            dt_fim_def = hoje

        with c_p2:
            data_inicio_rel = st.date_input("Início:", value=dt_inicio_def, format="DD/MM/YYYY", key="data_ini_rel")
        with c_p3:
            data_fim_rel = st.date_input("Fim:", value=dt_fim_def, format="DD/MM/YYYY", key="data_fim_rel")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            eng_relatorio = st.selectbox("Engenheiro:", ["TODOS OS ENGENHEIROS"] + ENGENHEIROS, key="eng_rel")
        with col_r2:
            obras_rel_lista = sorted(list(set([o['nome'] for o in obras]))) if obras else []
            obra_relatorio = st.selectbox("Filtro por Obra:", ["TODAS AS OBRAS"] + obras_rel_lista, key="obra_rel")

        query_rel = supabase.table("convocacoes").select("*").gte("data", data_inicio_rel.isoformat()).lte("data", data_fim_rel.isoformat())
        if eng_relatorio != "TODOS OS ENGENHEIROS":
            query_rel = query_rel.eq("engenheiro", eng_relatorio)
        if obra_relatorio != "TODAS AS OBRAS":
            obra_id_filtro = next((o['id'] for o in obras if o['nome'] == obra_relatorio), None)
            if obra_id_filtro:
                query_rel = query_rel.eq("obra_id", obra_id_filtro)
                
        dados_relatorio = query_rel.execute().data if data_inicio_rel <= data_fim_rel else []

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("📄 Gerar PDF", type="primary", use_container_width=True):
                try:
                    if data_inicio_rel > data_fim_rel:
                        st.error("Data inicial maior que a final.")
                    elif not dados_relatorio:
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
                            pdf.cell(0, 10, txt=to_latin(f"APROAR - RELATÓRIO DE CUSTOS | ENG: {eng}"), ln=True, align='C')
                            pdf.set_font("Arial", size=10)
                            pdf.cell(0, 8, txt=to_latin(f"Período: {data_inicio_rel.strftime('%d/%m/%Y')} a {data_fim_rel.strftime('%d/%m/%Y')} ({periodicidade})"), ln=True, align='C')
                            pdf.ln(5)
                            
                            for o_id, apontamentos in obras_eng.items():
                                dados_ob = dict_obras.get(o_id, {"nome": "N/A", "unidade": "N/A"})
                                pdf.set_font("Arial", 'B', 10)
                                pdf.set_fill_color(30, 41, 59)
                                pdf.set_text_color(255, 255, 255)
                                pdf.cell(0, 7, txt=to_latin(f"Unidade: {dados_ob['unidade']} | Obra: {dados_ob['nome']}"), ln=True, fill=True)
                                pdf.set_text_color(0, 0, 0)
                                
                                pdf.set_font("Arial", 'B', 9)
                                pdf.cell(25, 6, to_latin("Data"), border=1, align='C')
                                pdf.cell(65, 6, to_latin("Colaborador"), border=1)
                                pdf.cell(50, 6, to_latin("Função"), border=1)
                                pdf.cell(32, 6, to_latin("Status"), border=1, align='C')
                                pdf.cell(24, 6, to_latin("Diária"), border=1, align='C')
                                pdf.cell(24, 6, to_latin("Extra"), border=1, align='C')
                                pdf.cell(51, 6, to_latin("Obs"), border=1, ln=True)
                                
                                pdf.set_font("Arial", '', 8)
                                for row in apontamentos:
                                    colab = dict_colaboradores.get(row['colaborador_id'], {})
                                    nome = colab.get('nome', 'N/A')
                                    funcao = colab.get('funcao', 'N/A')
                                    status = row.get('status', 'Presente (Integral)')
                                    extra = float(row.get('valor_extra', 0) or 0)
                                    obs = row.get('observacao', '')
                                    diaria_base = calcular_diaria_proporcional(status, colab.get('valor_diaria'))
                                    
                                    pdf.cell(25, 6, to_latin(row.get('data', '')), border=1, align='C')
                                    pdf.cell(65, 6, to_latin(nome[:28]), border=1)
                                    pdf.cell(50, 6, to_latin(funcao[:20]), border=1)
                                    pdf.cell(32, 6, to_latin(status[:14]), border=1, align='C')
                                    pdf.cell(24, 6, to_latin(f"R$ {diaria_base:.2f}"), border=1, align='C')
                                    pdf.cell(24, 6, to_latin(f"R$ {extra:.2f}"), border=1, align='C')
                                    pdf.cell(51, 6, to_latin(obs[:30]), border=1, ln=True)
                                pdf.ln(3)

                        pdf_output = pdf.output(dest='S').encode('latin1')
                        st.download_button(
                            label="📥 Baixar PDF Gerado",
                            data=pdf_output,
                            file_name=f"relatorio_custos_{data_inicio_rel.strftime('%d-%m-%Y')}_a_{data_fim_rel.strftime('%d-%m-%Y')}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

        with col_btn2:
            if st.button("📊 Gerar Excel (Abas por Dia + Cores por Engenheiro)", use_container_width=True):
                try:
                    if data_inicio_rel > data_fim_rel:
                        st.error("Data inicial maior que a final.")
                    elif not dados_relatorio:
                        st.warning("Sem dados no período.")
                    else:
                        lista_excel = []
                        for row in dados_relatorio:
                            ob = dict_obras.get(row['obra_id'], {"nome": "N/A", "unidade": "N/A"})
                            colab = dict_colaboradores.get(row['colaborador_id'], {})
                            status = row.get('status', 'Presente (Integral)')
                            diaria_calc = float(calcular_diaria_proporcional(status, colab.get('valor_diaria')))
                            extra = float(row.get('valor_extra') or 0.0)
                            
                            lista_excel.append({
                                "Data": str(row.get('data')),
                                "Engenheiro": str(row.get('engenheiro', 'N/A')),
                                "Unidade": str(ob['unidade']),
                                "Obra": str(ob['nome']),
                                "Colaborador": str(colab.get('nome', 'N/A')),
                                "Funcao": str(colab.get('funcao', 'N/A')),
                                "Status": str(status),
                                "Diaria": diaria_calc,
                                "Extra": extra,
                                "Observacao": str(row.get('observacao', ''))
                            })
                        
                        df_excel = pd.DataFrame(lista_excel)
                        cores_engenheiros = {
                            "VICTOR": "E0F2FE", "EDUARDO": "DCFCE7", "GUSTAVO": "FEF9C3",
                            "JOEL": "F3E8FF", "NETO": "FFEDD5", "SOARES": "FFE4E6",
                            "GABRIEL": "CCFBF1", "PAULO": "F1F5F9"
                        }
                        
                        wb = openpyxl.Workbook()
                        wb.remove(wb.active)
                        
                        font_titulo = Font(name="Arial", size=11, bold=True, color="FFFFFF")
                        fill_cabecalho = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
                        font_obra_hdr = Font(name="Arial", size=10, bold=True, color="1E293B")
                        fill_obra_hdr = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
                        borda_fina = Border(
                            left=Side(style='thin', color='CBD5E1'), right=Side(style='thin', color='CBD5E1'),
                            top=Side(style='thin', color='CBD5E1'), bottom=Side(style='thin', color='CBD5E1')
                        )
                        
                        for data_str in sorted(df_excel['Data'].unique()):
                            df_dia = df_excel[df_excel['Data'] == data_str]
                            ws = wb.create_sheet(title=str(data_str))
                            
                            current_row = 1
                            ws.cell(row=current_row, column=1, value=f"APONTAMENTO DIÁRIO DE EQUIPES - DATA: {data_str}").font = Font(name="Arial", size=12, bold=True)
                            current_row += 2
                            
                            for unidade_nome in sorted(df_dia['Unidade'].unique()):
                                df_unidade = df_dia[df_dia['Unidade'] == unidade_nome]
                                for obra_nome in sorted(df_unidade['Obra'].unique()):
                                    df_obra = df_unidade[df_unidade['Obra'] == obra_nome]
                                    
                                    ws.cell(row=current_row, column=1, value=f"UNIDADE: {unidade_nome}  |  OBRA: {obra_nome}").font = font_obra_hdr
                                    for c_idx in range(1, 9):
                                        ws.cell(row=current_row, column=c_idx).fill = fill_obra_hdr
                                    current_row += 1
                                    
                                    colunas_tabela = ["Colaborador", "Função", "Engenheiro Resp.", "Status", "Diária (R$)", "Extra (R$)", "Custo Total (R$)", "Observação"]
                                    for c_idx, col_nome in enumerate(colunas_tabela, 1):
                                        cell = ws.cell(row=current_row, column=c_idx, value=col_nome)
                                        cell.font = font_titulo
                                        cell.fill = fill_cabecalho
                                        cell.alignment = Alignment(horizontal="center", vertical="center")
                                    current_row += 1
                                    
                                    inicio_dados_obra = current_row
                                    for _, r in df_obra.iterrows():
                                        eng_resp = r["Engenheiro"]
                                        cor_hex = cores_engenheiros.get(str(eng_resp).upper(), "FFFFFF")
                                        fill_engenheiro = PatternFill(start_color=cor_hex, end_color=cor_hex, fill_type="solid")
                                        
                                        celula_custo_formula = f"=E{current_row}+F{current_row}"
                                        linha_dados = [
                                            r["Colaborador"], r["Funcao"], r["Engenheiro"], r["Status"],
                                            r["Diaria"], r["Extra"], celula_custo_formula, r["Observacao"]
                                        ]
                                        
                                        for c_idx, val in enumerate(linha_dados, 1):
                                            c_cell = ws.cell(row=current_row, column=c_idx, value=val)
                                            c_cell.font = Font(name="Arial", size=9)
                                            c_cell.border = borda_fina
                                            c_cell.fill = fill_engenheiro 
                                            
                                            if c_idx in [5, 6, 7]:
                                                c_cell.number_format = 'R$ #,##0.00'
                                                c_cell.alignment = Alignment(horizontal="right")
                                            elif c_idx in [3, 4]:
                                                c_cell.alignment = Alignment(horizontal="center")
                                        current_row += 1
                                    
                                    fim_dados_obra = current_row - 1
                                    ws.cell(row=current_row, column=5, value=f"TOTAL OBRA {obra_nome}:").font = Font(name="Arial", size=10, bold=True)
                                    ws.cell(row=current_row, column=5).alignment = Alignment(horizontal="right")
                                    
                                    celula_subtotal = ws.cell(row=current_row, column=7, value=f"=SUM(G{inicio_dados_obra}:G{fim_dados_obra})")
                                    celula_subtotal.font = Font(name="Arial", size=10, bold=True)
                                    celula_subtotal.number_format = 'R$ #,##0.00'
                                    celula_subtotal.border = borda_fina
                                    current_row += 2

                            for col in ws.columns:
                                max_len = 0
                                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                                for cell in col:
                                    if cell.row in [1, 2, 3] or (cell.value and str(cell.value).startswith("UNIDADE:")):
                                        continue
                                    if cell.value:
                                        val_str = str(cell.value)
                                        if len(val_str) > max_len:
                                            max_len = len(val_str)
                                ws.column_dimensions[col_letter].width = max(min(max_len + 4, 35), 14)

                        buffer = io.BytesIO()
                        wb.save(buffer)
                        
                        st.download_button(
                            label="📥 Baixar Excel (Abas por Dia + Cores de Engenheiros)",
                            data=buffer.getvalue(),
                            file_name=f"apontamentos_por_dia_{data_inicio_rel.strftime('%d-%m-%Y')}_a_{data_fim_rel.strftime('%d-%m-%Y')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Erro ao gerar Excel: {e}")

    # --- 5. INDICADORES (OPERACIONAIS E ABSENTEÍSMO) ---
    elif menu_escolhido == "📈 INDICADORES":
        st.markdown("## 📈 INDICADORES OPERACIONAIS E ABSENTEÍSMO")
        
        c_ind1, c_ind2, c_ind3 = st.columns(3)
        with c_ind1:
            d_ini_ind = st.date_input("Início:", value=datetime.date.today() - datetime.timedelta(days=30), format="DD/MM/YYYY", key="d_ini_ind")
        with c_ind2:
            d_fim_ind = st.date_input("Fim:", value=datetime.date.today(), format="DD/MM/YYYY", key="d_fim_ind")
        with c_ind3:
            unidades_list = sorted(list(set([o['unidade'] for o in obras]))) if obras else []
            u_filtro_ind = st.selectbox("Filtrar por Unidade:", ["TODAS AS UNIDADES"] + unidades_list, key="u_filtro_ind")

        try:
            q_ind = supabase.table("convocacoes").select("*").gte("data", d_ini_ind.isoformat()).lte("data", d_fim_ind.isoformat())
            dados_ind = q_ind.execute().data
        except:
            dados_ind = []

        if not dados_ind:
            st.warning("Nenhum registro encontrado para o período informado.")
        else:
            registros_ind = []
            for item in dados_ind:
                ob = dict_obras.get(item['obra_id'], {"unidade": "GERAL", "nome": "Desconhecida"})
                if u_filtro_ind != "TODAS AS UNIDADES" and ob['unidade'] != u_filtro_ind:
                    continue
                registros_ind.append({
                    "id": item['id'],
                    "unidade": ob['unidade'],
                    "status": item.get('status', 'Presente (Integral)'),
                    "engenheiro": item.get('engenheiro', 'N/A')
                })

            df_ind = pd.DataFrame(registros_ind)
            
            if df_ind.empty:
                st.info("Nenhum registro encontrado para a unidade selecionada.")
            else:
                total_conv = len(df_ind)
                total_faltas = len(df_ind[df_ind['status'] == 'Falta'])
                total_atestados = len(df_ind[df_ind['status'] == 'Atestado'])
                total_ausencias = total_faltas + total_atestados
                taxa_absenteismo = (total_ausencias / total_conv * 100) if total_conv > 0 else 0.0

                m_ind1, m_ind2, m_ind3, m_ind4 = st.columns(4)
                m_ind1.metric("CONVOCAÇÕES TOTAL", total_conv)
                m_ind2.metric("FALTAS", total_faltas)
                m_ind3.metric("ATESTADOS", total_atestados)
                m_ind4.metric("TAXA DE ABSENTEÍSMO", f"{taxa_absenteismo:.1f}%")

                st.markdown("---")
                st.markdown("### 🏢 DETALHAMENTO E CONSOLIDAÇÃO DE FALTAS POR UNIDADE")
                
                resumo_unidades = []
                for und in df_ind['unidade'].unique():
                    df_u = df_ind[df_ind['unidade'] == und]
                    t_u = len(df_u)
                    f_u = len(df_u[df_u['status'] == 'Falta'])
                    a_u = len(df_u[df_u['status'] == 'Atestado'])
                    aus_u = f_u + a_u
                    taxa_u = (aus_u / t_u * 100) if t_u > 0 else 0.0
                    resumo_unidades.append({
                        "Unidade": und,
                        "Convocações": t_u,
                        "Faltas": f_u,
                        "Atestados": a_u,
                        "Total Ausências": aus_u,
                        "Taxa Absenteísmo (%)": round(taxa_u, 1)
                    })

                df_resumo_u = pd.DataFrame(resumo_unidades).sort_values(by="Taxa Absenteísmo (%)", ascending=False)
                st.dataframe(df_resumo_u, use_container_width=True, hide_index=True)

    # --- 6. DISPONIBILIDADE ---
    elif menu_escolhido == "👥 DISPONIBILIDADE":
        render_aba_disponibilidade("admin")

    # --- 7. CONFIGURAÇÕES E SINCRONIZAÇÃO TRELLO ---
    elif menu_escolhido == "⚙️ CONFIGURAÇÕES":
        st.markdown("## ⚙️ CONFIGURAÇÕES E GERENCIAMENTO")
        
        # Sincronização Dinâmica Trello (Mês Vigente ou Dropdown Manual)
        with st.container(border=True):
            st.markdown("### 🔄 Sincronização com o Trello")
            st.write("Sincronize automaticamente as obras da lista do mês vigente ou selecione manualmente uma lista específica do quadro.")
            
            lists_trello, _ = obter_listas_trello()
            
            c_tr1, c_tr2 = st.columns(2)
            with c_tr1:
                if st.button("🚀 SINCRONIZAR MÊS VIGENTE (AUTOMÁTICO)", type="primary"):
                    with st.spinner("Sincronizando mês vigente..."):
                        sucesso, me = executar_sincronizacao_trello()
                        if sucesso: st.success(me); st.rerun()
                        else: st.error(me)
            
            with c_tr2:
                if lists_trello:
                    mapa_listas = {l['name']: l['id'] for l in lists_trello if not l.get('closed', False)}
                    lista_manual_sel = st.selectbox("Ou selecione uma Lista do Trello:", list(mapa_listas.keys()), key="sel_trello_manual")
                    if st.button("🔄 SINCRONIZAR LISTA SELECIONADA"):
                        id_sel = mapa_listas[lista_manual_sel]
                        with st.spinner(f"Sincronizando {lista_manual_sel}..."):
                            sucesso, me = executar_sincronizacao_trello(id_lista_target=id_sel)
                            if sucesso: st.success(me); st.rerun()
                            else: st.error(me)
                else:
                    st.caption("Não foi possível obter o menu suspenso de listas do Trello.")

        st.markdown("---")
        tab_cad_obra, tab_cad_colab, tab_limpeza = st.tabs(["🏗️ Obras", "👷 Colaboradores", "🗑️ Limpeza de Dados"])
        
        with tab_cad_obra:
            st.markdown("### Cadastrar Nova Obra")
            with st.form("form_cad_obra"):
                nome_obra = st.text_input("Nome da Obra (Ex: 1863, 1383...):")
                unidade_obra = st.text_input("Unidade (Ex: CENTRO, MUSEU, FIEC...):")
                submit_obra = st.form_submit_button("Cadastrar Obra")
                if submit_obra:
                    if nome_obra and unidade_obra:
                        supabase.table("obras").insert({"nome": nome_obra, "unidade": unidade_obra.upper()}).execute()
                        st.cache_data.clear()
                        st.success("Obra cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Preencha todos os campos.")

        with tab_cad_colab:
            st.markdown("### Cadastrar Novo Colaborador")
            with st.form("form_cad_colab"):
                nome_colab = st.text_input("Nome Completo:")
                funcao_colab = st.text_input("Função / Cargo:")
                diaria_colab = st.number_input("Valor Diária Base (R$):", value=240.0, step=10.0)
                submit_colab = st.form_submit_button("Cadastrar Colaborador")
                if submit_colab:
                    if nome_colab and funcao_colab:
                        supabase.table("colaboradores").insert({
                            "nome": nome_colab, 
                            "funcao": limpar_funcao(funcao_colab), 
                            "valor_diaria": diaria_colab
                        }).execute()
                        st.cache_data.clear()
                        st.success("Colaborador cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Preencha todos os campos.")

        with tab_limpeza:
            st.markdown("### 🗑️ Limpeza e Manutenção de Registros")
            st.write("Use esta seção para remover registros incorretos ou limpar dados antigos de convocações/apontamentos.")
            
            data_limpeza = st.date_input("Selecionar data para limpeza de convocações:", value=datetime.date.today(), format="DD/MM/YYYY")
            if st.button("🗑️ EXCLUIR CONVOCAÇÕES DESTA DATA", type="primary"):
                try:
                    supabase.table("convocacoes").delete().eq("data", data_limpeza.isoformat()).execute()
                    st.success(f"Todas as convocações do dia {data_limpeza.strftime('%d/%m/%Y')} foram removidas com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao limpar dados: {e}")
