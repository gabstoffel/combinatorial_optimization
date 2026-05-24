import json
import logging
import sys
from typing import Any


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
