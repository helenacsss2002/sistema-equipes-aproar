import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import io
from fpdf import FPDF

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

def get_cor_funcao(funcao):
    cores = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛"]
    hash_num = sum(ord(c) for c in str(funcao))
    return cores[hash_num % len(cores)]

st.title("👷 Gestão de Equipes")

tab_convocacao, tab_apontamento, tab_relatorios, tab_config = st.tabs(["📋 Convocação", "✅ Apontamento", "📊 Relatório", "⚙️ Config"])

hoje = datetime.date.today().isoformat()

# ==========================================
# ABA 1: CONVOCAÇÃO
# ==========================================
with tab_convocacao:
    if obras and colaboradores:
        st.markdown("### Informações da Demanda")
        engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv")
        opcoes_obras = {f"{o['unidade']} - {o['nome']}": o['id'] for o in obras}
        obra_selecionada = st.selectbox("Selecione a Unidade e Obra/Serviço:", list(opcoes_obras.keys()))

        st.markdown("### Montar Equipe")
        funcoes_disponiveis = sorted(list(set([str(c['funcao']) for c in colaboradores])))
        frente_selecionada = st.selectbox("Frente de Trabalho:", funcoes_disponiveis)

        colaboradores_filtrados = [c for c in colaboradores if c['funcao'] == frente_selecionada]
        opcoes_colaboradores = {c['nome']: c['id'] for c in colaboradores_filtrados}

        equipe_selecionada = st.multiselect("Selecione os colaboradores para esta frente:", list(opcoes_colaboradores.keys()))

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
                        "status": "Presente",
                        "valor_extra": 0,
                        "observacao": ""
                    })
                try:
                    supabase.table("convocacoes").insert(dados_insercao).execute()
                    st.success("✅ Equipe convocada com sucesso!")
                except Exception as e:
                    st.error("❌ Erro: Possível duplicidade. Colaborador já convocado hoje.")
    else:
        st.info("Cadastre obras e colaboradores na aba Configurações.")

# ==========================================
# ABA 2: APONTAMENTOS (COM ACORDOS FINANCEIROS)
# ==========================================
with tab_apontamento:
    st.markdown("### Apontamento Diário")
    engenheiro_apont = st.selectbox("Engenheiro:", ENGENHEIROS, key="eng_apont")
    
    try:
        convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", hoje).execute().data
    except:
        convocacoes_hoje = []

    if convocacoes_hoje:
        with st.form("form_apontamentos"):
            alteracoes = {}
            opcoes_status = ["Presente", "Falta", "Atestado", "Extra"]
            
            for conv in convocacoes_hoje:
                c_id = conv['id']
                dados_colab = dict_colaboradores.get(conv['colaborador_id'], {"nome": "Desconhecido", "funcao": "-"})
                nome = dados_colab['nome']
                funcao = dados_colab['funcao']
                cor = get_cor_funcao(funcao)
                status_atual = conv.get("status", "Presente")
                idx = opcoes_status.index(status_atual) if status_atual in opcoes_status else 0
                
                # Exibe Nome e Função
                st.markdown(f"**{nome}** &nbsp; {cor} `{funcao}`")
                
                # Botões de Status
                status_sel = st.radio("Status", opcoes_status, index=idx, key=f"status_{c_id}", horizontal=True, label_visibility="collapsed")
                
                # Sanfona Oculta para Extras e Observações (Mantém a tela limpa no celular)
                with st.expander("💸 Inserir Extra ou Observação"):
                    val_atual = float(conv.get("valor_extra") or 0.0)
                    obs_atual = conv.get("observacao") or ""
                    
                    val_extra = st.number_input("Bonificação / Extra (R$)", value=val_atual, step=10.0, key=f"val_{c_id}")
                    obs = st.text_input("Justificativa / Acordo", value=obs_atual, key=f"obs_{c_id}")
                
                alteracoes[c_id] = {"status": status_sel, "valor_extra": val_extra, "observacao": obs}
                st.divider()
            
            if st.form_submit_button("Salvar Apontamentos", type="primary", use_container_width=True):
                try:
                    for c_id, dados in alteracoes.items():
                        supabase.table("convocacoes").update(dados).eq("id", c_id).execute()
                    st.success("✅ Apontamentos e Acordos salvos com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
    else:
        st.warning("Nenhuma equipe convocada por você para a data de hoje.")

# ==========================================
# ABA 3: RELATÓRIOS EM PDF
# ==========================================
with tab_relatorios:
    st.markdown("### 📊 Relatório do Dia")
    eng_relatorio = st.selectbox("Selecione o Engenheiro:", ENGENHEIROS, key="eng_rel")
    
    if st.button("Gerar PDF de Custos/Apontamento"):
        try:
            dados_relatorio = supabase.table("convocacoes").select("*").eq("engenheiro", eng_relatorio).eq("data", hoje).execute().data
            
            if not dados_relatorio:
                st.warning("Sem apontamentos hoje.")
            else:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, txt="Relatorio de Apontamentos e Acordos", ln=True, align='C')
                pdf.set_font("Arial", size=10)
                pdf.cell(200, 10, txt=f"Data: {hoje} | Engenheiro: {eng_relatorio}", ln=True, align='C')
                pdf.ln(5)
                
                for row in dados_relatorio:
                    colab = dict_colaboradores.get(row['colaborador_id'], {})
                    nome = colab.get('nome', 'N/A')
                    status = row.get('status', 'N/A')
                    extra = row.get('valor_extra', 0)
                    obs = row.get('observacao', '')
                    
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(0, 8, txt=f"Colaborador: {nome}", ln=True)
                    pdf.set_font("Arial", '', 10)
                    pdf.cell(0, 6, txt=f"Status: {status} | Bonificacao/Extra: R$ {extra:.2f}", ln=True)
                    if obs:
                        pdf.cell(0, 6, txt=f"Obs: {obs}", ln=True)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(3)
                
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                st.download_button(label="📥 Baixar Relatório", data=pdf_bytes, file_name=f"Relatorio_{eng_relatorio}.pdf", mime="application/pdf")
        except Exception as e:
            st.error("Erro ao gerar PDF.")

# ==========================================
# ABA 4: IMPORTAR COLABORADORES (ATUALIZADA C/ FINANCEIRO)
# ==========================================
with tab_config:
    st.markdown("### 📥 Sincronizar Base de Colaboradores")
    st.info("O sistema agora lê 'VALOR DIÁRIA' e 'PASSAGEM' da planilha.")
    arquivo_excel = st.file_uploader("Selecione a planilha", type=["xlsx"])
    
    if arquivo_excel is not None:
        if st.button("🔄 Importar e Atualizar", type="primary"):
            with st.spinner("Lendo custos e atualizando banco..."):
                try:
                    df = pd.read_excel(arquivo_excel, sheet_name="Base de dados")
                    nomes_existentes = [c['nome'] for c in colaboradores] if colaboradores else []
                    novos_colaboradores = []
                    
                    for index, row in df.iterrows():
                        nome_excel = str(row.get('NOME', '')).strip()
                        funcao_excel = str(row.get('FUNÇÃO', '')).strip()
                        
                        # Extrai valores financeiros tratando erros caso a célula esteja vazia (NaN)
                        try: diaria = float(row.get('VALOR DIÁRIA (R$)', 0))
                        except: diaria = 0.0
                        
                        try: passagem = float(row.get('PASSAGEM', 0))
                        except: passagem = 0.0
                        
                        if nome_excel and nome_excel.upper() != 'NAN' and nome_excel not in nomes_existentes:
                            novos_colaboradores.append({
                                "nome": nome_excel, 
                                "funcao": funcao_excel, 
                                "valor_diaria": diaria,
                                "valor_passagem": passagem,
                                "ativo": True
                            })
                            nomes_existentes.append(nome_excel) 
                    
                    if novos_colaboradores:
                        supabase.table("colaboradores").insert(novos_colaboradores).execute()
                        st.success(f"🎉 {len(novos_colaboradores)} novos colaboradores com custos importados.")
                    else:
                        st.info("Nenhum colaborador novo foi encontrado.")
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro: {e}")
