"""UI event queue."""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Any


class UIQueue:
    """Simple FIFO queue for UI-bound events."""

    def __init__(self) -> None:
        self._queue: Deque[Dict[str, Any]] = deque()

    def put(self, event: Dict[str, Any]) -> None:
        self._queue.append(event)

    def pop(self) -> Dict[str, Any] | None:
        if not self._queue:
            return None
        return self._queue.popleft()

    def empty(self) -> bool:
        return not self._queue
