# ============================================================
# CONFIG UPDATE - $2000 PER TRADE
# ============================================================
# Copy these lines into your config.py
# Replace the existing POSITION SIZING section
# ============================================================

# HOW POSITION SIZING WORKS:
# Alpaca gives you $100,000 paper money
# MAX_POSITION_SIZE = what % to use per trade
#
# Examples:
#   0.02 = 2%  = $2,000 per trade  ← YOU WANT THIS
#   0.05 = 5%  = $5,000 per trade
#   0.10 = 10% = $10,000 per trade
#   0.30 = 30% = $30,000 per trade (too risky!)

# ── POSITION SIZING ──────────────────────────────────────────
MAX_POSITION_SIZE = 0.02      # 2% = ~$2,000 per trade

# ── RISK MANAGEMENT ──────────────────────────────────────────
STOP_LOSS_PERCENT = 0.05      # Exit if price drops 5%  = -$100 max loss
TAKE_PROFIT_PERCENT = 0.10    # Exit if price rises 10% = +$200 target

# RISK/REWARD RATIO:
# Risk:   $2,000 × 5%  = $100 per trade
# Reward: $2,000 × 10% = $200 per trade
# Ratio: 1:2 (risking $100 to make $200) ← GOOD!

# ── PAPER TRADING ────────────────────────────────────────────
PAPER_TRADING = True          # KEEP TRUE until consistently profitable!
INITIAL_CAPITAL = 100000.00   # Alpaca paper account ($100k)

# ── WHAT $2000 PER TRADE MEANS ───────────────────────────────
# If AAPL is at $180:
#   $2,000 / $180 = 11 shares bought
#
# If NVDA is at $875:
#   $2,000 / $875 = 2 shares bought
#
# Maximum simultaneous trades:
#   $100,000 / $2,000 = 50 trades max (but you only have 16 symbols)
#   So all 16 symbols could have open trades = $32,000 max exposure
#   Remaining cash: $68,000 always available

# ── TO USE REAL MONEY LATER ──────────────────────────────────
# When you're ready for real trading (months from now):
# 1. Create Alpaca LIVE account (not paper)
# 2. Deposit real money (recommend starting with $5,000-$10,000)
# 3. Get live API keys from Alpaca dashboard
# 4. Update .env file:
#    ALPACA_BASE_URL=https://api.alpaca.markets  (remove "paper-")
#    ALPACA_API_KEY=your_LIVE_key
#    ALPACA_SECRET_KEY=your_LIVE_secret
# 5. Change MAX_POSITION_SIZE to match your real capital
#    Example: Real $5,000 account, want $200 per trade:
#    MAX_POSITION_SIZE = 0.04  (4% of $5,000 = $200)
# 6. Keep STOP_LOSS_PERCENT and TAKE_PROFIT_PERCENT the same

# ── DO NOT RUSH TO REAL MONEY ────────────────────────────────
# Paper trade for at least 3-6 months
# Must be consistently profitable
# Must understand WHY signals work
# Start real trading with small amounts ($100-500)
