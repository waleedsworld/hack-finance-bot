#!/usr/bin/env python3
"""
Start the Polymarket Arbitrage Bot Dashboard
"""
import asyncio
import random
import os
from datetime import datetime
from dashboard.api import app, init_dashboard
from core.position_tracker import PositionTracker
from core.pair_cost_engine import MarketPosition
from data.trade_logger import TradeLogger
import uvicorn

# Get port from environment or use default
PORT = int(os.getenv('PORT', '5108'))

# Initialize components
tracker = PositionTracker()
logger = TradeLogger()
init_dashboard(tracker, logger)

async def simulate_trading():
    """Simulate trading activity for demo"""
    print("🤖 Starting simulated trading bot...")
    
    markets = [
        "btc_up_15min_001",
        "btc_up_15min_002", 
        "btc_up_15min_003"
    ]
    
    # Create some initial positions
    for i, market_id in enumerate(markets):
        position = tracker.get_position(market_id)
        
        # Simulate different scenarios
        if i == 0:
            # Locked profit position
            position.qty_yes = 150
            position.cost_yes = 70
            position.qty_no = 150
            position.cost_no = 65
        elif i == 1:
            # Active position, not locked yet
            position.qty_yes = 100
            position.cost_yes = 52
            position.qty_no = 80
            position.cost_no = 42
        else:
            # New position just starting
            position.qty_yes = 50
            position.cost_yes = 24
            position.qty_no = 50
            position.cost_no = 23
    
    print(f"✅ Created {len(markets)} demo positions")
    print(f"   - Total exposure: ${tracker.get_total_exposure():.2f}")
    print(f"   - Locked profit: ${tracker.get_total_locked_profit():.2f}")
    
    # Keep updating positions
    while True:
        await asyncio.sleep(10)
        
        # Randomly update a position
        market_id = random.choice(markets)
        position = tracker.get_position(market_id)
        
        if not position.is_profit_locked:
            # Add small amounts, and log the fill so the trade blotter /
            # CSV export reflect the simulated activity.
            qty = 10
            if random.random() > 0.5:
                cost = random.uniform(4, 5)
                position.qty_yes += qty
                position.cost_yes += cost
                logger.log_trade(market_id, "YES", cost / qty, qty)
            else:
                cost = random.uniform(4, 5)
                position.qty_no += qty
                position.cost_no += cost
                logger.log_trade(market_id, "NO", cost / qty, qty)

            print(f"📊 Updated {market_id[:15]}... - Pair cost: {position.pair_cost:.4f}")

def run_dashboard():
    """Run the dashboard server"""
    print("=" * 70)
    print("🚀 POLYMARKET + KALSHI ARBITRAGE BOT DASHBOARD")
    print("=" * 70)
    print(f"\n📡 Dashboard running on port {PORT}")
    print("\n✨ Features:")
    print("   - Real-time position tracking")
    print("   - Portfolio health analytics (/api/analytics)")
    print("   - One-click trade blotter CSV export (/api/trades.csv)")
    print("   - Live profit calculations")
    print("\n⌨️  Press Ctrl+C to stop\n")
    
    # Start background task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(simulate_trading())
    
    # Run server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())

if __name__ == "__main__":
    run_dashboard()
