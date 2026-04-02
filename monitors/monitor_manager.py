"""Monitor discovery and role assignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import ctypes
from ctypes import wintypes

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
        self._monitors = self._get_ctypes_monitors()
        if not self._monitors:
            self._monitors = self._get_screeninfo_monitors()
        self._assign_roles()

    def _get_ctypes_monitors(self) -> List[MonitorInfo]:
        monitors: List[MonitorInfo] = []
        user32 = ctypes.WinDLL("user32", use_last_error=True)

        DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x1
        DISPLAY_DEVICE_PRIMARY_DEVICE = 0x4
        DISPLAY_DEVICE_MIRRORING_DRIVER = 0x8
        DISPLAY_DEVICE_ACTIVE = 0x1
        ENUM_CURRENT_SETTINGS = 0xFFFFFFFF

        class DISPLAY_DEVICEW(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("DeviceName", wintypes.WCHAR * 32),
                ("DeviceString", wintypes.WCHAR * 128),
                ("StateFlags", wintypes.DWORD),
                ("DeviceID", wintypes.WCHAR * 128),
                ("DeviceKey", wintypes.WCHAR * 128),
            ]

        class POINTL(ctypes.Structure):
            _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

        class DEVMODEW(ctypes.Structure):
            _fields_ = [
                ("dmDeviceName", wintypes.WCHAR * 32),
                ("dmSpecVersion", wintypes.WORD),
                ("dmDriverVersion", wintypes.WORD),
                ("dmSize", wintypes.WORD),
                ("dmDriverExtra", wintypes.WORD),
                ("dmFields", wintypes.DWORD),
                ("dmPosition", POINTL),
                ("dmDisplayOrientation", wintypes.DWORD),
                ("dmDisplayFixedOutput", wintypes.DWORD),
                ("dmColor", wintypes.SHORT),
                ("dmDuplex", wintypes.SHORT),
                ("dmYResolution", wintypes.SHORT),
                ("dmTTOption", wintypes.SHORT),
                ("dmCollate", wintypes.SHORT),
                ("dmFormName", wintypes.WCHAR * 32),
                ("dmLogPixels", wintypes.WORD),
                ("dmBitsPerPel", wintypes.DWORD),
                ("dmPelsWidth", wintypes.DWORD),
                ("dmPelsHeight", wintypes.DWORD),
                ("dmDisplayFlags", wintypes.DWORD),
                ("dmDisplayFrequency", wintypes.DWORD),
                ("dmICMMethod", wintypes.DWORD),
                ("dmICMIntent", wintypes.DWORD),
                ("dmMediaType", wintypes.DWORD),
                ("dmDitherType", wintypes.DWORD),
                ("dmReserved1", wintypes.DWORD),
                ("dmReserved2", wintypes.DWORD),
                ("dmPanningWidth", wintypes.DWORD),
                ("dmPanningHeight", wintypes.DWORD),
            ]

        enum_display_devices = user32.EnumDisplayDevicesW
        enum_display_devices.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DISPLAY_DEVICEW), wintypes.DWORD]
        enum_display_devices.restype = wintypes.BOOL

        enum_display_settings = user32.EnumDisplaySettingsW
        enum_display_settings.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DEVMODEW)]
        enum_display_settings.restype = wintypes.BOOL

        dev_index = 0
        while True:
            dd = DISPLAY_DEVICEW()
            dd.cb = ctypes.sizeof(DISPLAY_DEVICEW)
            if not enum_display_devices(None, dev_index, ctypes.byref(dd), 0):
                break
            dev_index += 1
            if not (dd.StateFlags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP):
                continue
            if dd.StateFlags & DISPLAY_DEVICE_MIRRORING_DRIVER:
                continue

            device_name = dd.DeviceName
            monitor_name = ""

            mon_index = 0
            while True:
                md = DISPLAY_DEVICEW()
                md.cb = ctypes.sizeof(DISPLAY_DEVICEW)
                if not enum_display_devices(device_name, mon_index, ctypes.byref(md), 0):
                    break
                mon_index += 1
                if md.StateFlags & DISPLAY_DEVICE_ACTIVE or mon_index == 1:
                    if md.DeviceString:
                        monitor_name = md.DeviceString
                        break

            if not monitor_name:
                monitor_name = dd.DeviceString or device_name

            devmode = DEVMODEW()
            devmode.dmSize = ctypes.sizeof(DEVMODEW)
            if enum_display_settings(device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(devmode)):
                x = int(devmode.dmPosition.x)
                y = int(devmode.dmPosition.y)
                width = int(devmode.dmPelsWidth)
                height = int(devmode.dmPelsHeight)
            else:
                x = y = width = height = 0

            is_primary = bool(dd.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE)
            monitors.append(
                MonitorInfo(
                    index=len(monitors),
                    name=monitor_name,
                    device_name=device_name,
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
