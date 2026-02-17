"""
SIGNAL_DASHBOARD.PY - Premium Trading Dashboard
================================================
Self-contained: fetches its own data via yfinance
No dependency on model.py or config.py
Works perfectly on Streamlit Cloud

Deploy: streamlit run signal_dashboard.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AlphaSignal — Raghu",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Load secrets ──────────────────────────────────────────────
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, default)

ALPACA_KEY    = get_secret("ALPACA_API_KEY")
ALPACA_SECRET = get_secret("ALPACA_SECRET_KEY")
ALPACA_URL    = get_secret("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ALPACA_OK     = bool(ALPACA_KEY and ALPACA_SECRET)

if ALPACA_OK:
    try:
        from alpaca_trade_api import REST
        _api = REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL)
    except:
        ALPACA_OK = False
        _api = None
else:
    _api = None

# ── Symbols ───────────────────────────────────────────────────
SYMBOLS = [
    "AAPL","MSFT","GOOGL","META","NVDA","TSLA",
    "AMD","INTC","UNH","JNJ","LLY","JPM",
    "BAC","GS","XOM","CVX"
]

# ── Strategy config ───────────────────────────────────────────
MA_FAST   = 5
MA_SLOW   = 15
RSI_PERIOD = 14
RSI_BUY   = 40
RSI_SELL  = 60

# ── Market clocks ─────────────────────────────────────────────
MARKETS = [
    {"name":"NEW YORK","flag":"🇺🇸","tz":"America/New_York",
     "open":(9,30),"close":(16,0),"short":"NYSE"},
    {"name":"MUMBAI",  "flag":"🇮🇳","tz":"Asia/Kolkata",
     "open":(9,15),"close":(15,30),"short":"NSE"},
    {"name":"LONDON",  "flag":"🇬🇧","tz":"Europe/London",
     "open":(8,0), "close":(16,30),"short":"LSE"},
    {"name":"TOKYO",   "flag":"🇯🇵","tz":"Asia/Tokyo",
     "open":(9,0), "close":(15,30),"short":"TSE"},
]

def market_status(m):
    tz  = pytz.timezone(m["tz"])
    now = datetime.now(tz)
    wd  = now.weekday() < 5
    oh, om = m["open"];  ch, cm = m["close"]
    ot = now.replace(hour=oh, minute=om, second=0, microsecond=0)
    ct = now.replace(hour=ch, minute=cm, second=0, microsecond=0)
    open_ = wd and ot <= now <= ct
    return now.strftime("%H:%M:%S"), now.strftime("%d %b"), open_

# ── Data & signals ────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def fetch_signals():
    results = []
    for sym in SYMBOLS:
        try:
            df = yf.download(sym, period="3mo", interval="1d",
                             progress=False, auto_adjust=True)
            if df is None or len(df) < MA_SLOW + 5:
                continue

            df = df.copy()
            close = df["Close"].squeeze()

            # Moving averages
            df["ma_fast"] = close.rolling(MA_FAST).mean()
            df["ma_slow"] = close.rolling(MA_SLOW).mean()

            # RSI
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
            loss  = (-delta.clip(upper=0)).rolling(RSI_PERIOD).mean()
            rs    = gain / loss.replace(0, np.nan)
            df["rsi"] = 100 - (100 / (1 + rs))

            cur  = df.iloc[-1]
            prev = df.iloc[-2]

            price    = float(cur["Close"])
            rsi_val  = float(cur["rsi"]) if not np.isnan(cur["rsi"]) else 50.0
            maf      = float(cur["ma_fast"]) if not np.isnan(cur["ma_fast"]) else price
            mas      = float(cur["ma_slow"]) if not np.isnan(cur["ma_slow"]) else price
            prev_p   = float(prev["Close"])
            chg_pct  = (price - prev_p) / prev_p * 100

            # MA crossover
            prev_maf = float(prev["ma_fast"]) if not np.isnan(prev["ma_fast"]) else maf
            prev_mas = float(prev["ma_slow"]) if not np.isnan(prev["ma_slow"]) else mas

            ma_sig = "HOLD"
            if prev_maf <= prev_mas and maf > mas:
                ma_sig = "BUY"
            elif prev_maf >= prev_mas and maf < mas:
                ma_sig = "SELL"
            elif maf > mas:
                ma_sig = "BUY"
            elif maf < mas:
                ma_sig = "SELL"

            # RSI signal
            rsi_sig = "HOLD"
            if rsi_val < RSI_BUY:
                rsi_sig = "BUY"
            elif rsi_val > RSI_SELL:
                rsi_sig = "SELL"

            # Final: any strategy
            final = "HOLD"
            if ma_sig == "BUY" or rsi_sig == "BUY":
                final = "BUY"
            if ma_sig == "SELL" or rsi_sig == "SELL":
                final = "SELL"
            if ma_sig == "BUY" and rsi_sig == "SELL":
                final = "HOLD"
            if ma_sig == "SELL" and rsi_sig == "BUY":
                final = "HOLD"

            results.append({
                "sym": sym, "price": price,
                "chg": chg_pct, "rsi": rsi_val,
                "maf": maf, "mas": mas,
                "ma_sig": ma_sig, "rsi_sig": rsi_sig,
                "signal": final,
            })
        except Exception:
            continue
    return results

@st.cache_data(ttl=30, show_spinner=False)
def fetch_portfolio():
    if not ALPACA_OK:
        return None
    try:
        acc  = _api.get_account()
        pos  = _api.list_positions()
        return {
            "value": float(acc.portfolio_value),
            "cash":  float(acc.cash),
            "bp":    float(acc.buying_power),
            "positions": [{
                "sym": p.symbol,
                "qty": float(p.qty),
                "entry": float(p.avg_entry_price),
                "val":   float(p.market_value),
                "pl":    float(p.unrealized_pl),
                "plpct": float(p.unrealized_plpc)*100,
            } for p in pos]
        }
    except:
        return None


# ═══════════════════════════════════════════════════════════════
# PREMIUM CSS — Bloomberg Terminal × Luxury Finance
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:       #060a10;
    --surface:  #0c1220;
    --border:   #162030;
    --border2:  #1e3048;
    --gold:     #c9a84c;
    --gold2:    #e8c97a;
    --green:    #0dff8c;
    --green2:   #00c853;
    --red:      #ff3d5a;
    --red2:     #ff6b81;
    --text:     #c8d8e8;
    --muted:    #4a6278;
    --white:    #eef4ff;
}

html, body, [class*="css"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Mono', monospace;
}
.main .block-container { padding: 1.5rem 2.5rem 3rem; max-width: 1600px; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }
[data-testid="stSidebar"] { display: none; }

/* ── HEADER ── */
.hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 1.5rem 0;
    border-bottom: 1px solid var(--border2);
    margin-bottom: 2rem;
}
.hdr-brand {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, var(--gold2) 0%, var(--gold) 60%, #a07830 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hdr-sub {
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}
.hdr-meta {
    text-align: right;
    font-size: 12px;
    color: var(--muted);
    line-height: 1.8;
}
.live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    background: var(--green);
    border-radius: 50%;
    margin-right: 5px;
    box-shadow: 0 0 8px var(--green);
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.85); }
}

/* ── SECTION LABEL ── */
.sec-label {
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--gold);
    border-left: 2px solid var(--gold);
    padding-left: 10px;
    margin: 2rem 0 1rem 0;
}

/* ── CLOCK CARDS ── */
.clocks-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 0.5rem;
}
.clock {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.clock::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--border2);
    transition: background 0.3s;
}
.clock.open { border-color: var(--border2); }
.clock.open::before { background: var(--green2); }
.clock-flag { font-size: 20px; margin-bottom: 6px; }
.clock-name {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.clock-time {
    font-size: 26px;
    font-weight: 500;
    color: var(--white);
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.clock-date { font-size: 11px; color: var(--muted); margin-bottom: 8px; }
.badge-open {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 10px; font-weight: 700; letter-spacing: 1px;
    color: var(--green); text-transform: uppercase;
}
.badge-open::before {
    content: ''; display: inline-block;
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
    animation: pulse 1.5s infinite;
}
.badge-closed {
    font-size: 10px; color: var(--muted);
    text-transform: uppercase; letter-spacing: 1px;
}

/* ── STAT CARDS ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}
.stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
}
.stat-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
}
.stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: var(--white);
}
.stat-val.pos { color: var(--green); }
.stat-val.neg { color: var(--red); }
.stat-val.gold { color: var(--gold2); }

/* ── SIGNAL SUMMARY ── */
.sig-summary {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin-bottom: 1.5rem;
}
.sig-count {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}
.sig-count-label { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
.sig-count-num { font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800; }
.sig-count-num.buy { color: var(--green); }
.sig-count-num.sell { color: var(--red); }
.sig-count-num.hold { color: var(--muted); }

/* ── SIGNAL CARDS ── */
.signals-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
.sig-col-head {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
}
.sig-col-head.buy { color: var(--green); }
.sig-col-head.sell { color: var(--red); }

.sig-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
}
.sig-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
}
.sig-card.buy { border-color: #0d2818; }
.sig-card.buy::before { background: var(--green); box-shadow: 0 0 10px var(--green); }
.sig-card.sell { border-color: #2d0a0a; }
.sig-card.sell::before { background: var(--red); box-shadow: 0 0 10px var(--red); }

.sig-row1 { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.sig-sym { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 800; color: var(--white); letter-spacing: 0.5px; }
.sig-action { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px; }
.sig-action.buy { color: var(--green); }
.sig-action.sell { color: var(--red); }
.sig-price { font-size: 22px; font-weight: 500; color: var(--white); text-align: right; }
.sig-chg { font-size: 11px; text-align: right; margin-top: 1px; }
.sig-chg.pos { color: var(--green); }
.sig-chg.neg { color: var(--red); }

.sig-indicators {
    display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px;
}
.ind-chip {
    font-size: 10px; letter-spacing: 0.5px;
    background: #0c1825;
    border: 1px solid var(--border2);
    border-radius: 4px;
    padding: 3px 8px;
    color: var(--muted);
}
.ind-chip.active-buy { border-color: var(--green2); color: var(--green); }
.ind-chip.active-sell { border-color: #c0392b; color: var(--red); }

/* ── EMPTY STATE ── */
.empty {
    background: var(--surface);
    border: 1px dashed var(--border2);
    border-radius: 8px;
    padding: 40px 20px;
    text-align: center;
    color: var(--muted);
}
.empty-icon { font-size: 28px; margin-bottom: 10px; }
.empty-text { font-size: 13px; line-height: 1.6; }

/* ── WATCHING ROW ── */
.watching-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.watch-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 11px;
    letter-spacing: 1px;
    color: var(--muted);
}

/* ── POSITIONS TABLE ── */
.pos-row {
    display: grid;
    grid-template-columns: 80px 60px 100px 110px 110px 90px;
    gap: 0;
    border-bottom: 1px solid var(--border);
    padding: 10px 0;
    align-items: center;
    font-size: 12px;
}
.pos-row.header {
    font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--muted); border-color: var(--border2);
}
.pos-sym { font-family: 'Syne', sans-serif; font-weight: 700; color: var(--white); }

/* ── FOOTER ── */
.footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
    color: var(--muted);
}
.footer-brand { font-family: 'Syne', sans-serif; font-weight: 700; color: var(--gold); }

/* ── SHARE BANNER ── */
.share-banner {
    background: linear-gradient(135deg, #0d1a2a 0%, #0c2040 100%);
    border: 1px solid var(--border2);
    border-radius: 8px;
    padding: 14px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}
.share-text { font-size: 12px; color: var(--text); }
.share-url {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: var(--gold2);
    letter-spacing: 0.3px;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# RENDER DASHBOARD
# ═══════════════════════════════════════════════════════════════

def render():
    now_utc = datetime.now(pytz.utc)

    # ── HEADER ────────────────────────────────────────────────
    col_hdr, col_btn = st.columns([6, 1])
    with col_hdr:
        st.markdown(f"""
        <div class='hdr'>
            <div>
                <div class='hdr-brand'>⚡ AlphaSignal</div>
                <div class='hdr-sub'>Paper Trading Monitor · by Raghu</div>
            </div>
            <div class='hdr-meta'>
                <span class='live-dot'></span>LIVE FEED<br>
                {now_utc.strftime('%d %b %Y  %H:%M:%S')} UTC<br>
                {len(SYMBOLS)} symbols · Alpaca Paper
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("⟳  Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── SHARE BANNER ──────────────────────────────────────────
    st.markdown("""
    <div class='share-banner'>
        <div>
            <div class='share-text'>📤 Share this dashboard with anyone:</div>
            <div class='share-url'>https://alpacaintegration.streamlit.app</div>
        </div>
        <div style='font-size:12px; color:#4a6278;'>
            ⚙️ Settings → Share → Make Public
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── MARKET CLOCKS ─────────────────────────────────────────
    st.markdown("<div class='sec-label'>Global Market Hours</div>", unsafe_allow_html=True)

    clk_cols = st.columns(4)
    for i, m in enumerate(MARKETS):
        t, d, is_open = market_status(m)
        with clk_cols[i]:
            badge = f"<span class='badge-open'>OPEN</span>" if is_open \
                    else "<span class='badge-closed'>○ CLOSED</span>"
            st.markdown(f"""
            <div class='clock {"open" if is_open else ""}'>
                <div class='clock-flag'>{m['flag']}</div>
                <div class='clock-name'>{m['name']} · {m['short']}</div>
                <div class='clock-time'>{t}</div>
                <div class='clock-date'>{d}</div>
                {badge}
            </div>""", unsafe_allow_html=True)

    # ── PORTFOLIO ─────────────────────────────────────────────
    st.markdown("<div class='sec-label'>Alpaca Portfolio</div>", unsafe_allow_html=True)

    pf = fetch_portfolio()
    if pf:
        start = 100_000.0
        total_pl = pf["value"] - start
        pl_cls = "pos" if total_pl >= 0 else "neg"
        pl_sign = "+" if total_pl >= 0 else ""
        pl_pct = (total_pl / start) * 100

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.markdown(f"""<div class='stat'>
                <div class='stat-label'>Portfolio Value</div>
                <div class='stat-val gold'>${pf['value']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with p2:
            st.markdown(f"""<div class='stat'>
                <div class='stat-label'>Cash Available</div>
                <div class='stat-val'>${pf['cash']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with p3:
            st.markdown(f"""<div class='stat'>
                <div class='stat-label'>Open Positions</div>
                <div class='stat-val'>{len(pf['positions'])}</div>
            </div>""", unsafe_allow_html=True)
        with p4:
            st.markdown(f"""<div class='stat'>
                <div class='stat-label'>Total Return</div>
                <div class='stat-val {pl_cls}'>{pl_sign}${total_pl:,.2f}<br>
                    <span style='font-size:14px;'>{pl_sign}{pl_pct:.2f}%</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='stat' style='text-align:center; color:#4a6278;'>
            ⚠️ Alpaca not connected — Add API keys in Streamlit Secrets
        </div>""", unsafe_allow_html=True)

    # ── SIGNALS ───────────────────────────────────────────────
    st.markdown("<div class='sec-label'>Live Signal Analysis</div>", unsafe_allow_html=True)

    with st.spinner("Fetching market data..."):
        data = fetch_signals()

    buys  = [r for r in data if r["signal"] == "BUY"]
    sells = [r for r in data if r["signal"] == "SELL"]
    holds = [r for r in data if r["signal"] == "HOLD"]

    # Signal count summary
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""<div class='sig-count'>
            <div class='sig-count-label'>Buy Signals</div>
            <div class='sig-count-num buy'>{len(buys)}</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class='sig-count'>
            <div class='sig-count-label'>Sell Signals</div>
            <div class='sig-count-num sell'>{len(sells)}</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""<div class='sig-count'>
            <div class='sig-count-label'>Monitoring</div>
            <div class='sig-count-num hold'>{len(holds)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Signal cards - 2 column layout
    left_col, right_col = st.columns(2)

    def render_card(r, side):
        chg_cls = "pos" if r["chg"] >= 0 else "neg"
        sign    = "+" if r["chg"] >= 0 else ""

        ma_cls  = f"active-{side}" if r["ma_sig"]  == side.upper() else ""
        rsi_cls = f"active-{side}" if r["rsi_sig"] == side.upper() else ""

        return f"""
        <div class='sig-card {side}'>
            <div class='sig-row1'>
                <div>
                    <div class='sig-sym'>{r["sym"]}</div>
                    <div class='sig-action {side}'>{"▲ LONG · BUY" if side=="buy" else "▼ SHORT · SELL"}</div>
                </div>
                <div>
                    <div class='sig-price'>${r["price"]:.2f}</div>
                    <div class='sig-chg {chg_cls}'>{sign}{r["chg"]:.2f}% today</div>
                </div>
            </div>
            <div class='sig-indicators'>
                <span class='ind-chip {ma_cls}'>MA {r["ma_sig"]}</span>
                <span class='ind-chip {rsi_cls}'>RSI {r["rsi"]:.0f} · {r["rsi_sig"]}</span>
                <span class='ind-chip'>Fast ${r["maf"]:.2f}</span>
                <span class='ind-chip'>Slow ${r["mas"]:.2f}</span>
            </div>
        </div>"""

    with left_col:
        st.markdown("<div class='sig-col-head buy'>▲ Buy Opportunities</div>", unsafe_allow_html=True)
        if buys:
            for r in buys:
                st.markdown(render_card(r, "buy"), unsafe_allow_html=True)
        else:
            st.markdown("""<div class='empty'>
                <div class='empty-icon'>◌</div>
                <div class='empty-text'>
                    No buy signals detected<br>
                    <span style='font-size:11px;opacity:0.6;'>
                    Market closed or no uptrend conditions met
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='sig-col-head sell'>▼ Sell Signals</div>", unsafe_allow_html=True)
        if sells:
            for r in sells:
                st.markdown(render_card(r, "sell"), unsafe_allow_html=True)
        else:
            st.markdown("""<div class='empty'>
                <div class='empty-icon'>◌</div>
                <div class='empty-text'>
                    No sell signals detected<br>
                    <span style='font-size:11px;opacity:0.6;'>
                    No overbought conditions found
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

    # ── MONITORING ────────────────────────────────────────────
    if holds:
        st.markdown("<div class='sec-label'>Monitoring — Awaiting Signals</div>", unsafe_allow_html=True)
        pills = "".join([f"<span class='watch-pill'>{r['sym']}</span>" for r in holds])
        st.markdown(f"<div class='watching-wrap'>{pills}</div>", unsafe_allow_html=True)

    # ── POSITIONS ─────────────────────────────────────────────
    if pf and pf["positions"]:
        st.markdown("<div class='sec-label'>Open Positions</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='pos-row header'>
            <span>SYMBOL</span><span>QTY</span><span>ENTRY</span>
            <span>MKT VALUE</span><span>P/L $</span><span>P/L %</span>
        </div>""", unsafe_allow_html=True)
        for p in pf["positions"]:
            cl = "pos" if p["pl"] >= 0 else "neg"
            sign = "+" if p["pl"] >= 0 else ""
            st.markdown(f"""
            <div class='pos-row'>
                <span class='pos-sym'>{p['sym']}</span>
                <span>{p['qty']:.0f}</span>
                <span>${p['entry']:.2f}</span>
                <span>${p['val']:,.2f}</span>
                <span style='color:{"var(--green)" if p["pl"]>=0 else "var(--red)"};'>
                    {sign}${p['pl']:.2f}</span>
                <span style='color:{"var(--green)" if p["pl"]>=0 else "var(--red)"};'>
                    {sign}{p['plpct']:.2f}%</span>
            </div>""", unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────
    st.markdown(f"""
    <div class='footer'>
        <div>
            <span class='footer-brand'>⚡ AlphaSignal</span>
            &nbsp;·&nbsp; Paper Trading Only · No Real Money
            &nbsp;·&nbsp; Not Financial Advice
        </div>
        <div>
            MA({MA_FAST}/{MA_SLOW}) + RSI({RSI_PERIOD})
            &nbsp;·&nbsp;
            Data: Yahoo Finance
            &nbsp;·&nbsp;
            Trades: Alpaca Paper
        </div>
    </div>
    """, unsafe_allow_html=True)


render()