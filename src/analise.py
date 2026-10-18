"""analise.py

Tabelas, testes estatísticos e figuras a partir dos CSVs/JSONs de
resultados/ (nada é inventado: tudo sai dos arquivos gerados por
experimentos.py).

Saídas (na pasta de resultados):
    tabelas.md                          todas as tabelas, em Markdown
    figuras/t2_vizinhancas.png          boxplots das vizinhanças (T2)
    figuras/boxplots.png                Greedy x SA x GA por instância
    figuras/convergencia_<inst>.png     melhor h x avaliações (+ média do GA)
    figuras/sa_aceitacao.png            taxa de aceitação de piores do SA
    figuras/ga_diversidade.png          diversidade da população do GA
    figuras/extra_ga.png                experimento extra (boxplots)

Testes: Mann-Whitney U bilateral (scipy.stats.mannwhitneyu) para cada
comparação par a par dentro de uma instância; o nível de significância é
corrigido por Bonferroni (alfa = 0,05 / nº de comparações do grupo).
"""

import itertools
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

INSTANCIAS = ["pequena", "media", "grande"]
REFERENCIAS = {"pequena": 1875, "media": 16332, "grande": 60417}
CORES = {"Greedy": "#1f77b4", "SA": "#d62728", "GA": "#2ca02c"}
ALFA = 0.05


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def rotulo(linha):
    """Rótulo curto de uma linha de resultados."""
    if linha["algoritmo"] == "greedy":
        return f"Greedy-{linha['variante']}"
    if linha["algoritmo"] == "sa":
        return "SA"
    return "GA" if linha["variante"] == "ox" else f"GA-{linha['variante']}"


def familia(rot):
    return rot.split("-")[0]


def marcar_rotulos(df):
    df = df.copy()
    df["rotulo"] = df.apply(rotulo, axis=1)
    return df


def tabela_markdown(df, formatos=None):
    """Converte um DataFrame em tabela Markdown (sem depender de tabulate)."""
    formatos = formatos or {}
    colunas = list(df.columns)
    linhas = ["| " + " | ".join(str(c) for c in colunas) + " |",
              "|" + "|".join("---" for _ in colunas) + "|"]
    for _, linha in df.iterrows():
        celulas = []
        for c in colunas:
            valor = linha[c]
            if c in formatos and pd.notna(valor):
                celulas.append(formatos[c].format(valor))
            elif isinstance(valor, float):
                celulas.append(f"{valor:.2f}" if pd.notna(valor) else "-")
            else:
                celulas.append(str(valor))
        linhas.append("| " + " | ".join(celulas) + " |")
    return "\n".join(linhas)


def mann_whitney(a, b):
    """p-valor bilateral do teste de Mann-Whitney (1.0 se amostras idênticas)."""
    if len(set(a) | set(b)) == 1:
        return 1.0
    return float(stats.mannwhitneyu(a, b, alternative="two-sided").pvalue)


def comparar_pares(grupos):
    """Comparações par a par: {rotulo: valores} -> DataFrame de p-valores."""
    pares = list(itertools.combinations(grupos, 2))
    alfa = ALFA / max(1, len(pares))
    linhas = []
    for a, b in pares:
        p = mann_whitney(grupos[a], grupos[b])
        med_a, med_b = float(np.median(grupos[a])), float(np.median(grupos[b]))
        significativo = p < alfa
        if not significativo:
            conclusao = "sem diferença significativa"
        else:
            conclusao = f"{a} melhor" if med_a < med_b else f"{b} melhor"
        linhas.append({
            "A": a, "B": b, "mediana A": med_a, "mediana B": med_b,
            "p-valor": p, "alfa (Bonferroni)": alfa, "conclusão": conclusao,
        })
    return pd.DataFrame(linhas)


def formatar_p(p):
    return f"{p:.2e}" if p < 1e-3 else f"{p:.4f}"


# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------

def resumo(df, agrupar):
    """média, desvio, mínimo, mediana, tempo e avaliações por grupo."""
    g = df.groupby(agrupar, sort=False)
    saida = g.agg(
        execucoes=("melhor_h", "size"),
        media=("melhor_h", "mean"),
        desvio=("melhor_h", lambda v: v.std(ddof=1) if len(v) > 1 else 0.0),
        minimo=("melhor_h", "min"),
        mediana=("melhor_h", "median"),
        passos=("passos", "mean"),
        restarts=("restarts", "mean"),
        tempo_s=("tempo_segundos", "mean"),
        avaliacoes=("avaliacoes", "mean"),
    ).reset_index()
    return saida


def tabela_principal(df):
    """Tabela principal: 3 instâncias x 3 algoritmos."""
    df = marcar_rotulos(df)
    t = resumo(df, ["instancia", "rotulo"])
    t["instancia"] = pd.Categorical(t["instancia"], INSTANCIAS, ordered=True)
    t = t.sort_values(["instancia", "rotulo"]).reset_index(drop=True)
    t["referencia"] = t["instancia"].map(REFERENCIAS).astype(float)
    t["gap_ref_%"] = 100 * (t["media"] - t["referencia"]) / t["referencia"]
    t["gap_melhor_%"] = 100 * (t["minimo"] - t["referencia"]) / t["referencia"]
    t["media ± desvio"] = t.apply(
        lambda r: f"{r['media']:.1f} ± {r['desvio']:.1f}", axis=1)
    return t


def tabela_otimos_locais(df):
    """Instância pequena: ótimos locais distintos e execuções que atingem h*."""
    df = marcar_rotulos(df)
    pequena = df[df["instancia"] == "pequena"]
    linhas = []
    for rot, g in pequena.groupby("rotulo", sort=False):
        linhas.append({
            "algoritmo": rot,
            "execuções": len(g),
            "execuções com h = 1875": int((g["melhor_h"] == 1875).sum()),
            "ótimos locais por execução (média)": g["otimos_locais"].mean(),
            "ótimos locais distintos por execução (média)":
                g["otimos_distintos"].mean(),
        })
    return pd.DataFrame(linhas)


def tabela_t2(df):
    df = df.copy()
    t = resumo(df, ["instancia", "vizinhanca", "variante"])
    t["instancia"] = pd.Categorical(t["instancia"], INSTANCIAS, ordered=True)
    t = t.sort_values(["instancia", "vizinhanca", "variante"]).reset_index(
        drop=True)
    extra = df.groupby(["instancia", "vizinhanca", "variante"], sort=False).agg(
        otimos_distintos=("otimos_distintos", "mean"),
    ).reset_index()
    t = t.merge(extra[["instancia", "vizinhanca", "variante",
                       "otimos_distintos"]],
                on=["instancia", "vizinhanca", "variante"])
    t["media ± desvio"] = t.apply(
        lambda r: f"{r['media']:.1f} ± {r['desvio']:.1f}", axis=1)
    return t


def testes_principais(df):
    """Mann-Whitney par a par entre os algoritmos, por instância."""
    df = marcar_rotulos(df)
    saida = []
    for inst in INSTANCIAS:
        sub = df[df["instancia"] == inst]
        grupos = {rot: g["melhor_h"].tolist()
                  for rot, g in sub.groupby("rotulo", sort=False)}
        tabela = comparar_pares(grupos)
        tabela.insert(0, "instância", inst)
        saida.append(tabela)
    return pd.concat(saida, ignore_index=True)


def ranking(tabela):
    """Ranking dos algoritmos por média em cada instância."""
    linhas = {}
    for inst in INSTANCIAS:
        sub = tabela[tabela["instancia"] == inst].sort_values("media")
        linhas[inst] = " < ".join(sub["rotulo"])
    return linhas


def tabela_incremental(df):
    """Ganho de tempo da avaliação incremental por instância e vizinhança."""
    linhas = []
    for (inst, viz), g in df.groupby(["instancia", "vizinhanca"], sort=False):
        completa = g[~g["incremental"].astype(bool)].iloc[0]
        incr = g[g["incremental"].astype(bool)].iloc[0]
        linhas.append({
            "instância": inst,
            "vizinhança": viz,
            "µs/avaliação (completa)": completa["us_por_avaliacao"],
            "µs/avaliação (incremental)": incr["us_por_avaliacao"],
            "ganho": completa["tempo_segundos"] / incr["tempo_segundos"],
            "mesmo h e mesmas avaliações": bool(
                completa["melhor_h"] == incr["melhor_h"]
                and completa["avaliacoes"] == incr["avaliacoes"]),
        })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def _boxplot(ax, grupos, titulo, referencia=None, rotacao=0):
    rotulos = list(grupos)
    caixas = ax.boxplot([grupos[r] for r in rotulos], patch_artist=True,
                        widths=0.6)
    for caixa, rot in zip(caixas["boxes"], rotulos):
        caixa.set_facecolor(CORES.get(familia(rot), "#9a9a9a"))
        caixa.set_alpha(0.6)
    for mediana in caixas["medians"]:
        mediana.set_color("black")
    ax.set_xticks(range(1, len(rotulos) + 1))
    ax.set_xticklabels(rotulos, rotation=rotacao, ha="right" if rotacao else
                       "center")
    if referencia is not None:
        ax.axhline(referencia, color="gray", linestyle="--", linewidth=1,
                   label=f"referência = {referencia}")
        ax.legend(fontsize=8)
    ax.set_title(titulo)
    ax.set_ylabel("melhor h")
    ax.grid(axis="y", alpha=0.3)


def fig_boxplots(df, pasta):
    df = marcar_rotulos(df)
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, inst in zip(eixos, INSTANCIAS):
        sub = df[df["instancia"] == inst]
        grupos = {rot: g["melhor_h"].tolist()
                  for rot, g in sub.groupby("rotulo", sort=False)}
        _boxplot(ax, grupos, f"instância {inst}", REFERENCIAS[inst])
    fig.tight_layout()
    caminho = os.path.join(pasta, "figuras", "boxplots.png")
    fig.savefig(caminho, dpi=130)
    plt.close(fig)


def fig_t2(df, pasta):
    fig, eixos = plt.subplots(1, 3, figsize=(15, 5))
    for ax, inst in zip(eixos, INSTANCIAS):
        sub = df[df["instancia"] == inst]
        grupos = {}
        for (viz, var), g in sub.groupby(["vizinhanca", "variante"],
                                         sort=False):
            grupos[f"{viz}\n{var}"] = g["melhor_h"].tolist()
        _boxplot(ax, grupos, f"instância {inst}", REFERENCIAS[inst])
        ax.tick_params(axis="x", labelsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(pasta, "figuras", "t2_vizinhancas.png"), dpi=130)
    plt.close(fig)


def _escada(historico, grade):
    """Avalia, nos pontos da grade, a função em escada (avaliacoes, valor)."""
    xs = np.array([a for a, _ in historico])
    ys = np.array([v for _, v in historico], dtype=float)
    idx = np.searchsorted(xs, grade, side="right") - 1
    # antes da primeira entrada vale o primeiro valor (curva começa plana)
    return ys[np.clip(idx, 0, None)]


def carregar_extras(pasta):
    caminho = os.path.join(pasta, "principal_extras.json")
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def fig_convergencia(df, extras, pasta):
    for inst in INSTANCIAS:
        orcamento = orcamento_efetivo(df, inst)
        grade = np.linspace(0, orcamento, 400)
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        sub = marcar_rotulos(df[df["instancia"] == inst])
        for rot in sub["rotulo"].unique():
            chaves = [
                f"{r.instancia}|{r.algoritmo}|{r.variante}|{r.vizinhanca}|{r.seed}"
                for r in sub[sub["rotulo"] == rot].itertuples()
            ]
            curvas = np.array([_escada(extras[k]["historico"], grade)
                               for k in chaves])
            mediana = np.nanmedian(curvas, axis=0)
            ax.plot(grade, mediana, label=f"{rot} (mediana do melhor h)",
                    color=CORES[familia(rot)], linewidth=2)
            if familia(rot) == "GA":
                medias = np.array([
                    _escada([(g["avaliacoes"], g["media_h"])
                             for g in extras[k]["geracoes"]], grade)
                    for k in chaves])
                ax.plot(grade, np.nanmedian(medias, axis=0),
                        label="GA (mediana da média da população)",
                        color=CORES["GA"], linestyle="--", linewidth=1.5)
        ax.axhline(REFERENCIAS[inst], color="gray", linestyle=":",
                   label=f"referência = {REFERENCIAS[inst]}")
        ax.set_yscale("log")
        ax.set_xlabel("avaliações de h")
        ax.set_ylabel("h (escala log)")
        ax.set_title(f"Convergência - instância {inst}")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(pasta, "figuras",
                                 f"convergencia_{inst}.png"), dpi=130)
        plt.close(fig)


def orcamento_efetivo(df, inst):
    """Orçamento realmente usado (máximo de avaliações nas linhas da instância)."""
    return int(df[df["instancia"] == inst]["avaliacoes"].max())


def fig_sa(df, extras, pasta, bins=60):
    fig, eixos = plt.subplots(1, 3, figsize=(15, 4.2))
    sa = df[df["algoritmo"] == "sa"]
    for ax, inst in zip(eixos, INSTANCIAS):
        orcamento = orcamento_efetivo(df, inst)
        limites = np.linspace(0, orcamento, bins + 1)
        propostos = np.zeros(bins)
        aceitos = np.zeros(bins)
        temperatura = []
        for r in sa[sa["instancia"] == inst].itertuples():
            k = f"{r.instancia}|{r.algoritmo}|{r.variante}|{r.vizinhanca}|{r.seed}"
            niveis = extras[k]["taxa_aceitacao"]
            xs = np.array([n[0] for n in niveis])
            idx = np.clip(np.searchsorted(limites, xs, side="right") - 1, 0,
                          bins - 1)
            for i, (_, _, prop, ace) in zip(idx, niveis):
                propostos[i] += prop
                aceitos[i] += ace
            temperatura.append(_escada([(n[0], n[1]) for n in niveis],
                                       limites[1:]))
        centros = (limites[:-1] + limites[1:]) / 2
        taxa = np.where(propostos > 0, aceitos / np.maximum(propostos, 1),
                        np.nan)
        ax.plot(centros, taxa, color=CORES["SA"], linewidth=2)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel("avaliações de h")
        ax.set_ylabel("taxa de aceitação de movimentos piores")
        ax.set_title(f"SA - instância {inst}")
        ax.grid(alpha=0.3)
        ax2 = ax.twinx()
        ax2.plot(centros, np.nanmedian(temperatura, axis=0), color="gray",
                 linestyle="--", linewidth=1)
        ax2.set_yscale("log")
        ax2.set_ylabel("temperatura T (mediana)", color="gray")
    fig.tight_layout()
    fig.savefig(os.path.join(pasta, "figuras", "sa_aceitacao.png"), dpi=130)
    plt.close(fig)


def fig_ga(df, extras, pasta):
    fig, eixos = plt.subplots(2, 3, figsize=(15, 7), sharex="col")
    ga = df[(df["algoritmo"] == "ga") & (df["variante"] == "ox")]
    for coluna, inst in enumerate(INSTANCIAS):
        grade = np.linspace(0, orcamento_efetivo(df, inst), 300)
        distintos, distancia = [], []
        for r in ga[ga["instancia"] == inst].itertuples():
            k = f"{r.instancia}|{r.algoritmo}|{r.variante}|{r.vizinhanca}|{r.seed}"
            ger = extras[k]["geracoes"]
            distintos.append(_escada([(g["avaliacoes"], g["distintos"])
                                      for g in ger], grade))
            distancia.append(_escada([(g["avaliacoes"], g["distancia_media"])
                                      for g in ger], grade))
        for linha, (curvas, nome) in enumerate(
                [(distintos, "cromossomos distintos"),
                 (distancia, "distância média entre pares")]):
            ax = eixos[linha][coluna]
            curvas = np.array(curvas)
            ax.plot(grade, np.nanmedian(curvas, axis=0), color=CORES["GA"],
                    linewidth=2)
            ax.fill_between(grade, np.nanmin(curvas, axis=0),
                            np.nanmax(curvas, axis=0), color=CORES["GA"],
                            alpha=0.15)
            ax.set_ylabel(nome)
            ax.grid(alpha=0.3)
            if linha == 0:
                ax.set_title(f"GA - instância {inst}")
            else:
                ax.set_xlabel("avaliações de h")
    fig.tight_layout()
    fig.savefig(os.path.join(pasta, "figuras", "ga_diversidade.png"), dpi=130)
    plt.close(fig)


def fig_extra(df, pasta):
    df = marcar_rotulos(df)
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.5))
    for ax, inst in zip(eixos, INSTANCIAS):
        sub = df[df["instancia"] == inst]
        grupos = {rot: g["melhor_h"].tolist()
                  for rot, g in sub.groupby("rotulo", sort=False)}
        _boxplot(ax, grupos, f"instância {inst}", REFERENCIAS[inst],
                 rotacao=20)
    fig.tight_layout()
    fig.savefig(os.path.join(pasta, "figuras", "extra_ga.png"), dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def gerar_tudo(pasta):
    """Gera tabelas.md e figuras/ a partir do que existir em `pasta`."""
    os.makedirs(os.path.join(pasta, "figuras"), exist_ok=True)
    partes = ["# Tabelas geradas por `python -m src.experimentos analise`\n"]

    def ler(nome):
        caminho = os.path.join(pasta, nome)
        return pd.read_csv(caminho) if os.path.exists(caminho) else None

    fmt_res = {"media": "{:.1f}", "desvio": "{:.1f}", "mediana": "{:.1f}",
               "passos": "{:.0f}", "restarts": "{:.1f}", "tempo_s": "{:.2f}",
               "avaliacoes": "{:.0f}", "gap_ref_%": "{:+.2f}",
               "gap_melhor_%": "{:+.2f}", "otimos_distintos": "{:.1f}"}

    t2 = ler("t2_vizinhancas.csv")
    if t2 is not None:
        tabela = tabela_t2(t2)
        partes.append("## T2 - Vizinhanças (Greedy Descent + Random Restart)\n")
        partes.append(tabela_markdown(
            tabela[["instancia", "vizinhanca", "variante", "media ± desvio",
                    "minimo", "mediana", "passos", "restarts",
                    "otimos_distintos", "tempo_s"]], fmt_res) + "\n")
        escolha = os.path.join(pasta, "t2_escolha.json")
        if os.path.exists(escolha):
            with open(escolha, encoding="utf-8") as f:
                e = json.load(f)
            partes.append(
                f"Escolha automática: vizinhança **{e['vizinhanca']}**, "
                f"variante do greedy **{e['variante_greedy']}**. "
                f"Razão média ao melhor (1,0 = melhor): "
                f"{json.dumps({k: round(v, 3) for k, v in e['razao_media_vizinhanca'].items()}, ensure_ascii=False)}\n")
        # testes entre vizinhanças usando a melhor variante de cada uma
        partes.append("### Testes entre vizinhanças (melhor variante de cada)\n")
        for inst in INSTANCIAS:
            sub = t2[t2["instancia"] == inst]
            melhores = {}
            for viz, g in sub.groupby("vizinhanca"):
                var = g.groupby("variante")["melhor_h"].mean().idxmin()
                melhores[f"{viz}-{var}"] = g[g["variante"] == var][
                    "melhor_h"].tolist()
            comp = comparar_pares(melhores)
            comp["p-valor"] = comp["p-valor"].map(formatar_p)
            partes.append(f"**{inst}**\n")
            partes.append(tabela_markdown(comp) + "\n")
        fig_t2(t2, pasta)

    inc = ler("incremental.csv")
    if inc is not None:
        partes.append("## Avaliação incremental (tempo de parede)\n")
        partes.append(tabela_markdown(
            tabela_incremental(inc),
            {"µs/avaliação (completa)": "{:.2f}",
             "µs/avaliação (incremental)": "{:.2f}", "ganho": "x{:.2f}"})
            + "\n")

    principal = ler("principal.csv")
    if principal is not None:
        tabela = tabela_principal(principal)
        partes.append("## Tabela principal (Greedy x SA x GA)\n")
        partes.append(tabela_markdown(
            tabela[["instancia", "rotulo", "media ± desvio", "minimo",
                    "mediana", "gap_ref_%", "gap_melhor_%", "passos",
                    "restarts", "tempo_s", "avaliacoes"]], fmt_res) + "\n")
        partes.append("gap_ref_% = (média - referência)/referência; "
                      "gap_melhor_% = (melhor - referência)/referência. "
                      "Referências: 1875 (ótimo, pequena), 16332 e 60417 "
                      "(melhores conhecidos).\n")
        partes.append("Ranking por média (menor = melhor):\n")
        for inst, r in ranking(tabela).items():
            partes.append(f"- {inst}: {r}")
        partes.append("")
        partes.append("## Testes de Mann-Whitney (par a par)\n")
        tm = testes_principais(principal)
        tm["p-valor"] = tm["p-valor"].map(formatar_p)
        partes.append(tabela_markdown(tm) + "\n")
        partes.append("## Ótimos locais e h* na instância pequena\n")
        partes.append(tabela_markdown(tabela_otimos_locais(principal)) + "\n")
        fig_boxplots(principal, pasta)
        if os.path.exists(os.path.join(pasta, "principal_extras.json")):
            extras = carregar_extras(pasta)
            fig_convergencia(principal, extras, pasta)
            fig_sa(principal, extras, pasta)
            fig_ga(principal, extras, pasta)

            # resumo da diversidade final e da aceitação, para o texto
            partes.append("## Diversidade do GA (final da execução, mediana)\n")
            linhas = []
            for inst in INSTANCIAS:
                finais = [
                    (extras[k]["geracoes"][-1]["distintos"],
                     extras[k]["geracoes"][-1]["distancia_media"])
                    for k in extras if k.startswith(f"{inst}|ga|")]
                linhas.append({
                    "instância": inst,
                    "distintos (de N=50)": float(np.median([f[0] for f in finais])),
                    "distância média": float(np.median([f[1] for f in finais])),
                })
            partes.append(tabela_markdown(pd.DataFrame(linhas)) + "\n")

            partes.append("## Parâmetros calibrados do SA (mediana)\n")
            linhas = []
            for inst in INSTANCIAS:
                ps = [extras[k]["parametros"] for k in extras
                      if k.startswith(f"{inst}|sa|")]
                linhas.append({
                    "instância": inst,
                    "T0": float(np.median([p["t0"] for p in ps])),
                    "Tf": float(np.median([p["tf"] for p in ps])),
                    "alpha": float(np.median([p["alpha"] for p in ps])),
                })
            partes.append(tabela_markdown(
                pd.DataFrame(linhas),
                {"T0": "{:.1f}", "Tf": "{:.3f}", "alpha": "{:.6f}"}) + "\n")

    extra = ler("extra_ga.csv")
    if extra is not None and principal is not None:
        ga_ox = principal[(principal["algoritmo"] == "ga")]
        tudo = pd.concat([ga_ox, extra], ignore_index=True)
        partes.append("## Experimento extra: a recombinação ajuda no GA?\n")
        tabela = tabela_principal(tudo)
        partes.append(tabela_markdown(
            tabela[["instancia", "rotulo", "media ± desvio", "minimo",
                    "mediana", "tempo_s"]], fmt_res) + "\n")
        tm = testes_principais(tudo)
        tm["p-valor"] = tm["p-valor"].map(formatar_p)
        partes.append(tabela_markdown(tm) + "\n")
        fig_extra(tudo, pasta)

    caminho = os.path.join(pasta, "tabelas.md")
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(partes))
    print(f"  tabelas em {caminho}")
    return caminho
