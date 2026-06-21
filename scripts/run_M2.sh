#!/usr/bin/env bash
# M2 — Gabriel (PC-B, Linux): HEURÍSTICA bloco A3 (max_iter, 5) + B (config completa, 3),
# mais a fatia oma05-07 do SOLVER exato (HiGHS + CPLEX).
# Bloco tabu mais pesado (max_iter até 5000). Saída em results/metaheuristica/tabu/M2/<config_id>/.
# Baseline (demais parâmetros): tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50.
set -u
OUT=results/metaheuristica/tabu/M2
SOLVER_TL=600
SOLVER_INSTANCES="5 6 7"   # fatia desta máquina (editável para balancear carga)

# --- A3: varredura de max_iter (demais na baseline) ---
uv run oma all --tabu --max-iter 250  --config-id A3_maxiter-0250 --out-dir "$OUT"
uv run oma all --tabu --max-iter 500  --config-id A3_maxiter-0500 --out-dir "$OUT"
uv run oma all --tabu --max-iter 1000 --config-id A3_maxiter-1000 --out-dir "$OUT"
uv run oma all --tabu --max-iter 2000 --config-id A3_maxiter-2000 --out-dir "$OUT"
uv run oma all --tabu --max-iter 5000 --config-id A3_maxiter-5000 --out-dir "$OUT"

# --- B: configurações completas para a tabela final ---
# B_baseline: ponto de referência (todos os parâmetros na baseline).
uv run oma all --tabu --config-id B_baseline --out-dir "$OUT"

# B_tuned: MELHOR combinação encontrada nas varreduras A1–A4. Rodar POR ÚLTIMO,
# depois de analisar M1/M2/M3 e preencher os valores abaixo. (Placeholder: ajustar!)
uv run oma all --tabu --tenure 10 --max-no-improve 400 --max-iter 2000 --diversify-freq 50 \
  --config-id B_tuned --out-dir "$OUT"

# B_degenerate: configuração propositalmente fraca (contraste no relatório):
# tenure mínimo, pouca paciência, poucas iterações, sem diversificação.
uv run oma all --tabu --tenure 1 --max-no-improve 25 --max-iter 250 --diversify-freq 0 \
  --config-id B_degenerate --out-dir "$OUT"

# --- Solver exato: fatia oma05-07 (HiGHS + CPLEX) ---
# Saída: results/solver/<solver>/M2/tl-600/. Determinístico: 1 linha por instância.
for i in $SOLVER_INSTANCES; do
  uv run oma "$i" --highs --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/highs/M2
  uv run oma "$i" --cplex --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/cplex/M2
done
