# 🪟 Complete Windows Setup Guide for Beginners

This guide will walk you through **every single step** to get the trading bot running on Windows.

---

## 📋 Pre-Setup Checklist

Before we begin, make sure you have:
- [ ] Windows 10 or Windows 11
- [ ] Internet connection
- [ ] Administrator access on your computer
- [ ] At least 1 GB free space

---

## Step 1: Install Python (15 minutes)

### Download Python:

1. Open your web browser (Chrome, Edge, Firefox)

2. Go to: **https://www.python.org/downloads/**

3. Click the big yellow button "Download Python 3.11.x"

4. Wait for the download (python-3.11.x-amd64.exe, about 25 MB)

### Install Python:

1. Find the downloaded file (usually in your Downloads folder)

2. **Double-click** the installer file

3. ⚠️ **IMPORTANT:** Check the box "Add Python to PATH"
   - This is at the BOTTOM of the installer window
   - DON'T skip this step!

4. Click **"Install Now"**

5. Wait 2-3 minutes for installation

6. Click **"Close"** when done

### Verify Installation:

1. Press **Windows Key + R**

2. Type: `cmd` and press Enter
   - This opens Command Prompt (black window)

3. Type: `python --version` and press Enter

4. You should see: `Python 3.11.x`

✅ If you see the version number, Python is installed!
❌ If you see "not recognized", restart your computer and try again

---

## Step 2: Create Project Folder (5 minutes)

### Option A: Using File Explorer (Easy)

1. Open **File Explorer** (folder icon on taskbar)

2. Navigate to your **Documents** folder

3. Right-click in empty space → **New** → **Folder**

4. Name it: `algo_trading_bot`

5. Open the folder (double-click)

6. Copy **all the bot files** into this folder:
   - config.py
   - model.py
   - view.py
   - controller.py
   - main.py
   - requirements.txt
   - README.md
   - quick_start.py

### Option B: Using Command Line (Advanced)

1. Open Command Prompt:
   - Press **Windows Key + R**
   - Type: `cmd` and press Enter

2. Navigate to Documents:
```bash
cd Documents
```

3. Create folder:
```bash
mkdir algo_trading_bot
cd algo_trading_bot
```

4. Copy your bot files here

---

## Step 3: Install Required Packages (10 minutes)

### Open Command Prompt in Project Folder:

#### Method 1: From File Explorer (Easiest)
1. Open File Explorer to your `algo_trading_bot` folder
2. Click in the **address bar** at the top
3. Type: `cmd` and press Enter
4. Command Prompt opens in your folder!

#### Method 2: Navigate in Command Prompt
1. Open Command Prompt (Windows Key + R, type `cmd`)
2. Type: `cd Documents\algo_trading_bot`
3. Press Enter

### Install Packages:

1. In Command Prompt, type:
```bash
pip install -r requirements.txt
```

2. Press Enter

3. Wait 2-5 minutes while it downloads and installs

4. You'll see messages like:
   ```
   Collecting pandas...
   Downloading pandas-2.x.x...
   Successfully installed pandas-2.x.x numpy-1.x.x ...
   ```

### Troubleshooting:

**If you see "pip is not recognized":**
```bash
python -m pip install -r requirements.txt
```

**If packages fail to install:**
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Step 4: Test Your Installation (5 minutes)

Still in Command Prompt in your project folder:

```bash
python quick_start.py
```

You should see:
```
🔍 Testing package installations...

✅ pandas          - Data manipulation
✅ numpy           - Numerical computations
✅ yfinance        - Stock data fetching
✅ matplotlib      - Chart creation

🎉 All packages installed successfully!
```

If you see all ✅ checkmarks, you're ready!

---

## Step 5: Configure the Bot (5 minutes)

1. Open `config.py` with Notepad or VS Code

2. Review settings (defaults are good for learning):
```python
INITIAL_CAPITAL = 100.00      # Starting money
SYMBOLS = ['AAPL']            # Stocks to trade
MA_FAST_PERIOD = 10           # Fast moving average
MA_SLOW_PERIOD = 30           # Slow moving average
```

3. You can change these later!

4. Save and close

---

## Step 6: Run Your First Backtest! (2 minutes)

In Command Prompt (in your project folder):

```bash
python main.py
```

What happens:
1. Bot downloads AAPL stock data (6 months)
2. Calculates moving averages
3. Simulates trades
4. Shows performance
5. Creates charts

You should see output like:
```
🚀 Trading Bot Initialized!
💰 Starting Capital: $100.00
📈 Strategy: Moving Average Crossover

📊 Fetching data for AAPL...
✅ Downloaded 126 data points
```

Wait about 30 seconds for completion.

---

## Step 7: Understand the Results

### Look for these sections:

1. **Market Data Summary:**
```
📊 MARKET DATA SUMMARY - AAPL
Close Price: $180.50
Fast MA (10): $181.20
Slow MA (30): $178.90
```

2. **Trade Signals:**
```
🟢 GOLDEN CROSS DETECTED for AAPL!
→ BULLISH signal (uptrend starting)
```

3. **Trade Execution:**
```
✅ BUY ORDER EXECUTED
Shares: 1
Price: $180.50
```

4. **Performance Metrics:**
```
📊 PERFORMANCE METRICS
Total Trades: 5
Winning Trades: 3 🎉
Win Rate: 60.00%
Total Return: +15.30%
```

5. **Chart:**
- A PNG file is created: `AAPL_chart.png`
- Find it in your project folder
- Open with any image viewer

---

## Common Issues and Solutions

### Issue 1: "Python not recognized"
**Solution:**
- Restart computer
- Reinstall Python (check "Add to PATH")
- Or use full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`

### Issue 2: "No module named..."
**Solution:**
```bash
pip install [module_name]
```
Example:
```bash
pip install pandas
```

### Issue 3: Can't download stock data
**Solution:**
- Check internet connection
- Try different stock: Change AAPL to MSFT in config.py
- Yahoo Finance might be temporarily down (wait and retry)

### Issue 4: Charts not showing
**Solution:**
- Charts are saved as PNG files, not displayed
- Look for `AAPL_chart.png` in your folder
- Open with Photos or any image viewer

### Issue 5: Permission errors
**Solution:**
- Run Command Prompt as Administrator
- Right-click Command Prompt → "Run as Administrator"

---

## Next Steps

### 1. Experiment with Settings
Edit `config.py`:
- Try different stocks: `SYMBOLS = ['MSFT']`
- Change MA periods: `MA_FAST_PERIOD = 20`
- Adjust capital: `INITIAL_CAPITAL = 500.00`

### 2. Analyze Single Stocks
```bash
python main.py analyze AAPL
python main.py analyze MSFT
python main.py analyze GOOGL
```

### 3. Learn from the Code
Open each file and read the comments:
1. Start with `main.py` (entry point)
2. Then `controller.py` (orchestration)
3. Then `model.py` (the brain)
4. Finally `view.py` (display)

### 4. Keep a Trading Journal
Document:
- What settings you tried
- What results you got
- What you learned
- Ideas for improvement

---

## Recommended Development Setup

### Install VS Code (Optional but Recommended):

1. Download from: **https://code.visualstudio.com/**

2. Install VS Code

3. Open VS Code

4. Install Python extension:
   - Click Extensions icon (left sidebar)
   - Search "Python"
   - Click Install on "Python" by Microsoft

5. Open your project:
   - File → Open Folder
   - Select `algo_trading_bot` folder

6. Benefits:
   - Syntax highlighting
   - Autocomplete
   - Integrated terminal
   - Debugging tools

### VS Code Tips:

- **Run in terminal:** Ctrl + `
- **Run file:** Click green play button
- **Auto-save:** File → Auto Save

---

## Windows-Specific Tips

### Create Desktop Shortcut:

1. Right-click on Desktop → New → Shortcut

2. Location:
```
cmd /k "cd /d C:\Users\YourName\Documents\algo_trading_bot && python main.py"
```
(Replace YourName with your username)

3. Name it: "Trading Bot"

4. Click Finish

5. Double-click to run bot anytime!

### Schedule Automatic Runs:

Use Windows Task Scheduler to run bot daily:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily
4. Action: Start a Program
5. Program: `python`
6. Arguments: `C:\Users\YourName\Documents\algo_trading_bot\main.py`

---

## Getting Help

### Before Asking for Help:

1. Read error messages carefully
2. Check this guide's "Common Issues"
3. Read README.md in project folder
4. Search error message on Google

### Where to Get Help:

- Python beginners: r/learnpython (Reddit)
- Trading questions: r/algotrading (Reddit)
- General programming: Stack Overflow

### What to Include When Asking:

1. What you're trying to do
2. What you expected to happen
3. What actually happened
4. Full error message (if any)
5. Your operating system (Windows 10/11)
6. Python version

---

## Final Checklist

Before you start experimenting:

- [ ] Python installed and working
- [ ] Project folder created
- [ ] All bot files in folder
- [ ] Packages installed (quick_start.py passed)
- [ ] Successfully ran first backtest
- [ ] Chart image created
- [ ] Read the README.md

---

## Safety Reminders

1. ⚠️ This is **paper trading** (simulated)
2. ⚠️ Start with small amounts if you go live later
3. ⚠️ Never invest money you can't afford to lose
4. ⚠️ Past performance ≠ future results
5. ⚠️ This is for education, not financial advice

---

## Celebration Time! 🎉

If you've gotten this far, congratulations!

You have:
✅ Set up a Python development environment
✅ Installed packages using pip
✅ Organized a project structure
✅ Run an algorithmic trading bot
✅ Generated analytical charts

These are valuable skills that go beyond just trading!

**Now go explore, experiment, and learn! 🚀**
