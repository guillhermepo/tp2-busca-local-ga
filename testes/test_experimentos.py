"""Testes do pipeline de experimentos e da análise (em escala reduzida)."""

import csv
import json
import os

import numpy as np
import pandas as pd
import pytest

from src import analise, experimentos


def tarefa(algoritmo, variante, vizinhanca="insertion", instancia="pequena",
           seed=0, orcamento=1500, **extra):
    t = {"instancia": instancia, "algoritmo": algoritmo, "variante": variante,
         "vizinhanca": vizinhanca, "seed": seed, "orcamento": orcamento,
         "guardar_extras": True}
    t.update(extra)
    return t


def test_validar_reproduz_h_da_identidade():
    assert experimentos.validar() == 4366


@pytest.mark.parametrize("algoritmo,variante", [
    ("greedy", "best"), ("greedy", "first"), ("greedy", "random"),
    ("sa", "geometrico"), ("ga", "ox"), ("ga", "pmx"),
    ("ga", "sem_cruzamento"),
])
def test_executar_uma_gera_linha_completa(algoritmo, variante):
    linha, extras = experimentos.executar_uma(tarefa(algoritmo, variante))
    assert list(linha) == experimentos.COLUNAS_CSV
    assert linha["avaliacoes"] == 1500
    assert linha["melhor_h"] >= 1875
    assert extras["historico"][-1][1] == linha["melhor_h"]


def test_extras_especificos_por_algoritmo():
    _, sa = experimentos.executar_uma(tarefa("sa", "geometrico"))
    assert {"taxa_aceitacao", "parametros"} <= set(sa)
    _, ga = experimentos.executar_uma(tarefa("ga", "ox"))
    assert "geracoes" in ga
    _, gr = experimentos.executar_uma(tarefa("greedy", "best"))
    assert "otimos_locais_h" in gr


def test_execucao_e_reprodutivel_e_depende_da_semente():
    a, _ = experimentos.executar_uma(tarefa("sa", "geometrico", seed=3))
    b, _ = experimentos.executar_uma(tarefa("sa", "geometrico", seed=3))
    c, _ = experimentos.executar_uma(tarefa("sa", "geometrico", seed=4,
                                            orcamento=20000))
    for campo in ("melhor_h", "passos", "avaliacoes"):
        assert a[campo] == b[campo]
    assert c["avaliacoes"] == 20000


def test_algoritmo_desconhecido():
    with pytest.raises(ValueError):
        experimentos.executar_uma(tarefa("tabu", "x"))
    with pytest.raises(ValueError):
        experimentos.parametros_ga("xyz")


def test_orcamentos_oficiais():
    cfg = experimentos.CONFIGURACOES
    assert [cfg[n]["orcamento"] for n in ("pequena", "media", "grande")] == \
        [50_000, 150_000, 300_000]
    assert [cfg[n]["execucoes"] for n in ("pequena", "media", "grande")] == \
        [30, 30, 10]


def test_montar_tarefas_oficiais_conta_execucoes():
    tarefas = experimentos.montar_tarefas([("sa", "geometrico", "swap")],
                                          rapido=False)
    por_inst = {n: sum(t["instancia"] == n for t in tarefas)
                for n in experimentos.CONFIGURACOES}
    assert por_inst == {"pequena": 30, "media": 30, "grande": 10}
    assert {t["seed"] for t in tarefas if t["instancia"] == "grande"} == \
        set(range(10))


def test_salvar_csv_so_grava_o_recebido(tmp_path):
    linha = {c: 0 for c in experimentos.COLUNAS_CSV}
    caminho = experimentos.salvar_csv([linha], "x.csv", str(tmp_path))
    with open(caminho, newline="", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 1 and list(linhas[0]) == experimentos.COLUNAS_CSV


def _linhas_sinteticas():
    """h médio: swap pior que insertion, que é pior que 2opt; first < best."""
    base = {"swap": 300, "insertion": 200, "2opt": 100}
    extra = {"best": 50, "first": 0, "random": 20}
    linhas = []
    for inst in experimentos.CONFIGURACOES:
        for viz, b in base.items():
            for var, e in extra.items():
                for seed in range(3):
                    linhas.append({"instancia": inst, "vizinhanca": viz,
                                   "variante": var, "melhor_h": b + e + seed})
    return linhas


def test_escolher_vizinhanca():
    escolha = experimentos.escolher_vizinhanca(_linhas_sinteticas())
    assert escolha["vizinhanca"] == "2opt"
    assert escolha["variante_greedy"] == "first"
    assert escolha["razao_media_vizinhanca"]["2opt"] == pytest.approx(1.0)


def test_pipeline_rapido_completo(tmp_path, monkeypatch):
    """Roda T2 -> principal -> extra -> análise em escala mínima."""
    monkeypatch.setattr(experimentos, "PASTA_RESULTADOS", str(tmp_path))
    monkeypatch.setitem(experimentos.RAPIDO, "orcamento", 1500)
    monkeypatch.setitem(experimentos.RAPIDO, "execucoes", 2)
    experimentos.t2(rapido=True, processos=2)
    experimentos.principal(rapido=True, processos=2)
    experimentos.extra(rapido=True, processos=2)
    experimentos.incremental(rapido=True)
    pasta = os.path.join(str(tmp_path), "rapido")
    analise.gerar_tudo(pasta)
    for nome in ("t2_vizinhancas.csv", "t2_escolha.json", "principal.csv",
                 "principal_extras.json", "extra_ga.csv", "incremental.csv",
                 "tabelas.md", "figuras/boxplots.png",
                 "figuras/convergencia_grande.png", "figuras/sa_aceitacao.png",
                 "figuras/ga_diversidade.png", "figuras/extra_ga.png",
                 "figuras/t2_vizinhancas.png"):
        assert os.path.exists(os.path.join(pasta, nome)), nome
    df = pd.read_csv(os.path.join(pasta, "principal.csv"))
    assert len(df) == 3 * 3 * 2
    assert (df["avaliacoes"] <= 1500).all()
    with open(os.path.join(pasta, "principal_extras.json")) as f:
        assert len(json.load(f)) == 18


def test_ler_escolha_sem_t2_aborta(tmp_path, monkeypatch):
    monkeypatch.setattr(experimentos, "PASTA_RESULTADOS", str(tmp_path))
    with pytest.raises(SystemExit):
        experimentos.ler_escolha(rapido=False)


# --- análise ---------------------------------------------------------------

def test_mann_whitney_amostras_identicas_e_diferentes():
    assert analise.mann_whitney([5, 5, 5], [5, 5, 5]) == 1.0
    assert analise.mann_whitney(list(range(20)), list(range(100, 120))) < 1e-4


def test_comparar_pares_bonferroni_e_conclusao():
    grupos = {"A": list(range(20)), "B": list(range(100, 120)),
              "C": list(range(100, 120))}
    t = analise.comparar_pares(grupos)
    assert len(t) == 3
    assert (t["alfa (Bonferroni)"] == 0.05 / 3).all()
    ab = t[(t["A"] == "A") & (t["B"] == "B")].iloc[0]
    assert ab["conclusão"] == "A melhor"
    bc = t[(t["A"] == "B") & (t["B"] == "C")].iloc[0]
    assert bc["conclusão"] == "sem diferença significativa"


def test_escada_funcao_em_degrau():
    hist = [(10, 100), (50, 80), (200, 60)]
    valores = analise._escada(hist, np.array([0, 10, 49, 50, 199, 200, 1000]))
    assert list(valores) == [100, 100, 100, 80, 80, 60, 60]


def test_tabela_principal_gap():
    df = pd.DataFrame({
        "instancia": ["pequena"] * 4, "algoritmo": ["sa"] * 4,
        "variante": ["geometrico"] * 4, "vizinhanca": ["swap"] * 4,
        "seed": range(4), "melhor_h": [1875, 1937, 1875, 1937],
        "avaliacoes": 100, "passos": 1, "restarts": 0,
        "tempo_segundos": 1.0, "otimos_locais": 0, "otimos_distintos": 0,
    })
    t = analise.tabela_principal(df)
    assert t.loc[0, "media"] == pytest.approx(1906)
    assert t.loc[0, "minimo"] == 1875
    assert t.loc[0, "gap_melhor_%"] == pytest.approx(0.0)
    assert t.loc[0, "gap_ref_%"] == pytest.approx(100 * 31 / 1875)


def test_tabela_markdown_formata():
    md = analise.tabela_markdown(pd.DataFrame({"a": [1.2345], "b": ["x"]}),
                                 {"a": "{:.1f}"})
    assert md.splitlines()[0] == "| a | b |"
    assert "| 1.2 | x |" in md
