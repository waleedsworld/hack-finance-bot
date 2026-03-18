from typing import Dict
from .pair_cost_engine import MarketPosition

class PositionTracker:
    """Tracks all active market positions."""
    
    def __init__(self):
        self.positions: Dict[str, MarketPosition] = {}
    
    def get_position(self, market_id: str) -> MarketPosition:
        """Get or create position for a market."""
        if market_id not in self.positions:
            self.positions[market_id] = MarketPosition(market_id=market_id)
        return self.positions[market_id]
    
    def get_all_positions(self):
        """Return all tracked positions."""
        return list(self.positions.values())
    
    def get_total_exposure(self) -> float:
        """Calculate total USD exposure across all positions."""
        return sum(
            p.cost_yes + p.cost_no 
            for p in self.positions.values()
        )
    
    def get_total_locked_profit(self) -> float:
        """Calculate total locked profit across all positions."""
        return sum(
            p.locked_profit 
            for p in self.positions.values() 
            if p.is_profit_locked
        )
    
    def get_locked_positions(self):
        """Return positions with locked profit."""
        return [p for p in self.positions.values() if p.is_profit_locked]
