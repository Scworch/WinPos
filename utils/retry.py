"""Retry helpers for async operations."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, TypeVar


T = TypeVar("T")


async def retry_async(
    func: Callable[[], Awaitable[T]],
    retries: int = 2,
    delay_s: float = 0.5,
) -> T:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await func()
        except Exception as exc:  # noqa: BLE001 - deliberate retry wrapper
            last_exc = exc
            if attempt >= retries:
                raise
            await asyncio.sleep(delay_s)
    raise last_exc or RuntimeError("Retry failed")
