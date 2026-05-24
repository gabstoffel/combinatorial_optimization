# Formulação como Programa Inteiro

## Variáveis de Decisão

- $x_i \in \{0, 1\}$ para todo $i \in [n]$: indica se a pessoa $i$ foi selecionada.
- $z_{ij} \in \{0, 1\}$ para todo $i, j \in [n]$ com $i < j$: linearização do produto $x_i \cdot x_j$, de modo que $z_{ij} = 1$ apenas quando ambas as pessoas $i$ e $j$ pertencem à solução, permitindo contabilizar a afinidade da aresta $\{i, j\}$.

## Formulação

$$\max \sum_{\substack{i,j \in [n] \\ i < j}} a_{ij}\, z_{ij}$$

Sujeito a:

$$\sum_{i=1}^{n} x_i = m$$

$$z_{ij} \leq x_i \quad \forall\, i, j \in [n],\; i < j \qquad (1)$$

$$z_{ij} \leq x_j \quad \forall\, i, j \in [n],\; i < j \qquad (2)$$

$$z_{ij} \geq x_i + x_j - 1 \quad \forall\, i, j \in [n],\; i < j \qquad (3)$$

$$x_i \in \{0, 1\} \quad \forall\, i \in [n] \qquad (4)$$

$$z_{ij} \in \{0, 1\} \quad \forall\, i, j \in [n],\; i < j \qquad (5)$$

### Explicação das restrições

- **Cardinalidade**: Exatamente $m$ pessoas devem ser selecionadas.
- **(1) e (2)**: $z_{ij}$ só pode ser 1 se ambos $x_i$ e $x_j$ forem 1.
- **(3)**: Força $z_{ij} = 1$ quando ambos $x_i = 1$ e $x_j = 1$ (garante que a afinidade é contabilizada).
- **(4) e (5)**: Restrições de integralidade.
