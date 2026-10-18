"""Testes da validação, pipeline curto de experimentos e análises."""

import os

import pandas as pd

from src import analise, experimentos


def test_validar_retorna_true():
    assert experimentos.validar() is True


def test_gap_calculado_apenas_para_pequena():
    assert analise.calcular_gap_pequena("pequena", 1875) == 0.0
    assert abs(analise.calcular_gap_pequena("pequena", 2062.5) - 10.0) < 1e-9
    assert analise.calcular_gap_pequena("media", 16332) is None
    assert analise.calcular_gap_pequena("grande", 60417) is None


def test_pipeline_experimentos_e_analise_curto(tmp_path, monkeypatch):
    pasta_resultados = str(tmp_path)
    pasta_figuras = os.path.join(pasta_resultados, "figuras")

    config_curta = {
        "pequena": {
            "arquivo": "manutencao_pequena.txt",
            "orcamento": 800,
            "execucoes": 2,
        },
        "media": {
            "arquivo": "manutencao_media.txt",
            "orcamento": 300,
            "execucoes": 2,
        },
        "grande": {
            "arquivo": "manutencao_grande.txt",
            "orcamento": 300,
            "execucoes": 2,
        },
    }

    monkeypatch.setattr(experimentos, "PASTA_RESULTADOS", pasta_resultados)
    monkeypatch.setattr(experimentos, "CONFIGURACOES", config_curta)
    monkeypatch.setattr(experimentos, "EXECUCOES_INCREMENTAL", 1)
    monkeypatch.setattr(
        experimentos,
        "PARAMETROS_SA",
        {"p_inicial": 0.8, "razao_final": 1e-3, "amostras": 20},
    )
    monkeypatch.setattr(
        experimentos,
        "PARAMETROS_GA",
        {"tamanho_populacao": 10, "pc": 0.9, "pm": 0.2,
         "tamanho_torneio": 2, "elites": 1},
    )

    monkeypatch.setattr(analise, "PASTA_RESULTADOS", pasta_resultados)
    monkeypatch.setattr(analise, "PASTA_FIGURAS", pasta_figuras)
    monkeypatch.setattr(analise, "CONFIGURACOES", config_curta)

    experimentos.experimento_t2()
    experimentos.experimento_incremental()
    experimentos.experimento_calibrar_sa("insertion")
    experimentos.experimento_t3("insertion", "first")
    experimentos.experimento_extra()

    for nome_csv in (
        "t2_vizinhancas.csv",
        "incremental.csv",
        "sa_calibracao.csv",
        "t3_principal.csv",
        "t3_greedy_otimos_locais.csv",
        "t3_convergencia.csv",
        "t3_sa_aceitacao.csv",
        "t3_ga_geracoes.csv",
        "extra_ga_sem_cruzamento.csv",
    ):
        assert os.path.exists(os.path.join(pasta_resultados, nome_csv))

    inc = pd.read_csv(os.path.join(pasta_resultados, "incremental.csv"))
    assert "tempo_por_avaliacao" in inc.columns

    analise.analisar_vizinhancas()
    analise.gerar_tabela_principal()
    analise.gerar_boxplots()
    analise.gerar_convergencia()
    analise.gerar_aceitacao_sa()
    analise.gerar_diversidade_ga()

    caminho_tabelas = os.path.join(pasta_resultados, "tabelas.md")
    assert os.path.exists(caminho_tabelas)
    with open(caminho_tabelas, "r", encoding="utf-8") as arq:
        conteudo_md = arq.read()
    assert "melhor valor conhecido" in conteudo_md
    assert "Permutações de ótimo local distintas" in conteudo_md

    for nome_png in (
        "vizinhancas.png",
        "boxplots.png",
        "convergencia.png",
        "sa_aceitacao.png",
        "ga_diversidade.png",
    ):
        assert os.path.exists(os.path.join(pasta_figuras, nome_png))
