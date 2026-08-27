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

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"Erro de credenciais: {e}")
    st.stop()

# --- BUSCA DE DADOS (COM CAPTURA DE ERRO) ---
def buscar_obras():
    try:
        res = supabase.table("obras").select("*").execute()
        return res.data
    except Exception as e:
        st.error(f"Erro real ao ler Obras: {e}")
        return []

def buscar_colaboradores():
    try:
        res = supabase.table("colaboradores").select("*").eq("ativo", True).execute()
        return res.data
    except Exception as e:
        st.error(f"Erro real ao ler Colaboradores: {e}")
        return []

obras = buscar_obras()
colaboradores = buscar_colaboradores()

# --- INTERFACE: TELA DE CONVOCAÇÃO ---
st.title("👷 Convocação Diária")

# Só renderiza a tela se conseguir puxar os dados
if obras and colaboradores:
    st.markdown("### 📋 Informações da Demanda")
    engenheiro = st.text_input("Nome do Engenheiro responsável:")

    # Formatar lista de obras
    opcoes_obras = {f"{o['unidade']} - {o['nome']}": o['id'] for o in obras}
    obra_selecionada = st.selectbox("Selecione a Unidade e Obra:", list(opcoes_obras.keys()))

    st.markdown("### 🛠️ Montar Equipe")
    funcoes = list(set([c['funcao'] for c in colaboradores]))
    frente_selecionada = st.selectbox("Frente de Trabalho:", funcoes)

    colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
    opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}

    equipe_selecionada = st.multiselect(
        "Selecione os colaboradores para esta frente:", 
        list(opcoes_colaboradores.keys())
    )

    if st.button("Confirmar Convocação", type="primary", use_container_width=True):
        if not engenheiro:
            st.warning("⚠️ Por favor, preencha o nome do engenheiro.")
        elif not equipe_selecionada:
            st.warning("⚠️ Selecione pelo menos um colaborador.")
        else:
            obra_id = opcoes_obras[obra_selecionada]
            hoje = datetime.date.today().isoformat()
            
            dados_insercao = []
            for nome in equipe_selecionada:
                colab_id = opcoes_colaboradores[nome]
                dados_insercao.append({
                    "obra_id": obra_id,
                    "colaborador_id": colab_id,
                    "data": hoje,
                    "engenheiro": engenheiro,
                    "status": "Presente"
                })
            
            try:
                supabase.table("convocacoes").insert(dados_insercao).execute()
                st.success("✅ Equipe convocada com sucesso!")
                st.balloons()
            except Exception as e:
                if "duplicate key value" in str(e):
                    st.error("❌ Erro: Colaborador já convocado para hoje.")
                else:
                    st.error(f"❌ Ocorreu um erro: {e}")
else:
    st.info("Aguardando carregamento do banco de dados ou corrigindo erros de conexão...")
