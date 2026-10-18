# TP2 - Busca Local e Algoritmo Genético

Trabalho Prático 2 da disciplina Fundamentos de Inteligência Artificial - UFMG.

## Instalação

```bash
python -m venv .venv
```

Ativar no Windows:

```bash
.venv\Scripts\activate
```

Ativar no Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar as dependências:

```bash
pip install -r requirements.txt
```

## Testes

```bash
python -m pytest
```

Validação direta da função `h` nos casos de referência do enunciado:

```bash
python -m src.experimentos validar
```

## Experimentos

Executar todo o protocolo oficial (T1, T2, avaliação incremental, T3 e experimento adicional do GA):

```bash
python -m src.experimentos tudo
```

Ou executar cada etapa separadamente:

```bash
python -m src.experimentos t2
python -m src.experimentos incremental
python -m src.experimentos t3
python -m src.experimentos extra
```

## Resultados

Os CSVs brutos são salvos em `resultados/`:

- `resultados/t2_vizinhancas.csv`
- `resultados/incremental.csv`
- `resultados/t3_principal.csv`
- `resultados/t3_convergencia.csv`
- `resultados/t3_sa_aceitacao.csv`
- `resultados/t3_ga_geracoes.csv`
- `resultados/extra_ga_sem_cruzamento.csv`

As tabelas consolidadas são salvas em `resultados/tabelas.md` e os gráficos em `resultados/figuras/`.

## Reprodução das tabelas e figuras

Comparação das vizinhanças:

```bash
python -m src.analise vizinhancas
```

Tabela principal:

```bash
python -m src.analise tabela
```

Boxplots:

```bash
python -m src.analise boxplots
```

Curvas de convergência:

```bash
python -m src.analise convergencia
```

Taxa de aceitação do Simulated Annealing:

```bash
python -m src.analise aceitacao
```

Diversidade do Genetic Algorithm:

```bash
python -m src.analise diversidade
```
