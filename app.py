import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import io
import json
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
dict_obras = {o['id']: o for o in obras} if obras else {}

ENGENHEIROS = ["EDUARDO", "GABRIEL", "GUSTAVO", "JOEL", "NETO", "PAULO", "SOARES", "VICTOR"]

def get_cor_funcao(funcao):
    cores = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛"]
    hash_num = sum(ord(c) for c in str(funcao))
    return cores[hash_num % len(cores)]

st.title("👷 Gestão de Equipes")

tab_convocacao, tab_apontamento, tab_relatorios, tab_config = st.tabs(["📋 Convocação", "✅ Apontamento", "📊 Relatório", "⚙️ Config"])

hoje = datetime.date.today().isoformat()

# ==========================================
# ABA 1: CONVOCAÇÃO (COM FILTRO CASCATA)
# ==========================================
with tab_convocacao:
    if obras and colaboradores:
        st.markdown("### Informações da Demanda")
        engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv")
        
        # Filtro Cascata: Unidade -> Obra
        unidades_unicas = sorted(list(set([o['unidade'] for o in obras])))
        col_u, col_o = st.columns(2)
        
        with col_u:
            unidade_selecionada = st.selectbox("Unidade:", unidades_unicas)
        
        obras_da_unidade = {o['nome']: o['id'] for o in obras if o['unidade'] == unidade_selecionada}
        with col_o:
            obra_selecionada = st.selectbox("Obra/Serviço:", list(obras_da_unidade.keys()))

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
# ABA 2: APONTAMENTOS (COM FILTRO CASCATA)
# ==========================================
with tab_apontamento:
    st.markdown("### Apontamento Diário")
    engenheiro_apont = st.selectbox("Engenheiro:", ENGENHEIROS, key="eng_apont")
    
    try:
        convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", hoje).execute().data
    except:
        convocacoes_hoje = []

    if convocacoes_hoje:
        # Enriquecer convocações com os dados da obra para permitir o filtro
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
        
        # Filtra a lista final que será renderizada na tela
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
                    dados_ob = dict_obras.get(row['obra_id'], {"nome": "N/A", "unidade": "N/A"})
                    
                    nome = colab.get('nome', 'N/A')
                    status = row.get('status', 'N/A')
                    extra = row.get('valor_extra', 0)
                    obs = row.get('observacao', '')
                    
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(0, 8, txt=f"Colaborador: {nome} | Obra: {dados_ob['unidade']} - {dados_ob['nome']}", ln=True)
                    pdf.set_font("Arial", '', 10)
                    pdf.cell(0, 6, txt=f"Status: {status} | Bonificacao/Extra: R$ {extra:.2f}", ln=True)
                    if obs:
                        pdf.cell(0, 6, txt=f"Obs: {obs}", ln=True)
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
    # --- IMPORTAÇÃO DO JSON DO TRELLO ---
    st.markdown("### 📋 Sincronizar Obras (Trello JSON)")
    st.info("O sistema buscará apenas os cards da lista 'EM EXECUÇÃO' e separará a Unidade do Nome da Obra automaticamente.")
    arquivo_json = st.file_uploader("Selecione o arquivo JSON do Trello", type=["json"], key="json_trello")
    
    if arquivo_json is not None:
        if st.button("🔄 Importar Obras em Execução", type="primary"):
            with st.spinner("Analisando Trello..."):
                try:
                    trello_data = json.load(arquivo_json)
                    list_execucao_id = None
                    
                    # Localiza o ID da lista "EM EXECUÇÃO"
                    for lst in trello_data.get('lists', []):
                        if lst.get('name', '').upper() == 'EM EXECUÇÃO' and not lst.get('closed', False):
                            list_execucao_id = lst.get('id')
                            break
                    
                    if not list_execucao_id:
                        st.error("❌ Lista 'EM EXECUÇÃO' não encontrada no arquivo.")
                    else:
                        cards = [c for c in trello_data.get('cards', []) if c.get('idList') == list_execucao_id and not c.get('closed', False)]
                        novas_obras = []
                        
                        for c in cards:
                            nome_card = c.get('name', '')
                            # Corta a string pela barra vertical "|"
                            partes = [p.strip() for p in nome_card.split('|')]
                            
                            if len(partes) >= 2:
                                nome_obra = partes[0]
                                unidade_obra = partes[1]
                            else:
                                nome_obra = nome_card
                                unidade_obra = "GERAL"
                            
                            novas_obras.append({"unidade": unidade_obra, "nome": nome_obra})
                        
                        if novas_obras:
                            # Compara com o banco para não duplicar obras que já entraram antes
                            existentes = supabase.table("obras").select("unidade, nome").execute().data
                            set_existentes = {f"{o['unidade']} - {o['nome']}" for o in existentes}
                            
                            inserir = [o for o in novas_obras if f"{o['unidade']} - {o['nome']}" not in set_existentes]
                            
                            if inserir:
                                supabase.table("obras").insert(inserir).execute()
                                st.success(f"🎉 {len(inserir)} novas obras cadastradas com sucesso!")
                            else:
                                st.info("👍 Nenhuma obra nova detectada. O banco já estava atualizado.")
                        else:
                            st.warning("⚠️ A lista 'EM EXECUÇÃO' está vazia no Trello.")
                except Exception as e:
                    st.error(f"Erro ao processar JSON: {e}")
    
    st.divider()
    
    # --- IMPORTAÇÃO DO EXCEL DOS COLABORADORES ---
    st.markdown("### 📥 Sincronizar Base de Colaboradores (Excel)")
    arquivo_excel = st.file_uploader("Selecione a planilha Excel", type=["xlsx"], key="excel_colab")
    
    if arquivo_excel is not None:
        if st.button("🔄 Importar e Atualizar Colaboradores", type="secondary"):
            with st.spinner("Lendo custos e atualizando banco..."):
                try:
                    df = pd.read_excel(arquivo_excel, sheet_name="Base de dados")
                    nomes_existentes = [c['nome'] for c in colaboradores] if colaboradores else []
                    novos_colaboradores = []
                    
                    for index, row in df.iterrows():
                        nome_excel = str(row.get('NOME', '')).strip()
                        funcao_excel = str(row.get('FUNÇÃO', '')).strip()
                        
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
