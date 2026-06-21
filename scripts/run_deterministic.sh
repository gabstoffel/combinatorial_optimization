#!/usr/bin/env bash
# DETERMINÍSTICO — script único: HEURÍSTICA (tabu) em modo determinístico sobre TODAS
# as 10 instâncias, varrendo os mesmos parâmetros dos scripts M1/M2/M3, porém SEM seed
# e SEM qualquer geração aleatória (greedy parte da pessoa 0, perturbação determinística,
# 1 execução por instância). Saída em results/metaheuristica/deterministic/all/<config_id>/.
#
# Blocos: A1 (tenure), A2 (max_no_improve), A3 (max_iter) e B (configs completas).
# Excluídos de propósito: A4 (diversify_freq) e A5 (init) — dependem de aleatoriedade —
# e as fatias dos solvers exatos (HiGHS/CPLEX).
#
# Os config-id são idênticos aos da versão com seed (tabu/M*), para comparação direta.
# Baseline (demais parâmetros): tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50.
set -u
OUT=results/metaheuristica/deterministic/all

# --- A1: varredura de tenure (demais na baseline) ---
uv run oma all --tabu --deterministic --tenure 1  --config-id A1_tenure-01 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 3  --config-id A1_tenure-03 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 5  --config-id A1_tenure-05 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 7  --config-id A1_tenure-07 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 10 --config-id A1_tenure-10 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 15 --config-id A1_tenure-15 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 20 --config-id A1_tenure-20 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 30 --config-id A1_tenure-30 --out-dir "$OUT"
uv run oma all --tabu --deterministic --tenure 50 --config-id A1_tenure-50 --out-dir "$OUT"

# --- A2: varredura de max_no_improve (demais na baseline) ---
uv run oma all --tabu --deterministic --max-no-improve 25  --config-id A2_maxni-025 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-no-improve 50  --config-id A2_maxni-050 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-no-improve 100 --config-id A2_maxni-100 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-no-improve 200 --config-id A2_maxni-200 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-no-improve 400 --config-id A2_maxni-400 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-no-improve 800 --config-id A2_maxni-800 --out-dir "$OUT"

# --- A3: varredura de max_iter (demais na baseline) ---
uv run oma all --tabu --deterministic --max-iter 250  --config-id A3_maxiter-0250 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-iter 500  --config-id A3_maxiter-0500 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-iter 1000 --config-id A3_maxiter-1000 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-iter 2000 --config-id A3_maxiter-2000 --out-dir "$OUT"
uv run oma all --tabu --deterministic --max-iter 5000 --config-id A3_maxiter-5000 --out-dir "$OUT"

# --- B: configurações completas para a tabela final ---
# B_baseline: ponto de referência (todos os parâmetros na baseline).
uv run oma all --tabu --deterministic --config-id B_baseline --out-dir "$OUT"

# B_tuned: MELHOR combinação encontrada nas varreduras A1–A4 (mesmos valores do run_M2.sh).
uv run oma all --tabu --deterministic --tenure 10 --max-no-improve 400 --max-iter 2000 --diversify-freq 50 \
  --config-id B_tuned --out-dir "$OUT"

# B_degenerate: configuração propositalmente fraca (contraste no relatório).
uv run oma all --tabu --deterministic --tenure 1 --max-no-improve 25 --max-iter 250 --diversify-freq 0 \
  --config-id B_degenerate --out-dir "$OUT"
