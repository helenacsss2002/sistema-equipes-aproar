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

# CSS Moderno com Tema Escuro, Sidebar Menor e Azul APROAR
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
    /* Sidebar Escura, Moderna e Mais Estreita */
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
    /* Inputs e Selects Limpos no Tema Escuro */
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
    /* Botões Principais no Azul APROAR */
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
    /* Containers com Efeito de Elevação Suave */
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

# --- MAPA DE MESES PARA INTEGRAÇÃO ---
MESES_PT = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO",
    7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
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

# --- SINCRONIZAÇÃO COM TRELLO (DINÂMICA: MÊS ATUAL / LISTA ESPECÍFICA / EM EXECUÇÃO) ---
def executar_sincronizacao_trello(termo_busca=None):
    url_trello = "https://trello.com/b/TX8hGvmI.json"
    try:
        resp = requests.get(url_trello, timeout=10)
        if resp.status_code != 200:
            return False, "Erro ao acessar o quadro público do Trello."
        
        data = resp.json()
        lists = data.get('lists', [])
        cards = data.get('cards', [])
        
        id_lista = None
        mes_atual_nome = MESES_PT[datetime.date.today().month]
        termos_testar = [termo_busca] if termo_busca else [f"MEDICOES {mes_atual_nome}", "EM EXECUCAO", "EXECUCAO"]
        
        for t in termos_testar:
            if not t: continue
            t_norm = normalizar(t)
            for lst in lists:
                nome_lista = normalizar(lst.get('name', ''))
                if t_norm in nome_lista:
                    id_lista = lst.get('id')
                    break
            if id_lista: break
        
        if not id_lista:
            return False, "Nenhuma lista correspondente encontrada no quadro do Trello."
        
        cards_alvo = [c for c in cards if c.get('idList') == id_lista and not c.get('closed', False)]
        
        obras_atuais = buscar_obras()
        nomes_cadastrados = {normalizar(o['nome']) for o in obras_atuais}
        
        novas_inseridas = 0
        for card in cards_alvo:
            nome_card = card.get('name', '').strip()
            if not nome_card:
                continue
            
            unidade_card = identificar_unidade(nome_card)
            
            if normalizar(nome_card) not in nomes_cadastrados:
                supabase.table("obras").insert({
                    "unidade": unidade_card,
                    "nome": nome_card
                }).execute()
                novas_inseridas += 1
                nomes_cadastrados.add(normalizar(nome_card))
                
        st.cache_data.clear()
        return True, f"Sincronização realizada com sucesso! {novas_inseridas} nova(s) obra(s) adicionadas à base."
    except Exception as e:
        return False, f"Erro na conexão com o Trello: {e}"

# --- BUSCA DE DADOS COM CACHE (OTIMIZAÇÃO DE VELOCIDADE) ---
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
            
            if st.button("✅ MARCAR TODOS COMO PRESENTES"):
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
            st.warning("Nenhuma equipe convocada para hoje sob sua responsabilidade.")

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
            
            # BUSCA NOMINAL E SELEÇÃO DE COLABORADOR NO CAMPO
            st.markdown("#### Seleção Nominal de Colaboradores")
            lista_nomes_colabs = [c['nome'] for c in colaboradores]
            nome_busca_campo = st.selectbox("Buscar Colaborador pelo Nome:", options=[""] + lista_nomes_colabs, key="busca_nom_campo")
            
            funcao_auto_campo = ""
            if nome_busca_campo:
                obj_colab = next((c for c in colaboradores if c['nome'] == nome_busca_campo), None)
                if obj_colab:
                    funcao_auto_campo = obj_colab['funcao']
            st.text_input("Função do Colaborador:", value=funcao_auto_campo, disabled=True, key="func_auto_c")

            funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
            frente_selecionada = st.selectbox("Filtrar por Função (opcional para lista):", ["TODAS"] + funcoes_disponiveis, key="f_c_sel")

            colaboradores_filtrados = colaboradores if frente_selecionada == "TODAS" else [c for c in colaboradores if c['funcao'] == frente_selecionada]
            opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}
            
            padrao_sel = [nome_busca_campo] if nome_busca_campo and nome_busca_campo in opcoes_colaboradores else []
            equipe_selecionada = st.multiselect("Confirmar Selecionados:", list(opcoes_colaboradores.keys()), default=padrao_sel, key="eq_c_sel")

            with st.container(border=True):
                st.markdown(f"#### 👁️ Panorama de {engenheiro_conv} ({data_conv.strftime('%d/%m/%Y')})")
                try:
                    convs_eng_data = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_conv).eq("data", data_conv.isoformat()).execute().data
                except:
                    convs_eng_data = []
                
                ids_ja_alocados_eng = {c['colaborador_id'] for c in convs_eng_data}
                nomes_ja_alocados = [dict_colaboradores.get(cid, {}).get('nome', '') for cid in ids_ja_alocados_eng]
                if nomes_ja_alocados:
                    st.caption("Já escalados por você hoje: " + ", ".join(nomes_ja_alocados))
                else:
                    st.caption("Nenhum escalado por você nesta data.")

            if st.button("CONFIRMAR CONVOCAÇÃO", type="primary", use_container_width=True):
                if not equipe_selecionada:
                    st.warning("Selecione pelo menos um colaborador.")
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
    # PAINEL ADMINISTRATIVO (TEMA ESCURO)
    # ==========================================
    
    if "menu_ativo" not in st.session_state:
        st.session_state.menu_ativo = "🎛️ DASHBOARD"

    # --- MENU LATERAL EM MAIÚSCULAS ---
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

    # --- CONTEÚDO PRINCIPAL ---

    # 1. DASHBOARD
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
                            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                            with c1:
                                st.markdown(f"**{row['colab_nome']}** &nbsp; `{row['colab_funcao']}` &nbsp; <small style='color:#94A3B8;'>({row['data_item']})</small>", unsafe_allow_html=True)
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
                            with c4:
                                st.write("")
                                if st.button("🗑️", key=f"del_c_{c_id}", help="Excluir Convocação"):
                                    supabase.table("convocacoes").delete().eq("id", c_id).execute()
                                    st.toast("Convocação excluída com sucesso!")
                                    st.rerun()
                            st.divider()

    # 2. CONVOCAÇÃO (MELHORIAS: BUSCA NOMINAL + CONVOLUÇÃO DE UNIDADES/OBRAS + REMOÇÃO RÁPIDA)
    elif menu_escolhido == "📋 CONVOCAÇÃO":
        st.markdown("## 📋 NOVA CONVOCAÇÃO DE EQUIPE")
        if obras and colaboradores:
            col_eng, col_data_conv, col_data_exec = st.columns(3)
            with col_eng:
                engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv")
            with col_data_conv:
                dt_hoje = datetime.date.today()
                data_solic = st.date_input("Data do Pedido:", value=dt_hoje, format="DD/MM/YYYY", key="dt_solic_c")
            with col_data_exec:
                amanha = dt_hoje + datetime.timedelta(days=1)
                data_conv = st.date_input("Data do Serviço:", value=amanha, format="DD/MM/YYYY", key="dt_serv_c")

            antecedencia_dias = (data_conv - data_solic).days
            if antecedencia_dias < 0:
                st.warning("⚠️ Atenção: A data do serviço é anterior à data da convocação.")
            else:
                st.info(f"⏱️ Antecedência de convocação: **{antecedencia_dias} dia(s)**")

            unidades_unicas = sorted(list(set([o['unidade'] for o in obras])))
            col_u, col_o = st.columns(2)
            with col_u:
                unidade_selecionada = st.selectbox("Selecione a Unidade:", unidades_unicas, key="u_sel_adm_c")
            
            obras_da_unidade = {o['nome']: o['id'] for o in obras if o['unidade'] == unidade_selecionada}
            with col_o:
                obra_selecionada = st.selectbox("Selecione a Obra / Serviço:", list(obras_da_unidade.keys()), key="o_sel_adm_c")

            turno_conv_adm = st.selectbox("Turno / Período:", ["Integral", "Manhã", "Tarde"], key="turno_conv_adm")

            st.markdown("---")
            st.markdown("### 👤 Seleção do Colaborador")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                lista_nomes_colabs = [c['nome'] for c in colaboradores]
                nome_busca_adm = st.selectbox("Buscar Colaborador pelo Nome:", options=[""] + lista_nomes_colabs, key="busca_nom_adm")
            
            funcao_auto_adm = ""
            if nome_busca_adm:
                obj_c = next((c for c in colaboradores if c['nome'] == nome_busca_adm), None)
                if obj_c:
                    funcao_auto_adm = obj_c['funcao']
            with col_b2:
                st.text_input("Função (Automático):", value=funcao_auto_adm, disabled=True, key="func_auto_adm")

            funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
            frente_selecionada = st.selectbox("Filtro Adicional por Função:", ["TODAS"] + funcoes_disponiveis, key="filt_func_adm")

            colaboradores_filtrados = colaboradores if frente_selecionada == "TODAS" else [c for c in colaboradores if c['funcao'] == frente_selecionada]
            opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}
            
            padrao_mult = [nome_busca_adm] if nome_busca_adm and nome_busca_adm in opcoes_colaboradores else []
            equipe_selecionada = st.multiselect("Colaboradores Selecionados para a Lista:", list(opcoes_colaboradores.keys()), default=padrao_mult, key="msel_eq_adm")

            with st.container(border=True):
                st.markdown(f"**Panorama de {engenheiro_conv} ({data_conv.strftime('%d/%m/%Y')})**")
                try:
                    convs_eng_data = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_conv).eq("data", data_conv.isoformat()).execute().data
                except:
                    convs_eng_data = []
                ids_ja_alocados_eng = {c['colaborador_id'] for c in convs_eng_data}
                nomes_ja_alocados = [dict_colaboradores.get(cid, {}).get('nome', '') for cid in ids_ja_alocados_eng]
                if nomes_ja_alocados:
                    st.caption("Já escalados por você nesta data: " + ", ".join(nomes_ja_alocados))
                else:
                    st.caption("Nenhum escalado por você ainda nesta data.")

            if st.button("CONFIRMAR CONVOCAÇÃO", type="primary", use_container_width=True):
                if not equipe_selecionada:
                    st.warning("Selecione pelo menos um colaborador.")
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
                    st.success(f"✅ {sucessos} colaborador(es) convocado(s) para a obra {obra_selecionada}!")
                    st.rerun()
        else:
            st.info("Cadastre obras e colaboradores na aba Configurações.")

    # 3. APONTAMENTO
    elif menu_escolhido == "✅ APONTAMENTO":
        st.markdown("## ✅ APONTAMENTO DIÁRIO DE CAMPO")
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
            
            if st.button("✅ MARCAR TODOS COMO PRESENTES", key="btn_all_present_adm"):
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

    # 4. RELATÓRIOS (COM FILTROS EXPANDIDOS POR UNIDADE E OBRA)
    elif menu_escolhido == "📊 RELATÓRIOS":
        st.markdown("## 📊 RELATÓRIO DE CUSTOS E FECHAMENTO")
        col_rel_eng, col_rel_unid = st.columns(2)
        with col_rel_eng:
            eng_relatorio = st.selectbox("Engenheiro:", ["TODOS OS ENGENHEIROS"] + ENGENHEIROS, key="eng_rel")
        with col_rel_unid:
            unidades_cad = sorted(list(set([o['unidade'] for o in obras]))) if obras else []
            unidade_relatorio = st.selectbox("Unidade:", ["TODAS AS UNIDADES"] + unidades_cad, key="unid_rel")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_inicio_rel = st.date_input("Início:", value=datetime.date.today() - datetime.timedelta(days=7), format="DD/MM/YYYY", key="data_ini")
        with col_d2:
            data_fim_rel = st.date_input("Fim:", value=datetime.date.today(), format="DD/MM/YYYY", key="data_fim")
        
        query_rel = supabase.table("convocacoes").select("*").gte("data", data_inicio_rel.isoformat()).lte("data", data_fim_rel.isoformat())
        if eng_relatorio != "TODOS OS ENGENHEIROS":
            query_rel = query_rel.eq("engenheiro", eng_relatorio)
            
        dados_relatorio = query_rel.execute().data if data_inicio_rel <= data_fim_rel else []

        # Filtro de Unidade em Memória
        if unidade_relatorio != "TODAS AS UNIDADES" and dados_relatorio:
            ids_obras_unid = {o['id'] for o in obras if o['unidade'] == unidade_relatorio}
            dados_relatorio = [r for r in dados_relatorio if r['obra_id'] in ids_obras_unid]

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
                            pdf.cell(0, 8, txt=to_latin(f"Período: {data_inicio_rel.strftime('%d/%m/%Y')} a {data_fim_rel.strftime('%d/%m/%Y')}"), ln=True, align='C')
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
                            "VICTOR": "E0F2FE",
                            "EDUARDO": "DCFCE7",
                            "GUSTAVO": "FEF9C3",
                            "JOEL": "F3E8FF",
                            "NETO": "FFEDD5",
                            "SOARES": "FFE4E6",
                            "GABRIEL": "CCFBF1",
                            "PAULO": "F1F5F9"
                        }
                        
                        wb = openpyxl.Workbook()
                        wb.remove(wb.active)
                        
                        font_titulo = Font(name="Arial", size=11, bold=True, color="FFFFFF")
                        fill_cabecalho = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
                        font_obra_hdr = Font(name="Arial", size=10, bold=True, color="1E293B")
                        fill_obra_hdr = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
                        borda_fina = Border(
                            left=Side(style='thin', color='CBD5E1'),
                            right=Side(style='thin', color='CBD5E1'),
                            top=Side(style='thin', color='CBD5E1'),
                            bottom=Side(style='thin', color='CBD5E1')
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
                    st.error(f"Erro ao gerar Excel por dias: {e}")

    # 5. INDICADORES & ABSENTEÍSMO (IMPLEMENTAÇÃO COMPLETA)
    elif menu_escolhido == "📈 INDICADORES":
        st.markdown("## 📈 INDICADORES OPERACIONAIS E ABSENTEÍSMO")
        
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            data_ini_ind = st.date_input("Início do Período:", value=datetime.date.today() - datetime.timedelta(days=30), format="DD/MM/YYYY", key="ind_ini")
        with col_i2:
            data_fim_ind = st.date_input("Fim do Período:", value=datetime.date.today(), format="DD/MM/YYYY", key="ind_fim")
        with col_i3:
            unidades_ind_disp = sorted(list(set([o['unidade'] for o in obras]))) if obras else []
            unidade_ind = st.selectbox("Filtrar Unidade:", ["TODAS"] + unidades_ind_disp, key="ind_u")

        try:
            query_ind = supabase.table("convocacoes").select("*").gte("data", data_ini_ind.isoformat()).lte("data", data_fim_ind.isoformat())
            convs_ind = query_ind.execute().data
        except:
            convs_ind = []

        if not convs_ind:
            st.info("Nenhum dado encontrado para o período selecionado.")
        else:
            df_ind = pd.DataFrame(convs_ind)
            df_ind['unidade'] = df_ind['obra_id'].apply(lambda oid: dict_obras.get(oid, {}).get('unidade', 'GERAL'))
            df_ind['obra_nome'] = df_ind['obra_id'].apply(lambda oid: dict_obras.get(oid, {}).get('nome', 'N/A'))
            df_ind['colab_nome'] = df_ind['colaborador_id'].apply(lambda cid: dict_colaboradores.get(cid, {}).get('nome', 'N/A'))
            df_ind['colab_funcao'] = df_ind['colaborador_id'].apply(lambda cid: dict_colaboradores.get(cid, {}).get('funcao', 'N/A'))

            if unidade_ind != "TODAS":
                df_ind = df_ind[df_ind['unidade'] == unidade_ind]

            if df_ind.empty:
                st.warning("Nenhum registro para esta unidade no período.")
            else:
                total_registros = len(df_ind)
                total_faltas = len(df_ind[df_ind['status'] == 'Falta'])
                total_atestados = len(df_ind[df_ind['status'] == 'Atestado'])
                total_presencas = len(df_ind[df_ind['status'].str.contains('Presente', na=False) | (df_ind['status'] == 'Extra')])
                taxa_absenteismo = ((total_faltas + total_atestados) / total_registros * 100) if total_registros > 0 else 0

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Total Convocações", total_registros)
                m2.metric("Presenças", total_presencas)
                m3.metric("Faltas", total_faltas)
                m4.metric("Atestados", total_atestados)
                m5.metric("Taxa Absenteísmo", f"{taxa_absenteismo:.1f}%")

                st.markdown("---")
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.markdown("### 🚨 Ranking Nominal de Faltas & Ocorrências")
                    df_ausencias = df_ind[df_ind['status'].isin(['Falta', 'Atestado', 'Saída Antecipada'])]
                    if df_ausencias.empty:
                        st.success("Nenhuma falta ou atestado registrado no período!")
                    else:
                        ranking_faltas = df_ausencias.groupby(['colab_nome', 'colab_funcao', 'unidade', 'status']).size().reset_index(name='Qtd_Faltas')
                        ranking_faltas = ranking_faltas.sort_values(by='Qtd_Faltas', ascending=False)
                        
                        st.dataframe(
                            ranking_faltas.rename(columns={
                                'colab_nome': 'Colaborador',
                                'colab_funcao': 'Função',
                                'unidade': 'Unidade',
                                'status': 'Tipo',
                                'Qtd_Faltas': 'Qtd'
                            }),
                            use_container_width=True,
                            hide_index=True
                        )

                with col_chart2:
                    st.markdown("### 📍 Detalhamento das Ocorrências")
                    if df_ausencias.empty:
                        st.info("Sem ocorrências para exibir.")
                    else:
                        for _, row_aus in df_ausencias.iterrows():
                            cor_tag = "🔴" if row_aus['status'] == 'Falta' else ("🟡" if row_aus['status'] == 'Atestado' else "🟧")
                            st.markdown(
                                f"{cor_tag} **{row_aus['colab_nome']}** (`{row_aus['colab_funcao']}`) — "
                                f"**{row_aus['status']}** em `{row_aus['data']}` <br>"
                                f"<small style='color:#94A3B8;'>Unidade: {row_aus['unidade']} | Obra: {row_aus['obra_nome']}</small>",
                                unsafe_allow_html=True
                            )
                            st.divider()

    # 6. DISPONIBILIDADE
    elif menu_escolhido == "👥 DISPONIBILIDADE":
        render_aba_disponibilidade("admin")

    # 7. CONFIGURAÇÕES (COM MULTI-OPÇÃO DO TRELLO E GERENCIAMENTO DE DADOS)
    elif menu_escolhido == "⚙️ CONFIGURAÇÕES":
        st.markdown("## ⚙️ CONFIGURAÇÕES E GERENCIAMENTO")
        
        # Seção de Sincronização Trello
        with st.container(border=True):
            st.markdown("### 🔄 Sincronização com o Trello")
            st.write("Sincronize automaticamente os cartões do quadro do Trello para cadastrar novas obras.")
            
            mes_atual_str = MESES_PT[datetime.date.today().month]
            col_tr1, col_tr2 = st.columns([2, 1])
            with col_tr1:
                opcao_trello = st.radio(
                    "Origem / Nome da Lista do Trello:",
                    [f"Automático (Lista 'MEDIÇÕES {mes_atual_str}')", "Em Execução ('EM EXECUÇÃO')", "Nome Personalizado"],
                    key="radio_trello_opt"
                )
            
            termo_final_trello = None
            if "Automático" in opcao_trello:
                termo_final_trello = f"MEDICOES {mes_atual_str}"
            elif "Em Execução" in opcao_trello:
                termo_final_trello = "EM EXECUCAO"
            else:
                termo_final_trello = st.text_input("Digite o nome exato da lista do Trello:", value=f"MEDIÇÕES {mes_atual_str}")

            if st.button("SINCRONIZAR OBRAS DO TRELLO AGORA"):
                with st.spinner(f"Buscando obras no Trello (Lista: '{termo_final_trello}')..."):
                    sucesso, mensagem = executar_sincronizacao_trello(termo_busca=termo_final_trello)
                    if sucesso:
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)

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
