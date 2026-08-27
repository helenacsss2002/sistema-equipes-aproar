import streamlit as st
from supabase import create_client, Client
import datetime
import pandas as pd
import json
from fpdf import FPDF
import unicodedata
import re

# --- CONFIGURAÇÕES DA PÁGINA & IDENTIDADE VISUAL APROAR ---
st.set_page_config(page_title="App Obras - APROAR", page_icon="👷", layout="centered")

# Injeção de CSS para o tema escuro institucional (Azul Marinho Aproar)
st.markdown("""
    <style>
    .stApp {
        background-color: #0C102B;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: #FFFFFF !important;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #0C102B !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

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

def get_cor_funcao(funcao):
    cores = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛"]
    hash_num = sum(ord(c) for c in str(funcao))
    return cores[hash_num % len(cores)]

def to_latin(texto):
    if not texto: return ""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

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

st.title("👷 APROAR - Gestão de Equipes")

tab_convocacao, tab_apontamento, tab_relatorios, tab_config = st.tabs(["📋 Convocação", "✅ Apontamento", "📊 Relatório", "⚙️ Config"])

# ==========================================
# ABA 1: CONVOCAÇÃO
# ==========================================
with tab_convocacao:
    if obras and colaboradores:
        st.markdown("### Informações da Demanda")
        col_eng, col_data = st.columns(2)
        with col_eng:
            engenheiro_conv = st.selectbox("Engenheiro responsável:", ENGENHEIROS, key="eng_conv")
        with col_data:
            amanha = datetime.date.today() + datetime.timedelta(days=1)
            data_conv = st.date_input("Data da Obra/Serviço (Amanhã):", value=amanha, format="DD/MM/YYYY")

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
                        "data": data_conv.isoformat(),
                        "engenheiro": engenheiro_conv,
                        "status": "Presente",
                        "valor_extra": 0,
                        "observacao": ""
                    })
                try:
                    supabase.table("convocacoes").insert(dados_insercao).execute()
                    st.success(f"✅ Equipe convocada com sucesso para {data_conv.strftime('%d/%m/%Y')}!")
                except Exception as e:
                    st.error("❌ Erro: O sistema bloqueou a ação pois o colaborador já está convocado para o mesmo dia em outra obra.")
    else:
        st.info("Cadastre obras (JSON) e colaboradores (Excel) na aba Configurações.")

# ==========================================
# ABA 2: APONTAMENTOS (SALVAMENTO EM TEMPO REAL / SEM BLOQUEIO)
# ==========================================
with tab_apontamento:
    st.markdown("### Apontamento Diário (Salvo em Tempo Real)")
    col_eng_ap, col_data_ap = st.columns(2)
    with col_eng_ap:
        engenheiro_apont = st.selectbox("Engenheiro:", ENGENHEIROS, key="eng_apont")
    with col_data_ap:
        data_apont = st.date_input("Data do Apontamento:", value=datetime.date.today(), format="DD/MM/YYYY")
    
    try:
        convocacoes_hoje = supabase.table("convocacoes").select("*").eq("engenheiro", engenheiro_apont).eq("data", data_apont.isoformat()).execute().data
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
        
        st.info("💡 Suas alterações são salvas automaticamente conforme você clica. Você pode parar e continuar de onde parou a qualquer momento.")
        
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
            
            # Atualização imediata no banco ao alterar o rádio
            status_sel = st.radio("Status", opcoes_status, index=idx, key=f"status_{c_id}", horizontal=True, label_visibility="collapsed")
            if status_sel != status_atual:
                supabase.table("convocacoes").update({"status": status_sel}).eq("id", c_id).execute()
            
            with st.expander("💸 Inserir Extra ou Observação"):
                val_atual = float(conv.get("valor_extra") or 0.0)
                obs_atual = conv.get("observacao") or ""
                
                val_extra = st.number_input("Bonificação / Extra (R$)", value=val_atual, step=10.0, key=f"val_{c_id}")
                obs = st.text_input("Justificativa / Acordo", value=obs_atual, key=f"obs_{c_id}")
                
                if val_extra != val_atual or obs != obs_atual:
                    supabase.table("convocacoes").update({"valor_extra": val_extra, "observacao": obs}).eq("id", c_id).execute()
            
            st.divider()
    else:
        st.warning(f"Nenhuma equipe convocada por {engenheiro_apont} para o dia {data_apont.strftime('%d/%m/%Y')}.")

# ==========================================
# ABA 3: RELATÓRIOS (DIÁRIO, SEMANAL, MENSAL)
# ==========================================
with tab_relatorios:
    st.markdown("### 📊 Relatório de Custos e Apontamentos")
    col_rel_eng, col_rel_tipo = st.columns(2)
    with col_eng:
        opcoes_relatorio = ["TODOS OS ENGENHEIROS"] + ENGENHEIROS
        eng_relatorio = st.selectbox("Engenheiro:", opcoes_relatorio, key="eng_rel")
    with col_rel_tipo:
        tipo_rel = st.selectbox("Frequência do Relatório:", ["Diário", "Semanal", "Mensal"], key="tipo_rel")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        data_base_rel = st.date_input("Data de Referência:", value=datetime.date.today(), format="DD/MM/YYYY", key="data_ref_rel")
    
    if st.button("Gerar PDF de Relatório Consolidado", type="primary"):
        try:
            # Lógica de cálculo de intervalo de datas (Diário, Semanal, Mensal)
            if tipo_rel == "Diário":
                data_inicio = data_base_rel.isoformat()
                data_fim = data_base_rel.isoformat()
                titulo_periodo = f"Diário - Data: {data_base_rel.strftime('%d/%m/%Y')}"
            elif tipo_rel == "Semanal":
                # Início da semana (Segunda) até Domingo
                inicio_sem = data_base_rel - datetime.timedelta(days=data_base_rel.weekday())
                fim_sem = inicio_sem + datetime.timedelta(days=6)
                data_inicio = inicio_sem.isoformat()
                data_fim = fim_sem.isoformat()
                titulo_periodo = f"Semanal - De {inicio_sem.strftime('%d/%m/%Y')} até {fim_sem.strftime('%d/%m/%Y')}"
            else: # Mensal
                inicio_mes = data_base_rel.replace(day=1)
                # último dia do mês
                if data_base_rel.month == 12:
                    fim_mes = data_base_rel.replace(year=data_base_rel.year+1, month=1, day=1) - datetime.timedelta(days=1)
                else:
                    fim_mes = data_base_rel.replace(month=data_base_rel.month+1, day=1) - datetime.timedelta(days=1)
                data_inicio = inicio_mes.isoformat()
                data_fim = fim_mes.isoformat()
                titulo_periodo = f"Mensal - Mês: {data_base_rel.strftime('%m/%Y')}"

            # Busca no Supabase por intervalo de datas
            query = supabase.table("convocacoes").select("*").gte("data", data_inicio).lte("data", data_fim)
            if eng_relatorio != "TODOS OS ENGENHEIROS":
                query = query.eq("engenheiro", eng_relatorio)
            
            dados_relatorio = query.execute().data
            
            if not dados_relatorio:
                st.warning(f"Sem apontamentos registrados para o período selecionado.")
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
                    pdf.set_font("Arial", 'B', 15)
                    pdf.cell(0, 10, txt=to_latin("APROAR ENGENHARIA - RELATÓRIO DE CUSTOS"), ln=True, align='C')
                    pdf.set_font("Arial", size=10)
                    pdf.cell(0, 8, txt=to_latin(f"Período: {titulo_periodo} | Engenheiro: {eng}"), ln=True, align='C')
                    pdf.ln(5)
                    
                    custo_total_engenheiro = 0.0
                    
                    for o_id, apontamentos in obras_eng.items():
                        dados_ob = dict_obras.get(o_id, {"nome": "N/A", "unidade": "N/A"})
                        
                        pdf.set_font("Arial", 'B', 11)
                        pdf.set_fill_color(220, 220, 220)
                        titulo_obra = f"Unidade: {dados_ob['unidade']} | Obra/Serviço: {dados_ob['nome']}"
                        pdf.cell(0, 8, txt=to_latin(titulo_obra), ln=True, fill=True)
                        
                        pdf.set_font("Arial", 'B', 9)
                        pdf.cell(25, 7, to_latin("Data"), border=1, align='C')
                        pdf.cell(65, 7, to_latin("Colaborador"), border=1)
                        pdf.cell(50, 7, to_latin("Função"), border=1)
                        pdf.cell(22, 7, to_latin("Status"), border=1, align='C')
                        pdf.cell(28, 7, to_latin("Diária (R$)"), border=1, align='C')
                        pdf.cell(28, 7, to_latin("Extra (R$)"), border=1, align='C')
                        pdf.cell(61, 7, to_latin("Observação"), border=1, ln=True)
                        
                        pdf.set_font("Arial", '', 9)
                        custo_total_obra = 0.0
                        
                        for row in apontamentos:
                            colab = dict_colaboradores.get(row['colaborador_id'], {})
                            nome = colab.get('nome', 'N/A')
                            funcao = colab.get('funcao', 'N/A')
                            status = row.get('status', 'Presente')
                            extra = float(row.get('valor_extra', 0) or 0)
                            obs = row.get('observacao', '')
                            data_item = row.get('data', '')
                            
                            diaria_base = 0.0
                            if status in ["Presente", "Extra"]:
                                diaria_base = float(colab.get('valor_diaria') or 240.0)
                            
                            subtotal_colab = diaria_base + extra
                            custo_total_obra += subtotal_colab
                            
                            nome_str = (nome[:28] + '..') if len(nome) > 28 else nome
                            func_str = (funcao[:20] + '..') if len(funcao) > 20 else funcao
                            obs_str = (obs[:30] + '..') if len(obs) > 30 else obs
                            
                            pdf.cell(25, 7, to_latin(data_item), border=1, align='C')
                            pdf.cell(65, 7, to_latin(nome_str), border=1)
                            pdf.cell(50, 7, to_latin(func_str), border=1)
                            pdf.cell(22, 7, to_latin(status), border=1, align='C')
                            pdf.cell(28, 7, to_latin(f"R$ {diaria_base:.2f}"), border=1, align='C')
                            pdf.cell(28, 7, to_latin(f"R$ {extra:.2f}"), border=1, align='C')
                            pdf.cell(61, 7, to_latin(obs_str), border=1, ln=True)
                        
                        pdf.set_font("Arial", 'B', 9)
                        pdf.set_fill_color(245, 245, 245)
                        pdf.cell(218, 7, to_latin("CUSTO TOTAL DA OBRA/SERVIÇO:"), border=1, align='R', fill=True)
                        pdf.cell(61, 7, to_latin(f"R$ {custo_total_obra:.2f}"), border=1, align='C', fill=True, ln=True)
                        pdf.ln(5)
                        
                        custo_total_engenheiro += custo_total_obra
                    
                    pdf.set_font("Arial", 'B', 10)
                    pdf.cell(0, 8, to_latin(f"CUSTO TOTAL GERAL (ENGENHEIRO {eng}): R$ {custo_total_engenheiro:.2f}"), ln=True, align='R')
                
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                nome_arquivo = f"Relatorio_Aproar_{tipo_rel}_{eng_relatorio}.pdf"
                st.download_button(label="📥 Baixar Relatório PDF Consolidado", data=pdf_bytes, file_name=nome_arquivo, mime="application/pdf")
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")

# ==========================================
# ABA 4: CONFIGURAÇÕES E IMPORTAÇÕES
# ==========================================
with tab_config:
    st.markdown("### 📋 Sincronizar Obras (Trello JSON)")
    arquivo_json = st.file_uploader("Selecione o arquivo JSON do Trello", type=["json"], key="json_trello")
    
    if arquivo_json is not None:
        if st.button("🔄 Importar Obras em Execução", type="primary"):
            with st.spinner("Analisando Trello..."):
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
                            nome_obra = partes[0] if len(partes) >= 2 else nome_card
                            unidade_limpa = identificar_unidade(nome_card)
                            novas_obras.append({"unidade": unidade_limpa, "nome": nome_obra})
                        
                        if novas_obras:
                            existentes = supabase.table("obras").select("unidade, nome").execute().data
                            set_existentes = {f"{o['unidade']} - {o['nome']}" for o in existentes}
                            inserir = [o for o in novas_obras if f"{o['unidade']} - {o['nome']}" not in set_existentes]
                            if inserir:
                                supabase.table("obras").insert(inserir).execute()
                                st.success(f"🎉 {len(inserir)} novas obras salvas!")
                                st.rerun()
                            else:
                                st.info("👍 Obras atualizadas. Sem novos registros.")
                        else:
                            st.warning("⚠️ Lista 'EM EXECUÇÃO' vazia.")
                except Exception as e:
                    st.error(f"Erro ao processar JSON: {e}")
    
    st.divider()
    
    st.markdown("### 📥 Sincronizar Base de Colaboradores (Excel)")
    arquivo_excel = st.file_uploader("Selecione a planilha Excel", type=["xlsx"], key="excel_colab")
    
    if arquivo_excel is not None:
        if st.button("🔄 Limpar e Importar Colaboradores", type="secondary"):
            with st.spinner("Lendo arquivo..."):
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
                        if diaria <= 0: diaria = 240.0 # Padrão de R$ 240,00 por profissional
                        
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
                        st.success(f"🎉 {len(novos_colaboradores)} colaboradores importados.")
                        st.rerun()
                    else:
                        st.info("Nenhum colaborador novo foi encontrado.")
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro: {e}")
