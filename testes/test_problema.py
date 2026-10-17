"""Testes do módulo problema.

Execute a partir da raiz do projeto:  pytest   (ou  python -m pytest)
"""

import os

from src.problema import (
    avaliar,
    avaliar_com_contagem,
    calcular_distancia,
    carregar_instancia,
    solucao_aleatoria,
    zerar_contador,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_PEQUENA = os.path.join(RAIZ, "dados", "manutencao_pequena.txt")


def carregar_pequena():
    return carregar_instancia(CAMINHO_PEQUENA)


def test_instancia_pequena_tem_12_ativos():
    instancia = carregar_pequena()
    assert instancia["n"] == 12
    # lista de ativos tem n+1 posições (índice 0 = base)
    assert len(instancia["ativos"]) == 13


def test_base_da_instancia_pequena():
    instancia = carregar_pequena()
    assert instancia["base"] == (50, 50)


def test_primeiro_ativo_da_instancia_pequena():
    ativo = carregar_pequena()["ativos"][1]
    assert ativo["x"] == 78
    assert ativo["y"] == 31
    assert ativo["p"] == 2
    assert ativo["d"] == 118
    assert ativo["w"] == 2


def test_solucao_aleatoria_e_permutacao_valida():
    n = 12
    solucao = solucao_aleatoria(n, rng=42)
    assert len(solucao) == n
    assert sorted(solucao) == list(range(1, n + 1))  # todos de 1 a n
    assert len(set(solucao)) == n                    # sem repetições


def test_solucao_aleatoria_reprodutivel_com_mesma_seed():
    assert solucao_aleatoria(50, rng=7) == solucao_aleatoria(50, rng=7)


def test_identidade_produz_4366():
    """Teste mais importante: h([1, 2, ..., 12]) = 4366."""
    instancia = carregar_pequena()
    identidade = list(range(1, 13))
    assert avaliar(identidade, instancia) == 4366


def test_distancia_euclidiana_arredondada():
    assert calcular_distancia((0, 0), (3, 4)) == 5      # exata
    assert calcular_distancia((0, 0), (1, 1)) == 1      # 1,41 -> 1
    assert calcular_distancia((0, 0), (2, 2)) == 3      # 2,83 -> 3


def test_matriz_de_tempos_base_e_simetria():
    instancia = carregar_pequena()
    tempos = instancia["tempos"]
    assert len(tempos) == 13
    assert tempos[0][0] == 0
    # base (50,50) -> ativo 1 (78,31): sqrt(28^2 + 19^2) = 33,84 -> 34
    assert tempos[0][1] == 34
    assert tempos[1][0] == tempos[0][1]


def test_contador_de_avaliacoes():
    instancia = carregar_pequena()
    zerar_contador(instancia)
    identidade = list(range(1, 13))
    avaliar(identidade, instancia)            # não conta
    assert instancia["avaliacoes"] == 0
    avaliar_com_contagem(identidade, instancia)
    avaliar_com_contagem(identidade, instancia)
    assert instancia["avaliacoes"] == 2
