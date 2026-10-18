"""Execução dos experimentos do TP2."""

import csv
import os
import random
import sys
import time

from src.genetic_algorithm import genetic_algorithm
from src.greedy import greedy_random_restart
from src.problema import (
    Problema,
    avaliar,
    carregar_instancia,
    instancia_exemplo_figura1,
)
from src.simulated_annealing import calibrar_sa, simulated_annealing
from src.vizinhancas import OPERADORES

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")
PASTA_RESULTADOS = os.path.join(RAIZ, "resultados")

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

H_OTIMO_PEQUENA = 1875

PARAMETROS_SA = {"p_inicial": 0.8, "razao_final": 1e-3, "amostras": 200}
SEED_CALIBRACAO_SA = 42
PARAMETROS_GA = {
    "tamanho_populacao": 60,
    "pc": 0.9,
    "pm": 0.2,
    "tamanho_torneio": 3,
    "elites": 2,
}

EXECUCOES_INCREMENTAL = 3


def caminho_instancia(nome):
    """Devolve o caminho do arquivo da instância."""
    return os.path.join(PASTA_DADOS, CONFIGURACOES[nome]["arquivo"])


def criar_problema(nome, orcamento=None):
    """Carrega a instância e devolve a interface Problema."""
    instancia = carregar_instancia(caminho_instancia(nome))
    return Problema(instancia, orcamento=orcamento)


def salvar_csv(linhas, nome_arquivo, colunas=None):
    """Salva uma lista de dicionários em resultados/."""
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    caminho = os.path.join(PASTA_RESULTADOS, nome_arquivo)
    if colunas is None:
        colunas = list(linhas[0].keys())
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def texto_solucao(solucao):
    return " ".join(str(ativo) for ativo in solucao)


def distintos(otimos_locais):
    return len(set(tuple(solucao) for solucao, _ in otimos_locais))


def validar():
    """Executa as verificações de h exigidas na Tarefa 1."""
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


def experimento_t2():
    """Compara Swap, Insertion e 2-opt com Best e First Improvement (T2)."""
    linhas = []
    for nome, config in CONFIGURACOES.items():
        problema = criar_problema(nome)
        for variante in ("best", "first"):
            for operador in OPERADORES:
                for seed in range(config["execucoes"]):
                    inicio = time.perf_counter()
                    r = greedy_random_restart(
                        problema, operador, variante, config["orcamento"],
                        random.Random(seed),
                    )
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
    """Compara o tempo da avaliação completa com a incremental no Greedy."""
    linhas = []
    for nome, config in CONFIGURACOES.items():
        problema = criar_problema(nome)
        for operador in OPERADORES:
            for incremental in (False, True):
                for seed in range(EXECUCOES_INCREMENTAL):
                    inicio = time.perf_counter()
                    r = greedy_random_restart(
                        problema, operador, "best", config["orcamento"],
                        random.Random(seed), incremental,
                    )
                    tempo = time.perf_counter() - inicio
                    tempo_por_aval = tempo / r["avaliacoes"]
                    linhas.append({
                        "instancia": nome,
                        "vizinhanca": operador,
                        "incremental": incremental,
                        "seed": seed,
                        "melhor_h": r["melhor_h"],
                        "avaliacoes": r["avaliacoes"],
                        "passos": r["passos"],
                        "tempo_segundos": round(tempo, 6),
                        "tempo_por_avaliacao": round(tempo_por_aval, 9),
                    })
                    print(f"incremental {nome} {operador} {incremental} "
                          f"seed={seed} h={r['melhor_h']} {tempo:.2f}s",
                          flush=True)
        salvar_csv(linhas, "incremental.csv")


def experimento_calibrar_sa(vizinhanca=None):
    """Calibra T0, Tf e alfa fixos por instância antes das execuções da T3."""
    if vizinhanca is not None and vizinhanca not in OPERADORES:
        raise ValueError(f"vizinhança inválida: {vizinhanca}")

    operadores = (vizinhanca,) if vizinhanca is not None else OPERADORES
    linhas = []

    for nome, config in CONFIGURACOES.items():
        problema = criar_problema(nome)
        orcamento = config["orcamento"]
        for operador in operadores:
            cal = calibrar_sa(
                problema, operador, orcamento,
                rng=random.Random(SEED_CALIBRACAO_SA),
                **PARAMETROS_SA,
            )
            linhas.append({
                "instancia": nome,
                "vizinhanca": operador,
                "orcamento": orcamento,
                "amostras": PARAMETROS_SA["amostras"],
                "p_inicial": PARAMETROS_SA["p_inicial"],
                "razao_final": PARAMETROS_SA["razao_final"],
                "delta_medio": round(cal["delta_medio"], 4),
                "t0": cal["t0"],
                "tf": cal["tf"],
                "alfa": cal["alfa"],
            })
            print(
                f"calibrar_sa {nome} {operador}: "
                f"delta_medio={cal['delta_medio']:.2f} "
                f"T0={cal['t0']:.2f} Tf={cal['tf']:.4f} "
                f"alfa={cal['alfa']:.8f}",
                flush=True,
            )

    salvar_csv(linhas, "sa_calibracao.csv")
    return linhas


def carregar_calibracao_sa(vizinhanca):
    """Lê os parâmetros T0, Tf e alfa calibrados para a vizinhança escolhida."""
    caminho = os.path.join(PASTA_RESULTADOS, "sa_calibracao.csv")
    if not os.path.exists(caminho):
        experimento_calibrar_sa(vizinhanca)

    parametros = {}
    with open(caminho, "r", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            if linha["vizinhanca"] == vizinhanca:
                parametros[linha["instancia"]] = {
                    "t0": float(linha["t0"]),
                    "tf": float(linha["tf"]),
                    "alfa": float(linha["alfa"]),
                }

    if set(parametros.keys()) != set(CONFIGURACOES.keys()):
        experimento_calibrar_sa(vizinhanca)
        return carregar_calibracao_sa(vizinhanca)

    return parametros


def linha_principal(nome, algoritmo, seed, r, tempo):
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


def experimento_t3(vizinhanca, variante_greedy):
    """Executa o protocolo oficial da T3 com a vizinhança e variante escolhidas."""
    if vizinhanca not in OPERADORES:
        raise ValueError(f"vizinhança inválida: {vizinhanca}")
    if variante_greedy not in ("best", "first"):
        raise ValueError(f"variante do Greedy inválida: {variante_greedy}")

    calibracao_sa = carregar_calibracao_sa(vizinhanca)

    principal = []
    otimos_greedy = []
    convergencia = []
    aceitacao = []
    geracoes = []

    for nome, config in CONFIGURACOES.items():
        problema = criar_problema(nome)
        orcamento = config["orcamento"]
        params_sa = calibracao_sa[nome]

        for seed in range(config["execucoes"]):
            inicio = time.perf_counter()
            r = greedy_random_restart(
                problema, vizinhanca, variante_greedy, orcamento,
                random.Random(seed),
            )
            tempo = time.perf_counter() - inicio
            linha = linha_principal(nome, "greedy", seed, r, tempo)
            linha["passos"] = r["passos"]
            linha["restarts"] = r["restarts"]
            linha["otimos_locais_distintos"] = distintos(r["otimos_locais"])
            principal.append(linha)

            for idx_restart, (sol_otimo, h_otimo) in enumerate(r["otimos_locais"]):
                otimos_greedy.append({
                    "instancia": nome,
                    "seed": seed,
                    "restart": idx_restart,
                    "h": h_otimo,
                    "solucao": texto_solucao(sol_otimo),
                })

            for avaliacoes, h in r["historico"]:
                convergencia.append({
                    "instancia": nome,
                    "algoritmo": "greedy",
                    "seed": seed,
                    "avaliacoes": avaliacoes,
                    "melhor_h": h,
                })
            print(f"t3 {nome} greedy ({vizinhanca}/{variante_greedy}) "
                  f"seed={seed} h={r['melhor_h']} {tempo:.1f}s", flush=True)

            inicio = time.perf_counter()
            r = simulated_annealing(
                problema, vizinhanca, orcamento, random.Random(seed),
                t0=params_sa["t0"], tf=params_sa["tf"], alfa=params_sa["alfa"],
            )
            tempo = time.perf_counter() - inicio
            linha = linha_principal(nome, "sa", seed, r, tempo)
            for chave in ("aceitos", "piores_aceitos", "piores_propostos",
                          "t0", "tf", "alfa"):
                linha[chave] = r[chave]
            principal.append(linha)
            for avaliacoes, h in r["historico"]:
                convergencia.append({
                    "instancia": nome,
                    "algoritmo": "sa",
                    "seed": seed,
                    "avaliacoes": avaliacoes,
                    "melhor_h": h,
                })
            for avaliacoes, temperatura, taxa in r["aceitacao"]:
                aceitacao.append({
                    "instancia": nome,
                    "seed": seed,
                    "avaliacoes": avaliacoes,
                    "temperatura": temperatura,
                    "taxa_aceitacao_piores": taxa,
                })
            print(f"t3 {nome} sa ({vizinhanca}) seed={seed} "
                  f"h={r['melhor_h']} {tempo:.1f}s", flush=True)

            inicio = time.perf_counter()
            r = genetic_algorithm(
                problema, orcamento, random.Random(seed), **PARAMETROS_GA
            )
            tempo = time.perf_counter() - inicio
            linha = linha_principal(nome, "ga", seed, r, tempo)
            linha["geracoes"] = r["geracoes"]
            principal.append(linha)
            for avaliacoes, h in r["historico"]:
                convergencia.append({
                    "instancia": nome,
                    "algoritmo": "ga",
                    "seed": seed,
                    "avaliacoes": avaliacoes,
                    "melhor_h": h,
                })
            for info in r["geracoes_info"]:
                geracoes.append({"instancia": nome, "seed": seed, **info})
            print(f"t3 {nome} ga seed={seed} h={r['melhor_h']} "
                  f"{tempo:.1f}s", flush=True)

        salvar_csv(principal, "t3_principal.csv")
        salvar_csv(
            otimos_greedy,
            "t3_greedy_otimos_locais.csv",
            colunas=["instancia", "seed", "restart", "h", "solucao"],
        )
        salvar_csv(convergencia, "t3_convergencia.csv")
        salvar_csv(aceitacao, "t3_sa_aceitacao.csv")
        salvar_csv(geracoes, "t3_ga_geracoes.csv")


def experimento_extra():
    """Executa o GA sem cruzamento (pc = 0) com as mesmas sementes da T3."""
    parametros = dict(PARAMETROS_GA)
    parametros["pc"] = 0.0
    linhas = []
    for nome, config in CONFIGURACOES.items():
        problema = criar_problema(nome)
        for seed in range(config["execucoes"]):
            inicio = time.perf_counter()
            r = genetic_algorithm(
                problema, config["orcamento"], random.Random(seed),
                **parametros,
            )
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


def _ler_opcoes_t3(args):
    vizinhanca = None
    variante = None
    posicionais = []
    i = 0
    while i < len(args):
        if args[i] == "--vizinhanca" and i + 1 < len(args):
            vizinhanca = args[i + 1]
            i += 2
        elif args[i] == "--greedy" and i + 1 < len(args):
            variante = args[i + 1]
            i += 2
        else:
            posicionais.append(args[i])
            i += 1

    if vizinhanca is None and len(posicionais) >= 1:
        vizinhanca = posicionais[0]
    if variante is None and len(posicionais) >= 2:
        variante = posicionais[1]
    return vizinhanca, variante


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "uso:\n"
            "  python -m src.experimentos validar\n"
            "  python -m src.experimentos t2\n"
            "  python -m src.experimentos incremental\n"
            "  python -m src.experimentos calibrar_sa [swap|insertion|2opt]\n"
            "  python -m src.experimentos t3 <swap|insertion|2opt> <best|first>\n"
            "  python -m src.experimentos extra"
        )
        sys.exit(1)

    acao = sys.argv[1]
    if acao == "validar":
        validar()
    elif acao == "t2":
        experimento_t2()
    elif acao == "incremental":
        experimento_incremental()
    elif acao == "calibrar_sa":
        op = sys.argv[2] if len(sys.argv) > 2 else None
        experimento_calibrar_sa(op)
    elif acao == "t3":
        viz, var = _ler_opcoes_t3(sys.argv[2:])
        if viz not in OPERADORES or var not in ("best", "first"):
            print(
                "uso: python -m src.experimentos t3 "
                "<swap|insertion|2opt> <best|first>"
            )
            sys.exit(1)
        experimento_t3(viz, var)
    elif acao == "extra":
        experimento_extra()
    else:
        print(f"comando desconhecido: {acao}")
        sys.exit(1)
