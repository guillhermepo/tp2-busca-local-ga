"""Testes do genetic_algorithm.py."""

import os
import random

from src.genetic_algorithm import (
    diversidade,
    genetic_algorithm,
    order_crossover,
    swap_mutation,
)
from src.problema import Problema, avaliar, carregar_instancia

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar(nome):
    return carregar_instancia(
        os.path.join(RAIZ, "dados", f"manutencao_{nome}.txt")
    )


class CortesFixos:
    """Imita random.Random para fixar os cortes do OX no exemplo."""

    def sample(self, populacao, k):
        return [4, 2]


def test_ox_exemplo_da_documentacao():
    pai1 = [1, 2, 3, 4, 5, 6, 7]
    pai2 = [5, 7, 4, 1, 6, 3, 2]
    assert order_crossover(pai1, pai2, CortesFixos()) == [1, 6, 3, 4, 5, 2, 7]


def test_ox_e_mutacao_geram_permutacoes_validas():
    rng = random.Random(0)
    for n in (2, 5, 12, 50):
        for _ in range(200):
            pai1 = rng.sample(range(1, n + 1), n)
            pai2 = rng.sample(range(1, n + 1), n)
            filho = order_crossover(pai1, pai2, rng)
            assert sorted(filho) == list(range(1, n + 1))
            mutante = swap_mutation(filho, rng)
            assert sorted(mutante) == list(range(1, n + 1))
            assert sum(a != b for a, b in zip(filho, mutante)) == 2


def test_diversidade():
    iguais = [([1, 2, 3, 4], 0)] * 3
    assert diversidade(iguais) == (1, 0.0)
    opostos = [([1, 2, 3, 4], 0), ([2, 1, 4, 3], 0)]
    assert diversidade(opostos) == (2, 1.0)


def test_ga_para_exatamente_no_orcamento_e_h_confere():
    instancia = carregar("pequena")
    problema = Problema(instancia)
    for orcamento in (1000, 1037):
        resultado = genetic_algorithm(
            problema, orcamento, random.Random(1), tamanho_populacao=30
        )
        assert resultado["avaliacoes"] == orcamento
        assert problema.avaliacoes_usadas == orcamento
        assert avaliar(resultado["melhor_solucao"], instancia) == resultado["melhor_h"]
        assert sorted(resultado["melhor_solucao"]) == list(range(1, 13))


def test_ga_sem_cruzamento_tambem_respeita_orcamento():
    instancia = carregar("pequena")
    problema = Problema(instancia)
    resultado = genetic_algorithm(
        problema, 1000, random.Random(3), tamanho_populacao=20, pc=0.0
    )
    assert resultado["avaliacoes"] == 1000
    assert avaliar(resultado["melhor_solucao"], instancia) == resultado["melhor_h"]


def test_ga_elitismo_nunca_piora_o_melhor_da_populacao():
    instancia = carregar("media")
    problema = Problema(instancia)
    resultado = genetic_algorithm(
        problema, 3000, random.Random(4), tamanho_populacao=40
    )
    melhores = [g["melhor_h"] for g in resultado["geracoes_info"]]
    assert melhores == sorted(melhores, reverse=True)
    assert resultado["melhor_h"] <= melhores[-1]


def test_ga_nao_registra_geracao_parcial_como_completa():
    instancia = carregar("pequena")
    problema = Problema(instancia)
    # População = 20, elites = 2, pc = 1.0, pm = 1.0 -> toda geração completa
    # consome 18 avaliações novas (geração 0 = 20, geração 1 = 38, geração 2 = 56).
    # Com orçamento = 45, a geração 2 para no meio (após 7 filhos avaliados).
    resultado = genetic_algorithm(
        problema, orcamento=45, rng=random.Random(10),
        tamanho_populacao=20, pc=1.0, pm=1.0, tamanho_torneio=2, elites=2,
    )
    assert resultado["avaliacoes"] == 45
    assert resultado["geracoes"] == 1
    assert [g["geracao"] for g in resultado["geracoes_info"]] == [0, 1]
    assert resultado["geracoes_info"][-1]["avaliacoes"] == 38
