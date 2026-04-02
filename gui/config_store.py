"""Config store for GUI editing."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from config.manager import DEFAULT_CONFIG, validate_config


class ConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Dict[str, Any]:
        data = _deep_merge(DEFAULT_CONFIG, {})
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as handle:
                loaded = yaml.safe_load(handle) or {}
            data = _deep_merge(data, loaded)
        return data

    def save(self, data: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)

    def validate(self, data: Dict[str, Any]) -> List[str]:
        return validate_config(data)


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
