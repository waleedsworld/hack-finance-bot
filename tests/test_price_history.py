"""Tests for the rolling PriceHistory TWAP/volatility helper."""
import pytest

from data.price_history import PriceHistory


def test_empty_twap_defaults_to_half():
    ph = PriceHistory()
    assert ph.yes_twap == 0.5
    assert ph.no_twap == 0.5


def test_yes_twap_is_mean_of_added_prices():
    ph = PriceHistory()
    ph.add_yes_price(0.40)
    ph.add_yes_price(0.60)
    assert ph.yes_twap == pytest.approx(0.50)


def test_no_twap_is_mean_of_added_prices():
    ph = PriceHistory()
    ph.add_no_price(0.30)
    ph.add_no_price(0.50)
    ph.add_no_price(0.40)
    assert ph.no_twap == pytest.approx(0.40)


def test_std_defaults_with_fewer_than_two_points():
    ph = PriceHistory()
    ph.add_yes_price(0.5)
    assert ph.yes_std == 0.05
    assert ph.no_std == 0.05


def test_std_computed_with_multiple_points():
    ph = PriceHistory()
    for p in (0.40, 0.50, 0.60):
        ph.add_yes_price(p)
    assert ph.yes_std == pytest.approx(0.1)


def test_prune_drops_expired_prices():
    ph = PriceHistory(window_seconds=300)
    # Inject a stale entry directly outside the window.
    ph.yes_prices.append((0.0, 0.99))  # timestamp epoch 0 -> way outside window
    ph.add_yes_price(0.42)  # triggers prune
    remaining = [p for _, p in ph.yes_prices]
    assert 0.99 not in remaining
    assert remaining == [0.42]
