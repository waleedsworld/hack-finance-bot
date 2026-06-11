"""Tests for the pair-cost engine (MarketPosition)."""
import pytest

from core.pair_cost_engine import MarketPosition


def test_empty_position_defaults(empty_position):
    assert empty_position.qty_yes == 0.0
    assert empty_position.qty_no == 0.0
    # With no shares, average cost defaults to 1.0 (worst case).
    assert empty_position.avg_yes == 1.0
    assert empty_position.avg_no == 1.0
    assert empty_position.pair_cost == 2.0


def test_avg_yes_after_buys():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.40, 100)
    pos.record_buy("YES", 0.60, 100)
    # 100*0.40 + 100*0.60 = 100 over 200 shares => 0.50
    assert pos.avg_yes == pytest.approx(0.50)


def test_avg_no_after_buys():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("NO", 0.30, 50)
    assert pos.avg_no == pytest.approx(0.30)
    assert pos.cost_no == pytest.approx(15.0)


def test_pair_cost_is_sum_of_averages():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.48, 10)
    pos.record_buy("NO", 0.47, 10)
    assert pos.pair_cost == pytest.approx(0.95)


def test_record_buy_accumulates_qty_and_cost():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.50, 20)
    pos.record_buy("YES", 0.50, 30)
    assert pos.qty_yes == pytest.approx(50)
    assert pos.cost_yes == pytest.approx(25.0)


def test_simulate_buy_does_not_mutate_state():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.50, 100)
    before_qty = pos.qty_yes
    before_cost = pos.cost_yes
    pos.simulate_buy("YES", 0.10, 100)
    assert pos.qty_yes == before_qty
    assert pos.cost_yes == before_cost


def test_simulate_buy_yes_returns_expected_pair_cost():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.50, 100)
    pos.record_buy("NO", 0.40, 100)
    # Buying 100 more YES at 0.30: new avg_yes = (50 + 30) / 200 = 0.40
    # pair cost = 0.40 (new yes) + 0.40 (existing no) = 0.80
    simulated = pos.simulate_buy("YES", 0.30, 100)
    assert simulated == pytest.approx(0.80)


def test_simulate_buy_no_returns_expected_pair_cost():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.50, 100)
    pos.record_buy("NO", 0.50, 100)
    # Buying 100 more NO at 0.30: new avg_no = (50 + 30)/200 = 0.40
    # pair cost = existing avg_yes 0.50 + 0.40 = 0.90
    simulated = pos.simulate_buy("NO", 0.30, 100)
    assert simulated == pytest.approx(0.90)


def test_is_profit_locked_false_without_both_sides():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.10, 100)
    assert pos.is_profit_locked is False


def test_is_profit_locked_true(locked_position):
    assert locked_position.is_profit_locked is True


def test_locked_profit_amount(locked_position):
    # payout = min(100, 100) = 100, spent = 45 + 45 = 90 => 10
    assert locked_position.locked_profit == pytest.approx(10.0)


def test_not_locked_when_pair_cost_above_one():
    pos = MarketPosition(market_id="M1")
    pos.record_buy("YES", 0.60, 100)
    pos.record_buy("NO", 0.55, 100)
    assert pos.is_profit_locked is False
    assert pos.locked_profit < 0
