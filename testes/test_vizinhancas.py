"""Testes dos operadores de vizinhança."""

import random

import pytest

from src import vizinhancas as v


@pytest.mark.parametrize("operador", v.OPERADORES)
@pytest.mark.parametrize("n", [2, 3, 6, 12])
def test_tamanho_da_vizinhanca(operador, n):
    solucao = list(range(1, n + 1))
    vizinhos = v.gerar_vizinhos(solucao, operador)
    assert len(vizinhos) == v.tamanho_vizinhanca(n, operador)
    assert len(vizinhos) == len(v.movimentos(n, operador))


def test_formulas_de_tamanho():
    assert v.tamanho_vizinhanca(150, "swap") == 11175  # citado no enunciado
    assert v.tamanho_vizinhanca(150, "2opt") == 11175
    assert v.tamanho_vizinhanca(150, "insertion") == 149 ** 2
    assert v.tamanho_vizinhanca(1, "swap") == 0


@pytest.mark.parametrize("operador", v.OPERADORES)
def test_vizinhos_sao_permutacoes_distintas_da_original(operador):
    solucao = [3, 1, 4, 6, 2, 5]
    vizinhos = v.gerar_vizinhos(solucao, operador)
    for viz in vizinhos:
        assert sorted(viz) == [1, 2, 3, 4, 5, 6]
        assert viz != solucao
    assert len({tuple(x) for x in vizinhos}) == len(vizinhos)  # sem duplicatas


@pytest.mark.parametrize("operador", v.OPERADORES)
def test_nao_modifica_a_lista_recebida(operador):
    solucao = [3, 1, 4, 6, 2, 5]
    copia = list(solucao)
    v.gerar_vizinhos(solucao, operador)
    v.sucessor_aleatorio(solucao, operador, random.Random(1))
    assert solucao == copia


def test_exemplos_da_figura3():
    base = [3, 7, 1, 5, 2, 8]
    assert v.aplicar_movimento(base, (1, 4), "swap") == [3, 2, 1, 5, 7, 8]
    assert v.aplicar_movimento(base, (1, 4), "insertion") == [3, 1, 5, 2, 7, 8]
    assert v.aplicar_movimento(base, (1, 4), "2opt") == [3, 2, 5, 1, 7, 8]


def test_insertion_para_tras():
    assert v.aplicar_movimento([1, 2, 3, 4], (3, 0), "insertion") == [4, 1, 2, 3]


@pytest.mark.parametrize("operador", v.OPERADORES)
def test_sucessor_aleatorio_pertence_a_vizinhanca(operador):
    solucao = [3, 1, 4, 6, 2, 5]
    todos = {tuple(x) for x in v.gerar_vizinhos(solucao, operador)}
    rng = random.Random(0)
    for _ in range(200):
        assert tuple(v.sucessor_aleatorio(solucao, operador, rng)) in todos


@pytest.mark.parametrize("operador", v.OPERADORES)
def test_movimento_aleatorio_cobre_todos_os_movimentos(operador):
    rng = random.Random(0)
    n = 5
    vistos = {v.movimento_aleatorio(n, operador, rng) for _ in range(3000)}
    assert vistos == set(v.movimentos(n, operador))


@pytest.mark.parametrize("operador", v.OPERADORES)
def test_sucessor_aleatorio_com_semente_inteira(operador):
    a = v.sucessor_aleatorio(list(range(1, 9)), operador, 4)
    b = v.sucessor_aleatorio(list(range(1, 9)), operador, 4)
    assert a == b


def test_operador_invalido():
    with pytest.raises(ValueError):
        v.gerar_vizinhos([1, 2, 3], "3opt")


def test_menos_de_dois_ativos_nao_tem_vizinhos():
    assert v.gerar_vizinhos([1], "swap") == []
    with pytest.raises(ValueError):
        v.movimento_aleatorio(1, "swap", random.Random(0))
