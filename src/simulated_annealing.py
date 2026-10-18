"""simulated_annealing.py

Simulated Annealing com resfriamento geométrico, T <- alpha * T.

Regra de aceitação (sucessor aleatório pi' da solução corrente pi):
- se h(pi') <= h(pi), aceita;
- senão, aceita com probabilidade exp(-(h(pi') - h(pi)) / T) (Gibbs).

CALIBRAÇÃO DO ANNEALING SCHEDULE (automática, por instância)

A escala de h(pi') - h(pi) muda muito com o tamanho da instância (dezenas na
pequena, milhares na grande), então T0 e Tf não são constantes:

- T0: amostram-se `amostras_calibracao` sucessores de uma solução aleatória
  e toma-se a média dos aumentos de h (apenas os deltas > 0), `delta_medio`.
  T0 = -delta_medio / ln(p0), isto é, T0 faz um movimento pior típico ser
  aceito com probabilidade p0 (padrão 0.8): a busca começa quase como um
  random walk.
- Tf = T0 * razao_final (padrão 1e-3): ao final, um movimento pior típico
  tem probabilidade ~p0^(1000) de ser aceito, ou seja, a busca termina
  praticamente como um greedy descent.
- Em cada temperatura fazem-se `passos_por_temperatura` propostas (padrão n).
  O número de patamares K sai do orçamento restante, e
  alpha = (Tf / T0) ** (1 / (K - 1)). Assim o resfriamento usa o orçamento
  inteiro, e o schedule é comparável entre instâncias.

As avaliações da calibração são contadas no orçamento (nada é gratuito).

Taxa de aceitação de movimentos piores: em cada patamar guarda-se
(avaliacoes, temperatura, piores_propostos, piores_aceitos) para o gráfico
exigido no relatório.
"""

import math
import random

from src.rastro import Rastro


def calibrar_temperaturas(problema, rng, amostras, p0, razao_final, rastro):
    """Estima (T0, Tf) a partir de deltas amostrados de uma solução aleatória.

    Devolve (t0, tf, delta_medio). Cada sucessor amostrado conta 1 avaliação.
    """
    solucao = problema.solucao_aleatoria(rng)
    h_base = problema.h(solucao)
    rastro.observar(problema.avaliacoes, solucao, h_base)
    deltas = []
    for _ in range(amostras):
        vizinho, h_vizinho = problema.sucessor_aleatorio(solucao, rng)
        rastro.observar(problema.avaliacoes, vizinho, h_vizinho)
        if h_vizinho > h_base:
            deltas.append(h_vizinho - h_base)
    delta_medio = sum(deltas) / len(deltas) if deltas else 1.0
    t0 = -delta_medio / math.log(p0)
    return t0, t0 * razao_final, delta_medio


def simulated_annealing(problema, orcamento, rng=None, p0=0.8,
                        razao_final=1e-3, passos_por_temperatura=None,
                        amostras_calibracao=100, t0=None, tf=None):
    """Executa o SA até gastar exatamente `orcamento` avaliações.

    t0/tf: se informados, substituem a calibração automática (as
    amostras de calibração não são gastas).

    Devolve um dicionário com melhor_solucao, melhor_h, avaliacoes,
    passos (movimentos aceitos), restarts (0), historico, t0, tf, alpha e
    taxa_aceitacao: lista de (avaliacoes, T, piores_propostos,
    piores_aceitos), uma entrada por patamar de temperatura.
    """
    if rng is None:
        rng = random.Random()
    elif isinstance(rng, int):
        rng = random.Random(rng)
    if passos_por_temperatura is None:
        passos_por_temperatura = max(1, problema.n)

    problema.zerar()
    rastro = Rastro()

    if t0 is None or tf is None:
        t0, tf, _ = calibrar_temperaturas(
            problema, rng, amostras_calibracao, p0, razao_final, rastro
        )
    restante = max(0, orcamento - problema.avaliacoes)
    patamares = max(2, restante // passos_por_temperatura)
    alpha = (tf / t0) ** (1.0 / (patamares - 1))

    atual = problema.solucao_aleatoria(rng)
    h_atual = problema.h(atual)
    rastro.observar(problema.avaliacoes, atual, h_atual)

    temperatura = t0
    aceitos = 0
    taxa_aceitacao = []

    while problema.avaliacoes < orcamento:
        piores_propostos = 0
        piores_aceitos = 0
        for _ in range(passos_por_temperatura):
            if problema.avaliacoes >= orcamento:
                break
            vizinho, h_vizinho = problema.sucessor_aleatorio(atual, rng)
            rastro.observar(problema.avaliacoes, vizinho, h_vizinho)
            delta = h_vizinho - h_atual
            if delta <= 0:
                aceitar = True
            else:
                piores_propostos += 1
                aceitar = rng.random() < math.exp(-delta / temperatura)
                if aceitar:
                    piores_aceitos += 1
            if aceitar:
                atual, h_atual = vizinho, h_vizinho
                aceitos += 1
        taxa_aceitacao.append(
            (problema.avaliacoes, temperatura, piores_propostos,
             piores_aceitos)
        )
        temperatura *= alpha

    return {
        "melhor_solucao": rastro.melhor_solucao,
        "melhor_h": rastro.melhor_h,
        "avaliacoes": problema.avaliacoes,
        "passos": aceitos,
        "restarts": 0,
        "historico": rastro.historico,
        "t0": t0,
        "tf": tf,
        "alpha": alpha,
        "taxa_aceitacao": taxa_aceitacao,
    }
