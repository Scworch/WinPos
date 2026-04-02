"""WinAPI-based window management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

import win32con
import win32gui

from config.models import WindowMatch
from monitors.monitor_manager import MonitorInfo


@dataclass
class WindowInfo:
    handle: int
    title: str
    class_name: str


class WindowManager:
    """Find and control windows using WinAPI."""

    def list_windows(self) -> List[WindowInfo]:
        windows: List[WindowInfo] = []

        def callback(handle: int, _: int) -> None:
            if not win32gui.IsWindowVisible(handle):
                return
            title = win32gui.GetWindowText(handle)
            if not title:
                return
            class_name = win32gui.GetClassName(handle)
            windows.append(WindowInfo(handle=handle, title=title, class_name=class_name))

        win32gui.EnumWindows(callback, 0)
        return windows

    def find_windows(self, match: WindowMatch | None) -> List[WindowInfo]:
        if not match:
            return []
        windows = self.list_windows()
        results: List[WindowInfo] = []
        for window in windows:
            if match.title_contains and match.title_contains not in window.title:
                continue
            if match.title_equals and match.title_equals != window.title:
                continue
            if match.class_name and match.class_name != window.class_name:
                continue
            results.append(window)
        return results

    def bring_to_foreground(self, handle: int) -> None:
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(handle)

    def maximize(self, handle: int) -> None:
        win32gui.ShowWindow(handle, win32con.SW_MAXIMIZE)

    def minimize(self, handle: int) -> None:
        win32gui.ShowWindow(handle, win32con.SW_MINIMIZE)

    def move_to_monitor(self, handle: int, monitor: MonitorInfo) -> None:
        x, y, width, height = monitor.bounds
        win32gui.MoveWindow(handle, x, y, width, height, True)

    def resize(self, handle: int, width: int, height: int) -> None:
        rect = win32gui.GetWindowRect(handle)
        win32gui.MoveWindow(handle, rect[0], rect[1], width, height, True)

    def center_on_monitor(self, handle: int, monitor: MonitorInfo) -> None:
        rect = win32gui.GetWindowRect(handle)
        win_width = rect[2] - rect[0]
        win_height = rect[3] - rect[1]
        x = monitor.x + (monitor.width - win_width) // 2
        y = monitor.y + (monitor.height - win_height) // 2
        win32gui.MoveWindow(handle, x, y, win_width, win_height, True)

    async def wait_for_window(self, match: WindowMatch, timeout_s: float) -> Optional[WindowInfo]:
        from utils.waiters import wait_until

        result: List[WindowInfo] = []

        def predicate() -> bool:
            result.clear()
            result.extend(self.find_windows(match))
            return bool(result)

        if await wait_until(predicate, timeout_s=timeout_s):
            return result[0]
        return None
