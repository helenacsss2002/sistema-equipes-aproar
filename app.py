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

# --- BUSCA DE DADOS ---
def buscar_obras():
    try:
        return supabase.table("obras").select("*").execute().data
    except Exception as e:
        st.error(f"Erro ao ler Obras: {e}")
        return []

def buscar_colaboradores():
    try:
        return supabase.table("colaboradores").select("*").eq("ativo", True).execute().data
    except Exception as e:
        st.error(f"Erro ao ler Colaboradores: {e}")
        return []

obras = buscar_obras()
colaboradores = buscar_colaboradores()

# Lista fixa de engenheiros
ENGENHEIROS = ["EDUARDO", "GABRIEL", "GUSTAVO", "JOEL", "NETO", "PAULO", "SOARES", "VICTOR"]

st.title("👷 Gestão de Equipes")

# Só renderiza as telas se conseguir puxar os dados
if obras and colaboradores:
    
    # Criando as Abas de navegação
    tab_convocacao, tab_apontamento = st.tabs(["📋 Convocação", "✅ Apontamentos"])
    
    hoje = datetime.date.today().isoformat()
    
    # ==========================================
    # ABA 1: CONVOCAÇÃO
    # ==========================================
    with tab_convocacao:
        st.markdown("### Informações da Demanda")
        # Substituímos o texto livre por uma caixa de seleção
        engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv")

        opcoes_obras = {f"{o['unidade']} - {o['nome']}": o['id'] for o in obras}
        obra_selecionada = st.selectbox("Selecione a Unidade e Obra:", list(opcoes_obras.keys()))

        st.markdown("### Montar Equipe")
        funcoes = list(set([c['funcao'] for c in colaboradores]))
        frente_selecionada = st.selectbox("Frente de Trabalho:", funcoes)

        colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
        opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}

        equipe_selecionada = st.multiselect(
            "Selecione os colaboradores para esta frente:", 
            list(opcoes_colaboradores.keys())
        )

        if st.button("Confirmar Convocação", type="primary", use_container_width=True):
            if not equipe_selecionada:
                st.warning("⚠️ Selecione pelo menos um colaborador.")
            else:
                obra_id = opcoes_obras[obra_selecionada]
                
                dados_insercao = []
                for nome in equipe_selecionada:
                    colab_id = opcoes_colaboradores[nome]
                    dados_insercao.append({
                        "obra_id": obra_id,
                        "colaborador_id": colab_id,
                        "data": hoje,
                        "engenheiro": engenheiro_conv,
                        "status": "Presente" # Status padrão na convocação
                    })
                
                try:
                    supabase.table("convocacoes").insert(dados_insercao).execute()
                    st.success("✅ Equipe convocada com sucesso!")
                except Exception as e:
                    if "duplicate key value" in str(e):
                        st.error("❌ Erro: Colaborador já convocado para hoje em outra obra.")
                    else:
                        st.error(f"❌ Ocorreu um erro: {e}")

    # ==========================================
    # ABA 2: APONTAMENTOS (FIM DO IMPROVISO NO WHATSAPP)
    # ==========================================
    with tab_apontamento:
        st.markdown("### Apontamento Diário")
        engenheiro_apont = st.selectbox("Selecione seu nome para ver sua equipe de hoje:", ENGENHEIROS, key="eng_apont")
        
        # Busca apenas as convocações de HOJE feitas por este ENGENHEIRO
        try:
            res_convs = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", hoje).execute()
            convocacoes_hoje = res_convs.data
        except Exception as e:
            st.error("Erro ao buscar equipe de hoje.")
            convocacoes_hoje = []

        if convocacoes_hoje:
            st.info("Todos estão marcados como 'Presente' por padrão. Altere apenas as exceções.")
            
            # Dicionário para facilitar a busca do nome do colaborador pelo ID
            dict_colaboradores = {c['id']: c['nome'] for c in colaboradores}
            
            with st.form("form_apontamentos"):
                novos_status = {}
                opcoes_status = ["Presente", "Falta", "Atestado", "Extra"]
                
                for conv in convocacoes_hoje:
                    nome = dict_colaboradores.get(conv['colaborador_id'], "Desconhecido")
                    status_atual = conv.get("status", "Presente")
                    
                    # Garante que o índice selecionado bata com o banco de dados
                    idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                    
                    st.markdown(f"**{nome}**")
                    # Botões horizontais fáceis de clicar no celular
                    selecao = st.radio(
                        "Status", 
                        opcoes_status, 
                        index=idx, 
                        key=f"status_{conv['id']}", 
                        horizontal=True, 
                        label_visibility="collapsed"
                    )
                    novos_status[conv['id']] = selecao
                    st.divider()
                
                # Botão de salvar alterações
                if st.form_submit_button("Salvar Apontamentos", type="primary", use_container_width=True):
                    try:
                        # Atualiza o status de cada colaborador modificado
                        for c_id, n_status in novos_status.items():
                            supabase.table("convocacoes").update({"status": n_status}).eq("id", c_id).execute()
                        st.success("✅ Apontamentos atualizados com sucesso no banco de dados!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
        else:
            st.warning("Nenhuma equipe foi convocada por você para a data de hoje.")

else:
    st.info("Aguardando carregamento do banco de dados ou corrigindo erros de conexão...")
