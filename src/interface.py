"""interface.py

Interface entre os algoritmos e o problema (algoritmo != problema).

Os três algoritmos (greedy.py, simulated_annealing.py, genetico.py) só
conhecem os métodos de ProblemaManutencao, e não o que há dentro dele:

    solucao_aleatoria(rng)        ponto de partida (uma permutação)
    h(s)                          fitness (minimização), conta 1 avaliação
    sucessores(s, rng, limite)    itera sobre os sucessores de s, já avaliados
    sucessor_aleatorio(s, rng)    sorteia um sucessor de s, já avaliado
    cruzamento(s1, s2, rng)       recombinação (dois filhos)
    mutacao(s, rng)               mutação (não avalia)
    tamanho_vizinhanca()          |N(s)|

Contagem de avaliações: o contador fica em instancia["avaliacoes"] e é
incrementado SOMENTE por problema.avaliar_com_contagem e
problema.avaliar_sufixo_com_contagem (cada chamada = 1 avaliação).

Avaliação incremental: com incremental=True, os sucessores são avaliados
reaproveitando o prefixo da solução-base que o movimento não altera
(problema.avaliar_sufixo). O resultado é idêntico ao da avaliação completa e
cada sucessor conta 1 avaliação do mesmo jeito; só o tempo de parede muda.
Para isso, os prefixos da última solução-base são guardados em cache (por
identidade do objeto); por isso as listas NUNCA devem ser modificadas no lugar.
"""

from src import problema, vizinhancas
from src.cruzamentos import CRUZAMENTOS


class ProblemaManutencao:
    def __init__(self, instancia, operador="swap", incremental=True,
                 cruzamento="ox", operador_mutacao="insertion"):
        vizinhancas._validar_operador(operador)
        vizinhancas._validar_operador(operador_mutacao)
        if cruzamento not in CRUZAMENTOS:
            raise ValueError(f"cruzamento inválido: {cruzamento!r}")
        self.instancia = instancia
        self.n = instancia["n"]
        self.operador = operador
        self.incremental = incremental
        self.operador_mutacao = operador_mutacao
        self._cruzamento = CRUZAMENTOS[cruzamento]
        self._cache_solucao = None
        self._cache_prefixos = None

    # -- contagem ----------------------------------------------------------

    @property
    def avaliacoes(self):
        return self.instancia["avaliacoes"]

    def zerar(self):
        problema.zerar_contador(self.instancia)
        self._cache_solucao = None
        self._cache_prefixos = None

    # -- problema ----------------------------------------------------------

    def solucao_aleatoria(self, rng=None):
        return problema.solucao_aleatoria(self.n, rng)

    def h(self, solucao):
        """Fitness (minimização) com contagem de 1 avaliação."""
        return problema.avaliar_com_contagem(solucao, self.instancia)

    def tamanho_vizinhanca(self):
        return vizinhancas.tamanho_vizinhanca(self.n, self.operador)

    def _prefixos_de(self, solucao):
        if self._cache_solucao is not solucao:
            self._cache_prefixos = problema.prefixos(solucao, self.instancia)
            self._cache_solucao = solucao
        return self._cache_prefixos

    def _avaliar_vizinho(self, solucao, vizinho, movimento):
        if not self.incremental:
            return problema.avaliar_com_contagem(vizinho, self.instancia)
        C, H = self._prefixos_de(solucao)
        k = vizinhancas.primeira_posicao_afetada(movimento, self.operador)
        return problema.avaliar_sufixo_com_contagem(
            vizinho, self.instancia, k, C, H
        )

    def sucessores(self, solucao, rng=None, limite=None):
        """Gera (vizinho, h_vizinho) para cada sucessor de solucao.

        rng: se dado, percorre os sucessores em ordem aleatória (usado pelo
        First Improvement). limite: se dado, a geração para quando o contador
        de avaliações atinge esse valor (verificado ANTES de cada avaliação).
        """
        lista = vizinhancas.movimentos(len(solucao), self.operador)
        if rng is not None:
            rng.shuffle(lista)
        for movimento in lista:
            if limite is not None and self.avaliacoes >= limite:
                return
            vizinho = vizinhancas.aplicar_movimento(
                solucao, movimento, self.operador
            )
            yield vizinho, self._avaliar_vizinho(solucao, vizinho, movimento)

    def sucessor_aleatorio(self, solucao, rng):
        """Sorteia um sucessor e o avalia. Devolve (vizinho, h_vizinho)."""
        movimento = vizinhancas.movimento_aleatorio(
            len(solucao), self.operador, rng
        )
        vizinho = vizinhancas.aplicar_movimento(
            solucao, movimento, self.operador
        )
        return vizinho, self._avaliar_vizinho(solucao, vizinho, movimento)

    # -- operadores genéticos ---------------------------------------------

    def cruzamento(self, pai_1, pai_2, rng):
        """Recombina dois pais; devolve (filho_1, filho_2). Não avalia."""
        return self._cruzamento(pai_1, pai_2, rng)

    def mutacao(self, solucao, rng):
        """Devolve uma cópia mutada (um movimento aleatório). Não avalia."""
        return vizinhancas.sucessor_aleatorio(
            solucao, self.operador_mutacao, rng
        )
