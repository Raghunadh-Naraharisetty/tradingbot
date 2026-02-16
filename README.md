# 📈 Hybrid Trading Bot with Multi-Sector Support

An educational algorithmic trading bot built with Python. Features a **hybrid strategy** (Moving Average Crossover + RSI) and supports **100+ stocks across 7 major sectors**!

## 🎯 Features

✅ **Hybrid Strategy** - MA Crossover + RSI for better signals
✅ **Multi-Sector Support** - 100+ stocks across 7 sectors
✅ **Sector-Based Configuration** - Easy sector selection
✅ **MVC Architecture** - Professional code structure
✅ **Risk Management** - Stop-loss & take-profit built-in
✅ **Educational** - 1000+ lines of comments
✅ **Paper Trading** - Practice without real money
✅ **Comprehensive Charts** - Visual analysis with indicators

## 📊 Available Sectors (100+ Stocks)

- **Technology/IT** (20 stocks): AAPL, MSFT, GOOGL, META, NVDA...
- **Semiconductors/Chips** (20 stocks): NVDA, AMD, INTC, TSM...
- **Healthcare** (20 stocks): UNH, JNJ, LLY, ABBV, MRK...
- **Pharmaceuticals** (20 stocks): PFE, MRK, ABBV, LLY...
- **Financial Services** (20 stocks): JPM, BAC, GS, MS...
- **Energy** (20 stocks): XOM, CVX, COP, SLB...
- **Consumer/Retail** (20 stocks): AMZN, TSLA, WMT, HD...

## ⚠️ IMPORTANT DISCLAIMER

**This is educational software only.** 
- NOT financial advice
- Past performance does NOT guarantee future results
- Always practice with paper trading first
- Real trading involves fees, slippage, and taxes
- Never invest money you can't afford to lose

## 🎯 What is Moving Average Crossover?

The Moving Average Crossover strategy is one of the **simplest and most popular** trading strategies:

### How It Works:

1. **Two Moving Averages:**
   - **Fast MA** (10 periods): Reacts quickly to price changes
   - **Slow MA** (30 periods): Shows the overall trend

2. **Buy Signal (Golden Cross) 🟢:**
   - When Fast MA crosses **ABOVE** Slow MA
   - Indicates uptrend is starting

3. **Sell Signal (Death Cross) 🔴:**
   - When Fast MA crosses **BELOW** Slow MA
   - Indicates downtrend is starting

### Example:
```
Price: $150 → $152 → $155 → $158 → $160
Fast MA (10 days): Moving up quickly
Slow MA (30 days): Moving up slowly

When Fast > Slow = BUY! 📈
```

## 🏗️ Project Structure (MVC Architecture)

```
algo_trading_bot/
│
├── config.py         # Settings (capital, symbols, strategy parameters)
├── model.py          # Brain (data fetching, calculations, trading logic)
├── view.py           # Display (charts, reports, formatted output)
├── controller.py     # Conductor (orchestrates model and view)
├── main.py           # Entry point (run this file)
├── requirements.txt  # Python packages needed
└── README.md         # This file
```

### What is MVC?

**Model-View-Controller** is a design pattern that separates concerns:

- **Model**: Business logic and data (the "brain")
- **View**: User interface and display (the "eyes")
- **Controller**: Coordinates model and view (the "conductor")

Benefits:
- Organized code
- Easy to modify
- Each part has one job
- Professional structure

## 🚀 Setup Instructions for Windows

### Step 1: Install Python

1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.11 or newer
3. **Important:** Check "Add Python to PATH" during installation
4. Click "Install Now"

Verify installation:
```bash
python --version
```
Should show: `Python 3.11.x` or newer

### Step 2: Install Required Tools

1. **Install VS Code** (Recommended code editor)
   - Download from [code.visualstudio.com](https://code.visualstudio.com/)
   - Install Python extension in VS Code

2. **Install Git** (Optional but recommended)
   - Download from [git-scm.com](https://git-scm.com/)

### Step 3: Set Up the Project

1. **Create project folder:**
```bash
mkdir algo_trading_bot
cd algo_trading_bot
```

2. **Copy all the bot files** into this folder:
   - config.py
   - model.py
   - view.py
   - controller.py
   - main.py
   - requirements.txt

3. **Install Python packages:**
```bash
pip install -r requirements.txt
```

If you get an error, try:
```bash
python -m pip install -r requirements.txt
```

### Step 4: Configure the Bot

Open `config.py` and customize:

```python
# How much money to start with
INITIAL_CAPITAL = 100.00

# Which stocks to trade
SYMBOLS = ['AAPL']  # Start with one stock

# Moving Average periods
MA_FAST_PERIOD = 10   # Fast MA
MA_SLOW_PERIOD = 30   # Slow MA

# Risk management
MAX_POSITION_SIZE = 0.3      # 30% of capital per trade
STOP_LOSS_PERCENT = 0.05     # Exit if -5% loss
TAKE_PROFIT_PERCENT = 0.10   # Exit if +10% gain
```

### Step 4: Configure Your Sectors

Open `config.py` and choose which stocks to trade. The bot now supports **100+ stocks across 7 sectors**!

**Quick Options:**

```python
# Option 1: Top 5 Tech Stocks (Recommended for beginners)
SYMBOLS = TECH_SYMBOLS[:5]  # AAPL, MSFT, GOOGL, META, NVDA

# Option 2: Top 5 Healthcare Stocks
SYMBOLS = HEALTHCARE_SYMBOLS[:5]  # UNH, JNJ, LLY, ABBV, MRK

# Option 3: Diversified Portfolio (3 stocks from each sector)
SYMBOLS = (TECH_SYMBOLS[:3] + HEALTHCARE_SYMBOLS[:3] + FINANCE_SYMBOLS[:3])

# Option 4: All Tech Stocks (Advanced)
SYMBOLS = TECH_SYMBOLS  # All 20 tech stocks
```

**Use the Sector Viewer to explore:**
```bash
python sector_viewer.py              # See all sectors
python sector_viewer.py tech         # See tech stocks
python sector_viewer.py current      # See your config
```

**📖 See `SECTOR_TRADING_GUIDE.md` for complete sector information!**

## 🎮 How to Run

### Option 1: Full Backtest (Recommended for beginners)

Test the strategy on historical data:

```bash
python main.py
```

This will:
1. Download 6 months of AAPL data
2. Calculate moving averages
3. Simulate trades
4. Show performance results
5. Generate charts

### Option 2: Analyze Single Stock

Check what the strategy says about a stock right now:

```bash
python main.py analyze AAPL
```

or any other stock:

```bash
python main.py analyze MSFT
python main.py analyze TSLA
```

### Option 3: Show Help

```bash
python main.py help
```

## 📊 Understanding the Output

### 1. Market Data Summary
```
📊 MARKET DATA SUMMARY - AAPL
Close Price: $180.50
Fast MA (10): $181.20
Slow MA (30): $178.90
Current Trend: 🟢 BULLISH (Fast > Slow)
```
- Shows current price and moving averages
- Indicates if we're in uptrend or downtrend

### 2. Trading Signals
```
🟢 GOLDEN CROSS DETECTED for AAPL!
Price: $180.50
Fast MA crossed above Slow MA
→ BULLISH signal (uptrend starting)
```
- When the bot detects a buy or sell opportunity

### 3. Trade Execution
```
✅ BUY ORDER EXECUTED
Symbol: AAPL
Shares: 1
Price: $180.50
Total Cost: $180.50
Cash Remaining: $19.50
```
- Confirms trades that were made

### 4. Performance Metrics
```
📊 PERFORMANCE METRICS
Total Completed Trades: 5
Winning Trades: 3 🎉
Losing Trades: 2 😞
Win Rate: 60.00%
Total Profit/Loss: $15.30
Average P/L per Trade: $3.06
```
- Summary of how the strategy performed

### 5. Charts

The bot generates PNG charts showing:
- Stock price over time
- Fast and Slow moving averages
- Buy signals (green triangles ▲)
- Sell signals (red triangles ▼)
- Trading volume

## 🎓 Learning Path

### Week 1: Understand the Code
1. Read through each file with comments
2. Run the bot and observe the output
3. Try changing MA periods (e.g., 20/50 instead of 10/30)
4. See how it affects results

### Week 2: Experiment with Settings
1. Try different stocks (MSFT, GOOGL, TSLA)
2. Adjust risk management parameters
3. Test longer historical periods
4. Compare different MA combinations

### Week 3: Understand Limitations
1. Why 90% win rate is impossible
2. The tradeoff between win rate and profit size
3. How false signals happen
4. Importance of risk management

### Week 4: Expand Knowledge
1. Learn about other indicators (RSI, MACD)
2. Study different timeframes (hourly vs daily)
3. Understand market conditions (trending vs ranging)
4. Research more advanced strategies

## 🔧 Customization Ideas

### Easy Modifications:

1. **Change Stocks:**
```python
SYMBOLS = ['MSFT', 'GOOGL', 'TSLA']
```

2. **Adjust Moving Averages:**
```python
MA_FAST_PERIOD = 20   # Slower, fewer signals
MA_SLOW_PERIOD = 50   # Common combination
```

3. **Tighter Risk Management:**
```python
STOP_LOSS_PERCENT = 0.03      # Stop at -3%
TAKE_PROFIT_PERCENT = 0.06    # Take profit at +6%
```

### Advanced Modifications:

1. **Add More Indicators** (requires learning):
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands

2. **Multiple Timeframes:**
   - Check daily and weekly trends
   - Trade on hourly but confirm with daily

3. **Portfolio Management:**
   - Allocate capital across multiple stocks
   - Rebalancing logic

## 📚 Key Concepts Explained

### Moving Average
- Average price over N periods
- Smooths out noise
- Shows trend direction

### Crossover
- When one line crosses another
- Indicates momentum shift
- Basis for many strategies

### Win Rate vs Profit
- 90% win rate is unrealistic
- A 55% win rate can be profitable
- Important: Average win > Average loss

### Risk Management
- **Stop Loss**: Limits losses
- **Take Profit**: Locks in gains
- **Position Sizing**: Don't risk too much

### Backtesting
- Testing strategy on past data
- Helps evaluate performance
- NOT a guarantee of future results

## ⚠️ Common Mistakes to Avoid

1. **Overfitting:** Tweaking strategy to perfectly match past data (won't work on future data)

2. **No Risk Management:** Trading without stop-losses (can wipe out account)

3. **Emotional Trading:** Ignoring strategy signals (defeats the purpose of algo trading)

4. **Jumping to Live Trading:** Practice extensively before risking real money

5. **Unrealistic Expectations:** Expecting consistent 90%+ win rates

## 🐛 Troubleshooting

### "pip not recognized"
```bash
python -m pip install -r requirements.txt
```

### "No module named 'pandas'"
```bash
pip install pandas numpy yfinance matplotlib
```

### "Can't download data for symbol"
- Check internet connection
- Verify symbol is correct (AAPL not Apple)
- Yahoo Finance might be temporarily down

### Charts not generating
- Make sure matplotlib is installed
- Check if `/home/claude/algo_trading_bot/` path exists

## 📖 Additional Resources

### Learning to Code:
- [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/)
- [Codecademy Python](https://www.codecademy.com/learn/learn-python-3)

### Learning Trading:
- [Investopedia](https://www.investopedia.com/)
- [BabyPips](https://www.babypips.com/) (forex but good concepts)
- [Khan Academy Finance](https://www.khanacademy.org/economics-finance-domain)

### Technical Analysis:
- "Technical Analysis of the Financial Markets" by John Murphy
- "A Beginner's Guide to the Stock Market" by Matthew Kratter
- YouTube: "The Chart Guys", "Rayner Teo"

## 🚀 Next Steps

After mastering this bot:

1. **Learn More Strategies:**
   - Mean reversion
   - Breakout trading
   - Trend following

2. **Improve the Bot:**
   - Add more indicators
   - Implement better risk management
   - Add backtesting statistics

3. **Build Real Applications:**
   - Web dashboard with Flask/Django
   - Real-time alerts via email/SMS
   - Portfolio tracker

4. **Consider Paper Trading APIs:**
   - Alpaca (free paper trading)
   - TD Ameritrade API
   - Interactive Brokers API

## 💡 Final Advice

1. **Be Patient:** Learning takes time. Don't rush into live trading.

2. **Start Small:** Even when you go live, start with small amounts.

3. **Keep Learning:** Markets evolve. Keep studying and adapting.

4. **Manage Risk:** Protect your capital first, make profits second.

5. **Stay Realistic:** No strategy wins 90% of the time consistently.

6. **Have Fun:** Enjoy the learning process!

## 📞 Support

If you have questions:
1. Read through the code comments
2. Check this README
3. Search online for specific errors
4. Join trading/programming communities

Remember: This is a learning tool. The goal is education, not getting rich quick!

---

**Good luck on your trading and programming journey! 🚀📈**
