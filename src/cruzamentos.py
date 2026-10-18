"""cruzamentos.py

Operadores de recombinação que preservam a validade da permutação:
Order Crossover (OX) e Partially Mapped Crossover (PMX).

Cruzamentos clássicos de um ou múltiplos pontos duplicariam ativos; estes
dois sempre produzem permutações válidas.

Exemplo passo a passo do OX (pais de 8 ativos, corte nas posições 3..5):

    pai 1 = 1 2 3 | 4 5 6 | 7 8
    pai 2 = 3 7 5 | 2 6 8 | 1 4

    1. O filho 1 herda o trecho do pai 1:        _ _ _ 4 5 6 _ _
    2. Lê-se o pai 2 a partir da posição após o corte (6), de forma
       circular: 1 4 3 7 5 2 6 8. Descartam-se os ativos já presentes
       (4, 5, 6): sobram 1 3 7 2 8.
    3. Esses ativos preenchem as posições livres a partir da posição após o
       corte, também de forma circular (posições 6, 7, 0, 1, 2):
                                                 7 2 8 4 5 6 1 3
       Conferindo: posições 6,7,0,1,2 recebem 1, 3, 7, 2, 8 e o filho fica
                                                 7 2 8 4 5 6 1 3.
    O filho 2 é obtido trocando os papéis dos pais.

(O exemplo é verificado em testes/test_cruzamentos.py.)
"""


def _cortes(n, rng):
    """Sorteia dois cortes a <= b (posições inclusivas)."""
    a = rng.randrange(n)
    b = rng.randrange(n)
    return (a, b) if a <= b else (b, a)


def _filho_ox(pai_a, pai_b, a, b):
    n = len(pai_a)
    filho = [None] * n
    filho[a:b + 1] = pai_a[a:b + 1]
    presentes = set(pai_a[a:b + 1])
    # ativos de pai_b na ordem circular a partir de b+1, sem os já copiados
    restantes = [
        pai_b[(b + 1 + k) % n]
        for k in range(n)
        if pai_b[(b + 1 + k) % n] not in presentes
    ]
    for k, ativo in enumerate(restantes):
        filho[(b + 1 + k) % n] = ativo
    return filho


def ox(pai_1, pai_2, a, b):
    """Order Crossover com cortes explícitos a <= b. Devolve (filho1, filho2)."""
    return _filho_ox(pai_1, pai_2, a, b), _filho_ox(pai_2, pai_1, a, b)


def cruzamento_ox(pai_1, pai_2, rng):
    """OX com cortes sorteados por rng."""
    a, b = _cortes(len(pai_1), rng)
    return ox(pai_1, pai_2, a, b)


def _filho_pmx(pai_a, pai_b, a, b):
    n = len(pai_a)
    filho = [None] * n
    filho[a:b + 1] = pai_a[a:b + 1]
    segmento = set(pai_a[a:b + 1])
    posicao_em_b = {ativo: i for i, ativo in enumerate(pai_b)}
    for i in range(a, b + 1):
        ativo = pai_b[i]
        if ativo in segmento:
            continue
        # segue o mapeamento até achar uma posição fora do segmento
        pos = i
        while a <= pos <= b:
            pos = posicao_em_b[pai_a[pos]]
        filho[pos] = ativo
    for i in range(n):
        if filho[i] is None:
            filho[i] = pai_b[i]
    return filho


def pmx(pai_1, pai_2, a, b):
    """Partially Mapped Crossover com cortes explícitos a <= b."""
    return _filho_pmx(pai_1, pai_2, a, b), _filho_pmx(pai_2, pai_1, a, b)


def cruzamento_pmx(pai_1, pai_2, rng):
    """PMX com cortes sorteados por rng."""
    a, b = _cortes(len(pai_1), rng)
    return pmx(pai_1, pai_2, a, b)


CRUZAMENTOS = {"ox": cruzamento_ox, "pmx": cruzamento_pmx}
