"""Simulated Annealing com resfriamento geométrico e aceitação de Gibbs."""

import math
import random


def calibrar_sa(problema, operador, orcamento, rng=None, amostras=200,
                p_inicial=0.8, razao_final=1e-3):
    """Estima T0, Tf e alfa a partir da escala típica de pioras na instância."""
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    problema.iniciar_orcamento(None)
    pioras = []
    for _ in range(amostras):
        solucao = problema.solucao_aleatoria(rng)
        h_solucao = problema.avaliar(solucao)
        vizinho = problema.sucessor_aleatorio(solucao, operador, rng)
        h_vizinho = problema.avaliar(vizinho)
        if h_vizinho > h_solucao:
            pioras.append(h_vizinho - h_solucao)

    if not pioras:
        pioras = [1.0]

    delta_medio = sum(pioras) / len(pioras)
    t0 = -delta_medio / math.log(p_inicial)
    tf = t0 * razao_final
    iteracoes = max(1, orcamento - 1)
    alfa = (tf / t0) ** (1 / iteracoes)

    return {
        "delta_medio": delta_medio,
        "t0": t0,
        "tf": tf,
        "alfa": alfa,
    }


def simulated_annealing(problema, operador, orcamento=None, rng=None,
                        t0=None, tf=None, alfa=None, janelas=100,
                        p_inicial=0.8, razao_final=1e-3, amostras=200):
    """Executa o Simulated Annealing até esgotar o orçamento de avaliações."""
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    limite = orcamento if orcamento is not None else problema.orcamento

    # Quando T0/Tf não vêm calibrados previamente, calibra fora do orçamento
    # da execução para que todas as avaliações do orçamento sejam da busca.
    if t0 is None or tf is None:
        calibrado = calibrar_sa(
            problema, operador, limite, random.Random(0),
            amostras=amostras, p_inicial=p_inicial, razao_final=razao_final,
        )
        t0 = calibrado["t0"]
        tf = calibrado["tf"]
        alfa = calibrado["alfa"]

    problema.iniciar_orcamento(limite)

    atual = problema.solucao_aleatoria(rng)
    h_atual = problema.avaliar(atual)
    melhor_solucao = atual
    melhor_h = h_atual
    historico = [(problema.avaliacoes_usadas, melhor_h)]

    iteracoes = max(1, problema.orcamento - problema.avaliacoes_usadas)
    if alfa is None:
        alfa = (tf / t0) ** (1 / iteracoes)
    tamanho_janela = max(1, iteracoes // janelas)

    temperatura = t0
    aceitos = 0
    piores_propostos = 0
    piores_aceitos = 0
    janela_propostos = 0
    janela_aceitos = 0
    iteracao = 0
    aceitacao = []

    while not problema.orcamento_esgotado():
        vizinho = problema.sucessor_aleatorio(atual, operador, rng)
        h_vizinho = problema.avaliar(vizinho)
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
                historico.append((problema.avaliacoes_usadas, melhor_h))

        iteracao += 1
        if iteracao % tamanho_janela == 0:
            taxa = janela_aceitos / janela_propostos if janela_propostos > 0 else 0.0
            aceitacao.append((problema.avaliacoes_usadas, temperatura, taxa))
            janela_propostos = 0
            janela_aceitos = 0

        temperatura *= alfa

    # Registra a janela parcial final caso restem movimentos piores propostos.
    if janela_propostos > 0:
        taxa = janela_aceitos / janela_propostos
        aceitacao.append((problema.avaliacoes_usadas, temperatura, taxa))

    return {
        "melhor_solucao": melhor_solucao,
        "melhor_h": melhor_h,
        "avaliacoes": problema.avaliacoes_usadas,
        "t0": t0,
        "tf": tf,
        "alfa": alfa,
        "aceitos": aceitos,
        "piores_propostos": piores_propostos,
        "piores_aceitos": piores_aceitos,
        "historico": historico,
        "aceitacao": aceitacao,
    }
