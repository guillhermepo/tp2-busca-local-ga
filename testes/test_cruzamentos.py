"""Testes dos cruzamentos OX e PMX."""

import random

import pytest

from src import cruzamentos as c


def test_exemplo_numerico_do_ox():
    """O exemplo passo a passo documentado em cruzamentos.py."""
    pai_1 = [1, 2, 3, 4, 5, 6, 7, 8]
    pai_2 = [3, 7, 5, 2, 6, 8, 1, 4]
    filho_1, filho_2 = c.ox(pai_1, pai_2, 3, 5)
    assert filho_1 == [7, 2, 8, 4, 5, 6, 1, 3]
    assert filho_2[3:6] == [2, 6, 8]  # herda o trecho do pai 2


def test_pmx_exemplo_classico():
    pai_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    pai_2 = [9, 3, 7, 8, 2, 6, 5, 1, 4]
    filho_1, filho_2 = c.pmx(pai_1, pai_2, 3, 6)
    assert filho_1 == [9, 3, 2, 4, 5, 6, 7, 1, 8]
    assert filho_2 == [1, 7, 3, 8, 2, 6, 5, 4, 9]


@pytest.mark.parametrize("nome", ["ox", "pmx"])
@pytest.mark.parametrize("n", [2, 3, 12, 50])
def test_filhos_sao_permutacoes_validas(nome, n):
    rng = random.Random(n)
    for _ in range(300):
        p1 = list(range(1, n + 1))
        p2 = list(range(1, n + 1))
        rng.shuffle(p1)
        rng.shuffle(p2)
        copia = (list(p1), list(p2))
        for filho in c.CRUZAMENTOS[nome](p1, p2, rng):
            assert sorted(filho) == list(range(1, n + 1))
        assert (p1, p2) == copia  # pais intactos


@pytest.mark.parametrize("nome", ["ox", "pmx"])
def test_cruzar_pais_iguais_devolve_o_mesmo(nome):
    rng = random.Random(0)
    pai = [4, 2, 5, 1, 3]
    f1, f2 = c.CRUZAMENTOS[nome](pai, list(pai), rng)
    assert f1 == pai and f2 == pai


def test_filho_herda_trecho_do_pai():
    rng = random.Random(3)
    for _ in range(100):
        p1 = rng.sample(range(1, 11), 10)
        p2 = rng.sample(range(1, 11), 10)
        for fn in (c.ox, c.pmx):
            f1, f2 = fn(p1, p2, 2, 6)
            assert f1[2:7] == p1[2:7]
            assert f2[2:7] == p2[2:7]
