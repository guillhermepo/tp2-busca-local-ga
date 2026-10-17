"""greedy.py

Greedy Descent com Random Restart.

Para NÃO depender de vizinhancas.py (ainda em desenvolvimento por outro
integrante), as funções recebem `gerar_vizinhos`: uma função que recebe
uma solução e devolve a lista de todos os vizinhos dela. Quando
vizinhancas.py estiver pronto, basta passar, por exemplo:

    from src.vizinhancas import gerar_vizinhos
    vizinhos = lambda s: gerar_vizinhos(s, "swap")
    resultado = greedy_random_restart(instancia, vizinhos, "best", 50000, rng)

Contagem de avaliações: todas as avaliações passam por
problema.avaliar_com_contagem. O orçamento é conferido ANTES de cada
avaliação, logo o total nunca ultrapassa o orçamento.
"""

import random

from src.problema import avaliar_com_contagem, solucao_aleatoria, zerar_contador


def orcamento_esgotado(instancia, orcamento):
    """True se o número de avaliações já atingiu o orçamento."""
    return instancia["avaliacoes"] >= orcamento


def descida(instancia, solucao_inicial, gerar_vizinhos, estrategia,
            orcamento, rng):
    """Uma descida gulosa a partir de solucao_inicial.

    estrategia: "best" (Best Improvement) ou "first" (First Improvement).

    Devolve (solucao, h, passos, otimo_local):
    - passos: quantidade de movimentos de melhoria feitos;
    - otimo_local: True se a descida terminou porque nenhum vizinho melhora
      a solução (vizinhança inteira avaliada). False se o orçamento acabou
      antes disso.
    """
    atual = solucao_inicial
    h_atual = avaliar_com_contagem(atual, instancia)
    passos = 0

    while True:
        vizinhos = gerar_vizinhos(atual)
        if estrategia == "first":
            # ordem aleatória, para o First Improvement não ser sempre igual
            rng.shuffle(vizinhos)

        melhor_vizinho = None
        h_melhor_vizinho = h_atual

        for vizinho in vizinhos:
            if orcamento_esgotado(instancia, orcamento):
                return atual, h_atual, passos, False

            h_vizinho = avaliar_com_contagem(vizinho, instancia)

            if h_vizinho < h_melhor_vizinho:
                melhor_vizinho = vizinho
                h_melhor_vizinho = h_vizinho
                if estrategia == "first":
                    break  # aceita o primeiro que melhora

        if melhor_vizinho is None:
            # nenhum vizinho melhora: ótimo local
            return atual, h_atual, passos, True

        atual = melhor_vizinho
        h_atual = h_melhor_vizinho
        passos += 1


def greedy_random_restart(instancia, gerar_vizinhos, estrategia, orcamento,
                          rng=None):
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
        solucao, h, passos, otimo_local = descida(
            instancia, inicial, gerar_vizinhos, estrategia, orcamento, rng
        )
        descidas += 1
        passos_total += passos

        if otimo_local:
            otimos_locais.append((solucao, h))

        if melhor_h is None or h < melhor_h:
            melhor_solucao = solucao
            melhor_h = h
            historico.append((instancia["avaliacoes"], melhor_h))

    return {
        "melhor_solucao": melhor_solucao,
        "melhor_h": melhor_h,
        "avaliacoes": instancia["avaliacoes"],
        "passos": passos_total,
        "restarts": descidas - 1,
        "otimos_locais": otimos_locais,
        "historico": historico,
    }
