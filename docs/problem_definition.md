# Os Melhores Amigos

**INF05010 -- Otimização Combinatória**

Gabriel Stoffel | Rodrigo Feldens

## Instância

Dado um conjunto de $n$ pessoas $P = [n]$, um valor de afinidade não negativo $a_{ij} \geq 0$ para cada par $\{i, j\}$ ($i < j$), e um inteiro $m$.

## Solução

Uma solução é um subconjunto $S \subseteq P$ com exatamente $m$ pessoas.

## Objetivo

Maximizar a afinidade total do grupo:

$$A(S) = \sum_{\{i,j\} \subseteq S} a_{ij}$$

## Formato das Instâncias

Cada arquivo de instância (`.dat`) segue o formato:

1. Primeira linha: `n m` -- $n$ = número de pessoas, $m$ = tamanho do grupo a selecionar.
2. Demais linhas: `i j a` -- índices $i$ e $j$ (base 0, com $i < j$) e afinidade $a$ entre o par.

Todos os pares são listados uma única vez.

## Melhores Valores Conhecidos (BKV)

| Instância | BKV | Instância | BKV |
|-----------|-----|-----------|-----|
| oma01     | 472 | oma06     | 719 |
| oma02     | 474 | oma07     | 724 |
| oma03     | 470 | oma08     | 732 |
| oma04     | 470 | oma09     | 733 |
| oma05     | 474 | oma10     | 721 |
