"""Testes do módulo problema e do desacoplamento algoritmo != problema."""

import ast
import os
import random

from src.genetic_algorithm import genetic_algorithm
from src.greedy import greedy_random_restart
from src.problema import (
    Problema,
    avaliar,
    calcular_distancia,
    carregar_instancia,
    instancia_exemplo_figura1,
    solucao_aleatoria,
)
from src.simulated_annealing import simulated_annealing
from src.vizinhancas import (
    avaliar_vizinhos,
    sucessor_aleatorio,
    tamanho_vizinhanca,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_PEQUENA = os.path.join(RAIZ, "dados", "manutencao_pequena.txt")


def carregar_pequena():
    return carregar_instancia(CAMINHO_PEQUENA)


def test_instancia_pequena_tem_12_ativos():
    instancia = carregar_pequena()
    assert instancia["n"] == 12
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
    assert sorted(solucao) == list(range(1, n + 1))
    assert len(set(solucao)) == n


def test_solucao_aleatoria_reprodutivel_com_mesma_seed():
    assert solucao_aleatoria(50, rng=7) == solucao_aleatoria(50, rng=7)


def test_identidade_produz_4366():
    instancia = carregar_pequena()
    identidade = list(range(1, 13))
    assert avaliar(identidade, instancia) == 4366


def test_exemplo_figura_1_do_enunciado():
    instancia = instancia_exemplo_figura1()
    assert avaliar([1, 4, 2, 3], instancia) == 39
    assert avaliar([1, 4, 3, 2], instancia) == 22


def test_avaliacao_a_partir_de_um_prefixo():
    instancia = carregar_pequena()
    solucao = solucao_aleatoria(12, rng=3)
    prefixos = [(0, 0)]
    total = avaliar(solucao, instancia, prefixos=prefixos)
    assert prefixos[-1][1] == total
    for k in range(13):
        tempo, custo = prefixos[k]
        assert avaliar(solucao, instancia, k, tempo, custo) == total


def test_distancia_euclidiana_arredondada():
    assert calcular_distancia((0, 0), (3, 4)) == 5
    assert calcular_distancia((0, 0), (1, 1)) == 1
    assert calcular_distancia((0, 0), (2, 2)) == 3


def test_matriz_de_tempos_base_e_simetria():
    instancia = carregar_pequena()
    tempos = instancia["tempos"]
    assert len(tempos) == 13
    assert tempos[0][0] == 0
    assert tempos[0][1] == 34
    assert tempos[1][0] == tempos[0][1]


def test_contador_de_avaliacoes():
    instancia = carregar_pequena()
    problema = Problema(instancia, orcamento=3)
    identidade = list(range(1, 13))
    avaliar(identidade, instancia)
    assert problema.avaliacoes_usadas == 0
    problema.avaliar(identidade)
    problema.avaliar(identidade)
    assert problema.avaliacoes_usadas == 2
    assert not problema.orcamento_esgotado()
    problema.avaliar(identidade)
    assert problema.orcamento_esgotado()


class ProblemaPermutacaoSimples:
    """Problema sintético de permutação sem qualquer dado de manutenção."""

    def __init__(self, n=6, orcamento=100):
        self.n = n
        self.orcamento = orcamento
        self.avaliacoes_usadas = 0

    def iniciar_orcamento(self, orcamento=None):
        if orcamento is not None:
            self.orcamento = orcamento
        self.avaliacoes_usadas = 0

    def orcamento_esgotado(self):
        return (self.orcamento is not None
                and self.avaliacoes_usadas >= self.orcamento)

    def solucao_aleatoria(self, rng=None):
        return solucao_aleatoria(self.n, rng)

    def avaliar(self, solucao, inicio=0, estado=None):
        self.avaliacoes_usadas += 1
        custo = 0 if estado is None else estado
        for pos in range(inicio, len(solucao)):
            custo += (pos + 1) * solucao[pos]
        return custo

    def estados_prefixo(self, solucao):
        prefixos = [0]
        acumulado = 0
        for pos, valor in enumerate(solucao):
            acumulado += (pos + 1) * valor
            prefixos.append(acumulado)
        return prefixos

    def sucessores(self, solucao, operador, incremental=True, rng=None):
        return avaliar_vizinhos(solucao, operador, self, incremental, rng)

    def sucessor_aleatorio(self, solucao, operador, rng=None):
        return sucessor_aleatorio(solucao, operador, rng)

    def tamanho_vizinhanca(self, operador):
        return tamanho_vizinhanca(self.n, operador)


def test_algoritmos_nao_dependem_de_detalhes_da_instancia():
    for nome_arquivo in (
        "greedy.py",
        "simulated_annealing.py",
        "genetic_algorithm.py",
        "vizinhancas.py",
    ):
        caminho = os.path.join(RAIZ, "src", nome_arquivo)
        with open(caminho, "r", encoding="utf-8") as arq:
            arvore = ast.parse(arq.read())
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.module:
                assert "problema" not in no.module
            elif isinstance(no, ast.Import):
                for alias in no.names:
                    assert "problema" not in alias.name

    prob = ProblemaPermutacaoSimples(n=6, orcamento=80)
    rg = greedy_random_restart(prob, "swap", "first", 80, random.Random(1))
    assert rg["avaliacoes"] == 80

    rs = simulated_annealing(
        prob, "swap", 80, random.Random(1), t0=10.0, tf=0.01
    )
    assert rs["avaliacoes"] == 80

    rga = genetic_algorithm(
        prob, 80, random.Random(1), tamanho_populacao=10, tamanho_torneio=2,
        elites=1,
    )
    assert rga["avaliacoes"] == 80
