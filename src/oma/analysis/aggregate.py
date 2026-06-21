"""Agrega os registros em estatísticas, tabelas e no JSON agregado do relatório."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean, pstdev

from oma.analysis.load import Record, meta_records, solver_records


def _stats(values: list[float]) -> tuple[float, float]:
    """(média, desvio-padrão populacional); (0,0) se vazio."""
    if not values:
        return 0.0, 0.0
    return mean(values), (pstdev(values) if len(values) > 1 else 0.0)


# --------------------------------------------------------------------------- #
# Agregação da metaheurística por (config_id, instância) sobre as sementes.
# --------------------------------------------------------------------------- #
def aggregate_meta(records: list[Record]) -> dict[tuple[str, str], dict]:
    groups: dict[tuple[str, str], list[Record]] = defaultdict(list)
    for r in meta_records(records):
        groups[(r.config_id, r.instance)].append(r)

    out: dict[tuple[str, str], dict] = {}
    for (config_id, instance), recs in groups.items():
        sf = [r.final_solution for r in recs]
        si = [r.initial_solution for r in recs if r.initial_solution is not None]
        times = [r.time_ms for r in recs]
        sf_mean, sf_std = _stats(sf)
        si_mean, _ = _stats(si)
        time_mean, _ = _stats(times)
        best = max(recs, key=lambda r: r.final_solution)
        out[(config_id, instance)] = {
            "config_id": config_id,
            "instance": instance,
            "replications": len(recs),
            "si_mean": si_mean,
            "sf_mean": sf_mean,
            "sf_std": sf_std,
            "sf_best": best.final_solution,
            "best_seed": best.seed,
            "time_ms_mean": time_mean,
            "bkv": recs[0].bkv,
            "dev_initial_pct_mean": _stats(
                [r.dev_initial_pct for r in recs if r.dev_initial_pct is not None]
            )[0],
            "dev_bkv_pct_mean": _stats([r.dev_bkv_pct for r in recs])[0],
            "otimalidade_pct_mean": _stats([r.otimalidade_pct for r in recs])[0],
        }
    return out


# --------------------------------------------------------------------------- #
# Séries de sensibilidade: por bloco, agrega todas as instâncias×sementes de
# cada config (= cada valor do parâmetro variado).
# --------------------------------------------------------------------------- #
def sensitivity_series(records: list[Record], block: str) -> list[dict]:
    recs = [r for r in meta_records(records) if r.block == block]
    by_value: dict[object, list[Record]] = defaultdict(list)
    for r in recs:
        by_value[r.varied_value].append(r)

    series = []
    for value, group in by_value.items():
        otim_mean, otim_std = _stats([r.otimalidade_pct for r in group])
        time_mean, _ = _stats([r.time_ms for r in group])
        series.append({
            "value": value,
            "otimalidade_pct_mean": otim_mean,
            "otimalidade_pct_std": otim_std,
            "time_ms_mean": time_mean,
            "n": len(group),
        })

    # Ordena numericamente quando possível (A1-A4); categórico em A5.
    def sort_key(d):
        v = d["value"]
        return (0, v) if isinstance(v, (int, float)) else (1, str(v))

    return sorted(series, key=sort_key)


# --------------------------------------------------------------------------- #
# Solver: 1 registro por (solver, instância). Une as máquinas automaticamente
# (cada máquina cobre uma fatia de instâncias).
# --------------------------------------------------------------------------- #
def aggregate_solver(records: list[Record]) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    for r in solver_records(records):
        out[(r.key, r.instance)] = {
            "solver": r.key,
            "instance": r.instance,
            "bkv": r.bkv,
            "final_solution": r.final_solution,
            "status": r.status,
            "time_ms": r.time_ms,
            "dev_bkv_pct": r.dev_bkv_pct,
        }
    return out


# --------------------------------------------------------------------------- #
# JSON agregado (schema do test_plan.md §7).
# --------------------------------------------------------------------------- #
def aggregated_json(meta_agg: dict[tuple[str, str], dict]) -> list[dict]:
    rows = []
    for v in meta_agg.values():
        rows.append({
            "instance": v["instance"],
            "config": v["config_id"],
            "replications": v["replications"],
            "final_solution_mean": round(v["sf_mean"], 3),
            "final_solution_std": round(v["sf_std"], 3),
            "dev_bkv_pct_mean": round(v["dev_bkv_pct_mean"], 3),
            "time_ms_mean": round(v["time_ms_mean"], 3),
        })
    return sorted(rows, key=lambda r: (r["config"], r["instance"]))


# --------------------------------------------------------------------------- #
# Tabelas do relatório.
# --------------------------------------------------------------------------- #
def table_config(meta_agg, solver_agg, config_id: str, solver: str | None) -> list[dict]:
    """T1: uma linha por instância para a config B dada (referência Tabelas 2-4)."""
    rows = []
    for instance in sorted({inst for (cfg, inst) in meta_agg if cfg == config_id}):
        m = meta_agg[(config_id, instance)]
        s = solver_agg.get((solver, instance)) if solver else None
        rows.append({
            "instance": instance,
            "SI": round(m["si_mean"], 1),
            "SF": round(m["sf_mean"], 1),
            "dev_SI_pct": round(m["dev_initial_pct_mean"], 2),
            "dev_BKV_pct": round(m["dev_bkv_pct_mean"], 2),
            "time_MH_ms": round(m["time_ms_mean"], 1),
            "time_solver_ms": round(s["time_ms"], 1) if s else None,
            "seed": m["best_seed"],
        })
    return rows


def table_solver(solver_agg, solver: str) -> list[dict]:
    """T2: referência Tabela 5, para um solver."""
    rows = []
    for (slv, instance), v in sorted(solver_agg.items()):
        if slv != solver:
            continue
        rows.append({
            "instance": instance,
            "BKV": v["bkv"],
            "obtido": v["final_solution"],
            "dev_BKV_pct": round(v["dev_bkv_pct"], 2),
            "status": v["status"],
            "time_ms": round(v["time_ms"], 1),
        })
    return rows


# --------------------------------------------------------------------------- #
# Render CSV / Markdown (sem dependências externas).
# --------------------------------------------------------------------------- #
def to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [",".join(headers)]
    for r in rows:
        lines.append(",".join("" if r[h] is None else str(r[h]) for h in headers))
    return "\n".join(lines) + "\n"


def to_markdown(rows: list[dict]) -> str:
    if not rows:
        return "_(sem dados)_\n"
    headers = list(rows[0].keys())
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join("" if r[h] is None else str(r[h]) for h in headers) + " |")
    return "\n".join(out) + "\n"
