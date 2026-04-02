"""Action base classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from config.models import AppDefinition, Config, ActionSpec
from launcher.launcher import Launcher
from monitors.monitor_manager import MonitorManager
from windows.window_manager import WindowManager
from ui.action_queue import UIQueue
from state.state_manager import StateManager


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionContext:
    config: Config
    app: AppDefinition
    launcher: Launcher
    window_manager: WindowManager
    monitor_manager: MonitorManager
    ui_queue: UIQueue
    state_manager: StateManager
    logger_name: str

    def child_logger(self, action_type: str) -> str:
        return f"{self.logger_name}.{action_type}"


class Action:
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:  # pragma: no cover - interface
        raise NotImplementedError
