"""Testes adicionais do módulo problema: exemplo da Figura 1, validações e
avaliação incremental."""

import itertools
import random
import re

import pytest

from src import problema, vizinhancas


def test_figura1_rota_gulosa_custa_39(exemplo_figura1):
    assert problema.avaliar([1, 4, 2, 3], exemplo_figura1) == 39


def test_figura1_otimo_custa_22(exemplo_figura1):
    assert problema.avaliar([1, 4, 3, 2], exemplo_figura1) == 22


def test_figura1_otimo_por_forca_bruta(exemplo_figura1):
    melhor = min(
        itertools.permutations(range(1, 5)),
        key=lambda p: problema.avaliar(list(p), exemplo_figura1),
    )
    assert list(melhor) == [1, 4, 3, 2]
    assert problema.avaliar(list(melhor), exemplo_figura1) == 22


def test_figura1_cronograma(exemplo_figura1):
    C, H = problema.prefixos([1, 4, 2, 3], exemplo_figura1)
    assert C == [0, 7, 16, 27, 38]
    assert H == [0, 0, 0, 13, 39]


def test_somas_das_duracoes_conferem_com_enunciado(pequena, media, grande):
    def soma(inst):
        return sum(a["p"] for a in inst["ativos"])

    assert soma(pequena) == 55
    assert soma(media) == 239
    assert soma(grande) == 684
    assert grande["n"] == 150


def test_tamanhos_das_instancias(pequena, media):
    assert pequena["n"] == 12 and media["n"] == 50


def test_arquivo_inconsistente_gera_erro(tmp_path):
    arquivo = tmp_path / "ruim.txt"
    arquivo.write_text("3\n0 0\n1 1 1 1 1\n")
    with pytest.raises(ValueError):
        problema.carregar_instancia(str(arquivo))


def test_instancia_minima_de_um_ativo(tmp_path):
    arquivo = tmp_path / "um.txt"
    arquivo.write_text("1\n0 0\n3 4 2 5 7\n")
    inst = problema.carregar_instancia(str(arquivo))
    # chega em t=5, conclui em 7; atraso 2; custo 7*2
    assert problema.avaliar([1], inst) == 14


def test_solucao_vazia_custa_zero(pequena):
    assert problema.avaliar([], pequena) == 0


@pytest.mark.parametrize("operador", vizinhancas.OPERADORES)
def test_avaliacao_incremental_igual_a_completa(media, operador):
    rng = random.Random(11)
    for _ in range(30):
        solucao = problema.solucao_aleatoria(media["n"], rng)
        C, H = problema.prefixos(solucao, media)
        for _ in range(40):
            mov = vizinhancas.movimento_aleatorio(media["n"], operador, rng)
            viz = vizinhancas.aplicar_movimento(solucao, mov, operador)
            k = vizinhancas.primeira_posicao_afetada(mov, operador)
            assert problema.avaliar_sufixo(viz, media, k, C, H) == \
                problema.avaliar(viz, media)


@pytest.mark.parametrize("operador", vizinhancas.OPERADORES)
def test_incremental_vizinhanca_completa_pequena(pequena, operador):
    solucao = problema.solucao_aleatoria(pequena["n"], 3)
    C, H = problema.prefixos(solucao, pequena)
    for mov in vizinhancas.movimentos(pequena["n"], operador):
        viz = vizinhancas.aplicar_movimento(solucao, mov, operador)
        k = vizinhancas.primeira_posicao_afetada(mov, operador)
        assert problema.avaliar_sufixo(viz, pequena, k, C, H) == \
            problema.avaliar(viz, pequena)


def test_incremental_conta_uma_avaliacao(pequena):
    solucao = list(range(1, 13))
    C, H = problema.prefixos(solucao, pequena)
    problema.zerar_contador(pequena)
    problema.avaliar_sufixo_com_contagem(solucao, pequena, 5, C, H)
    assert pequena["avaliacoes"] == 1
    problema.prefixos(solucao, pequena)                  # não conta
    problema.avaliar_sufixo(solucao, pequena, 5, C, H)   # não conta
    assert pequena["avaliacoes"] == 1


def test_prefixos_ultimo_valor_e_h(media):
    solucao = problema.solucao_aleatoria(media["n"], 5)
    C, H = problema.prefixos(solucao, media)
    assert H[-1] == problema.avaliar(solucao, media)
    assert len(C) == len(H) == media["n"] + 1
    assert all(H[i] <= H[i + 1] for i in range(len(H) - 1))  # h não decresce


def test_contador_so_e_incrementado_em_problema_py():
    """A contagem de avaliações é centralizada em problema.py."""
    import os

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for nome in os.listdir(os.path.join(raiz, "src")):
        if not nome.endswith(".py") or nome == "problema.py":
            continue
        with open(os.path.join(raiz, "src", nome), encoding="utf-8") as f:
            codigo = f.read()
        assert not re.search(r'\["avaliacoes"\]\s*[-+]?=(?!=)', codigo), nome
