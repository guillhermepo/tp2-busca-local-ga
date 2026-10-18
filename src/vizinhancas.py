"""vizinhancas.py

Operadores de vizinhança sobre permutações: swap, insertion e 2-opt.

Um MOVIMENTO é uma tupla (i, j) de posições (0-based) na permutação; o
significado depende do operador:

- swap:      troca os elementos das posições i e j (i < j).
- insertion: remove o elemento da posição i e o reinsere de modo que passe a
             ocupar a posição j (i != j).
- 2opt:      inverte o trecho solucao[i..j] (i < j).

Tamanho da vizinhança em função de n (quantidade de ativos):

- swap:      n(n-1)/2
- insertion: (n-1)^2   (os n(n-1) pares (i, j) geram cada troca de vizinhos
                        adjacentes duas vezes; o duplicado é descartado)
- 2opt:      n(n-1)/2  (os n-1 movimentos com j = i+1 coincidem com swaps
                        adjacentes; são mantidos por ser a definição clássica)

Convenções:
- solucao é uma lista com uma permutação de 1..n.
- As funções NUNCA modificam a lista recebida: devolvem novas listas.
- Gerar vizinhos NÃO avalia h. Quem avalia (e conta) é o algoritmo.
"""

import random

OPERADORES = ("swap", "insertion", "2opt")


def _validar_operador(operador):
    if operador not in OPERADORES:
        raise ValueError(
            f"operador inválido: {operador!r}; use um de {OPERADORES}"
        )


def tamanho_vizinhanca(n, operador):
    """Número de vizinhos de uma permutação de tamanho n."""
    _validar_operador(operador)
    if n < 2:
        return 0
    if operador == "insertion":
        return (n - 1) ** 2
    return n * (n - 1) // 2


def movimentos(n, operador):
    """Lista de todos os movimentos (i, j) válidos do operador."""
    _validar_operador(operador)
    if operador == "insertion":
        return [
            (i, j)
            for i in range(n)
            for j in range(n)
            if j != i and j != i - 1
        ]
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def movimento_aleatorio(n, operador, rng):
    """Sorteia, uniformemente, um dos movimentos do operador."""
    _validar_operador(operador)
    if n < 2:
        raise ValueError("é preciso ao menos 2 ativos para gerar um vizinho")
    if operador == "insertion":
        # j != i e j != i-1; sorteia entre as n-2 posições restantes
        # (n-1 quando i = 0, já que i-1 não existe).
        i = rng.randrange(n)
        while True:
            j = rng.randrange(n)
            if j != i and j != i - 1:
                return i, j
    i = rng.randrange(n)
    j = rng.randrange(n - 1)
    if j >= i:
        j += 1
    return (i, j) if i < j else (j, i)


def aplicar_movimento(solucao, movimento, operador):
    """Devolve uma NOVA lista com o movimento aplicado."""
    i, j = movimento
    vizinho = list(solucao)
    if operador == "swap":
        vizinho[i], vizinho[j] = vizinho[j], vizinho[i]
    elif operador == "insertion":
        elemento = vizinho.pop(i)
        vizinho.insert(j, elemento)
    elif operador == "2opt":
        vizinho[i:j + 1] = vizinho[i:j + 1][::-1]
    else:
        _validar_operador(operador)
    return vizinho


def primeira_posicao_afetada(movimento, operador):
    """Menor posição cujo conteúdo muda: o prefixo anterior fica intacto."""
    return min(movimento)


def gerar_vizinhos(solucao, operador):
    """Devolve a lista com TODOS os vizinhos de solucao pelo operador."""
    n = len(solucao)
    return [
        aplicar_movimento(solucao, mov, operador)
        for mov in movimentos(n, operador)
    ]


def sucessor_aleatorio(solucao, operador, rng=None):
    """Devolve UM vizinho aleatório de solucao pelo operador.

    rng: random.Random, inteiro (semente) ou None.
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)
    movimento = movimento_aleatorio(len(solucao), operador, rng)
    return aplicar_movimento(solucao, movimento, operador)
