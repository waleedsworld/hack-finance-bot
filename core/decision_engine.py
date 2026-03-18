from .pair_cost_engine import MarketPosition

class DecisionEngine:
    """Determines whether to execute a trade based on strategy rules."""
    
    def __init__(self, config):
        self.safety_margin = config.get("safety_margin", 0.99)
        self.max_imbalance_ratio = config.get("max_imbalance", 1.20)
        self.min_price_discount = config.get("min_discount", 0.03)
        self.max_position_usd = config.get("max_position_usd", 1000)

    def should_buy_yes(self, position: MarketPosition, yes_price: float,
                       yes_twap: float, qty: float) -> tuple[bool, str]:
        """Evaluate if YES purchase meets all criteria."""
        
        # Rule 1: Must be cheap relative to recent average
        if yes_price > yes_twap - self.min_price_discount:
            return False, "YES not cheap enough vs TWAP"

        # Rule 2: Simulate impact on pair cost
        simulated_pair_cost = position.simulate_buy("YES", yes_price, qty)
        if simulated_pair_cost >= self.safety_margin:
            return False, f"Would push pair cost to {simulated_pair_cost:.4f}"

        # Rule 3: Don't let YES get too far ahead of NO
        if position.qty_yes > 0 and position.qty_no > 0:
            if (position.qty_yes + qty) / position.qty_no > self.max_imbalance_ratio:
                return False, "YES quantity too imbalanced vs NO"

        # Rule 4: Don't exceed max position size
        if position.cost_yes + (yes_price * qty) > self.max_position_usd:
            return False, "Max position size reached"

        return True, "BUY YES approved"

    def should_buy_no(self, position: MarketPosition, no_price: float,
                      no_twap: float, qty: float) -> tuple[bool, str]:
        """Evaluate if NO purchase meets all criteria."""
        
        if no_price > no_twap - self.min_price_discount:
            return False, "NO not cheap enough vs TWAP"

        simulated_pair_cost = position.simulate_buy("NO", no_price, qty)
        if simulated_pair_cost >= self.safety_margin:
            return False, f"Would push pair cost to {simulated_pair_cost:.4f}"

        if position.qty_yes > 0 and position.qty_no > 0:
            if (position.qty_no + qty) / position.qty_yes > self.max_imbalance_ratio:
                return False, "NO quantity too imbalanced vs YES"

        if position.cost_no + (no_price * qty) > self.max_position_usd:
            return False, "Max position size reached"

        return True, "BUY NO approved"
