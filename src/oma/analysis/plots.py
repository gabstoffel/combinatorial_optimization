"""Figuras do relatório (matplotlib, backend headless 'Agg').

Mapeadas ao reference_report.md §7-8 / test_plan.md §4-5:
- G1-G4: sensibilidade por parâmetro (otimalidade % + tempo, eixo duplo).
- G5: comparação da construção inicial (greedy vs random).
- G6/G7: comparação por instância (configs B + solvers) em qualidade e tempo.
"""

from __future__ import annotations

from collections import defaultdict
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def sensitivity_plot(series: list[dict], block: str, param: str, out_path: str) -> None:
    """G1-G4: eixo X = valor do parâmetro; Y1 = otimalidade % (±desvio); Y2 = tempo."""
    xs = [str(d["value"]) for d in series]
    pos = range(len(xs))
    otim = [d["otimalidade_pct_mean"] for d in series]
    err = [d["otimalidade_pct_std"] for d in series]
    times = [d["time_ms_mean"] for d in series]

    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.errorbar(pos, otim, yerr=err, marker="o", color="tab:blue", capsize=3,
                 label="otimalidade (%)")
    ax1.set_xlabel(param)
    ax1.set_ylabel("otimalidade média (% do BKV)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.set_xticks(list(pos))
    ax1.set_xticklabels(xs)

    ax2 = ax1.twinx()
    ax2.plot(pos, times, marker="s", color="tab:red", label="tempo (ms)")
    ax2.set_ylabel("tempo médio (ms)", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    ax1.set_title(f"{block}: sensibilidade a {param}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def init_comparison_plot(meta_agg: dict, out_path: str) -> None:
    """G5: SI e SF médios (sobre instâncias) para greedy vs random."""
    labels, si_vals, sf_vals = [], [], []
    for cfg, name in (("A5_init-greedy", "greedy"), ("A5_init-random", "random")):
        rows = [v for (c, _i), v in meta_agg.items() if c == cfg]
        if not rows:
            continue
        labels.append(name)
        si_vals.append(mean(r["si_mean"] for r in rows))
        sf_vals.append(mean(r["sf_mean"] for r in rows))
    if not labels:
        return

    pos = range(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.bar([p - width / 2 for p in pos], si_vals, width, label="SI (inicial)", color="tab:gray")
    ax.bar([p + width / 2 for p in pos], sf_vals, width, label="SF (final)", color="tab:green")
    ax.set_xticks(list(pos))
    ax.set_xticklabels(labels)
    ax.set_ylabel("objetivo médio")
    ax.set_title("A5: construção inicial (greedy vs random)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _instances(meta_agg, solver_agg) -> list[str]:
    names = {i for (_c, i) in meta_agg} | {i for (_s, i) in solver_agg}
    return sorted(names)


def instance_quality_plot(meta_agg, solver_agg, configs: dict, solvers: list[str],
                          out_path: str) -> None:
    """G6: otimalidade % por instância, barras agrupadas (configs B + solvers)."""
    instances = _instances(meta_agg, solver_agg)
    if not instances:
        return
    pos = range(len(instances))

    # série -> valores por instância (otimalidade %)
    series: list[tuple[str, list[float]]] = []
    for label, cfg in configs.items():
        vals = [meta_agg[(cfg, i)]["otimalidade_pct_mean"] if (cfg, i) in meta_agg else 0.0
                for i in instances]
        if any(vals):
            series.append((label, vals))
    for slv in solvers:
        vals = [100.0 * solver_agg[(slv, i)]["final_solution"] / solver_agg[(slv, i)]["bkv"]
                if (slv, i) in solver_agg else 0.0 for i in instances]
        if any(vals):
            series.append((slv, vals))
    if not series:
        return

    n = len(series)
    width = 0.8 / n
    fig, ax = plt.subplots(figsize=(11, 5))
    for k, (label, vals) in enumerate(series):
        offset = (k - (n - 1) / 2) * width
        ax.bar([p + offset for p in pos], vals, width, label=label)
    ax.axhline(100.0, color="black", linewidth=0.8, linestyle="--", label="BKV (100%)")
    ax.set_xticks(list(pos))
    ax.set_xticklabels(instances, rotation=45, ha="right")
    ax.set_ylabel("otimalidade (% do BKV)")
    ax.set_ylim(min(80, *(min(v) for _l, v in series)) - 2, 102)
    ax.set_title("Comparação por instância — qualidade")
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def instance_time_plot(meta_agg, solver_agg, configs: dict, solvers: list[str],
                       out_path: str) -> None:
    """G7: tempo por instância (MH por config × solvers), escala log."""
    instances = _instances(meta_agg, solver_agg)
    if not instances:
        return
    pos = range(len(instances))

    series: list[tuple[str, list[float]]] = []
    for label, cfg in configs.items():
        vals = [meta_agg[(cfg, i)]["time_ms_mean"] if (cfg, i) in meta_agg else 0.0
                for i in instances]
        if any(vals):
            series.append((f"MH {label}", vals))
    for slv in solvers:
        vals = [solver_agg[(slv, i)]["time_ms"] if (slv, i) in solver_agg else 0.0
                for i in instances]
        if any(vals):
            series.append((slv, vals))
    if not series:
        return

    n = len(series)
    width = 0.8 / n
    fig, ax = plt.subplots(figsize=(11, 5))
    for k, (label, vals) in enumerate(series):
        offset = (k - (n - 1) / 2) * width
        ax.bar([p + offset for p in pos], vals, width, label=label)
    ax.set_yscale("log")
    ax.set_xticks(list(pos))
    ax.set_xticklabels(instances, rotation=45, ha="right")
    ax.set_ylabel("tempo (ms, log)")
    ax.set_title("Comparação por instância — tempo (MH × solvers)")
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
