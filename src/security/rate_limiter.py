import time
from collections import defaultdict
from typing import Tuple


class SlidingWindowRateLimiter:
    """
    In-memory Sliding-Window Rate Limiter.
    Protects APIs from denial-of-service and brute force attacks.
    """

    def __init__(self, default_limit: int = 60, default_window_seconds: float = 60.0):
        self.default_limit = default_limit
        self.default_window_seconds = default_window_seconds
        self._clients: dict[str, list[float]] = defaultdict(list)

    def is_allowed(
        self,
        client_id: str,
        limit: int = None,
        window_seconds: float = None,
    ) -> Tuple[bool, int, float]:
        """
        Determines if a request from client_id is within rate limits.
        Returns: (is_allowed, remaining_quota, retry_after_seconds)
        """
        now = time.time()
        max_requests = limit or self.default_limit
        window = window_seconds or self.default_window_seconds

        timestamps = self._clients[client_id]
        # Evict timestamps older than the sliding window
        valid_timestamps = [t for t in timestamps if (now - t) <= window]
        self._clients[client_id] = valid_timestamps

        if len(valid_timestamps) < max_requests:
            self._clients[client_id].append(now)
            remaining = max_requests - (len(valid_timestamps) + 1)
            return True, remaining, 0.0
        else:
            oldest_in_window = valid_timestamps[0]
            retry_after = round(window - (now - oldest_in_window), 1)
            return False, 0, max(0.1, retry_after)
