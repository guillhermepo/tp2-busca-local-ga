# Trabalho Prático 2 - Busca Local e Algoritmo Genético

## Disciplina

Fundamentos de Inteligência Artificial - UFMG

## Descrição

Uma concessionária de distribuição de energia possui uma única equipe de
manutenção. A equipe parte de uma base, visita os ativos um de cada vez e não
precisa retornar à base ao final. Cada ativo `j` tem posição `(x_j, y_j)`,
duração do serviço `p_j`, prazo regulatório `d_j` e peso de criticidade `w_j`.

Uma solução é uma permutação dos ativos `π = (π1, ..., πn)`, que representa a
ordem de visita. Toda permutação é válida; o objetivo é encontrar a de menor
custo.

O tempo de deslocamento entre dois pontos é a distância euclidiana
arredondada para o inteiro mais próximo:
`t_ij = round(sqrt((x_i - x_j)^2 + (y_i - y_j)^2))`.

## Instâncias

| Arquivo | Ativos |
|---|---|
| `dados/manutencao_pequena.txt` | 12 |
| `dados/manutencao_media.txt` | 50 |
| `dados/manutencao_grande.txt` | 150 |

Formato: primeira linha `n`; segunda linha `x_base y_base`; depois uma linha
por ativo `x y p d w`. Os arquivos foram fornecidos pelo professor e **não
devem ser alterados**.

Convenção de índices no código: `0 = base`, `1 = ativo 1`, ..., `n = ativo n`.

## Função objetivo

O tempo de conclusão do ativo na posição `k` é
`C(k) = C(k-1) + t(π(k-1), π(k)) + p(π(k))`, com `π0 = 0` (base) e `C0 = 0`.

A função a minimizar é o atraso ponderado total:

```
h(π) = Σ w_j * max(0, C_j - d_j)
```

Ativos concluídos no prazo contribuem com 0; os atrasados contribuem com o
atraso multiplicado pelo peso. Quanto menor `h`, melhor. Na instância pequena
o ótimo global conhecido é `h* = 1875`.

## Algoritmos

- Greedy Descent com Random Restart (Best Improvement e First Improvement) -
  `src/greedy.py` implementado; falta integrar com as vizinhanças.
- Simulated Annealing - **ainda não implementado**.
- Genetic Algorithm - **ainda não implementado**.

> Alguns módulos ainda estão em desenvolvimento: `src/vizinhancas.py` contém
> apenas a interface esperada e `src/experimentos.py` contém apenas
> constantes e utilitários.

## Estrutura do projeto

```
tp2-busca-local-ga/
├── dados/                   # instâncias do professor (não alterar)
├── src/
│   ├── problema.py          # leitura, tempos, função h, solução aleatória, contador de avaliações
│   ├── greedy.py            # Greedy Descent + Random Restart (vizinhança passada como função)
│   ├── vizinhancas.py       # Swap, Insertion, 2-opt (interface; a implementar)
│   └── experimentos.py      # orçamentos oficiais, colunas do CSV, salvar_csv (execução: a implementar)
├── resultados/              # CSVs de resultados (.gitkeep mantém a pasta no Git)
├── testes/
│   ├── test_problema.py     # testes do problema (inclui h = 4366)
│   └── test_greedy.py       # testes do greedy (usa um swap local ao teste)
├── pytest.ini               # permite rodar `pytest` a partir da raiz
├── requirements.txt
├── .gitignore
└── README.md
```

Orçamentos oficiais (avaliações de `h` por execução):

| Instância | Orçamento | Execuções |
|---|---|---|
| pequena | 50.000 | 30 |
| média | 150.000 | 30 |
| grande | 300.000 | 10 |

A contagem de avaliações é centralizada em `problema.avaliar_com_contagem`.
Os algoritmos devem usar essa função, nunca incrementar o contador por conta
própria.

## Ambiente

Criar o ambiente virtual:

```
python -m venv .venv
```

Ativar no Windows:

```
.venv\Scripts\activate
```

Ativar no Linux/macOS:

```
source .venv/bin/activate
```

Instalar as dependências:

```
pip install -r requirements.txt
```

## Testes

A partir da raiz do projeto:

```
pytest
```

ou:

```
python -m pytest
```

## Validação

Para a instância pequena, a permutação identidade `[1, 2, ..., 12]` deve
produzir exatamente `h = 4366`. Esse caso é verificado em
`testes/test_problema.py`.

## Reprodução dos resultados

> Ainda não implementado. Os itens abaixo serão documentados, com os comandos
> exatos, quando existirem.

- TODO: geração dos resultados brutos (CSVs em `resultados/`)
- TODO: tabela principal
- TODO: boxplots
- TODO: curvas de convergência
- TODO: gráfico do Simulated Annealing
- TODO: gráfico de diversidade do Genetic Algorithm

## Integrantes

- Integrante 1:
- Integrante 2:
- Integrante 3:
- Integrante 4:
