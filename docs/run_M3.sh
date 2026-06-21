#!/usr/bin/env bash
# M3 — Rodrigo: bloco A2 (max_no_improve, 6) + A4 (diversify_freq, 6) = 12 configs.
# Cada config roda as 10 instâncias × 5 sementes. Saída em results/M3/<config_id>/.
# Baseline (demais parâmetros): tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50.
set -u
OUT=results/M3

# --- A2: varredura de max_no_improve (demais na baseline) ---
uv run oma all --tabu --max-no-improve 25  --config-id A2_maxni-025 --out-dir "$OUT"
uv run oma all --tabu --max-no-improve 50  --config-id A2_maxni-050 --out-dir "$OUT"
uv run oma all --tabu --max-no-improve 100 --config-id A2_maxni-100 --out-dir "$OUT"
uv run oma all --tabu --max-no-improve 200 --config-id A2_maxni-200 --out-dir "$OUT"
uv run oma all --tabu --max-no-improve 400 --config-id A2_maxni-400 --out-dir "$OUT"
uv run oma all --tabu --max-no-improve 800 --config-id A2_maxni-800 --out-dir "$OUT"

# --- A4: varredura de diversify_freq (0 = sem diversificação periódica) ---
uv run oma all --tabu --diversify-freq 0   --config-id A4_divfreq-000 --out-dir "$OUT"
uv run oma all --tabu --diversify-freq 10  --config-id A4_divfreq-010 --out-dir "$OUT"
uv run oma all --tabu --diversify-freq 25  --config-id A4_divfreq-025 --out-dir "$OUT"
uv run oma all --tabu --diversify-freq 50  --config-id A4_divfreq-050 --out-dir "$OUT"
uv run oma all --tabu --diversify-freq 100 --config-id A4_divfreq-100 --out-dir "$OUT"
uv run oma all --tabu --diversify-freq 200 --config-id A4_divfreq-200 --out-dir "$OUT"
