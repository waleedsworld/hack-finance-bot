"""Integration tests for the FastAPI dashboard endpoints."""
import pytest
from fastapi.testclient import TestClient

import dashboard.api as api
from core.position_tracker import PositionTracker
from data.trade_logger import TradeLogger


@pytest.fixture
def client_uninitialized():
    """Client with global state reset (dashboard not initialized)."""
    api.position_tracker = None
    api.trade_logger = None
    with TestClient(api.app) as c:
        yield c


@pytest.fixture
def client_initialized(tmp_path):
    """Client wired to a real tracker and logger with sample data."""
    tracker = PositionTracker()
    locked = tracker.get_position("BTC")
    locked.record_buy("YES", 0.45, 100)
    locked.record_buy("NO", 0.45, 100)

    logger = TradeLogger(db_path=str(tmp_path / "dash.db"))
    logger.log_trade("BTC", "YES", 0.45, 100)

    api.init_dashboard(tracker, logger)
    with TestClient(api.app) as c:
        yield c
    api.position_tracker = None
    api.trade_logger = None


def test_health_endpoint(client_uninitialized):
    r = client_uninitialized.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["tracker_ready"] is False
    assert body["logger_ready"] is False
    assert "uptime_seconds" in body


def test_positions_empty_when_uninitialized(client_uninitialized):
    r = client_uninitialized.get("/api/positions")
    assert r.status_code == 200
    assert r.json() == []


def test_stats_empty_when_uninitialized(client_uninitialized):
    r = client_uninitialized.get("/api/stats")
    assert r.status_code == 200
    assert r.json() == {}


def test_trades_empty_when_uninitialized(client_uninitialized):
    r = client_uninitialized.get("/api/trades/BTC")
    assert r.status_code == 200
    assert r.json() == []


def test_positions_reports_locked_position(client_initialized):
    r = client_initialized.get("/api/positions")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    p = data[0]
    assert p["market_id"] == "BTC"
    assert p["profit_locked"] is True
    assert p["locked_profit"] == pytest.approx(10.0)
    assert p["pair_cost"] == pytest.approx(0.90)


def test_stats_reports_totals(client_initialized):
    r = client_initialized.get("/api/stats")
    assert r.status_code == 200
    stats = r.json()
    assert stats["active_positions"] == 1
    assert stats["locked_positions"] == 1
    assert stats["total_exposure"] == pytest.approx(90.0)
    assert stats["total_locked_profit"] == pytest.approx(10.0)


def test_health_reports_ready_when_initialized(client_initialized):
    body = client_initialized.get("/api/health").json()
    assert body["tracker_ready"] is True
    assert body["logger_ready"] is True


def test_trades_endpoint_returns_logged_trade(client_initialized):
    r = client_initialized.get("/api/trades/BTC")
    assert r.status_code == 200
    trades = r.json()
    assert len(trades) == 1
    assert trades[0]["side"] == "YES"
    assert trades[0]["cost"] == pytest.approx(45.0)


def test_root_serves_dashboard_html(client_uninitialized):
    r = client_uninitialized.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
