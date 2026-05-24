# Plano de Implementação -- Busca Tabu

## 1. Representação da Solução

Uma solução $S$ é um subconjunto de $P$ com cardinalidade $|S| = m$. Ou seja, $S$ é um subconjunto com $m$ pessoas.

## 2. Solução Inicial (Construção Gulosa)

Dado o conjunto $P$ de pessoas e uma matriz de afinidades $a$:

```
solucao = set()
while |solucao| != m:
    max_ganho = -1
    melhor_pessoa = None
    for p in P:
        if p in solucao:
            continue
        ganho = sum(a[i][p] for i in solucao)
        if ganho > max_ganho:
            melhor_pessoa = p
            max_ganho = ganho
    solucao.add(melhor_pessoa)
```

**Obs**: Na implementação, manter um vetor de ganhos incrementais para evitar recalcular a soma de afinidades a cada iteração, reduzindo a complexidade.

## 3. Vizinhança

Dada uma solução $S = \{p_1, p_2, \ldots, p_m\}$, um vizinho $S'$ é obtido por troca (swap):

$$S' = (S \setminus \{p\}) \cup \{p'\} \quad \text{tal que } p \in S,\; p' \notin S$$

## 4. Critério de Parada

- Número máximo de iterações.
- Número máximo de iterações sem melhora.

A cada iteração, manter um contador para verificar se houve melhora na função objetivo.

## 5. Função Objetivo e Delta

A função objetivo é a soma das afinidades entre todos os pares de pessoas na solução $S$.

Para evitar recalcular a função objetivo inteira, usar a expressão de delta ao trocar $p$ por $p'$:

$$\Delta = A(S') - A(S) = -\sum_{i \in S \setminus \{p\}} a[p][i] + \sum_{i \in S \setminus \{p\}} a[p'][i]$$

## 6. Lista Tabu

A lista tabu $T$ armazena pessoas recentemente removidas da solução. Cada pessoa permanece na lista tabu por um número determinado de iterações (tenure), impedindo sua reinserção imediata e evitando ciclos.
