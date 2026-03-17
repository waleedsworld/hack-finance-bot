import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Kalshi API
    KALSHI_API_KEY = os.getenv('KALSHI_API_KEY', '')
    KALSHI_API_SECRET = os.getenv('KALSHI_API_SECRET', '')
    KALSHI_BASE_URL = os.getenv('KALSHI_BASE_URL', 'https://trading-api.kalshi.com/trade-api/v2')
    
    # Polymarket API
    POLYMARKET_PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY', '')
    POLYMARKET_RPC_URL = os.getenv('POLYMARKET_RPC_URL', 'https://polygon-rpc.com')
    POLYMARKET_CLOB_URL = os.getenv('POLYMARKET_CLOB_URL', 'https://clob.polymarket.com')
    
    # Trading Parameters
    SAFETY_MARGIN = float(os.getenv('SAFETY_MARGIN', '0.99'))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '1000'))
    BALANCE_THRESHOLD = float(os.getenv('BALANCE_THRESHOLD', '0.20'))
    SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', '60'))
    MIN_PROFIT_THRESHOLD = float(os.getenv('MIN_PROFIT_THRESHOLD', '10'))
    
    # Risk Management
    MAX_TOTAL_EXPOSURE = float(os.getenv('MAX_TOTAL_EXPOSURE', '5000'))
    ENABLE_AUTO_TRADING = os.getenv('ENABLE_AUTO_TRADING', 'false').lower() == 'true'
    DRY_RUN_MODE = os.getenv('DRY_RUN_MODE', 'true').lower() == 'true'
