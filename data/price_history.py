from collections import deque
import statistics
import time

class PriceHistory:
    """Tracks rolling price history for TWAP and volatility calculations."""
    
    def __init__(self, window_seconds=300):
        self.window_seconds = window_seconds
        self.yes_prices = deque()  # (timestamp, price)
        self.no_prices = deque()

    def add_yes_price(self, price: float):
        now = time.time()
        self.yes_prices.append((now, price))
        self._prune(self.yes_prices)

    def add_no_price(self, price: float):
        now = time.time()
        self.no_prices.append((now, price))
        self._prune(self.no_prices)

    def _prune(self, prices: deque):
        """Remove prices outside the rolling window."""
        cutoff = time.time() - self.window_seconds
        while prices and prices[0][0] < cutoff:
            prices.popleft()

    @property
    def yes_twap(self) -> float:
        """Time-weighted average price for YES."""
        if not self.yes_prices:
            return 0.5
        return statistics.mean(p for _, p in self.yes_prices)

    @property
    def no_twap(self) -> float:
        """Time-weighted average price for NO."""
        if not self.no_prices:
            return 0.5
        return statistics.mean(p for _, p in self.no_prices)

    @property
    def yes_std(self) -> float:
        """Standard deviation of YES prices."""
        prices = [p for _, p in self.yes_prices]
        return statistics.stdev(prices) if len(prices) > 1 else 0.05

    @property
    def no_std(self) -> float:
        """Standard deviation of NO prices."""
        prices = [p for _, p in self.no_prices]
        return statistics.stdev(prices) if len(prices) > 1 else 0.05
