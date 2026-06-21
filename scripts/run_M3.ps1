# M3 — Rodrigo (Windows/PowerShell): HEURÍSTICA bloco A2 (max_no_improve, 6) + A4 (diversify_freq, 6)
# = 12 configs, mais a fatia oma08-10 do SOLVER exato (HiGHS + CPLEX).
# Cada config tabu roda as 10 instâncias × 5 sementes. Saída em results/metaheuristica/tabu/M3/<config_id>/.
# Baseline (demais parâmetros): tenure=10, max_no_improve=100, max_iter=1000, diversify_freq=50.
# OBS: se o CPLEX no Windows estiver em outro caminho, ajuste CPLEX_BINARY_PATH em src/oma/solvers/generic.py.
$ErrorActionPreference = "Stop"
$OUT = "results/metaheuristica/tabu/M3"
$SOLVER_TL = 600
$SOLVER_INSTANCES = 8, 9, 10   # fatia desta máquina (editável para balancear carga)

# --- A2: varredura de max_no_improve (demais na baseline) ---
uv run oma all --tabu --max-no-improve 25  --config-id A2_maxni-025 --out-dir $OUT
uv run oma all --tabu --max-no-improve 50  --config-id A2_maxni-050 --out-dir $OUT
uv run oma all --tabu --max-no-improve 100 --config-id A2_maxni-100 --out-dir $OUT
uv run oma all --tabu --max-no-improve 200 --config-id A2_maxni-200 --out-dir $OUT
uv run oma all --tabu --max-no-improve 400 --config-id A2_maxni-400 --out-dir $OUT
uv run oma all --tabu --max-no-improve 800 --config-id A2_maxni-800 --out-dir $OUT

# --- A4: varredura de diversify_freq (0 = sem diversificação periódica) ---
uv run oma all --tabu --diversify-freq 0   --config-id A4_divfreq-000 --out-dir $OUT
uv run oma all --tabu --diversify-freq 10  --config-id A4_divfreq-010 --out-dir $OUT
uv run oma all --tabu --diversify-freq 25  --config-id A4_divfreq-025 --out-dir $OUT
uv run oma all --tabu --diversify-freq 50  --config-id A4_divfreq-050 --out-dir $OUT
uv run oma all --tabu --diversify-freq 100 --config-id A4_divfreq-100 --out-dir $OUT
uv run oma all --tabu --diversify-freq 200 --config-id A4_divfreq-200 --out-dir $OUT

# --- Solver exato: fatia oma08-10 (HiGHS + CPLEX) ---
# HiGHS e CPLEX rodam na MESMA máquina por instância → comparação solver-vs-solver
# por instância é justa. Determinístico: 1 linha por instância (campo `status`).
# Saída: results/solver/<solver>/M3/tl-600/. Rerodar acrescenta linhas (append).
foreach ($i in $SOLVER_INSTANCES) {
  uv run oma $i --highs --time-limit $SOLVER_TL --config-id "tl-$SOLVER_TL" --out-dir "results/solver/highs/M3"
  uv run oma $i --cplex --time-limit $SOLVER_TL --config-id "tl-$SOLVER_TL" --out-dir "results/solver/cplex/M3"
}
