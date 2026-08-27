from datetime import datetime
import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="APROAR - Gestão de Apontamentos e Custos",
    page_icon="🏗️",
    layout="wide",
)

# Estilização visual básica com CSS injetado
st.markdown(
    """
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    </style>
""",
    unsafe_allow_html=True,
)


def calcular_diaria_proporcional(status, valor_base):
  if not status or "Integral" in status:
    return float(valor_base)
  elif "Meio Período" in status or "Parcial" in status:
    return float(valor_base) / 2.0
  elif "Falta" in status or "Atestado" in status:
    return 0.0
  return float(valor_base)


def main():
  st.sidebar.title("🏗️ APROAR ENGENHARIA")
  st.sidebar.markdown("---")

  menu = st.sidebar.selectbox(
      "Navegação",
      ["📋 APONTAMENTOS", "📊 RELATÓRIOS", "👥 COLABORADORES", "🏗️ OBRAS"],
  )

  # Dados simulados/mock para demonstração de integridade caso o banco não esteja conectado nesta execução
  if "dict_colaboradores" not in st.session_state:
    st.session_state.dict_colaboradores = {
        1: {
            "nome": "João Silva",
            "funcao": "Pedreiro",
            "valor_diaria": 240.0,
        },
        2: {
            "nome": "Carlos Souza",
            "funcao": "Carpinteiro",
            "valor_diaria": 250.0,
        },
        3: {
            "nome": "Marcos Lima",
            "funcao": "Servente",
            "valor_diaria": 180.0,
        },
    }

  if "dict_obras" not in st.session_state:
    st.session_state.dict_obras = {
        101: {"nome": "Obra Centro Comercial", "unidade": "Unidade A"},
        102: {"nome": "Reforma Helipad FIEC", "unidade": "Unidade B"},
    }

  if "dados_relatorio" not in st.session_state:
    st.session_state.dados_relatorio = [
        {
            "data": "2026-08-25",
            "colaborador_id": 1,
            "obra_id": 101,
            "engenheiro": "EDUARDO",
            "status": "Presente (Integral)",
            "valor_extra": 50.0,
            "observacao": "Concretagem laje",
        },
        {
            "data": "2026-08-25",
            "colaborador_id": 2,
            "obra_id": 101,
            "engenheiro": "EDUARDO",
            "status": "Presente (Integral)",
            "valor_extra": 0.0,
            "observacao": "",
        },
        {
            "data": "2026-08-26",
            "colaborador_id": 3,
            "obra_id": 102,
            "engenheiro": "GABRIEL",
            "status": "Presente (Integral)",
            "valor_extra": 30.0,
            "observacao": "Instalação cobertura",
        },
    ]

  dict_colaboradores = st.session_state.dict_colaboradores
  dict_obras = st.session_state.dict_obras
  dados_relatorio = st.session_state.dados_relatorio

  if menu == "📋 APONTAMENTOS":
    st.title("📋 Módulo de Apontamentos Diários")
    st.info(
        "Utilize esta aba para registrar a presença, faltas e extras da"
        " equipe."
    )
    # Exemplo rápido de tabela na tela
    df_apont = pd.DataFrame(dados_relatorio)
    st.dataframe(df_apont, use_container_width=True)

  elif menu == "📊 RELATÓRIOS":
    st.title("📊 Relatórios Gerenciais e Custos")
    st.markdown(
        "Filtre os lançamentos por período e engenheiro para exportação"
        " profissional em Excel."
    )

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
      data_inicio_rel = st.date_input(
          "Data Inicial", value=datetime.strptime("2026-08-01", "%Y-%m-%d")
      )
    with col_f2:
      data_fim_rel = st.date_input(
          "Data Final", value=datetime.strptime("2026-08-31", "%Y-%m-%d")
      )
    with col_f3:
      eng_relatorio = st.selectbox(
          "Engenheiro Responsável",
          [
              "TODOS OS ENGENHEIROS",
              "EDUARDO",
              "GABRIEL",
              "GUSTAVO",
              "JOEL",
              "NETO",
              "PAULO",
              "SOARES",
              "VICTOR",
          ],
      )

    st.markdown("---")

    col_btn1, col_btn2 = st.columns([2, 2])
    with col_btn2:
      if st.button("📊 Gerar Excel", type="primary", use_container_width=True):
        try:
          if data_inicio_rel > data_fim_rel:
            st.error("Data inicial maior que a final.")
          elif not dados_relatorio:
            st.warning("Sem dados no período.")
          else:
            output = io.BytesIO()
            wb = openpyxl.Workbook()
            wb.remove(wb.active)  # Remove aba padrão

            # Estilos openpyxl corporativos
            fill_header = PatternFill(
                start_color="1E293B", end_color="1E293B", fill_type="solid"
            )
            font_header = Font(
                name="Calibri", size=11, bold=True, color="FFFFFF"
            )
            font_body = Font(name="Calibri", size=10)
            font_title = Font(
                name="Calibri", size=14, bold=True, color="1E293B"
            )
            font_subtitle = Font(
                name="Calibri", size=10, italic=True, color="475569"
            )

            fill_total = PatternFill(
                start_color="F1F5F9", end_color="F1F5F9", fill_type="solid"
            )
            font_total = Font(
                name="Calibri", size=10, bold=True, color="0F172A"
            )

            thin_border = Border(
                left=Side(style="thin", color="CBD5E1"),
                right=Side(style="thin", color="CBD5E1"),
                top=Side(style="thin", color="CBD5E1"),
                bottom=Side(style="thin", color="CBD5E1"),
            )

            # Paleta de cores para diferenciação visual por engenheiro
            eng_colors = {
                "EDUARDO": "DBEAFE",
                "GABRIEL": "DCFCE7",
                "GUSTAVO": "FEF9C3",
                "JOEL": "FFEDD5",
                "NETO": "FCE7F3",
                "PAULO": "F3E8FF",
                "SOARES": "CCFBF1",
                "VICTOR": "FEE2E2",
            }

            # Filtrar dados conforme o período e engenheiro selecionado
            dados_filtrados = []
            for row in dados_relatorio:
              dt_row = row.get("data", "")
              eng_row = row.get("engenheiro", "")
              try:
                dt_obj = datetime.strptime(dt_row, "%Y-%m-%d").date()
              except:
                continue

              if data_inicio_rel <= dt_obj <= data_fim_rel:
                if (
                    eng_relatorio == "TODOS OS ENGENHEIROS"
                    or eng_row == eng_relatorio
                ):
                  dados_filtrados.append(row)

            if not dados_filtrados:
              st.warning("Nenhum registro encontrado para os filtros definidos.")
              return

            # Agrupar dados por data para criar abas no formato DD-MM-YYYY
            dados_por_data = {}
            for row in dados_filtrados:
              dt = row.get("data", "")
              if dt not in dados_por_data:
                dados_por_data[dt] = []
              dados_por_data[dt].append(row)

            datas_ordenadas = sorted(dados_por_data.keys())

            for dt_str in datas_ordenadas:
              registros = dados_por_data[dt_str]
              try:
                partes_dt = dt_str.split("-")
                if len(partes_dt) == 3:
                  sheet_title = f"{partes_dt[2]}-{partes_dt[1]}-{partes_dt[0]}"
                else:
                  sheet_title = dt_str
              except:
                sheet_title = dt_str

              ws = wb.create_sheet(title=sheet_title)
              ws.views.sheetView[0].showGridLines = True

              # Título e Subtítulo na Planilha
              ws.merge_cells("A1:J1")
              ws["A1"] = (
                  f"APROAR - RELATÓRIO DIÁRIO DE APONTAMENTOS ({sheet_title})"
              )
              ws["A1"].font = font_title
              ws["A1"].alignment = Alignment(
                  horizontal="center", vertical="center"
              )
              ws.row_dimensions[1].height = 30

              ws.merge_cells("A2:J2")
              eng_filtro_texto = (
                  f"Engenheiro: {eng_relatorio}"
                  if eng_relatorio != "TODOS OS ENGENHEIROS"
                  else "Todos os Engenheiros"
              )
              ws["A2"] = (
                  f"Data de Referência: {sheet_title} | {eng_filtro_texto}"
              )
              ws["A2"].font = font_subtitle
              ws["A2"].alignment = Alignment(
                  horizontal="center", vertical="center"
              )
              ws.row_dimensions[2].height = 20

              # Cabeçalhos da Tabela (Linha 4)
              headers = [
                  "Colaborador",
                  "Função",
                  "Unidade",
                  "Obra",
                  "Engenheiro",
                  "Status",
                  "Diária (R$)",
                  "Extra (R$)",
                  "Custo Total (R$)",
                  "Observação",
              ]
              ws.row_dimensions[4].height = 25

              for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=4, column=col_idx, value=header)
                cell.fill = fill_header
                cell.font = font_header
                cell.alignment = Alignment(
                    horizontal="center", vertical="center", wrap_text=True
                )
                cell.border = thin_border

              current_row = 5
              for row in registros:
                colab = dict_colaboradores.get(row["colaborador_id"], {})
                ob = dict_obras.get(row["obra_id"], {})

                nome_c = colab.get("nome", "N/A")
                func_c = colab.get("funcao", "N/A")
                un_ob = ob.get("unidade", "GERAL")
                nome_ob = ob.get("nome", "N/A")
                eng_resp = row.get("engenheiro", "N/A")
                st_c = row.get("status", "Presente (Integral)")
                diaria_base = colab.get("valor_diaria", 240.0)
                d_calc = calcular_diaria_proporcional(st_c, diaria_base)
                ext_c = float(row.get("valor_extra") or 0.0)
                obs_c = row.get("observacao", "")

                ws.row_dimensions[current_row].height = 20

                r_cells = [
                    ws.cell(row=current_row, column=1, value=nome_c),
                    ws.cell(row=current_row, column=2, value=func_c),
                    ws.cell(row=current_row, column=3, value=un_ob),
                    ws.cell(row=current_row, column=4, value=nome_ob),
                    ws.cell(row=current_row, column=5, value=eng_resp),
                    ws.cell(row=current_row, column=6, value=st_c),
                    ws.cell(row=current_row, column=7, value=d_calc),
                    ws.cell(row=current_row, column=8, value=ext_c),
                    ws.cell(
                        row=current_row,
                        column=9,
                        value=f"=G{current_row}+H{current_row}",
                    ),
                    ws.cell(row=current_row, column=10, value=obs_c),
                ]

                cor_eng = eng_colors.get(eng_resp, "FFFFFF")
                fill_eng = PatternFill(
                    start_color=cor_eng, end_color=cor_eng, fill_type="solid"
                )

                for idx, cell in enumerate(r_cells, 1):
                  cell.font = font_body
                  cell.border = thin_border
                  if idx == 5:
                    cell.fill = fill_eng

                  if idx in [7, 8, 9]:
                    cell.number_format = "R$ #,##0.00"
                    cell.alignment = Alignment(
                        horizontal="right", vertical="center"
                    )
                  elif idx in [6]:
                    cell.alignment = Alignment(
                        horizontal="center", vertical="center"
                    )
                  else:
                    cell.alignment = Alignment(
                        horizontal="left", vertical="center"
                    )

                current_row += 1

              # Linha de Totais com Fórmula SUM
              total_row = current_row
              ws.row_dimensions[total_row].height = 22
              ws.merge_cells(
                  start_row=total_row,
                  start_column=1,
                  end_row=total_row,
                  end_column=6,
              )
              t_label = ws.cell(
                  row=total_row, column=1, value="TOTAL GERAL DO DIA"
              )
              t_label.font = font_total
              t_label.fill = fill_total
              t_label.alignment = Alignment(
                  horizontal="right", vertical="center"
              )

              for c_idx in range(1, 7):
                ws.cell(row=total_row, column=c_idx).border = thin_border
                ws.cell(row=total_row, column=c_idx).fill = fill_total

              sum_cols = [(7, "G"), (8, "H"), (9, "I")]
              for col_idx, col_let in sum_cols:
                cell = ws.cell(
                    row=total_row,
                    column=col_idx,
                    value=f"=SUM({col_let}5:{col_let}{total_row-1})",
                )
                cell.font = font_total
                cell.fill = fill_total
                cell.border = thin_border
                cell.number_format = "R$ #,##0.00"
                cell.alignment = Alignment(
                    horizontal="right", vertical="center"
                )

              obs_total_cell = ws.cell(row=total_row, column=10, value="")
              obs_total_cell.fill = fill_total
              obs_total_cell.border = thin_border

              # Ajustar largura das colunas automaticamente
              for col in ws.columns:
                max_len = 0
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                for cell in col:
                  if cell.row > 2:
                    val_str = str(cell.value or "")
                    if len(val_str) > max_len:
                      max_len = len(val_str)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

            wb.save(output)
            output.seek(0)

            st.download_button(
                label="📥 Baixar Relatório em Excel Estruturado",
                data=output,
                file_name=(
                    f"relatorio_custos_aproar_{data_inicio_rel}_a_{data_fim_rel}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True,
            )
        except Exception as e:
          st.error(f"Erro ao gerar Excel: {e}")

  elif menu == "👥 COLABORADORES":
    st.title("👥 Gestão de Colaboradores")
    st.write("Cadastro e consulta de equipe.")

  elif menu == "🏗️ OBRAS":
    st.title("🏗️ Cadastro de Obras e Unidades")
    st.write("Gerenciamento de obras e frentes de serviço.")


if __name__ == "__main__":
  main()
