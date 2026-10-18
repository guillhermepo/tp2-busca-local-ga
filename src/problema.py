"""Leitura das instâncias, cálculo da função objetivo h e interface do problema."""

import math
import random

from src.vizinhancas import (
    avaliar_vizinhos,
    sucessor_aleatorio,
    tamanho_vizinhanca,
)


def carregar_instancia(caminho):
    """Lê um arquivo de instância e devolve os dados do problema."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        numeros = [int(valor) for valor in arquivo.read().split()]

    n = numeros[0]
    base = (numeros[1], numeros[2])

    if len(numeros) != 3 + 5 * n:
        raise ValueError(
            f"Arquivo {caminho} inconsistente: esperados {3 + 5 * n} números, "
            f"encontrados {len(numeros)}"
        )

    # A base usa o índice 0; os ativos começam em 1.
    ativos = [{"x": base[0], "y": base[1], "p": 0, "d": 0, "w": 0}]

    posicao = 3
    for _ in range(n):
        x, y, p, d, w = numeros[posicao:posicao + 5]
        ativos.append({"x": x, "y": y, "p": p, "d": d, "w": w})
        posicao += 5

    return {
        "n": n,
        "base": base,
        "ativos": ativos,
        "tempos": calcular_matriz_tempos(ativos),
    }


def instancia_exemplo_figura1():
    """Instância didática da Figura 1 do enunciado (n = 4, base em (0, 0))."""
    ativos = [
        {"x": 0, "y": 0, "p": 0, "d": 0, "w": 0},
        {"x": 3, "y": 4, "p": 2, "d": 10, "w": 3},
        {"x": 6, "y": 0, "p": 3, "d": 14, "w": 1},
        {"x": 0, "y": 8, "p": 1, "d": 25, "w": 2},
        {"x": 6, "y": 8, "p": 4, "d": 20, "w": 5},
    ]
    return {
        "n": 4,
        "base": (0, 0),
        "ativos": ativos,
        "tempos": calcular_matriz_tempos(ativos),
    }


def calcular_distancia(ponto_a, ponto_b):
    """Calcula o tempo de deslocamento euclidiano arredondado entre dois pontos."""
    dx = ponto_a[0] - ponto_b[0]
    dy = ponto_a[1] - ponto_b[1]
    return round(math.sqrt(dx * dx + dy * dy))


def calcular_matriz_tempos(ativos):
    """Calcula os tempos de deslocamento entre todos os pontos."""
    pontos = [(ativo["x"], ativo["y"]) for ativo in ativos]
    return [
        [calcular_distancia(origem, destino) for destino in pontos]
        for origem in pontos
    ]


def avaliar(solucao, instancia, inicio=0, tempo_inicial=0, custo_inicial=0,
            prefixos=None):
    """Calcula o atraso ponderado total h(solucao) sem contar no orçamento."""
    ativos = instancia["ativos"]
    tempos = instancia["tempos"]

    posicao_atual = 0 if inicio == 0 else solucao[inicio - 1]
    tempo_atual = tempo_inicial
    custo = custo_inicial

    for k in range(inicio, len(solucao)):
        ativo = solucao[k]
        info = ativos[ativo]

        tempo_atual += tempos[posicao_atual][ativo] + info["p"]
        atraso = tempo_atual - info["d"]
        if atraso > 0:
            custo += info["w"] * atraso

        if prefixos is not None:
            prefixos.append((tempo_atual, custo))

        posicao_atual = ativo

    return custo


def solucao_aleatoria(n, rng=None):
    """Gera uma permutação aleatória dos ativos 1..n."""
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    solucao = list(range(1, n + 1))
    rng.shuffle(solucao)
    return solucao


class Problema:
    """Interface do problema usada pelos algoritmos de busca."""

    def __init__(self, instancia, orcamento=None):
        self._instancia = instancia
        self.n = instancia["n"]
        self.orcamento = orcamento
        self.avaliacoes_usadas = 0

    def iniciar_orcamento(self, orcamento=None):
        """Reinicia o contador de avaliações e define o orçamento da execução."""
        if orcamento is not None:
            self.orcamento = orcamento
        self.avaliacoes_usadas = 0

    def orcamento_esgotado(self):
        """Indica se o limite de avaliações de h foi atingido."""
        return (self.orcamento is not None
                and self.avaliacoes_usadas >= self.orcamento)

    def solucao_aleatoria(self, rng=None):
        return solucao_aleatoria(self.n, rng)

    def avaliar(self, solucao, inicio=0, estado=None):
        """Avalia uma solução (completa ou incremental) contabilizando 1 avaliação."""
        self.avaliacoes_usadas += 1
        if estado is None:
            return avaliar(solucao, self._instancia, inicio=inicio)
        tempo_inicial, custo_inicial = estado
        return avaliar(solucao, self._instancia, inicio, tempo_inicial,
                       custo_inicial)

    def h(self, solucao):
        return self.avaliar(solucao)

    def estados_prefixo(self, solucao):
        """Retorna (tempo, custo) acumulados ao longo de solucao sem gastar avaliação."""
        prefixos = [(0, 0)]
        avaliar(solucao, self._instancia, prefixos=prefixos)
        return prefixos

    def sucessores(self, solucao, operador, incremental=True, rng=None):
        return avaliar_vizinhos(solucao, operador, self, incremental, rng)

    def sucessor_aleatorio(self, solucao, operador, rng=None):
        return sucessor_aleatorio(solucao, operador, rng)

    def tamanho_vizinhanca(self, operador):
        return tamanho_vizinhanca(self.n, operador)
