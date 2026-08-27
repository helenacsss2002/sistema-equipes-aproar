import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import io
import json
from fpdf import FPDF
import unicodedata
import re

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

# --- FUNÇÕES DE LIMPEZA E PADRONIZAÇÃO ---
def limpar_unidade(texto):
    if not texto: return "GERAL"
    texto_limpo = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('utf-8').upper().strip()
    
    macro_unidades = {
        "HORIZONTE": "HORIZONTE",
        "FIEC": "FIEC",
        "CASA DA INDUSTRIA": "FIEC",
        "DR": "FIEC",
        "BARRA": "BARRA",
        "COLISEU": "COLISEU",
        "MARACANAU": "MARACANAÚ",
        "ESCRITORIO": "ESCRITÓRIO",
        "CENTRO": "CENTRO",
        "MUSEU": "MUSEU",
        "UNIFOR": "UNIFOR"
    }
    
    for chave, valor in macro_unidades.items():
         if chave in texto_limpo:
             return valor
    return texto_limpo

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
        st.info("Cadastre obras (JSON) e colaboradores (Excel) na aba Configurações.")

# ==========================================
# ABA 2: APONTAMENTOS
# ==========================================
with tab_apontamento:
    st.markdown("### Apontamento Diário")
    engenheiro_apont = st.selectbox("Engenheiro:", ENGENHEIROS, key="eng_apont")
    
    try:
        convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", hoje).execute().data
    except:
        convocacoes_hoje = []

    if convocacoes_hoje:
        for conv in convocacoes_hoje:
            conv['dados_obra'] = dict_obras.get(conv['obra_id'], {"unidade": "Desconhecida", "nome": "Desconhecida"})
            
        unidades_convocadas = sorted(list(set([c['dados_obra']['unidade'] for c in convocacoes_hoje])))
        
        st.markdown("##### Filtrar a equipe por:")
        col_ua, col_oa = st.columns(2)
        with col_ua:
            unidade_filtro = st.selectbox("Unidade Convocada:", unidades_convocadas, key="filtro_u_apont")
        
        obras_convocadas = sorted(list(set([c['dados_obra']['nome'] for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro])))
        with col_oa:
            obra_filtro = st.selectbox("Obra Convocada:", obras_convocadas, key="filtro_o_apont")
        
        convocacoes_render = [c for c in convocacoes_hoje if c['dados_obra']['unidade'] == unidade_filtro and c['dados_obra']['nome'] == obra_filtro]
        
        st.info("Marque as exceções do dia e insira bonificações se necessário.")
        with st.form("form_apontamentos"):
            alteracoes = {}
            opcoes_status = ["Presente", "Falta", "Atestado", "Extra"]
            
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
                
                with st.expander("💸 Inserir Extra ou Observação"):
                    val_atual = float(conv.get("valor_extra") or 0.0)
                    obs_atual = conv.get("observacao") or ""
                    
                    val_extra = st.number_input("Bonificação / Extra (R$)", value=val_atual, step=10.0, key=f"val_{c_id}")
                    obs = st.text_input("Justificativa / Acordo", value=obs_atual, key=f"obs_{c_id}")
                
                alteracoes[c_id] = {"status": status_sel, "valor_extra": val_extra, "observacao": obs}
                st.divider()
            
            if st.form_submit_button("Salvar Apontamentos desta Obra", type="primary", use_container_width=True):
                try:
                    for c_id, dados in alteracoes.items():
                        supabase.table("convocacoes").update(dados).eq("id", c_id).execute()
                    st.success("✅ Apontamentos e Acordos salvos com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
    else:
        st.warning("Nenhuma equipe convocada por você para a data de hoje.")

# ==========================================
# ABA 3: RELATÓRIOS
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
                    dados_ob = dict_obras.get(row['obra_id'], {"nome": "N/A", "unidade": "N/A"})
                    
                    nome = colab.get('nome', 'N/A')
                    status = row.get('status', 'N/A')
                    extra = row.get('valor_extra', 0)
                    obs = row.get('observacao', '')
                    
                    pdf.set_font("Arial", 'B', 10)
                    nome_pdf = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
                    unidade_pdf = unicodedata.normalize('NFKD', dados_ob['unidade']).encode('ASCII', 'ignore').decode('utf-8')
                    obra_pdf = unicodedata.normalize('NFKD', dados_ob['nome']).encode('ASCII', 'ignore').decode('utf-8')
                    
                    pdf.cell(0, 8, txt=f"Colaborador: {nome_pdf} | Obra: {unidade_pdf} - {obra_pdf}", ln=True)
                    pdf.set_font("Arial", '', 10)
                    pdf.cell(0, 6, txt=f"Status: {status} | Bonificacao/Extra: R$ {extra:.2f}", ln=True)
                    if obs:
                        obs_pdf = unicodedata.normalize('NFKD', obs).encode('ASCII', 'ignore').decode('utf-8')
                        pdf.cell(0, 6, txt=f"Obs: {obs_pdf}", ln=True)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(3)
                
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                st.download_button(label="📥 Baixar Relatório", data=pdf_bytes, file_name=f"Relatorio_{eng_relatorio}.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

# ==========================================
# ABA 4: CONFIGURAÇÕES E IMPORTAÇÕES
# ==========================================
with tab_config:
    st.markdown("### 📋 Sincronizar Obras (Trello JSON)")
    st.info("O sistema unifica os nomes das unidades e limpa discrepâncias (ex: SESI Centro vira CENTRO).")
    arquivo_json = st.file_uploader("Selecione o arquivo JSON do Trello", type=["json"], key="json_trello")
    
    if arquivo_json is not None:
        if st.button("🔄 Importar Obras em Execução", type="primary"):
            with st.spinner("Limpando e Analisando Trello..."):
                try:
                    trello_data = json.load(arquivo_json)
                    list_execucao_id = None
                    
                    for lst in trello_data.get('lists', []):
                        if lst.get('name', '').upper() == 'EM EXECUÇÃO' and not lst.get('closed', False):
                            list_execucao_id = lst.get('id')
                            break
                    
                    if not list_execucao_id:
                        st.error("❌ Lista 'EM EXECUÇÃO' não encontrada.")
                    else:
                        cards = [c for c in trello_data.get('cards', []) if c.get('idList') == list_execucao_id and not c.get('closed', False)]
                        novas_obras = []
                        
                        for c in cards:
                            nome_card = c.get('name', '')
                            partes = [p.strip() for p in nome_card.split('|')]
                            
                            if len(partes) >= 2:
                                nome_obra = partes[0]
                                unidade_crua = partes[1]
                            else:
                                nome_obra = nome_card
                                unidade_crua = "GERAL"
                            
                            unidade_limpa = limpar_unidade(unidade_crua)
                            novas_obras.append({"unidade": unidade_limpa, "nome": nome_obra})
                        
                        if novas_obras:
                            existentes = supabase.table("obras").select("unidade, nome").execute().data
                            set_existentes = {f"{o['unidade']} - {o['nome']}" for o in existentes}
                            
                            inserir = [o for o in novas_obras if f"{o['unidade']} - {o['nome']}" not in set_existentes]
                            
                            if inserir:
                                supabase.table("obras").insert(inserir).execute()
                                st.success(f"🎉 {len(inserir)} novas obras padronizadas e salvas!")
                                st.rerun() # Atualiza a tela automaticamente
                            else:
                                st.info("👍 Obras atualizadas. Sem novos registros.")
                        else:
                            st.warning("⚠️ Lista 'EM EXECUÇÃO' vazia.")
                except Exception as e:
                    st.error(f"Erro ao processar JSON: {e}")
    
    st.divider()
    
    st.markdown("### 📥 Sincronizar Base de Colaboradores (Excel)")
    st.info("O sistema remove numerações e acentos das funções (ex: 076 - PEDREIRO vira PEDREIRO).")
    arquivo_excel = st.file_uploader("Selecione a planilha Excel", type=["xlsx"], key="excel_colab")
    
    if arquivo_excel is not None:
        if st.button("🔄 Limpar e Importar Colaboradores", type="secondary"):
            with st.spinner("Lendo arquivo e padronizando funções..."):
                try:
                    xls = pd.ExcelFile(arquivo_excel)
                    nome_aba = "Base de dados" if "Base de dados" in xls.sheet_names else xls.sheet_names[0]
                    df = pd.read_excel(xls, sheet_name=nome_aba)
                    
                    nomes_existentes = [c['nome'] for c in colaboradores] if colaboradores else []
                    novos_colaboradores = []
                    
                    for index, row in df.iterrows():
                        nome_excel = str(row.get('NOME', '')).strip()
                        funcao_crua = str(row.get('FUNÇÃO', '')).strip()
                        funcao_limpa = limpar_funcao(funcao_crua)
                        
                        try: diaria = float(row.get('VALOR DIÁRIA (R$)', 0))
                        except: diaria = 0.0
                        
                        try: passagem = float(row.get('PASSAGEM', 0))
                        except: passagem = 0.0
                        
                        if nome_excel and nome_excel.upper() != 'NAN' and nome_excel not in nomes_existentes:
                            novos_colaboradores.append({
                                "nome": nome_excel, 
                                "funcao": funcao_limpa, 
                                "valor_diaria": diaria,
                                "valor_passagem": passagem,
                                "ativo": True
                            })
                            nomes_existentes.append(nome_excel) 
                    
                    if novos_colaboradores:
                        supabase.table("colaboradores").insert(novos_colaboradores).execute()
                        st.success(f"🎉 {len(novos_colaboradores)} colaboradores importados sem duplicidade de funções.")
                        st.rerun() # Atualiza a tela automaticamente
                    else:
                        st.info("Nenhum colaborador novo foi encontrado.")
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro: {e}")
