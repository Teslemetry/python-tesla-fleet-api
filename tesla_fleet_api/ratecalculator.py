"""Rate Calculator helper"""

import time

DAY = 24 * 60 * 60


class RateCalculator:
    """Calculate the consumption and remaining rate of a rate limit."""

    def __init__(
        self,
        limit: int,
        period: int = 86400,
        min_wait: int = 0,
        max_wait: int | None = None,
        factor: int = 5,
    ) -> None:
        """Initialize the rate calculator."""
        self.limit: int = limit
        self.period: int = period
        self.history: list[int] = []
        self.start = time.time()
        self.min_wait = min_wait
        self.max_wait = max_wait if max_wait is not None else period
        self.factor = factor

    def constrain(self, value: float) -> float:
        """Constrain a value between min and max."""
        return max(self.min_wait, min(self.max_wait, value))

    def consume(self, timestamp: int | None = None) -> None:
        """Consume a unit of the rate limit."""
        now = timestamp or int(time.time() + 1)
        self.history.append(now)

    def calculate(self, timestamp: int | None = None) -> float:
        """Return the ideal delay to avoid rate limiting."""

        count = len(self.history)
        if count == 0:
            return self.min_wait

        now = timestamp or int(time.time())

        while self.history and self.history[0] < now - self.period:
            self.history.pop(0)

        remaining = self.limit - count

        if remaining <= 0:
            # The wait until a request is available
            return self.constrain(self.history[abs(remaining)] + self.period - now)

        return self.constrain(self.period / remaining / self.factor)

    @property
    def count(self) -> int:
        """Return the number of requests in the current period."""
        return len(self.history)
