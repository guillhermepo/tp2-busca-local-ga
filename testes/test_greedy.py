"""Testes do greedy.py (Greedy Descent com Random Restart)."""

import random

import pytest

from src import vizinhancas
from src.greedy import ESTRATEGIAS, descida, greedy_random_restart
from src.interface import ProblemaManutencao
from src.problema import avaliar, zerar_contador
from src.rastro import Rastro


def rodar(instancia, estrategia, orcamento, seed=1, operador="swap",
          incremental=True):
    prob = ProblemaManutencao(instancia, operador, incremental)
    return prob, greedy_random_restart(
        prob, estrategia, orcamento, random.Random(seed))


@pytest.mark.parametrize("estrategia", ESTRATEGIAS)
@pytest.mark.parametrize("operador", vizinhancas.OPERADORES)
def test_respeita_orcamento_exatamente_e_h_confere(pequena, estrategia,
                                                   operador):
    prob, r = rodar(pequena, estrategia, 2000, operador=operador)
    assert r["avaliacoes"] == 2000  # para exatamente ao atingir o orçamento
    assert r["avaliacoes"] == pequena["avaliacoes"]
    assert avaliar(r["melhor_solucao"], pequena) == r["melhor_h"]
    assert sorted(r["melhor_solucao"]) == list(range(1, 13))


@pytest.mark.parametrize("estrategia", ESTRATEGIAS)
def test_melhora_a_identidade(pequena, estrategia):
    _, r = rodar(pequena, estrategia, 5000)
    assert r["melhor_h"] < 4366


@pytest.mark.parametrize("estrategia", ["best", "first"])
@pytest.mark.parametrize("operador", vizinhancas.OPERADORES)
def test_otimos_locais_sao_otimos_locais(pequena, estrategia, operador):
    _, r = rodar(pequena, estrategia, 8000, operador=operador)
    assert len(r["otimos_locais"]) >= 1
    for solucao, h in r["otimos_locais"]:
        assert avaliar(solucao, pequena) == h
        for viz in vizinhancas.gerar_vizinhos(solucao, operador):
            assert avaliar(viz, pequena) >= h


@pytest.mark.parametrize("estrategia", ESTRATEGIAS)
def test_reprodutivel(pequena, estrategia):
    _, r1 = rodar(pequena, estrategia, 3000, seed=5)
    _, r2 = rodar(pequena, estrategia, 3000, seed=5)
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["restarts"] == r2["restarts"]
    assert r1["historico"] == r2["historico"]


@pytest.mark.parametrize("estrategia", ESTRATEGIAS)
def test_incremental_nao_muda_o_comportamento(pequena, estrategia):
    """Mesmas decisões, mesmas avaliações: só muda o tempo."""
    _, r1 = rodar(pequena, estrategia, 3000, seed=9, incremental=True)
    _, r2 = rodar(pequena, estrategia, 3000, seed=9, incremental=False)
    assert r1["melhor_h"] == r2["melhor_h"]
    assert r1["passos"] == r2["passos"]
    assert r1["historico"] == r2["historico"]


def test_historico_e_decrescente_e_termina_no_melhor(pequena):
    _, r = rodar(pequena, "first", 5000)
    hs = [h for _, h in r["historico"]]
    avs = [a for a, _ in r["historico"]]
    assert hs == sorted(hs, reverse=True) and len(set(hs)) == len(hs)
    assert avs == sorted(avs)
    assert hs[-1] == r["melhor_h"]
    assert avs[-1] <= r["avaliacoes"]


def test_best_improvement_gasta_uma_varredura_por_passo(pequena):
    """Um passo do best improvement custa exatamente |N| avaliações."""
    prob = ProblemaManutencao(pequena, "swap")
    prob.zerar()
    inicial = prob.solucao_aleatoria(random.Random(2))
    rastro = Rastro()
    _, _, passos, otimo = descida(prob, inicial, "best", 10 ** 9,
                                  random.Random(0), rastro)
    assert otimo
    # 1 avaliação inicial + (passos + 1) varreduras completas
    assert pequena["avaliacoes"] == 1 + (passos + 1) * prob.tamanho_vizinhanca()


def test_orcamento_muito_pequeno(pequena):
    for estrategia in ESTRATEGIAS:
        _, r = rodar(pequena, estrategia, 1)
        assert r["avaliacoes"] == 1
        assert r["melhor_h"] is not None


def test_best_cortado_pelo_orcamento_nao_e_marcado_como_otimo_local(pequena):
    prob = ProblemaManutencao(pequena, "swap")
    prob.zerar()
    inicial = prob.solucao_aleatoria(random.Random(2))
    _, _, _, otimo = descida(prob, inicial, "best", 30, random.Random(0),
                             Rastro())
    assert not otimo
    assert pequena["avaliacoes"] == 30


def test_estrategia_invalida(pequena):
    prob = ProblemaManutencao(pequena)
    with pytest.raises(ValueError):
        greedy_random_restart(prob, "otima", 100, 0)


def test_semente_inteira_aceita(pequena):
    prob = ProblemaManutencao(pequena)
    r = greedy_random_restart(prob, "first", 1000, 3)
    assert r["avaliacoes"] == 1000


def test_zerar_contador_reinicia_execucao(pequena):
    zerar_contador(pequena)
    prob = ProblemaManutencao(pequena)
    greedy_random_restart(prob, "first", 500, 1)
    r = greedy_random_restart(prob, "first", 500, 1)
    assert r["avaliacoes"] == 500  # contador reiniciado, não acumulado
