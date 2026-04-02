"""Application launcher and process utilities."""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import psutil

from config.models import AppDefinition


@dataclass
class LaunchResult:
    started: bool
    pid: Optional[int] = None
    message: str = ""


class Launcher:
    """Launches applications and detects running instances."""

    def is_running(self, app: AppDefinition) -> bool:
        if not app.launch or not app.launch.cmd:
            return False
        cmd = app.launch.cmd.lower()
        cmd_basename = os.path.basename(cmd)
        for proc in psutil.process_iter(["name", "exe"]):
            try:
                name = (proc.info.get("name") or "").lower()
                exe = (proc.info.get("exe") or "").lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            if cmd in (name, exe) or cmd_basename in (name, os.path.basename(exe)):
                return True
        return False

    def launch(self, app: AppDefinition) -> LaunchResult:
        if not app.launch or not app.launch.cmd:
            return LaunchResult(started=False, message="No launch command")

        if self.is_running(app):
            return LaunchResult(started=False, message="Already running")

        args = [app.launch.cmd] + app.launch.args
        process = subprocess.Popen(args, cwd=app.launch.cwd)
        return LaunchResult(started=True, pid=process.pid)

    def wait_for_process(self, app: AppDefinition, timeout_s: float) -> Optional[int]:
        if not app.launch or not app.launch.cmd:
            return None
        cmd = app.launch.cmd.lower()
        cmd_basename = os.path.basename(cmd)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            for proc in psutil.process_iter(["pid", "name", "exe"]):
                try:
                    name = (proc.info.get("name") or "").lower()
                    exe = (proc.info.get("exe") or "").lower()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                if cmd in (name, exe) or cmd_basename in (name, os.path.basename(exe)):
                    return proc.pid
        return None
