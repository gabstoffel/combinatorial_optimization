# Parâmetros da Busca Tabu

Este documento descreve os parâmetros ajustáveis da meta-heurística (construção gulosa + Busca
Tabu) usados no problema OMA. Eles são a base do plano de experimentos em
[`test_plan.md`](test_plan.md); os valores de referência (BKV) estão em [`bkv.md`](bkv.md) e a
descrição da abordagem em [`implementation_plan.md`](implementation_plan.md).

## Parâmetros da Busca Tabu

Assinatura em `src/oma/metaheuristica/tabu_search.py`:
`run_tabu_search(instance, initial_solution, max_iter, max_no_improve, tenure, diversify_freq)`.

| Parâmetro        | Tipo | Padrão | Domínio sugerido | Significado e efeito na busca |
|------------------|------|-------:|------------------|-------------------------------|
| `max_iter`       | int  |   1000 | $\geq 1$         | Número máximo de iterações. Limita o esforço total; valores maiores exploram mais, ao custo de tempo. |
| `max_no_improve` | int  |    100 | $\geq 1$         | Número máximo de iterações **sem melhora** do melhor valor antes de parar. Controla a paciência da busca; valores baixos param cedo, altos insistem em regiões já exploradas. |
| `tenure`         | int  |     10 | $1$ a $\sim 50$  | Tempo (em iterações) que uma pessoa removida fica proibida de retornar à solução. Tenure pequeno permite reversões rápidas (risco de ciclos); grande força mais diversificação, podendo bloquear bons movimentos. |
| `diversify_freq` | int  |     50 | $0$ ou $\geq 1$  | A cada `diversify_freq` iterações aplica-se uma perturbação aleatória (troca de uma pessoa) para escapar de ótimos locais. **`0` desliga** a diversificação periódica. |

Notas de comportamento (ver `tabu_search.py`):

- **Critério de aspiração**: um movimento tabu é permitido se levar a um valor melhor que o
  melhor global já encontrado (`current_obj + delta > best_obj`).
- **Parada**: a busca termina quando `iter_count >= max_iter` **ou**
  `iters_without_improvement >= max_no_improve`.
- **Avaliação incremental (delta)**: o ganho de uma troca é calculado em $O(m)$, sem recomputar
  toda a função objetivo $A(S)$.

## Solução inicial (construção gulosa)

Assinatura em `src/oma/metaheuristica/greedy.py`:
`greedy_construction(instance, start_person=None)`.

| Parâmetro      | Tipo      | Padrão     | Domínio          | Significado e efeito |
|----------------|-----------|------------|------------------|----------------------|
| `start_person` | int\|None | None (aleatório) | $0 \dots n-1$ | Pessoa de partida da construção gulosa. Com `None`, é sorteada aleatoriamente (`random.randint`), evitando o viés de começar sempre pela pessoa 0. |

Como a partida é aleatória por padrão, a **solução inicial (SI) é estocástica entre réplicas**:
sementes diferentes produzem SIs (e, portanto, SFs) diferentes. Isso justifica reportar médias
sobre várias sementes.

## Semente aleatória (reprodutibilidade)

| Parâmetro | Tipo | Significado |
|-----------|------|-------------|
| `seed`    | int  | Semente do gerador `random`. Governa a partida do greedy e as perturbações da Busca Tabu. **Mesma semente + mesmos parâmetros ⇒ mesma solução**, garantindo reprodutibilidade. |

Para os experimentos estocásticos, fixa-se uma lista de sementes e reporta-se a média (e
desvio-padrão) sobre elas — ver [`test_plan.md`](test_plan.md).

## Configuração baseline

Configuração de referência usada como ponto fixo nas varreduras de sensibilidade (varia-se um
parâmetro por vez, mantendo os demais nestes valores):

| Parâmetro        | Valor baseline |
|------------------|---------------:|
| `tenure`         |             10 |
| `max_no_improve` |            100 |
| `max_iter`       |           1000 |
| `diversify_freq` |             50 |
| solução inicial  | greedy (partida aleatória) |
