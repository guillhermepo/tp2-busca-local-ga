# Tabelas geradas por `python -m src.experimentos analise`

## T2 - Vizinhanças (Greedy Descent + Random Restart)

| instancia | vizinhanca | variante | media ± desvio | minimo | mediana | passos | restarts | otimos_distintos | tempo_s |
|---|---|---|---|---|---|---|---|---|---|
| pequena | 2opt | best | 1875.0 ± 0.0 | 1875 | 1875.0 | 675 | 81.7 | 28.1 | 0.72 |
| pequena | 2opt | first | 1875.0 ± 0.0 | 1875 | 1875.0 | 3780 | 218.0 | 47.9 | 1.08 |
| pequena | 2opt | random | 1875.0 ± 0.0 | 1875 | 1875.0 | 3921 | 244.7 | 148.2 | 0.89 |
| pequena | insertion | best | 1875.0 ± 0.0 | 1875 | 1875.0 | 364 | 48.5 | 12.8 | 0.67 |
| pequena | insertion | first | 1875.0 ± 0.0 | 1875 | 1875.0 | 2425 | 137.9 | 17.1 | 1.14 |
| pequena | insertion | random | 1875.0 ± 0.0 | 1875 | 1875.0 | 2526 | 152.1 | 67.5 | 1.05 |
| pequena | swap | best | 1875.0 ± 0.0 | 1875 | 1875.0 | 668 | 88.8 | 62.7 | 0.65 |
| pequena | swap | first | 1875.0 ± 0.0 | 1875 | 1875.0 | 3498 | 220.7 | 114.5 | 1.01 |
| pequena | swap | random | 1875.0 ± 0.0 | 1875 | 1875.0 | 3657 | 253.0 | 207.3 | 1.00 |
| media | 2opt | best | 20805.3 ± 1705.3 | 17747 | 20460.0 | 121 | 2.0 | 2.0 | 5.68 |
| media | 2opt | first | 18507.7 ± 648.6 | 16706 | 18489.0 | 2621 | 18.5 | 18.5 | 9.71 |
| media | 2opt | random | 18523.6 ± 723.4 | 17103 | 18514.5 | 2800 | 20.4 | 20.4 | 6.24 |
| media | insertion | best | 20017.9 ± 2582.2 | 16460 | 19805.5 | 62 | 1.0 | 1.0 | 5.91 |
| media | insertion | first | 17362.1 ± 723.4 | 16530 | 17216.5 | 1653 | 10.2 | 10.2 | 10.73 |
| media | insertion | random | 17588.2 ± 728.0 | 16460 | 17548.0 | 1810 | 11.7 | 11.7 | 5.99 |
| media | swap | best | 29999.1 ± 3078.4 | 24653 | 29691.5 | 121 | 2.0 | 2.0 | 5.47 |
| media | swap | first | 24508.1 ± 2217.5 | 20121 | 24848.0 | 2331 | 17.8 | 17.8 | 10.31 |
| media | swap | random | 24510.7 ± 1840.0 | 20881 | 24847.5 | 2479 | 19.3 | 19.3 | 5.68 |
| grande | 2opt | best | 505642.1 ± 26031.6 | 463918 | 504022.0 | 27 | 0.0 | 0.0 | 32.42 |
| grande | 2opt | first | 91426.9 ± 4455.0 | 86019 | 90604.0 | 1980 | 2.8 | 2.8 | 66.90 |
| grande | 2opt | random | 91334.7 ± 4812.4 | 85240 | 89959.0 | 1963 | 2.8 | 2.8 | 30.88 |
| grande | insertion | best | 814719.9 ± 75268.8 | 714957 | 804360.5 | 14 | 0.0 | 0.0 | 29.01 |
| grande | insertion | first | 82782.1 ± 4369.2 | 75887 | 82215.5 | 1225 | 1.0 | 1.0 | 70.12 |
| grande | insertion | random | 81376.8 ± 3172.7 | 77594 | 80563.5 | 1289 | 1.2 | 1.2 | 31.87 |
| grande | swap | best | 489483.7 ± 28139.3 | 439240 | 490195.5 | 27 | 0.0 | 0.0 | 31.04 |
| grande | swap | first | 148940.3 ± 10210.2 | 135569 | 152195.0 | 1645 | 2.1 | 2.1 | 57.64 |
| grande | swap | random | 150150.7 ± 11482.9 | 137004 | 147257.5 | 1768 | 2.4 | 2.4 | 34.03 |

Escolha automática: vizinhança **insertion**, variante do greedy **random**. Razão média ao melhor (1,0 = melhor): {"swap": 1.414, "insertion": 1.0, "2opt": 1.063}

### Testes entre vizinhanças (melhor variante de cada)

**pequena**

| A | B | mediana A | mediana B | p-valor | alfa (Bonferroni) | conclusão |
|---|---|---|---|---|---|---|
| 2opt-best | insertion-best | 1875.00 | 1875.00 | 1.0000 | 0.02 | sem diferença significativa |
| 2opt-best | swap-best | 1875.00 | 1875.00 | 1.0000 | 0.02 | sem diferença significativa |
| insertion-best | swap-best | 1875.00 | 1875.00 | 1.0000 | 0.02 | sem diferença significativa |

**media**

| A | B | mediana A | mediana B | p-valor | alfa (Bonferroni) | conclusão |
|---|---|---|---|---|---|---|
| 2opt-first | insertion-first | 18489.00 | 17216.50 | 8.19e-07 | 0.02 | insertion-first melhor |
| 2opt-first | swap-first | 18489.00 | 24848.00 | 3.02e-11 | 0.02 | 2opt-first melhor |
| insertion-first | swap-first | 17216.50 | 24848.00 | 3.01e-11 | 0.02 | insertion-first melhor |

**grande**

| A | B | mediana A | mediana B | p-valor | alfa (Bonferroni) | conclusão |
|---|---|---|---|---|---|---|
| 2opt-random | insertion-random | 89959.00 | 80563.50 | 5.83e-04 | 0.02 | insertion-random melhor |
| 2opt-random | swap-first | 89959.00 | 152195.00 | 1.83e-04 | 0.02 | 2opt-random melhor |
| insertion-random | swap-first | 80563.50 | 152195.00 | 1.83e-04 | 0.02 | insertion-random melhor |

## Avaliação incremental (tempo de parede)

| instância | vizinhança | µs/avaliação (completa) | µs/avaliação (incremental) | ganho | mesmo h e mesmas avaliações |
|---|---|---|---|---|---|
| pequena | swap | 7.17 | 6.07 | x1.18 | True |
| pequena | insertion | 7.58 | 6.53 | x1.16 | True |
| pequena | 2opt | 7.98 | 6.96 | x1.15 | True |
| media | swap | 25.09 | 15.71 | x1.60 | True |
| media | insertion | 24.94 | 15.97 | x1.56 | True |
| media | 2opt | 24.74 | 16.95 | x1.46 | True |
| grande | swap | 68.02 | 41.52 | x1.64 | True |
| grande | insertion | 70.28 | 42.73 | x1.64 | True |
| grande | 2opt | 66.06 | 46.34 | x1.43 | True |

## Tabela principal (Greedy x SA x GA)

| instancia | rotulo | media ± desvio | minimo | mediana | gap_ref_% | gap_melhor_% | passos | restarts | tempo_s | avaliacoes |
|---|---|---|---|---|---|---|---|---|---|---|
| pequena | GA | 1972.9 ± 133.8 | 1875 | 1937.0 | +5.22 | +0.00 | 1042 | 0.0 | 3.29 | 50000 |
| pequena | Greedy-random | 1875.0 ± 0.0 | 1875 | 1875.0 | +0.00 | +0.00 | 2526 | 152.1 | 1.07 | 50000 |
| pequena | SA | 1875.0 ± 0.0 | 1875 | 1875.0 | +0.00 | +0.00 | 11695 | 0.0 | 1.25 | 50000 |
| media | GA | 19367.3 ± 2106.2 | 16559 | 19315.0 | +18.58 | +1.39 | 3125 | 0.0 | 24.52 | 150000 |
| media | Greedy-random | 17588.2 ± 728.0 | 16460 | 17548.0 | +7.69 | +0.78 | 1810 | 11.7 | 5.50 | 150000 |
| media | SA | 17102.6 ± 800.1 | 16181 | 16810.0 | +4.72 | -0.92 | 41478 | 0.0 | 8.76 | 150000 |
| grande | GA | 95503.9 ± 10742.8 | 81687 | 94983.0 | +58.07 | +35.21 | 6250 | 0.0 | 124.63 | 300000 |
| grande | Greedy-random | 81376.8 ± 3172.7 | 77594 | 80563.5 | +34.69 | +28.43 | 1289 | 1.2 | 25.24 | 300000 |
| grande | SA | 72803.7 ± 3745.0 | 66054 | 72618.0 | +20.50 | +9.33 | 87003 | 0.0 | 42.69 | 300000 |

gap_ref_% = (média - referência)/referência; gap_melhor_% = (melhor - referência)/referência. Referências: 1875 (ótimo, pequena), 16332 e 60417 (melhores conhecidos).

Ranking por média (menor = melhor):

- pequena: Greedy-random < SA < GA
- media: SA < Greedy-random < GA
- grande: SA < Greedy-random < GA

## Testes de Mann-Whitney (par a par)

| instância | A | B | mediana A | mediana B | p-valor | alfa (Bonferroni) | conclusão |
|---|---|---|---|---|---|---|---|
| pequena | GA | Greedy-random | 1937.00 | 1875.00 | 2.76e-07 | 0.02 | Greedy-random melhor |
| pequena | GA | SA | 1937.00 | 1875.00 | 2.76e-07 | 0.02 | SA melhor |
| pequena | Greedy-random | SA | 1875.00 | 1875.00 | 1.0000 | 0.02 | sem diferença significativa |
| media | GA | Greedy-random | 19315.00 | 17548.00 | 1.78e-04 | 0.02 | Greedy-random melhor |
| media | GA | SA | 19315.00 | 16810.00 | 3.57e-06 | 0.02 | SA melhor |
| media | Greedy-random | SA | 17548.00 | 16810.00 | 0.0065 | 0.02 | SA melhor |
| grande | GA | Greedy-random | 94983.00 | 80563.50 | 0.0013 | 0.02 | Greedy-random melhor |
| grande | GA | SA | 94983.00 | 72618.00 | 1.83e-04 | 0.02 | SA melhor |
| grande | Greedy-random | SA | 80563.50 | 72618.00 | 3.30e-04 | 0.02 | SA melhor |

## Ótimos locais e h* na instância pequena

| algoritmo | execuções | execuções com h = 1875 | ótimos locais por execução (média) | ótimos locais distintos por execução (média) |
|---|---|---|---|---|
| GA | 30 | 11 | 0.00 | 0.00 |
| Greedy-random | 30 | 30 | 152.07 | 67.47 |
| SA | 30 | 30 | 0.00 | 0.00 |

## Diversidade do GA (final da execução, mediana)

| instância | distintos (de N=50) | distância média |
|---|---|---|
| pequena | 21.50 | 0.52 |
| media | 32.50 | 0.52 |
| grande | 36.00 | 0.56 |

## Parâmetros calibrados do SA (mediana)

| instância | T0 | Tf | alpha |
|---|---|---|---|
| pequena | 2845.3 | 2.845 | 0.998340 |
| media | 15201.3 | 15.201 | 0.997697 |
| grande | 42990.3 | 42.990 | 0.996549 |

## Experimento extra: a recombinação ajuda no GA?

| instancia | rotulo | media ± desvio | minimo | mediana | tempo_s |
|---|---|---|---|---|---|
| pequena | GA | 1972.9 ± 133.8 | 1875 | 1937.0 | 3.29 |
| pequena | GA-pmx | 1941.7 ± 127.1 | 1875 | 1875.0 | 3.44 |
| pequena | GA-sem_cruzamento | 1982.6 ± 141.5 | 1875 | 1937.0 | 2.95 |
| media | GA | 19367.3 ± 2106.2 | 16559 | 19315.0 | 24.52 |
| media | GA-pmx | 20295.3 ± 3094.4 | 16612 | 19331.5 | 23.40 |
| media | GA-sem_cruzamento | 20493.9 ± 2220.5 | 16996 | 20292.0 | 18.32 |
| grande | GA | 95503.9 ± 10742.8 | 81687 | 94983.0 | 124.63 |
| grande | GA-pmx | 89426.0 ± 8812.0 | 73437 | 90673.5 | 114.51 |
| grande | GA-sem_cruzamento | 85659.2 ± 10520.4 | 76494 | 82861.0 | 87.62 |

| instância | A | B | mediana A | mediana B | p-valor | alfa (Bonferroni) | conclusão |
|---|---|---|---|---|---|---|---|
| pequena | GA | GA-pmx | 1937.00 | 1875.00 | 0.1087 | 0.02 | sem diferença significativa |
| pequena | GA | GA-sem_cruzamento | 1937.00 | 1937.00 | 0.8865 | 0.02 | sem diferença significativa |
| pequena | GA-pmx | GA-sem_cruzamento | 1875.00 | 1937.00 | 0.0914 | 0.02 | sem diferença significativa |
| media | GA | GA-pmx | 19315.00 | 19331.50 | 0.3750 | 0.02 | sem diferença significativa |
| media | GA | GA-sem_cruzamento | 19315.00 | 20292.00 | 0.0351 | 0.02 | sem diferença significativa |
| media | GA-pmx | GA-sem_cruzamento | 19331.50 | 20292.00 | 0.3632 | 0.02 | sem diferença significativa |
| grande | GA | GA-pmx | 94983.00 | 90673.50 | 0.3075 | 0.02 | sem diferença significativa |
| grande | GA | GA-sem_cruzamento | 94983.00 | 82861.00 | 0.0257 | 0.02 | sem diferença significativa |
| grande | GA-pmx | GA-sem_cruzamento | 90673.50 | 82861.00 | 0.2123 | 0.02 | sem diferença significativa |
