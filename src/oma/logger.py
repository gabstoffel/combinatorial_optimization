import json
import logging
import os
import sys
from typing import Any


def write_run(
    instance_number: int,
    method: str,
    final_solution: float,
    time_ms: float,
    initial_solution: float | None = None,
    status: str | None = None,
    params: dict | None = None,
) -> None:
    record = {
        "instance": f"oma{instance_number:02d}",
        "method": method,
        "status": status,
        "params": params,
        "initial_solution": initial_solution,
        "final_solution": final_solution,
        "time_ms": time_ms,
    }

    os.makedirs("logs", exist_ok=True)
    path = f"logs/oma{instance_number:02d}_{method}.json"
    with open(path, "w") as file:
        json.dump(record, file, indent=2)


def _meta_dir(out_dir: str, config_id: str | None) -> str:
    """Directory holding the metaheuristic logs for a run/config."""
    return os.path.join(out_dir, config_id) if config_id else out_dir


def append_meta_run(
    instance_number: int,
    method: str,
    seed: int,
    initial_solution: float,
    final_solution: float,
    time_ms: float,
    params: dict | None = None,
    config_id: str | None = None,
    out_dir: str = "logs",
) -> None:
    """Append one metaheuristic run (a single seed) as a JSON line to
    `<out_dir>[/<config_id>]/omaNN_<method>.jsonl`. Always appends, so history
    accumulates across invocations. The `params` and `config_id` are embedded in
    every line, making each result self-describing.
    """
    record = {
        "instance": f"oma{instance_number:02d}",
        "method": method,
        "config_id": config_id,
        "seed": seed,
        "params": params,
        "initial_solution": initial_solution,
        "final_solution": final_solution,
        "time_ms": time_ms,
    }

    directory = _meta_dir(out_dir, config_id)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"oma{instance_number:02d}_{method}.jsonl")
    with open(path, "a") as file:
        file.write(json.dumps(record) + "\n")


def write_config(config: dict, config_id: str | None, out_dir: str = "logs") -> None:
    """Write a one-time `config.json` describing the parameters of a config, so a
    results directory is self-describing alongside its `.jsonl` files."""
    directory = _meta_dir(out_dir, config_id)
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, "config.json"), "w") as file:
        json.dump(config, file, indent=2)


class Logger:
    def __init__(self, file_path: str | None = None, stderr: bool = True):
        self._logger = logging.getLogger("oma")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()

        formatter = logging.Formatter("%(message)s")

        if stderr:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        if file_path:
            parent = os.path.dirname(file_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            handler = logging.FileHandler(file_path)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def _emit(self, level: int, event_kind: str, data: Any):
        entry = {"event_kind": event_kind, "data": data}
        self._logger.log(level, json.dumps(entry))

    def info(self, event_kind: str, data: Any = None):
        self._emit(logging.INFO, event_kind, data)

    def warning(self, event_kind: str, data: Any = None):
        self._emit(logging.WARNING, event_kind, data)

    def error(self, event_kind: str, data: Any = None):
        self._emit(logging.ERROR, event_kind, data)
