"""Monitor discovery and role assignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import win32api
import win32con
from screeninfo import get_monitors


@dataclass
class MonitorInfo:
    index: int
    name: str
    device_name: str
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
        self._monitors = self._get_win32_monitors()
        if not self._monitors:
            self._monitors = self._get_screeninfo_monitors()
        self._assign_roles()

    def _get_win32_monitors(self) -> List[MonitorInfo]:
        monitors: List[MonitorInfo] = []
        index = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, index, 0)
            except win32api.error:
                break
            index += 1
            if not (device.StateFlags & win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP):
                continue

            dev_name = device.DeviceName
            dev_string = device.DeviceString or dev_name
            try:
                settings = win32api.EnumDisplaySettings(dev_name, win32con.ENUM_CURRENT_SETTINGS)
                x = int(getattr(settings, "Position_x", 0))
                y = int(getattr(settings, "Position_y", 0))
                width = int(getattr(settings, "PelsWidth", 0))
                height = int(getattr(settings, "PelsHeight", 0))
            except win32api.error:
                x = y = width = height = 0

            is_primary = bool(device.StateFlags & win32con.DISPLAY_DEVICE_PRIMARY_DEVICE)
            monitors.append(
                MonitorInfo(
                    index=len(monitors),
                    name=dev_string,
                    device_name=dev_name,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    is_primary=is_primary,
                )
            )
        return monitors

    def _get_screeninfo_monitors(self) -> List[MonitorInfo]:
        monitors: List[MonitorInfo] = []
        for idx, monitor in enumerate(get_monitors()):
            name = getattr(monitor, "name", f"monitor-{idx}")
            monitors.append(
                MonitorInfo(
                    index=idx,
                    name=name,
                    device_name=name,
                    x=monitor.x,
                    y=monitor.y,
                    width=monitor.width,
                    height=monitor.height,
                    is_primary=getattr(monitor, "is_primary", False),
                )
            )
        return monitors

    def _assign_roles(self) -> None:
        self._roles = {}
        for role, criteria in self._role_map.items():
            match = criteria.get("match", {}) if isinstance(criteria, dict) else {}
            selected = self._match_monitor(match)
            if selected:
                self._roles[role] = selected

    def _match_monitor(self, match: Dict[str, Any]) -> Optional[MonitorInfo]:
        for monitor in self._monitors:
            if "device_name" in match and monitor.device_name != match["device_name"]:
                continue
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
