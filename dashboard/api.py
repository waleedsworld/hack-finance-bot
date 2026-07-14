from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict
import os
import time

app = FastAPI(title="Polymarket Arbitrage Bot Dashboard")

# Track process start so the dashboard can report uptime.
_STARTED_AT = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Global state (in production, use proper state management)
position_tracker = None
trade_logger = None

def init_dashboard(tracker, logger_instance):
    """Initialize dashboard with tracker and logger."""
    global position_tracker, trade_logger
    position_tracker = tracker
    trade_logger = logger_instance

@app.get("/")
async def root():
    """Serve the dashboard UI."""
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "running", "bot": "Polymarket Arbitrage Bot"}

@app.get("/api/positions")
async def get_positions():
    """Return all active positions."""
    if not position_tracker:
        return []
    
    positions = position_tracker.get_all_positions()
    return [{
        "market_id": p.market_id,
        "qty_yes": p.qty_yes,
        "qty_no": p.qty_no,
        "cost_yes": p.cost_yes,
        "cost_no": p.cost_no,
        "avg_yes": p.avg_yes,
        "avg_no": p.avg_no,
        "pair_cost": p.pair_cost,
        "profit_locked": p.is_profit_locked,
        "locked_profit": p.locked_profit,
    } for p in positions]


@app.get("/api/stats")
async def get_stats():
    """Return overall statistics."""
    if not position_tracker:
        return {}
    
    return {
        "total_exposure": position_tracker.get_total_exposure(),
        "total_locked_profit": position_tracker.get_total_locked_profit(),
        "active_positions": len(position_tracker.get_all_positions()),
        "locked_positions": len(position_tracker.get_locked_positions()),
    }

@app.get("/api/trades/{market_id}")
async def get_trades(market_id: str):
    """Return trade history for a market."""
    if not trade_logger:
        return []
    
    return trade_logger.get_trades_for_market(market_id)


@app.get("/api/health")
async def health():
    """Lightweight liveness probe for uptime monitors and the UI status pill."""
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - _STARTED_AT, 1),
        "tracker_ready": position_tracker is not None,
        "logger_ready": trade_logger is not None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
