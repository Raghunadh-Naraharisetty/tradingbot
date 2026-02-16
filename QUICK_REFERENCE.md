# 🚀 QUICK REFERENCE CARD

Everything you need on one page!

---

## 📝 MANAGING SYMBOLS (Super Easy!)

### Edit ONE file: `symbols.txt`

```
# Just list your symbols, one per line:
AAPL
MSFT
GOOGL
NVDA
TSLA

# Comment out to disable:
# AMD
```

**That's it!** Save and restart bot.

---

## 💬 TELEGRAM MESSAGES (Simple & Clean!)

You'll receive messages like:

```
🟢 BUY AAPL at $180.50
10:30:15

🔴 SELL MSFT at $420.30
14:22:48
```

**Just what you need:**
- Action (BUY/SELL)
- Symbol
- Price
- Time

---

## ⚡ COMMON COMMANDS

```bash
# SYMBOL MANAGEMENT
python symbol_loader.py list           # Show symbols
python symbol_loader.py add NVDA       # Add symbol
python symbol_loader.py remove TSLA    # Remove symbol

# TELEGRAM
python telegram_bot.py test            # Test Telegram
python telegram_bot.py signal          # Send signals now
python telegram_bot.py                 # Start bot

# AUTOMATION
python scheduler.py --interval 1h      # Run every hour
python scheduler.py --interval 5m      # Run every 5 min
python scheduler.py --interval 1d      # Run daily

# DASHBOARD
streamlit run dashboard.py             # Open web dashboard

# MANUAL TRADING
python main.py                         # Full backtest
python main.py analyze AAPL            # Analyze one stock
```

---

## 🎯 DAILY WORKFLOW

**Morning:**
```bash
1. Edit symbols.txt (if needed)
2. python scheduler.py --interval 1h
3. Check Telegram throughout day
```

**Evening:**
```bash
1. Review signals
2. Update symbols.txt for tomorrow
```

---

## 📁 KEY FILES

| File | What to Do |
|------|------------|
| **symbols.txt** | ✏️ Edit to add/remove stocks |
| telegram_bot.py | ▶️ Run for Telegram |
| scheduler.py | ▶️ Run for automation |
| dashboard.py | ▶️ Run for web view |
| .env | ✏️ Put Telegram token here |

---

## 🔧 QUICK SETUP (First Time)

```bash
# 1. Install packages
pip install -r requirements.txt

# 2. Edit symbols
notepad symbols.txt

# 3. Setup Telegram
python telegram_bot.py get_chat_id
# Add to .env file

# 4. Test
python telegram_bot.py test

# 5. Start automated
python scheduler.py --interval 1h
```

---

## 📱 TELEGRAM SETUP (5 Minutes)

1. **Create bot:** Message @BotFather on Telegram
2. **Get token:** Copy from BotFather
3. **Add to .env:** `TELEGRAM_BOT_TOKEN=your_token`
4. **Get chat ID:** `python telegram_bot.py get_chat_id`
5. **Add to .env:** `TELEGRAM_CHAT_ID=your_id`
6. **Test:** `python telegram_bot.py test`

---

## ⚙️ CONFIGURATION

**Want more/fewer signals?**

Edit `config.py`:
```python
# Conservative (fewer signals, higher quality)
STRATEGY_VOTE_REQUIRED = 'all'

# Balanced (recommended)
STRATEGY_VOTE_REQUIRED = 'majority'

# Aggressive (more signals)
STRATEGY_VOTE_REQUIRED = 'any'
```

---

## 🐛 TROUBLESHOOTING

**No signals?**
- Check if markets are open
- Run: `python main.py analyze AAPL`

**Telegram not working?**
- Run: `python telegram_bot.py test`
- Check .env file has token and chat ID

**Symbols not loading?**
- Run: `python symbol_loader.py list`
- Check symbols.txt exists

**Bot running slow?**
- Reduce symbols in symbols.txt (keep 5-10)

---

## 💡 PRO TIPS

✅ Start with 5-10 symbols
✅ Use 1h interval for beginning
✅ Keep symbols.txt organized with comments
✅ Test changes before going live
✅ Monitor Telegram regularly

---

## 📞 GETTING HELP

1. Check **SYMBOL_MANAGEMENT_GUIDE.md**
2. Check **QUICK_START_DASHBOARD.md**
3. Check **DEPLOYMENT_GUIDE.md**
4. Run `python symbol_loader.py`
5. Run `python telegram_bot.py help`

---

**That's everything you need! 🎉**

Save this as a reference! 📑
