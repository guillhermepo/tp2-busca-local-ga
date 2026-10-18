"""simulated_annealing.py

Simulated Annealing com resfriamento geométrico (T <- alfa * T).

Regra de aceitação, para o sucessor sorteado s' da solução corrente s:
    se h(s') <= h(s): aceita;
    senão: aceita com probabilidade exp(-(h(s') - h(s)) / T)   (Gibbs).

Calibração (feita em cada execução, com avaliações que contam no orçamento):
    A partir da solução inicial aleatória, sorteiam-se `amostras` sucessores
    e mede-se a piora média delta_medio dos que são piores. Então:
        T0 = -delta_medio / ln(p_inicial)   -> no início, uma piora típica é
                                               aceita com prob. p_inicial;
        Tf = T0 * razao_final               -> no fim, T caiu três ordens de
                                               grandeza (razao_final = 1e-3),
                                               e pioras quase não são aceitas;
        alfa = (Tf / T0) ** (1 / iteracoes) -> T chega a Tf exatamente quando
                                               o orçamento acaba.
    Como delta_medio é medido na própria instância, a escala de T acompanha
    a magnitude de h em cada instância.
"""

import math
import random

from src.problema import avaliar_com_contagem, solucao_aleatoria, zerar_contador
from src.vizinhancas import sucessor_aleatorio


def simulated_annealing(instancia, operador, orcamento, rng=None,
                        p_inicial=0.8, razao_final=1e-3, amostras=100,
                        janelas=100):
    """Executa o SA até gastar exatamente o orçamento de avaliações.

    janelas: a execução é dividida em `janelas` trechos de mesmo número de
    iterações; em cada um registra-se a taxa de aceitação de movimentos
    piores (aceitos piores / propostos piores).

    Devolve um dicionário com:
    - melhor_solucao, melhor_h, avaliacoes
    - t0, tf, alfa
    - aceitos: movimentos aceitos (melhores, iguais ou piores)
    - piores_propostos, piores_aceitos: totais da execução
    - historico: lista de (avaliacoes, melhor_h) a cada nova melhor solução
    - aceitacao: lista de (avaliacoes, temperatura, taxa) por janela
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    zerar_contador(instancia)

    atual = solucao_aleatoria(instancia["n"], rng)
    h_atual = avaliar_com_contagem(atual, instancia)
    melhor_solucao = atual
    melhor_h = h_atual
    historico = [(instancia["avaliacoes"], melhor_h)]

    # --- Calibração de T0 e Tf ---
    pioras = []
    for _ in range(amostras):
        vizinho = sucessor_aleatorio(atual, operador, rng)
        h_vizinho = avaliar_com_contagem(vizinho, instancia)
        if h_vizinho > h_atual:
            pioras.append(h_vizinho - h_atual)
        if h_vizinho < melhor_h:
            melhor_solucao = vizinho
            melhor_h = h_vizinho
            historico.append((instancia["avaliacoes"], melhor_h))

    if not pioras:
        pioras = [1]  # caso degenerado: nenhum sucessor sorteado piorou h
    delta_medio = sum(pioras) / len(pioras)
    t0 = -delta_medio / math.log(p_inicial)
    tf = t0 * razao_final

    iteracoes = orcamento - instancia["avaliacoes"]
    alfa = (tf / t0) ** (1 / iteracoes)
    tamanho_janela = max(1, iteracoes // janelas)

    # --- Laço principal ---
    temperatura = t0
    aceitos = 0
    piores_propostos = 0
    piores_aceitos = 0
    janela_propostos = 0
    janela_aceitos = 0
    iteracao = 0
    aceitacao = []

    while instancia["avaliacoes"] < orcamento:
        vizinho = sucessor_aleatorio(atual, operador, rng)
        h_vizinho = avaliar_com_contagem(vizinho, instancia)
        delta = h_vizinho - h_atual

        if delta <= 0:
            aceita = True
        else:
            piores_propostos += 1
            janela_propostos += 1
            aceita = rng.random() < math.exp(-delta / temperatura)
            if aceita:
                piores_aceitos += 1
                janela_aceitos += 1

        if aceita:
            atual = vizinho
            h_atual = h_vizinho
            aceitos += 1
            if h_atual < melhor_h:
                melhor_solucao = atual
                melhor_h = h_atual
                historico.append((instancia["avaliacoes"], melhor_h))

        iteracao += 1
        if iteracao % tamanho_janela == 0:
            if janela_propostos > 0:
                taxa = janela_aceitos / janela_propostos
            else:
                taxa = 0.0
            aceitacao.append((instancia["avaliacoes"], temperatura, taxa))
            janela_propostos = 0
            janela_aceitos = 0

        temperatura *= alfa

    return {
        "melhor_solucao": melhor_solucao,
        "melhor_h": melhor_h,
        "avaliacoes": instancia["avaliacoes"],
        "t0": t0,
        "tf": tf,
        "alfa": alfa,
        "aceitos": aceitos,
        "piores_propostos": piores_propostos,
        "piores_aceitos": piores_aceitos,
        "historico": historico,
        "aceitacao": aceitacao,
    }
