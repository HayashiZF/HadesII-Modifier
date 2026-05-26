from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .defaults import DEFAULT_STATE


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return copy.deepcopy(DEFAULT_STATE)

        with self.path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        return _deep_merge(DEFAULT_STATE, loaded)

    def save(self, state: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8", newline="") as handle:
            json.dump(state, handle, indent=2)


__all__ = ["StateStore", "_deep_merge"]
