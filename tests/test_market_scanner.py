"""Tests for the MarketScanner filtering and liveness helpers.

Async coroutines are driven with ``asyncio.run`` so the suite needs no
extra pytest plugins.
"""
import asyncio
import time

from data.market_scanner import MarketScanner


class FakeClient:
    """Minimal stand-in for the Polymarket client."""

    def __init__(self, markets=None, raise_error=False):
        self._markets = markets or []
        self._raise = raise_error

    async def get_active_btc_markets(self):
        if self._raise:
            raise RuntimeError("boom")
        return self._markets


def test_scan_filters_btc_15min_markets():
    markets = [
        {"question": "Will Bitcoin go up in the next 15 minutes?"},
        {"question": "Will BTC be higher in 15 min?"},
        {"question": "Will Ethereum go up in 15 minutes?"},  # not BTC
        {"question": "Will Bitcoin close green today?"},  # BTC but no 15
    ]
    scanner = MarketScanner(FakeClient(markets))
    result = asyncio.run(scanner.scan_btc_markets())
    assert len(result) == 2


def test_scan_handles_client_error_gracefully():
    scanner = MarketScanner(FakeClient(raise_error=True))
    result = asyncio.run(scanner.scan_btc_markets())
    assert result == []


def test_scan_empty_market_list():
    scanner = MarketScanner(FakeClient([]))
    assert asyncio.run(scanner.scan_btc_markets()) == []


def test_get_market_details_returns_cached_entry():
    scanner = MarketScanner(FakeClient())
    scanner.active_markets["m1"] = {"question": "hello"}
    details = asyncio.run(scanner.get_market_details("m1"))
    assert details == {"question": "hello"}
    assert asyncio.run(scanner.get_market_details("missing")) == {}


def test_is_market_active_without_end_date():
    scanner = MarketScanner(FakeClient())
    assert scanner.is_market_active({}) is True


def test_is_market_active_future_and_past():
    scanner = MarketScanner(FakeClient())
    assert scanner.is_market_active({"end_date_iso": time.time() + 1000}) is True
    assert scanner.is_market_active({"end_date_iso": time.time() - 1000}) is False
