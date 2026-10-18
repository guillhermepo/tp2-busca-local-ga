"""genetico.py

Algoritmo Genético para permutações (codificação: o cromossomo é a própria
sequência de manutenção).

Ciclo de vida (por geração):
    1. elitismo: os `elite` melhores indivíduos passam intactos (sem reavaliar);
    2. seleção de dois pais (torneio ou roleta);
    3. cruzamento com probabilidade Pc (senão os filhos são cópias dos pais);
    4. mutação de cada filho com probabilidade Pm;
    5. avaliação dos filhos (cada filho avaliado conta 1 avaliação).
O critério de parada é o esgotamento do orçamento de avaliações; a geração
corrente é interrompida no instante em que o orçamento acaba.

SELEÇÃO EM UM PROBLEMA DE MINIMIZAÇÃO
- Torneio de tamanho k: sorteia k indivíduos e escolhe o de MENOR h. Só
  depende da ordem dos custos, então não precisa converter h em aptidão.
- Roleta: a probabilidade deve ser proporcional a uma aptidão que cresce
  quando h diminui. Usa-se f = (h_max - h) + 1, com h_max o pior h da
  população corrente (o +1 evita probabilidade zero para o pior indivíduo).

DIVERSIDADE: a cada geração registram-se o número de cromossomos distintos,
a distância média entre pares (fração de posições diferentes, estimada em
`pares_diversidade` pares sorteados) e o h médio da população.
"""

import random

from src.rastro import Rastro


def _torneio(populacao, k, rng):
    candidatos = [populacao[rng.randrange(len(populacao))] for _ in range(k)]
    return min(candidatos, key=lambda individuo: individuo[0])[1]


def _roleta(populacao, rng):
    h_max = max(h for h, _ in populacao)
    aptidoes = [(h_max - h) + 1 for h, _ in populacao]
    return rng.choices([s for _, s in populacao], weights=aptidoes, k=1)[0]


def _diversidade(populacao, rng, pares):
    distintos = len({tuple(s) for _, s in populacao})
    n = len(populacao[0][1])
    tamanho = len(populacao)
    if tamanho < 2:
        return distintos, 0.0
    total = 0
    for _ in range(pares):
        i = rng.randrange(tamanho)
        j = rng.randrange(tamanho - 1)
        if j >= i:
            j += 1
        a, b = populacao[i][1], populacao[j][1]
        total += sum(1 for x, y in zip(a, b) if x != y)
    return distintos, total / (pares * n)


def algoritmo_genetico(problema, orcamento, rng=None, tamanho_populacao=50,
                       pc=0.9, pm=0.5, elite=2, selecao="torneio",
                       tamanho_torneio=3, pares_diversidade=200):
    """Executa o GA até gastar exatamente `orcamento` avaliações.

    Devolve um dicionário com melhor_solucao, melhor_h, avaliacoes,
    passos (gerações concluídas), restarts (0), historico (melhor h por
    avaliação) e geracoes: lista de dicionários por geração com
    avaliacoes, melhor_h, media_h, distintos e distancia_media.
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)
    if selecao not in ("torneio", "roleta"):
        raise ValueError(f"seleção inválida: {selecao!r}")
    if tamanho_populacao < 2 or elite >= tamanho_populacao:
        raise ValueError("população deve ter >= 2 indivíduos e elite < N")

    problema.zerar()
    rastro = Rastro()

    populacao = []
    while len(populacao) < tamanho_populacao:
        if problema.avaliacoes >= orcamento:
            break
        solucao = problema.solucao_aleatoria(rng)
        h = problema.h(solucao)
        rastro.observar(problema.avaliacoes, solucao, h)
        populacao.append((h, solucao))

    geracoes = []

    def registrar():
        distintos, distancia = _diversidade(populacao, rng, pares_diversidade)
        geracoes.append({
            "avaliacoes": problema.avaliacoes,
            "melhor_h": min(h for h, _ in populacao),
            "media_h": sum(h for h, _ in populacao) / len(populacao),
            "distintos": distintos,
            "distancia_media": distancia,
        })

    if len(populacao) >= 2:
        registrar()

    def escolher():
        if selecao == "torneio":
            return _torneio(populacao, tamanho_torneio, rng)
        return _roleta(populacao, rng)

    while problema.avaliacoes < orcamento and len(populacao) >= 2:
        populacao.sort(key=lambda individuo: individuo[0])
        nova = populacao[:elite]
        while len(nova) < tamanho_populacao:
            pai_1, pai_2 = escolher(), escolher()
            if rng.random() < pc:
                filhos = problema.cruzamento(pai_1, pai_2, rng)
            else:
                filhos = (list(pai_1), list(pai_2))
            for filho in filhos:
                if len(nova) >= tamanho_populacao:
                    break
                if problema.avaliacoes >= orcamento:
                    break
                if rng.random() < pm:
                    filho = problema.mutacao(filho, rng)
                h = problema.h(filho)
                rastro.observar(problema.avaliacoes, filho, h)
                nova.append((h, filho))
            if problema.avaliacoes >= orcamento:
                break
        populacao = nova
        registrar()

    return {
        "melhor_solucao": rastro.melhor_solucao,
        "melhor_h": rastro.melhor_h,
        "avaliacoes": problema.avaliacoes,
        "passos": len(geracoes),
        "restarts": 0,
        "historico": rastro.historico,
        "geracoes": geracoes,
    }
