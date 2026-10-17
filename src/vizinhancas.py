"""vizinhancas.py

Operadores de vizinhança sobre permutações.

STATUS: ainda NÃO implementado. Este módulo será desenvolvido principalmente
por outro integrante do grupo. Aqui ficam apenas as assinaturas esperadas,
para que greedy.py, o Simulated Annealing e o experimentos.py possam
ser integrados depois.

Convenções:
- solucao é uma lista com uma permutação de 1..n.
- As funções NUNCA devem modificar a lista recebida: devolvem novas listas.
- Gerar vizinhos NÃO avalia h. Quem avalia (e conta) é o algoritmo, usando
  problema.avaliar_com_contagem.
"""

OPERADORES = ("swap", "insertion", "2opt")


def gerar_vizinhos(solucao, operador):
    """Devolve a lista com TODOS os vizinhos de solucao pelo operador.

    operador: "swap", "insertion" ou "2opt".

    TODO (outro integrante):
    - swap: troca as posições i e j (i < j).
    - insertion: remove o elemento da posição i e o insere na posição j.
    - 2opt: inverte o trecho solucao[i..j].
    """
    raise NotImplementedError("gerar_vizinhos ainda não foi implementado")


def sucessor_aleatorio(solucao, operador, rng=None):
    """Devolve UM vizinho aleatório de solucao pelo operador.

    rng: objeto random.Random (para reprodutibilidade). Usado pelo
    Simulated Annealing.

    TODO (outro integrante).
    """
    raise NotImplementedError("sucessor_aleatorio ainda não foi implementado")
