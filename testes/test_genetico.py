"""Testes do genetico.py."""

import random

import pytest

from src.genetico import algoritmo_genetico
from src.interface import ProblemaManutencao
from src.problema import avaliar


def rodar(instancia, orcamento, seed=1, cruzamento="ox", **kwargs):
    prob = ProblemaManutencao(instancia, "swap", cruzamento=cruzamento)
    return prob, algoritmo_genetico(prob, orcamento, random.Random(seed),
                                    **kwargs)


@pytest.mark.parametrize("cruzamento", ["ox", "pmx"])
@pytest.mark.parametrize("selecao", ["torneio", "roleta"])
def test_respeita_orcamento_e_h_confere(pequena, cruzamento, selecao):
    _, r = rodar(pequena, 4000, cruzamento=cruzamento, selecao=selecao)
    assert r["avaliacoes"] == 4000 == pequena["avaliacoes"]
    assert avaliar(r["melhor_solucao"], pequena) == r["melhor_h"]
    assert sorted(r["melhor_solucao"]) == list(range(1, 13))


def test_orcamento_que_termina_no_meio_de_uma_geracao(pequena):
    _, r = rodar(pequena, 1234, tamanho_populacao=50)
    assert r["avaliacoes"] == 1234


def test_orcamento_menor_que_a_populacao(pequena):
    _, r = rodar(pequena, 30, tamanho_populacao=50)
    assert r["avaliacoes"] == 30
    assert r["melhor_h"] is not None


def test_reprodutivel(pequena):
    _, r1 = rodar(pequena, 3000, seed=4)
    _, r2 = rodar(pequena, 3000, seed=4)
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["geracoes"] == r2["geracoes"]


def test_elitismo_melhor_da_populacao_nunca_piora(pequena):
    _, r = rodar(pequena, 10_000, elite=2)
    melhores = [g["melhor_h"] for g in r["geracoes"][:-1]]  # última pode ser parcial
    assert all(a >= b for a, b in zip(melhores, melhores[1:]))


def test_historico_decrescente(pequena):
    _, r = rodar(pequena, 5000)
    hs = [h for _, h in r["historico"]]
    assert hs == sorted(hs, reverse=True)
    assert hs[-1] == r["melhor_h"]


def test_registra_diversidade_por_geracao(pequena):
    _, r = rodar(pequena, 5000, tamanho_populacao=50)
    ger = r["geracoes"]
    assert len(ger) >= 2
    assert ger[0]["distintos"] <= 50
    assert ger[0]["distintos"] > 40  # população aleatória inicial
    assert 0 <= ger[0]["distancia_media"] <= 1
    # a população perde diversidade ao longo das gerações
    assert ger[-1]["distancia_media"] < ger[0]["distancia_media"]
    assert ger[-1]["media_h"] < ger[0]["media_h"]


def test_sem_cruzamento_nem_mutacao_populacao_so_herda(pequena):
    _, r = rodar(pequena, 3000, pc=0.0, pm=0.0, tamanho_populacao=20)
    assert r["geracoes"][-1]["distintos"] <= r["geracoes"][0]["distintos"]


def test_encontra_bom_valor_na_pequena(pequena):
    _, r = rodar(pequena, 50_000)
    assert r["melhor_h"] <= 2100


def test_parametros_invalidos(pequena):
    prob = ProblemaManutencao(pequena)
    with pytest.raises(ValueError):
        algoritmo_genetico(prob, 100, 0, selecao="sorteio")
    with pytest.raises(ValueError):
        algoritmo_genetico(prob, 100, 0, tamanho_populacao=1)
    with pytest.raises(ValueError):
        algoritmo_genetico(prob, 100, 0, tamanho_populacao=5, elite=5)
