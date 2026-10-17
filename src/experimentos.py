"""experimentos.py

Preparação para os experimentos oficiais.

STATUS: apenas constantes e funções utilitárias. Nenhum experimento é
executado aqui ainda, e nenhum resultado é gerado.

Contagem de avaliações: o orçamento é medido em avaliações de h, contadas
em UM único lugar: problema.avaliar_com_contagem (contador guardado em
instancia["avaliacoes"]). Cada execução deve começar com
problema.zerar_contador(instancia) (o greedy já faz isso).
"""

import csv
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")
PASTA_RESULTADOS = os.path.join(RAIZ, "resultados")

# Orçamentos oficiais (avaliações de h por execução) e nº de execuções.
CONFIGURACOES = {
    "pequena": {
        "arquivo": "manutencao_pequena.txt",
        "orcamento": 50_000,
        "execucoes": 30,
    },
    "media": {
        "arquivo": "manutencao_media.txt",
        "orcamento": 150_000,
        "execucoes": 30,
    },
    "grande": {
        "arquivo": "manutencao_grande.txt",
        "orcamento": 300_000,
        "execucoes": 10,
    },
}

# Colunas dos CSVs de resultados (uma linha por execução).
COLUNAS_CSV = [
    "instancia",
    "algoritmo",
    "variante",
    "vizinhanca",
    "seed",
    "melhor_h",
    "avaliacoes",
    "passos",
    "restarts",
    "tempo_segundos",
]


def caminho_instancia(nome):
    """Caminho do arquivo da instância: "pequena", "media" ou "grande"."""
    return os.path.join(PASTA_DADOS, CONFIGURACOES[nome]["arquivo"])


def salvar_csv(linhas, nome_arquivo):
    """Salva uma lista de dicionários (chaves = COLUNAS_CSV) em resultados/.

    Só grava o que receber: não inventa nenhuma linha.
    """
    caminho = os.path.join(PASTA_RESULTADOS, nome_arquivo)
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS_CSV)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


# TODO: executar_experimento(nome_instancia, algoritmo, variante, vizinhanca)
#   Para cada execução (seed = 0, 1, ..., execucoes - 1):
#     1. carregar a instância (problema.carregar_instancia)
#     2. medir o tempo (time.perf_counter) ao redor do algoritmo
#     3. montar um dicionário com as chaves de COLUNAS_CSV
#     4. ao final, chamar salvar_csv(linhas, "nome.csv")
#
# TODO: ligar greedy.greedy_random_restart às vizinhanças quando
#   vizinhancas.py estiver implementado.
# TODO: Simulated Annealing e Algoritmo Genético (outros módulos).
