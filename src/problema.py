"""problema.py

Base comum do projeto: leitura da instância, tempos de deslocamento,
função objetivo h (atraso ponderado total) e solução aleatória.

CONVENÇÃO DE ÍNDICES (importante, vale para todo o projeto):

    índice 0 = base
    índice 1 = ativo 1
    ...
    índice n = ativo n

Uma solução é uma lista com uma permutação de 1..n (a base NÃO aparece nela).
Exemplo para n = 3: [2, 3, 1] -> sai da base, visita o ativo 2, depois o 3,
depois o 1.

A instância é um dicionário com as chaves:

    "n"          -> quantidade de ativos
    "base"       -> tupla (x, y) da base
    "ativos"     -> lista de tamanho n+1; ativos[0] é a base (p=d=w=0) e
                    ativos[j] é um dicionário {"x", "y", "p", "d", "w"}
    "tempos"     -> matriz (n+1) x (n+1) com os tempos de deslocamento
    "avaliacoes" -> contador de avaliações de h (ver avaliar_com_contagem)
"""

import math
import random


# ---------------------------------------------------------------------------
# Leitura da instância
# ---------------------------------------------------------------------------

def carregar_instancia(caminho):
    """Lê um arquivo de instância e devolve o dicionário da instância.

    Formato do arquivo:
        n
        x_base y_base
        x_1 y_1 p_1 d_1 w_1
        ...
        x_n y_n p_n d_n w_n
    """
    with open(caminho, "r", encoding="utf-8") as arquivo:
        # Lê todos os números do arquivo, ignorando quebras de linha e espaços
        numeros = [int(valor) for valor in arquivo.read().split()]

    n = numeros[0]
    base = (numeros[1], numeros[2])

    if len(numeros) != 3 + 5 * n:
        raise ValueError(
            f"Arquivo {caminho} inconsistente: esperados {3 + 5 * n} números, "
            f"encontrados {len(numeros)}"
        )

    # A posição 0 representa a base: duração, prazo e peso são zero.
    ativos = [{"x": base[0], "y": base[1], "p": 0, "d": 0, "w": 0}]

    posicao = 3  # primeiro número depois de n e da base
    for _ in range(n):
        x, y, p, d, w = numeros[posicao:posicao + 5]
        ativos.append({"x": x, "y": y, "p": p, "d": d, "w": w})
        posicao += 5

    instancia = {
        "n": n,
        "base": base,
        "ativos": ativos,
        "avaliacoes": 0,
    }
    instancia["tempos"] = calcular_matriz_tempos(ativos)
    return instancia


# ---------------------------------------------------------------------------
# Tempos de deslocamento
# ---------------------------------------------------------------------------

def calcular_distancia(ponto_a, ponto_b):
    """Tempo de deslocamento entre dois pontos (x, y).

    t_ij = round(sqrt((x_i - x_j)^2 + (y_i - y_j)^2))

    O round do Python devolve o inteiro mais próximo. (O caso especial de
    empate em .5 não ocorre aqui: a raiz de um inteiro ou é inteira ou é
    irracional.)
    """
    dx = ponto_a[0] - ponto_b[0]
    dy = ponto_a[1] - ponto_b[1]
    return round(math.sqrt(dx * dx + dy * dy))


def calcular_matriz_tempos(ativos):
    """Pré-calcula os tempos entre todos os pares de pontos.

    tempos[i][j] = tempo de deslocamento do ponto i ao ponto j, com
    índice 0 = base, 1 = ativo 1, ..., n = ativo n.
    """
    pontos = [(ativo["x"], ativo["y"]) for ativo in ativos]
    return [
        [calcular_distancia(origem, destino) for destino in pontos]
        for origem in pontos
    ]


# ---------------------------------------------------------------------------
# Função de avaliação
# ---------------------------------------------------------------------------

def avaliar(solucao, instancia):
    """Calcula h(solucao) = soma de w_j * max(0, C_j - d_j).

    Esta função NÃO conta avaliações. Use-a em testes e verificações.
    Os algoritmos devem usar avaliar_com_contagem.
    """
    ativos = instancia["ativos"]
    tempos = instancia["tempos"]

    posicao_atual = 0     # começa na base (índice 0)
    tempo_atual = 0       # tempo acumulado C_0 = 0
    custo = 0             # valor de h acumulado

    for ativo in solucao:
        # Tempo de conclusão: tempo anterior + deslocamento + manutenção
        tempo_atual += tempos[posicao_atual][ativo]
        tempo_atual += ativos[ativo]["p"]

        # Atraso é zero se terminou no prazo (ou antes)
        atraso = max(0, tempo_atual - ativos[ativo]["d"])

        # Custo ponderado pela criticidade
        custo += ativos[ativo]["w"] * atraso

        posicao_atual = ativo  # próxima viagem parte deste ativo

    return custo


# ---------------------------------------------------------------------------
# Contagem de avaliações (centralizada aqui)
# ---------------------------------------------------------------------------

def avaliar_com_contagem(solucao, instancia):
    """Igual a avaliar, mas incrementa instancia["avaliacoes"].

    É o ÚNICO lugar onde o contador aumenta. Todos os algoritmos
    (Greedy, SA, GA) devem avaliar soluções através desta função, para que
    o orçamento de avaliações seja contado corretamente.
    """
    instancia["avaliacoes"] += 1
    return avaliar(solucao, instancia)


def zerar_contador(instancia):
    """Zera o contador de avaliações (chamar no início de cada execução)."""
    instancia["avaliacoes"] = 0


# ---------------------------------------------------------------------------
# Solução aleatória
# ---------------------------------------------------------------------------

def solucao_aleatoria(n, rng=None):
    """Gera uma permutação aleatória de 1..n.

    rng: objeto random.Random (para reprodutibilidade), ou um inteiro usado
    como semente. Se for None, usa uma fonte aleatória nova.
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)

    solucao = list(range(1, n + 1))
    rng.shuffle(solucao)
    return solucao


# ---------------------------------------------------------------------------
# Avaliação incremental (apenas o sufixo afetado por um movimento)
# ---------------------------------------------------------------------------

def prefixos(solucao, instancia):
    """Tempos de conclusão e custos acumulados de cada prefixo de solucao.

    Devolve (C, H), listas de tamanho n+1 em que, para k ativos já visitados,
    C[k] é o instante de conclusão do k-ésimo ativo (C[0] = 0) e H[k] é o
    custo acumulado deles (H[0] = 0). Não conta avaliações: é só preparação
    para avaliar_sufixo.
    """
    ativos = instancia["ativos"]
    tempos = instancia["tempos"]
    C = [0]
    H = [0]
    posicao = 0
    tempo = 0
    custo = 0
    for ativo in solucao:
        tempo += tempos[posicao][ativo] + ativos[ativo]["p"]
        atraso = tempo - ativos[ativo]["d"]
        if atraso > 0:
            custo += ativos[ativo]["w"] * atraso
        posicao = ativo
        C.append(tempo)
        H.append(custo)
    return C, H


def avaliar_sufixo(vizinho, instancia, k, C, H):
    """h(vizinho), reaproveitando os k primeiros ativos de uma solução-base.

    Pré-condição: vizinho[:k] é igual aos k primeiros ativos da solução cujos
    prefixos (C, H) foram calculados por prefixos(). Só os ativos a partir da
    posição k são reavaliados: custo O(n - k) em vez de O(n). O resultado é
    idêntico a avaliar(vizinho, instancia). Não conta avaliações.
    """
    ativos = instancia["ativos"]
    tempos = instancia["tempos"]
    posicao = vizinho[k - 1] if k > 0 else 0
    tempo = C[k]
    custo = H[k]
    for i in range(k, len(vizinho)):
        ativo = vizinho[i]
        dados = ativos[ativo]
        tempo += tempos[posicao][ativo] + dados["p"]
        atraso = tempo - dados["d"]
        if atraso > 0:
            custo += dados["w"] * atraso
        posicao = ativo
    return custo


def avaliar_sufixo_com_contagem(vizinho, instancia, k, C, H):
    """Igual a avaliar_sufixo, mas conta UMA avaliação de h.

    Uma avaliação incremental vale uma avaliação no orçamento: o ganho é de
    tempo de parede, não de contagem.
    """
    instancia["avaliacoes"] += 1
    return avaliar_sufixo(vizinho, instancia, k, C, H)
