"""experimentos.py

Execução dos experimentos oficiais (protocolo da Seção 3 do enunciado).

Uso, a partir da raiz do projeto (veja o README):

    python -m src.experimentos validar       # T1: h(identidade) e h*
    python -m src.experimentos t2            # T2: comparação das vizinhanças
    python -m src.experimentos incremental   # ganho da avaliação incremental
    python -m src.experimentos principal     # T3: Greedy x SA x GA
    python -m src.experimentos extra         # experimento extra do GA
    python -m src.experimentos analise       # tabelas e figuras (a partir dos CSVs)
    python -m src.experimentos tudo          # tudo acima, na ordem

Todos aceitam --rapido (orçamento e execuções reduzidos, escreve em
resultados/rapido/, serve para conferir que o pipeline funciona) e
--processos N.

Contagem de avaliações: o orçamento é medido em avaliações de h, contadas em
UM único lugar (problema.avaliar_com_contagem / avaliar_sufixo_com_contagem,
contador em instancia["avaliacoes"]). Cada execução zera o contador no início.

Reprodutibilidade: a semente de cada execução é uma string derivada de
(instância, algoritmo, variante, vizinhança, índice da execução), logo
rodar de novo produz exatamente os mesmos resultados (exceto o tempo).
Os tempos de parede de execuções em paralelo sofrem alguma contenção; as
medições de tempo comparáveis entre si estão em `incremental`.
"""

import argparse
import csv
import json
import multiprocessing
import os
import random
import time

from src import problema
from src.genetico import algoritmo_genetico
from src.greedy import ESTRATEGIAS, greedy_random_restart
from src.interface import ProblemaManutencao
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

# Reduções do modo --rapido (apenas para testar o pipeline).
RAPIDO = {"orcamento": 3_000, "execucoes": 3}

# Valores de referência (Tabela 1 do enunciado).
REFERENCIAS = {"pequena": 1875, "media": 16332, "grande": 60417}
H_IDENTIDADE_PEQUENA = 4366

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
    "otimos_locais",
    "otimos_distintos",
]

ALGORITMOS = ("greedy", "sa", "ga")


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def caminho_instancia(nome):
    """Caminho do arquivo da instância: "pequena", "media" ou "grande"."""
    return os.path.join(PASTA_DADOS, CONFIGURACOES[nome]["arquivo"])


def pasta_saida(rapido):
    pasta = os.path.join(PASTA_RESULTADOS, "rapido") if rapido else PASTA_RESULTADOS
    os.makedirs(pasta, exist_ok=True)
    return pasta


def salvar_csv(linhas, nome_arquivo, pasta=None, colunas=None):
    """Salva uma lista de dicionários em resultados/ (ou `pasta`).

    Só grava o que receber: não inventa nenhuma linha.
    """
    pasta = pasta or PASTA_RESULTADOS
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, nome_arquivo)
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas or COLUNAS_CSV)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def salvar_json(objeto, nome_arquivo, pasta=None):
    pasta = pasta or PASTA_RESULTADOS
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(objeto, arquivo)
    return caminho


def chave_execucao(tarefa):
    return "|".join(
        str(tarefa[c])
        for c in ("instancia", "algoritmo", "variante", "vizinhanca", "seed")
    )


def parametros_ga(variante):
    """Parâmetros do GA para cada variante do experimento extra."""
    if variante == "ox":
        return {"cruzamento": "ox", "pc": 0.9}
    if variante == "pmx":
        return {"cruzamento": "pmx", "pc": 0.9}
    if variante == "sem_cruzamento":
        return {"cruzamento": "ox", "pc": 0.0}
    raise ValueError(f"variante de GA desconhecida: {variante!r}")


# ---------------------------------------------------------------------------
# Uma execução
# ---------------------------------------------------------------------------

def executar_uma(tarefa):
    """Executa UMA execução de um algoritmo. Roda em processo separado.

    tarefa: dicionário com instancia, algoritmo, variante, vizinhanca, seed,
    orcamento, incremental (opcional) e guardar_extras (opcional).
    Devolve (linha_csv, extras), com extras = histórico de convergência e
    dados específicos do algoritmo (None se guardar_extras for falso).
    """
    instancia = problema.carregar_instancia(caminho_instancia(tarefa["instancia"]))
    algoritmo = tarefa["algoritmo"]
    variante = tarefa["variante"]
    rng = random.Random(chave_execucao(tarefa))
    orcamento = tarefa["orcamento"]
    incremental = tarefa.get("incremental", True)

    if algoritmo == "ga":
        p = parametros_ga(variante)
        prob = ProblemaManutencao(
            instancia, tarefa["vizinhanca"], incremental,
            cruzamento=p["cruzamento"],
        )
    else:
        prob = ProblemaManutencao(instancia, tarefa["vizinhanca"], incremental)

    inicio = time.perf_counter()
    if algoritmo == "greedy":
        res = greedy_random_restart(prob, variante, orcamento, rng)
    elif algoritmo == "sa":
        res = simulated_annealing(prob, orcamento, rng)
    elif algoritmo == "ga":
        res = algoritmo_genetico(prob, orcamento, rng, pc=p["pc"])
    else:
        raise ValueError(f"algoritmo desconhecido: {algoritmo!r}")
    tempo = time.perf_counter() - inicio

    # Conferência independente: o h guardado bate com uma reavaliação.
    assert problema.avaliar(res["melhor_solucao"], instancia) == res["melhor_h"]
    assert res["avaliacoes"] <= orcamento

    otimos = res.get("otimos_locais", [])
    linha = {
        "instancia": tarefa["instancia"],
        "algoritmo": algoritmo,
        "variante": variante,
        "vizinhanca": tarefa["vizinhanca"],
        "seed": tarefa["seed"],
        "melhor_h": res["melhor_h"],
        "avaliacoes": res["avaliacoes"],
        "passos": res["passos"],
        "restarts": res["restarts"],
        "tempo_segundos": round(tempo, 4),
        "otimos_locais": len(otimos),
        "otimos_distintos": len({tuple(s) for s, _ in otimos}),
    }

    extras = None
    if tarefa.get("guardar_extras"):
        extras = {"historico": res["historico"]}
        if algoritmo == "sa":
            extras["taxa_aceitacao"] = res["taxa_aceitacao"]
            extras["parametros"] = {
                "t0": res["t0"], "tf": res["tf"], "alpha": res["alpha"]
            }
        if algoritmo == "ga":
            extras["geracoes"] = res["geracoes"]
        if algoritmo == "greedy":
            extras["otimos_locais_h"] = sorted(h for _, h in otimos)
    return linha, extras


def executar_tarefas(tarefas, processos):
    """Executa as tarefas em paralelo. Devolve [(tarefa, linha, extras)]."""
    # Maiores primeiro, para balancear a carga entre os processos.
    ordenadas = sorted(tarefas, key=lambda t: -t["orcamento"] * (
        problema_tamanho(t["instancia"])))
    resultados = []
    total = len(ordenadas)
    with multiprocessing.Pool(processos) as pool:
        for i, (linha, extras) in enumerate(
                pool.imap_unordered(executar_uma, ordenadas, chunksize=1), 1):
            resultados.append((linha, extras))
            if i % 25 == 0 or i == total:
                print(f"  {i}/{total} execuções concluídas", flush=True)
    # ordem determinística no CSV
    resultados.sort(key=lambda r: (
        list(CONFIGURACOES).index(r[0]["instancia"]), r[0]["algoritmo"],
        r[0]["variante"], r[0]["vizinhanca"], r[0]["seed"]))
    return resultados


_TAMANHOS = {"pequena": 12, "media": 50, "grande": 150}


def problema_tamanho(nome):
    return _TAMANHOS[nome]


def configuracao(nome, rapido):
    cfg = dict(CONFIGURACOES[nome])
    if rapido:
        cfg["orcamento"] = RAPIDO["orcamento"]
        cfg["execucoes"] = RAPIDO["execucoes"]
    return cfg


def montar_tarefas(combinacoes, rapido, guardar_extras=False):
    """combinacoes: lista de (algoritmo, variante, vizinhanca)."""
    tarefas = []
    for nome in CONFIGURACOES:
        cfg = configuracao(nome, rapido)
        for algoritmo, variante, vizinhanca in combinacoes:
            for seed in range(cfg["execucoes"]):
                tarefas.append({
                    "instancia": nome,
                    "algoritmo": algoritmo,
                    "variante": variante,
                    "vizinhanca": vizinhanca,
                    "seed": seed,
                    "orcamento": cfg["orcamento"],
                    "guardar_extras": guardar_extras,
                })
    return tarefas


def rodar_e_salvar(combinacoes, nome_csv, nome_json, rapido, processos):
    pasta = pasta_saida(rapido)
    tarefas = montar_tarefas(combinacoes, rapido, guardar_extras=bool(nome_json))
    print(f"{nome_csv}: {len(tarefas)} execuções", flush=True)
    inicio = time.perf_counter()
    resultados = executar_tarefas(tarefas, processos)
    linhas = [linha for linha, _ in resultados]
    salvar_csv(linhas, nome_csv, pasta)
    if nome_json:
        extras = {
            chave_execucao(linha): ext for linha, ext in resultados
        }
        salvar_json(extras, nome_json, pasta)
    print(f"  gravado em {pasta} ({time.perf_counter() - inicio:.0f}s)",
          flush=True)
    return linhas


# ---------------------------------------------------------------------------
# T1 - validação da função de avaliação
# ---------------------------------------------------------------------------

def validar():
    """T1: reproduz h(identidade) = 4366 e confere h* = 1875 por execução."""
    instancia = problema.carregar_instancia(caminho_instancia("pequena"))
    identidade = list(range(1, instancia["n"] + 1))
    h = problema.avaliar(identidade, instancia)
    print(f"h(identidade, pequena) = {h} (esperado {H_IDENTIDADE_PEQUENA})")
    assert h == H_IDENTIDADE_PEQUENA
    # Exemplo da Figura 1 do enunciado, rota gulosa por proximidade.
    print("Confira também o exemplo da Figura 1 em testes/test_exemplo_figura1.py")
    return h


# ---------------------------------------------------------------------------
# T2 - comparação das vizinhanças
# ---------------------------------------------------------------------------

def escolher_vizinhanca(linhas):
    """Escolhe a vizinhança (e a variante do greedy) a partir dos resultados T2.

    Para cada instância e vizinhança toma-se a MELHOR variante pela média de
    h; divide-se pelo melhor valor entre as vizinhanças (razão >= 1) e
    tira-se a média das razões entre as instâncias. A vizinhança com a menor
    razão média é a adotada; a variante do greedy é a de menor razão média
    dentro dela.
    """
    from collections import defaultdict
    medias = defaultdict(list)
    for r in linhas:
        medias[(r["instancia"], r["vizinhanca"], r["variante"])].append(
            r["melhor_h"])
    medias = {k: sum(v) / len(v) for k, v in medias.items()}

    melhor_por_viz = {}
    for (inst, viz, var), m in medias.items():
        atual = melhor_por_viz.get((inst, viz))
        if atual is None or m < atual:
            melhor_por_viz[(inst, viz)] = m
    razoes = {}
    for viz in OPERADORES:
        rs = []
        for inst in CONFIGURACOES:
            melhor_inst = min(melhor_por_viz[(inst, v)] for v in OPERADORES)
            rs.append(melhor_por_viz[(inst, viz)] / melhor_inst)
        razoes[viz] = sum(rs) / len(rs)
    vizinhanca = min(razoes, key=razoes.get)

    razoes_var = {}
    for var in ESTRATEGIAS:
        rs = []
        for inst in CONFIGURACOES:
            melhor_inst = min(medias[(inst, vizinhanca, v)] for v in ESTRATEGIAS)
            rs.append(medias[(inst, vizinhanca, var)] / melhor_inst)
        razoes_var[var] = sum(rs) / len(rs)
    variante = min(razoes_var, key=razoes_var.get)
    return {
        "vizinhanca": vizinhanca,
        "variante_greedy": variante,
        "razao_media_vizinhanca": razoes,
        "razao_media_variante": razoes_var,
    }


def t2(rapido, processos):
    combinacoes = [("greedy", est, op) for op in OPERADORES
                   for est in ESTRATEGIAS]
    linhas = rodar_e_salvar(combinacoes, "t2_vizinhancas.csv", None, rapido,
                            processos)
    escolha = escolher_vizinhanca(linhas)
    salvar_json(escolha, "t2_escolha.json", pasta_saida(rapido))
    print("  escolha:", escolha["vizinhanca"], escolha["variante_greedy"])
    return escolha


def ler_escolha(rapido):
    caminho = os.path.join(pasta_saida(rapido), "t2_escolha.json")
    if not os.path.exists(caminho):
        raise SystemExit("Rode primeiro `python -m src.experimentos t2`.")
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


# ---------------------------------------------------------------------------
# Ganho da avaliação incremental
# ---------------------------------------------------------------------------

def incremental(rapido):
    """Mede o tempo de parede com e sem avaliação incremental.

    Executa em UM processo (sem paralelismo), o mesmo greedy (Best
    Improvement, mesma semente) em cada vizinhança, com a avaliação completa
    e com a incremental. As duas versões devem fazer exatamente as mesmas
    avaliações e chegar ao mesmo melhor h (verificado aqui).
    """
    orcamento = 3_000 if rapido else 30_000
    linhas = []
    for nome in CONFIGURACOES:
        for operador in OPERADORES:
            par = {}
            for usar in (False, True):
                inst = problema.carregar_instancia(caminho_instancia(nome))
                prob = ProblemaManutencao(inst, operador, incremental=usar)
                rng = random.Random(f"incremental-{nome}-{operador}")
                inicio = time.perf_counter()
                res = greedy_random_restart(prob, "best", orcamento, rng)
                tempo = time.perf_counter() - inicio
                par[usar] = (tempo, res)
                linhas.append({
                    "instancia": nome,
                    "vizinhanca": operador,
                    "incremental": usar,
                    "avaliacoes": res["avaliacoes"],
                    "passos": res["passos"],
                    "melhor_h": res["melhor_h"],
                    "tempo_segundos": round(tempo, 4),
                    "us_por_avaliacao": round(1e6 * tempo / res["avaliacoes"], 3),
                })
            assert par[True][1]["melhor_h"] == par[False][1]["melhor_h"]
            assert par[True][1]["avaliacoes"] == par[False][1]["avaliacoes"]
            ganho = par[False][0] / par[True][0]
            print(f"  {nome:8s} {operador:10s} ganho x{ganho:.2f}", flush=True)
    colunas = ["instancia", "vizinhanca", "incremental", "avaliacoes", "passos",
               "melhor_h", "tempo_segundos", "us_por_avaliacao"]
    salvar_csv(linhas, "incremental.csv", pasta_saida(rapido), colunas)
    return linhas


# ---------------------------------------------------------------------------
# T3 - experimento principal e experimento extra
# ---------------------------------------------------------------------------

def principal(rapido, processos):
    escolha = ler_escolha(rapido)
    viz = escolha["vizinhanca"]
    combinacoes = [
        ("greedy", escolha["variante_greedy"], viz),
        ("sa", "geometrico", viz),
        ("ga", "ox", viz),
    ]
    return rodar_e_salvar(combinacoes, "principal.csv", "principal_extras.json",
                          rapido, processos)


def extra(rapido, processos):
    """Experimento extra: a recombinação ajuda? GA sem cruzamento e com PMX.

    A variante "ox" (Pc = 0.9) já está em principal.csv e é reutilizada na
    análise; aqui rodam apenas as variantes de comparação, com as mesmas
    sementes.
    """
    viz = ler_escolha(rapido)["vizinhanca"]
    combinacoes = [("ga", "sem_cruzamento", viz), ("ga", "pmx", viz)]
    return rodar_e_salvar(combinacoes, "extra_ga.csv", None, rapido, processos)


# ---------------------------------------------------------------------------
# Linha de comando
# ---------------------------------------------------------------------------

def main(argv=None):
    analisador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analisador.add_argument(
        "etapa",
        choices=["validar", "t2", "incremental", "principal", "extra",
                 "analise", "tudo"],
    )
    analisador.add_argument("--rapido", action="store_true",
                            help="orçamento/execuções reduzidos (teste do pipeline)")
    analisador.add_argument("--processos", type=int,
                            default=min(16, os.cpu_count() or 1))
    args = analisador.parse_args(argv)

    etapas = (["validar", "t2", "incremental", "principal", "extra", "analise"]
              if args.etapa == "tudo" else [args.etapa])
    for etapa in etapas:
        print(f"== {etapa} ==", flush=True)
        if etapa == "validar":
            validar()
        elif etapa == "t2":
            t2(args.rapido, args.processos)
        elif etapa == "incremental":
            incremental(args.rapido)
        elif etapa == "principal":
            principal(args.rapido, args.processos)
        elif etapa == "extra":
            extra(args.rapido, args.processos)
        elif etapa == "analise":
            from src import analise
            analise.gerar_tudo(pasta_saida(args.rapido))


if __name__ == "__main__":
    main()
