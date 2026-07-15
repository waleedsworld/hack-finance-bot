"""
Main entry point for the Polymarket + Kalshi Arbitrage Bot.
Run this file to start the bot.
"""
import sys
import argparse
from config import Config
from bot import ArbitrageBot

def main():
    parser = argparse.ArgumentParser(
        description="Automated Polymarket + Kalshi Profit-Locking Arbitrage Bot"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live trading (default: dry-run mode)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Scan interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--safety-margin",
        type=float,
        default=0.99,
        help="Safety margin for pair cost (default: 0.99)"
    )
    
    args = parser.parse_args()
    
    # Override config with command-line arguments
    config = Config()
    if args.live:
        config.DRY_RUN_MODE = False
        config.ENABLE_AUTO_TRADING = True
        print("⚠️  WARNING: LIVE TRADING MODE ENABLED")
        print("Press Ctrl+C within 5 seconds to cancel...")
        import time
        time.sleep(5)
    
    config.SCAN_INTERVAL = args.interval
    config.SAFETY_MARGIN = args.safety_margin
    
    # Create and run bot
    bot = ArbitrageBot(config)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
