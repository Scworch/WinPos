"""Monitor discovery and metadata."""

from __future__ import annotations

from dataclasses import dataclass

from screeninfo import get_monitors

from modules.ui_queue import UIQueue


@dataclass
class MonitorManager:
    ui_queue: UIQueue

    async def refresh(self) -> None:
        """Collect monitor info and emit a UI event."""
        monitors = get_monitors()
        self.ui_queue.put({"event": "monitors_refreshed", "count": len(monitors)})
