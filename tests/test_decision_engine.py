"""Tests for the DecisionEngine trade approval rules."""
import pytest

from core.decision_engine import DecisionEngine
from core.pair_cost_engine import MarketPosition


@pytest.fixture
def config():
    return {
        "safety_margin": 0.99,
        "max_imbalance": 1.20,
        "min_discount": 0.03,
        "max_position_usd": 1000,
    }


@pytest.fixture
def engine(config):
    return DecisionEngine(config)


def test_defaults_used_when_config_empty():
    eng = DecisionEngine({})
    assert eng.safety_margin == 0.99
    assert eng.max_imbalance_ratio == 1.20
    assert eng.min_price_discount == 0.03
    assert eng.max_position_usd == 1000


# ---------- should_buy_yes ----------

def test_buy_yes_approved(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("NO", 0.40, 100)  # gives a real (low) avg_no
    ok, reason = engine.should_buy_yes(pos, yes_price=0.45, yes_twap=0.50, qty=100)
    assert ok is True
    assert "approved" in reason.lower()


def test_buy_yes_rejected_not_cheap(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("NO", 0.40, 100)
    # 0.49 is not <= twap(0.50) - discount(0.03) = 0.47
    ok, reason = engine.should_buy_yes(pos, yes_price=0.49, yes_twap=0.50, qty=100)
    assert ok is False
    assert "cheap" in reason.lower()


def test_buy_yes_rejected_pair_cost_too_high(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("NO", 0.60, 100)  # high avg_no
    # price cheap vs twap, but 0.45 + 0.60 = 1.05 >= safety margin
    ok, reason = engine.should_buy_yes(pos, yes_price=0.45, yes_twap=0.50, qty=100)
    assert ok is False
    assert "pair cost" in reason.lower()


def test_buy_yes_rejected_imbalance(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("YES", 0.30, 100)
    pos.record_buy("NO", 0.30, 100)
    # (100 + 50) / 100 = 1.5 > 1.20
    ok, reason = engine.should_buy_yes(pos, yes_price=0.40, yes_twap=0.50, qty=50)
    assert ok is False
    assert "imbalanced" in reason.lower()


def test_buy_yes_rejected_max_position():
    eng = DecisionEngine({"max_position_usd": 100})
    pos = MarketPosition(market_id="M")
    pos.record_buy("NO", 0.40, 100)
    # 0.45 * 1000 = 450 > max 100
    ok, reason = eng.should_buy_yes(pos, yes_price=0.45, yes_twap=0.50, qty=1000)
    assert ok is False
    assert "max position" in reason.lower()


# ---------- should_buy_no ----------

def test_buy_no_approved(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("YES", 0.40, 100)
    ok, reason = engine.should_buy_no(pos, no_price=0.45, no_twap=0.50, qty=100)
    assert ok is True
    assert "approved" in reason.lower()


def test_buy_no_rejected_not_cheap(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("YES", 0.40, 100)
    ok, reason = engine.should_buy_no(pos, no_price=0.49, no_twap=0.50, qty=100)
    assert ok is False
    assert "cheap" in reason.lower()


def test_buy_no_rejected_pair_cost_too_high(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("YES", 0.60, 100)
    ok, reason = engine.should_buy_no(pos, no_price=0.45, no_twap=0.50, qty=100)
    assert ok is False
    assert "pair cost" in reason.lower()


def test_buy_no_rejected_imbalance(engine):
    pos = MarketPosition(market_id="M")
    pos.record_buy("YES", 0.30, 100)
    pos.record_buy("NO", 0.30, 100)
    ok, reason = engine.should_buy_no(pos, no_price=0.40, no_twap=0.50, qty=50)
    assert ok is False
    assert "imbalanced" in reason.lower()
