"""analise.py

Processamento dos CSVs de resultados/, testes estatísticos (Mann-Whitney) e
geração das tabelas e figuras do relatório.

Uso, a partir da raiz do projeto:

    python -m src.analise vizinhancas   # tabela e figura da T2 + incremental
    python -m src.analise tabela        # tabela principal (T3), testes e extra
    python -m src.analise boxplots      # boxplots por instância (T3)
    python -m src.analise convergencia  # curvas de convergência (T3)
    python -m src.analise aceitacao     # taxa de aceitação de piores do SA
    python -m src.analise diversidade   # diversidade da população do GA
    python -m src.analise tudo          # executa todos os itens acima
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from src.experimentos import CONFIGURACOES, H_OTIMO_PEQUENA, PASTA_RESULTADOS
from src.vizinhancas import OPERADORES, tamanho_vizinhanca

PASTA_FIGURAS = os.path.join(PASTA_RESULTADOS, "figuras")
INSTANCIAS = ("pequena", "media", "grande")
REFERENCIAS = {"pequena": H_OTIMO_PEQUENA, "media": 16332, "grande": 60417}
NOMES_ALGORITMOS = {"greedy": "Greedy", "sa": "SA", "ga": "GA"}
CORES = {"greedy": "#1f77b4", "sa": "#d62728", "ga": "#2ca02c"}


def ler_csv(nome_arquivo):
    caminho = os.path.join(PASTA_RESULTADOS, nome_arquivo)
    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo {caminho} não encontrado. Rode primeiro os experimentos."
        )
    return pd.read_csv(caminho)


def mann_whitney(amostra_a, amostra_b):
    """Teste de Mann-Whitney U bilateral; devolve p = 1.0 se tudo for igual."""
    if set(amostra_a) == set(amostra_b) and len(set(amostra_a)) == 1:
        return 1.0
    _, p_valor = stats.mannwhitneyu(amostra_a, amostra_b, alternative="two-sided")
    return float(p_valor)


def formatar_p(p):
    return f"{p:.2e}" if p < 0.001 else f"{p:.4f}"


# ---------------------------------------------------------------------------
# 1. Comparação das vizinhanças (T2) e avaliação incremental
# ---------------------------------------------------------------------------

def analisar_vizinhancas():
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    df = ler_csv("t2_vizinhancas.csv")

    print("\n=== Tamanho das vizinhanças (produzido pela implementação) ===")
    print("| n | swap | insertion | 2opt |")
    print("|---|---|---|---|")
    for n in (12, 50, 150):
        tamanhos = [tamanho_vizinhanca(n, op) for op in OPERADORES]
        print(f"| {n} | {tamanhos[0]} | {tamanhos[1]} | {tamanhos[2]} |")

    print("\n=== T2: Comparação das vizinhanças (Greedy + Random Restart) ===")
    print("| instância | variante | vizinhança | média ± desvio | mínimo | "
          "mediana | passos | restarts | ótimos distintos | tempo (s) |")
    print("|---|---|---|---|---|---|---|---|---|---|")

    for inst in INSTANCIAS:
        for var in ("best", "first"):
            for op in OPERADORES:
                sub = df[(df["instancia"] == inst)
                         & (df["variante"] == var)
                         & (df["vizinhanca"] == op)]
                if sub.empty:
                    continue
                h = sub["melhor_h"]
                desvio = h.std(ddof=1) if len(h) > 1 else 0.0
                print(
                    f"| {inst} | {var} | {op} | "
                    f"{h.mean():.1f} ± {desvio:.1f} | {int(h.min())} | "
                    f"{h.median():.1f} | {sub['passos'].mean():.1f} | "
                    f"{sub['restarts'].mean():.1f} | "
                    f"{sub['otimos_locais_distintos'].mean():.1f} | "
                    f"{sub['tempo_segundos'].mean():.2f} |"
                )

    print("\n=== Testes de Mann-Whitney na T2 (entre vizinhanças) ===")
    print("| instância | variante | comparação | p-valor |")
    print("|---|---|---|---|")
    pares_op = [("swap", "insertion"), ("swap", "2opt"), ("insertion", "2opt")]
    for inst in INSTANCIAS:
        for var in ("best", "first"):
            for op_a, op_b in pares_op:
                a = df[(df["instancia"] == inst) & (df["variante"] == var)
                       & (df["vizinhanca"] == op_a)]["melhor_h"]
                b = df[(df["instancia"] == inst) & (df["variante"] == var)
                       & (df["vizinhanca"] == op_b)]["melhor_h"]
                if len(a) > 0 and len(b) > 0:
                    p = mann_whitney(a, b)
                    print(f"| {inst} | {var} | {op_a} vs {op_b} | "
                          f"{formatar_p(p)} |")

    caminho_inc = os.path.join(PASTA_RESULTADOS, "incremental.csv")
    if os.path.exists(caminho_inc):
        inc = pd.read_csv(caminho_inc)
        print("\n=== Avaliação completa vs incremental (Greedy best) ===")
        print("| instância | vizinhança | tempo completa (s) | "
              "tempo incremental (s) | ganho (x) | mesmo h e avaliações? |")
        print("|---|---|---|---|---|---|")
        for inst in INSTANCIAS:
            for op in OPERADORES:
                comp = inc[(inc["instancia"] == inst)
                           & (inc["vizinhanca"] == op)
                           & (inc["incremental"] == False)]
                incr = inc[(inc["instancia"] == inst)
                           & (inc["vizinhanca"] == op)
                           & (inc["incremental"] == True)]
                if comp.empty or incr.empty:
                    continue
                t_comp = comp["tempo_segundos"].mean()
                t_incr = incr["tempo_segundos"].mean()
                ganho = t_comp / t_incr if t_incr > 0 else 1.0
                iguais = (
                    list(comp["melhor_h"]) == list(incr["melhor_h"])
                    and list(comp["avaliacoes"]) == list(incr["avaliacoes"])
                )
                print(f"| {inst} | {op} | {t_comp:.2f} | {t_incr:.2f} | "
                      f"{ganho:.2f}x | {'sim' if iguais else 'NÃO'} |")

    # Figura da T2
    fig, eixos = plt.subplots(1, 3, figsize=(14, 4.5))
    for eixo, inst in zip(eixos, INSTANCIAS):
        dados = []
        rotulos = []
        for var in ("best", "first"):
            for op in OPERADORES:
                sub = df[(df["instancia"] == inst)
                         & (df["variante"] == var)
                         & (df["vizinhanca"] == op)]
                if not sub.empty:
                    dados.append(sub["melhor_h"].values)
                    rotulos.append(f"{var}\n{op}")
        if dados:
            eixo.boxplot(dados, tick_labels=rotulos, showmeans=True)
        eixo.set_title(f"Instância {inst}")
        eixo.set_ylabel("Melhor h")
        eixo.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    saida = os.path.join(PASTA_FIGURAS, "vizinhancas.png")
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"\nFigura salva em: {saida}")


# ---------------------------------------------------------------------------
# 2. Tabela principal, testes estatísticos e experimento extra (T3)
# ---------------------------------------------------------------------------

def gerar_tabela_principal():
    df = ler_csv("t3_principal.csv")
    linhas_md = []

    def registrar(texto=""):
        print(texto)
        linhas_md.append(texto)

    registrar("# Tabelas de Resultados — TP2\n")
    registrar("## Tabela Principal (T3)\n")
    registrar(
        "| Instância | Algoritmo | Média ± Desvio | Mínimo | Mediana | "
        "Gap Mínimo (%) | Gap Média (%) | Avaliações | Tempo Médio (s) |"
    )
    registrar("|---|---|---|---|---|---|---|---|---|")

    for inst in INSTANCIAS:
        ref = REFERENCIAS[inst]
        for alg in ("greedy", "sa", "ga"):
            sub = df[(df["instancia"] == inst) & (df["algoritmo"] == alg)]
            if sub.empty:
                continue
            h = sub["melhor_h"]
            desvio = h.std(ddof=1) if len(h) > 1 else 0.0
            gap_min = 100.0 * (h.min() - ref) / ref
            gap_med = 100.0 * (h.mean() - ref) / ref
            registrar(
                f"| {inst} | {NOMES_ALGORITMOS[alg]} | "
                f"{h.mean():.1f} ± {desvio:.1f} | {int(h.min())} | "
                f"{h.median():.1f} | {gap_min:+.2f}% | {gap_med:+.2f}% | "
                f"{int(sub['avaliacoes'].mean())} | "
                f"{sub['tempo_segundos'].mean():.2f} |"
            )

    registrar("\n## Testes Estatísticos Par a Par (Mann-Whitney U bilateral)\n")
    registrar("| Instância | Comparação | Mediana A | Mediana B | p-valor | "
              "Significativo (p < 0,05)? |")
    registrar("|---|---|---|---|---|---|")
    pares = [("greedy", "sa"), ("greedy", "ga"), ("sa", "ga")]
    for inst in INSTANCIAS:
        for a, b in pares:
            va = df[(df["instancia"] == inst)
                    & (df["algoritmo"] == a)]["melhor_h"]
            vb = df[(df["instancia"] == inst)
                    & (df["algoritmo"] == b)]["melhor_h"]
            if va.empty or vb.empty:
                continue
            p = mann_whitney(va, vb)
            sig = "sim" if p < 0.05 else "não"
            registrar(
                f"| {inst} | {NOMES_ALGORITMOS[a]} vs {NOMES_ALGORITMOS[b]} | "
                f"{va.median():.1f} | {vb.median():.1f} | {formatar_p(p)} | "
                f"{sig} |"
            )

    registrar("\n## Ótimos Locais e Alcance de h* = 1875 na Instância Pequena\n")
    peq = df[df["instancia"] == "pequena"]
    if not peq.empty:
        registrar("| Algoritmo | Execuções no ótimo (1875) | "
                  "Ótimos locais distintos médios |")
        registrar("|---|---|---|")
        for alg in ("greedy", "sa", "ga"):
            sub = peq[peq["algoritmo"] == alg]
            if sub.empty:
                continue
            no_otimo = int((sub["melhor_h"] == H_OTIMO_PEQUENA).sum())
            total = len(sub)
            if alg == "greedy" and "otimos_locais_distintos" in sub:
                dist = pd.to_numeric(
                    sub["otimos_locais_distintos"], errors="coerce"
                ).mean()
                texto_dist = f"{dist:.1f}"
            else:
                texto_dist = "-"
            registrar(f"| {NOMES_ALGORITMOS[alg]} | {no_otimo}/{total} | "
                      f"{texto_dist} |")

    caminho_extra = os.path.join(PASTA_RESULTADOS, "extra_ga_sem_cruzamento.csv")
    if os.path.exists(caminho_extra):
        extra = pd.read_csv(caminho_extra)
        registrar("\n## Experimento Adicional: GA com OX vs GA sem Cruzamento "
                  "(Pc = 0)\n")
        registrar("| Instância | GA com OX (média ± desvio) | "
                  "GA sem OX (média ± desvio) | p-valor (Mann-Whitney) |")
        registrar("|---|---|---|---|")
        for inst in INSTANCIAS:
            com_ox = df[(df["instancia"] == inst)
                        & (df["algoritmo"] == "ga")]["melhor_h"]
            sem_ox = extra[extra["instancia"] == inst]["melhor_h"]
            if com_ox.empty or sem_ox.empty:
                continue
            d1 = com_ox.std(ddof=1) if len(com_ox) > 1 else 0.0
            d2 = sem_ox.std(ddof=1) if len(sem_ox) > 1 else 0.0
            p = mann_whitney(com_ox, sem_ox)
            registrar(
                f"| {inst} | {com_ox.mean():.1f} ± {d1:.1f} | "
                f"{sem_ox.mean():.1f} ± {d2:.1f} | {formatar_p(p)} |"
            )

    caminho_md = os.path.join(PASTA_RESULTADOS, "tabelas.md")
    with open(caminho_md, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas_md) + "\n")
    print(f"\nTabelas salvas em: {caminho_md}")


# ---------------------------------------------------------------------------
# 3. Boxplots por instância
# ---------------------------------------------------------------------------

def gerar_boxplots():
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    df = ler_csv("t3_principal.csv")

    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.2))
    for eixo, inst in zip(eixos, INSTANCIAS):
        dados = []
        rotulos = []
        for alg in ("greedy", "sa", "ga"):
            sub = df[(df["instancia"] == inst) & (df["algoritmo"] == alg)]
            if not sub.empty:
                dados.append(sub["melhor_h"].values)
                rotulos.append(NOMES_ALGORITMOS[alg])
        if dados:
            eixo.boxplot(dados, tick_labels=rotulos, showmeans=True)
        if inst == "pequena":
            eixo.axhline(H_OTIMO_PEQUENA, color="black", linestyle="--",
                         linewidth=1, label=f"h* = {H_OTIMO_PEQUENA}")
            eixo.legend()
        eixo.set_title(f"Instância {inst}")
        eixo.set_ylabel("Melhor h ao final do orçamento")
        eixo.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    saida = os.path.join(PASTA_FIGURAS, "boxplots.png")
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Figura salva em: {saida}")


# ---------------------------------------------------------------------------
# 4. Curvas de convergência
# ---------------------------------------------------------------------------

def curva_em_grade(avaliacoes_pontos, valores_pontos, grade):
    """Reconstrói o melhor h acumulado em cada ponto da grade (função degrau)."""
    indices = np.searchsorted(avaliacoes_pontos, grade, side="right") - 1
    indices = np.clip(indices, 0, len(valores_pontos) - 1)
    return valores_pontos[indices]


def gerar_convergencia():
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    conv = ler_csv("t3_convergencia.csv")
    ga_gen = ler_csv("t3_ga_geracoes.csv")

    fig, eixos = plt.subplots(1, 3, figsize=(14, 4.2))
    for eixo, inst in zip(eixos, INSTANCIAS):
        orcamento = CONFIGURACOES[inst]["orcamento"]
        grade = np.linspace(1, orcamento, 200)

        for alg in ("greedy", "sa", "ga"):
            sub = conv[(conv["instancia"] == inst) & (conv["algoritmo"] == alg)]
            if sub.empty:
                continue
            curvas = []
            for _, grupo in sub.groupby("seed"):
                grupo = grupo.sort_values("avaliacoes")
                curvas.append(
                    curva_em_grade(grupo["avaliacoes"].values,
                                   grupo["melhor_h"].values, grade)
                )
            mediana = np.median(curvas, axis=0)
            eixo.plot(grade, mediana, label=NOMES_ALGORITMOS[alg],
                      color=CORES[alg], linewidth=1.8)

        # Curva da média da população do GA (indicador visual de diversidade)
        sub_ga = ga_gen[ga_gen["instancia"] == inst]
        if not sub_ga.empty:
            curvas_media = []
            for _, grupo in sub_ga.groupby("seed"):
                grupo = grupo.sort_values("avaliacoes")
                curvas_media.append(
                    np.interp(grade, grupo["avaliacoes"].values,
                              grupo["media_h"].values)
                )
            mediana_media = np.median(curvas_media, axis=0)
            eixo.plot(grade, mediana_media, label="GA (média da pop.)",
                      color=CORES["ga"], linestyle="--", alpha=0.8)

        eixo.set_title(f"Instância {inst}")
        eixo.set_xlabel("Avaliações de h")
        eixo.set_ylabel("h (mediana das execuções)")
        eixo.grid(True, alpha=0.3)
        eixo.legend()

    fig.tight_layout()
    saida = os.path.join(PASTA_FIGURAS, "convergencia.png")
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Figura salva em: {saida}")


# ---------------------------------------------------------------------------
# 5. Taxa de aceitação de movimentos piores do Simulated Annealing
# ---------------------------------------------------------------------------

def gerar_aceitacao_sa():
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    df = ler_csv("t3_sa_aceitacao.csv")

    fig, eixos = plt.subplots(1, 3, figsize=(14, 4.0))
    for eixo, inst in zip(eixos, INSTANCIAS):
        sub = df[df["instancia"] == inst]
        if sub.empty:
            continue
        orcamento = CONFIGURACOES[inst]["orcamento"]
        grade = np.linspace(1, orcamento, 100)
        curvas = []
        for _, grupo in sub.groupby("seed"):
            grupo = grupo.sort_values("avaliacoes")
            curvas.append(
                np.interp(grade, grupo["avaliacoes"].values,
                          grupo["taxa_aceitacao_piores"].values)
            )
        mediana = np.median(curvas, axis=0)
        q25 = np.percentile(curvas, 25, axis=0)
        q75 = np.percentile(curvas, 75, axis=0)

        eixo.plot(grade, mediana, color=CORES["sa"], linewidth=1.8,
                  label="Mediana")
        eixo.fill_between(grade, q25, q75, color=CORES["sa"], alpha=0.2,
                          label="Quartis 25%–75%")
        eixo.set_ylim(-0.02, 1.02)
        eixo.set_title(f"Instância {inst}")
        eixo.set_xlabel("Avaliações de h")
        eixo.set_ylabel("Taxa de aceitação de movimentos piores")
        eixo.grid(True, alpha=0.3)
        eixo.legend()

    fig.tight_layout()
    saida = os.path.join(PASTA_FIGURAS, "sa_aceitacao.png")
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Figura salva em: {saida}")


# ---------------------------------------------------------------------------
# 6. Diversidade da população do Genetic Algorithm
# ---------------------------------------------------------------------------

def gerar_diversidade_ga():
    os.makedirs(PASTA_FIGURAS, exist_ok=True)
    df = ler_csv("t3_ga_geracoes.csv")

    fig, eixos = plt.subplots(2, 3, figsize=(14, 6.8), sharex="col")
    for col, inst in enumerate(INSTANCIAS):
        sub = df[df["instancia"] == inst]
        if sub.empty:
            continue
        orcamento = CONFIGURACOES[inst]["orcamento"]
        grade = np.linspace(1, orcamento, 100)

        curvas_dist = []
        curvas_hamming = []
        for _, grupo in sub.groupby("seed"):
            grupo = grupo.sort_values("avaliacoes")
            curvas_dist.append(
                np.interp(grade, grupo["avaliacoes"].values,
                          grupo["distintos"].values)
            )
            curvas_hamming.append(
                np.interp(grade, grupo["avaliacoes"].values,
                          grupo["distancia_media"].values)
            )

        eixo_sup = eixos[0, col]
        eixo_sup.plot(grade, np.median(curvas_dist, axis=0),
                      color=CORES["ga"], linewidth=1.8)
        eixo_sup.set_title(f"Instância {inst}")
        if col == 0:
            eixo_sup.set_ylabel("Cromossomos distintos (mediana)")
        eixo_sup.grid(True, alpha=0.3)

        eixo_inf = eixos[1, col]
        eixo_inf.plot(grade, np.median(curvas_hamming, axis=0),
                      color="#9467bd", linewidth=1.8)
        eixo_inf.set_ylim(-0.02, 1.02)
        eixo_inf.set_xlabel("Avaliações de h")
        if col == 0:
            eixo_inf.set_ylabel("Distância média entre pares")
        eixo_inf.grid(True, alpha=0.3)

    fig.tight_layout()
    saida = os.path.join(PASTA_FIGURAS, "ga_diversidade.png")
    fig.savefig(saida, dpi=150)
    plt.close(fig)
    print(f"Figura salva em: {saida}")


def executar_tudo():
    if os.path.exists(os.path.join(PASTA_RESULTADOS, "t2_vizinhancas.csv")):
        analisar_vizinhancas()
    if os.path.exists(os.path.join(PASTA_RESULTADOS, "t3_principal.csv")):
        gerar_tabela_principal()
        gerar_boxplots()
        gerar_convergencia()
        gerar_aceitacao_sa()
        gerar_diversidade_ga()


if __name__ == "__main__":
    comandos = {
        "vizinhancas": analisar_vizinhancas,
        "tabela": gerar_tabela_principal,
        "boxplots": gerar_boxplots,
        "convergencia": gerar_convergencia,
        "aceitacao": gerar_aceitacao_sa,
        "diversidade": gerar_diversidade_ga,
        "tudo": executar_tudo,
    }
    acao = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if acao not in comandos:
        print("uso: python -m src.analise "
              "[vizinhancas | tabela | boxplots | convergencia | "
              "aceitacao | diversidade | tudo]")
        sys.exit(1)
    comandos[acao]()

