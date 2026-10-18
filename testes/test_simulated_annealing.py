"""Testes do simulated_annealing.py."""

import random

import pytest

from src.interface import ProblemaManutencao
from src.problema import avaliar
from src.simulated_annealing import calibrar_temperaturas, simulated_annealing


def rodar(instancia, orcamento, seed=1, operador="insertion", **kwargs):
    prob = ProblemaManutencao(instancia, operador)
    return prob, simulated_annealing(prob, orcamento, random.Random(seed),
                                     **kwargs)


@pytest.mark.parametrize("operador", ["swap", "insertion", "2opt"])
def test_respeita_orcamento_exatamente(pequena, operador):
    _, r = rodar(pequena, 5000, operador=operador)
    assert r["avaliacoes"] == 5000 == pequena["avaliacoes"]
    assert avaliar(r["melhor_solucao"], pequena) == r["melhor_h"]
    assert sorted(r["melhor_solucao"]) == list(range(1, 13))


def test_reprodutivel(pequena):
    _, r1 = rodar(pequena, 4000, seed=7)
    _, r2 = rodar(pequena, 4000, seed=7)
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["historico"] == r2["historico"]
    assert r1["taxa_aceitacao"] == r2["taxa_aceitacao"]


def test_encontra_bom_valor_na_pequena(pequena):
    _, r = rodar(pequena, 50_000)
    assert r["melhor_h"] <= 1937  # o ótimo é 1875


def test_calibracao_temperaturas(media):
    prob = ProblemaManutencao(media, "insertion")
    prob.zerar()
    from src.rastro import Rastro
    t0, tf, delta = calibrar_temperaturas(prob, random.Random(0), 100, 0.8,
                                          1e-3, Rastro())
    assert t0 > tf > 0
    assert delta > 0
    # com T0 calibrado, exp(-delta_medio/T0) = p0
    import math
    assert math.exp(-delta / t0) == pytest.approx(0.8)
    assert prob.avaliacoes == 101  # a calibração é contada no orçamento


def test_escala_da_temperatura_muda_com_a_instancia(pequena, grande):
    t = {}
    for nome, inst in (("pequena", pequena), ("grande", grande)):
        prob = ProblemaManutencao(inst, "insertion")
        prob.zerar()
        from src.rastro import Rastro
        t[nome] = calibrar_temperaturas(prob, random.Random(0), 100, 0.8,
                                        1e-3, Rastro())[0]
    assert t["grande"] > 5 * t["pequena"]


def test_taxa_de_aceitacao_cai_ao_longo_da_execucao(media):
    """Começa quase como random walk e termina quase como greedy descent."""
    _, r = rodar(media, 60_000)
    niveis = [n for n in r["taxa_aceitacao"] if n[2] > 0]
    ini, fim = niveis[: len(niveis) // 10], niveis[-len(niveis) // 10:]
    taxa = lambda ns: sum(n[3] for n in ns) / sum(n[2] for n in ns)
    assert taxa(ini) > 0.5
    assert taxa(fim) < 0.1
    assert taxa(ini) > taxa(fim)


def test_temperatura_decresce_geometricamente(pequena):
    _, r = rodar(pequena, 5000)
    temps = [n[1] for n in r["taxa_aceitacao"]]
    assert all(a > b for a, b in zip(temps, temps[1:]))
    razoes = {round(b / a, 9) for a, b in zip(temps, temps[1:])}
    assert len(razoes) == 1
    assert razoes.pop() == pytest.approx(r["alpha"], rel=1e-6)


def test_temperatura_muito_baixa_vira_descida(pequena):
    """Com T fixo ~0 nenhuma piora é aceita."""
    _, r = rodar(pequena, 3000, t0=1e-9, tf=1e-9)
    assert all(n[3] == 0 for n in r["taxa_aceitacao"])


def test_temperatura_muito_alta_aceita_quase_tudo(pequena):
    _, r = rodar(pequena, 3000, t0=1e12, tf=1e12)
    propostos = sum(n[2] for n in r["taxa_aceitacao"])
    aceitos = sum(n[3] for n in r["taxa_aceitacao"])
    assert aceitos / propostos > 0.99


def test_parametros_manuais_nao_gastam_calibracao(pequena):
    _, r = rodar(pequena, 1000, t0=100.0, tf=1.0)
    assert r["avaliacoes"] == 1000
    assert r["t0"] == 100.0 and r["tf"] == 1.0
