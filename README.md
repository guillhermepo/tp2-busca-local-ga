# TP2 - Busca Local e Algoritmo Genético

## 1. Nome do Projeto
**TP2 - Busca Local e Algoritmo Genético**

## 2. Disciplina
Fundamentos de Inteligência Artificial (UFMG)

## 3. Descrição Breve
O trabalho aborda a aplicação de técnicas de Busca Local (Greedy Descent, Simulated Annealing) e Algoritmos Genéticos para o problema de sequenciamento de manutenção de ativos. Uma única equipe parte de uma base e deve visitar um conjunto de ativos, cada um com coordenadas `(x, y)`, duração `p`, prazo `d` e peso de criticidade `w`. O objetivo é minimizar o atraso ponderado total `h(π)` da ordem de visita `π`.

## 4. Algoritmos Planejados
- **Greedy Descent** (Best Improvement & First Improvement) com Random Restart
- **Simulated Annealing**
- **Algoritmo Genético**

> **Nota:** Ainda não implementados – estrutura dos módulos está preparada.

## 5. Estrutura do Repositório
```
 tp2-busca-local-ga/
 ├─ dados/                     # instâncias fornecidas pelo professor
 │   ├─ manutencao_pequena.txt
 │   ├─ manutencao_media.txt
 │   └─ manutencao_grande.txt
 ├─ src/                       # código fonte
 │   ├─ problema.py            # leitura, representação e avaliação
 │   ├─ greedy.py              # estratégias greedy
 │   ├─ vizinhancas.py         # operadores de vizinhança (Swap, Insertion, 2‑opt)
 │   └─ experimentos.py        # orquestração de experimentos
 ├─ resultados/                # arquivos CSV de resultados
 │   └─ .gitkeep
 ├─ testes/                    # suit de testes com pytest
 │   └─ test_problema.py
 ├─ .gitignore                 # arquivos a serem ignorados pelo Git
 ├─ requirements.txt           # dependências do projeto
 └─ README.md                  # este documento
```

## 6. Instâncias de Dados
| Instância | Nº de ativos | Comentário |
|-----------|--------------|------------|
| `manutencao_pequena.txt` | 12 | Utilizada nos testes iniciais (h([1..12]) = 4366) |
| `manutencao_media.txt`   | 50 | Instância média para experimentos |
| `manutencao_grande.txt`  | 150| Instância grande para experimentos |

> **Importante:** Não altere o conteúdo destes arquivos.

## 7. Criação e Ativação do Ambiente Virtual
```powershell
# Crie o ambiente virtual (único para este projeto)
python -m venv .venv

# Ative o ambiente (PowerShell)
.\.venv\Scripts\Activate.ps1
```

## 8. Instalação das Dependências
```bash
pip install -r requirements.txt
```

## 9. Execução do Código
> Ainda não há scripts executáveis. Quando os algoritmos forem implementados, o ponto de entrada será algo como:
```bash
python -m src.experimentos --algoritmo greedy --instancia dados/manutencao_pequena.txt
```

## 10. Execução dos Testes
```bash
pytest
```
Os testes atuais são placeholders; eles serão preenchidos conforme as funções forem desenvolvidas.

## 11. Reprodução dos Resultados
Quando as implementações estiverem completas, a seção deverá conter instruções para reproduzir:
- resultados brutos (CSV em `resultados/`)
- tabelas principais do relatório
- box‑plots de desempenho
- curvas de convergência
- gráficos de aceitação do Simulated Annealing
- análise de diversidade do Algoritmo Genético

## 12. Integrantes do Grupo
| Nome | Papel | Contato |
|------|-------|--------|
| **[Seu Nome]** | Leitura de instâncias, representação, cálculo de distâncias, avaliação `h`, geração aleatória, Greedy Descent, Random Restart, controle de orçamento, experimentos e relatório | email@example.com |
| **[Outro Integrante]** | Operadores de vizinhança, avaliação incremental | email2@example.com |

---
*Este README foi gerado inicialmente e será atualizado à medida que o desenvolvimento avançar.*

