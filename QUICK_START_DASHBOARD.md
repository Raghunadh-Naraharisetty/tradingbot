# 🚀 QUICK START - Dashboard & Telegram

Get your professional dashboard and Telegram notifications running in 10 minutes!

---

## ⚡ Step 1: Install New Packages (2 minutes)

```bash
pip install -r requirements.txt
```

This installs:
- Streamlit (dashboard)
- Plotly (interactive charts)
- python-telegram-bot (notifications)
- Rich (colored output)
- Schedule (automation)

---

## 📊 Step 2: Launch Dashboard (1 minute)

```bash
streamlit run dashboard.py
```

**What you'll see:**
- Beautiful web interface at http://localhost:8501
- Real-time charts with all indicators
- Strategy voting visualization
- Current signals for all stocks

**Tips:**
- Select different stocks from dropdown
- Change timeframe (1d, 1h, 15m, 5m)
- Enable auto-refresh for live monitoring
- Click refresh button to update data

---

## 📱 Step 3: Setup Telegram (5 minutes)

### A. Create Your Bot

1. Open Telegram and search: `@BotFather`
2. Send: `/newbot`
3. Choose name: "Raghu Trading Bot"
4. Choose username: `raghu_trading_bot` (must end in 'bot')
5. **Copy the token** BotFather gives you

### B. Configure

1. Copy example file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your token:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

### C. Get Your Chat ID

1. Start your bot on Telegram (search for your bot)
2. Send it any message (like "hello")
3. Run:
   ```bash
   python telegram_bot.py get_chat_id
   ```
4. Copy the chat ID shown
5. Add to `.env`:
   ```
   TELEGRAM_CHAT_ID=your_chat_id
   ```

### D. Test It!

```bash
python telegram_bot.py test
```

You should receive a test message! 🎉

---

## 🤖 Step 4: Try Different Modes (2 minutes)

### Mode 1: Interactive Bot
```bash
python telegram_bot.py
```

Then use these commands in Telegram:
- `/start` - Welcome
- `/signal` - Get current signals
- `/portfolio` - View portfolio
- `/help` - Show commands

### Mode 2: Send Signals Now
```bash
python telegram_bot.py signal
```

Sends BUY/SELL signals for all stocks to your Telegram.

### Mode 3: Automated (Best!)
```bash
python scheduler.py --interval 5m
```

Runs every 5 minutes, sends signals automatically!

---

## 🎯 Recommended Daily Workflow

### Morning (Market Open):

**Terminal 1 - Dashboard:**
```bash
streamlit run dashboard.py
```
Keep open for monitoring

**Terminal 2 - Automated Trading:**
```bash
python scheduler.py --interval 1h
```
Runs every hour, sends Telegram alerts

### Throughout Day:
- Check Telegram for signals
- Review dashboard for performance
- Bot handles everything automatically

### Evening (Market Close):
- Check final signals: `python telegram_bot.py signal`
- Review performance on dashboard
- Plan for next day

---

## 💡 Pro Tips

### Dashboard Tips:
1. **Multiple monitors?** Keep dashboard on second screen
2. **Want mobile?** Dashboard works on phone browser
3. **Specific stock?** Use dropdown to focus on one
4. **Need details?** Expand "Detailed Indicator Values"

### Telegram Tips:
1. **Group chat?** Add bot to group, all members get signals
2. **Multiple bots?** Create separate bot for each account
3. **Too many messages?** Adjust signal thresholds
4. **Want summaries only?** Modify `telegram_bot.py`

### Automation Tips:
1. **Start small:** Begin with 1h interval
2. **Test first:** Run `--no-telegram` to test without spam
3. **Specific symbols:** Use `--symbols AAPL,MSFT`
4. **Monitor logs:** Check console output regularly

---

## 🔍 Commands Reference

### Dashboard:
```bash
streamlit run dashboard.py                    # Start dashboard
streamlit run dashboard.py --server.port 8502 # Different port
```

### Telegram:
```bash
python telegram_bot.py                  # Start interactive bot
python telegram_bot.py test             # Send test message
python telegram_bot.py signal           # Send current signals
python telegram_bot.py get_chat_id      # Get your chat ID
python telegram_bot.py help             # Show help
```

### Scheduler:
```bash
python scheduler.py                              # Every 5min (default)
python scheduler.py --interval 1m                # Every 1 minute
python scheduler.py --interval 1h                # Every hour
python scheduler.py --interval 1d                # Daily at 9:30 AM
python scheduler.py --symbols AAPL,MSFT          # Specific stocks
python scheduler.py --no-telegram                # Without Telegram
python scheduler.py --interval 5m --symbols NVDA # Combined
```

---

## 🎨 What Each Tool Does

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Dashboard** | Visual analysis, monitoring | Throughout trading day |
| **Telegram** | Mobile alerts, notifications | Anytime, anywhere |
| **Scheduler** | Automated trading | Run and forget |
| **main.py** | Manual backtesting | Strategy testing |

---

## ⚠️ Important Notes

### Dashboard:
- Updates when you click refresh or auto-refresh
- Loads data from Yahoo Finance (internet required)
- Can handle any stock symbol
- Uses same config as main bot

### Telegram:
- FREE to use (no fees)
- Works worldwide
- Instant notifications
- Bot token is private (don't share)

### Scheduler:
- Runs continuously (keep terminal open)
- Checks for signals at intervals
- Executes trades automatically
- Sends Telegram on signals

### All Tools:
- Still **paper trading** by default
- Change `PAPER_TRADING = False` for real trading (careful!)
- All use same config.py settings
- All support same symbols/sectors

---

## 🚀 Next Steps

After mastering the basics:

1. **Customize Dashboard:**
   - Edit `dashboard.py` to add features
   - Add more metrics
   - Create custom views

2. **Enhance Telegram:**
   - Add more notification types
   - Create custom commands
   - Add portfolio tracking

3. **Cloud Deployment:**
   - Read `DEPLOYMENT_GUIDE.md`
   - Choose cloud platform
   - Deploy for 24/7 operation

4. **Advanced Features:**
   - Database integration
   - Multiple accounts
   - Portfolio optimization
   - Machine learning signals

---

## 🐛 Quick Troubleshooting

**Dashboard won't start:**
```bash
pip install streamlit --upgrade
streamlit run dashboard.py
```

**Telegram not working:**
```bash
# Check .env file exists
type .env

# Verify token
python telegram_bot.py test
```

**Scheduler stops:**
```bash
# Check for errors in console
# Make sure config.SYMBOLS is set
python -c "import config; print(config.SYMBOLS)"
```

**No signals appearing:**
```bash
# Markets might be closed
# Try: python main.py analyze AAPL
# Check if indicators calculated
```

---

## 📖 Full Documentation

For detailed information, see:
- **DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **MULTI_STRATEGY_GUIDE.md** - Strategy system
- **SECTOR_TRADING_GUIDE.md** - Sector selection
- **README.md** - Main documentation

---

**Your bot is now PRODUCTION-READY with professional features! 🎉**

Start with dashboard for analysis, add Telegram for alerts, then automate with scheduler!

Questions? Check DEPLOYMENT_GUIDE.md for detailed instructions!
