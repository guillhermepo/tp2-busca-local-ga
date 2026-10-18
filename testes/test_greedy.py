"""Testes do greedy.py."""

import os
import random

from src.greedy import greedy_random_restart
from src.problema import avaliar, carregar_instancia
from src.vizinhancas import OPERADORES, gerar_vizinhos

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_PEQUENA = os.path.join(RAIZ, "dados", "manutencao_pequena.txt")


def rodar(estrategia, orcamento, seed=1, operador="swap", incremental=True):
    instancia = carregar_instancia(CAMINHO_PEQUENA)
    resultado = greedy_random_restart(
        instancia, operador, estrategia, orcamento, random.Random(seed),
        incremental
    )
    return instancia, resultado


def test_greedy_respeita_orcamento_e_h_confere():
    for operador in OPERADORES:
        for estrategia in ("best", "first"):
            instancia, resultado = rodar(estrategia, 2000, operador=operador)
            assert resultado["avaliacoes"] == 2000  # para exatamente no orçamento
            assert resultado["avaliacoes"] == instancia["avaliacoes"]
            # o h guardado bate com uma reavaliação independente
            assert avaliar(resultado["melhor_solucao"], instancia) == resultado["melhor_h"]
            assert sorted(resultado["melhor_solucao"]) == list(range(1, 13))


def test_greedy_melhora_a_identidade():
    instancia, resultado = rodar("best", 5000)
    assert resultado["melhor_h"] < 4366


def test_greedy_ots_locais_sao_otimos_locais():
    for operador in OPERADORES:
        for estrategia in ("best", "first"):
            instancia, resultado = rodar(estrategia, 5000, operador=operador)
            assert len(resultado["otimos_locais"]) >= 1
            for solucao, h in resultado["otimos_locais"]:
                assert avaliar(solucao, instancia) == h
                for vizinho in gerar_vizinhos(solucao, operador):
                    assert avaliar(vizinho, instancia) >= h


def test_greedy_reprodutivel():
    _, r1 = rodar("first", 3000, seed=5)
    _, r2 = rodar("first", 3000, seed=5)
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["restarts"] == r2["restarts"]


def test_incremental_nao_muda_o_resultado():
    for operador in OPERADORES:
        for estrategia in ("best", "first"):
            _, r1 = rodar(estrategia, 4000, seed=2, operador=operador,
                          incremental=True)
            _, r2 = rodar(estrategia, 4000, seed=2, operador=operador,
                          incremental=False)
            assert r1["melhor_h"] == r2["melhor_h"]
            assert r1["avaliacoes"] == r2["avaliacoes"]
            assert r1["passos"] == r2["passos"]
            assert r1["historico"] == r2["historico"]


def test_historico_e_decrescente_e_termina_no_melhor():
    _, resultado = rodar("best", 5000)
    valores = [h for _, h in resultado["historico"]]
    assert valores == sorted(valores, reverse=True)
    assert valores[-1] == resultado["melhor_h"]
