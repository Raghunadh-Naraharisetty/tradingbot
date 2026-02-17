@echo off
:: Trading Bot Scheduler
:: Runs during market hours automatically

:: Change to bot directory
cd C:\Users\Raghu\tradingbot

:: Activate virtual environment (if you have one)
:: call venv\Scripts\activate

:: Run scheduler for 8 hours (market hours)
:: Will auto-stop after 8 hours
timeout /t 5 /nobreak > nul
python scheduler.py --interval 1h

:: Keep window open if error occurs
pause
```

**Save and close!**

---

### Step 2: Test the Batch File

**Double-click `start_trading_bot.bat`**

**You should see:**
```
✅ Loaded 6 symbols from symbols.txt
🤖 Scheduler initialized
   Interval: 1h
...
```

**If it works, press Ctrl+C to stop.**

---

### Step 3: Open Task Scheduler

**Press `Win + R`, type:**
```
taskschd.msc