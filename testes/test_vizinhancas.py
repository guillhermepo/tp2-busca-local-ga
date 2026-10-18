"""Testes das vizinhanças e da avaliação incremental."""

import os
import random

from src.problema import avaliar, carregar_instancia, solucao_aleatoria
from src.vizinhancas import (
    OPERADORES,
    aplicar_movimento,
    avaliar_vizinhos,
    gerar_vizinhos,
    sucessor_aleatorio,
    tamanho_vizinhanca,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar(nome):
    return carregar_instancia(os.path.join(RAIZ, "dados", f"manutencao_{nome}.txt"))


def test_exemplos_da_figura_3():
    s = [3, 7, 1, 5, 2, 8]
    assert aplicar_movimento(s, "swap", 1, 4) == [3, 2, 1, 5, 7, 8]
    assert aplicar_movimento(s, "insertion", 1, 4) == [3, 1, 5, 2, 7, 8]
    assert aplicar_movimento(s, "2opt", 1, 4) == [3, 2, 5, 1, 7, 8]
    assert s == [3, 7, 1, 5, 2, 8]  # a solução original não muda


def test_vizinhos_sao_permutacoes_distintas_e_diferentes_da_original():
    for n in range(2, 9):
        solucao = solucao_aleatoria(n, rng=n)
        for operador in OPERADORES:
            vizinhos = gerar_vizinhos(solucao, operador)
            for vizinho in vizinhos:
                assert sorted(vizinho) == list(range(1, n + 1))
                assert vizinho != solucao
            assert len(set(tuple(v) for v in vizinhos)) == len(vizinhos)


def test_tamanho_das_vizinhancas_por_enumeracao():
    # Fórmulas conferidas contra a enumeração feita pela implementação.
    formulas = {
        "swap": lambda n: n * (n - 1) // 2,
        "insertion": lambda n: (n - 1) ** 2,
        "2opt": lambda n: n * (n - 1) // 2,
    }
    for n in range(2, 9):
        solucao = list(range(1, n + 1))
        for operador in OPERADORES:
            distintos = set(tuple(v) for v in gerar_vizinhos(solucao, operador))
            assert len(distintos) == formulas[operador](n)
            assert tamanho_vizinhanca(n, operador) == formulas[operador](n)


def test_insertion_nao_perde_vizinhos_ao_excluir_repetidos():
    # Todos os pares i != j geram o mesmo conjunto que a vizinhança usada.
    solucao = [4, 1, 6, 2, 5, 3]
    todos = set()
    for i in range(6):
        for j in range(6):
            if i != j:
                todos.add(tuple(aplicar_movimento(solucao, "insertion", i, j)))
    usados = set(tuple(v) for v in gerar_vizinhos(solucao, "insertion"))
    assert usados == todos


def test_sucessor_aleatorio_pertence_a_vizinhanca():
    rng = random.Random(3)
    solucao = [5, 2, 7, 1, 3, 6, 4]
    for operador in OPERADORES:
        vizinhos = set(tuple(v) for v in gerar_vizinhos(solucao, operador))
        sorteados = set()
        for _ in range(3000):
            sorteados.add(tuple(sucessor_aleatorio(solucao, operador, rng)))
        assert sorteados <= vizinhos
        assert sorteados == vizinhos  # com 3000 sorteios, todos aparecem


def test_incremental_igual_a_completa_em_toda_a_vizinhanca_pequena():
    instancia = carregar("pequena")
    for semente in range(5):
        solucao = solucao_aleatoria(12, rng=semente)
        for operador in OPERADORES:
            for vizinho, h in avaliar_vizinhos(solucao, operador, instancia):
                assert h == avaliar(vizinho, instancia)


def test_incremental_igual_a_completa_na_media_e_grande():
    for nome, n in (("media", 50), ("grande", 150)):
        instancia = carregar(nome)
        solucao = solucao_aleatoria(n, rng=1)
        for operador in OPERADORES:
            rng = random.Random(2)
            for k, (vizinho, h) in enumerate(
                avaliar_vizinhos(solucao, operador, instancia, rng=rng)
            ):
                assert h == avaliar(vizinho, instancia)
                if k == 500:
                    break


def test_incremental_conta_uma_avaliacao_por_vizinho():
    instancia = carregar("pequena")
    solucao = list(range(1, 13))
    for incremental in (True, False):
        instancia["avaliacoes"] = 0
        total = sum(1 for _ in avaliar_vizinhos(solucao, "insertion", instancia,
                                                 incremental))
        assert total == tamanho_vizinhanca(12, "insertion")
        assert instancia["avaliacoes"] == total

