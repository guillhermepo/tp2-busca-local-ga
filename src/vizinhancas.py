"""Operadores de vizinhança sobre permutações e avaliação incremental."""

import random

OPERADORES = ("swap", "insertion", "2opt")


def movimentos(n, operador):
    """Lista os pares de índices (i, j) do operador sem gerar vizinhos repetidos."""
    lista = []
    if operador == "swap" or operador == "2opt":
        for i in range(n):
            for j in range(i + 1, n):
                lista.append((i, j))
    elif operador == "insertion":
        # Mover de i para i+1 produz a mesma permutação que mover de i+1 para i;
        # exclui-se j = i - 1 para evitar duplicatas.
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
    """Devolve uma nova permutação com o movimento (i, j) aplicado."""
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
    """Gera todos os vizinhos de solucao segundo o operador."""
    vizinhos = []
    for i, j in movimentos(len(solucao), operador):
        vizinhos.append(aplicar_movimento(solucao, operador, i, j))
    return vizinhos


def sucessor_aleatorio(solucao, operador, rng=None):
    """Sorteia uniformemente um vizinho sem construir toda a vizinhança."""
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


def avaliar_vizinhos(solucao, operador, problema, incremental=True, rng=None):
    """Gera pares (vizinho, h) sob demanda, reaproveitando o prefixo se incremental=True."""
    lista = movimentos(len(solucao), operador)

    # A solução corrente já foi avaliada; esta passada só monta
    # os estados do prefixo para a avaliação incremental.
    prefixos = problema.estados_prefixo(solucao) if incremental else None

    total = len(lista)
    for pos in range(total):
        if rng is not None:
            sorteado = rng.randrange(pos, total)
            lista[pos], lista[sorteado] = lista[sorteado], lista[pos]
        i, j = lista[pos]
        vizinho = aplicar_movimento(solucao, operador, i, j)
        if incremental:
            k = i if i < j else j
            h = problema.avaliar(vizinho, k, prefixos[k])
        else:
            h = problema.avaliar(vizinho)
        yield vizinho, h
