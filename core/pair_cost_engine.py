from dataclasses import dataclass

@dataclass
class MarketPosition:
    """Tracks position state for a single market."""
    market_id: str
    qty_yes: float = 0.0
    qty_no: float = 0.0
    cost_yes: float = 0.0
    cost_no: float = 0.0

    @property
    def avg_yes(self) -> float:
        """Average cost per YES share."""
        return self.cost_yes / self.qty_yes if self.qty_yes > 0 else 1.0

    @property
    def avg_no(self) -> float:
        """Average cost per NO share."""
        return self.cost_no / self.qty_no if self.qty_no > 0 else 1.0

    @property
    def pair_cost(self) -> float:
        """THE KEY METRIC: sum of average costs."""
        return self.avg_yes + self.avg_no

    @property
    def is_profit_locked(self) -> bool:
        """Check if profit is mathematically guaranteed."""
        if self.qty_yes == 0 or self.qty_no == 0:
            return False
        guaranteed_payout = min(self.qty_yes, self.qty_no)
        total_spent = self.cost_yes + self.cost_no
        return guaranteed_payout > total_spent

    @property
    def locked_profit(self) -> float:
        """Calculate guaranteed profit amount."""
        return min(self.qty_yes, self.qty_no) - (self.cost_yes + self.cost_no)

    def simulate_buy(self, side: str, price: float, qty: float) -> float:
        """Returns pair_cost AFTER a hypothetical buy, without modifying state."""
        if side == "YES":
            new_avg_yes = (self.cost_yes + price * qty) / (self.qty_yes + qty)
            return new_avg_yes + self.avg_no
        else:
            new_avg_no = (self.cost_no + price * qty) / (self.qty_no + qty)
            return self.avg_yes + new_avg_no

    def record_buy(self, side: str, price: float, qty: float):
        """Record an executed trade."""
        if side == "YES":
            self.qty_yes += qty
            self.cost_yes += price * qty
        else:
            self.qty_no += qty
            self.cost_no += price * qty
