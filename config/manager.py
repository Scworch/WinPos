"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import yaml

from config.models import Config


DEFAULT_CONFIG: Dict[str, Any] = {
    "version": 1,
    "monitor_roles": {
        "primary": {"match": {"is_primary": True}},
    },
    "action_chains": {},
    "apps": {},
    "profiles": {
        "default": {"apps": []},
    },
    "settings": {
        "allow_profile_reentry": False,
        "default_timeout_s": 15.0,
        "default_profile": "default",
    },
}


class ConfigManager:
    """Load, validate, and expose configuration data."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.raw: Dict[str, Any] = {}
        self.config: Config | None = None

    def load(self) -> Config:
        data = dict(DEFAULT_CONFIG)
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as handle:
                loaded = yaml.safe_load(handle) or {}
            data = _deep_merge(data, loaded)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as handle:
                yaml.safe_dump(DEFAULT_CONFIG, handle, sort_keys=False, allow_unicode=True)

        self.raw = data
        issues = validate_config(data)
        if issues:
            issue_text = "; ".join(issues)
            raise ValueError(f"Config validation failed: {issue_text}")

        self.config = Config.from_dict(data)
        return self.config

    def to_dict(self) -> Dict[str, Any]:
        if not self.config:
            return {}
        return asdict(self.config)


def validate_config(data: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    if "apps" not in data or not isinstance(data.get("apps"), dict):
        issues.append("apps must be a mapping")
    if "profiles" not in data or not isinstance(data.get("profiles"), dict):
        issues.append("profiles must be a mapping")
    for profile_id, profile in (data.get("profiles", {}) or {}).items():
        apps = profile.get("apps", [])
        if not isinstance(apps, list):
            issues.append(f"profile '{profile_id}' apps must be a list")
    return issues


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
