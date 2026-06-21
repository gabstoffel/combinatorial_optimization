# Especificação do Trabalho — Os Melhores Amigos (OMA)

> Documento guarda-chuva: reúne o contexto do trabalho, as decisões tomadas, as
> convenções obrigatórias, o cronograma e o estado atual da implementação. Os
> detalhes técnicos vivem nos documentos referenciados ao longo do texto.

## 1. Identificação

- **Disciplina**: INF05010 — Otimização Combinatória (UFRGS).
- **Integrantes**: Gabriel Stoffel e Rodrigo Feldens (grupo de 2).
- **Problema escolhido**: *Os Melhores Amigos* / *Maximum Affinity Group Selection* (OMA).
- **Meta-heurística escolhida**: **Busca Tabu (BT)**.

Cada combinação problema + meta-heurística é única na turma; esta foi reservada por email.

## 2. Objetivo do trabalho

O propósito é **conhecer profundamente uma meta-heurística** e ganhar experiência prática
para aplicá-la a novos problemas. Concretamente, o grupo deve:

- Formular o problema como um programa (inteiro) linear.
- Resolver as instâncias com um solver genérico (HiGHS/CPLEX/GLPK/SCIP).
- Definir e implementar a meta-heurística escolhida para o problema.
- Resolver as instâncias com a meta-heurística.
- Documentar e analisar os experimentos em um relatório.
- Apresentar os resultados em aula.

## 3. Descrição do problema

Dado um conjunto de $n$ pessoas $P = [n]$, um valor de afinidade não negativo
$a_{ij} \geq 0$ para cada par $\{i,j\}$ com $i < j$, e um inteiro $m$, deseja-se escolher
um subconjunto $S \subseteq P$ com **exatamente** $m$ pessoas que maximize a afinidade total:

$$A(S) = \sum_{\{i,j\} \subseteq S} a_{ij}$$

Definição completa e melhores valores conhecidos (BKV): ver
[`problem_definition.md`](problem_definition.md).

**Formato das instâncias** (ver [`dataset/Readme.md`](../dataset/Readme.md)):

- 1ª linha: `n m` — número de pessoas e tamanho do grupo a selecionar.
- Demais linhas: `i j a` — índices $i$ e $j$ (base 0, $i < j$) e afinidade $a$ do par.

Há 10 instâncias de teste, `oma01.dat` … `oma10.dat`, em `dataset/`.

### Melhores Valores Conhecidos (BKV)

| Instância | BKV | Instância | BKV |
|-----------|----:|-----------|----:|
| oma01     | 472 | oma06     | 719 |
| oma02     | 474 | oma07     | 724 |
| oma03     | 470 | oma08     | 732 |
| oma04     | 470 | oma09     | 733 |
| oma05     | 474 | oma10     | 721 |

## 4. Formulação matemática

Programa inteiro com variáveis binárias $x_i$ (pessoa $i$ selecionada) e $z_{ij}$
(linearização do produto $x_i \cdot x_j$), sujeito à cardinalidade $\sum_i x_i = m$.
Formulação completa e explicação das restrições: ver [`formulation.md`](formulation.md).

## 5. Abordagem meta-heurística — Busca Tabu

Resumo dos elementos exigidos na avaliação (detalhes em
[`implementation_plan.md`](implementation_plan.md)):

- **Representação da solução**: subconjunto $S \subseteq P$ com $|S| = m$.
- **Solução inicial**: construção gulosa por ganho incremental (vetor de ganhos para evitar
  recálculo da função objetivo).
- **Vizinhança**: troca (*swap*) $S' = (S \setminus \{p\}) \cup \{p'\}$, com $p \in S$ e
  $p' \notin S$.
- **Função objetivo e delta**: avaliação incremental do ganho de uma troca, sem recalcular
  $A(S)$ inteira.
- **Lista tabu e tenure**: pessoas recentemente removidas ficam tabu por um número de
  iterações (tenure), evitando ciclos.
- **Critério de aspiração**: um movimento tabu é permitido se melhora o melhor valor global.
- **Diversificação**: perturbações periódicas para escapar de ótimos locais.
- **Critérios de parada**: número máximo de iterações e número máximo de iterações sem melhora.

## 6. Convenções de implementação (obrigatórias)

Requisitos verificáveis impostos pelo enunciado:

- A implementação lê a instância na **entrada padrão (stdin)**.
- Imprime a melhor solução encontrada na **saída padrão (stdout)**.
- O **primeiro parâmetro da linha de comando é o nome do arquivo** onde gravar a melhor
  solução encontrada.
- Os principais parâmetros do método são definíveis por linha de comando (ex.: `tenure`,
  `max_iter`, `max_no_improve`, semente aleatória).
- Apenas **software livre**, sem bibliotecas proprietárias: HiGHS é open-source; CPLEX é
  opcional. Linguagem: Python 3.12, gerenciado com `uv`.

## 7. Estrutura do repositório

```
.
├── docs/
│   ├── specification.md          (este documento)
│   ├── problem_definition.md     (definição do problema + BKV)
│   ├── formulation.md            (formulação inteira)
│   └── implementation_plan.md    (plano da Busca Tabu)
├── dataset/
│   ├── Readme.md                 (formato das instâncias)
│   └── oma01.dat … oma10.dat     (instâncias de teste)
├── src/oma/
│   ├── main.py                   (ponto de entrada / parser de argumentos)
│   ├── instance.py               (estrutura de dados da instância)
│   ├── logger.py                 (registro de execuções em JSON)
│   ├── solvers/
│   │   ├── model.py              (modelo PLI em PuLP)
│   │   └── generic.py            (fábrica de solver: HiGHS, CPLEX)
│   └── metaheuristica/
│       ├── greedy.py             (construção gulosa)
│       └── tabu_search.py        (Busca Tabu)
├── pyproject.toml / uv.lock      (dependências: highspy, pulp)
└── README.md
```

## 8. Protocolo experimental

Para alinhar com os critérios de reprodutibilidade e avaliação:

- Executar todas as 10 instâncias `oma01` … `oma10`.
- Por ser estocástica, a Busca Tabu deve reportar **média de pelo menos 5 replicações** por
  instância, com **sementes diferentes** e documentadas.
- Documentar parâmetros, método de escolha de parâmetros, tempo de execução, número de
  experimentos e dados experimentais.
- Para cada instância, registrar: valor da solução inicial (SI), valor da solução final (SF),
  desvio percentual da SF em relação à SI — $100 \cdot (SI - SF) / SI$ —, desvio percentual da
  SF em relação ao ótimo, tempo da meta-heurística e tempo do solver.
- O módulo `logger.py` já grava resultados em JSON (`logs/omaXX_METODO.json`), base para a
  agregação das replicações e a tabela final.

## 9. Entregáveis e prazos

**Entregáveis**:

- **Relatório** no formato das normas SOBRAPO (≤ 12 páginas, fonte 11pt, sem uso excessivo de
  listas), com as seções obrigatórias: Introdução, Formulação, Descrição da solução,
  Resultados obtidos com análise, Conclusão e Bibliografia.
- **Implementação** do modelo matemático e da heurística (somente software livre).
- **Tabela de resultados** com as métricas descritas na Seção 8.
- **Protocolos** das execuções do solver e da meta-heurística e demais dados experimentais.
- **Apresentação** em aula.

**Cronograma**:

| Etapa                       | Prazo          |
|-----------------------------|----------------|
| Proposta da heurística      | 01/04/2026     |
| Formulação matemática       | 06/05/2026     |
| Entrega do trabalho completo| 22/06/2026     |
| Apresentação em aula        | a definir      |

## 10. Diretrizes do relatório (como não perder pontos)

Checklist derivado do material "Como perder pontos" (Marcus Ritt):

- **Não omitir** o modelo matemático (e *explicá-lo*), os resultados do modelo, os resultados
  da heurística, a conclusão nem as referências bibliográficas.
- **Não incluir** código-fonte no relatório nem detalhes irrelevantes de implementação
  (frameworks, comandos de execução, threads, etc.).
- **Ser concreto**: evitar afirmações vagas ou exageradas ("convergência incrivelmente
  rápida", "mostrou-se eficiente") sem números que as sustentem.
- Evitar introduções genéricas e clichês ("cada vez mais…", "o que fiz nas férias").
- Apresentar **conclusões apoiadas em evidência** (dados e tabelas), não opinião.
- Tratar NP-dificuldade com correção e apenas se for relevante; não banalizar.
- Cuidar da forma: sem erros ortográficos/gramaticais, sem plágio, figuras de boa qualidade,
  **colunas numéricas alinhadas à direita** e sem citar artigos recentes para fatos
  consolidados.

## 11. Estado atual e pendências

**Já implementado**:

- Solver exato: modelo PLI em PuLP (`solvers/model.py`) e fábrica de solver HiGHS/CPLEX
  (`solvers/generic.py`).
- `Instance.affinity` (`instance.py`): matriz n×n simétrica construída a partir da lista de
  arestas `a`, usada pela metaheurística.
- Construção gulosa (`metaheuristica/greedy.py`) e Busca Tabu (`metaheuristica/tabu_search.py`).
- Pipeline em `main.py` com parser de flags (`--cplex` / `--highs` / `--tabu`) que roda o solver
  e/ou a metaheurística sobre uma ou todas as instâncias, com 5 sementes na metaheurística.
- Registro de execuções em JSON (`logger.py`), **incluindo os parâmetros usados** (`params`),
  para reprodutibilidade.

**Pendências conhecidas**:

- O I/O **ainda não** segue a convenção obrigatória: stdin para a instância, stdout para a
  solução, e primeiro argumento da linha de comando como arquivo de saída (ver Seção 6).
- A metaheurística já registra **todas** as réplicas (uma linha JSONL por semente, com `params`
  e `config_id`); falta a agregação estatística (média e desvio-padrão sobre as ≥5 sementes) e a
  geração da tabela de resultados final (ver [`test_plan.md`](test_plan.md)).
- `README.md` está vazio.
