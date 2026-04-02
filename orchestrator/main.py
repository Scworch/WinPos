"""WinPos orchestrator entry point."""

from __future__ import annotations

import asyncio
from pathlib import Path

from modules.launcher import Launcher
from modules.monitor_manager import MonitorManager
from modules.window_manager import WindowManager
from modules.ui_queue import UIQueue
from utils.waiters import wait_until


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.yaml"


def load_config(path: Path) -> dict:
    """Load a minimal key: value config without extra dependencies."""
    defaults = {
        "log_level": "INFO",
        "poll_interval_ms": 250,
    }

    if not path.exists():
        return defaults

    data: dict[str, str | int] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = [part.strip() for part in line.split(":", 1)]
            if value.isdigit():
                data[key] = int(value)
            else:
                data[key] = value.strip(\"\\\"'\")

    return {**defaults, **data}


async def main() -> None:
    config = load_config(CONFIG_PATH)

    ui_queue = UIQueue()
    launcher = Launcher(ui_queue=ui_queue)
    window_manager = WindowManager(ui_queue=ui_queue)
    monitor_manager = MonitorManager(ui_queue=ui_queue)

    # Basic startup sequence; replace with real workflow.
    await launcher.initialize(config)
    await monitor_manager.refresh()
    await window_manager.refresh()

    await wait_until(lambda: ui_queue.empty(), timeout_s=2.0)


if __name__ == "__main__":
    asyncio.run(main())
