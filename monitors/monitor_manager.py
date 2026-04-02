"""Monitor discovery and role assignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from screeninfo import get_monitors


@dataclass
class MonitorInfo:
    index: int
    name: str
    x: int
    y: int
    width: int
    height: int
    is_primary: bool

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


class MonitorManager:
    """Detect monitors and map them to semantic roles."""

    def __init__(self, role_map: Dict[str, Dict[str, Any]]) -> None:
        self._role_map = role_map
        self._monitors: List[MonitorInfo] = []
        self._roles: Dict[str, MonitorInfo] = {}

    def refresh(self) -> None:
        self._monitors = []
        for idx, monitor in enumerate(get_monitors()):
            self._monitors.append(
                MonitorInfo(
                    index=idx,
                    name=getattr(monitor, "name", f"monitor-{idx}"),
                    x=monitor.x,
                    y=monitor.y,
                    width=monitor.width,
                    height=monitor.height,
                    is_primary=getattr(monitor, "is_primary", False),
                )
            )
        self._assign_roles()

    def _assign_roles(self) -> None:
        self._roles = {}
        for role, criteria in self._role_map.items():
            match = criteria.get("match", {}) if isinstance(criteria, dict) else {}
            selected = self._match_monitor(match)
            if selected:
                self._roles[role] = selected

    def _match_monitor(self, match: Dict[str, Any]) -> Optional[MonitorInfo]:
        for monitor in self._monitors:
            if "is_primary" in match and monitor.is_primary != bool(match["is_primary"]):
                continue
            if "index" in match and monitor.index != int(match["index"]):
                continue
            if "name_contains" in match and match["name_contains"].lower() not in monitor.name.lower():
                continue
            return monitor
        return None

    def get_by_role(self, role: str) -> Optional[MonitorInfo]:
        return self._roles.get(role)

    def get_all(self) -> List[MonitorInfo]:
        return list(self._monitors)
