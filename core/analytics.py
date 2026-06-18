from typing import Dict, List, Optional
from .pair_cost_engine import MarketPosition


def _has_both_legs(p: MarketPosition) -> bool:
    """A book only has a meaningful pair cost once both legs are open."""
    return p.qty_yes > 0 and p.qty_no > 0


def compute_portfolio_analytics(positions: List[MarketPosition]) -> Dict:
    """Derive desk-level health metrics from the raw position book.

    Everything here is computed from state the tracker already holds, so it
    stays consistent with /api/stats — this endpoint just surfaces the ratios
    a trader actually watches: how hard the capital is working, which book is
    closest to locking, and how concentrated the exposure is.
    """
    two_legged = [p for p in positions if _has_both_legs(p)]
    total_exposure = sum(p.cost_yes + p.cost_no for p in positions)
    locked = [p for p in two_legged if p.is_profit_locked]
    total_locked_profit = sum(p.locked_profit for p in locked)

    # Return on exposure: locked profit as a fraction of capital at work.
    return_on_exposure = (total_locked_profit / total_exposure) if total_exposure > 0 else 0.0

    # Average pair cost across books that actually have a pair.
    avg_pair_cost = (
        sum(p.pair_cost for p in two_legged) / len(two_legged)
        if two_legged else 0.0
    )

    # Tightest (best) and loosest (worst) book by pair cost.
    best_book: Optional[Dict] = None
    worst_book: Optional[Dict] = None
    if two_legged:
        best = min(two_legged, key=lambda p: p.pair_cost)
        worst = max(two_legged, key=lambda p: p.pair_cost)
        best_book = {"market_id": best.market_id, "pair_cost": round(best.pair_cost, 4)}
        worst_book = {"market_id": worst.market_id, "pair_cost": round(worst.pair_cost, 4)}

    # Nearest-to-lock: the open book with the smallest remaining spread to 1.00.
    nearest_to_lock: Optional[Dict] = None
    open_books = [p for p in two_legged if not p.is_profit_locked]
    if open_books:
        near = min(open_books, key=lambda p: p.pair_cost)
        nearest_to_lock = {
            "market_id": near.market_id,
            "pair_cost": round(near.pair_cost, 4),
            "spread_to_lock": round(max(0.0, near.pair_cost - 1.0), 4),
        }

    # Concentration: largest single book as a share of total exposure.
    concentration = 0.0
    if total_exposure > 0:
        largest = max((p.cost_yes + p.cost_no) for p in positions)
        concentration = largest / total_exposure

    return {
        "return_on_exposure": round(return_on_exposure, 4),
        "avg_pair_cost": round(avg_pair_cost, 4),
        "concentration": round(concentration, 4),
        "best_book": best_book,
        "worst_book": worst_book,
        "nearest_to_lock": nearest_to_lock,
        "total_exposure": round(total_exposure, 2),
        "total_locked_profit": round(total_locked_profit, 2),
    }
