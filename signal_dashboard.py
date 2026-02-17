"""
SIGNAL_DASHBOARD.PY — 100% Alpaca Powered
==========================================
Everything comes from Alpaca:
  ✅ Symbols   → your Alpaca watchlist OR symbols you define here
  ✅ Price data → Alpaca Market Data API (not Yahoo Finance!)
  ✅ Portfolio  → Alpaca account
  ✅ Positions  → Alpaca open positions

Why not Yahoo Finance?
  - You already have Alpaca connected
  - Alpaca gives REAL-TIME data (paper account still gets real prices)
  - Yahoo Finance has delays and rate limits
  - One source of truth = no confusion

Deploy: streamlit run signal_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import os

# ── Secrets: works locally (.env) AND on Streamlit Cloud ─────
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        return os.getenv(key, default)

ALPACA_KEY    = get_secret("ALPACA_API_KEY")
ALPACA_SECRET = get_secret("ALPACA_SECRET_KEY")
ALPACA_URL    = get_secret("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# ── ALL YOUR SYMBOLS (keep in sync with symbols.txt) ─────────
# Add/remove symbols here to match your symbols.txt
ALL_SYMBOLS = [
    # Tech
    "AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA",
    "AMD",  "INTC", "AMZN",  "NFLX", "CRM",  "ORCL",
    # Healthcare
    "UNH",  "JNJ",  "LLY",   "PFE",
    # Finance
    "JPM",  "BAC",  "GS",    "MS",
    # Energy
    "XOM",  "CVX",
    # ETFs (optional)
    "SPY",  "QQQ",  "IWM",   "VXX",
]

# ── Strategy settings ─────────────────────────────────────────
MA_FAST    = 5
MA_SLOW    = 15
RSI_PERIOD = 14
RSI_BUY    = 40   # RSI below this = BUY
RSI_SELL   = 60   # RSI above this = SELL

# ── Market clocks ─────────────────────────────────────────────
MARKETS = [
    {"name": "NEW YORK", "short": "NYSE", "flag": "🇺🇸",
     "tz": "America/New_York", "open": (9,30), "close": (16,0)},
    {"name": "MUMBAI",   "short": "NSE",  "flag": "🇮🇳",
     "tz": "Asia/Kolkata",     "open": (9,15), "close": (15,30)},
    {"name": "LONDON",   "short": "LSE",  "flag": "🇬🇧",
     "tz": "Europe/London",    "open": (8,0),  "close": (16,30)},
    {"name": "TOKYO",    "short": "TSE",  "flag": "🇯🇵",
     "tz": "Asia/Tokyo",       "open": (9,0),  "close": (15,30)},
]

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AlphaSignal — Raghu",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ─────────────────────────────────────────────────────────────
# ALPACA CLIENT
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_alpaca():
    """Get Alpaca REST client (cached, shared across sessions)."""
    if not (ALPACA_KEY and ALPACA_SECRET):
        return None
    try:
        from alpaca_trade_api import REST
        return REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL)
    except Exception as e:
        st.error(f"Alpaca init error: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# DATA FUNCTIONS — ALL FROM ALPACA
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def get_alpaca_bars(symbol: str, timeframe: str = "1Day", limit: int = 60):
    """
    Fetch OHLCV bars from Alpaca Market Data API.
    Uses Alpaca — NOT Yahoo Finance!
    """
    api = get_alpaca()
    if api is None:
        return None
    try:
        bars = api.get_bars(symbol, timeframe, limit=limit).df
        if bars.empty:
            return None
        bars = bars.rename(columns={
            "open": "Open", "high": "High",
            "low":  "Low",  "close": "Close", "volume": "Volume"
        })
        return bars
    except Exception:
        return None


@st.cache_data(ttl=20, show_spinner=False)
def get_portfolio():
    """Get full portfolio from Alpaca."""
    api = get_alpaca()
    if api is None:
        return None
    try:
        acc = api.get_account()
        pos = api.list_positions()
        return {
            "value":  float(acc.portfolio_value),
            "cash":   float(acc.cash),
            "bp":     float(acc.buying_power),
            "equity": float(acc.equity),
            "positions": [{
                "sym":   p.symbol,
                "qty":   float(p.qty),
                "entry": float(p.avg_entry_price),
                "val":   float(p.market_value),
                "pl":    float(p.unrealized_pl),
                "plpct": float(p.unrealized_plpc) * 100,
            } for p in pos]
        }
    except Exception as e:
        return None


@st.cache_data(ttl=120, show_spinner=False)
def analyze_symbol(symbol: str):
    """
    Fetch Alpaca bars and calculate MA + RSI signals.
    Returns dict with signal info or None if no data.
    """
    df = get_alpaca_bars(symbol, "1Day", 60)
    if df is None or len(df) < MA_SLOW + 5:
        return None

    close = df["Close"].squeeze().astype(float)

    # Moving averages
    df["maf"] = close.rolling(MA_FAST).mean()
    df["mas"] = close.rolling(MA_SLOW).mean()

    # RSI
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
    loss  = (-delta.clip(upper=0)).rolling(RSI_PERIOD).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    cur  = df.iloc[-1]
    prev = df.iloc[-2]

    price   = float(cur["Close"])
    rsi_val = float(cur["rsi"]) if not np.isnan(cur["rsi"]) else 50.0
    maf_v   = float(cur["maf"]) if not np.isnan(cur["maf"]) else price
    mas_v   = float(cur["mas"]) if not np.isnan(cur["mas"]) else price
    prev_p  = float(prev["Close"])
    chg_pct = (price - prev_p) / prev_p * 100

    # MA crossover direction
    pmaf = float(prev["maf"]) if not np.isnan(prev["maf"]) else maf_v
    pmas = float(prev["mas"]) if not np.isnan(prev["mas"]) else mas_v
    ma_sig = "BUY" if maf_v > mas_v else "SELL" if maf_v < mas_v else "HOLD"

    # RSI signal
    rsi_sig = "BUY" if rsi_val < RSI_BUY else "SELL" if rsi_val > RSI_SELL else "HOLD"

    # Final: require BOTH to agree (cleaner signals)
    if ma_sig == "BUY" and rsi_sig == "BUY":
        final = "BUY"
    elif ma_sig == "SELL" and rsi_sig == "SELL":
        final = "SELL"
    else:
        final = "HOLD"

    return {
        "sym": symbol, "price": price, "chg": chg_pct,
        "rsi": rsi_val, "maf": maf_v, "mas": mas_v,
        "ma_sig": ma_sig, "rsi_sig": rsi_sig, "signal": final,
    }


@st.cache_data(ttl=120, show_spinner=False)
def analyze_all():
    """Analyze all symbols using Alpaca data."""
    results = []
    for sym in ALL_SYMBOLS:
        r = analyze_symbol(sym)
        if r:
            results.append(r)
    return results


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def market_status(m):
    tz  = pytz.timezone(m["tz"])
    now = datetime.now(tz)
    wd  = now.weekday() < 5
    oh, om = m["open"];  ch, cm = m["close"]
    ot = now.replace(hour=oh, minute=om, second=0, microsecond=0)
    ct = now.replace(hour=ch, minute=cm, second=0, microsecond=0)
    return now.strftime("%H:%M:%S"), now.strftime("%d %b"), (wd and ot <= now <= ct)


# ─────────────────────────────────────────────────────────────
# CSS — Bloomberg Terminal Aesthetic
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:      #060a10;
    --surf:    #0c1220;
    --bdr:     #162030;
    --bdr2:    #1e3048;
    --gold:    #c9a84c;
    --gold2:   #e8c97a;
    --green:   #0dff8c;
    --green2:  #00c853;
    --red:     #ff3d5a;
    --text:    #c8d8e8;
    --muted:   #4a6278;
    --white:   #eef4ff;
}
html, body, [class*="css"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Mono', monospace;
}
.main .block-container { padding: 1.5rem 2.5rem 3rem; max-width: 1700px; }
#MainMenu, footer, header, .stDeployButton { display:none !important; }

/* HEADER */
.hdr { padding-bottom: 1.5rem; border-bottom: 1px solid var(--bdr2); margin-bottom: 1.8rem; }
.hdr-brand {
    font-family: 'Syne', sans-serif; font-size: 30px; font-weight: 800;
    background: linear-gradient(135deg, var(--gold2), var(--gold), #a07830);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hdr-sub { font-size: 11px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; margin-top: 3px; }
.live-dot {
    display: inline-block; width: 7px; height: 7px;
    background: var(--green); border-radius: 50%;
    box-shadow: 0 0 8px var(--green);
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.85)} }

/* SECTION */
.sec {
    font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase; color: var(--gold);
    border-left: 2px solid var(--gold); padding-left: 10px;
    margin: 2rem 0 1rem;
}

/* SHARE BANNER */
.share {
    background: linear-gradient(135deg,#0d1a2a,#0c2040);
    border: 1px solid var(--bdr2); border-radius: 8px;
    padding: 14px 20px; margin-bottom: 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
}
.share-url { font-family:'Syne',sans-serif; font-size:14px; font-weight:700; color:var(--gold2); }

/* CLOCKS */
.clk {
    background: var(--surf); border: 1px solid var(--bdr);
    border-radius: 8px; padding: 18px 16px; position: relative;
}
.clk::before { content:''; position:absolute; top:0;left:0;right:0;height:2px; background:var(--bdr2); }
.clk.open { border-color: var(--bdr2); }
.clk.open::before { background: var(--green2); }
.clk-name { font-family:'Syne',sans-serif; font-size:10px; font-weight:700; letter-spacing:1.5px; color:var(--muted); text-transform:uppercase; margin-bottom:8px; }
.clk-time { font-size:26px; font-weight:500; color:var(--white); letter-spacing:1px; margin-bottom:3px; }
.clk-date { font-size:11px; color:var(--muted); margin-bottom:8px; }
.badge-open { font-size:10px; font-weight:700; color:var(--green); letter-spacing:1px; text-transform:uppercase; }
.badge-open::before { content:''; display:inline-block; width:6px;height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 6px var(--green); margin-right:5px; animation:pulse 1.5s infinite; }
.badge-closed { font-size:10px; color:var(--muted); letter-spacing:1px; text-transform:uppercase; }

/* STAT CARDS */
.stat { background:var(--surf); border:1px solid var(--bdr); border-radius:8px; padding:20px; }
.stat-lbl { font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--muted); margin-bottom:10px; }
.stat-val { font-family:'Syne',sans-serif; font-size:26px; font-weight:700; color:var(--white); }
.stat-val.gold { color:var(--gold2); }
.stat-val.pos  { color:var(--green); }
.stat-val.neg  { color:var(--red); }

/* SIGNAL SUMMARY */
.sc { background:var(--surf); border:1px solid var(--bdr); border-radius:8px; padding:20px; text-align:center; }
.sc-lbl { font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--muted); margin-bottom:8px; }
.sc-n { font-family:'Syne',sans-serif; font-size:38px; font-weight:800; }
.sc-n.buy { color:var(--green); }
.sc-n.sell { color:var(--red); }
.sc-n.hold { color:var(--muted); }

/* SIGNAL CARDS */
.sig { background:var(--surf); border:1px solid var(--bdr); border-radius:8px; padding:16px 20px; margin-bottom:10px; position:relative; overflow:hidden; }
.sig::before { content:''; position:absolute; left:0;top:0;bottom:0;width:3px; }
.sig.buy  { border-color:#0d2818; }
.sig.buy::before  { background:var(--green); box-shadow:0 0 10px var(--green); }
.sig.sell { border-color:#2d0a0a; }
.sig.sell::before { background:var(--red);   box-shadow:0 0 10px var(--red); }
.sig-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; }
.sig-sym { font-family:'Syne',sans-serif; font-size:22px; font-weight:800; color:var(--white); }
.sig-act { font-size:10px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin-top:2px; }
.sig-act.buy { color:var(--green); }
.sig-act.sell { color:var(--red); }
.sig-px { font-size:22px; font-weight:500; color:var(--white); text-align:right; }
.sig-chg { font-size:11px; text-align:right; }
.sig-chg.pos { color:var(--green); }
.sig-chg.neg { color:var(--red); }
.chips { display:flex; gap:7px; flex-wrap:wrap; margin-top:6px; }
.chip { font-size:10px; background:#0c1825; border:1px solid var(--bdr2); border-radius:4px; padding:3px 8px; color:var(--muted); }
.chip.abuy  { border-color:var(--green2); color:var(--green); }
.chip.asell { border-color:#c0392b; color:var(--red); }

/* EMPTY */
.empty { background:var(--surf); border:1px dashed var(--bdr2); border-radius:8px; padding:40px; text-align:center; color:var(--muted); }

/* WATCHING */
.ww { display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }
.wp { background:var(--surf); border:1px solid var(--bdr); border-radius:4px; padding:5px 12px; font-size:11px; letter-spacing:1px; color:var(--muted); }

/* POSITIONS */
.ph { display:grid; grid-template-columns:80px 60px 100px 110px 110px 90px; border-bottom:1px solid var(--bdr2); padding:8px 0; font-size:10px; letter-spacing:1.5px; text-transform:uppercase; color:var(--muted); }
.pr { display:grid; grid-template-columns:80px 60px 100px 110px 110px 90px; border-bottom:1px solid var(--bdr); padding:10px 0; font-size:12px; align-items:center; }
.pr-sym { font-family:'Syne',sans-serif; font-weight:700; color:var(--white); }

/* DATA SOURCE BADGE */
.ds-badge { display:inline-flex; align-items:center; gap:6px; background:#0c1825; border:1px solid var(--bdr2); border-radius:4px; padding:4px 10px; font-size:10px; color:var(--muted); letter-spacing:1px; }
.ds-badge .dot { width:5px;height:5px; border-radius:50%; background:var(--gold); }

/* FOOTER */
.ftr { margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--bdr); display:flex; justify-content:space-between; font-size:11px; color:var(--muted); }
.ftr-brand { font-family:'Syne',sans-serif; font-weight:700; color:var(--gold); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────────────────────
def render():
    now_utc = datetime.now(pytz.utc)
    pf = get_portfolio()
    connected = pf is not None

    # ── HEADER ───────────────────────────────────────────────
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f"""
        <div class='hdr'>
          <div>
            <div class='hdr-brand'>⚡ AlphaSignal</div>
            <div class='hdr-sub'>Paper Trading Monitor · by Raghu</div>
          </div>
          <div style='display:flex;align-items:center;gap:16px;margin-top:8px;'>
            <span class='ds-badge'><span class='dot'></span>DATA: ALPACA API</span>
            <span class='ds-badge'><span class='dot'></span>{len(ALL_SYMBOLS)} SYMBOLS</span>
            <span style='font-size:12px;color:var(--muted);'>
              <span class='live-dot'></span>
              {now_utc.strftime("%d %b %Y  %H:%M")} UTC
            </span>
          </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("⟳ Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── SHARE BANNER ─────────────────────────────────────────
    st.markdown("""
    <div class='share'>
      <div>
        <div style='font-size:11px;color:var(--muted);margin-bottom:4px;'>📤 SHARE THIS DASHBOARD</div>
        <div class='share-url'>https://alpacaintegration.streamlit.app</div>
      </div>
      <div style='font-size:11px;color:var(--muted);text-align:right;line-height:1.8;'>
        To make public:<br>
        ⚙️ Streamlit → Settings → Sharing → Public
      </div>
    </div>""", unsafe_allow_html=True)

    # ── CONNECTION STATUS ─────────────────────────────────────
    if not connected:
        st.warning("⚠️ Alpaca not connected. Go to Streamlit → Settings → Secrets and add your ALPACA_API_KEY and ALPACA_SECRET_KEY")

    # ── MARKET CLOCKS ─────────────────────────────────────────
    st.markdown("<div class='sec'>🌍 Global Market Hours</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, m in enumerate(MARKETS):
        t, d, is_open = market_status(m)
        badge = "<span class='badge-open'>OPEN</span>" if is_open else "<span class='badge-closed'>○ CLOSED</span>"
        with cols[i]:
            st.markdown(f"""
            <div class='clk {"open" if is_open else ""}'>
              <div class='clk-name'>{m['flag']} {m['name']} · {m['short']}</div>
              <div class='clk-time'>{t}</div>
              <div class='clk-date'>{d}</div>
              {badge}
            </div>""", unsafe_allow_html=True)

    # ── ALPACA PORTFOLIO ─────────────────────────────────────
    st.markdown("<div class='sec'>💼 Alpaca Portfolio (Paper Trading)</div>", unsafe_allow_html=True)
    if pf:
        start  = 100_000.0
        pl     = pf["value"] - start
        pl_pct = (pl / start) * 100
        pl_cls = "pos" if pl >= 0 else "neg"
        sign   = "+" if pl >= 0 else ""

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.markdown(f"""<div class='stat'>
              <div class='stat-lbl'>Portfolio Value</div>
              <div class='stat-val gold'>${pf['value']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with p2:
            st.markdown(f"""<div class='stat'>
              <div class='stat-lbl'>Cash Available</div>
              <div class='stat-val'>${pf['cash']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with p3:
            st.markdown(f"""<div class='stat'>
              <div class='stat-lbl'>Open Positions</div>
              <div class='stat-val'>{len(pf['positions'])}</div>
            </div>""", unsafe_allow_html=True)
        with p4:
            st.markdown(f"""<div class='stat'>
              <div class='stat-lbl'>Total Return</div>
              <div class='stat-val {pl_cls}'>
                {sign}${pl:,.2f}
                <span style='font-size:14px;'>&nbsp;{sign}{pl_pct:.2f}%</span>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='stat' style='text-align:center;'>
          <span style='color:var(--muted);'>Alpaca API not connected</span>
        </div>""", unsafe_allow_html=True)

    # ── SIGNALS ───────────────────────────────────────────────
    st.markdown(f"<div class='sec'>🎯 Live Signals — Alpaca Data · {len(ALL_SYMBOLS)} Symbols</div>",
                unsafe_allow_html=True)

    with st.spinner(f"Fetching data for {len(ALL_SYMBOLS)} symbols from Alpaca..."):
        data = analyze_all()

    if not data:
        st.warning("No data received from Alpaca. Market may be closed or API issue.")
        return

    buys  = [r for r in data if r["signal"] == "BUY"]
    sells = [r for r in data if r["signal"] == "SELL"]
    holds = [r for r in data if r["signal"] == "HOLD"]

    # Summary
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""<div class='sc'>
          <div class='sc-lbl'>Buy Signals</div>
          <div class='sc-n buy'>{len(buys)}</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class='sc'>
          <div class='sc-lbl'>Sell Signals</div>
          <div class='sc-n sell'>{len(sells)}</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""<div class='sc'>
          <div class='sc-lbl'>Monitoring</div>
          <div class='sc-n hold'>{len(holds)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def sig_card(r, side):
        cc   = "pos" if r["chg"] >= 0 else "neg"
        sign = "+" if r["chg"] >= 0 else ""
        mac  = f"a{side}" if r["ma_sig"]  == side.upper() else ""
        rsic = f"a{side}" if r["rsi_sig"] == side.upper() else ""
        lbl  = "▲ LONG · BUY" if side == "buy" else "▼ SHORT · SELL"
        return f"""
        <div class='sig {side}'>
          <div class='sig-top'>
            <div>
              <div class='sig-sym'>{r['sym']}</div>
              <div class='sig-act {side}'>{lbl}</div>
            </div>
            <div>
              <div class='sig-px'>${r['price']:.2f}</div>
              <div class='sig-chg {cc}'>{sign}{r['chg']:.2f}%</div>
            </div>
          </div>
          <div class='chips'>
            <span class='chip {mac}'>MA {r['ma_sig']}</span>
            <span class='chip {rsic}'>RSI {r['rsi']:.0f} · {r['rsi_sig']}</span>
            <span class='chip'>Fast ${r['maf']:.2f}</span>
            <span class='chip'>Slow ${r['mas']:.2f}</span>
          </div>
        </div>"""

    lcol, rcol = st.columns(2)

    with lcol:
        st.markdown("<div style='font-size:13px;font-weight:700;color:var(--green);font-family:Syne,sans-serif;margin-bottom:10px;'>▲ BUY OPPORTUNITIES</div>",
                    unsafe_allow_html=True)
        if buys:
            for r in buys:
                st.markdown(sig_card(r, "buy"), unsafe_allow_html=True)
        else:
            st.markdown("""<div class='empty'>
              <div style='font-size:26px;'>◌</div>
              <div style='margin-top:8px;font-size:13px;'>No buy signals right now</div>
              <div style='font-size:11px;opacity:.5;margin-top:4px;'>Market closed or no uptrend conditions</div>
            </div>""", unsafe_allow_html=True)

    with rcol:
        st.markdown("<div style='font-size:13px;font-weight:700;color:var(--red);font-family:Syne,sans-serif;margin-bottom:10px;'>▼ SELL SIGNALS</div>",
                    unsafe_allow_html=True)
        if sells:
            for r in sells:
                st.markdown(sig_card(r, "sell"), unsafe_allow_html=True)
        else:
            st.markdown("""<div class='empty'>
              <div style='font-size:26px;'>◌</div>
              <div style='margin-top:8px;font-size:13px;'>No sell signals right now</div>
              <div style='font-size:11px;opacity:.5;margin-top:4px;'>No overbought conditions found</div>
            </div>""", unsafe_allow_html=True)

    # ── MONITORING ────────────────────────────────────────────
    if holds:
        st.markdown("<div class='sec'>👁 Monitoring — Awaiting Signal</div>", unsafe_allow_html=True)
        pills = "".join([f"<span class='wp'>{r['sym']}</span>" for r in holds])
        st.markdown(f"<div class='ww'>{pills}</div>", unsafe_allow_html=True)

    # ── POSITIONS ─────────────────────────────────────────────
    if pf and pf["positions"]:
        st.markdown("<div class='sec'>📂 Open Positions (Alpaca Paper)</div>", unsafe_allow_html=True)
        st.markdown("""<div class='ph'>
          <span>SYMBOL</span><span>QTY</span><span>ENTRY</span>
          <span>MKT VALUE</span><span>P/L $</span><span>P/L %</span>
        </div>""", unsafe_allow_html=True)
        for p in pf["positions"]:
            cl = "var(--green)" if p["pl"] >= 0 else "var(--red)"
            s  = "+" if p["pl"] >= 0 else ""
            st.markdown(f"""<div class='pr'>
              <span class='pr-sym'>{p['sym']}</span>
              <span>{p['qty']:.0f}</span>
              <span>${p['entry']:.2f}</span>
              <span>${p['val']:,.2f}</span>
              <span style='color:{cl};'>{s}${p['pl']:.2f}</span>
              <span style='color:{cl};'>{s}{p['plpct']:.2f}%</span>
            </div>""", unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────
    st.markdown(f"""
    <div class='ftr'>
      <div>
        <span class='ftr-brand'>⚡ AlphaSignal</span>
        &nbsp;·&nbsp; Paper Trading Only · No Real Money · Not Financial Advice
      </div>
      <div>
        Data: <b>Alpaca Market Data API</b>
        &nbsp;·&nbsp; MA({MA_FAST}/{MA_SLOW}) + RSI({RSI_PERIOD})
        &nbsp;·&nbsp; {len(ALL_SYMBOLS)} symbols
      </div>
    </div>""", unsafe_allow_html=True)


render()