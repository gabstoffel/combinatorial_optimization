# Setup do Solver Exato e Taxonomia de `results/`

Documenta o que foi implementado para rodar os solvers exatos (HiGHS/CPLEX) nas 10
instâncias gerando estatísticas no mesmo padrão da metaheurística, e a reorganização
da árvore de resultados.

## 1. Solver exato no mesmo padrão da metaheurística

O runner (`uv run oma`) agora roteia o solver exato exatamente como a tabu:

```bash
uv run oma all --highs --time-limit 600 --config-id tl-600 --out-dir results/solver/highs/M2
uv run oma all --cplex --time-limit 600 --config-id tl-600 --out-dir results/solver/cplex/M2
```

- `all` roda as 10 instâncias em sequência (ou `1..10` para uma só).
- **`--time-limit`** (novo): tempo limite do solver em segundos (default 600). Antes era
  hardcoded.
- Saída auto-descritiva em `<out-dir>/<config-id>/omaNN_<solver>.jsonl` (append) +
  `config.json`, via `append_solver_run`/`write_config` em `src/oma/logger.py`.
- Solver é **determinístico**: 1 linha por instância (sem sementes).

Registro de cada linha (`omaNN_<solver>.jsonl`):
```json
{"instance":"oma01","method":"highs","config_id":"tl-600","status":"Feasible",
 "params":{"time_limit_s":600},"final_solution":266.0,"time_ms":3322.6}
```

### Status confiável (fix importante)
O PuLP rotula um stop por time-limit como `LpStatus = "Optimal"` (status do problema),
o que é enganoso. Passamos a derivar o status de **`prob.sol_status`** (status da
**solução**), mapeado em `SOLVER_STATUS` (`src/oma/main.py`):

| Significado | `sol_status` | `status` gravado |
|---|---|---|
| Ótimo provado | `LpSolutionOptimal` | `Optimal` |
| Viável, não provado (ex.: time-limit) | `LpSolutionIntegerFeasible` | `Feasible` |
| Inviável / ilimitado / sem solução | demais | `Infeasible` / `Unbounded` / `No Solution` |

> Nota prática: nas instâncias do trabalho o **HiGHS é fraco** — em oma01 com 600s nem
> ramifica (`Nodes 0`), gap ~892% (bound 3353 vs incumbente 338), abaixo da tabu (472).
> Portanto espere `status=Feasible` na maioria dos runs HiGHS; o **CPLEX** deve fechar
> mais instâncias como `Optimal`.

## 2. Taxonomia de `results/` (method-first)

```
results/
  metaheuristica/
    tabu/
      M1/<config_id>/omaNN_tabu.jsonl + config.json     # A1_*, A5_*
      M2/<config_id>/...                                 # A3_*, B_*
      M3/<config_id>/...                                 # A2_*, A4_*
  solver/
    highs/ M1/tl-600/oma01..04_highs.jsonl   M2/tl-600/oma05..07   M3/tl-600/oma08..10   (+ config.json)
    cplex/ M1/tl-600/oma01..04_cplex.jsonl   M2/tl-600/oma05..07   M3/tl-600/oma08..10   (+ config.json)
```

O solver é **dividido por intervalo de instâncias** entre as 3 máquinas (ver §3), então cada
pasta de máquina tem só a sua fatia; juntas, as 3 cobrem as 10 instâncias por solver.

Justificativa de cada nível: **family** (`solver`/`metaheuristica` = seções do relatório)
→ **method** (extensível: `grasp`, `gurobi`…) → **machine** (fronteira de merge entre os
3 PCs + proveniência de tempo) → **config** (unidade experimental) → arquivo por instância.
Solver e tabu nunca compartilham diretório, então não há colisão de `config.json`.

A árvore é consumida pelo agregador (ver `aggregator_plan.md`) via glob `results/**/*.jsonl`
+ registros auto-descritivos; `family`/`solver`/`maquina` saem do caminho.

## 3. Como rodar

Cada máquina tem **um** script com a sua fatia de heurística **e** a sua fatia de solver:

| Máquina | Script | Heurística | Fatia do solver |
|---|---|---|---|
| M1 (Linux) | `bash docs/run_M1.sh` | A1 (tenure) + A5 (init) | oma01-04 (HiGHS+CPLEX) |
| M2 (Linux) | `bash docs/run_M2.sh` | A3 (max_iter) + B | oma05-07 (HiGHS+CPLEX) |
| M3 (Windows) | `pwsh docs/run_M3.ps1` | A2 + A4 | oma08-10 (HiGHS+CPLEX) |

A divisão do solver é **por intervalo de instâncias** (`SOLVER_INSTANCES` em cada script,
editável). HiGHS e CPLEX rodam na **mesma máquina por instância**, então a comparação
solver-vs-solver por instância é justa; só o tempo **entre instâncias** (em máquinas
diferentes) não é diretamente comparável. Dentro de cada script tudo roda em sequência
(heurística depois solver), sem concorrência de CPU — não rode dois scripts ao mesmo tempo
na mesma máquina.

## 4. O solver roda UMA vez por instância (não por seed/caso aleatório)

A aleatoriedade da metaheurística (sementes 0-4, `--init random` do bloco A5) está **no
algoritmo**, não na instância: as 10 instâncias (`oma01..oma10`) são fixas, lidas do
`dataset/`. O solver exato é **determinístico** e resolve cada instância **uma única vez**,
produzindo o valor de referência (ótimo ou melhor limite) daquela instância. Esse único
valor por instância é a base de comparação para **todas** as execuções da heurística —
todas as sementes e todas as configs, inclusive as de init aleatório. Portanto **não** se
multiplica o solver por seed nem por caso aleatório; a fatia por máquina já cobre cada
instância uma vez por solver. (Onde o solver não prova o ótimo em 600s, a referência do
relatório é a BKV de `bkv.md`, não o incumbente do solver.)

## 5. Arquivos alterados

- `src/oma/logger.py` — `append_solver_run` (espelha `append_meta_run`); removido `write_run`.
- `src/oma/main.py` — `--time-limit`; status via `prob.sol_status` + `SOLVER_STATUS`;
  `run_one` roteado por `--config-id`/`--out-dir`; `config.json` na fase do solver.
- `docs/run_M1.sh`, `run_M2.sh` (bash) — `OUT=results/metaheuristica/tabu/M<n>` + fatia do
  solver (oma01-04 / oma05-07).
- `docs/run_M3.ps1` (PowerShell, novo; substitui `run_M3.sh`) — A2+A4 + fatia oma08-10.
- `docs/run_solver.sh` — removido (solver agora dividido nos scripts de máquina).
- `docs/aggregator_plan.md` — atualizado para a taxonomia method-first.
