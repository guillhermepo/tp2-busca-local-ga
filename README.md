# TP2 - Busca Local e Algoritmo Genético

Trabalho Prático 2 - Fundamentos de Inteligência Artificial - UFMG.

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

No Linux/macOS, ative o ambiente com `source .venv/bin/activate`.

## Testes

```bash
python -m pytest
```

## Validação

```bash
python -m src.experimentos validar
```

## Comparação das vizinhanças

```bash
python -m src.experimentos t2
python -m src.experimentos incremental
python -m src.analise vizinhancas
```

Após analisar a T2, escolha a vizinhança utilizada nos experimentos principais.

## Calibração do SA

```bash
python -m src.experimentos calibrar_sa insertion
```

## Experimentos principais

```bash
python -m src.experimentos t3 insertion first
```

## Experimento adicional do GA

```bash
python -m src.experimentos extra
```

## Reprodução das tabelas e figuras

Tabela principal:

```bash
python -m src.analise tabela
```

Boxplots:

```bash
python -m src.analise boxplots
```

Convergência:

```bash
python -m src.analise convergencia
```

Aceitação do SA:

```bash
python -m src.analise aceitacao
```

Diversidade do GA:

```bash
python -m src.analise diversidade
```
