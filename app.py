import pandas as pd

def gerar_relatorio_custos():
    # Simulando os dados do relatório (substitua pela sua fonte real de dados)
    dados = [
        {
            "Data": "2026-08-28",
            "Unidade": "ESCRITÓRIO",
            "Obra": "APR9C019 - REFORMA ESCRITÓRIO APROAR",
            "Engenheiro": "PAULO",
            "Colaborador": "ANTONIO ERIVALDO NOBRE MACIE",
            "Função": "ALMOXARIFE",
            "Status": "Presente (Inte",
            "Diária": 240.00,
            "Extra": 0.00,
            "Obs": "Turno: Integral"
        },
        {
            "Data": "2026-08-28",
            "Unidade": "ESCRITÓRIO",
            "Obra": "APR9C019 - REFORMA ESCRITÓRIO APROAR",
            "Engenheiro": "PAULO",
            "Colaborador": "JEFFERSON MARREIRO DA SILVA",
            "Função": "AUX. PINTOR",
            "Status": "Presente (Inte",
            "Diária": 240.00,
            "Extra": 0.00,
            "Obs": "Turno: Integral"
        },
        {
            "Data": "2026-08-28",
            "Unidade": "ESCRITÓRIO",
            "Obra": "APR9C019 - REFORMA ESCRITÓRIO APROAR",
            "Engenheiro": "PAULO",
            "Colaborador": "FRANCISCO HILARIO COSTA BARB",
            "Função": "CARPINTEIRO",
            "Status": "Presente (Inte",
            "Diária": 240.00,
            "Extra": 0.00,
            "Obs": "Turno: Integral"
        },
        {
            "Data": "2026-08-28",
            "Unidade": "ESCRITÓRIO",
            "Obra": "APR9C019 - REFORMA ESCRITÓRIO APROAR",
            "Engenheiro": "PAULO",
            "Colaborador": "FRANCISCO ITALO BERNARDO ROD",
            "Função": "CARPINTEIRO",
            "Status": "Presente (Inte",
            "Diária": 240.00,
            "Extra": 0.00,
            "Obs": "Turno: Integral"
        }
    ]

    df = pd.DataFrame(dados)

    # 1. Cálculo do valor total por lançamento (Diária + Extra)
    df['Valor_Total_Linha'] = df['Diária'] + df['Extra']

    # 2. Cálculo dos totais consolidados por Engenheiro, Unidade e Obra
    totais_por_obra = df.groupby(
        ['Engenheiro', 'Unidade', 'Obra']
    )['Valor_Total_Linha'].sum().reset_index()
    
    totais_por_obra.rename(columns={'Valor_Total_Linha': 'Custo_Total'}, inplace=True)

    print("--- RESUMO: CUSTO TOTAL POR OBRA / ENGENHEIRO ---")
    print(totais_por_obra.to_string(index=False))
    print("-" * 50)

    # 3. Exportação segura para XLSX usando openpyxl (Evita erro de formato inválido no Excel)
    nome_arquivo = "relatorio_custos_25-08-2026_a_28-08-2026.xlsx"
    
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        # Aba 1: Relatório Detalhado
        df.to_excel(writer, sheet_name='Detalhado', index=False)
        # Aba 2: Resumo Financeiro por Obra e Engenheiro
        totais_por_obra.to_excel(writer, sheet_name='Totais por Obra', index=False)

    print(f"\n[Sucesso] Arquivo gerado corretamente e salvo como: {nome_arquivo}")

if __name__ == "__main__":
    gerar_relatorio_custos()
