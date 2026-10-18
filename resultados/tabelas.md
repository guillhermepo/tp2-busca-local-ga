# Tabelas de Resultados — TP2

## Tabela Principal (T3)

| Instância | Referência | Algoritmo | Média ± Desvio | Mínimo | Mediana | Gap Mínimo (h*) | Gap Média (h*) | Avaliações | Tempo Médio (s) |
|---|---|---|---|---|---|---|---|---|---|
| pequena | h* = 1875 (ótimo global) | Greedy | 1875.0 ± 0.0 | 1875 | 1875.0 | +0.00% | +0.00% | 50000 | 0.19 |
| pequena | h* = 1875 (ótimo global) | SA | 1875.0 ± 0.0 | 1875 | 1875.0 | +0.00% | +0.00% | 50000 | 0.27 |
| pequena | h* = 1875 (ótimo global) | GA | 2320.4 ± 172.7 | 1937 | 2286.5 | +3.31% | +23.75% | 50000 | 0.63 |
| media | 16332 (melhor valor conhecido) | Greedy | 17510.0 ± 896.5 | 16175 | 17278.0 | - | - | 150000 | 1.64 |
| media | 16332 (melhor valor conhecido) | SA | 17021.0 ± 606.2 | 16179 | 16734.5 | - | - | 150000 | 1.95 |
| media | 16332 (melhor valor conhecido) | GA | 29196.0 ± 4019.4 | 20310 | 29407.0 | - | - | 150000 | 3.71 |
| grande | 60417 (melhor valor conhecido) | Greedy | 82754.6 ± 5564.0 | 77982 | 80633.5 | - | - | 300000 | 10.55 |
| grande | 60417 (melhor valor conhecido) | SA | 71785.9 ± 2429.6 | 67484 | 72151.5 | - | - | 300000 | 10.51 |
| grande | 60417 (melhor valor conhecido) | GA | 169818.3 ± 13205.7 | 149100 | 169844.0 | - | - | 300000 | 17.64 |

## Testes Estatísticos Par a Par (Mann-Whitney U bilateral)

| Instância | Comparação | Mediana A | Mediana B | p-valor | Significativo (p < 0,05)? |
|---|---|---|---|---|---|
| pequena | Greedy vs SA | 1875.0 | 1875.0 | 1.0000 | não |
| pequena | Greedy vs GA | 1875.0 | 2286.5 | 1.19e-12 | sim |
| pequena | SA vs GA | 1875.0 | 2286.5 | 1.19e-12 | sim |
| media | Greedy vs SA | 17278.0 | 16734.5 | 0.0105 | sim |
| media | Greedy vs GA | 17278.0 | 29407.0 | 3.02e-11 | sim |
| media | SA vs GA | 16734.5 | 29407.0 | 3.02e-11 | sim |
| grande | Greedy vs SA | 80633.5 | 72151.5 | 1.83e-04 | sim |
| grande | Greedy vs GA | 80633.5 | 169844.0 | 1.83e-04 | sim |
| grande | SA vs GA | 72151.5 | 169844.0 | 1.83e-04 | sim |

## Ótimos Locais e Alcance de h* = 1875 na Instância Pequena

| Algoritmo | Execuções que atingiram h* = 1875 | Proporção de alcance de 1875 |
|---|---|---|
| Greedy | 30/30 | 100.0% |
| SA | 30/30 | 100.0% |
| GA | 0/30 | 0.0% |

- **Total de ótimos locais visitados pelo Greedy na pequena (todas as execuções)**: 4131
- **Permutações de ótimo local distintas (total acumulado nas 30 execuções)**: 19
- **Valores de h distintos entre esses ótimos locais (informação complementar)**: 17

## Experimento Adicional: GA com OX vs GA sem Cruzamento (Pc = 0)

| Instância | GA com OX (média ± desvio) | GA sem OX (média ± desvio) | p-valor (Mann-Whitney) |
|---|---|---|---|
| pequena | 2320.4 ± 172.7 | 2372.0 ± 356.3 | 0.9882 |
| media | 29196.0 ± 4019.4 | 30188.0 ± 4384.0 | 0.2838 |
| grande | 169818.3 ± 13205.7 | 164644.8 ± 16815.0 | 0.4727 |
