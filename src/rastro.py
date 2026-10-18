"""rastro.py

Registro do melhor valor encontrado ao longo de uma execução.

O historico é uma lista de (avaliacoes, melhor_h), com uma entrada a cada vez
que o melhor h conhecido melhora. Vale como função em escada: o melhor h
após `a` avaliações é o da última entrada com avaliacoes <= a. É a base das
curvas de convergência.
"""


class Rastro:
    def __init__(self):
        self.melhor_h = None
        self.melhor_solucao = None
        self.historico = []

    def observar(self, avaliacoes, solucao, h):
        """Registra uma solução avaliada; guarda-a se for a melhor até agora."""
        if self.melhor_h is None or h < self.melhor_h:
            self.melhor_h = h
            self.melhor_solucao = list(solucao)
            self.historico.append((avaliacoes, h))
            return True
        return False
