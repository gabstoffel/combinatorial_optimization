"""Carrega e normaliza a árvore de resultados em registros tipados.

Árvore esperada (method-first, 4 níveis):
    results/<family>/<key>/<machine>/<config_id>/omaNN_<method>.jsonl
  - metaheurística: family=metaheuristica, key=tabu  (1 linha por semente)
  - solver:         family=solver,        key=highs|cplex (1 linha por instância)

`machine` NÃO é dimensão de análise (hardware idêntico) — serve só para unir os
arquivos. Reexecuções acrescentam linhas (append); este módulo deduplica por
(family, key, machine, config_id, instance, seed) mantendo a última ocorrência.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from oma.analysis.bkv import bkv_for

# Bloco de varredura -> parâmetro que ele varia (config_id começa com o bloco).
BLOCK_PARAM = {
    "A1": "tenure",
    "A2": "max_no_improve",
    "A3": "max_iter",
    "A4": "diversify_freq",
    "A5": "init",
}


@dataclass
class Record:
    family: str            # "metaheuristica" | "solver"
    key: str               # "tabu" | "highs" | "cplex"
    machine: str           # M1/M2/M3 (colapsado na análise)
    config_id: str         # "A1_tenure-05", "B_baseline", "tl-600", ...
    instance: str          # "oma01"
    instance_num: int      # 1..10
    method: str            # "tabu" | "highs" | "cplex"
    params: dict
    final_solution: float
    time_ms: float
    bkv: int
    seed: int | None = None             # metaheurística
    status: str | None = None           # solver (Optimal/Feasible/...)
    initial_solution: float | None = None  # metaheurística (SI)

    @property
    def is_solver(self) -> bool:
        return self.family == "solver"

    @property
    def block(self) -> str | None:
        """Bloco de varredura (A1..A5, B) derivado do config_id; None p/ solver."""
        head = self.config_id.split("_", 1)[0]
        if head in BLOCK_PARAM or head == "B":
            return head
        return None

    @property
    def varied_value(self):
        """Valor do parâmetro variado neste bloco (ex.: A1 -> tenure)."""
        block = self.block
        if block in BLOCK_PARAM:
            return self.params.get(BLOCK_PARAM[block])
        return None

    @property
    def otimalidade_pct(self) -> float:
        return 100.0 * self.final_solution / self.bkv

    @property
    def dev_bkv_pct(self) -> float:
        return 100.0 * (self.bkv - self.final_solution) / self.bkv

    @property
    def dev_initial_pct(self) -> float | None:
        if self.initial_solution in (None, 0):
            return None
        return 100.0 * (self.initial_solution - self.final_solution) / self.initial_solution


def _warn(msg: str) -> None:
    print(f"[oma-report] aviso: {msg}", file=sys.stderr)


def _parse_path(jsonl: Path, root: Path) -> tuple[str, str, str, str] | None:
    """Deriva (family, key, machine, config_id) do caminho relativo à raiz."""
    rel = jsonl.relative_to(root).parts
    if len(rel) < 5:
        _warn(f"caminho raso ignorado: {jsonl}")
        return None
    family, key, machine, config_id = rel[0], rel[1], rel[2], rel[3]
    return family, key, machine, config_id


def load_records(results_dir: str | Path) -> list[Record]:
    """Lê todos os `*.jsonl` sob `results_dir`, normaliza e deduplica."""
    root = Path(results_dir)
    by_key: dict[tuple, Record] = {}
    dups = 0

    for jsonl in sorted(root.glob("**/*.jsonl")):
        parsed = _parse_path(jsonl, root)
        if parsed is None:
            continue
        family, key, machine, config_id = parsed

        for raw in jsonl.read_text().splitlines():
            raw = raw.strip()
            if not raw:
                continue
            row = json.loads(raw)
            instance = row["instance"]
            instance_num = int(instance[3:])
            rec = Record(
                family=family,
                key=key,
                machine=machine,
                config_id=config_id,
                instance=instance,
                instance_num=instance_num,
                method=row.get("method", key),
                params=row.get("params") or {},
                final_solution=row["final_solution"],
                time_ms=row["time_ms"],
                bkv=bkv_for(instance),
                seed=row.get("seed"),
                status=row.get("status"),
                initial_solution=row.get("initial_solution"),
            )
            dkey = (family, key, machine, config_id, instance, rec.seed)
            if dkey in by_key:
                dups += 1
            by_key[dkey] = rec  # keep last

    if dups:
        _warn(f"{dups} linha(s) duplicada(s) por reexecução — mantida a última de cada.")
    return list(by_key.values())


def meta_records(records: list[Record]) -> list[Record]:
    return [r for r in records if r.family == "metaheuristica"]


def solver_records(records: list[Record]) -> list[Record]:
    return [r for r in records if r.is_solver]


def solvers_present(records: list[Record]) -> list[str]:
    return sorted({r.key for r in records if r.is_solver})
