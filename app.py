# --- IMPORTAÇÃO DO EXCEL DOS COLABORADORES ---
    st.markdown("### 📥 Sincronizar Base de Colaboradores (Excel)")
    st.info("O sistema remove numerações e acentos das funções (ex: 076 - PEDREIRO vira PEDREIRO).")
    arquivo_excel = st.file_uploader("Selecione a planilha Excel", type=["xlsx"], key="excel_colab")
    
    if arquivo_excel is not None:
        if st.button("🔄 Limpar e Importar Colaboradores", type="secondary"):
            with st.spinner("Lendo arquivo e padronizando funções..."):
                try:
                    # Deixa a leitura dinâmica para qualquer nome de aba
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
                    else:
                        st.info("Nenhum colaborador novo foi encontrado.")
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro: {e}")
