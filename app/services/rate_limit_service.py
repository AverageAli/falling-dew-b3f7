from collections import defaultdict, deque
from datetime import datetime, timedelta


class InMemoryRateLimiter:
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.buckets: dict[int, deque[datetime]] = defaultdict(deque)

    def allowed(self, user_id: int) -> bool:
        now = datetime.utcnow()
        bucket = self.buckets[user_id]
        cutoff = now - timedelta(minutes=1)
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.max_per_minute:
            return False
        bucket.append(now)
        return True
