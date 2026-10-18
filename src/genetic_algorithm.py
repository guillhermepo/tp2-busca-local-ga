"""genetic_algorithm.py

Genetic Algorithm para problemas cujas soluções são permutações.

- Cromossomo: uma permutação (gene = posição, alelo = ativo).
- Inicialização: N permutações aleatórias.
- Seleção: torneio. Como h é custo (minimização), vence o indivíduo de
  menor h; o torneio só compara valores, então não é preciso converter h
  em uma aptidão positiva (como seria na roleta).
- Cruzamento: Order Crossover (OX), aplicado com probabilidade Pc.
- Mutação: Swap Mutation, aplicada a cada filho com probabilidade Pm.
- Elitismo: os `elites` melhores passam intactos para a próxima geração.
- Parada: esgotamento do orçamento de avaliações.

Cada filho novo avaliado conta 1 avaliação. Um filho que não sofreu
cruzamento nem mutação é cópia de um pai e herda o h já conhecido; os
elites também não são reavaliados.
"""

import random

from src.problema import avaliar_com_contagem, solucao_aleatoria, zerar_contador


def torneio(populacao, tamanho, rng):
    """Sorteia `tamanho` indivíduos e devolve o de menor h."""
    competidores = rng.sample(populacao, tamanho)
    vencedor = competidores[0]
    for individuo in competidores[1:]:
        if individuo[1] < vencedor[1]:
            vencedor = individuo
    return vencedor


def order_crossover(pai1, pai2, rng):
    """Order Crossover (OX).

    1. Sorteia dois cortes a <= b e copia pai1[a..b] para o filho, nas
       mesmas posições.
    2. Percorre pai2 a partir da posição b+1 (voltando ao início ao chegar
       ao fim) e, na mesma ordem, preenche as posições livres do filho, também
       a partir de b+1, pulando os ativos que já estão no filho.

    Exemplo com a = 2, b = 4:
        pai1  = [1, 2, 3, 4, 5, 6, 7]
        pai2  = [5, 7, 4, 1, 6, 3, 2]
        filho = [_, _, 3, 4, 5, _, _]
        pai2 a partir da posição 5: 3, 2, 5, 7, 4, 1, 6 -> sem 3, 4, 5: 2, 7, 1, 6
        posições livres a partir da 5: 5, 6, 0, 1
        filho = [1, 6, 3, 4, 5, 2, 7]
    """
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
    """Troca os alelos de duas posições sorteadas (devolve nova lista)."""
    mutante = list(cromossomo)
    i, j = rng.sample(range(len(mutante)), 2)
    mutante[i], mutante[j] = mutante[j], mutante[i]
    return mutante


def diversidade(populacao):
    """Devolve (cromossomos distintos, distância média entre pares).

    A distância entre dois cromossomos é a fração de posições em que os
    alelos diferem (Hamming normalizada): 0 = iguais, 1 = nenhuma posição
    em comum.
    """
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


def genetic_algorithm(instancia, orcamento, rng=None, tamanho_populacao=60,
                      pc=0.9, pm=0.2, tamanho_torneio=3, elites=2,
                      janelas=100):
    """Executa o GA até gastar exatamente o orçamento de avaliações.

    A população é uma lista de pares (cromossomo, h).

    Devolve um dicionário com:
    - melhor_solucao, melhor_h, avaliacoes, geracoes
    - historico: lista de (avaliacoes, melhor_h) a cada nova melhor solução
    - geracoes_info: lista de dicionários ao longo das gerações, com
      avaliacoes, melhor_h (da população), media_h, distintos e
      distancia_media
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    zerar_contador(instancia)

    melhor_solucao = None
    melhor_h = None
    historico = []

    populacao = []
    for _ in range(tamanho_populacao):
        cromossomo = solucao_aleatoria(instancia["n"], rng)
        h = avaliar_com_contagem(cromossomo, instancia)
        populacao.append((cromossomo, h))
        if melhor_h is None or h < melhor_h:
            melhor_solucao = cromossomo
            melhor_h = h
            historico.append((instancia["avaliacoes"], melhor_h))

    novos_por_geracao = max(1, tamanho_populacao - elites)
    geracoes_estimadas = max(1, (orcamento - tamanho_populacao) // novos_por_geracao)
    passo_registro = max(1, geracoes_estimadas // janelas)

    geracoes_info = []
    geracao = 0

    while True:
        fim = instancia["avaliacoes"] >= orcamento
        if geracao % passo_registro == 0 or fim:
            valores = [individuo[1] for individuo in populacao]
            distintos, distancia = diversidade(populacao)
            geracoes_info.append({
                "geracao": geracao,
                "avaliacoes": instancia["avaliacoes"],
                "melhor_h": min(valores),
                "media_h": sum(valores) / len(valores),
                "distintos": distintos,
                "distancia_media": distancia,
            })

        if fim:
            break

        ordenada = sorted(populacao, key=lambda individuo: individuo[1])
        nova_populacao = ordenada[:elites]

        while (len(nova_populacao) < tamanho_populacao
               and instancia["avaliacoes"] < orcamento):
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
                if not alterados[k]:
                    nova_populacao.append(pais[k])
                    continue
                if instancia["avaliacoes"] >= orcamento:
                    break
                h = avaliar_com_contagem(filhos[k], instancia)
                nova_populacao.append((filhos[k], h))
                if h < melhor_h:
                    melhor_solucao = filhos[k]
                    melhor_h = h
                    historico.append((instancia["avaliacoes"], melhor_h))

        # Se o orçamento acabar no meio da geração, ela fica incompleta; os
        # indivíduos que faltam nunca seriam avaliados mesmo.
        populacao = nova_populacao
        geracao += 1

    return {
        "melhor_solucao": melhor_solucao,
        "melhor_h": melhor_h,
        "avaliacoes": instancia["avaliacoes"],
        "geracoes": geracao,
        "historico": historico,
        "geracoes_info": geracoes_info,
    }
