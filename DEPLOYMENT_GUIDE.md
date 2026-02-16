# 🚀 DASHBOARD, TELEGRAM & CLOUD DEPLOYMENT GUIDE

Complete guide to running your trading bot with professional features!

---

## 📋 Table of Contents

1. [Phase 1: Beautiful Dashboard](#phase-1-beautiful-dashboard)
2. [Phase 2: Telegram Integration](#phase-2-telegram-integration)
3. [Phase 3: Automated Scheduling](#phase-3-automated-scheduling)
4. [Phase 4: Cloud Deployment](#phase-4-cloud-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Phase 1: Beautiful Dashboard

### 🎨 What You Get:
- Interactive web interface
- Real-time charts with all indicators
- Strategy voting visualization
- Clean, professional design
- Auto-refresh capability

### Setup (5 minutes):

#### Step 1: Install New Packages
```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web dashboard
- `plotly` - Interactive charts
- `rich` - Colored terminal output
- `python-telegram-bot` - Telegram integration
- `schedule` - Automation
- `python-dotenv` - Environment variables

#### Step 2: Run the Dashboard
```bash
streamlit run dashboard.py
```

Your browser will automatically open to: `http://localhost:8501`

### Dashboard Features:

**📊 Main View:**
- Current price with change percentage
- RSI, MACD, Volume ratio, Bollinger position
- Strategy votes (see each strategy's decision)
- Final signal (BUY/SELL/HOLD)

**📈 Interactive Chart:**
- Candlestick price chart
- Moving averages (blue/red lines)
- Bollinger Bands (gray bands)
- RSI indicator (purple line with 30/70 zones)
- MACD (with histogram)
- Volume bars with average

**⚙️ Sidebar Controls:**
- Select any stock from your list
- Choose timeframe (1d, 1h, 15m, 5m)
- Change historical period
- Auto-refresh toggle
- Manual refresh button

### Tips:

**For Multiple Monitors:**
Keep dashboard open on second screen while you work

**For Live Monitoring:**
Enable auto-refresh (refreshes every 60 seconds)

**For Analysis:**
Click any chart element to zoom/inspect

**For Presentation:**
Use full-screen mode (F11) for clean view

---

## Phase 2: Telegram Integration

### 📱 What You Get:
- Trading signals sent to your phone
- Trade execution notifications
- Portfolio updates
- Daily summaries
- Bot commands (/signal, /portfolio, etc.)

### Setup (10 minutes):

#### Step 1: Create Telegram Bot

1. **Open Telegram** and search for `@BotFather`

2. **Send** `/newbot` command

3. **Choose a name:** "Raghu Trading Bot" (or anything)

4. **Choose a username:** Must end in "bot" (e.g., `raghu_trading_bot`)

5. **Copy the token** BotFather gives you. Looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ123456789
   ```

#### Step 2: Configure Bot

1. **Create `.env` file** in your project folder:
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env`** and add your token:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ123456789
   ```

#### Step 3: Get Your Chat ID

1. **Start your bot on Telegram** (search for your bot's username)

2. **Send any message** to it (like "hello")

3. **Run this command:**
   ```bash
   python telegram_bot.py get_chat_id
   ```

4. **Copy the chat ID** shown (looks like: 123456789)

5. **Add to `.env` file:**
   ```
   TELEGRAM_CHAT_ID=123456789
   ```

#### Step 4: Test It!
```bash
python telegram_bot.py test
```

You should receive a test message on Telegram! 🎉

### Using Telegram Bot:

#### Method 1: Start Interactive Bot
```bash
python telegram_bot.py
```

Then use these commands in Telegram:
- `/start` - Welcome message
- `/signal` - Get current signals for all stocks
- `/portfolio` - View portfolio status
- `/help` - Show available commands

#### Method 2: Send Signals Programmatically
```bash
python telegram_bot.py signal
```

This analyzes all symbols and sends signals to your Telegram.

#### Method 3: Integrate with Your Bot

Add this to your trading code:

```python
from telegram_bot import TelegramNotifier
import asyncio

# Create notifier
notifier = TelegramNotifier()

# Send signal
asyncio.run(notifier.send_signal(
    symbol='AAPL',
    signal='BUY',
    price=180.50,
    indicators={
        'rsi': '55.3',
        'macd': 'Bullish',
        'ma': 'Uptrend'
    }
))

# Send trade execution
asyncio.run(notifier.send_trade_execution(
    symbol='AAPL',
    action='BUY',
    shares=1,
    price=180.50,
    total=180.50
))
```

### Notification Types:

**📊 Trading Signals:**
Sent when BUY/SELL signal detected
- Symbol, signal type, price
- All indicator values
- Timestamp

**✅ Trade Executions:**
Sent when trade is executed
- Action (BUY/SELL)
- Shares, price, total cost
- Portfolio impact

**💼 Portfolio Updates:**
Regular status updates
- Cash, total value, return %
- Open positions with P/L
- Can be scheduled hourly/daily

**📈 Daily Summaries:**
End-of-day report
- Trades made, win rate
- Best/worst trade
- Performance metrics

---

## Phase 3: Automated Scheduling

### ⏰ What You Get:
- Run bot automatically at intervals
- 1min, 3min, 5min, 15min, 30min, 1h, 4h, 1d
- Automatic signal detection
- Auto trade execution
- Telegram notifications on signals

### Setup:

#### Basic Usage:

**Run every 5 minutes:**
```bash
python scheduler.py
```

**Run every 1 minute:**
```bash
python scheduler.py --interval 1m
```

**Run every hour:**
```bash
python scheduler.py --interval 1h
```

**Run daily at market open:**
```bash
python scheduler.py --interval 1d
```

**Specific symbols only:**
```bash
python scheduler.py --interval 5m --symbols AAPL,MSFT,GOOGL
```

**Without Telegram:**
```bash
python scheduler.py --no-telegram
```

### What Happens Automatically:

1. **Analysis runs** at specified interval
2. **Indicators calculated** for all symbols
3. **Signals generated** using multi-strategy
4. **Trades executed** if signals present
5. **Telegram sent** if signal found
6. **Risk managed** (stop-loss/take-profit checked)
7. **Portfolio updated**
8. **Repeat** at next interval

### Intervals Explained:

| Interval | Use Case | Pro | Con |
|----------|----------|-----|-----|
| 1m | Day trading | Fast signals | Many false signals |
| 3m | Active trading | Quick reactions | Still noisy |
| 5m | **Recommended** | Good balance | Requires monitoring |
| 15m | Swing trading | Quality signals | Slower reactions |
| 30m | Part-time trading | Less noise | Miss some moves |
| 1h | **Casual trading** | High quality | Fewer trades |
| 4h | Position trading | Very stable | Very few trades |
| 1d | Long-term | Best quality | Overnight risk |

**Recommendation for beginners:** Start with **1h** or **1d**

### Running 24/7:

#### On Windows:

1. **Create batch file** `start_bot.bat`:
   ```batch
   @echo off
   cd C:\Users\Raghu\tradingbot
   python scheduler.py --interval 5m
   pause
   ```

2. **Double-click** to start

3. **Keep window open** or minimize

#### Keep Running on Restart:

1. Press `Win + R`
2. Type: `shell:startup`
3. Put your `.bat` file there
4. Bot starts on Windows startup

---

## Phase 4: Cloud Deployment

### ☁️ Why Cloud?

- **24/7 operation** - Never stops
- **No local computer needed** - Runs independently
- **Better reliability** - Professional infrastructure
- **Remote access** - Monitor from anywhere
- **Scalability** - Handle more symbols

### Options:

#### Option 1: AWS EC2 (Recommended for production)

**Pros:**
- Most reliable
- Full control
- Can run 24/7
- Many instances available

**Cons:**
- Costs money (~$5-20/month)
- Requires some Linux knowledge

**Quick Start:**

1. **Create AWS Account** (free tier available)

2. **Launch EC2 Instance:**
   - Ubuntu 22.04 LTS
   - t2.micro (free tier)
   - Open port 8501 for dashboard

3. **Connect via SSH:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ip
   ```

4. **Install Python & Dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```

5. **Upload Your Files:**
   ```bash
   scp -i your-key.pem *.py ubuntu@your-ip:~/
   ```

6. **Run with screen:**
   ```bash
   screen -S trading
   python3 scheduler.py --interval 5m
   # Press Ctrl+A, then D to detach
   ```

7. **Access Dashboard:**
   ```bash
   streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
   ```
   Open: `http://your-ip:8501`

#### Option 2: Heroku (Easiest for beginners)

**Pros:**
- Very easy setup
- Free tier available
- Automatic deployment
- Built-in monitoring

**Cons:**
- Free tier sleeps after 30 mins inactive
- Limited to web processes
- Need to upgrade for 24/7

**Quick Start:**

1. **Install Heroku CLI**

2. **Create files:**

`Procfile`:
```
web: streamlit run dashboard.py --server.port=$PORT
worker: python scheduler.py --interval 5m
```

`runtime.txt`:
```
python-3.11.0
```

3. **Deploy:**
```bash
heroku login
heroku create raghu-trading-bot
git push heroku main
heroku ps:scale worker=1
```

#### Option 3: Google Cloud Run (Good balance)

**Pros:**
- Pay per use
- Auto-scaling
- Easy to use
- Good free tier

**Cons:**
- Request-based (not ideal for scheduler)
- Need to containerize

#### Option 4: Raspberry Pi (Local 24/7)

**Pros:**
- One-time cost (~$50)
- Full control
- Low power consumption
- No monthly fees

**Cons:**
- Need physical device
- Your internet connection
- You maintain it

**Setup:**
1. Install Raspberry Pi OS
2. Install Python
3. Copy files
4. Run scheduler
5. Use systemd for auto-start

### Database Integration (Advanced):

For storing historical data:

```python
# PostgreSQL
import psycopg2

# SQLite (simplest)
import sqlite3

# MongoDB (flexible)
import pymongo
```

Store:
- Trade history
- Performance metrics
- Signal history
- Portfolio snapshots

---

## 🎯 Recommended Setup

### For Learning (Local):
```bash
# Terminal 1: Dashboard
streamlit run dashboard.py

# Terminal 2: Manual trading
python main.py
```

### For Testing (Local + Telegram):
```bash
# Setup Telegram first
python telegram_bot.py test

# Run automated
python scheduler.py --interval 1h
```

### For Production (Cloud):
```bash
# AWS EC2 with screen:
screen -S trading
python scheduler.py --interval 5m

# Separate screen for dashboard:
screen -S dashboard
streamlit run dashboard.py --server.address 0.0.0.0
```

---

## 🔧 Configuration Tips

### For Different Timeframes:

**1-Minute (Day Trading):**
```python
# In config.py
MA_FAST_PERIOD = 5
MA_SLOW_PERIOD = 15
RSI_PERIOD = 9
STRATEGY_VOTE_REQUIRED = 'all'  # Very strict
```

**5-Minute (Active Trading):**
```python
MA_FAST_PERIOD = 10
MA_SLOW_PERIOD = 30
RSI_PERIOD = 14
STRATEGY_VOTE_REQUIRED = 'majority'  # Balanced
```

**1-Hour (Recommended):**
```python
MA_FAST_PERIOD = 10
MA_SLOW_PERIOD = 30
RSI_PERIOD = 14
STRATEGY_VOTE_REQUIRED = 'majority'
```

**Daily (Long-term):**
```python
MA_FAST_PERIOD = 20
MA_SLOW_PERIOD = 50
RSI_PERIOD = 14
STRATEGY_VOTE_REQUIRED = 'majority'
```

---

## 📊 Monitoring & Maintenance

### Daily Tasks:
- Check Telegram for signals
- Review dashboard for performance
- Monitor open positions

### Weekly Tasks:
- Review win rate and returns
- Adjust strategy if needed
- Check for errors in logs

### Monthly Tasks:
- Analyze overall performance
- Optimize parameters
- Update to new bot versions

---

## 🐛 Troubleshooting

### Dashboard won't start:
```bash
# Check if streamlit installed
streamlit --version

# Reinstall if needed
pip install streamlit --upgrade

# Check port not in use
netstat -ano | findstr :8501
```

### Telegram not sending:
```bash
# Test connection
python telegram_bot.py test

# Check .env file exists and has token
type .env

# Verify chat ID
python telegram_bot.py get_chat_id
```

### Scheduler not running:
```bash
# Check for errors
python scheduler.py --interval 5m

# Verify config.py has symbols
python -c "import config; print(config.SYMBOLS)"
```

### Cloud deployment issues:
```bash
# Check logs
heroku logs --tail

# AWS: check security groups
# Make sure port 8501 is open

# Verify files uploaded
ls -la
```

---

## 🚀 Next Steps

1. ✅ **Install new packages**
   ```bash
   pip install -r requirements.txt
   ```

2. ✅ **Try dashboard**
   ```bash
   streamlit run dashboard.py
   ```

3. ✅ **Setup Telegram**
   - Create bot with @BotFather
   - Get token and chat ID
   - Test: `python telegram_bot.py test`

4. ✅ **Test automation**
   ```bash
   python scheduler.py --interval 1h
   ```

5. ✅ **Plan cloud deployment**
   - Choose platform (AWS/Heroku/GCP)
   - Prepare for migration
   - Test thoroughly first

---

## 📚 Additional Resources

**Dashboard:**
- Streamlit docs: https://docs.streamlit.io
- Plotly charts: https://plotly.com/python

**Telegram:**
- Bot API: https://core.telegram.org/bots
- python-telegram-bot: https://python-telegram-bot.org

**Cloud:**
- AWS Free Tier: https://aws.amazon.com/free
- Heroku: https://heroku.com
- GCP: https://cloud.google.com

---

**Your bot is now PRODUCTION-READY! 🎉**

Start with local dashboard and Telegram, then move to cloud when ready!

Questions? Issues? Check the troubleshooting section or reach out!
