"""Window management helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pygetwindow as gw

from modules.ui_queue import UIQueue


@dataclass
class WindowManager:
    ui_queue: UIQueue

    async def refresh(self) -> None:
        """Capture current windows and emit a UI event."""
        titles = [title for title in gw.getAllTitles() if title]
        self.ui_queue.put({"event": "windows_refreshed", "count": len(titles)})
