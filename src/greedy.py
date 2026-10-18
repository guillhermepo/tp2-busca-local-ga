"""greedy.py

Greedy Descent com Random Restart.

O algoritmo é genérico: só usa a interface de interface.ProblemaManutencao
(solucao_aleatoria, h, sucessores, sucessor_aleatorio, tamanho_vizinhanca).

Variantes de seleção do próximo sucessor (parâmetro `estrategia`):

- "best":   Best Improvement. Varre TODA a vizinhança e move-se para o melhor
           sucessor, se ele melhorar h. Termina em um ótimo local verdadeiro.
- "first":  First Improvement. Percorre a vizinhança em ordem aleatória e
           aceita o primeiro sucessor que melhora h. Termina em um ótimo local
           verdadeiro (a vizinhança inteira foi percorrida sem melhora).
- "random": Sucessor aleatório com aceitação de melhora. Sorteia um sucessor
           e o aceita apenas se melhorar h. Não há varredura completa, então
           o "ótimo local" é declarado por paciência: após `paciencia`
           sorteios seguidos sem melhora (padrão: |N|, o tamanho da
           vizinhança) a descida termina. Trata-se de um critério
           probabilístico: não prova que a solução é um ótimo local, mas
           com |N| sorteios uniformes sem sucesso a chance de ainda existir
           uma fração 1/|N| de vizinhos melhores é de cerca de e^-1.

Contagem de avaliações: todas passam por ProblemaManutencao (que usa
problema.avaliar_com_contagem). O orçamento é conferido ANTES de cada
avaliação, logo o total nunca ultrapassa o orçamento.
"""

import random

from src.rastro import Rastro

ESTRATEGIAS = ("best", "first", "random")


def orcamento_esgotado(problema, orcamento):
    """True se o número de avaliações já atingiu o orçamento."""
    return problema.avaliacoes >= orcamento


def descida(problema, solucao_inicial, estrategia, orcamento, rng, rastro,
            paciencia=None):
    """Uma descida gulosa a partir de solucao_inicial.

    Devolve (solucao, h, passos, otimo_local):
    - passos: quantidade de movimentos de melhoria feitos;
    - otimo_local: True se a descida terminou por não haver sucessor
      melhor (ou, em "random", por esgotar a paciência). False se o
      orçamento acabou antes disso.

    O `rastro` é atualizado com todo sucessor avaliado que melhore o melhor
    h global, mesmo que a descida seja interrompida pelo orçamento.
    """
    if estrategia not in ESTRATEGIAS:
        raise ValueError(f"estratégia inválida: {estrategia!r}")
    if paciencia is None:
        paciencia = max(1, problema.tamanho_vizinhanca())

    atual = solucao_inicial
    h_atual = problema.h(atual)
    rastro.observar(problema.avaliacoes, atual, h_atual)
    passos = 0

    while True:
        if orcamento_esgotado(problema, orcamento):
            return atual, h_atual, passos, False

        if estrategia == "random":
            sem_melhora = 0
            while sem_melhora < paciencia:
                if orcamento_esgotado(problema, orcamento):
                    return atual, h_atual, passos, False
                vizinho, h_vizinho = problema.sucessor_aleatorio(atual, rng)
                rastro.observar(problema.avaliacoes, vizinho, h_vizinho)
                if h_vizinho < h_atual:
                    atual, h_atual = vizinho, h_vizinho
                    passos += 1
                    sem_melhora = 0
                else:
                    sem_melhora += 1
            return atual, h_atual, passos, True

        # "best" e "first": percorre a vizinhança
        ordem = rng if estrategia == "first" else None
        melhor_vizinho = None
        h_melhor_vizinho = h_atual
        interrompido = False

        geracao = problema.sucessores(atual, rng=ordem, limite=orcamento)
        for vizinho, h_vizinho in geracao:
            rastro.observar(problema.avaliacoes, vizinho, h_vizinho)
            if h_vizinho < h_melhor_vizinho:
                melhor_vizinho = vizinho
                h_melhor_vizinho = h_vizinho
                if estrategia == "first":
                    break  # aceita o primeiro que melhora
        else:
            # gerador esgotado: ou a vizinhança acabou, ou o limite foi atingido
            interrompido = orcamento_esgotado(problema, orcamento)

        if melhor_vizinho is not None:
            atual, h_atual = melhor_vizinho, h_melhor_vizinho
            passos += 1
            continue
        # nenhum vizinho melhora; só é ótimo local se a varredura foi completa
        return atual, h_atual, passos, not interrompido


def greedy_random_restart(problema, estrategia, orcamento, rng=None,
                          paciencia=None):
    """Greedy Descent com Random Restart até gastar o orçamento.

    Zera o contador de avaliações no início. Enquanto houver orçamento:
    sorteia uma solução inicial, desce até um ótimo local e recomeça.

    Devolve um dicionário com:
    - melhor_solucao, melhor_h
    - avaliacoes: total de avaliações usadas
    - passos: total de passos de melhoria (somando todas as descidas)
    - restarts: quantas vezes recomeçou (descidas - 1)
    - otimos_locais: lista de (solucao, h) de cada ótimo local alcançado
    - historico: lista de (avaliacoes, melhor_h) a cada nova melhor solução
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    problema.zerar()
    rastro = Rastro()
    passos_total = 0
    descidas = 0
    otimos_locais = []

    while not orcamento_esgotado(problema, orcamento):
        inicial = problema.solucao_aleatoria(rng)
        solucao, h, passos, otimo_local = descida(
            problema, inicial, estrategia, orcamento, rng, rastro, paciencia
        )
        descidas += 1
        passos_total += passos
        if otimo_local:
            otimos_locais.append((solucao, h))

    return {
        "melhor_solucao": rastro.melhor_solucao,
        "melhor_h": rastro.melhor_h,
        "avaliacoes": problema.avaliacoes,
        "passos": passos_total,
        "restarts": descidas - 1,
        "otimos_locais": otimos_locais,
        "historico": rastro.historico,
    }
