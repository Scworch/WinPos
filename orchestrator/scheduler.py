"""Profile scheduler and execution loop."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from actions.base import ActionContext, ActionResult
from actions.engine import ActionEngine
from config.models import AppDefinition, Config
from launcher.launcher import Launcher
from monitors.monitor_manager import MonitorManager
from ui.action_queue import UIQueue
from windows.window_manager import WindowManager
from state.state_manager import StateManager
from recovery.watchdog import Watchdog


@dataclass
class Scheduler:
    config: Config
    launcher: Launcher
    window_manager: WindowManager
    monitor_manager: MonitorManager
    ui_queue: UIQueue
    state_manager: StateManager
    watchdog: Watchdog

    async def run_app(self, app: AppDefinition) -> List[ActionResult]:
        logger_name = f"app.{app.app_id}"
        ctx = ActionContext(
            config=self.config,
            app=app,
            launcher=self.launcher,
            window_manager=self.window_manager,
            monitor_manager=self.monitor_manager,
            ui_queue=self.ui_queue,
            state_manager=self.state_manager,
            logger_name=logger_name,
        )
        engine = ActionEngine()
        results = await engine.execute_chain(app.actions, ctx)
        for result in results:
            self.state_manager.record(app.app_id, result)
        return results

    async def run_profile(self, profile_id: str, apps: List[AppDefinition]) -> None:
        logger = logging.getLogger("scheduler")
        logger.info("Starting profile '%s' with %d apps", profile_id, len(apps))
        for app in apps:
            try:
                results = await self.run_app(app)
                if any(not r.success for r in results):
                    self.watchdog.handle_failure(app.app_id, "Action failure")
            except Exception as exc:  # noqa: BLE001
                logger.exception("App '%s' failed", app.app_id)
                self.watchdog.handle_failure(app.app_id, str(exc))
        logger.info("Profile '%s' finished", profile_id)
