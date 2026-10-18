"""Testes do simulated_annealing.py."""

import os
import random

from src.problema import Problema, avaliar, carregar_instancia
from src.simulated_annealing import calibrar_sa, simulated_annealing

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar(nome):
    return carregar_instancia(
        os.path.join(RAIZ, "dados", f"manutencao_{nome}.txt")
    )


def criar_problema(nome):
    return Problema(carregar(nome))


def test_sa_para_exatamente_no_orcamento_e_h_confere():
    instancia = carregar("pequena")
    problema = Problema(instancia)
    for operador in ("swap", "insertion", "2opt"):
        cal = calibrar_sa(problema, operador, 3000, random.Random(42))
        resultado = simulated_annealing(
            problema, operador, 3000, random.Random(1),
            t0=cal["t0"], tf=cal["tf"], alfa=cal["alfa"],
        )
        assert resultado["avaliacoes"] == 3000
        assert problema.avaliacoes_usadas == 3000
        assert avaliar(resultado["melhor_solucao"], instancia) == resultado["melhor_h"]
        assert sorted(resultado["melhor_solucao"]) == list(range(1, 13))


def test_sa_temperatura_decresce_de_t0_ate_tf():
    problema = criar_problema("media")
    cal = calibrar_sa(problema, "insertion", 5000, random.Random(2))
    resultado = simulated_annealing(
        problema, "insertion", 5000, random.Random(2),
        t0=cal["t0"], tf=cal["tf"], alfa=cal["alfa"],
    )
    assert resultado["t0"] > resultado["tf"] > 0
    assert 0 < resultado["alfa"] < 1
    temperaturas = [t for _, t, _ in resultado["aceitacao"]]
    assert temperaturas == sorted(temperaturas, reverse=True)
    assert resultado["piores_aceitos"] <= resultado["piores_propostos"]


def test_sa_calibracao_acompanha_a_escala_da_instancia():
    t0 = {}
    for nome in ("pequena", "grande"):
        cal = calibrar_sa(
            criar_problema(nome), "insertion", 2000, random.Random(0)
        )
        t0[nome] = cal["t0"]
    assert t0["grande"] > t0["pequena"]


def test_sa_reprodutivel():
    problema = criar_problema("pequena")
    cal = calibrar_sa(problema, "swap", 2000, random.Random(42))
    r1 = simulated_annealing(
        problema, "swap", 2000, random.Random(7),
        t0=cal["t0"], tf=cal["tf"], alfa=cal["alfa"],
    )
    r2 = simulated_annealing(
        problema, "swap", 2000, random.Random(7),
        t0=cal["t0"], tf=cal["tf"], alfa=cal["alfa"],
    )
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["historico"] == r2["historico"]


def test_sa_registra_ultima_janela_parcial():
    problema = criar_problema("pequena")
    # Com orcamento = 100, há 99 iterações; para janelas = 10, tamanho_janela = 9.
    # Se o número de iterações não for múltiplo de tamanho_janela (ex.: orcamento = 105,
    # iteracoes = 104, tamanho_janela = 10, sobram 4 iterações finais), a janela
    # parcial deve ser registrada ao final em avaliacoes == 105.
    resultado = simulated_annealing(
        problema, "insertion", orcamento=105, rng=random.Random(0),
        t0=500.0, tf=0.5, janelas=10,
    )
    assert resultado["avaliacoes"] == 105
    assert resultado["aceitacao"][-1][0] == 105
    assert len(resultado["aceitacao"]) == 11
