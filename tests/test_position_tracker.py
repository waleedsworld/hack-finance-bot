"""Tests for the PositionTracker aggregation logic."""
import pytest

from core.pair_cost_engine import MarketPosition


def test_get_position_creates_and_caches(tracker):
    p1 = tracker.get_position("BTC")
    p2 = tracker.get_position("BTC")
    assert isinstance(p1, MarketPosition)
    assert p1 is p2  # same instance returned on repeat access
    assert p1.market_id == "BTC"


def test_get_all_positions(tracker):
    tracker.get_position("A")
    tracker.get_position("B")
    all_positions = tracker.get_all_positions()
    assert len(all_positions) == 2
    assert {p.market_id for p in all_positions} == {"A", "B"}


def test_total_exposure_sums_costs(tracker):
    a = tracker.get_position("A")
    a.record_buy("YES", 0.50, 100)  # cost 50
    b = tracker.get_position("B")
    b.record_buy("NO", 0.40, 50)  # cost 20
    assert tracker.get_total_exposure() == pytest.approx(70.0)


def test_total_exposure_empty(tracker):
    assert tracker.get_total_exposure() == 0.0


def test_locked_profit_only_counts_locked_positions(tracker):
    locked = tracker.get_position("LOCKED")
    locked.record_buy("YES", 0.45, 100)
    locked.record_buy("NO", 0.45, 100)  # locked profit 10

    unlocked = tracker.get_position("UNLOCKED")
    unlocked.record_buy("YES", 0.60, 100)
    unlocked.record_buy("NO", 0.55, 100)  # negative, not locked

    assert tracker.get_total_locked_profit() == pytest.approx(10.0)
    locked_list = tracker.get_locked_positions()
    assert len(locked_list) == 1
    assert locked_list[0].market_id == "LOCKED"
