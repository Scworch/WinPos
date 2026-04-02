"""Runtime state tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from actions.base import ActionResult


@dataclass
class AppState:
    app_id: str
    results: List[ActionResult] = field(default_factory=list)


class StateManager:
    """Tracks app execution state and results."""

    def __init__(self) -> None:
        self._apps: Dict[str, AppState] = {}

    def record(self, app_id: str, result: ActionResult) -> None:
        state = self._apps.setdefault(app_id, AppState(app_id=app_id))
        state.results.append(result)

    def summary(self) -> Dict[str, int]:
        summary = {}
        for app_id, state in self._apps.items():
            summary[app_id] = sum(1 for r in state.results if r.success)
        return summary
