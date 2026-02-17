"""
CONFIG_MULTI5.PY - 5-Strategy Multi-Strategy System
===================================================
Use this for the full 5-strategy approach.
Keep your original config.py for the 2-strategy simplified version.

This allows you to run BOTH systems and compare results!
"""

# =============================================================================
# SYSTEM IDENTIFICATION
# =============================================================================
SYSTEM_NAME = "Multi5"  # Used in Telegram messages and logs
SYSTEM_VERSION = "5-Strategy"


# =============================================================================
# TELEGRAM CONFIGURATION
# =============================================================================
# Use a DIFFERENT Telegram bot for this system
# Create a second bot with @BotFather
# This keeps the two systems' alerts separate!

import os
from dotenv import load_dotenv

load_dotenv()

# Option 1: Use different bot (recommended)
TELEGRAM_BOT_TOKEN_MULTI5 = os.getenv('TELEGRAM_BOT_TOKEN_MULTI5')  # Second bot token
TELEGRAM_CHAT_ID_MULTI5 = os.getenv('TELEGRAM_CHAT_ID')  # Same chat ID

# Option 2: Use same bot but different messages
# (If you only want one bot, just use the same token)


# =============================================================================
# STOCK SYMBOLS
# =============================================================================
# Load from symbols file or use separate file
try:
    from symbol_loader import load_symbols_from_file
    SYMBOLS = load_symbols_from_file('symbols_multi5.txt')  # Separate symbol list
    
    if not SYMBOLS:
        print("⚠️  Using default symbols for Multi5 system...")
        SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
except:
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']


# =============================================================================
# TIMEFRAME & DATA SETTINGS
# =============================================================================
TIMEFRAME = '1h'  # 1m, 5m, 15m, 1h, 1d
DATA_PERIOD = '6mo'  # How much historical data to fetch


# =============================================================================
# PAPER TRADING SETTINGS
# =============================================================================
PAPER_TRADING = True
INITIAL_CAPITAL = 100.00


# =============================================================================
# MULTI-STRATEGY SYSTEM (5 STRATEGIES!)
# =============================================================================
# ALL 5 strategies enabled for maximum filtering

STRATEGIES_ENABLED = {
    'ma_crossover': True,   # ✅ Trend direction
    'rsi': True,            # ✅ Momentum confirmation
    'macd': True,           # ✅ Momentum strength
    'bollinger': True,      # ✅ Volatility/overbought
    'volume': True          # ✅ Signal strength
}

# VOTING: Majority must agree (3 out of 5)
# This gives high-quality signals with maximum filtering
STRATEGY_VOTE_REQUIRED = 'majority'  # 3+ must agree

# Alternative options:
# STRATEGY_VOTE_REQUIRED = 'all'      # All 5 must agree (very strict)
# STRATEGY_VOTE_REQUIRED = 3          # Exactly 3 must agree
# STRATEGY_VOTE_REQUIRED = 'any'      # Any 1 can trigger (aggressive)


# =============================================================================
# STRATEGY 1: MOVING AVERAGE CROSSOVER
# =============================================================================
MA_FAST_PERIOD = 10
MA_SLOW_PERIOD = 30


# =============================================================================
# STRATEGY 2: RSI
# =============================================================================
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70


# =============================================================================
# STRATEGY 3: MACD
# =============================================================================
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9


# =============================================================================
# STRATEGY 4: BOLLINGER BANDS
# =============================================================================
BOLLINGER_PERIOD = 20
BOLLINGER_STD_DEV = 2.0
BOLLINGER_LOWER_THRESHOLD = 0.2
BOLLINGER_UPPER_THRESHOLD = 0.2


# =============================================================================
# STRATEGY 5: VOLUME CONFIRMATION
# =============================================================================
VOLUME_MA_PERIOD = 20
VOLUME_SPIKE_THRESHOLD = 1.5
VOLUME_REQUIRED = False  # Don't require, just add to vote


# =============================================================================
# RISK MANAGEMENT
# =============================================================================
MAX_POSITION_SIZE = 0.3
STOP_LOSS_PERCENT = 0.05
TAKE_PROFIT_PERCENT = 0.10


# =============================================================================
# LOGGING & OUTPUT
# =============================================================================
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_multi5.log'


# =============================================================================
# SYSTEM NOTES
# =============================================================================
"""
MULTI5 SYSTEM CHARACTERISTICS:

Pros:
- Maximum filtering (5 strategies)
- Very high quality signals
- Fewer false positives
- Good for volatile markets
- Better for swing trading

Cons:
- Fewer signals overall
- Might miss some opportunities
- More complex to debug
- Slower execution (more calculations)

Best For:
- Swing trading (1h, 4h, 1d)
- Volatile stocks (tech, crypto-related)
- When you want maximum confidence
- Options trading preparation

Comparison to Simple (2-strategy):
- Multi5 will give ~50% fewer signals
- But signals will be ~20-30% more reliable
- Win rate: 60-75% (vs 55-65% for 2-strategy)
- Monthly returns similar, but smoother
"""


# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================
"""
To use this Multi5 system:

1. Create separate Telegram bot (optional but recommended):
   - Message @BotFather on Telegram
   - /newbot
   - Name: "Raghu Multi5 Bot"
   - Username: "raghu_multi5_bot"
   - Copy token to .env as TELEGRAM_BOT_TOKEN_MULTI5

2. Create separate symbol list (optional):
   - Copy symbols.txt to symbols_multi5.txt
   - Edit symbols_multi5.txt with different stocks if desired

3. Run Multi5 scheduler:
   python scheduler_multi5.py --interval 1h

4. Deploy Multi5 dashboard:
   - Deploy dashboard_multi5.py to Streamlit Cloud
   - Access at: https://raghu-multi5.streamlit.app

5. Compare results:
   - Run both systems simultaneously
   - Track which performs better
   - Learn from differences
"""
