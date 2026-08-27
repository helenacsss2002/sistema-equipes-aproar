import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import io
from fpdf import FPDF
import random

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

dict_colaboradores = {c['id']: c for c in colaboradores} if colaboradores else {}

ENGENHEIROS = ["EDUARDO", "GABRIEL", "GUSTAVO", "JOEL", "NETO", "PAULO", "SOARES", "VICTOR"]

# Sistema simples para atribuir uma cor (emoji) consistente para cada função
def get_cor_funcao(funcao):
    cores = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫"]
    hash_num = sum(ord(c) for c in funcao)
    return cores[hash_num % len(cores)]

st.title("👷 Gestão de Equipes")

tab_convocacao, tab_apontamento, tab_relatorios, tab_config = st.tabs(["📋 Convocação", "✅ Apontamentos", "📊 Relatórios", "⚙️ Config"])

hoje = datetime.date.today().isoformat()

# ==========================================
# ABA 1: CONVOCAÇÃO
# ==========================================
with tab_convocacao:
    if obras and colaboradores:
        st.markdown("### Informações da Demanda")
        engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv")

        opcoes_obras = {f"{o['unidade']} - {o['nome']}": o['id'] for o in obras}
        obra_selecionada = st.selectbox("Selecione a Unidade e Serviço em Execução:", list(opcoes_obras.keys()))

        st.markdown("### Montar Equipe")
        # Puxa APENAS as funções que existem na base de colaboradores importada
        funcoes_disponiveis = sorted(list(set([c['funcao'] for c in colaboradores])))
        frente_selecionada = st.selectbox("Frente de Trabalho:", funcoes_disponiveis)

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
                    dados_insercao.append({
                        "obra_id": obra_id,
                        "colaborador_id": opcoes_colaboradores[nome],
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
# ABA 2: APONTAMENTOS (COM CORES POR FUNÇÃO)
# ==========================================
with tab_apontamento:
    st.markdown("### Apontamento Diário")
    engenheiro_apont = st.selectbox("Selecione seu nome para ver sua equipe de hoje:", ENGENHEIROS, key="eng_apont")
    
    try:
        convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", hoje).execute().data
    except:
        convocacoes_hoje = []

    if convocacoes_hoje:
        st.info("Marque as exceções do dia.")
        with st.form("form_apontamentos"):
            novos_status = {}
            opcoes_status = ["Presente", "Falta", "Atestado", "Extra"]
            
            for conv in convocacoes_hoje:
                dados_colab = dict_colaboradores.get(conv['colaborador_id'], {"nome": "Desconhecido", "funcao": "-"})
                nome = dados_colab['nome']
                funcao = dados_colab['funcao']
                cor = get_cor_funcao(funcao)
                status_atual = conv.get("status", "Presente")
                idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                
                st.markdown(f"**{nome}** &nbsp; {cor} `{funcao}`")
                
                selecao = st.radio("Status", opcoes_status, index=idx, key=f"status_{conv['id']}", horizontal=True, label_visibility="collapsed")
                novos_status[conv['id']] = selecao
                st.divider()
            
            if st.form_submit_button("Salvar Apontamentos", type="primary", use_container_width=True):
                try:
                    for c_id, n_status in novos_status.items():
                        supabase.table("convocacoes").update({"status": n_status}).eq("id", c_id).execute()
                    st.success("✅ Apontamentos atualizados com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
    else:
        st.warning("Nenhuma equipe convocada para hoje.")

# ==========================================
# ABA 3: RELATÓRIOS (PDF INDIVIDUAL)
# ==========================================
with tab_relatorios:
    st.markdown("### 📊 Gerar Relatório Diário")
    eng_relatorio = st.selectbox("Gerar relatório para o Engenheiro:", ENGENHEIROS, key="eng_rel")
    
    if st.button("Gerar PDF de Apontamentos"):
        try:
            dados_relatorio = supabase.table("convocacoes").select("*").eq("engenheiro", eng_relatorio).eq("data", hoje).execute().data
            
            if not dados_relatorio:
                st.warning("Sem dados para este engenheiro hoje.")
            else:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="Relatorio Diario de Apontamentos", ln=True, align='C')
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Data: {hoje} | Engenheiro: {eng_relatorio}", ln=True, align='C')
                pdf.ln(10)
                
                for row in dados_relatorio:
                    colab = dict_colaboradores.get(row['colaborador_id'], {})
                    nome = colab.get('nome', 'N/A')
                    funcao = colab.get('funcao', 'N/A')
                    status = row.get('status', 'N/A')
                    
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(80, 8, txt=f"Nome: {nome}", border=1)
                    pdf.set_font("Arial", '', 10)
                    pdf.cell(70, 8, txt=f"Funcao: {funcao}", border=1)
                    pdf.cell(40, 8, txt=f"Status: {status}", border=1, ln=True)
                
                # Gera o PDF em memória para download no Streamlit
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                
                st.download_button(
                    label="📥 Baixar Relatório PDF",
                    data=pdf_bytes,
                    file_name=f"Relatorio_{eng_relatorio}_{hoje}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")

# ==========================================
# ABA 4: IMPORTAR COLABORADORES
# ==========================================
with tab_config:
    st.markdown("### 📥 Importar Colaboradores via Excel")
    arquivo_excel = st.file_uploader("Selecione a planilha", type=["xlsx"])
    
    if arquivo_excel is not None:
        if st.button("🔄 Sincronizar Banco de Dados", type="primary"):
            with st.spinner("Atualizando banco..."):
                try:
                    df = pd.read_excel(arquivo_excel, sheet_name="Base de dados")
                    nomes_existentes = [c['nome'] for c in colaboradores] if colaboradores else []
                    novos_colaboradores = []
                    
                    for index, row in df.iterrows():
                        nome_excel = str(row.get('NOME', '')).strip()
                        funcao_excel = str(row.get('FUNÇÃO', '')).strip()
                        
                        if nome_excel and nome_excel.upper() != 'NAN' and nome_excel not in nomes_existentes:
                            novos_colaboradores.append({"nome": nome_excel, "funcao": funcao_excel, "ativo": True})
                            nomes_existentes.append(nome_excel) 
                    
                    if novos_colaboradores:
                        supabase.table("colaboradores").insert(novos_colaboradores).execute()
                        st.success(f"🎉 {len(novos_colaboradores)} novos colaboradores cadastrados.")
                    else:
                        st.info("Nenhum colaborador novo foi encontrado.")
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro: {e}")
