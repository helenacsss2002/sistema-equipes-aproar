import streamlit as st
from supabase import create_client, Client
import datetime

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="App Obras", page_icon="👷", layout="centered")

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=60) # Atualiza a cada 60s
def buscar_obras():
    res = supabase.table("obras").select("*").execute()
    return res.data

@st.cache_data(ttl=60)
def buscar_colaboradores():
    res = supabase.table("colaboradores").select("*").eq("ativo", True).execute()
    return res.data

obras = buscar_obras()
colaboradores = buscar_colaboradores()

# --- INTERFACE: TELA DE CONVOCAÇÃO ---
st.title("👷 Convocação Diária")

# 1. Identificação do Engenheiro e Obra
st.markdown("### 📋 Informações da Demanda")
engenheiro = st.text_input("Nome do Engenheiro responsável:")

# Formatar lista de obras para o selectbox
opcoes_obras = {f"{o['unidade']} - {o['nome']}": o['id'] for o in obras}
obra_selecionada = st.selectbox("Selecione a Unidade e Obra:", list(opcoes_obras.keys()))

# 2. Seleção de Frente de Trabalho
st.markdown("### 🛠️ Montar Equipe")
# Extrair funções únicas dos colaboradores
funcoes = list(set([c['funcao'] for c in colaboradores]))
frente_selecionada = st.selectbox("Frente de Trabalho:", funcoes)

# Filtrar colaboradores pela função escolhida
colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}

equipe_selecionada = st.multiselect(
    "Selecione os colaboradores para esta frente:", 
    list(opcoes_colaboradores.keys()),
    help="Colaboradores já convocados em outra obra hoje não aparecerão aqui (em breve implementaremos a trava visual)."
)

# 3. Botão de Salvar
if st.button("Confirmar Convocação", type="primary", use_container_width=True):
    if not engenheiro:
        st.warning("⚠️ Por favor, preencha o nome do engenheiro.")
    elif not equipe_selecionada:
        st.warning("⚠️ Selecione pelo menos um colaborador.")
    else:
        obra_id = opcoes_obras[obra_selecionada]
        hoje = datetime.date.today().isoformat()
        
        # Prepara os dados para salvar no Supabase
        dados_insercao = []
        for nome in equipe_selecionada:
            colab_id = opcoes_colaboradores[nome]
            dados_insercao.append({
                "obra_id": obra_id,
                "colaborador_id": colab_id,
                "data": hoje,
                "engenheiro": engenheiro,
                "status": "Presente" # Status padrão
            })
        
        try:
            supabase.table("convocacoes").insert(dados_insercao).execute()
            st.success("✅ Equipe convocada com sucesso!")
            st.balloons()
        except Exception as e:
            # Captura o erro da trava de segurança (colaborador já convocado)
            if "duplicate key value" in str(e):
                st.error("❌ Erro: Um ou mais colaboradores selecionados já foram convocados para hoje em outra obra.")
            else:
                st.error(f"❌ Ocorreu um erro: {e}")
