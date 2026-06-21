# Plano de Testes — Busca Tabu (OMA)

Este plano define os experimentos para avaliar a Busca Tabu no problema OMA e medir **como a
variação de cada parâmetro afeta a solução final**. A estrutura segue o relatório de referência
([`reference_report.md`](reference_report.md), seções 7 e 8). Os parâmetros estão definidos em
[`parameters.md`](parameters.md) e os melhores valores conhecidos em [`bkv.md`](bkv.md).

## 1. Objetivo

Determinar a sensibilidade da solução final a cada parâmetro da Busca Tabu, propor uma
configuração tunada e comparar o desempenho da meta-heurística com o solver exato e com o BKV.

## 2. Metodologia

Varredura *one-factor-at-a-time*: varia-se **um parâmetro por vez**, mantendo os demais na
configuração baseline (ver [`parameters.md`](parameters.md)). Cada caso é executado sobre as
**10 instâncias** `oma01`–`oma10` com **pelo menos 5 sementes distintas**; reporta-se a **média**
(e o desvio-padrão) sobre as sementes. Por ser um método estocástico, nenhuma conclusão é tirada
de uma execução isolada.

## 3. Métricas e fórmulas

Para cada execução registram-se:

- **SI** — valor da solução inicial (greedy).
- **SF** — valor da solução final (após a Busca Tabu).
- **Desvio em relação à inicial**: $100 \cdot (SI - SF) / SI$. Por ser maximização, $SF \geq SI$
  e o valor é $\leq 0$ (coerente com os valores negativos do relatório de referência).
- **Desvio em relação ao BKV**: $100 \cdot (BKV - SF) / BKV$ — quanto menor, mais próximo do ótimo.
- **Tempo da meta-heurística** e **tempo do solver** (ms).

Para os gráficos de sensibilidade, normaliza-se o valor da solução pelo BKV (percentual de
otimalidade) e analisa-se em função do parâmetro variado, em paralelo com o tempo de execução.

## 4. Experimento A — Sensibilidade por parâmetro

Cada subseção varia um parâmetro sobre o conjunto indicado, mantendo os demais no baseline,
em todas as 10 instâncias, com 5 sementes.

| # | Parâmetro variado | Valores testados | Demais parâmetros | Execuções |
|---|-------------------|------------------|-------------------|----------:|
| A1 | `tenure` | 1, 3, 5, 7, 10, 15, 20, 30, 50 | baseline | 9 × 10 × 5 = 450 |
| A2 | `max_no_improve` | 25, 50, 100, 200, 400, 800 | baseline | 6 × 10 × 5 = 300 |
| A3 | `max_iter` | 250, 500, 1000, 2000, 5000 | baseline | 5 × 10 × 5 = 250 |
| A4 | `diversify_freq` | 0, 10, 25, 50, 100, 200 | baseline | 6 × 10 × 5 = 300 |
| A5 | solução inicial | greedy vs. aleatória pura | baseline | 2 × 10 × 5 = 100 |

Observações:

- Em **A4**, o valor `0` desliga a diversificação periódica (Busca Tabu "pura").
- Em **A5**, compara-se a partida gulosa (que já é aleatória na pessoa inicial) contra uma
  solução inicial totalmente aleatória, para medir o ganho da construção gulosa.
- Total do Experimento A: **≈ 1400 execuções** da heurística.

Para cada parâmetro, espera-se uma análise (texto + gráfico) da forma da curva
qualidade × valor do parâmetro e tempo × valor do parâmetro, concluindo por um valor recomendado.

## 5. Experimento B — Instâncias × configurações

Análogo à seção 8 do relatório de referência: rodar as **10 instâncias** em 3 configurações,
com 5 sementes cada, e comparar com o solver e o BKV.

| Configuração | Descrição |
|--------------|-----------|
| Baseline | valores default (ver [`parameters.md`](parameters.md)) |
| Tunada | melhores valores obtidos no Experimento A |
| Degenerada | `diversify_freq = 0` (Busca Tabu sem diversificação periódica), para medir o impacto da diversificação |

Execuções: 3 × 10 × 5 = **150** da heurística, mais **10** execuções determinísticas do solver.

**Tabela de resultados** (uma linha por instância, por configuração) — formato exigido pelo
enunciado:

| Instância | SI | SF | Desvio p/ SI (%) | Desvio p/ BKV (%) | Tempo MH (ms) | Tempo Solver (ms) | Semente |
|-----------|---:|---:|-----------------:|------------------:|--------------:|------------------:|--------:|

Os valores estocásticos (SI, SF, tempos) são médias sobre as 5 sementes; a semente reportada
pode ser a da melhor réplica.

## 6. Reprodutibilidade

- **Sementes** (lista fixa): 1, 2, 3, 4, 5 (ou outras 5 documentadas no relatório).
- **Hardware/SO**: registrar processador, memória e SO usados nas execuções.
- **Versões**: Python 3.12; solver HiGHS (`highspy`); gerenciamento via `uv`.
- **Linhas de comando**: documentar o comando exato usado para cada execução (instância via
  stdin, primeiro argumento = arquivo de saída da melhor solução, parâmetros via CLI), conforme
  as convenções da Seção 6 de [`specification.md`](specification.md).

## 7. Formato de saída (JSON)

Cada execução gera um registro JSON, estendendo o esquema de `src/oma/logger.py`:

```json
{
  "instance": "oma01",
  "method": "tabu",
  "params": {
    "max_iter": 1000,
    "max_no_improve": 100,
    "tenure": 10,
    "diversify_freq": 50,
    "initial": "greedy"
  },
  "seed": 1,
  "initial_solution": 0.0,
  "final_solution": 0.0,
  "dev_initial_pct": 0.0,
  "dev_bkv_pct": 0.0,
  "time_ms": 0.0
}
```

Um JSON **agregado** resume cada par (instância, configuração) com a média e o desvio-padrão
sobre as sementes — base direta para as tabelas e gráficos do relatório:

```json
{
  "instance": "oma01",
  "config": "baseline",
  "replications": 5,
  "final_solution_mean": 0.0,
  "final_solution_std": 0.0,
  "dev_bkv_pct_mean": 0.0,
  "time_ms_mean": 0.0
}
```
