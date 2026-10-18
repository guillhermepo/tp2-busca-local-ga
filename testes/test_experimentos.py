"""Testes da rotina de validação, experimentos curtos e geração de análises."""

import os

from src import analise, experimentos


def test_validar_retorna_true():
    assert experimentos.validar() is True


def test_pipeline_experimentos_e_analise_curto(tmp_path, monkeypatch):
    pasta_resultados = str(tmp_path)
    pasta_figuras = os.path.join(pasta_resultados, "figuras")

    config_curta = {
        "pequena": {
            "arquivo": "manutencao_pequena.txt",
            "orcamento": 300,
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
        "PARAMETROS_GA",
        {"tamanho_populacao": 10, "pc": 0.9, "pm": 0.2,
         "tamanho_torneio": 2, "elites": 1},
    )

    monkeypatch.setattr(analise, "PASTA_RESULTADOS", pasta_resultados)
    monkeypatch.setattr(analise, "PASTA_FIGURAS", pasta_figuras)
    monkeypatch.setattr(analise, "CONFIGURACOES", config_curta)

    experimentos.executar_tudo()

    for nome_csv in (
        "t2_vizinhancas.csv",
        "incremental.csv",
        "t3_principal.csv",
        "t3_convergencia.csv",
        "t3_sa_aceitacao.csv",
        "t3_ga_geracoes.csv",
        "extra_ga_sem_cruzamento.csv",
    ):
        assert os.path.exists(os.path.join(pasta_resultados, nome_csv))

    analise.executar_tudo()

    assert os.path.exists(os.path.join(pasta_resultados, "tabelas.md"))
    for nome_png in (
        "vizinhancas.png",
        "boxplots.png",
        "convergencia.png",
        "sa_aceitacao.png",
        "ga_diversidade.png",
    ):
        assert os.path.exists(os.path.join(pasta_figuras, nome_png))

