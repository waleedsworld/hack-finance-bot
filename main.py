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

    while True:
        try:
            # 1. Scan for active BTC markets
            markets = await poly_client.get_active_btc_markets()
            logger.info(f"Found {len(markets)} active BTC markets")
            
            # 2. Process each market
            for market in markets:
                market_id = market.get('id')
                
                if market_id not in positions:
                    positions[market_id] = {
                        'position': MarketPosition(market_id=market_id),
                        'history': PriceHistory()
                    }
                
                pos_data = positions[market_id]
                position = pos_data['position']
                history = pos_data['history']
                
                # Get current prices
                yes_token = market.get('tokens', [{}])[0].get('token_id')
                no_token = market.get('tokens', [{}])[1].get('token_id') if len(market.get('tokens', [])) > 1 else None
                
                if yes_token and no_token:
                    yes_price = await poly_client.get_price(yes_token)
                    no_price = await poly_client.get_price(no_token)
                    
                    if yes_price and no_price:
                        history.add_yes_price(yes_price)
                        history.add_no_price(no_price)
                        
                        logger.info(f"Market {market_id[:8]}: YES=${yes_price:.4f} NO=${no_price:.4f} pair_cost={position.pair_cost:.4f}")

                        # Check if profit is already locked
                        if position.is_profit_locked:
                            logger.success(f"💰 Profit locked: ${position.locked_profit:.2f}")
                            continue
                        
                        # Evaluate YES buy
                        qty = config['pair_cost_strategy']['base_lot_size']
                        should_buy_yes, reason_yes = decision_engine.should_buy_yes(
                            position, yes_price, history.yes_twap, qty
                        )
                        
                        if should_buy_yes:
                            logger.info(f"✅ BUY YES: {reason_yes}")
                            await poly_client.place_order("BUY", yes_price, qty, yes_token)
                            position.record_buy("YES", yes_price, qty)
                        
                        # Evaluate NO buy
                        should_buy_no, reason_no = decision_engine.should_buy_no(
                            position, no_price, history.no_twap, qty
                        )
                        
                        if should_buy_no:
                            logger.info(f"✅ BUY NO: {reason_no}")
                            await poly_client.place_order("BUY", no_price, qty, no_token)
                            position.record_buy("NO", no_price, qty)
            
            # Sleep before next cycle
            await asyncio.sleep(config['pair_cost_strategy']['scan_interval_seconds'])
            
        except Exception as e:
            logger.error(f"⚠️ Error in main loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
