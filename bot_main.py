#!/usr/bin/env python3
"""
Polymarket + Kalshi Profit-Locking Arbitrage Bot
Complete implementation with all strategies
"""
import asyncio
import os
import sys
import yaml
from dotenv import load_dotenv
from loguru import logger

# Core components
from core.pair_cost_engine import MarketPosition
from core.decision_engine import DecisionEngine
from core.position_tracker import PositionTracker

# Exchange clients
from exchanges.polymarket_client import PolymarketClient
from exchanges.kalshi_client import KalshiClient

# Strategies
from strategies.intra_market_arb import IntraMarketArbStrategy
from strategies.cross_platform_arb import CrossPlatformArbStrategy

# Data & Risk
from data.price_history import PriceHistory
from data.trade_logger import TradeLogger
from data.market_scanner import MarketScanner
from risk.circuit_breaker import CircuitBreaker

# Alerts
from alerts.telegram_alerts import TelegramAlerter

load_dotenv()

async def main():
    """Main bot loop."""
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config.yaml not found!")
        sys.exit(1)
    
    logger.info("🤖 Polymarket + Kalshi Arbitrage Bot Starting...")
    logger.info("=" * 50)
    
    # Check paper trade mode
    paper_trade = os.getenv("PAPER_TRADE", "true").lower() == "true"
    if paper_trade:
        logger.warning("📄 PAPER TRADING MODE - No real orders will be placed")
    else:
        logger.warning("💰 LIVE TRADING MODE - Real money at risk!")
        logger.warning("Waiting 5 seconds... Press Ctrl+C to cancel")
        await asyncio.sleep(5)

    # Initialize clients
    logger.info("Initializing exchange clients...")
    poly_client = PolymarketClient()
    kalshi_client = KalshiClient()
    
    await poly_client.initialize()
    await kalshi_client.initialize()
    
    # Initialize components
    logger.info("Initializing bot components...")
    position_tracker = PositionTracker()
    trade_logger = TradeLogger()
    market_scanner = MarketScanner(poly_client)
    alerter = TelegramAlerter()
    circuit_breaker = CircuitBreaker(config['risk']['max_loss_per_day_usd'])
    
    # Initialize strategies
    decision_engine = DecisionEngine(config['pair_cost_strategy'])
    intra_arb = IntraMarketArbStrategy(poly_client, decision_engine, config['pair_cost_strategy'])
    cross_arb = CrossPlatformArbStrategy(poly_client, kalshi_client, config['cross_platform_arb'])
    
    await alerter.send("🤖 Bot started and scanning markets...")
    
    logger.success("✅ All components initialized")
    logger.info("=" * 50)
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            logger.info(f"\n--- Cycle {cycle_count} ---")
            
            # Check circuit breaker
            if not circuit_breaker.can_trade():
                logger.error("🚨 Circuit breaker tripped - trading halted")
                await alerter.send_error("Circuit breaker tripped - daily loss limit reached")
                await asyncio.sleep(3600)  # Wait 1 hour
                continue

            # 1. Scan for active BTC markets
            markets = await market_scanner.scan_btc_markets()
            
            if not markets:
                logger.info("No active markets found, waiting...")
                await asyncio.sleep(config['pair_cost_strategy']['scan_interval_seconds'])
                continue
            
            # 2. Run intra-market pair cost strategy
            for market in markets:
                market_id = market.get('id')
                if not market_id:
                    continue
                
                position = position_tracker.get_position(market_id)
                
                try:
                    await intra_arb.run_cycle(market, position)
                    
                    # Check if profit just locked
                    if position.is_profit_locked:
                        logger.success(f"💰 Profit locked: ${position.locked_profit:.2f}")
                        await alerter.send_profit_locked(market_id, position.locked_profit)
                    
                    # Log position to database
                    trade_logger.update_position(position)
                    
                except Exception as e:
                    logger.error(f"Error processing market {market_id[:8]}: {e}")
            
            # 3. Run cross-platform arbitrage scan
            try:
                await cross_arb.run_cycle()
            except Exception as e:
                logger.error(f"Error in cross-platform scan: {e}")
            
            # 4. Log statistics
            total_exposure = position_tracker.get_total_exposure()
            total_profit = position_tracker.get_total_locked_profit()
            active_count = len(position_tracker.get_all_positions())
            locked_count = len(position_tracker.get_locked_positions())
            
            logger.info(
                f"Stats: {active_count} active positions, "
                f"{locked_count} locked, "
                f"${total_exposure:.2f} exposure, "
                f"${total_profit:.2f} profit"
            )

            # Sleep before next cycle
            scan_interval = config['pair_cost_strategy']['scan_interval_seconds']
            await asyncio.sleep(scan_interval)
            
        except KeyboardInterrupt:
            logger.info("\n\nBot stopped by user")
            await alerter.send("🛑 Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"⚠️ Error in main loop: {e}")
            await alerter.send_error(f"Main loop error: {str(e)}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nShutdown complete")
        sys.exit(0)
