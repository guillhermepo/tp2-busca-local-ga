"""greedy.py

Greedy Descent com Random Restart.

Variantes de escolha do próximo sucessor:
- "best":  Best Improvement, varre a vizinhança inteira e vai para o melhor
           vizinho;
- "first": First Improvement, percorre a vizinhança em ordem aleatória e vai
           para o primeiro vizinho que melhora h.

Os vizinhos e seus valores de h vêm de vizinhancas.avaliar_vizinhos, que
avalia cada vizinho através de problema.avaliar_com_contagem. O orçamento é
conferido depois de cada avaliação, logo o total nunca passa do orçamento.

Uso:
    resultado = greedy_random_restart(instancia, "swap", "best", 50000, rng)
"""

import random

from src.problema import avaliar_com_contagem, solucao_aleatoria, zerar_contador
from src.vizinhancas import avaliar_vizinhos, tamanho_vizinhanca


def orcamento_esgotado(instancia, orcamento):
    """True se o número de avaliações já atingiu o orçamento."""
    return instancia["avaliacoes"] >= orcamento


def descida(instancia, solucao_inicial, operador, estrategia, orcamento, rng,
            incremental=True):
    """Uma descida gulosa a partir de solucao_inicial.

    Devolve (solucao, h, passos, otimo_local, trajetoria):
    - passos: quantidade de movimentos de melhoria feitos;
    - otimo_local: True se a descida terminou porque nenhum vizinho melhora
      a solução (vizinhança inteira avaliada). False se o orçamento acabou
      antes disso;
    - trajetoria: lista de (avaliacoes, h) da solução inicial e de cada
      melhoria, com o número de avaliações no momento em que ela foi
      encontrada (usada nas curvas de convergência).
    """
    atual = solucao_inicial
    h_atual = avaliar_com_contagem(atual, instancia)
    passos = 0
    trajetoria = [(instancia["avaliacoes"], h_atual)]
    tamanho = tamanho_vizinhanca(len(atual), operador)

    # No First Improvement a ordem dos vizinhos é sorteada, para não
    # favorecer sempre os movimentos nas primeiras posições.
    rng_ordem = rng if estrategia == "first" else None

    while True:
        if orcamento_esgotado(instancia, orcamento):
            return atual, h_atual, passos, False, trajetoria

        melhor_vizinho = None
        h_melhor_vizinho = h_atual
        avaliacoes_do_melhor = 0
        examinados = 0

        for vizinho, h_vizinho in avaliar_vizinhos(
            atual, operador, instancia, incremental, rng_ordem
        ):
            examinados += 1

            if h_vizinho < h_melhor_vizinho:
                melhor_vizinho = vizinho
                h_melhor_vizinho = h_vizinho
                avaliacoes_do_melhor = instancia["avaliacoes"]
                if estrategia == "first":
                    break  # aceita o primeiro que melhora

            if orcamento_esgotado(instancia, orcamento):
                break

        if melhor_vizinho is not None:
            atual = melhor_vizinho
            h_atual = h_melhor_vizinho
            passos += 1
            trajetoria.append((avaliacoes_do_melhor, h_atual))
        elif examinados == tamanho:
            # vizinhança inteira avaliada e nenhum vizinho melhora
            return atual, h_atual, passos, True, trajetoria
        else:
            # o orçamento acabou no meio da varredura
            return atual, h_atual, passos, False, trajetoria


def greedy_random_restart(instancia, operador, estrategia, orcamento,
                          rng=None, incremental=True):
    """Greedy Descent com Random Restart até gastar o orçamento.

    Zera o contador de avaliações da instância no início.
    Enquanto houver orçamento: sorteia uma solução inicial, desce até um
    ótimo local e recomeça.

    Devolve um dicionário com:
    - melhor_solucao, melhor_h
    - avaliacoes: total de avaliações usadas
    - passos: total de passos de melhoria (somando todas as descidas)
    - restarts: quantas vezes recomeçou (descidas - 1)
    - otimos_locais: lista de (solucao, h) de cada ótimo local encontrado
    - historico: lista de (avaliacoes, melhor_h) a cada nova melhor solução
      (útil para curvas de convergência)
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    zerar_contador(instancia)

    melhor_solucao = None
    melhor_h = None
    passos_total = 0
    descidas = 0
    otimos_locais = []
    historico = []

    while not orcamento_esgotado(instancia, orcamento):
        inicial = solucao_aleatoria(instancia["n"], rng)
        solucao, h, passos, otimo_local, trajetoria = descida(
            instancia, inicial, operador, estrategia, orcamento, rng,
            incremental
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
        "avaliacoes": instancia["avaliacoes"],
        "passos": passos_total,
        "restarts": descidas - 1,
        "otimos_locais": otimos_locais,
        "historico": historico,
    }
