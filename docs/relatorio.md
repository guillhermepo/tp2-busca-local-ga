# Relatório técnico (texto-base) - TP2 Busca Local e Algoritmo Genético

> Este arquivo reúne a modelagem, as decisões de projeto, os resultados e a
> discussão exigidos pelo enunciado. **Todos os números vêm dos arquivos em
> `resultados/`** (reprodução: ver `README.md`). Tabelas completas:
> `resultados/tabelas.md`. Figuras: `resultados/figuras/`. O relatório final em
> PDF deve ser montado a partir deste texto (sugestão do enunciado: 5 páginas).

## 1. Problema e modelagem

Sequenciamento de manutenção de `n` ativos por uma única equipe. A solução é
uma permutação `π` dos ativos; `C_πk = C_πk-1 + t(πk-1, πk) + p_πk` e
`h(π) = Σ w_j · max(0, C_j − d_j)`, com `t_ij = round(√(Δx² + Δy²))`.
Toda permutação é viável (soft constraints) e o espaço de busca tem `n!`
soluções.

**T1 - validação.** `h([1..12]) = 4366` na instância pequena (verificado em
`testes/test_problema.py` e por `python -m src.experimentos validar`). O ótimo
`h* = 1875` foi alcançado por 30/30 execuções do Greedy e do SA. O exemplo da
Figura 1 (n = 4) foi reproduzido: a rota gulosa `(1,4,2,3)` custa 39 e o ótimo
`(1,4,3,2)`, 22 (confirmado por força bruta em
`testes/test_problema_extra.py`). As coordenadas desse exemplo foram deduzidas
do cronograma da figura (o enunciado não as lista).

## 2. Arquitetura

Os algoritmos não conhecem o problema: usam apenas `ProblemaManutencao`
(`src/interface.py`) com `solucao_aleatoria`, `h`, `sucessores`,
`sucessor_aleatorio`, `cruzamento` e `mutacao`, como sugerido no enunciado
(Seção 2.1). Trocar de problema exigiria reimplementar só essa classe.

**Contagem de avaliações.** Em um único ponto (`problema.py`); cada sucessor
examinado conta 1, cada indivíduo do GA conta 1, a calibração do SA conta, e
todos os algoritmos param exatamente no orçamento (50 000 / 150 000 /
300 000).

## 3. Vizinhanças (T2)

Tamanhos para `n` ativos: swap `n(n−1)/2`; insertion `(n−1)²` (os `n(n−1)`
pares `(i, j)` contariam duas vezes cada troca de elementos adjacentes);
2-opt `n(n−1)/2`. Para `n = 150`: 11 175, 22 201 e 11 175 vizinhos.

### Avaliação incremental

Um movimento que altera a partir da posição `k` só exige reavaliar o sufixo
(`prefixos` + `avaliar_sufixo`). Equivalência com a avaliação completa
verificada por teste automático (todas as vizinhanças da instância pequena e
milhares de movimentos aleatórios na média). Ganho de tempo medido em execução
serial, mesmo greedy `best`, mesma semente, mesmas avaliações e mesmo resultado:

| instância | swap | insertion | 2-opt |
|---|---|---|---|
| pequena (n=12) | x1,18 | x1,16 | x1,15 |
| média (n=50) | x1,60 | x1,56 | x1,46 |
| grande (n=150) | x1,64 | x1,64 | x1,43 |

O ganho cresce com `n`, mas é limitado (< 2x) porque em Python o custo por
avaliação é dominado pelo laço sobre o sufixo e por gerar a lista vizinha
(`O(n)`): na grande, 41,5 µs/avaliação (swap), 42,7 (insertion) e 46,3 (2-opt),
contra 66-70 µs sem incremental. 2-opt é o mais caro por vizinho (a causa não foi investigada). Por **movimento**, o best
improvement paga uma varredura inteira (`|N|` avaliações): insertion custa
cerca do dobro de swap/2-opt (`(n−1)²` contra `n(n−1)/2`).

### Qualidade dos ótimos locais

Médias de `h` (30/30/10 execuções; mesmas sementes; tabela completa em
`resultados/tabelas.md`). Melhor variante de cada vizinhança:

| instância | swap | insertion | 2-opt |
|---|---|---|---|
| pequena | 1875,0 ± 0,0 (todas as 9 combinações atingem o ótimo em 30/30) | idem | idem |
| média | 24508 ± 2218 (first) | **17362 ± 723** (first) | 18508 ± 649 (first) |
| grande | 148940 ± 10210 (first) | **81377 ± 3173** (random) | 91335 ± 4812 (random) |

Na instância pequena não há diferença (Mann-Whitney p = 1,0). Na média e na
grande, insertion é melhor que 2-opt e swap com `p < 0,001` (Bonferroni,
`α = 0,05/3`). **Vizinhança adotada: insertion**: ela obteve a menor razão média
ao melhor (1,000; 2-opt 1,063; swap 1,414), ou seja, insertion reorganiza a
sequência com mudanças mais "úteis" para uma função de custo ligada a prazos:
mover um ativo crítico para mais cedo/tarde não perturba a ordem relativa dos
demais, enquanto swap e 2-opt desorganizam o que já estava bom. É uma
hipótese consistente com os dados, não demonstrada isoladamente. O custo por
vizinho incremental é praticamente igual entre os operadores (diferença < 12%),
então a escolha não penaliza o tempo.

### Variantes do greedy e passos de melhoria

Passos de melhoria que cada variante consegue dar dentro do orçamento
(insertion; média das execuções):

| instância | best | first | random |
|---|---|---|---|
| pequena | 364 | 2425 | 2526 |
| média | 62 | 1653 | 1810 |
| grande | 14 | 1225 | 1289 |

Com `n = 150`, uma varredura de insertion custa 22 201 avaliações; o best
improvement faz só **14 passos** em 300 000 avaliações e termina com
`h ≈ 815 000` (contra 81 000 de first/random) e nenhum ótimo local alcançado.
First e random têm desempenho equivalente (razões médias 1,0058 e 1,0043; a
diferença não é significativa para a escolha); o experimento principal usa
**random** por ter a menor razão média. Moral: sob orçamento fixo, o preço de
olhar toda a vizinhança supera o benefício de escolher o melhor passo.

## 4. Algoritmos e calibração

**Greedy Descent + Random Restart** (insertion, sucessor aleatório com
aceitação de melhora): descida até o "ótimo local" e recomeço com nova
permutação aleatória. Na variante random, o ótimo local é declarado após `|N|`
sorteios consecutivos sem melhora (critério probabilístico).

**Simulated Annealing** (insertion), resfriamento geométrico `T ← αT`:
- `T0 = −Δ̄/ln(p0)`, com `Δ̄` a média dos aumentos de `h` em 100 sucessores de
  uma solução aleatória e `p0 = 0,8`: um movimento pior típico é aceito com
  probabilidade 0,8 no início. Por depender de `Δ̄`, `T0` acompanha a escala da
  instância: medianas 2845 (pequena), 15 201 (média), 42 990 (grande).
- `Tf = 10⁻³·T0` (fim praticamente sem aceitação de piores).
- `n` propostas por temperatura; o número de patamares sai do orçamento
  restante e `α = (Tf/T0)^(1/(K−1))` (0,99834 / 0,99770 / 0,99655).
- O gráfico `sa_aceitacao.png` mostra o resultado: a taxa de aceitação de
  movimentos piores começa em cerca de 0,75-0,80 (quase random walk) e termina
  perto de 0 (quase greedy descent) nas três instâncias; a curva cai de modo
  suave, sem platô, sinal de que o schedule percorre toda a faixa útil.
- Na calibração exploratória (3 sementes), `p0 ∈ {0,5; 0,8}`,
  `Tf/T0 ∈ {10⁻², 10⁻³, 10⁻⁴}` e `n/2, n, 4n` movimentos por temperatura: na
  média as oito melhores combinações ficaram entre 16 458 e 16 809 (o padrão
  adotado não foi a primeira, mas ficou nesse grupo); na grande o padrão
  (`p0 = 0,8`, `10⁻³`, `n`) foi a melhor combinação (67 555).

**Genetic Algorithm**: população `N = 50`, seleção por **torneio** (k = 3), OX
com `Pc = 0,9`, mutação por insertion com `Pm = 0,5` por filho, elitismo 2,
parada por orçamento (a geração em curso é interrompida no ponto exato). Como
o problema é de minimização, o torneio escolhe o menor `h` e só depende da
ordem dos custos, portanto não precisa converter custo em aptidão; a roleta
(também implementada) usa `f = (h_max − h) + 1`. **OX** (exemplo numérico no
docstring de `src/cruzamentos.py` e em `testes/test_cruzamentos.py`): o filho
herda um trecho do pai 1 e completa as posições restantes com a ordem relativa
do pai 2. PMX também foi implementado e testado.
Os cromossomos são `π` (gene = posição, alelo = ativo).

O ajuste inicial do GA mostrou que a mutação por swap converge prematuramente
(população de 100 colapsando para 8-16 cromossomos distintos) e que
populações menores (mais gerações) funcionam melhor; adotou-se a combinação que
mantém diversidade (`mutação insertion`, `Pm = 0,5`, `N = 50`).

## 5. Resultados (T3)

Protocolo oficial: 50 000 / 150 000 / 300 000 avaliações; 30 / 30 / 10 execuções
independentes. Médias ± desvio (menor = melhor); `gap` relativo à referência
(1875 = ótimo; 16 332 e 60 417 = melhores conhecidos):

| instância | algoritmo | média ± desvio | mínimo | mediana | gap da média | gap do mínimo |
|---|---|---|---|---|---|---|
| pequena | Greedy | 1875,0 ± 0,0 | 1875 | 1875 | +0,00% | +0,00% |
| pequena | SA | 1875,0 ± 0,0 | 1875 | 1875 | +0,00% | +0,00% |
| pequena | GA | 1972,9 ± 133,8 | 1875 | 1937 | +5,22% | +0,00% |
| média | Greedy | 17588,2 ± 728,0 | 16460 | 17548 | +7,69% | +0,78% |
| média | **SA** | **17102,6 ± 800,1** | **16181** | 16810 | +4,72% | **−0,92%** |
| média | GA | 19367,3 ± 2106,2 | 16559 | 19315 | +18,58% | +1,39% |
| grande | Greedy | 81376,8 ± 3172,7 | 77594 | 80563 | +34,69% | +28,43% |
| grande | **SA** | **72803,7 ± 3745,0** | **66054** | 72618 | +20,50% | +9,33% |
| grande | GA | 95503,9 ± 10742,8 | 81687 | 94983 | +58,07% | +35,21% |

Na média, o SA encontrou `h = 16181`, **abaixo** do "melhor valor conhecido"
(16 332) do enunciado, que portanto não é ótimo.

**Testes (Mann-Whitney bilateral, Bonferroni `α = 0,05/3 = 0,0167`)**:

| instância | comparação | p | conclusão |
|---|---|---|---|
| pequena | Greedy × SA | 1,0 | sem diferença (ambos 30/30 no ótimo) |
| pequena | GA × Greedy / GA × SA | 2,8e-7 | Greedy e SA melhores que GA |
| média | SA × Greedy | 0,0065 | SA melhor |
| média | GA × Greedy / GA × SA | 1,8e-4 / 3,6e-6 | GA pior |
| grande | SA × Greedy | 3,3e-4 | SA melhor |
| grande | GA × Greedy / GA × SA | 1,3e-3 / 1,8e-4 | GA pior |

Figuras: `boxplots.png`, `convergencia_*.png` (mediana do melhor `h`; para o
GA, também a mediana do `h` médio da população).

**Tempo × avaliações.** Todos gastam o mesmo número de avaliações, mas o tempo de
parede por execução difere (instância grande: Greedy 25 s, SA 43 s, GA 125 s;
pequena: 1,1 s, 1,3 s, 3,3 s). As causas: o Greedy/SA avaliam sucessores
de forma incremental (`O(n−k)`) e o GA avalia filhos do zero (`O(n)`), além de
cruzamento, mutação e métricas de diversidade; o SA ainda recalcula prefixos a
cada movimento aceito (87 mil aceitações na grande). A comparação justa é por
avaliações; o tempo mostra que "mesmo orçamento" não significa "mesmo custo".
(Tempos medidos com 16 processos em paralelo; comparar entre algoritmos, não em
valor absoluto.)

## 6. Discussão

**Ótimos locais.** Na instância pequena, o greedy com best improvement encontrou
em média 62,7 ótimos locais distintos (swap), 12,8 (insertion) e 28,1 (2-opt)
por execução, e 114,5/17,1/47,9 com first improvement (valores exatos, pois
essas variantes só encerram descidas em ótimos locais verdadeiros); **todas as
30 execuções de todas as variantes alcançaram `h* = 1875`**. Ou seja, existem
muitos ótimos locais, mas com ~100-250 reinícios por execução o greedy amostra
o suficiente para acertar o global. Com insertion, o número de ótimos locais
distintos é o menor: a vizinhança é a maior, o que torna mais difícil ser ótimo
local (cada armadilha é rara), compatível com a vizinhança de melhor qualidade.
(Na variante random, 67,5 distintos em média, contagem aproximada por usar
paciência.) SA atinge `h*` em 30/30 execuções sem reinícios, escapando dos
ótimos locais por aceitar movimentos piores; o GA só em 11/30.

**Exploração × intensificação.**
- *Greedy*: intensifica na descida (só aceita melhora); explora pelo random
  restart. Mal ajustado nas instâncias grandes: com apenas 1,2 reinícios, quase
  não explora; a descida é lenta (≈ 1 300 passos) e termina no orçamento,
  sem concluir mais que um ou dois ótimos locais.
- *SA*: explora com `T` alto (≈ 80% dos piores aceitos) e intensifica quando `T`
  cai; a transição suave (figura de aceitação) é o ponto forte e explica a
  vitória na média e na grande. Na pequena o SA atinge o ótimo em 30/30 execuções, ou seja, o
  equilíbrio foi suficiente.
- *GA*: explora via população, cruzamento e mutação; intensifica via seleção e
  elitismo. Está mal ajustado: a curva do melhor e a da média da população
  permanecem distantes (convergência lenta), e o GA dá apenas ~1 042 / 3 125 /
  6 250 gerações com `N = 50`, tempo em que cada indivíduo bom quase não é
  refinado. A diversidade final (mediana) é de 21,5 / 32,5 / 36 cromossomos
  distintos entre 50 e distância média de 0,52-0,56 entre pares: **não há
  colapso de diversidade** (a convergência prematura não é o problema); a
  mutação mantém a população dispersa, mas os indivíduos não ficam bons o bastante.
  O GA se comporta como busca de passo largo sem intensificação local.

**Efeito da escala.** O ranking muda da pequena para a média/grande, **mas só
no topo**: na pequena Greedy e SA empatam (ambos no ótimo, p = 1); na média e na
grande o SA vence o Greedy (p = 0,0065 e 3,3e-4). O GA é o pior nas três. Hipótese:
na pequena, `|N| = 66` e o orçamento permite ≈ 150 reinícios completos, então
a amostragem de ótimos locais basta; conforme `n` cresce, o espaço de busca
(`n!`) e `|N|` crescem, o greedy faz poucos reinícios (11,7 na média, 1,2 na
grande) e fica preso em ótimos locais de baixa qualidade, enquanto o SA usa
todo o orçamento em 41 mil/87 mil movimentos aceitos, escapando por aceitar
pioras. O argumento é coerente com os dados (reinícios por execução e passos),
mas a causa não foi isolada em um experimento controlado.

**Quando o GA compensa? Experimento adicional.** Hipótese: o OX só ajuda se
combinar trechos bons de dois pais gerar filhos melhores; como `h` depende do
**instante de chegada** (tempo acumulado), um trecho bom no pai pode deixar de
ser bom em outra posição, o que enfraquece a recombinação. Teste: o mesmo GA
(`N = 50`, `Pm = 0,5`) com `Pc = 0,9` + OX (padrão), com PMX e **sem
cruzamento** (`Pc = 0`), mesmas sementes e orçamento. Resultados (média ± desvio):

| instância | OX | PMX | sem cruzamento |
|---|---|---|---|
| pequena | 1972,9 ± 133,8 | 1941,7 ± 127,1 | 1982,6 ± 141,5 |
| média | 19367,3 ± 2106,2 | 20295,3 ± 3094,4 | 20493,9 ± 2220,5 |
| grande | 95503,9 ± 10742,8 | 89426,0 ± 8812,0 | 85659,2 ± 10520,4 |

Nenhuma diferença é significativa após Bonferroni (menor p: 0,0257, grande,
OX × sem cruzamento, **a favor de não cruzar**; na média, OX × sem cruzamento
p = 0,035, a favor do OX). A conclusão honesta é que, nestas instâncias e
parâmetros, **a recombinação não trouxe ganho demonstrável**, e o GA não superou
(nem aproximou) as buscas locais em nenhuma instância. O experimento
é coerente com a hipótese, mas não a prova (poderia haver ganho com outros
operadores, por exemplo OX com reparos por prazo, ou GA memético).

## 7. Limitações

- Ajuste de parâmetros pequeno e exploratório (médias/grande, sementes 0-2,
  coincidentes com as primeiras sementes oficiais). Para o GA, outros
  operadores/parâmetros podem diminuir a distância para o SA.
- Greedy `random`: ótimo local por paciência (aproximado).
- Referências 16 332 e 60 417 não são ótimos (a média já foi superada pelo SA).
- Instância grande: apenas 10 execuções (poder estatístico menor).
- Tempos medidos em paralelo (contenção).

## 8. Reprodução

Ver `README.md` (seção "Reprodução dos resultados"): `python -m src.experimentos
tudo`. As sementes são fixas e derivadas de (instância, algoritmo, variante,
vizinhança, índice): os valores de `h` são reproduzíveis exatamente.
