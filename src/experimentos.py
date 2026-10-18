"""experimentos.py

Execução dos experimentos do TP2. Uso, a partir da raiz do projeto:

    python -m src.experimentos validar       # T1: valores de verificação de h
    python -m src.experimentos t2            # T2: comparação das vizinhanças
    python -m src.experimentos incremental   # T2: tempo incremental x completa
    python -m src.experimentos t3            # T3: protocolo oficial
    python -m src.experimentos extra         # experimento adicional do GA

Cada comando grava CSVs em resultados/. Contagem de avaliações: o orçamento
é medido em avaliações de h, contadas em UM único lugar:
problema.avaliar_com_contagem. Cada algoritmo zera o contador ao começar.
O tempo de parede (time.perf_counter) é medido em volta de cada execução.
"""

import csv
import os
import random
import sys
import time

from src.genetic_algorithm import genetic_algorithm
from src.greedy import greedy_random_restart
from src.problema import avaliar, carregar_instancia, instancia_exemplo_figura1
from src.simulated_annealing import simulated_annealing
from src.vizinhancas import OPERADORES

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

# Ótimo global conhecido da instância pequena (enunciado, Tabela 1).
H_OTIMO_PEQUENA = 1875

# Escolhas usadas na T3. Devem ser conferidas com a tabela da T2
# (python -m src.analise vizinhancas) antes de rodar o protocolo oficial.
VIZINHANCA_ADOTADA = "insertion"
VARIANTE_GREEDY = "first"

PARAMETROS_SA = {"p_inicial": 0.8, "razao_final": 1e-3, "amostras": 100}
PARAMETROS_GA = {"tamanho_populacao": 60, "pc": 0.9, "pm": 0.2,
                 "tamanho_torneio": 3, "elites": 2}

# Execuções usadas para medir o ganho de tempo da avaliação incremental.
EXECUCOES_INCREMENTAL = 3


def caminho_instancia(nome):
    """Caminho do arquivo da instância: "pequena", "media" ou "grande"."""
    return os.path.join(PASTA_DADOS, CONFIGURACOES[nome]["arquivo"])


def salvar_csv(linhas, nome_arquivo):
    """Salva uma lista de dicionários em resultados/ (colunas = chaves).

    Só grava o que receber: não inventa nenhuma linha.
    """
    caminho = os.path.join(PASTA_RESULTADOS, nome_arquivo)
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def texto_solucao(solucao):
    return " ".join(str(ativo) for ativo in solucao)


def distintos(otimos_locais):
    return len(set(tuple(solucao) for solucao, _ in otimos_locais))


# ---------------------------------------------------------------------------
# T1 - validação da função de avaliação
# ---------------------------------------------------------------------------

def validar():
    exemplo = instancia_exemplo_figura1()
    pequena = carregar_instancia(caminho_instancia("pequena"))

    casos = [
        ("exemplo da Figura 1 (n = 4)", exemplo, [1, 4, 2, 3], 39),
        ("exemplo da Figura 1 (n = 4)", exemplo, [1, 4, 3, 2], 22),
        ("manutencao_pequena.txt", pequena, list(range(1, 13)), 4366),
    ]
    tudo_certo = True
    for nome, instancia, solucao, esperado in casos:
        h = avaliar(solucao, instancia)
        situacao = "OK" if h == esperado else "ERRO"
        if h != esperado:
            tudo_certo = False
        print(f"{nome}: h({solucao}) = {h}  (esperado {esperado}) {situacao}")
    print(f"Ótimo global conhecido da instância pequena: h* = {H_OTIMO_PEQUENA}")
    return tudo_certo


# ---------------------------------------------------------------------------
# T2 - comparação das vizinhanças (Greedy Descent + Random Restart)
# ---------------------------------------------------------------------------

def experimento_t2():
    linhas = []
    for nome, config in CONFIGURACOES.items():
        instancia = carregar_instancia(caminho_instancia(nome))
        for variante in ("best", "first"):
            for operador in OPERADORES:
                for seed in range(config["execucoes"]):
                    inicio = time.perf_counter()
                    r = greedy_random_restart(instancia, operador, variante,
                                              config["orcamento"],
                                              random.Random(seed))
                    tempo = time.perf_counter() - inicio
                    linhas.append({
                        "instancia": nome,
                        "variante": variante,
                        "vizinhanca": operador,
                        "seed": seed,
                        "melhor_h": r["melhor_h"],
                        "avaliacoes": r["avaliacoes"],
                        "tempo_segundos": round(tempo, 4),
                        "passos": r["passos"],
                        "restarts": r["restarts"],
                        "otimos_locais": len(r["otimos_locais"]),
                        "otimos_locais_distintos": distintos(r["otimos_locais"]),
                        "melhor_solucao": texto_solucao(r["melhor_solucao"]),
                    })
                    print(f"t2 {nome} {variante} {operador} seed={seed} "
                          f"h={r['melhor_h']} {tempo:.1f}s", flush=True)
        salvar_csv(linhas, "t2_vizinhancas.csv")


def experimento_incremental():
    """Mesmo Greedy (best), mesmas sementes: só muda o modo de avaliar.

    Best Improvement é usado porque nele quase todo o tempo é gasto
    avaliando vizinhos, então a diferença de tempo vem da avaliação.
    """
    linhas = []
    for nome, config in CONFIGURACOES.items():
        instancia = carregar_instancia(caminho_instancia(nome))
        for operador in OPERADORES:
            for incremental in (False, True):
                for seed in range(EXECUCOES_INCREMENTAL):
                    inicio = time.perf_counter()
                    r = greedy_random_restart(instancia, operador, "best",
                                              config["orcamento"],
                                              random.Random(seed), incremental)
                    tempo = time.perf_counter() - inicio
                    linhas.append({
                        "instancia": nome,
                        "vizinhanca": operador,
                        "incremental": incremental,
                        "seed": seed,
                        "melhor_h": r["melhor_h"],
                        "avaliacoes": r["avaliacoes"],
                        "passos": r["passos"],
                        "tempo_segundos": round(tempo, 4),
                    })
                    print(f"incremental {nome} {operador} {incremental} "
                          f"seed={seed} h={r['melhor_h']} {tempo:.1f}s",
                          flush=True)
        salvar_csv(linhas, "incremental.csv")


# ---------------------------------------------------------------------------
# T3 - protocolo oficial: 3 algoritmos x 3 instâncias
# ---------------------------------------------------------------------------

def linha_principal(nome, algoritmo, seed, r, tempo):
    """Colunas comuns aos três algoritmos; as específicas ficam vazias."""
    return {
        "instancia": nome,
        "algoritmo": algoritmo,
        "seed": seed,
        "melhor_h": r["melhor_h"],
        "avaliacoes": r["avaliacoes"],
        "tempo_segundos": round(tempo, 4),
        "passos": "",
        "restarts": "",
        "otimos_locais_distintos": "",
        "aceitos": "",
        "piores_aceitos": "",
        "piores_propostos": "",
        "t0": "",
        "tf": "",
        "alfa": "",
        "geracoes": "",
        "melhor_solucao": texto_solucao(r["melhor_solucao"]),
    }


def experimento_t3():
    principal = []
    convergencia = []
    aceitacao = []
    geracoes = []

    for nome, config in CONFIGURACOES.items():
        instancia = carregar_instancia(caminho_instancia(nome))
        orcamento = config["orcamento"]

        for seed in range(config["execucoes"]):
            # Greedy Descent + Random Restart
            inicio = time.perf_counter()
            r = greedy_random_restart(instancia, VIZINHANCA_ADOTADA,
                                      VARIANTE_GREEDY, orcamento,
                                      random.Random(seed))
            tempo = time.perf_counter() - inicio
            linha = linha_principal(nome, "greedy", seed, r, tempo)
            linha["passos"] = r["passos"]
            linha["restarts"] = r["restarts"]
            linha["otimos_locais_distintos"] = distintos(r["otimos_locais"])
            principal.append(linha)
            for avaliacoes, h in r["historico"]:
                convergencia.append({"instancia": nome, "algoritmo": "greedy",
                                     "seed": seed, "avaliacoes": avaliacoes,
                                     "melhor_h": h})
            print(f"t3 {nome} greedy seed={seed} h={r['melhor_h']} "
                  f"{tempo:.1f}s", flush=True)

            # Simulated Annealing
            inicio = time.perf_counter()
            r = simulated_annealing(instancia, VIZINHANCA_ADOTADA, orcamento,
                                    random.Random(seed), **PARAMETROS_SA)
            tempo = time.perf_counter() - inicio
            linha = linha_principal(nome, "sa", seed, r, tempo)
            for chave in ("aceitos", "piores_aceitos", "piores_propostos",
                          "t0", "tf", "alfa"):
                linha[chave] = r[chave]
            principal.append(linha)
            for avaliacoes, h in r["historico"]:
                convergencia.append({"instancia": nome, "algoritmo": "sa",
                                     "seed": seed, "avaliacoes": avaliacoes,
                                     "melhor_h": h})
            for avaliacoes, temperatura, taxa in r["aceitacao"]:
                aceitacao.append({"instancia": nome, "seed": seed,
                                  "avaliacoes": avaliacoes,
                                  "temperatura": temperatura,
                                  "taxa_aceitacao_piores": taxa})
            print(f"t3 {nome} sa seed={seed} h={r['melhor_h']} "
                  f"{tempo:.1f}s", flush=True)

            # Genetic Algorithm
            inicio = time.perf_counter()
            r = genetic_algorithm(instancia, orcamento, random.Random(seed),
                                  **PARAMETROS_GA)
            tempo = time.perf_counter() - inicio
            linha = linha_principal(nome, "ga", seed, r, tempo)
            linha["geracoes"] = r["geracoes"]
            principal.append(linha)
            for avaliacoes, h in r["historico"]:
                convergencia.append({"instancia": nome, "algoritmo": "ga",
                                     "seed": seed, "avaliacoes": avaliacoes,
                                     "melhor_h": h})
            for info in r["geracoes_info"]:
                geracoes.append({"instancia": nome, "seed": seed, **info})
            print(f"t3 {nome} ga seed={seed} h={r['melhor_h']} "
                  f"{tempo:.1f}s", flush=True)

        # Salva ao fim de cada instância para não perder o que já rodou.
        salvar_csv(principal, "t3_principal.csv")
        salvar_csv(convergencia, "t3_convergencia.csv")
        salvar_csv(aceitacao, "t3_sa_aceitacao.csv")
        salvar_csv(geracoes, "t3_ga_geracoes.csv")


# ---------------------------------------------------------------------------
# Experimento adicional: o cruzamento OX ajuda?
# ---------------------------------------------------------------------------

def experimento_extra():
    """GA sem cruzamento (pc = 0), demais parâmetros e sementes iguais à T3.

    A comparação é feita com as linhas "ga" de t3_principal.csv, que usam
    as mesmas sementes e o mesmo orçamento.
    """
    parametros = dict(PARAMETROS_GA)
    parametros["pc"] = 0.0
    linhas = []
    for nome, config in CONFIGURACOES.items():
        instancia = carregar_instancia(caminho_instancia(nome))
        for seed in range(config["execucoes"]):
            inicio = time.perf_counter()
            r = genetic_algorithm(instancia, config["orcamento"],
                                  random.Random(seed), **parametros)
            tempo = time.perf_counter() - inicio
            linhas.append({
                "instancia": nome,
                "algoritmo": "ga_sem_cruzamento",
                "seed": seed,
                "melhor_h": r["melhor_h"],
                "avaliacoes": r["avaliacoes"],
                "tempo_segundos": round(tempo, 4),
                "geracoes": r["geracoes"],
                "distintos_final": r["geracoes_info"][-1]["distintos"],
                "distancia_final": r["geracoes_info"][-1]["distancia_media"],
            })
            print(f"extra {nome} seed={seed} h={r['melhor_h']} {tempo:.1f}s",
                  flush=True)
        salvar_csv(linhas, "extra_ga_sem_cruzamento.csv")


def executar_tudo():
    validar()
    experimento_t2()
    experimento_incremental()
    experimento_t3()
    experimento_extra()


if __name__ == "__main__":
    comandos = {
        "validar": validar,
        "t2": experimento_t2,
        "incremental": experimento_incremental,
        "t3": experimento_t3,
        "extra": experimento_extra,
        "tudo": executar_tudo,
    }
    acao = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if acao not in comandos:
        print("uso: python -m src.experimentos "
              "[validar | t2 | incremental | t3 | extra | tudo]")
        sys.exit(1)
    comandos[acao]()
