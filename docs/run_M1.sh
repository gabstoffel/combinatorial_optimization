#!/usr/bin/env bash
# M1 — Gabriel (PC-A): bloco A1 (tenure, 9) + A5 (solução inicial, 2) = 11 configs.
# Cada config roda as 10 instâncias × 5 sementes. Saída em results/M1/<config_id>/.
# Baseline (demais parâmetros): tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50.
set -u
OUT=results/M1

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
