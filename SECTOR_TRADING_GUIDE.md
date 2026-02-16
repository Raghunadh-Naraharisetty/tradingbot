# 📊 SECTOR-BASED TRADING GUIDE

Your bot now supports **100+ stocks across 7 major sectors**!

---

## 🎯 Available Sectors

### 1. **Technology / IT** (20 stocks)
Top tech companies: AAPL, MSFT, GOOGL, META, NVDA, etc.
- **Best for:** Growth trading, momentum strategies
- **Volatility:** Medium to High
- **Trend:** Usually strong trends

### 2. **Semiconductors / Chips** (20 stocks)
Chip manufacturers: NVDA, AMD, INTC, TSM, etc.
- **Best for:** Tech enthusiasts, high volatility trading
- **Volatility:** High
- **Trend:** Very cyclical, strong moves

### 3. **Healthcare** (20 stocks)
Healthcare providers & equipment: UNH, JNJ, TMO, etc.
- **Best for:** Defensive trading, stability
- **Volatility:** Low to Medium
- **Trend:** Steady, less volatile

### 4. **Pharmaceuticals** (20 stocks)
Drug manufacturers: PFE, MRK, LLY, ABBV, etc.
- **Best for:** Event-driven trading (drug approvals)
- **Volatility:** Medium
- **Trend:** Mixed, news-driven

### 5. **Financial Services** (20 stocks)
Banks & financial institutions: JPM, BAC, GS, etc.
- **Best for:** Economic cycle trading
- **Volatility:** Medium
- **Trend:** Economic-dependent

### 6. **Energy** (20 stocks)
Oil, gas, energy companies: XOM, CVX, COP, etc.
- **Best for:** Commodity traders
- **Volatility:** High
- **Trend:** Commodity price-driven

### 7. **Consumer / Retail** (20 stocks)
Consumer companies: AMZN, TSLA, WMT, HD, etc.
- **Best for:** Consumer trend followers
- **Volatility:** Medium to High
- **Trend:** Mixed, consumer-dependent

---

## 🚀 Quick Start Options

### Option 1: Start Small (Recommended for Beginners)
**Trade top 5 stocks from ONE sector**

Open `config.py` and choose:

```python
# Technology
SYMBOLS = TECH_SYMBOLS[:5]  # AAPL, MSFT, GOOGL, META, NVDA

# OR Semiconductors
SYMBOLS = CHIP_SYMBOLS[:5]  # NVDA, AMD, INTC, TSM, AVGO

# OR Healthcare
SYMBOLS = HEALTHCARE_SYMBOLS[:5]  # UNH, JNJ, LLY, ABBV, MRK

# OR Pharma
SYMBOLS = PHARMA_SYMBOLS[:5]  # PFE, MRK, ABBV, LLY, BMY
```

**Runtime:** ~1-2 minutes

---

### Option 2: Diversified Portfolio (Intermediate)
**Mix stocks from multiple sectors**

```python
# Top 3 from each of 3 sectors (9 stocks total)
SYMBOLS = (TECH_SYMBOLS[:3] + 
           HEALTHCARE_SYMBOLS[:3] + 
           FINANCE_SYMBOLS[:3])

# Result: AAPL, MSFT, GOOGL, UNH, JNJ, LLY, JPM, BAC, WFC
```

**Runtime:** ~2-3 minutes

---

### Option 3: Full Sector (Advanced)
**Trade ALL 20 stocks in one sector**

```python
# All tech stocks
SYMBOLS = TECH_SYMBOLS

# OR all chip stocks
SYMBOLS = CHIP_SYMBOLS

# OR all healthcare stocks
SYMBOLS = HEALTHCARE_SYMBOLS
```

**Runtime:** ~3-5 minutes

---

### Option 4: Multi-Sector Portfolio (Expert)
**Top 2 from each sector (14 stocks)**

```python
SYMBOLS = (TECH_SYMBOLS[:2] + 
           CHIP_SYMBOLS[:2] + 
           HEALTHCARE_SYMBOLS[:2] + 
           PHARMA_SYMBOLS[:2] + 
           FINANCE_SYMBOLS[:2] + 
           ENERGY_SYMBOLS[:2] + 
           CONSUMER_SYMBOLS[:2])
```

**Runtime:** ~3-4 minutes

---

### Option 5: Everything (For the Brave!)
**All 100+ stocks across all sectors**

```python
SYMBOLS = (TECH_SYMBOLS + 
           CHIP_SYMBOLS + 
           HEALTHCARE_SYMBOLS + 
           PHARMA_SYMBOLS + 
           FINANCE_SYMBOLS + 
           ENERGY_SYMBOLS + 
           CONSUMER_SYMBOLS)
```

**⚠️ WARNING:**
- Downloads data for 100+ stocks
- Takes 5-10 minutes
- Generates 100+ charts
- Use only if you have time!

**Runtime:** ~10-15 minutes

---

## 📋 Step-by-Step Instructions

### Step 1: Open config.py

Navigate to: `C:\Users\Raghu\tradingbot\config.py`

### Step 2: Find the "SYMBOL SELECTION" Section

Scroll down to this part:
```python
# =============================================================================
# SYMBOL SELECTION
# =============================================================================
```

### Step 3: Choose Your Option

**Uncomment** (remove the `#`) from the option you want:

**Example - Want to trade top 5 tech stocks:**
```python
# BEFORE (default)
SYMBOLS = TECH_SYMBOLS[:5]  # Top 5 tech stocks

# You're good! This is already active.
```

**Example - Want to trade chip stocks instead:**
```python
# BEFORE
SYMBOLS = TECH_SYMBOLS[:5]  # Top 5 tech stocks
# SYMBOLS = CHIP_SYMBOLS[:5]  # Top 5 chip stocks

# AFTER (comment out tech, uncomment chips)
# SYMBOLS = TECH_SYMBOLS[:5]  # Top 5 tech stocks
SYMBOLS = CHIP_SYMBOLS[:5]  # Top 5 chip stocks
```

### Step 4: Save and Run

```bash
python main.py
```

---

## 🎓 Understanding the Syntax

### `[:5]` - Get first 5 stocks
```python
TECH_SYMBOLS[:5]  # Gets AAPL, MSFT, GOOGL, META, NVDA
```

### `[:10]` - Get first 10 stocks
```python
TECH_SYMBOLS[:10]  # Gets first 10 tech stocks
```

### `[5:10]` - Get stocks 6-10
```python
TECH_SYMBOLS[5:10]  # Gets positions 5-9 (AMD, INTC, CRM, ORCL, ADBE)
```

### `+` - Combine lists
```python
TECH_SYMBOLS[:3] + HEALTHCARE_SYMBOLS[:3]
# Gets: AAPL, MSFT, GOOGL, UNH, JNJ, LLY
```

---

## 💡 Strategy Recommendations by Sector

### Tech / Semiconductors
✅ **Best strategy:** Hybrid (MA + RSI)
- High volatility = clear signals
- Strong trends = MA works well
- Momentum is key = RSI helps

**Settings:**
```python
MA_FAST_PERIOD = 10
MA_SLOW_PERIOD = 30
RSI_PERIOD = 14
```

### Healthcare / Pharma
✅ **Best strategy:** Hybrid with slower MAs
- Lower volatility = need patience
- Steadier trends = slower MAs better

**Settings:**
```python
MA_FAST_PERIOD = 20
MA_SLOW_PERIOD = 50
RSI_PERIOD = 14
```

### Finance / Energy
✅ **Best strategy:** Standard Hybrid
- Moderate volatility
- Economic cycles important

**Settings:**
```python
MA_FAST_PERIOD = 10
MA_SLOW_PERIOD = 30
RSI_PERIOD = 14
```

### Consumer / Retail
✅ **Best strategy:** Faster signals
- News-driven moves
- Quick trends

**Settings:**
```python
MA_FAST_PERIOD = 9
MA_SLOW_PERIOD = 21
RSI_PERIOD = 14
```

---

## 📊 Performance Tips

### Tip 1: Start with Familiar Sectors
Trade sectors you understand:
- Know tech? Start with TECH_SYMBOLS
- Follow healthcare news? Try HEALTHCARE_SYMBOLS
- Interest in chips? Go with CHIP_SYMBOLS

### Tip 2: Avoid Overlaps
Some stocks appear in multiple sectors (e.g., NVDA in both TECH and CHIP). The bot handles duplicates, but be aware!

### Tip 3: Diversification is Good
Don't put all eggs in one basket:
```python
# Good: Mix of sectors
SYMBOLS = TECH_SYMBOLS[:2] + HEALTHCARE_SYMBOLS[:2] + FINANCE_SYMBOLS[:2]

# Risky: All in one volatile sector
SYMBOLS = CHIP_SYMBOLS  # All chips = high correlated risk
```

### Tip 4: Monitor Execution Time
More stocks = longer runtime:
- 5 stocks = ~1-2 minutes
- 10 stocks = ~2-3 minutes
- 20 stocks = ~3-5 minutes
- 50+ stocks = ~10+ minutes

### Tip 5: Quality Over Quantity
Better to trade 5 stocks well than 50 stocks poorly!

---

## 🔧 Advanced Customization

### Custom Stock List

Want specific stocks?
```python
# Your personal watchlist
SYMBOLS = [
    'AAPL',   # Tech
    'NVDA',   # Chips
    'UNH',    # Healthcare
    'JPM',    # Finance
    'XOM',    # Energy
    'AMZN'    # Consumer
]
```

### Sector Rotation Strategy

Trade one sector per week:
```python
# Week 1
SYMBOLS = TECH_SYMBOLS[:10]

# Week 2
SYMBOLS = HEALTHCARE_SYMBOLS[:10]

# Week 3
SYMBOLS = FINANCE_SYMBOLS[:10]

# Compare which sector performs best!
```

### Market Cap Based

Trade by size:
```python
# Large caps (stable, lower volatility)
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META']

# Mid caps (balanced)
SYMBOLS = ['AMD', 'CRM', 'ADBE', 'INTU', 'NOW']

# Mix
SYMBOLS = ['AAPL', 'MSFT', 'AMD', 'CRM']  # 2 large + 2 mid
```

---

## ⚠️ Important Notes

### 1. Data Download Time
- Each stock requires API call to Yahoo Finance
- Too many stocks = rate limiting possible
- If errors occur, reduce number of stocks

### 2. Capital Requirements
With $100 starting capital:
- Trading 5 stocks = ~$20 per stock max
- Trading 20 stocks = ~$5 per stock max
- Some expensive stocks (like GOOGL ~$140) might not be buyable

**Solution:** Increase capital in config.py:
```python
INITIAL_CAPITAL = 500.00  # More capital = more stocks tradeable
```

### 3. Chart Generation
- Bot generates 1 chart per stock
- 20 stocks = 20 chart files in your folder
- Make sure you have space!

### 4. Paper Trading
- All trading is simulated
- Perfect for testing multiple sectors
- No real money at risk

---

## 🎯 Recommended Starting Configurations

### For Learning (Beginner)
```python
# Start here - 3 familiar stocks
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']
```

### For Practice (Intermediate)
```python
# Top 5 from your favorite sector
SYMBOLS = TECH_SYMBOLS[:5]
```

### For Testing (Advanced)
```python
# Diversified portfolio
SYMBOLS = (TECH_SYMBOLS[:3] + 
           HEALTHCARE_SYMBOLS[:3] + 
           FINANCE_SYMBOLS[:2])
```

### For Analysis (Expert)
```python
# Full sector analysis
SYMBOLS = TECH_SYMBOLS  # All 20 tech stocks
```

---

## 📈 Comparing Sectors

After running different sectors, compare:

| Sector | Win Rate | Avg Return | Best Stock | Worst Stock |
|--------|----------|------------|------------|-------------|
| Tech | ? | ? | ? | ? |
| Healthcare | ? | ? | ? | ? |
| Finance | ? | ? | ? | ? |

Keep a journal of your findings!

---

## 🚀 Quick Commands

```bash
# Test top 5 tech stocks
python main.py

# Analyze single stock from any sector
python main.py analyze NVDA
python main.py analyze JPM
python main.py analyze UNH

# Run and compare
python main.py  # After changing config
```

---

## ❓ Troubleshooting

### "Can't download data for [SYMBOL]"
- Stock might be delisted or ticker changed
- Remove from list or replace with alternative

### "Takes too long to run"
- Reduce number of stocks
- Start with top 5 from one sector

### "Not enough capital to trade"
- Increase INITIAL_CAPITAL in config.py
- OR trade cheaper stocks
- OR reduce number of symbols

### "Too many chart files"
- Normal! One per stock
- Delete old charts: `del *.png` in Windows CMD
- Or organize into folders

---

## 💡 Pro Tips

1. **Start small** - Master 5 stocks before adding more
2. **One sector at a time** - Understand sector behavior
3. **Keep notes** - Which sectors work best for you?
4. **Compare performance** - Which sector has best win rate?
5. **Adjust strategy** - Different sectors may need different settings

---

## 🎓 Learning Exercise

**Week-by-Week Sector Challenge:**

- **Week 1:** Trade TECH_SYMBOLS[:5]
- **Week 2:** Trade HEALTHCARE_SYMBOLS[:5]
- **Week 3:** Trade FINANCE_SYMBOLS[:5]
- **Week 4:** Compare results!

Which sector performed best? Why?

---

**Ready to explore multiple sectors? Edit config.py and run `python main.py`! 🚀📊**
