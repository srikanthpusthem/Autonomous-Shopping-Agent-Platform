from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            history = [stamp for stamp in self._requests[key] if stamp >= cutoff]
            if len(history) >= self.max_requests:
                raise HTTPException(
                    status_code=429, detail="Too many run requests. Try again soon."
                )
            history.append(now)
            self._requests[key] = history


runs_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)
