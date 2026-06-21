#!/usr/bin/env bash
# RUN_ALL — script único (uma máquina): roda TUDO que M1+M2+M3 fazem juntos.
# HEURÍSTICA (tabu, com seeds) em todos os blocos de varredura sobre as 10 instâncias,
# mais os SOLVERS exatos (HiGHS + CPLEX) nas 10 instâncias.
#
# Para reproduzir EXATAMENTE a árvore de resultados existente (e não duplicar dados na
# análise, que colapsa a dimensão "machine"), cada bloco escreve na MESMA pasta M1/M2/M3
# usada pelos scripts originais. Rerodar acrescenta linhas (append) e o loader deduplica
# por (family, key, machine, config_id, instance, seed), mantendo a última de cada.
#
# Baseline (demais parâmetros): tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50.
# Cada config tabu roda as 10 instâncias × 5 sementes (--seeds padrão).
set -u
OUT1=results/metaheuristica/tabu/M1   # blocos A1, A5
OUT2=results/metaheuristica/tabu/M2   # blocos A3, B
OUT3=results/metaheuristica/tabu/M3   # blocos A2, A4
SOLVER_TL=600

# =====================================================================
# HEURÍSTICA (tabu) — varreduras de parâmetro
# =====================================================================

# --- A1: varredura de tenure (demais na baseline) ---
uv run oma all --tabu --tenure 1  --config-id A1_tenure-01 --out-dir "$OUT1"
uv run oma all --tabu --tenure 3  --config-id A1_tenure-03 --out-dir "$OUT1"
uv run oma all --tabu --tenure 5  --config-id A1_tenure-05 --out-dir "$OUT1"
uv run oma all --tabu --tenure 7  --config-id A1_tenure-07 --out-dir "$OUT1"
uv run oma all --tabu --tenure 10 --config-id A1_tenure-10 --out-dir "$OUT1"
uv run oma all --tabu --tenure 15 --config-id A1_tenure-15 --out-dir "$OUT1"
uv run oma all --tabu --tenure 20 --config-id A1_tenure-20 --out-dir "$OUT1"
uv run oma all --tabu --tenure 30 --config-id A1_tenure-30 --out-dir "$OUT1"
uv run oma all --tabu --tenure 50 --config-id A1_tenure-50 --out-dir "$OUT1"

# --- A2: varredura de max_no_improve (demais na baseline) ---
uv run oma all --tabu --max-no-improve 25  --config-id A2_maxni-025 --out-dir "$OUT3"
uv run oma all --tabu --max-no-improve 50  --config-id A2_maxni-050 --out-dir "$OUT3"
uv run oma all --tabu --max-no-improve 100 --config-id A2_maxni-100 --out-dir "$OUT3"
uv run oma all --tabu --max-no-improve 200 --config-id A2_maxni-200 --out-dir "$OUT3"
uv run oma all --tabu --max-no-improve 400 --config-id A2_maxni-400 --out-dir "$OUT3"
uv run oma all --tabu --max-no-improve 800 --config-id A2_maxni-800 --out-dir "$OUT3"

# --- A3: varredura de max_iter (demais na baseline) ---
uv run oma all --tabu --max-iter 250  --config-id A3_maxiter-0250 --out-dir "$OUT2"
uv run oma all --tabu --max-iter 500  --config-id A3_maxiter-0500 --out-dir "$OUT2"
uv run oma all --tabu --max-iter 1000 --config-id A3_maxiter-1000 --out-dir "$OUT2"
uv run oma all --tabu --max-iter 2000 --config-id A3_maxiter-2000 --out-dir "$OUT2"
uv run oma all --tabu --max-iter 5000 --config-id A3_maxiter-5000 --out-dir "$OUT2"

# --- A4: varredura de diversify_freq (0 = sem diversificação periódica) ---
uv run oma all --tabu --diversify-freq 0   --config-id A4_divfreq-000 --out-dir "$OUT3"
uv run oma all --tabu --diversify-freq 10  --config-id A4_divfreq-010 --out-dir "$OUT3"
uv run oma all --tabu --diversify-freq 25  --config-id A4_divfreq-025 --out-dir "$OUT3"
uv run oma all --tabu --diversify-freq 50  --config-id A4_divfreq-050 --out-dir "$OUT3"
uv run oma all --tabu --diversify-freq 100 --config-id A4_divfreq-100 --out-dir "$OUT3"
uv run oma all --tabu --diversify-freq 200 --config-id A4_divfreq-200 --out-dir "$OUT3"

# --- A5: solução inicial (baseline em tudo, varia a construção) ---
uv run oma all --tabu --init greedy --config-id A5_init-greedy --out-dir "$OUT1"
uv run oma all --tabu --init random --config-id A5_init-random --out-dir "$OUT1"

# =====================================================================
# HEURÍSTICA (tabu) — configurações completas (bloco B)
# =====================================================================

# B_baseline: ponto de referência (todos os parâmetros na baseline).
uv run oma all --tabu --config-id B_baseline --out-dir "$OUT2"

# B_tuned: MELHOR combinação encontrada nas varreduras A1–A4. (Placeholder: ajustar!)
uv run oma all --tabu --tenure 10 --max-no-improve 400 --max-iter 2000 --diversify-freq 50 \
  --config-id B_tuned --out-dir "$OUT2"

# B_degenerate: configuração propositalmente fraca (contraste no relatório).
uv run oma all --tabu --tenure 1 --max-no-improve 25 --max-iter 250 --diversify-freq 0 \
  --config-id B_degenerate --out-dir "$OUT2"

# =====================================================================
# SOLVERS exatos (HiGHS + CPLEX) — 10 instâncias
# =====================================================================
# Mantém a fatia original por máquina nas pastas M1/M2/M3 (1 linha por instância, append).
for i in 1 2 3 4; do
  uv run oma "$i" --highs --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/highs/M1
  uv run oma "$i" --cplex --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/cplex/M1
done
for i in 5 6 7; do
  uv run oma "$i" --highs --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/highs/M2
  uv run oma "$i" --cplex --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/cplex/M2
done
for i in 8 9 10; do
  uv run oma "$i" --highs --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/highs/M3
  uv run oma "$i" --cplex --time-limit "$SOLVER_TL" --config-id "tl-$SOLVER_TL" --out-dir results/solver/cplex/M3
done
