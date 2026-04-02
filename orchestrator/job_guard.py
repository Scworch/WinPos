"""Simple job guard to prevent duplicate profile runs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class JobGuard:
    lock_dir: Path
    lock_path: Optional[Path] = None

    def acquire(self, profile_id: str) -> bool:
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self.lock_dir / f"{profile_id}.lock"
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(str(os.getpid()))
            self.lock_path = lock_path
            return True
        except FileExistsError:
            return False

    def release(self) -> None:
        if self.lock_path and self.lock_path.exists():
            self.lock_path.unlink(missing_ok=True)
        self.lock_path = None
