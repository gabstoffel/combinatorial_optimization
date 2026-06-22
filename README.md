# Os Melhores Amigos (OMA)

INF05010 — Otimização Combinatória (UFRGS)
Gabriel Stoffel e Rodrigo Feldens

Dado um conjunto de `n` pessoas e a afinidade entre cada par, o problema consiste
em escolher exatamente `m` pessoas maximizando a soma das afinidades dentro do
grupo. Resolvemos o problema de duas maneiras: por uma formulação inteira
resolvida com um solver genérico (HiGHS ou CPLEX) e por uma meta-heurística de
Busca Tabu.

## Dependências

Usamos Python 3.12 e o [uv](https://docs.astral.sh/uv/) para o ambiente. As
dependências (HiGHS e PuLP) são software livre. Para instalar:

```bash
uv sync
```

O CPLEX é opcional, usado apenas na comparação do relatório, e não é necessário
para executar o trabalho.

## Execução

A instância é lida da entrada padrão e o primeiro argumento é o arquivo onde a
melhor solução é gravada (a solução também é escrita na saída padrão):

```bash
uv run oma-solve <arquivo_saida> [opções] < <instancia>.dat
```

O modelo exato e a heurística são executados separadamente, um por chamada:

```bash
uv run oma-solve solucao.txt --highs --time-limit 600 < dataset/oma01.dat
uv run oma-solve solucao.txt --tabu < dataset/oma01.dat
```

## Formato da entrada e da saída

A entrada segue o formato das instâncias: a primeira linha traz `n m` e cada
linha seguinte traz `i j a`, a afinidade `a` entre as pessoas `i` e `j`
(com `i < j`, índices base 0).

A saída tem duas linhas — o valor objetivo e os `m` índices escolhidos, em ordem
crescente:

```
472
7 30 33 37 42 51 52 65 72 77 109 116
```

## Parâmetros

Busca Tabu (padrões entre parênteses): `--tenure` (10), `--max-iter` (1000),
`--max-no-improve` (100), `--diversify-freq` (50, `0` desliga a perturbação),
`--init` (greedy, ou random) e `--seed` (0). Para o solver exato: `--time-limit`
(600 segundos).

```bash
uv run oma-solve solucao.txt --tabu --tenure 15 --max-iter 5000 --seed 7 < dataset/oma06.dat
```

## Organização

A Busca Tabu e as construções iniciais estão em `src/oma/metaheuristica/`; a
formulação inteira e a interface com os solvers, em `src/oma/solvers/`. As 10
instâncias estão em `dataset/` e o relatório em `report/`.
