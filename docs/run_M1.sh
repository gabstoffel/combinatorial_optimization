#!/usr/bin/env bash
# M1 — Gabriel (PC-A, Linux): HEURÍSTICA bloco A1 (tenure, 9) + A5 (init, 2) = 11 configs,
# mais a fatia oma01-04 do SOLVER exato (HiGHS + CPLEX).
# Cada config tabu roda as 10 instâncias × 5 sementes. Saída em results/metaheuristica/tabu/M1/<config_id>/.
# Baseline (demais parâmetros): tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50.
set -u
OUT=results/metaheuristica/tabu/M1
SOLVER_TL=600
SOLVER_INSTANCES="1 2 3 4"   # fatia desta máquina (editável para balancear carga)

# --- A1: varredura de tenure (demais na baseline) ---
uv run oma all --tabu --tenure 1  --config-id A1_tenure-01 --out-dir "$OUT"
uv run oma all --tabu --tenure 3  --config-id A1_tenure-03 --out-dir "$OUT"
uv run oma all --tabu --tenure 5  --config-id A1_tenure-05 --out-dir "$OUT"
uv run oma all --tabu --tenure 7  --config-id A1_tenure-07 --out-dir "$OUT"
uv run oma all --tabu --tenure 10 --config-id A1_tenure-10 --out-dir "$OUT"
uv run oma all --tabu --tenure 15 --config-id A1_tenure-15 --out-dir "$OUT"
uv run oma all --tabu --tenure 20 --config-id A1_tenure-20 --out-dir "$OUT"
uv run oma all --tabu --tenure 30 --config-id A1_tenure-30 --out-dir "$OUT"
uv run oma all --tabu --tenure 50 --config-id A1_tenure-50 --out-dir "$OUT"

# --- A5: solução inicial (baseline em tudo, varia a construção) ---
uv run oma all --tabu --init greedy --config-id A5_init-greedy --out-dir "$OUT"
uv run oma all --tabu --init random --config-id A5_init-random --out-dir "$OUT"

# --- Solver exato: fatia oma01-04 (HiGHS + CPLEX) ---
# HiGHS e CPLEX rodam na MESMA máquina por instância → comparação solver-vs-solver
# por instância é justa. Determinístico: 1 linha por instância (campo `status`).
# Saída: results/solver/<solver>/M1/tl-600/. Rerodar acrescenta linhas (append).
for i in $SOLVER_INSTANCES; do
  uv run oma "$i" --highs --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/highs/M1
  uv run oma "$i" --cplex --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/cplex/M1
done
