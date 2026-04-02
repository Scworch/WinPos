"""Global sequential queue for UI actions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, Awaitable, Optional


UIAction = Callable[[], Awaitable[bool]]


@dataclass
class UIQueue:
    """Single-threaded async UI action queue."""

    _queue: asyncio.Queue[UIAction]
    _running: bool = False

    def __init__(self) -> None:
        self._queue = asyncio.Queue()
        self._running = False

    async def enqueue(self, action: UIAction) -> None:
        await self._queue.put(action)

    async def run(self) -> None:
        if self._running:
            return
        self._running = True
        while self._running:
            action = await self._queue.get()
            try:
                await action()
            finally:
                self._queue.task_done()

    async def stop(self) -> None:
        self._running = False

    def empty(self) -> bool:
        return self._queue.empty()
