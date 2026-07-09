"""
Rate limiter — configurable in-memory sliding-window rate limiter.
Resets on server restart; for production use Redis or a DB-backed store.
"""

import logging
import time

logger = logging.getLogger(__name__)


class RateLimiter:
    """Sliding-window rate limiter keyed by string (IP, email, user_id)."""

    def __init__(self):
        self._buckets: dict[str, list[float]] = {}

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Returns True if the key is under the limit for this window.
        Records the attempt on success.
        """
        now = time.time()
        if key not in self._buckets:
            self._buckets[key] = []

        self._buckets[key] = [t for t in self._buckets[key] if now - t < window_seconds]

        if len(self._buckets[key]) >= max_requests:
            return False

        self._buckets[key].append(now)
        return True

    def remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Return how many requests the key can still make in this window."""
        now = time.time()
        if key not in self._buckets:
            return max_requests
        self._buckets[key] = [t for t in self._buckets[key] if now - t < window_seconds]
        return max(0, max_requests - len(self._buckets[key]))

    def get_cooldown(self, key: str, cooldown_seconds: int) -> float:
        """Return seconds remaining before the key can act again. 0 = allowed."""
        if key not in self._buckets or not self._buckets[key]:
            return 0.0
        elapsed = time.time() - self._buckets[key][-1]
        remaining = cooldown_seconds - elapsed
        return max(0.0, remaining)

    def clear(self, key: str):
        """Remove all records for a key (used after successful completion)."""
        self._buckets.pop(key, None)

    def clear_all(self):
        """Remove all rate-limit records (useful in tests)."""
        self._buckets.clear()


limiter = RateLimiter()
