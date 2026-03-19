# Hack Finance Bot

A cryptocurrency trading bot with automated decision-making and position tracking capabilities.

## Features

- Automated trading decisions based on market analysis
- Position tracking and management
- Real-time market scanning
- Trade logging and history
- Dashboard API for monitoring

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
TELEGRAM_BOT_TOKEN=your_token_here
GROQ_API_KEY=your_groq_key_here
```

3. Run the bot:
```bash
python start.py
```

## Project Structure

- `start.py` - Main entry point
- `bot_main.py` - Bot logic
- `main.py` - Core application
- `config.py` - Configuration management
- `core/` - Trading decision engine and position tracking
- `data/` - Market data and trade logging
- `dashboard/` - API endpoints for monitoring
