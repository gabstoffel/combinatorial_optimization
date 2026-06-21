"""CLI `oma-report`: lê a árvore `results/`, agrega e gera tabelas + figuras.

Uso:
    uv run oma-report --results-dir results --out-dir report
    uv run oma-report --configs baseline=B_baseline,tuned=B_tuned,degenerate=B_degenerate
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from oma.analysis import aggregate as agg
from oma.analysis.load import load_records, solvers_present

# Blocos de sensibilidade (G1-G4) -> parâmetro variado.
SENS_BLOCKS = [
    ("A1", "tenure"),
    ("A2", "max_no_improve"),
    ("A3", "max_iter"),
    ("A4", "diversify_freq"),
]
DEFAULT_CONFIGS = {"baseline": "B_baseline", "tuned": "B_tuned", "degenerate": "B_degenerate"}


def _warn(msg: str) -> None:
    print(f"[oma-report] aviso: {msg}", file=sys.stderr)


def _parse_configs(spec: str | None) -> dict:
    if not spec:
        return dict(DEFAULT_CONFIGS)
    out = {}
    for pair in spec.split(","):
        label, _, cfg = pair.partition("=")
        if label and cfg:
            out[label.strip()] = cfg.strip()
    return out


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="oma-report", description="Agrega resultados OMA e gera figuras.")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--out-dir", default="report")
    p.add_argument("--configs", default=None,
                   help="rótulo=config_id separados por vírgula (default: B_baseline/B_tuned/B_degenerate)")
    p.add_argument("--solver-for-table", default=None,
                   help="solver cuja coluna de tempo entra na T1 (default: cplex se houver)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv if argv is not None else sys.argv[1:])

    records = load_records(args.results_dir)
    if not records:
        _warn(f"nenhum .jsonl encontrado em {args.results_dir!r}")
        return
    print(f"[oma-report] {len(records)} registros carregados de {args.results_dir}")

    meta_agg = agg.aggregate_meta(records)
    solver_agg = agg.aggregate_solver(records)
    solvers = solvers_present(records)
    configs = _parse_configs(args.configs)

    fig_dir = os.path.join(args.out_dir, "figures")
    tbl_dir = os.path.join(args.out_dir, "tables")
    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(tbl_dir, exist_ok=True)

    # --- JSON agregado (test_plan §7) ---
    _write(os.path.join(args.out_dir, "aggregated.json"),
           json.dumps(agg.aggregated_json(meta_agg), indent=2) + "\n")

    # --- Tabelas ---
    solver_for_table = args.solver_for_table or ("cplex" if "cplex" in solvers
                                                 else solvers[0] if solvers else None)
    for label, cfg in configs.items():
        if not any(c == cfg for (c, _i) in meta_agg):
            _warn(f"config {cfg!r} ({label}) ausente — tabela T1 pulada.")
            continue
        rows = agg.table_config(meta_agg, solver_agg, cfg, solver_for_table)
        _write(os.path.join(tbl_dir, f"T1_{label}.csv"), agg.to_csv(rows))
        _write(os.path.join(tbl_dir, f"T1_{label}.md"), agg.to_markdown(rows))
    for slv in solvers:
        rows = agg.table_solver(solver_agg, slv)
        _write(os.path.join(tbl_dir, f"T2_{slv}.csv"), agg.to_csv(rows))
        _write(os.path.join(tbl_dir, f"T2_{slv}.md"), agg.to_markdown(rows))

    # --- Figuras (matplotlib importado tarde p/ não exigir a dep nas tabelas) ---
    from oma.analysis import plots

    for block, param in SENS_BLOCKS:
        series = agg.sensitivity_series(records, block)
        if not series:
            _warn(f"bloco {block} ausente — figura de sensibilidade pulada.")
            continue
        plots.sensitivity_plot(series, block, param, os.path.join(fig_dir, f"{block}_{param}.png"))

    plots.init_comparison_plot(meta_agg, os.path.join(fig_dir, "A5_init.png"))
    plots.instance_quality_plot(meta_agg, solver_agg, configs, solvers,
                                os.path.join(fig_dir, "B_instances_quality.png"))
    plots.instance_time_plot(meta_agg, solver_agg, configs, solvers,
                             os.path.join(fig_dir, "B_instances_time.png"))

    print(f"[oma-report] tabelas em {tbl_dir}/ e figuras em {fig_dir}/ ; aggregated.json em {args.out_dir}/")


if __name__ == "__main__":
    main()
