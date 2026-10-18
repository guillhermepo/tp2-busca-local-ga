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
atraso multiplicado pelo peso. Quanto menor `h`, melhor. Valores de
verificação (Seção 1.4 do enunciado): `h([1..12]) = 4366` e ótimo global
`h* = 1875` na instância pequena. O exemplo da Figura 1 (n = 4; rota gulosa
custa 39, ótimo custa 22) também é verificado nos testes.

## O que está implementado

| Componente | Arquivo | Observações |
|---|---|---|
| Problema, `h`, contagem de avaliações | `src/problema.py` | contador centralizado; avaliação **incremental** (`prefixos`, `avaliar_sufixo`) |
| Vizinhanças swap / insertion / 2-opt | `src/vizinhancas.py` | tamanhos: swap `n(n-1)/2`, insertion `(n-1)²`, 2-opt `n(n-1)/2` |
| Interface algoritmo ≠ problema | `src/interface.py` | `solucao_aleatoria`, `h`, `sucessores`, `sucessor_aleatorio`, `cruzamento`, `mutacao` |
| Greedy Descent + Random Restart | `src/greedy.py` | 3 variantes: `best`, `first`, `random` (sucessor aleatório com aceitação de melhora) |
| Simulated Annealing | `src/simulated_annealing.py` | resfriamento geométrico, `T0`/`Tf`/`alpha` calibrados por instância, registra taxa de aceitação de piores |
| Algoritmo Genético | `src/genetico.py` | torneio ou roleta, OX ou PMX, mutação, elitismo, registra diversidade por geração |
| Cruzamentos OX e PMX | `src/cruzamentos.py` | exemplo numérico passo a passo no docstring |
| Execução dos experimentos | `src/experimentos.py` | T1, T2, T3, avaliação incremental, experimento extra; paralelo e reprodutível |
| Tabelas, testes estatísticos, figuras | `src/analise.py` | Mann-Whitney com correção de Bonferroni |

Os resultados, a discussão e as decisões de projeto estão em
[`docs/relatorio.md`](docs/relatorio.md) (texto-base do relatório). As tabelas
geradas automaticamente estão em [`resultados/tabelas.md`](resultados/tabelas.md).

### Resultados em uma linha (média ± desvio de `h`)

| Instância | Greedy (insertion, random) | Simulated Annealing | Genetic Algorithm | Referência |
|---|---|---|---|---|
| pequena (50 000 aval., 30 exec.) | 1875,0 ± 0,0 | 1875,0 ± 0,0 | 1972,9 ± 133,8 | 1875 (ótimo) |
| média (150 000 aval., 30 exec.) | 17588,2 ± 728,0 | **17102,6 ± 800,1** | 19367,3 ± 2106,2 | 16332 |
| grande (300 000 aval., 10 exec.) | 81376,8 ± 3172,7 | **72803,7 ± 3745,0** | 95503,9 ± 10742,8 | 60417 |

## Estrutura do projeto

```
tp2-busca-local-ga/
├── dados/                       # instâncias do professor (não alterar)
├── src/
│   ├── problema.py              # leitura, tempos, h, contador, avaliação incremental
│   ├── vizinhancas.py           # swap, insertion, 2-opt (movimentos, vizinhos, sucessor aleatório)
│   ├── cruzamentos.py           # OX e PMX
│   ├── interface.py             # ProblemaManutencao: o que os algoritmos enxergam
│   ├── rastro.py                # melhor-até-agora e histórico de convergência
│   ├── greedy.py                # Greedy Descent + Random Restart
│   ├── simulated_annealing.py   # SA
│   ├── genetico.py              # GA
│   ├── experimentos.py          # T1/T2/T3, extra, incremental, linha de comando
│   └── analise.py               # tabelas, testes estatísticos, figuras
├── testes/                      # suíte pytest (163 testes)
├── resultados/                  # CSVs, tabelas.md e figuras/ gerados pelos experimentos
├── docs/relatorio.md            # texto-base do relatório (análise e discussão)
├── pytest.ini
├── requirements.txt
└── README.md
```

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

Instalar as dependências (numpy, pandas, matplotlib, scipy, pytest):

```
pip install -r requirements.txt
```

Testado com Python 3.14. Todos os comandos abaixo são executados **a partir da
raiz do projeto**.

## Testes

```
python -m pytest
```

A suíte (163 testes, ~1,5 min) cobre: leitura da instância e validação de
`h = 4366`; exemplo da Figura 1 (39 e 22, com ótimo por força bruta);
vizinhanças (tamanhos, validade, ausência de duplicatas, exemplos da Figura 3);
**equivalência entre avaliação incremental e completa** para os 3 operadores;
OX/PMX (exemplo numérico, validade das permutações); respeito **exato** ao
orçamento de avaliações em Greedy/SA/GA; centralização do contador; ótimos
locais devolvidos pelo greedy são de fato ótimos locais; reprodutibilidade por
semente; comportamento do SA (taxa de aceitação cai de ~0,8 a ~0, `T`
geométrico, extremos de temperatura); elitismo e diversidade do GA; e o pipeline
completo de experimentos e análise em escala reduzida.

Teste rápido (sem os testes mais lentos de pipeline):

```
python -m pytest -k "not pipeline"
```

## Reprodução dos resultados

Cada execução usa uma semente derivada de (instância, algoritmo, variante,
vizinhança, índice), então rodar de novo produz os mesmos valores de `h`
(somente os tempos mudam).

Reproduzir **tudo** (≈ 15 min em 16 núcleos; `--processos N` ajusta o paralelismo):

```
python -m src.experimentos tudo
```

Ou etapa por etapa:

| Etapa | Comando | Gera |
|---|---|---|
| T1 - valida `h(identidade) = 4366` | `python -m src.experimentos validar` | (saída no terminal) |
| T2 - compara as 3 vizinhanças × 3 variantes do greedy | `python -m src.experimentos t2` | `resultados/t2_vizinhancas.csv`, `resultados/t2_escolha.json` |
| Ganho da avaliação incremental | `python -m src.experimentos incremental` | `resultados/incremental.csv` |
| T3 - Greedy × SA × GA (protocolo oficial) | `python -m src.experimentos principal` | `resultados/principal.csv`, `resultados/principal_extras.json` |
| Experimento extra do GA (recombinação) | `python -m src.experimentos extra` | `resultados/extra_ga.csv` |
| Tabelas, testes estatísticos e figuras | `python -m src.experimentos analise` | `resultados/tabelas.md`, `resultados/figuras/*.png` |

`principal` depende de `t2` (a vizinhança e a variante do greedy usadas no
experimento principal são escolhidas automaticamente a partir de
`t2_escolha.json`). Todas as etapas aceitam `--rapido` (orçamento de 3000
avaliações e 3 execuções, saída em `resultados/rapido/`) para conferir
rapidamente que o pipeline funciona.

Mapa dos itens exigidos no relatório:

| Item do enunciado | Onde está |
|---|---|
| Tabela principal (9 combinações, média ± desvio, melhor, gap) | `resultados/tabelas.md` (seção "Tabela principal") |
| Boxplots por instância | `resultados/figuras/boxplots.png` |
| Curvas de convergência (+ média da população do GA) | `resultados/figuras/convergencia_{pequena,media,grande}.png` |
| Testes estatísticos (Mann-Whitney) | `resultados/tabelas.md` (seção "Testes de Mann-Whitney") |
| Tempo × avaliações | coluna `tempo_s`/`avaliacoes` da tabela principal; ganho incremental em `resultados/tabelas.md` |
| Taxa de aceitação de piores do SA | `resultados/figuras/sa_aceitacao.png` |
| Diversidade do GA | `resultados/figuras/ga_diversidade.png` |
| T2 (vizinhanças) | `resultados/tabelas.md` + `resultados/figuras/t2_vizinhancas.png` |
| Ótimos locais / execuções que atingem `h* = 1875` | `resultados/tabelas.md` (seção "Ótimos locais") e tabela T2 (coluna `otimos_distintos`) |
| Experimento adicional (GA, recombinação) | `resultados/tabelas.md` + `resultados/figuras/extra_ga.png` |

O histórico bruto de convergência (`principal_extras.json`, ~30 MB) não é
versionado; é regenerado por `python -m src.experimentos principal`.

## Contagem de avaliações

O orçamento é medido em avaliações de `h`. A contagem fica em um único lugar,
`instancia["avaliacoes"]`, e só é incrementada por
`problema.avaliar_com_contagem` e `problema.avaliar_sufixo_com_contagem`
(um teste automático impede incrementos em outros módulos). Cada sucessor
examinado pela busca local conta 1 e cada indivíduo avaliado pelo GA conta 1;
as amostras de calibração do SA também contam. Os algoritmos conferem o
orçamento **antes** de cada avaliação, portanto param exatamente ao atingi-lo.
Indivíduos de elite do GA não são reavaliados (não há nova avaliação).

A avaliação incremental reavalia só o sufixo afetado por um movimento; ela
**não** altera a contagem (1 sucessor = 1 avaliação), só o tempo de parede.

## Limitações e cuidados (leia antes de citar números)

- Os parâmetros do GA (população 50, `Pm = 0,5`, torneio 3, mutação por
  insertion) e do SA (`p0 = 0,8`, `Tf = T0·10⁻³`, `n` movimentos por
  temperatura) foram escolhidos em pequenas buscas exploratórias nas instâncias
  média/grande com sementes 0-2, que coincidem com as primeiras sementes das
  execuções oficiais. O ajuste é modesto, mas existe; o relatório deve
  declará-lo.
- No Greedy `random` não há varredura completa: o "ótimo local" é declarado por
  paciência (|N| sorteios seguidos sem melhora). As contagens de ótimos locais
  dessa variante são aproximadas; as de `best` e `first` são exatas.
- Os tempos de parede do experimento principal vêm de execuções em paralelo
  (com alguma contenção); compare-os entre algoritmos, não em valor absoluto.
  Os tempos comparáveis da avaliação incremental vêm de execução serial.
- Os valores de referência 16332 e 60417 são "melhores conhecidos", não
  ótimos provados.

## Integrantes

- Integrante 1:
- Integrante 2:
- Integrante 3:
- Integrante 4:
