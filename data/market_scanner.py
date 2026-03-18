from typing import List, Dict
from loguru import logger

class MarketScanner:
    """Scans for active markets on Polymarket."""
    
    def __init__(self, poly_client):
        self.poly_client = poly_client
        self.active_markets = {}
    
    async def scan_btc_markets(self) -> List[Dict]:
        """Find active 15-minute BTC markets."""
        try:
            all_markets = await self.poly_client.get_active_btc_markets()
            
            # Filter for 15-minute markets
            btc_15min = []
            for market in all_markets:
                question = market.get('question', '').lower()
                if 'bitcoin' in question or 'btc' in question:
                    if '15' in question or 'fifteen' in question:
                        btc_15min.append(market)
            
            logger.info(f"Found {len(btc_15min)} active 15-min BTC markets")
            return btc_15min
            
        except Exception as e:
            logger.error(f"Error scanning markets: {e}")
            return []
    
    async def get_market_details(self, market_id: str) -> Dict:
        """Get detailed info for a specific market."""
        try:
            # In a real implementation, would fetch from API
            return self.active_markets.get(market_id, {})
        except Exception as e:
            logger.error(f"Error fetching market details: {e}")
            return {}
    
    def is_market_active(self, market: Dict) -> bool:
        """Check if market is still active and tradeable."""
        # Check if market has ended
        end_date = market.get('end_date_iso')
        if not end_date:
            return True
        
        import time
        return time.time() < end_date
