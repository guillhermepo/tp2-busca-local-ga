"""vizinhancas.py

Operadores de vizinhança sobre permutações e avaliação incremental.

Convenções:
- solucao é uma lista com uma permutação de 1..n.
- As funções NUNCA modificam a lista recebida: devolvem novas listas.
- Um movimento é um par de posições (i, j), com posições de 0 a n-1:

    swap      (i < j): troca os elementos das posições i e j.
    insertion (i != j): retira o elemento da posição i e o reinsere de
              modo que ele fique na posição j da nova lista.
    2opt      (i < j): inverte o trecho solucao[i..j].

  Exemplos da Figura 3 do enunciado, com i = 1 e j = 4:
    swap:      [3, 7, 1, 5, 2, 8] -> [3, 2, 1, 5, 7, 8]
    insertion: [3, 7, 1, 5, 2, 8] -> [3, 1, 5, 2, 7, 8]
    2opt:      [3, 2, 5, 1, 7, 8] a partir de [3, 7, 1, 5, 2, 8]

- Os três operadores alteram a solução só a partir da posição min(i, j):
  o prefixo anterior continua igual, e é isso que a avaliação incremental
  aproveita.
"""

import random

from src.problema import avaliar, avaliar_com_contagem

OPERADORES = ("swap", "insertion", "2opt")


def movimentos(n, operador):
    """Lista dos movimentos (i, j) do operador, sem vizinhos repetidos."""
    lista = []
    if operador == "swap" or operador == "2opt":
        for i in range(n):
            for j in range(i + 1, n):
                lista.append((i, j))
    elif operador == "insertion":
        # Levar o elemento de i para i+1 dá a mesma permutação que
        # levar o de i+1 para i (troca de vizinhos adjacentes).
        # Fica só a primeira forma; por isso j = i - 1 é excluído.
        for i in range(n):
            for j in range(n):
                if j != i and j != i - 1:
                    lista.append((i, j))
    else:
        raise ValueError(f"operador desconhecido: {operador}")
    return lista


def tamanho_vizinhanca(n, operador):
    """Quantidade de vizinhos gerados pela implementação."""
    return len(movimentos(n, operador))


def aplicar_movimento(solucao, operador, i, j):
    """Devolve uma nova lista com o movimento (i, j) aplicado."""
    vizinho = list(solucao)
    if operador == "swap":
        vizinho[i], vizinho[j] = vizinho[j], vizinho[i]
    elif operador == "insertion":
        ativo = vizinho.pop(i)
        vizinho.insert(j, ativo)
    elif operador == "2opt":
        vizinho[i:j + 1] = vizinho[i:j + 1][::-1]
    else:
        raise ValueError(f"operador desconhecido: {operador}")
    return vizinho


def gerar_vizinhos(solucao, operador):
    """Lista com todos os vizinhos de solucao pelo operador."""
    vizinhos = []
    for i, j in movimentos(len(solucao), operador):
        vizinhos.append(aplicar_movimento(solucao, operador, i, j))
    return vizinhos


def sucessor_aleatorio(solucao, operador, rng=None):
    """Sorteia um único vizinho, com a mesma probabilidade para todos.

    Sorteia o par (i, j) diretamente, sem montar a lista de movimentos
    (o Simulated Annealing chama esta função centenas de milhares de vezes).
    """
    if rng is None:
        rng = random.Random()
    n = len(solucao)
    while True:
        i, j = rng.sample(range(n), 2)
        if operador == "insertion":
            if j != i - 1:
                break
        else:
            if i > j:
                i, j = j, i
            break
    return aplicar_movimento(solucao, operador, i, j)


def avaliar_vizinhos(solucao, operador, instancia, incremental=True,
                     rng=None):
    """Percorre os vizinhos de solucao devolvendo (vizinho, h(vizinho)).

    É um gerador: cada vizinho só é montado e avaliado quando o algoritmo
    pede o próximo, então quem para no meio (First Improvement ou fim do
    orçamento) não gasta avaliações com o resto da vizinhança.
    Cada h devolvido conta 1 avaliação (problema.avaliar_com_contagem).

    rng: se for dado, os vizinhos são percorridos em ordem aleatória.

    incremental=True: o vizinho só difere de solucao a partir da posição
    k = min(i, j); o tempo e o custo acumulados até k são reaproveitados e
    apenas o sufixo é reavaliado.
    """
    lista = movimentos(len(solucao), operador)

    # prefixos[k] = (C, h acumulado) após os k primeiros ativos de solucao.
    # Esta passada não conta como avaliação: h(solucao) já foi contado quando
    # solucao foi avaliada, e a avaliação incremental não deve mudar o número
    # de avaliações em relação à completa (só o tempo).
    prefixos = [(0, 0)]
    if incremental:
        avaliar(solucao, instancia, prefixos=prefixos)

    total = len(lista)
    for pos in range(total):
        if rng is not None:
            # Sorteia o próximo movimento sob demanda (evita embaralhar
            # dezenas de milhares de pares quando o First Improvement para
            # logo nos primeiros).
            sorteado = rng.randrange(pos, total)
            lista[pos], lista[sorteado] = lista[sorteado], lista[pos]
        i, j = lista[pos]
        vizinho = aplicar_movimento(solucao, operador, i, j)
        if incremental:
            k = i if i < j else j
            tempo, custo = prefixos[k]
            h = avaliar_com_contagem(vizinho, instancia, k, tempo, custo)
        else:
            h = avaliar_com_contagem(vizinho, instancia)
        yield vizinho, h
