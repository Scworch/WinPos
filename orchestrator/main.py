"""WinPos orchestrator entry point."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from config.manager import ConfigManager
from logging_system.logger import setup_logging
from orchestrator.job_guard import JobGuard
from orchestrator.scheduler import Scheduler
from launcher.launcher import Launcher
from monitors.monitor_manager import MonitorManager
from windows.window_manager import WindowManager
from ui.action_queue import UIQueue
from state.state_manager import StateManager
from recovery.watchdog import Watchdog
from registry.app_registry import AppRegistry


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.yaml"
LOG_DIR = ROOT / "logs"
LOCK_DIR = ROOT / "state" / "locks"


def _select_profile(config_manager: ConfigManager) -> str:
    raw_settings = (config_manager.raw or {}).get("settings", {}) if config_manager.raw else {}
    return str(raw_settings.get("default_profile", "default"))


async def main() -> None:
    config_manager = ConfigManager(CONFIG_PATH)
    config = config_manager.load()

    setup_logging(LOG_DIR, level="INFO")
    logger = logging.getLogger("orchestrator")

    profile_id = _select_profile(config_manager)
    guard = JobGuard(lock_dir=LOCK_DIR)
    if not config.settings.allow_profile_reentry and not guard.acquire(profile_id):
        logger.warning("Profile '%s' already running", profile_id)
        return

    try:
        monitor_manager = MonitorManager(config.monitor_roles)
        monitor_manager.refresh()

        scheduler = Scheduler(
            config=config,
            launcher=Launcher(),
            window_manager=WindowManager(),
            monitor_manager=monitor_manager,
            ui_queue=UIQueue(),
            state_manager=StateManager(),
            watchdog=Watchdog(),
        )

        ui_task = asyncio.create_task(scheduler.ui_queue.run())
        registry = AppRegistry.from_config(config)
        apps = registry.list_apps_for_profile(profile_id)
        await scheduler.run_profile(profile_id, apps)

        await scheduler.ui_queue.stop()
        ui_task.cancel()

        summary = scheduler.state_manager.summary()
        logger.info("Run summary: %s", summary)
    finally:
        guard.release()


if __name__ == "__main__":
    asyncio.run(main())
