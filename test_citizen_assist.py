import os
import tempfile
import unittest
from unittest.mock import patch

import citizen_assist as ca
from citizen_assist import ListaEncadeada, Servico, validar_id, validar_texto


def sv(i, titulo="Serviço teste", cat="Categoria A"):
    return Servico(i, titulo, cat, "Descrição de teste", "Nenhum", "Local X")


def ids(lista):
    return [s.id for s in lista.percorrer()]


class TestListaVazia(unittest.TestCase):
    def setUp(self):
        self.l = ListaEncadeada()

    def test_busca_remocao_ordenacao_em_lista_vazia(self):
        self.assertIsNone(self.l.buscar_por_id(1))
        self.assertFalse(self.l.remover(1))
        self.assertFalse(self.l.atualizar(1, titulo="Novo título"))
        self.l.ordenar(lambda s: s.id)
        self.assertTrue(self.l.esta_vazia())
        self.assertTrue(self.l.pesquisar("titulo", "x").esta_vazia())
        self.assertEqual(ca.contar_por_categoria(self.l), [])


class TestInsercaoBuscaRemocao(unittest.TestCase):
    def setUp(self):
        self.l = ListaEncadeada()
        for i in (3, 1, 2):
            self.l.inserir_fim(sv(i))

    def test_insercao_preserva_ordem_e_tamanho(self):
        self.assertEqual(ids(self.l), [3, 1, 2])
        self.assertEqual(self.l.tamanho, 3)

    def test_id_duplicado(self):
        with self.assertRaises(ValueError):
            self.l.inserir_fim(sv(1))
        self.assertEqual(self.l.tamanho, 3)

    def test_busca_por_id(self):
        self.assertEqual(self.l.buscar_por_id(2).id, 2)
        self.assertIsNone(self.l.buscar_por_id(99))

    def test_remover_cabeca_meio_cauda(self):
        self.assertTrue(self.l.remover(3));  self.assertEqual(ids(self.l), [1, 2])
        self.l.inserir_fim(sv(4))
        self.assertTrue(self.l.remover(2));  self.assertEqual(ids(self.l), [1, 4])
        self.assertTrue(self.l.remover(4));  self.assertEqual(ids(self.l), [1])
        self.l.inserir_fim(sv(5))            # cauda precisa estar consistente
        self.assertEqual(ids(self.l), [1, 5])
        self.assertFalse(self.l.remover(99))
        self.assertEqual(self.l.tamanho, 2)

    def test_remover_ate_esvaziar(self):
        for i in (3, 1, 2):
            self.assertTrue(self.l.remover(i))
        self.assertTrue(self.l.esta_vazia())
        self.assertIsNone(self.l.cauda)
        self.l.inserir_fim(sv(7))
        self.assertEqual(ids(self.l), [7])

    def test_atualizar(self):
        self.assertTrue(self.l.atualizar(1, titulo="Título novo", categoria="Outra"))
        self.assertEqual(self.l.buscar_por_id(1).titulo, "Título novo")

    def test_atualizar_invalido_nao_altera_nada(self):
        original = self.l.buscar_por_id(1).titulo
        with self.assertRaises(ValueError):
            self.l.atualizar(1, titulo="Válido ok", categoria="  ")
        self.assertEqual(self.l.buscar_por_id(1).titulo, original)
        with self.assertRaises(ValueError):
            self.l.atualizar(1, id=50)


class TestPesquisa(unittest.TestCase):
    def setUp(self):
        self.l = ListaEncadeada()
        self.l.inserir_fim(sv(1, "Delegacia da Mulher", "Violência doméstica"))
        self.l.inserir_fim(sv(2, "Defesa Civil", "Emergência"))
        self.l.inserir_fim(sv(3, "Polícia Militar", "Emergência"))

    def test_sem_acento_e_sem_maiusculas(self):
        self.assertEqual(ids(self.l.pesquisar("categoria", "EMERGENCIA")), [2, 3])
        self.assertEqual(ids(self.l.pesquisar("titulo", "policia")), [3])

    def test_sem_resultado(self):
        self.assertTrue(self.l.pesquisar("titulo", "inexistente").esta_vazia())


class TestOrdenacao(unittest.TestCase):
    def test_por_titulo_id_categoria(self):
        l = ListaEncadeada()
        l.inserir_fim(sv(3, "Zebra", "Cat B"))
        l.inserir_fim(sv(1, "Árvore", "Cat C"))
        l.inserir_fim(sv(2, "Banana", "Cat A"))
        l.ordenar(ca.CRITERIOS_ORDENACAO["2"][1]); self.assertEqual(ids(l), [1, 2, 3])
        l.ordenar(ca.CRITERIOS_ORDENACAO["1"][1]); self.assertEqual(ids(l), [1, 2, 3])
        l.ordenar(ca.CRITERIOS_ORDENACAO["3"][1]); self.assertEqual(ids(l), [2, 3, 1])
        self.assertEqual(l.tamanho, 3)

    def test_estabilidade_e_cauda_apos_ordenar(self):
        l = ListaEncadeada()
        for i in (5, 4, 3, 2, 1):
            l.inserir_fim(sv(i, f"Título {i}", "Mesma"))
        l.ordenar(lambda s: normalizar_cat(s))
        self.assertEqual(ids(l), [5, 4, 3, 2, 1])   # estável: ordem original preservada
        l.inserir_fim(sv(9))
        self.assertEqual(ids(l)[-1], 9)

    def test_lista_grande(self):
        l = ListaEncadeada()
        for i in range(500, 0, -1):
            l.inserir_fim(sv(i))
        l.ordenar(lambda s: s.id)
        self.assertEqual(ids(l), list(range(1, 501)))


def normalizar_cat(s):
    return ca.normalizar(s.categoria)


class TestValidacao(unittest.TestCase):
    def test_id_invalido(self):
        for ruim in ("", "   ", "abc", "-1", "0", "1.5", "1a"):
            with self.assertRaises(ValueError, msg=repr(ruim)):
                validar_id(ruim)
        self.assertEqual(validar_id(" 12 "), 12)

    def test_texto_invalido(self):
        with self.assertRaises(ValueError):
            validar_texto("", "campo")
        with self.assertRaises(ValueError):
            validar_texto("ab", "campo")
        with self.assertRaises(ValueError):
            validar_texto("x" * 500, "campo", 3, 80)

    def test_servico_invalido(self):
        with self.assertRaises(ValueError):
            Servico("x", "Título", "Cat", "Descrição", "Req", "Local")


class TestAnalise(unittest.TestCase):
    def test_contagem_por_categoria(self):
        l = ca.dados_iniciais()
        resultado = dict(ca.contar_por_categoria(l))
        self.assertEqual(sum(resultado.values()), l.tamanho)
        self.assertEqual(resultado["Emergência"], 3)


class TestMenuEPersistencia(unittest.TestCase):
    def rodar(self, entradas, arquivo=None):
        with patch("builtins.input", side_effect=entradas), patch("builtins.print") as p:
            ca.main(arquivo)
        return "\n".join(str(c.args[0]) if c.args else "" for c in p.call_args_list)

    def test_opcao_inexistente_e_encerrar(self):
        saida = self.rodar(["9", "abc", "", "0"])
        self.assertEqual(saida.count("Opção inexistente"), 3)

    def test_cadastro_com_id_duplicado_e_entradas_invalidas(self):
        saida = self.rodar(["1", "abc", "1", "100", "", "Novo serviço", "Cat X",
                            "Descrição ok", "Nenhum", "Local Y", "2", "100", "0"])
        self.assertIn("deve ser um número inteiro positivo", saida)
        self.assertIn("Já existe um registro com o ID 1", saida)
        self.assertIn("é obrigatório", saida)
        self.assertIn("Novo serviço", saida)

    def test_consulta_pesquisa_sem_resultado(self):
        saida = self.rodar(["2", "999", "5", "1", "zzzz", "5", "7", "0"])
        self.assertIn("Nenhum registro encontrado com esse ID", saida)
        self.assertIn("Nenhum registro encontrado para 'zzzz'", saida)
        self.assertIn("Opção inválida", saida)

    def test_excluir_e_cancelar(self):
        saida = self.rodar(["4", "1", "n", "4", "1", "s", "2", "1", "0"])
        self.assertIn("Exclusão cancelada", saida)
        self.assertIn("Registro removido", saida)

    def test_persistencia_e_arquivo_corrompido(self):
        with tempfile.TemporaryDirectory() as d:
            arq = os.path.join(d, "dados.json")
            self.rodar(["4", "1", "s", "0"], arq)
            recarregada = ca.carregar(arq)
            self.assertIsNone(recarregada.buscar_por_id(1))
            self.assertEqual(recarregada.tamanho, 7)
            with open(arq, "w", encoding="utf-8") as f:
                f.write("{lixo")
            self.assertIsNone(ca.carregar(arq))
            self.rodar(["0"], arq)   # não quebra: volta aos dados iniciais


if __name__ == "__main__":
    unittest.main(verbosity=2)
