"""Genetic Algorithm para problemas de permutação."""

import random


def torneio(populacao, tamanho, rng):
    """Sorteia `tamanho` indivíduos e devolve o de menor h."""
    competidores = rng.sample(populacao, tamanho)
    vencedor = competidores[0]
    for individuo in competidores[1:]:
        if individuo[1] < vencedor[1]:
            vencedor = individuo
    return vencedor


def order_crossover(pai1, pai2, rng):
    """Order Crossover (OX): preserva um trecho de pai1 e a ordem relativa de pai2."""
    n = len(pai1)
    a, b = sorted(rng.sample(range(n), 2))

    filho = [None] * n
    filho[a:b + 1] = pai1[a:b + 1]
    no_filho = set(pai1[a:b + 1])

    posicao = (b + 1) % n
    for k in range(n):
        ativo = pai2[(b + 1 + k) % n]
        if ativo not in no_filho:
            filho[posicao] = ativo
            posicao = (posicao + 1) % n
    return filho


def swap_mutation(cromossomo, rng):
    """Troca os alelos de duas posições sorteadas."""
    mutante = list(cromossomo)
    i, j = rng.sample(range(len(mutante)), 2)
    mutante[i], mutante[j] = mutante[j], mutante[i]
    return mutante


def diversidade(populacao):
    """Calcula a quantidade de cromossomos distintos e a distância de Hamming média."""
    cromossomos = [individuo[0] for individuo in populacao]
    distintos = len(set(tuple(c) for c in cromossomos))

    tamanho = len(cromossomos)
    if tamanho < 2:
        return distintos, 0.0

    n = len(cromossomos[0])
    diferencas = 0
    pares = 0
    for i in range(tamanho):
        a = cromossomos[i]
        for j in range(i + 1, tamanho):
            b = cromossomos[j]
            for k in range(n):
                if a[k] != b[k]:
                    diferencas += 1
            pares += 1
    return distintos, diferencas / (pares * n)


def _resumo_geracao(populacao, geracao, avaliacoes):
    valores = [individuo[1] for individuo in populacao]
    distintos, distancia = diversidade(populacao)
    return {
        "geracao": geracao,
        "avaliacoes": avaliacoes,
        "melhor_h": min(valores),
        "media_h": sum(valores) / len(valores),
        "distintos": distintos,
        "distancia_media": distancia,
    }


def genetic_algorithm(problema, orcamento=None, rng=None, tamanho_populacao=60,
                      pc=0.9, pm=0.2, tamanho_torneio=3, elites=2,
                      janelas=100):
    """Executa o Genetic Algorithm até esgotar o orçamento de avaliações."""
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    problema.iniciar_orcamento(orcamento)

    melhor_solucao = None
    melhor_h = None
    historico = []

    populacao = []
    for _ in range(tamanho_populacao):
        if problema.orcamento_esgotado():
            break
        cromossomo = problema.solucao_aleatoria(rng)
        h = problema.avaliar(cromossomo)
        populacao.append((cromossomo, h))
        if melhor_h is None or h < melhor_h:
            melhor_solucao = cromossomo
            melhor_h = h
            historico.append((problema.avaliacoes_usadas, melhor_h))

    novos_por_geracao = max(1, tamanho_populacao - elites)
    geracoes_estimadas = max(
        1, (problema.orcamento - len(populacao)) // novos_por_geracao
    )
    passo_registro = max(1, geracoes_estimadas // janelas)

    geracao = 0
    ultimo_resumo = _resumo_geracao(populacao, geracao, problema.avaliacoes_usadas)
    geracoes_info = [ultimo_resumo]

    while not problema.orcamento_esgotado():
        ordenada = sorted(populacao, key=lambda individuo: individuo[1])
        nova_populacao = ordenada[:elites]

        while (len(nova_populacao) < tamanho_populacao
               and not problema.orcamento_esgotado()):
            pai1 = torneio(populacao, tamanho_torneio, rng)
            pai2 = torneio(populacao, tamanho_torneio, rng)

            if rng.random() < pc:
                filhos = [order_crossover(pai1[0], pai2[0], rng),
                          order_crossover(pai2[0], pai1[0], rng)]
                alterados = [True, True]
            else:
                filhos = [pai1[0], pai2[0]]
                alterados = [False, False]

            for k in range(2):
                if rng.random() < pm:
                    filhos[k] = swap_mutation(filhos[k], rng)
                    alterados[k] = True

            pais = [pai1, pai2]
            for k in range(2):
                if len(nova_populacao) >= tamanho_populacao:
                    break
                # Filhos idênticos aos pais e elites reaproveitam o h já conhecido.
                if not alterados[k]:
                    nova_populacao.append(pais[k])
                    continue
                if problema.orcamento_esgotado():
                    break
                h = problema.avaliar(filhos[k])
                nova_populacao.append((filhos[k], h))
                if h < melhor_h:
                    melhor_solucao = filhos[k]
                    melhor_h = h
                    historico.append((problema.avaliacoes_usadas, melhor_h))

        # Se o orçamento acabar aqui, a geração fica incompleta e
        # não entra na medida de diversidade.
        if len(nova_populacao) < tamanho_populacao:
            break

        populacao = nova_populacao
        geracao += 1
        if geracao % passo_registro == 0 or problema.orcamento_esgotado():
            ultimo_resumo = _resumo_geracao(
                populacao, geracao, problema.avaliacoes_usadas
            )
            geracoes_info.append(ultimo_resumo)

    if geracoes_info[-1]["geracao"] != ultimo_resumo["geracao"]:
        geracoes_info.append(ultimo_resumo)

    return {
        "melhor_solucao": melhor_solucao,
        "melhor_h": melhor_h,
        "avaliacoes": problema.avaliacoes_usadas,
        "geracoes": geracao,
        "historico": historico,
        "geracoes_info": geracoes_info,
    }
