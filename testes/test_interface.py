"""Testes da interface ProblemaManutencao (algoritmo != problema)."""

import random

import pytest

from src import problema, vizinhancas
from src.interface import ProblemaManutencao


def test_h_conta_uma_avaliacao(pequena):
    prob = ProblemaManutencao(pequena)
    prob.zerar()
    s = list(range(1, 13))
    assert prob.h(s) == 4366
    assert prob.avaliacoes == 1


@pytest.mark.parametrize("operador", vizinhancas.OPERADORES)
@pytest.mark.parametrize("incremental", [True, False])
def test_sucessores_avaliados_corretamente(pequena, operador, incremental):
    prob = ProblemaManutencao(pequena, operador, incremental)
    prob.zerar()
    s = prob.solucao_aleatoria(random.Random(1))
    vistos = list(prob.sucessores(s))
    assert len(vistos) == prob.tamanho_vizinhanca()
    assert prob.avaliacoes == len(vistos)  # 1 avaliação por sucessor
    for viz, h in vistos:
        assert problema.avaliar(viz, pequena) == h


def test_sucessores_respeita_limite(pequena):
    prob = ProblemaManutencao(pequena)
    prob.zerar()
    s = prob.solucao_aleatoria(random.Random(1))
    assert len(list(prob.sucessores(s, limite=10))) == 10
    assert prob.avaliacoes == 10
    assert list(prob.sucessores(s, limite=10)) == []  # já no limite


def test_sucessores_em_ordem_aleatoria_mesmo_conjunto(pequena):
    prob = ProblemaManutencao(pequena)
    s = prob.solucao_aleatoria(random.Random(1))
    a = {tuple(v) for v, _ in prob.sucessores(s)}
    b = {tuple(v) for v, _ in prob.sucessores(s, rng=random.Random(3))}
    assert a == b


def test_cache_de_prefixos_troca_com_a_solucao(media):
    """Alternar entre soluções-base não pode reaproveitar prefixos errados."""
    prob = ProblemaManutencao(media, "insertion")
    rng = random.Random(0)
    s1 = prob.solucao_aleatoria(rng)
    s2 = prob.solucao_aleatoria(rng)
    for _ in range(50):
        for s in (s1, s2):
            viz, h = prob.sucessor_aleatorio(s, rng)
            assert h == problema.avaliar(viz, media)


def test_mutacao_devolve_permutacao_diferente(pequena):
    prob = ProblemaManutencao(pequena)
    rng = random.Random(0)
    s = prob.solucao_aleatoria(rng)
    copia = list(s)
    m = prob.mutacao(s, rng)
    assert s == copia and m != s and sorted(m) == sorted(s)


def test_mutacao_nao_avalia(pequena):
    prob = ProblemaManutencao(pequena)
    prob.zerar()
    prob.mutacao(prob.solucao_aleatoria(0), random.Random(0))
    prob.cruzamento(list(range(1, 13)), list(range(12, 0, -1)), random.Random(0))
    assert prob.avaliacoes == 0


def test_parametros_invalidos(pequena):
    with pytest.raises(ValueError):
        ProblemaManutencao(pequena, "3opt")
    with pytest.raises(ValueError):
        ProblemaManutencao(pequena, cruzamento="cx")
    with pytest.raises(ValueError):
        ProblemaManutencao(pequena, operador_mutacao="3opt")
