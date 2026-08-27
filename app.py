import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd

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
        return []

def buscar_colaboradores():
    try:
        return supabase.table("colaboradores").select("*").eq("ativo", True).execute().data
    except Exception as e:
        return []

obras = buscar_obras()
colaboradores = buscar_colaboradores()

# Dicionário de colaboradores para acesso rápido (ID -> Dados)
dict_colaboradores = {c['id']: c for c in colaboradores} if colaboradores else {}

# Lista fixa de engenheiros
ENGENHEIROS = ["EDUARDO", "GABRIEL", "GUSTAVO", "JOEL", "NETO", "PAULO", "SOARES", "VICTOR"]

st.title("👷 Gestão de Equipes")

# Criando as Abas de navegação (agora são 3)
tab_convocacao, tab_apontamento, tab_config = st.tabs(["📋 Convocação", "✅ Apontamentos", "⚙️ Configurações"])

hoje = datetime.date.today().isoformat()

# ==========================================
# ABA 1: CONVOCAÇÃO
# ==========================================
with tab_convocacao:
    if obras and colaboradores:
        st.markdown("### Informações da Demanda")
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
                        "status": "Presente" 
                    })
                
                try:
                    supabase.table("convocacoes").insert(dados_insercao).execute()
                    st.success("✅ Equipe convocada com sucesso!")
                except Exception as e:
                    if "duplicate key value" in str(e):
                        st.error("❌ Erro: Colaborador já convocado para hoje.")
                    else:
                        st.error(f"❌ Ocorreu um erro: {e}")
    else:
        st.info("Cadastre obras e colaboradores para começar.")

# ==========================================
# ABA 2: APONTAMENTOS (ENXUTO E COM ETIQUETA)
# ==========================================
with tab_apontamento:
    st.markdown("### Apontamento Diário")
    engenheiro_apont = st.selectbox("Selecione seu nome para ver sua equipe de hoje:", ENGENHEIROS, key="eng_apont")
    
    try:
        res_convs = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", hoje).execute()
        convocacoes_hoje = res_convs.data
    except Exception as e:
        convocacoes_hoje = []

    if convocacoes_hoje:
        st.info("Todos estão marcados como 'Presente' por padrão. Altere apenas as exceções.")
        
        with st.form("form_apontamentos"):
            novos_status = {}
            opcoes_status = ["Presente", "Falta", "Atestado", "Extra"]
            
            for conv in convocacoes_hoje:
                dados_colab = dict_colaboradores.get(conv['colaborador_id'], {"nome": "Desconhecido", "funcao": "-"})
                nome = dados_colab['nome']
                funcao = dados_colab['funcao']
                status_atual = conv.get("status", "Presente")
                
                idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                
                # Exibindo o Nome + Etiqueta de Função da maneira mais visual e enxuta
                st.markdown(f"**{nome}** &nbsp; 🏷️ `{funcao}`")
                
                # Botões de toque rápido para o celular
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
            
            if st.form_submit_button("Salvar Apontamentos", type="primary", use_container_width=True):
                try:
                    for c_id, n_status in novos_status.items():
                        supabase.table("convocacoes").update({"status": n_status}).eq("id", c_id).execute()
                    st.success("✅ Apontamentos atualizados com sucesso no banco de dados!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
    else:
        st.warning("Nenhuma equipe foi convocada por você para a data de hoje.")

# ==========================================
# ABA 3: IMPORTAR COLABORADORES
# ==========================================
with tab_config:
    st.markdown("### 📥 Importar Colaboradores via Excel")
    st.write("Faça o upload do arquivo `CONVOCAÇÃO DE COLABORADORES.xlsx` para adicionar novos funcionários automaticamente ao banco.")
    
    arquivo_excel = st.file_uploader("Selecione a planilha", type=["xlsx"])
    
    if arquivo_excel is not None:
        if st.button("🔄 Sincronizar Banco de Dados", type="primary"):
            with st.spinner("Lendo arquivo e atualizando banco..."):
                try:
                    # Lê o arquivo Excel enviado
                    df = pd.read_excel(arquivo_excel)
                    
                    # Pega a lista de nomes que já existem no banco para não duplicar
                    nomes_existentes = [c['nome'] for c in colaboradores] if colaboradores else []
                    
                    novos_colaboradores = []
                    
                    for index, row in df.iterrows():
                        # Pega o nome e a função (se as colunas existirem no Excel)
                        nome_excel = str(row.get('NOME', '')).strip()
                        funcao_excel = str(row.get('FUNÇÃO', '')).strip()
                        
                        # Verifica se a linha não está vazia e se o nome não está no banco
                        if nome_excel and nome_excel.upper() != 'NAN' and nome_excel not in nomes_existentes:
                            novos_colaboradores.append({
                                "nome": nome_excel,
                                "funcao": funcao_excel,
                                "ativo": True
                            })
                            # Adiciona na lista temporária para evitar duplicatas dentro da própria planilha
                            nomes_existentes.append(nome_excel) 
                    
                    if novos_colaboradores:
                        supabase.table("colaboradores").insert(novos_colaboradores).execute()
                        st.success(f"🎉 Sincronização concluída! {len(novos_colaboradores)} novos colaboradores cadastrados.")
                        st.balloons()
                    else:
                        st.info("Nenhum colaborador novo foi encontrado. Todos já estão no banco de dados!")
                        
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro ao processar a planilha: {e}")
