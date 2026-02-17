# 🔧 SIGNAL TROUBLESHOOTING - Step by Step

Follow these steps EXACTLY to get signals working!

---

## 🎯 STEP 1: Check Your Config (5 minutes)

### Open config.py:
```bash
notepad config.py
```

### Find and verify these settings:

**Look for `STRATEGIES_ENABLED` section:**
```python
STRATEGIES_ENABLED = {
    'ma_crossover': True,   # ✅ Should be True
    'rsi': True,            # ✅ Should be True
    'macd': False,          # ❌ Should be False
    'bollinger': False,     # ❌ Should be False
    'volume': False         # ❌ Should be False
}
```

**Look for `STRATEGY_VOTE_REQUIRED`:**
```python
# For TESTING (to see signals quickly):
STRATEGY_VOTE_REQUIRED = 'any'  # ✅ Use this temporarily

# For PRODUCTION (after testing):
# STRATEGY_VOTE_REQUIRED = 'all'  # Use this later
```

**Look for `PERIOD`:**
```python
PERIOD = '3mo'  # ✅ Should be 3mo or less
# NOT '6mo' if using short intervals!
```

### Save the file!

---

## 🎯 STEP 2: Run Signal Checker (2 minutes)

**This tool shows you EXACTLY what's happening:**

```bash
cd C:\Users\Raghu\tradingbot
python signal_checker.py
```

**What you'll see:**

```
🔍 SIGNAL DIAGNOSTIC TOOL
============================================================
Checking 6 symbols...
Strategies enabled: ['ma_crossover', 'rsi']
Vote requirement: any

📊 Analyzing AAPL...
   Price: $180.50
   MA Fast: $179.20
   MA Slow: $175.30
   RSI: 55.2
   🟢 MA Crossover: BUY
   ⚪ RSI: HOLD (value: 55.2)
   
   📊 Vote Count: BUY=1, SELL=0
   📊 Requirement: any
   ✅ FINAL: 🟢 BUY SIGNAL!
   
📊 SUMMARY
Signals found: 2
✅ Your bot is working correctly!
```

**If you see signals:** Great! Bot is working!

**If you see NO signals:** Continue to Step 3

---

## 🎯 STEP 3: Make Config More Sensitive (For Testing)

**If no signals found, temporarily use more sensitive settings:**

### In config.py, change:

```python
# TEMPORARY TESTING CONFIG
# Use this to confirm bot works, then switch back

STRATEGIES_ENABLED = {
    'ma_crossover': True,
    'rsi': True,
    'macd': False,
    'bollinger': False,
    'volume': False
}

STRATEGY_VOTE_REQUIRED = 'any'  # ⭐ ANY strategy can trigger

# More sensitive MAs (more signals)
MA_FAST_PERIOD = 5   # Very fast
MA_SLOW_PERIOD = 15  # Short

# Wider RSI range (more signals)
RSI_OVERSOLD = 40   # Higher = more BUY signals
RSI_OVERBOUGHT = 60  # Lower = more SELL signals

# Period
PERIOD = '2mo'
```

**Save and test again:**
```bash
python signal_checker.py
```

**You SHOULD see signals now!**

---

## 🎯 STEP 4: Run Scheduler with Verbose Output

**Once signal_checker shows signals, run scheduler:**

```bash
python scheduler.py --interval 1h
```

**Watch the output:**

```
============================================================
🔄 Running analysis at 2024-02-15 14:30:00
============================================================

📊 Analyzing AAPL...
🟢 BUY signal detected!
✅ Executed: Bought 1 share at $180.50

📱 Telegram sent: 🟢 BUY AAPL at $180.50
```

**Check your Telegram!**

---

## 🎯 STEP 5: Verify Telegram is Working

**Test Telegram separately:**

```bash
python telegram_bot.py test
```

**You should receive:**
```
🎉 Test Message

Your Telegram bot is working!
```

**If NOT working:**
- Check .env file has correct token
- Check .env file has correct chat ID
- Run: `python telegram_bot.py get_chat_id` again

---

## 🎯 STEP 6: Check Market Hours

**Important:** Signals only appear during market activity!

**US Market Hours:**
- 9:30 AM - 4:00 PM Eastern Time
- Monday - Friday only

**Current time:** (Check if market is open)

**If market closed:**
- Run signal_checker.py (shows historical signals)
- Wait for market open
- Or test with different symbols

---

## 🚨 Common Problems & Solutions

### Problem 1: "No signals found"

**Causes:**
- ✅ Voting too strict (`'all'` instead of `'any'`)
- ✅ Market conditions don't match
- ✅ MA periods too long
- ✅ RSI thresholds too tight

**Solution:**
Use test config (Step 3 above)

---

### Problem 2: "❌ No data available"

**Causes:**
- ✅ Period too long for interval
- ✅ Symbol delisted/wrong
- ✅ Yahoo Finance issue

**Solution:**
```python
# In config.py
PERIOD = '1mo'  # Shorter period
```

---

### Problem 3: "All strategies show HOLD"

**Cause:**
Market is ranging (no clear trend)

**Solution:**
- Normal! Wait for trends
- Or use more sensitive settings temporarily
- Or try different symbols

---

### Problem 4: Telegram not sending

**Causes:**
- ✅ .env file missing/incorrect
- ✅ Bot token wrong
- ✅ Chat ID wrong

**Solution:**
```bash
# Check .env file exists
type .env

# Test Telegram
python telegram_bot.py test

# Get new chat ID
python telegram_bot.py get_chat_id
```

---

## ✅ VERIFICATION CHECKLIST

**Check these off as you complete them:**

- [ ] Updated config.py with 2 strategies only
- [ ] Set `STRATEGY_VOTE_REQUIRED = 'any'` (for testing)
- [ ] Set `PERIOD = '3mo'` or less
- [ ] Ran `python signal_checker.py`
- [ ] Saw at least 1 signal in checker
- [ ] Ran `python telegram_bot.py test`
- [ ] Received test message on Telegram
- [ ] Ran `python scheduler.py --interval 1h`
- [ ] Scheduler shows "Analyzing..." messages
- [ ] Received signal on Telegram (if market open)

---

## 🎯 QUICK FIX - Copy This to config.py

**If nothing works, copy this ENTIRE section to your config.py:**

```python
# ========== TEMPORARY TEST CONFIG ==========
# This WILL give you signals for testing
# After confirming it works, adjust back

STRATEGIES_ENABLED = {
    'ma_crossover': True,
    'rsi': True,
    'macd': False,
    'bollinger': False,
    'volume': False
}

STRATEGY_VOTE_REQUIRED = 'any'  # ANY strategy triggers signal

MA_FAST_PERIOD = 5
MA_SLOW_PERIOD = 15
RSI_PERIOD = 14
RSI_OVERSOLD = 40
RSI_OVERBOUGHT = 60

PERIOD = '2mo'
TIMEFRAME = '1d'

PAPER_TRADING = True
INITIAL_CAPITAL = 100.00
STOP_LOSS_PERCENT = 0.05
TAKE_PROFIT_PERCENT = 0.10
MAX_POSITION_SIZE = 0.3
# ========== END TEST CONFIG ==========
```

**Then run:**
```bash
python signal_checker.py
```

**You WILL see signals!**

---

## 🎯 After You See Signals Working

**Once confirmed bot works, switch back to quality settings:**

```python
STRATEGY_VOTE_REQUIRED = 'all'  # Both must agree
MA_FAST_PERIOD = 10
MA_SLOW_PERIOD = 30
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
```

**This gives fewer but BETTER quality signals!**

---

## 📞 Still Not Working?

**Run this and share the output with me:**

```bash
python signal_checker.py > signal_check_output.txt
notepad signal_check_output.txt
```

**Share the output and I'll help debug!**

---

## 🎉 Success Indicators

**You'll know it's working when:**

✅ `signal_checker.py` shows signals
✅ Telegram test works
✅ Scheduler shows "Analyzing..." every hour
✅ Telegram receives: `🟢 BUY AAPL at $180.50`
✅ Terminal shows: "✅ Executed: Bought 1 share"

---

**Follow these steps and you WILL get signals! 🎯**
