"""Regressões do seletor 'Adicionar serviço' e rateio entre unidades, sem Neon/Streamlit."""
import ast
import pathlib
import unittest
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def carregar_funcao(nome, contexto):
    funcao = next(
        n for n in TREE.body
        if isinstance(n, ast.FunctionDef) and n.name == nome
    )
    bloco = ast.Module(body=[funcao], type_ignores=[])
    exec(compile(bloco, str(ROOT / "app.py"), "exec"), contexto)
    return contexto[nome]


def normalizar(valor):
    return "".join(
        c for c in unicodedata.normalize("NFD", str(valor or "").upper())
        if unicodedata.category(c) != "Mn"
    )


class TestCatalogoRateio(unittest.TestCase):
    def setUp(self):
        self.scope = {
            "normalizar": normalizar,
            "eh_obra_placeholder": lambda o: o.get("placeholder", False),
        }
        self.mapa = carregar_funcao(
            "mapa_obras_para_rateio_entre_unidades", self.scope
        )

    def test_obra_de_outra_unidade_fica_disponivel(self):
        obras = [
            {"id": 11, "nome": "Serviço 2700", "unidade": "Centro"},
            {"id": 22, "nome": "Serviço 2700", "unidade": "São Gonçalo"},
            {"id": 33, "nome": "Serviço 999", "unidade": "FIEC"},
            {"id": 44, "nome": "Temporário", "unidade": "FIEC", "placeholder": True},
        ]
        mapa = self.mapa(obras)
        self.assertEqual(set(mapa.values()), {11, 22, 33})
        self.assertTrue(any("Centro" in rotulo for rotulo in mapa))
        self.assertTrue(any("São Gonçalo" in rotulo for rotulo in mapa))

    def test_obras_com_nome_e_unidade_iguais_nao_se_sobrescrevem(self):
        obras = [
            {"id": 11, "nome": "Serviço A", "unidade": "Centro"},
            {"id": 22, "nome": "Serviço A", "unidade": "Centro"},
        ]
        mapa = self.mapa(obras)
        self.assertEqual(set(mapa.values()), {11, 22})
        self.assertEqual(len(mapa), 2)

    def test_obras_em_execucao_e_historicos_preservados(self):
        obras = [
            {"id": 1, "nome": "Ativa", "unidade": "Centro",
             "trello_card_id": "card-1", "trello_list_id": "em-execucao"},
            {"id": 2, "nome": "Encerrada", "unidade": "FIEC",
             "trello_card_id": "card-2", "trello_list_id": "finalizadas"},
            {"id": 3, "nome": "Manual", "unidade": "São Gonçalo"},
        ]
        atual = self.mapa(obras, "em-execucao")
        self.assertEqual(set(atual.values()), {1, 3})
        preservado = self.mapa(obras, "em-execucao", ids_preservar=["2"])
        self.assertEqual(set(preservado.values()), {1, 2, 3})

    def test_apenas_servico_adicional_usa_catalogo_geral(self):
        self.assertIn("mapa_obras_rateio.keys()", SOURCE)
        self.assertIn('"mapa_obras_rateio": mapa_obras_rateio', SOURCE)
        self.assertIn('item["mapa_obras_rateio"][servico_adic]', SOURCE)
        self.assertIn('item["mapa_obras_rateio"]\n', SOURCE)
        self.assertIn('obras_card = obras_reais_da_unidade(', SOURCE)


class TestRateioFabiano(unittest.TestCase):
    def test_duas_unidades_dividem_custo_sem_duplicar(self):
        scope = {
            "dict_colaboradores": {
                7: {"nome": "Fabiano", "funcao": "Pedreiro", "custo": 200}
            },
            "normalizar": normalizar,
            "normalizar_status_operacional": str,
            "normalizar_turno_convocacao": str,
            "status_eh_presenca": lambda s: s.startswith("Presente"),
            "tipo_diaria_registro": lambda r: "Não",
            "valor_diaria_financeiro_registro": lambda r, p: 100,
            "valor_financeiro_padrao_colaborador": lambda p, t: 100,
            "valor_controladoria_padrao_colaborador": lambda p, t: 0,
            "valor_adicional_noturno_registro": lambda r: 0,
            "valor_acordo_registro": lambda r: 0,
            "_valor_diario_controladoria_colaborador": lambda p: 200,
            "eh_unidade_sebrae": lambda x: False,
            "decompor_observacao_operacional": lambda x: ("Integral", ""),
            "aplica_periculosidade_controladoria": lambda p: 1,
            "numero_obra_relatorio": str,
            "turno_da_convocacao": lambda r: "Integral",
            "_peso_periodo_relatorio": lambda p: (
                {"M": 0.5} if p == "Manhã" else
                {"T": 0.5} if p == "Tarde" else
                {"M": 0.5, "T": 0.5}
            ),
            "_blocos_presenca_registro_relatorio": lambda r: {
                "M": 0.5, "T": 0.5
            },
            "_servicos_do_registro_relatorio": lambda r: [
                {"obra_id": "11", "obra": "Serviço A", "unidade": "Centro",
                 "periodo": "Manhã"},
                {"obra_id": "22", "obra": "Serviço B", "unidade": "São Gonçalo",
                 "periodo": "Tarde"},
            ],
        }
        ratear = carregar_funcao("ratear_registros_por_servico", scope)
        lancamento = {
            "data": "2026-11-17",
            "colaborador_id": 7,
            "status": "Presente (Integral)",
            "observacao": "",
            "engenheiro": "SUPERVISOR",
        }
        linhas = ratear([lancamento])
        self.assertEqual(len(linhas), 2)
        self.assertEqual({x["Unidade"] for x in linhas}, {"Centro", "São Gonçalo"})
        self.assertEqual(sum(x["Custo dia c/ encargos (R$)"] for x in linhas), 200)
        self.assertEqual(sum(x["Base Financeiro (R$)"] for x in linhas), 100)
        self.assertEqual(
            {x["Unidade"]: x["Custo dia c/ encargos (R$)"] for x in linhas},
            {"Centro": 100, "São Gonçalo": 100},
        )


if __name__ == "__main__":
    unittest.main()
