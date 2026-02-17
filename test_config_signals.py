# QUICK TEST CONFIG - COPY THIS SECTION TO YOUR config.py
# ========================================================
# This configuration will give you signals for TESTING
# Once you see signals working, switch back to stricter settings
# ========================================================

# STEP 1: Find these lines in your config.py and REPLACE them

# STRATEGIES - Use only 2 for simplicity
STRATEGIES_ENABLED = {
    'ma_crossover': True,   # Trend direction
    'rsi': True,            # Timing
    'macd': False,          # Disable
    'bollinger': False,     # Disable
    'volume': False         # Disable
}

# VOTING - For testing, use 'any' to see more signals
# After confirming it works, change to 'all' for quality
STRATEGY_VOTE_REQUIRED = 'any'  # TEMPORARY - Any strategy can trigger signal

# PERIOD - Use shorter period for intraday data
PERIOD = '2mo'  # 2 months - works well

# MA PERIODS - More sensitive for testing
MA_FAST_PERIOD = 5   # Faster (more signals)
MA_SLOW_PERIOD = 20  # Shorter (more signals)

# RSI - Standard
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# RISK MANAGEMENT
STOP_LOSS_PERCENT = 0.05      # 5% stop loss
TAKE_PROFIT_PERCENT = 0.10    # 10% take profit
MAX_POSITION_SIZE = 0.3       # 30% per trade

# PAPER TRADING
PAPER_TRADING = True
INITIAL_CAPITAL = 100.00


# ========================================================
# AFTER YOU SEE SIGNALS WORKING:
# ========================================================
# Change these back for quality trading:
# 
# STRATEGY_VOTE_REQUIRED = 'all'  # Both must agree
# MA_FAST_PERIOD = 10
# MA_SLOW_PERIOD = 30
# ========================================================
