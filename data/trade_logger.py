import sqlite3
import time
from typing import List, Dict
from datetime import datetime

class TradeLogger:
    """Logs all trades to SQLite database."""
    
    def __init__(self, db_path="trades.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                market_id TEXT,
                side TEXT,
                price REAL,
                quantity REAL,
                cost REAL,
                exchange TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                market_id TEXT PRIMARY KEY,
                qty_yes REAL,
                qty_no REAL,
                cost_yes REAL,
                cost_no REAL,
                pair_cost REAL,
                profit_locked BOOLEAN,
                locked_profit REAL,
                updated_at REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_trade(self, market_id: str, side: str, price: float, 
                  quantity: float, exchange: str = "polymarket"):
        """Log a single trade."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades (timestamp, market_id, side, price, quantity, cost, exchange)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (time.time(), market_id, side, price, quantity, price * quantity, exchange))
        
        conn.commit()
        conn.close()

    def update_position(self, position):
        """Update position snapshot in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO positions 
            (market_id, qty_yes, qty_no, cost_yes, cost_no, pair_cost, 
             profit_locked, locked_profit, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            position.market_id,
            position.qty_yes,
            position.qty_no,
            position.cost_yes,
            position.cost_no,
            position.pair_cost,
            position.is_profit_locked,
            position.locked_profit,
            time.time()
        ))
        
        conn.commit()
        conn.close()
    
    def get_trades_for_market(self, market_id: str) -> List[Dict]:
        """Get all trades for a specific market."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, side, price, quantity, cost, exchange
            FROM trades WHERE market_id = ?
            ORDER BY timestamp
        """, (market_id,))
        
        trades = []
        for row in cursor.fetchall():
            trades.append({
                "timestamp": row[0],
                "side": row[1],
                "price": row[2],
                "quantity": row[3],
                "cost": row[4],
                "exchange": row[5]
            })
        
        conn.close()
        return trades

    def get_all_trades(self, limit: int = 500) -> List[Dict]:
        """Get the most recent trades across every market (newest first).

        Powers both the recent-activity feed and the CSV export in the
        dashboard; `limit` keeps the payload bounded on a long-running desk.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, market_id, side, price, quantity, cost, exchange
            FROM trades
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        trades = []
        for row in cursor.fetchall():
            trades.append({
                "timestamp": row[0],
                "market_id": row[1],
                "side": row[2],
                "price": row[3],
                "quantity": row[4],
                "cost": row[5],
                "exchange": row[6]
            })

        conn.close()
        return trades
