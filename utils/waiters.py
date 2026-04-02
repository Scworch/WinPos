"""Async wait utilities."""

from __future__ import annotations

import asyncio
from typing import Callable


async def wait_until(predicate: Callable[[], bool], timeout_s: float = 5.0) -> bool:
    """Wait until predicate returns True or timeout occurs."""
    interval = 0.05
    elapsed = 0.0

    while elapsed < timeout_s:
        if predicate():
            return True
        await asyncio.sleep(interval)
        elapsed += interval

    return False
