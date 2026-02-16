"""
CONFIG.PY - Configuration File
===============================
This file stores all the settings for our trading bot.
Think of it as the "settings menu" of your bot.
"""

# TRADING SETTINGS
# ================
# Initial capital: How much money you're starting with
INITIAL_CAPITAL = 100.00

# STOCK SYMBOLS BY SECTOR
# =======================
# Organized by industry sectors for diversified trading
# You can select specific sectors or mix them

# TECHNOLOGY / IT (Top 20)
TECH_SYMBOLS = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google/Alphabet
    'META',   # Meta/Facebook
    'NVDA',   # NVIDIA
    'AMD',    # Advanced Micro Devices
    'INTC',   # Intel
    'CRM',    # Salesforce
    'ORCL',   # Oracle
    'ADBE',   # Adobe
    'CSCO',   # Cisco
    'AVGO',   # Broadcom
    'QCOM',   # Qualcomm
    'IBM',    # IBM
    'NOW',    # ServiceNow
    'INTU',   # Intuit
    'TXN',    # Texas Instruments
    'AMAT',   # Applied Materials
    'LRCX',   # Lam Research
    'KLAC'    # KLA Corporation
]

# SEMICONDUCTORS / CHIPS (Top 20)
CHIP_SYMBOLS = [
    'NVDA',   # NVIDIA
    'AMD',    # Advanced Micro Devices
    'INTC',   # Intel
    'TSM',    # Taiwan Semiconductor
    'AVGO',   # Broadcom
    'QCOM',   # Qualcomm
    'TXN',    # Texas Instruments
    'AMAT',   # Applied Materials
    'LRCX',   # Lam Research
    'KLAC',   # KLA Corporation
    'MU',     # Micron Technology
    'MCHP',   # Microchip Technology
    'ADI',    # Analog Devices
    'NXPI',   # NXP Semiconductors
    'ON',     # ON Semiconductor
    'SWKS',   # Skyworks Solutions
    'MPWR',   # Monolithic Power Systems
    'MRVL',   # Marvell Technology
    'ARM',    # ARM Holdings
    'ASML'    # ASML Holding
]

# HEALTHCARE (Top 20)
HEALTHCARE_SYMBOLS = [
    'UNH',    # UnitedHealth Group
    'JNJ',    # Johnson & Johnson
    'LLY',    # Eli Lilly
    'ABBV',   # AbbVie
    'MRK',    # Merck
    'TMO',    # Thermo Fisher Scientific
    'ABT',    # Abbott Laboratories
    'DHR',    # Danaher
    'PFE',    # Pfizer
    'CVS',    # CVS Health
    'BMY',    # Bristol-Myers Squibb
    'AMGN',   # Amgen
    'GILD',   # Gilead Sciences
    'MDT',    # Medtronic
    'ISRG',   # Intuitive Surgical
    'CI',     # Cigna
    'HUM',    # Humana
    'BSX',    # Boston Scientific
    'VRTX',   # Vertex Pharmaceuticals
    'SYK'     # Stryker
]

# PHARMACEUTICALS (Top 20)
PHARMA_SYMBOLS = [
    'PFE',    # Pfizer
    'MRK',    # Merck
    'ABBV',   # AbbVie
    'LLY',    # Eli Lilly
    'BMY',    # Bristol-Myers Squibb
    'GILD',   # Gilead Sciences
    'AMGN',   # Amgen
    'AZN',    # AstraZeneca
    'NVO',    # Novo Nordisk
    'REGN',   # Regeneron Pharmaceuticals
    'BIIB',   # Biogen
    'MRNA',   # Moderna
    'VRTX',   # Vertex Pharmaceuticals
    'BNTX',   # BioNTech
    'SNY',    # Sanofi
    'GSK',    # GSK (GlaxoSmithKline)
    'TAK',    # Takeda Pharmaceutical
    'ZTS',    # Zoetis
    'VTRS',   # Viatris
    'TEVA'    # Teva Pharmaceutical
]

# FINANCIAL SERVICES (Top 20)
FINANCE_SYMBOLS = [
    'JPM',    # JPMorgan Chase
    'BAC',    # Bank of America
    'WFC',    # Wells Fargo
    'GS',     # Goldman Sachs
    'MS',     # Morgan Stanley
    'C',      # Citigroup
    'BLK',    # BlackRock
    'SCHW',   # Charles Schwab
    'USB',    # U.S. Bancorp
    'PNC',    # PNC Financial
    'TFC',    # Truist Financial
    'COF',    # Capital One
    'AXP',    # American Express
    'BK',     # Bank of New York Mellon
    'STT',    # State Street
    'SPGI',   # S&P Global
    'MCO',    # Moody's
    'ICE',    # Intercontinental Exchange
    'CME',    # CME Group
    'V'       # Visa
]

# ENERGY (Top 20)
ENERGY_SYMBOLS = [
    'XOM',    # Exxon Mobil
    'CVX',    # Chevron
    'COP',    # ConocoPhillips
    'SLB',    # Schlumberger
    'EOG',    # EOG Resources
    'MPC',    # Marathon Petroleum
    'PSX',    # Phillips 66
    'VLO',    # Valero Energy
    'OXY',    # Occidental Petroleum
    'HES',    # Hess Corporation
    'BKR',    # Baker Hughes
    'HAL',    # Halliburton
    'DVN',    # Devon Energy
    'FANG',   # Diamondback Energy
    'MRO',    # Marathon Oil
    'APA',    # APA Corporation
    'CTRA',   # Coterra Energy
    'EQT',    # EQT Corporation
    'PXD',    # Pioneer Natural Resources
    'WMB'     # Williams Companies
]

# CONSUMER / RETAIL (Top 20)
CONSUMER_SYMBOLS = [
    'AMZN',   # Amazon
    'TSLA',   # Tesla
    'WMT',    # Walmart
    'HD',     # Home Depot
    'NKE',    # Nike
    'MCD',    # McDonald's
    'SBUX',   # Starbucks
    'TGT',    # Target
    'LOW',    # Lowe's
    'COST',   # Costco
    'TJX',    # TJX Companies
    'DG',     # Dollar General
    'ROST',   # Ross Stores
    'BKNG',   # Booking Holdings
    'MAR',    # Marriott International
    'CMG',    # Chipotle Mexican Grill
    'YUM',    # Yum! Brands
    'ABNB',   # Airbnb
    'LULU',   # Lululemon
    'ULTA'    # Ulta Beauty
]

# SYMBOL SELECTION
# =============================================================================
# EASY SYMBOL MANAGEMENT!
# =============================================================================
# 
# Instead of editing this file, just edit symbols.txt!
# 
# symbols.txt format:
# - One symbol per line
# - Lines starting with # are comments
# - Simple and easy!
# 
# Example symbols.txt:
#   AAPL
#   MSFT
#   GOOGL
#   # TSLA  (commented out - disabled)
# 
# Commands:
#   python symbol_loader.py list           # Show all symbols
#   python symbol_loader.py add NVDA       # Add symbol
#   python symbol_loader.py remove AAPL    # Remove symbol
# 
# =============================================================================

# Load symbols from symbols.txt file
try:
    from symbol_loader import load_symbols_from_file
    SYMBOLS = load_symbols_from_file('symbols.txt')
    
    if not SYMBOLS:
        print("⚠️  No symbols loaded! Using default...")
        SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
except Exception as e:
    print(f"⚠️  Error loading symbols: {e}")
    print("Using default symbols...")
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']

# =============================================================================
# LEGACY: Pre-defined sector lists (still available if needed)
# =============================================================================
# You can still use these by editing symbols.txt or using them directly:
# Example: SYMBOLS = TECH_SYMBOLS[:5]
# But the easiest way is just editing symbols.txt!
# =============================================================================

# Trading timeframe: How often to check for signals
# Options: '1m', '5m', '15m', '1h', '1d'
TIMEFRAME = '1d'  # Daily candles (easier for beginners)

# Historical data period for analysis
# Options: '1d', '5d', '1mo', '3mo', '6mo', '1y'
DATA_PERIOD = '6mo'  # 6 months of historical data


# MULTI-STRATEGY SYSTEM CONFIGURATION
# ====================================
# Your bot now supports MULTIPLE strategies that work together!
# Strategies included:
# 1. Moving Average Crossover (trend direction)
# 2. RSI (momentum confirmation)
# 3. MACD (momentum and trend strength)
# 4. Bollinger Bands (volatility and overbought/oversold)
# 5. Volume Confirmation (trade strength)

# STRATEGY SELECTION
# ==================
# Choose which strategies to enable (True = ON, False = OFF)

STRATEGIES_ENABLED = {
    'ma_crossover': True,   # Moving Average Crossover
    'rsi': True,            # RSI confirmation
    'macd': True,           # MACD (NEW!)
    'bollinger': True,      # Bollinger Bands (NEW!)
    'volume': True          # Volume confirmation (NEW!)
}

# VOTING SYSTEM
# =============
# How many strategies must agree before taking a trade?
# Options:
#   'all' - All enabled strategies must agree (most conservative)
#   'majority' - More than 50% must agree (balanced)
#   'any' - Any single strategy triggers trade (most aggressive)
#   Number (e.g., 3) - Exactly N strategies must agree

STRATEGY_VOTE_REQUIRED = 'majority'  # Recommended: 'majority'

# If using number: how many strategies must agree
# MIN_STRATEGIES_AGREE = 3  # Uncomment and set if using number


# STRATEGY 1: MOVING AVERAGE CROSSOVER
# =====================================
# Fast (Short-term) Moving Average
MA_FAST_PERIOD = 10  # Reacts quickly to price changes
                     # Common values: 9, 10, 12, 20

# Slow (Long-term) Moving Average  
MA_SLOW_PERIOD = 30  # Shows overall trend
                     # Common values: 26, 30, 50, 200


# STRATEGY 2: RSI (RELATIVE STRENGTH INDEX)
# ==========================================
RSI_PERIOD = 14       # Standard RSI calculation period
RSI_OVERSOLD = 30     # Below this = oversold (potential buy)
RSI_OVERBOUGHT = 70   # Above this = overbought (potential sell)


# STRATEGY 3: MACD (Moving Average Convergence Divergence)
# =========================================================
# MACD is a powerful momentum indicator that shows:
# - Trend direction (MACD line vs Signal line)
# - Momentum strength (histogram)
# - Trend changes (crossovers)

MACD_FAST_PERIOD = 12    # Fast EMA period (standard)
MACD_SLOW_PERIOD = 26    # Slow EMA period (standard)
MACD_SIGNAL_PERIOD = 9   # Signal line period (standard)

# MACD generates signals when:
# BUY: MACD line crosses above Signal line (bullish momentum)
# SELL: MACD line crosses below Signal line (bearish momentum)


# STRATEGY 4: BOLLINGER BANDS
# ============================
# Bollinger Bands show volatility and potential reversal points
# - Price touching lower band = oversold (potential buy)
# - Price touching upper band = overbought (potential sell)
# - Bands expanding = increased volatility
# - Bands contracting = decreased volatility (breakout coming)

BOLLINGER_PERIOD = 20         # Moving average period (standard: 20)
BOLLINGER_STD_DEV = 2.0       # Standard deviations (standard: 2)

# Thresholds: How close to bands to trigger signals (0.0 to 1.0)
# 0.0 = must touch band exactly
# 0.1 = within 10% of band distance
# 0.2 = within 20% of band distance (recommended)
BOLLINGER_LOWER_THRESHOLD = 0.2  # Buy when price near lower band
BOLLINGER_UPPER_THRESHOLD = 0.2  # Sell when price near upper band


# STRATEGY 5: VOLUME CONFIRMATION
# ================================
# Volume confirms the strength of price moves
# - High volume on breakouts = strong signal
# - Low volume on breakouts = weak signal (might fail)

VOLUME_MA_PERIOD = 20         # Volume moving average period
VOLUME_SPIKE_THRESHOLD = 1.5  # Volume must be X times average
                              # 1.5 = 50% above average (recommended)
                              # 2.0 = 100% above average (stricter)

# Should volume confirmation be required for all trades?
VOLUME_REQUIRED = False  # True = must have volume spike
                        # False = volume just adds to vote


# RISK MANAGEMENT
# ===============
# These protect you from losing too much money on a single trade

MAX_POSITION_SIZE = 0.3  # Maximum 30% of capital per trade
                         # Never put all eggs in one basket!

STOP_LOSS_PERCENT = 0.05  # Exit trade if price drops 5% below buy price
                          # This limits your losses

TAKE_PROFIT_PERCENT = 0.10  # Exit trade if price rises 10% above buy price
                            # Lock in your profits!


# TRADING MODE
# ============
PAPER_TRADING = True  # True = Simulated (no real money)
                      # False = Live trading (BE VERY CAREFUL!)

# Logging settings
LOG_LEVEL = 'INFO'  # How much information to display
LOG_TO_FILE = True
LOG_FILE = 'trading_bot.log'
