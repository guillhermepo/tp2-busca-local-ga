"""Greedy Descent (Best e First Improvement) com Random Restart."""

import random


def descida(problema, solucao_inicial, operador, estrategia, rng,
            incremental=True):
    """Executa uma descida gulosa a partir de solucao_inicial."""
    atual = solucao_inicial
    h_atual = problema.avaliar(atual)
    passos = 0
    trajetoria = [(problema.avaliacoes_usadas, h_atual)]
    tamanho = problema.tamanho_vizinhanca(operador)

    # No First Improvement a ordem é sorteada para não favorecer
    # sempre os primeiros movimentos.
    rng_ordem = rng if estrategia == "first" else None

    while True:
        if problema.orcamento_esgotado():
            return atual, h_atual, passos, False, trajetoria

        melhor_vizinho = None
        h_melhor_vizinho = h_atual
        avaliacoes_do_melhor = 0
        examinados = 0

        for vizinho, h_vizinho in problema.sucessores(
            atual, operador, incremental, rng_ordem
        ):
            examinados += 1

            if h_vizinho < h_melhor_vizinho:
                melhor_vizinho = vizinho
                h_melhor_vizinho = h_vizinho
                avaliacoes_do_melhor = problema.avaliacoes_usadas
                if estrategia == "first":
                    break

            if problema.orcamento_esgotado():
                break

        if melhor_vizinho is not None:
            atual = melhor_vizinho
            h_atual = h_melhor_vizinho
            passos += 1
            trajetoria.append((avaliacoes_do_melhor, h_atual))
        elif examinados == tamanho:
            return atual, h_atual, passos, True, trajetoria
        else:
            return atual, h_atual, passos, False, trajetoria


def greedy_random_restart(problema, operador, estrategia, orcamento=None,
                          rng=None, incremental=True):
    """Executa Greedy Descent com Random Restart até esgotar o orçamento."""
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    problema.iniciar_orcamento(orcamento)

    melhor_solucao = None
    melhor_h = None
    passos_total = 0
    descidas = 0
    otimos_locais = []
    historico = []

    while not problema.orcamento_esgotado():
        inicial = problema.solucao_aleatoria(rng)
        solucao, h, passos, otimo_local, trajetoria = descida(
            problema, inicial, operador, estrategia, rng, incremental
        )
        descidas += 1
        passos_total += passos

        if otimo_local:
            otimos_locais.append((solucao, h))

        for avaliacoes, h_passo in trajetoria:
            if melhor_h is None or h_passo < melhor_h:
                melhor_h = h_passo
                historico.append((avaliacoes, melhor_h))

        if h == melhor_h:
            melhor_solucao = solucao

    return {
        "melhor_solucao": melhor_solucao,
        "melhor_h": melhor_h,
        "avaliacoes": problema.avaliacoes_usadas,
        "passos": passos_total,
        "restarts": descidas - 1,
        "otimos_locais": otimos_locais,
        "historico": historico,
    }
