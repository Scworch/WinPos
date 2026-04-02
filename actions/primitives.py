"""Reusable action primitives."""

from __future__ import annotations

import asyncio
import logging
import webbrowser
from typing import Dict

import keyboard
import pyautogui
import win32gui

from actions.base import Action, ActionContext, ActionResult
from config.models import ActionSpec


def _get_window_handle(ctx: ActionContext) -> int | None:
    match = ctx.app.window_match
    if not match:
        return None
    windows = ctx.window_manager.find_windows(match)
    if not windows:
        return None
    return windows[0].handle


class LaunchApp(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        result = ctx.launcher.launch(ctx.app)
        if result.started:
            return ActionResult(True, message="Launched", data={"pid": result.pid})
        return ActionResult(False, message=result.message)


class WaitForProcess(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        timeout_s = float(spec.params.get("timeout_s", ctx.config.settings.default_timeout_s))
        pid = ctx.launcher.wait_for_process(ctx.app, timeout_s=timeout_s)
        if pid:
            return ActionResult(True, message="Process ready", data={"pid": pid})
        return ActionResult(False, message="Process not found")


class WaitForWindow(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        if not ctx.app.window_match:
            return ActionResult(False, message="No window match configured")
        timeout_s = float(spec.params.get("timeout_s", ctx.config.settings.default_timeout_s))
        window = await ctx.window_manager.wait_for_window(ctx.app.window_match, timeout_s=timeout_s)
        if window:
            return ActionResult(True, message="Window ready", data={"handle": window.handle})
        return ActionResult(False, message="Window not found")


class BringToForeground(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        ctx.window_manager.bring_to_foreground(handle)
        return ActionResult(True, message="Foreground")


class MoveWindowToMonitor(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        role = spec.params.get("monitor_role", "primary")
        monitor = ctx.monitor_manager.get_by_role(role)
        if not monitor:
            return ActionResult(False, message=f"Monitor role '{role}' not found")
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        ctx.window_manager.move_to_monitor(handle, monitor)
        return ActionResult(True, message="Moved")


class CenterWindow(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        role = spec.params.get("monitor_role", "primary")
        monitor = ctx.monitor_manager.get_by_role(role)
        if not monitor:
            return ActionResult(False, message=f"Monitor role '{role}' not found")
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        ctx.window_manager.center_on_monitor(handle, monitor)
        return ActionResult(True, message="Centered")


class ResizeWindow(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        width = int(spec.params.get("width", 1280))
        height = int(spec.params.get("height", 720))
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        ctx.window_manager.resize(handle, width, height)
        return ActionResult(True, message="Resized")


class Maximize(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        ctx.window_manager.maximize(handle)
        return ActionResult(True, message="Maximized")


class Minimize(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        ctx.window_manager.minimize(handle)
        return ActionResult(True, message="Minimized")


class SendHotkeys(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        keys = spec.params.get("keys", "")
        if not keys:
            return ActionResult(False, message="No hotkeys provided")
        await ctx.ui_queue.enqueue(lambda: _send_hotkeys(keys))
        return ActionResult(True, message="Queued hotkeys")


class SendText(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        text = spec.params.get("text", "")
        if not text:
            return ActionResult(False, message="No text provided")
        enter_after = bool(spec.params.get("enter_after", False))
        await ctx.ui_queue.enqueue(lambda: _send_text(text, enter_after))
        return ActionResult(True, message="Queued text")


class OpenUrl(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        url = spec.params.get("url", "")
        if not url:
            return ActionResult(False, message="No URL provided")
        webbrowser.open(url)
        return ActionResult(True, message="Opened URL")


class WaitForTitleChange(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        expected = spec.params.get("contains", "")
        timeout_s = float(spec.params.get("timeout_s", ctx.config.settings.default_timeout_s))

        def predicate() -> bool:
            return expected in win32gui.GetWindowText(handle)

        from utils.waiters import wait_until

        if await wait_until(predicate, timeout_s=timeout_s):
            return ActionResult(True, message="Title matched")
        return ActionResult(False, message="Title not matched")


class WaitForVisibility(Action):
    async def run(self, ctx: ActionContext, spec: ActionSpec) -> ActionResult:
        handle = _get_window_handle(ctx)
        if not handle:
            return ActionResult(False, message="Window handle missing")
        timeout_s = float(spec.params.get("timeout_s", ctx.config.settings.default_timeout_s))

        def predicate() -> bool:
            return win32gui.IsWindowVisible(handle)

        from utils.waiters import wait_until

        if await wait_until(predicate, timeout_s=timeout_s):
            return ActionResult(True, message="Window visible")
        return ActionResult(False, message="Window not visible")


async def _send_hotkeys(keys: str) -> bool:
    logging.getLogger("ui.hotkeys").info("Sending hotkeys: %s", keys)
    keyboard.send(keys)
    await asyncio.sleep(0)
    return True


async def _send_text(text: str, enter_after: bool) -> bool:
    logging.getLogger("ui.text").info("Sending text")
    pyautogui.write(text, interval=0.01)
    if enter_after:
        keyboard.send("enter")
    await asyncio.sleep(0)
    return True


ACTION_REGISTRY: Dict[str, Action] = {
    "launch_app": LaunchApp(),
    "wait_for_process": WaitForProcess(),
    "wait_for_window": WaitForWindow(),
    "bring_to_foreground": BringToForeground(),
    "move_window_to_monitor": MoveWindowToMonitor(),
    "center_window": CenterWindow(),
    "resize_window": ResizeWindow(),
    "maximize": Maximize(),
    "minimize": Minimize(),
    "send_hotkeys": SendHotkeys(),
    "send_text": SendText(),
    "open_url": OpenUrl(),
    "wait_for_title_change": WaitForTitleChange(),
    "wait_for_visibility": WaitForVisibility(),
}
