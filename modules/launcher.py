"""Launch and lifecycle helpers."""

from __future__ import annotations

from dataclasses import dataclass

from modules.ui_queue import UIQueue


@dataclass
class Launcher:
    ui_queue: UIQueue

    async def initialize(self, config: dict) -> None:
        """Prepare runtime dependencies and initial state."""
        self.ui_queue.put({"event": "launcher_initialized", "config": config})
