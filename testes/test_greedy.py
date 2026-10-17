"""Testes do greedy.py.

Como vizinhancas.py ainda não existe, o teste define aqui uma vizinhança
swap simples só para verificar o algoritmo.
"""

import os
import random

from src.greedy import greedy_random_restart
from src.problema import avaliar, carregar_instancia

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_PEQUENA = os.path.join(RAIZ, "dados", "manutencao_pequena.txt")


def vizinhos_swap(solucao):
    """Todos os vizinhos por troca de duas posições (apenas para teste)."""
    vizinhos = []
    for i in range(len(solucao)):
        for j in range(i + 1, len(solucao)):
            vizinho = list(solucao)
            vizinho[i], vizinho[j] = vizinho[j], vizinho[i]
            vizinhos.append(vizinho)
    return vizinhos


def rodar(estrategia, orcamento, seed=1):
    instancia = carregar_instancia(CAMINHO_PEQUENA)
    resultado = greedy_random_restart(
        instancia, vizinhos_swap, estrategia, orcamento, random.Random(seed)
    )
    return instancia, resultado


def test_greedy_respeita_orcamento_e_h_confere():
    for estrategia in ("best", "first"):
        instancia, resultado = rodar(estrategia, 2000)
        assert resultado["avaliacoes"] <= 2000
        assert resultado["avaliacoes"] == instancia["avaliacoes"]
        # o h guardado bate com uma reavaliação independente
        assert avaliar(resultado["melhor_solucao"], instancia) == resultado["melhor_h"]
        assert sorted(resultado["melhor_solucao"]) == list(range(1, 13))


def test_greedy_melhora_a_identidade():
    instancia, resultado = rodar("best", 5000)
    assert resultado["melhor_h"] < 4366


def test_greedy_ots_locais_sao_otimos_locais():
    instancia, resultado = rodar("best", 5000)
    assert len(resultado["otimos_locais"]) >= 1
    for solucao, h in resultado["otimos_locais"]:
        for vizinho in vizinhos_swap(solucao):
            assert avaliar(vizinho, instancia) >= h


def test_greedy_reprodutivel():
    _, r1 = rodar("first", 3000, seed=5)
    _, r2 = rodar("first", 3000, seed=5)
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["restarts"] == r2["restarts"]
