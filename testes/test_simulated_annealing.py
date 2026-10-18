"""Testes do simulated_annealing.py."""

import os
import random

from src.problema import avaliar, carregar_instancia
from src.simulated_annealing import simulated_annealing

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar(nome):
    return carregar_instancia(os.path.join(RAIZ, "dados", f"manutencao_{nome}.txt"))


def test_sa_para_exatamente_no_orcamento_e_h_confere():
    instancia = carregar("pequena")
    for operador in ("swap", "insertion", "2opt"):
        resultado = simulated_annealing(instancia, operador, 3000, random.Random(1))
        assert resultado["avaliacoes"] == 3000
        assert instancia["avaliacoes"] == 3000
        assert avaliar(resultado["melhor_solucao"], instancia) == resultado["melhor_h"]
        assert sorted(resultado["melhor_solucao"]) == list(range(1, 13))


def test_sa_temperatura_decresce_de_t0_ate_tf():
    instancia = carregar("media")
    resultado = simulated_annealing(instancia, "insertion", 5000, random.Random(2))
    assert resultado["t0"] > resultado["tf"] > 0
    assert 0 < resultado["alfa"] < 1
    temperaturas = [t for _, t, _ in resultado["aceitacao"]]
    assert temperaturas == sorted(temperaturas, reverse=True)
    assert resultado["piores_aceitos"] <= resultado["piores_propostos"]


def test_sa_calibracao_acompanha_a_escala_da_instancia():
    t0 = {}
    for nome in ("pequena", "grande"):
        resultado = simulated_annealing(carregar(nome), "insertion", 2000,
                                        random.Random(0))
        t0[nome] = resultado["t0"]
    assert t0["grande"] > t0["pequena"]


def test_sa_reprodutivel():
    instancia = carregar("pequena")
    r1 = simulated_annealing(instancia, "swap", 2000, random.Random(7))
    r2 = simulated_annealing(instancia, "swap", 2000, random.Random(7))
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["historico"] == r2["historico"]

