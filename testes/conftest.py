"""Utilitários comuns dos testes."""

import os

import pytest

from src.problema import calcular_matriz_tempos, carregar_instancia

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def caminho(nome):
    return os.path.join(RAIZ, "dados", f"manutencao_{nome}.txt")


@pytest.fixture
def pequena():
    return carregar_instancia(caminho("pequena"))


@pytest.fixture
def media():
    return carregar_instancia(caminho("media"))


@pytest.fixture
def grande():
    return carregar_instancia(caminho("grande"))


@pytest.fixture
def exemplo_figura1():
    """Instância n = 4 da Figura 1 do enunciado (base em (0, 0)).

    Coordenadas deduzidas do cronograma da figura: t(0,1)=5, t(1,4)=5,
    t(4,2)=8, t(2,3)=10, t(4,3)=6.
    """
    ativos = [
        {"x": 0, "y": 0, "p": 0, "d": 0, "w": 0},
        {"x": 3, "y": 4, "p": 2, "d": 10, "w": 3},
        {"x": 6, "y": 0, "p": 3, "d": 14, "w": 1},
        {"x": 0, "y": 8, "p": 1, "d": 25, "w": 2},
        {"x": 6, "y": 8, "p": 4, "d": 20, "w": 5},
    ]
    return {"n": 4, "base": (0, 0), "ativos": ativos, "avaliacoes": 0,
            "tempos": calcular_matriz_tempos(ativos)}
