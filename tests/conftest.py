"""Shared pytest fixtures and path setup for the test suite."""
import os
import sys

# Ensure the project root is importable when tests run from any CWD.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

from core.pair_cost_engine import MarketPosition
from core.position_tracker import PositionTracker


@pytest.fixture
def empty_position():
    """A fresh market position with no shares held."""
    return MarketPosition(market_id="BTC-15MIN")


@pytest.fixture
def locked_position():
    """A position where profit is mathematically locked.

    100 YES bought at 0.45 and 100 NO bought at 0.45 => total spent 90,
    guaranteed payout 100, so 10 of locked profit.
    """
    pos = MarketPosition(market_id="BTC-LOCKED")
    pos.record_buy("YES", 0.45, 100)
    pos.record_buy("NO", 0.45, 100)
    return pos


@pytest.fixture
def tracker():
    """An empty position tracker."""
    return PositionTracker()
