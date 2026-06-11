"""Tests for the SQLite-backed TradeLogger."""
import pytest

from data.trade_logger import TradeLogger
from core.pair_cost_engine import MarketPosition


@pytest.fixture
def logger(tmp_path):
    db = tmp_path / "trades_test.db"
    return TradeLogger(db_path=str(db))


def test_init_creates_tables(logger):
    import sqlite3
    conn = sqlite3.connect(logger.db_path)
    names = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()
    assert "trades" in names
    assert "positions" in names


def test_log_trade_and_read_back(logger):
    logger.log_trade("BTC", "YES", 0.45, 100, exchange="polymarket")
    trades = logger.get_trades_for_market("BTC")
    assert len(trades) == 1
    t = trades[0]
    assert t["side"] == "YES"
    assert t["price"] == pytest.approx(0.45)
    assert t["quantity"] == pytest.approx(100)
    assert t["cost"] == pytest.approx(45.0)
    assert t["exchange"] == "polymarket"


def test_default_exchange(logger):
    logger.log_trade("BTC", "NO", 0.30, 10)
    trades = logger.get_trades_for_market("BTC")
    assert trades[0]["exchange"] == "polymarket"


def test_trades_isolated_by_market(logger):
    logger.log_trade("BTC", "YES", 0.45, 100)
    logger.log_trade("ETH", "NO", 0.55, 50)
    assert len(logger.get_trades_for_market("BTC")) == 1
    assert len(logger.get_trades_for_market("ETH")) == 1
    assert logger.get_trades_for_market("DOGE") == []


def test_trades_returned_in_timestamp_order(logger):
    logger.log_trade("BTC", "YES", 0.10, 1)
    logger.log_trade("BTC", "YES", 0.20, 1)
    trades = logger.get_trades_for_market("BTC")
    assert [t["price"] for t in trades] == [0.10, 0.20]


def test_update_position_upserts(logger):
    pos = MarketPosition(market_id="BTC")
    pos.record_buy("YES", 0.45, 100)
    pos.record_buy("NO", 0.45, 100)
    logger.update_position(pos)

    import sqlite3
    conn = sqlite3.connect(logger.db_path)
    row = conn.execute(
        "SELECT market_id, qty_yes, qty_no, locked_profit FROM positions WHERE market_id=?",
        ("BTC",),
    ).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "BTC"
    assert row[1] == pytest.approx(100)
    assert row[3] == pytest.approx(10.0)

    # Second update on same market must replace, not duplicate.
    pos.record_buy("YES", 0.45, 100)
    logger.update_position(pos)
    conn = sqlite3.connect(logger.db_path)
    count = conn.execute(
        "SELECT COUNT(*) FROM positions WHERE market_id=?", ("BTC",)
    ).fetchone()[0]
    conn.close()
    assert count == 1
