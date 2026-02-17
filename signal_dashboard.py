"""
SIGNAL_DASHBOARD.PY — Auto-Refresh + Pair Trading
==================================================
New features:
  ✅ Auto-refresh (30s / 1min / 5min / manual)
  ✅ Pair trading signals (stock spreads)
  ✅ 100% Alpaca data
  ✅ All symbols from ALL_SYMBOLS list
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os
import time

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AlphaSignal — Raghu",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Secrets ───────────────────────────────────────────────────
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

# ── Symbols — keep in sync with your symbols.txt ─────────────
ALL_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA",
    "AMD",  "INTC", "AMZN",  "NFLX", "CRM",  "ORCL",
    "UNH",  "JNJ",  "LLY",   "PFE",
    "JPM",  "BAC",  "GS",    "MS",
    "XOM",  "CVX",
    "SPY",  "QQQ",  "IWM",   "VXX",
]

# Pair trading groups (stock spreads)
PAIRS = [
    ("AAPL", "MSFT",  "Tech Giants"),
    ("NVDA", "AMD",   "Chip Makers"),
    ("JPM",  "BAC",   "Big Banks"),
    ("XOM",  "CVX",   "Oil Majors"),
    ("GOOGL","META",  "Ad Tech"),
]

# ── Strategy settings ─────────────────────────────────────────
MA_FAST    = 5
MA_SLOW    = 15
RSI_PERIOD = 14
RSI_BUY    = 40
RSI_SELL   = 60

# ── Market clocks ─────────────────────────────────────────────
MARKETS = [
    {"name":"NEW YORK","short":"NYSE","flag":"🇺🇸",
     "tz":"America/New_York","open":(9,30),"close":(16,0)},
    {"name":"MUMBAI",  "short":"NSE", "flag":"🇮🇳",
     "tz":"Asia/Kolkata",    "open":(9,15),"close":(15,30)},
    {"name":"LONDON",  "short":"LSE", "flag":"🇬🇧",
     "tz":"Europe/London",   "open":(8,0), "close":(16,30)},
    {"name":"TOKYO",   "short":"TSE", "flag":"🇯🇵",
     "tz":"Asia/Tokyo",      "open":(9,0), "close":(15,30)},
]


# ── Alpaca client ─────────────────────────────────────────────
@st.cache_resource
def get_alpaca():
    if not (ALPACA_KEY and ALPACA_SECRET):
        return None
    try:
        from alpaca_trade_api import REST
        return REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL)
    except:
        return None


# ── Data functions ────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def get_bars(symbol, limit=60):
    api = get_alpaca()
    if api is None:
        return None
    try:
        bars = api.get_bars(symbol, "1Day", limit=limit).df
        if bars.empty:
            return None
        bars = bars.rename(columns={
            "open":"Open","high":"High",
            "low":"Low","close":"Close","volume":"Volume"
        })
        return bars
    except:
        return None


@st.cache_data(ttl=20, show_spinner=False)
def get_portfolio():
    api = get_alpaca()
    if api is None:
        return None
    try:
        acc = api.get_account()
        pos = api.list_positions()
        return {
            "value": float(acc.portfolio_value),
            "cash":  float(acc.cash),
            "bp":    float(acc.buying_power),
            "positions": [{
                "sym":   p.symbol,
                "qty":   float(p.qty),
                "entry": float(p.avg_entry_price),
                "val":   float(p.market_value),
                "pl":    float(p.unrealized_pl),
                "plpct": float(p.unrealized_plpc)*100,
            } for p in pos]
        }
    except:
        return None


@st.cache_data(ttl=120, show_spinner=False)
def analyze_symbol(symbol):
    df = get_bars(symbol, 60)
    if df is None or len(df) < MA_SLOW + 5:
        return None
    close = df["Close"].squeeze().astype(float)
    df["maf"] = close.rolling(MA_FAST).mean()
    df["mas"] = close.rolling(MA_SLOW).mean()
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
    loss  = (-delta.clip(upper=0)).rolling(RSI_PERIOD).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - (100/(1+rs))

    cur  = df.iloc[-1]
    prev = df.iloc[-2]
    price   = float(cur["Close"])
    rsi_val = float(cur["rsi"]) if not np.isnan(cur["rsi"]) else 50.0
    maf_v   = float(cur["maf"]) if not np.isnan(cur["maf"]) else price
    mas_v   = float(cur["mas"]) if not np.isnan(cur["mas"]) else price
    prev_p  = float(prev["Close"])
    chg_pct = (price - prev_p) / prev_p * 100

    ma_sig  = "BUY" if maf_v > mas_v else "SELL" if maf_v < mas_v else "HOLD"
    rsi_sig = "BUY" if rsi_val < RSI_BUY else "SELL" if rsi_val > RSI_SELL else "HOLD"

    if ma_sig == "BUY"  and rsi_sig == "BUY":  final = "BUY"
    elif ma_sig == "SELL" and rsi_sig == "SELL": final = "SELL"
    else:                                         final = "HOLD"

    return {
        "sym":sym, "price":price, "chg":chg_pct,
        "rsi":rsi_val, "maf":maf_v, "mas":mas_v,
        "ma_sig":ma_sig, "rsi_sig":rsi_sig, "signal":final,
    }


@st.cache_data(ttl=120, show_spinner=False)
def analyze_all():
    return [r for r in (analyze_symbol(s) for s in ALL_SYMBOLS) if r]


@st.cache_data(ttl=120, show_spinner=False)
def analyze_pairs():
    """
    Pair trading (Stock Spread):
    Compare performance of two related stocks.
    When Stock A outperforms Stock B → Long A, Short B
    """
    results = []
    for sym_a, sym_b, label in PAIRS:
        ra = analyze_symbol(sym_a)
        rb = analyze_symbol(sym_b)
        if not ra or not rb:
            continue

        # Spread signal: compare momentum
        spread = ra["chg"] - rb["chg"]
        ma_spread = ra["maf"]/ra["mas"] - rb["maf"]/rb["mas"]

        if spread > 0.5 and ma_spread > 0:
            signal = "LONG A / SHORT B"
            detail = f"Long {sym_a}, Short {sym_b}"
            color  = "buy"
        elif spread < -0.5 and ma_spread < 0:
            signal = "SHORT A / LONG B"
            detail = f"Short {sym_a}, Long {sym_b}"
            color  = "sell"
        else:
            signal = "NEUTRAL"
            detail = "No clear spread divergence"
            color  = "hold"

        results.append({
            "label": label,
            "sym_a": sym_a, "sym_b": sym_b,
            "price_a": ra["price"], "price_b": rb["price"],
            "chg_a": ra["chg"],   "chg_b": rb["chg"],
            "spread": spread,
            "signal": signal, "detail": detail, "color": color,
        })
    return results


def market_status(m):
    tz  = pytz.timezone(m["tz"])
    now = datetime.now(tz)
    wd  = now.weekday() < 5
    oh,om = m["open"]; ch,cm = m["close"]
    ot = now.replace(hour=oh,minute=om,second=0,microsecond=0)
    ct = now.replace(hour=ch,minute=cm,second=0,microsecond=0)
    return now.strftime("%H:%M:%S"), now.strftime("%d %b"), (wd and ot <= now <= ct)


# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
:root {
    --bg:#060a10; --surf:#0c1220; --bdr:#162030; --bdr2:#1e3048;
    --gold:#c9a84c; --gold2:#e8c97a;
    --green:#0dff8c; --green2:#00c853;
    --red:#ff3d5a; --text:#c8d8e8; --muted:#4a6278; --white:#eef4ff;
}
html,body,[class*="css"]{background:var(--bg)!important;color:var(--text);font-family:'DM Mono',monospace;}
.main .block-container{padding:1.5rem 2.5rem 3rem;max-width:1700px;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}

.hdr{padding-bottom:1.5rem;border-bottom:1px solid var(--bdr2);margin-bottom:1.8rem;}
.hdr-brand{font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
    background:linear-gradient(135deg,var(--gold2),var(--gold),#a07830);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hdr-sub{font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-top:3px;}

.live-dot{display:inline-block;width:7px;height:7px;background:var(--green);border-radius:50%;
    box-shadow:0 0 8px var(--green);animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.85)}}

.sec{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:3px;
    text-transform:uppercase;color:var(--gold);border-left:2px solid var(--gold);
    padding-left:10px;margin:2rem 0 1rem;}

/* AUTO-REFRESH BAR */
.refresh-bar{
    background:var(--surf);border:1px solid var(--bdr2);border-radius:8px;
    padding:12px 20px;margin-bottom:1.5rem;
    display:flex;justify-content:space-between;align-items:center;
}
.refresh-label{font-size:11px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;}
.refresh-count{font-family:'Syne',sans-serif;font-size:22px;font-weight:700;color:var(--gold2);}
.progress-wrap{width:200px;height:4px;background:var(--bdr);border-radius:2px;overflow:hidden;}
.progress-fill{height:100%;background:var(--gold);border-radius:2px;transition:width 1s linear;}

/* SHARE */
.share{background:linear-gradient(135deg,#0d1a2a,#0c2040);border:1px solid var(--bdr2);
    border-radius:8px;padding:14px 20px;margin-bottom:1.5rem;
    display:flex;justify-content:space-between;align-items:center;}
.share-url{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:var(--gold2);}

/* CLOCKS */
.clk{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:18px 16px;position:relative;}
.clk::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--bdr2);}
.clk.open::before{background:var(--green2);}
.clk-name{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:1.5px;color:var(--muted);text-transform:uppercase;margin-bottom:8px;}
.clk-time{font-size:26px;font-weight:500;color:var(--white);letter-spacing:1px;margin-bottom:3px;}
.clk-date{font-size:11px;color:var(--muted);margin-bottom:8px;}
.badge-open{font-size:10px;font-weight:700;color:var(--green);letter-spacing:1px;text-transform:uppercase;}
.badge-open::before{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;
    background:var(--green);box-shadow:0 0 6px var(--green);margin-right:5px;animation:pulse 1.5s infinite;}
.badge-closed{font-size:10px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;}

/* STATS */
.stat{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:20px;}
.stat-lbl{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:10px;}
.stat-val{font-family:'Syne',sans-serif;font-size:26px;font-weight:700;color:var(--white);}
.stat-val.gold{color:var(--gold2);}
.stat-val.pos{color:var(--green);}
.stat-val.neg{color:var(--red);}

/* SIGNAL COUNT */
.sc{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:20px;text-align:center;}
.sc-lbl{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}
.sc-n{font-family:'Syne',sans-serif;font-size:38px;font-weight:800;}
.sc-n.buy{color:var(--green);}
.sc-n.sell{color:var(--red);}
.sc-n.hold{color:var(--muted);}

/* SIGNAL CARDS */
.sig{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:16px 20px;margin-bottom:10px;position:relative;overflow:hidden;}
.sig::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;}
.sig.buy{border-color:#0d2818;}
.sig.buy::before{background:var(--green);box-shadow:0 0 10px var(--green);}
.sig.sell{border-color:#2d0a0a;}
.sig.sell::before{background:var(--red);box-shadow:0 0 10px var(--red);}
.sig-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;}
.sig-sym{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:var(--white);}
.sig-act{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;}
.sig-act.buy{color:var(--green);}
.sig-act.sell{color:var(--red);}
.sig-px{font-size:22px;font-weight:500;color:var(--white);text-align:right;}
.sig-chg{font-size:11px;text-align:right;}
.sig-chg.pos{color:var(--green);}
.sig-chg.neg{color:var(--red);}
.chips{display:flex;gap:7px;flex-wrap:wrap;margin-top:6px;}
.chip{font-size:10px;background:#0c1825;border:1px solid var(--bdr2);border-radius:4px;padding:3px 8px;color:var(--muted);}
.chip.abuy{border-color:var(--green2);color:var(--green);}
.chip.asell{border-color:#c0392b;color:var(--red);}

/* PAIR TRADING CARDS */
.pair-card{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:16px 20px;margin-bottom:10px;}
.pair-card.buy{border-left:3px solid var(--green);}
.pair-card.sell{border-left:3px solid var(--red);}
.pair-card.hold{border-left:3px solid var(--muted);opacity:0.7;}
.pair-label{font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:var(--white);margin-bottom:8px;}
.pair-signal{font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.pair-signal.buy{color:var(--green);}
.pair-signal.sell{color:var(--red);}
.pair-signal.hold{color:var(--muted);}
.pair-stocks{display:flex;gap:16px;margin-top:8px;}
.pair-stock{background:#0c1825;border:1px solid var(--bdr2);border-radius:6px;padding:8px 12px;flex:1;}
.pair-sym{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:var(--white);}
.pair-px{font-size:12px;color:var(--muted);margin-top:2px;}

/* WATCHING */
.ww{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px;}
.wp{background:var(--surf);border:1px solid var(--bdr);border-radius:4px;padding:5px 12px;font-size:11px;letter-spacing:1px;color:var(--muted);}

/* POSITIONS */
.ph{display:grid;grid-template-columns:80px 60px 100px 110px 110px 90px;border-bottom:1px solid var(--bdr2);padding:8px 0;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);}
.pr{display:grid;grid-template-columns:80px 60px 100px 110px 110px 90px;border-bottom:1px solid var(--bdr);padding:10px 0;font-size:12px;align-items:center;}
.pr-sym{font-family:'Syne',sans-serif;font-weight:700;color:var(--white);}

/* EMPTY */
.empty{background:var(--surf);border:1px dashed var(--bdr2);border-radius:8px;padding:40px;text-align:center;color:var(--muted);}

/* STRATEGY INFO BOX */
.strat-box{background:var(--surf);border:1px solid var(--bdr2);border-left:3px solid var(--gold);border-radius:8px;padding:16px 20px;margin-bottom:12px;}
.strat-title{font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:var(--gold2);margin-bottom:6px;letter-spacing:1px;}
.strat-desc{font-size:11px;color:var(--muted);line-height:1.7;}

.ftr{margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--bdr);display:flex;justify-content:space-between;font-size:11px;color:var(--muted);}
.ftr-brand{font-family:'Syne',sans-serif;font-weight:700;color:var(--gold);}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# AUTO-REFRESH STATE
# ═══════════════════════════════════════════════════════════════
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0


def render():
    now_utc = datetime.now(pytz.utc)
    pf      = get_portfolio()

    # ── HEADER ───────────────────────────────────────────────
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f"""
        <div class='hdr'>
          <div class='hdr-brand'>⚡ AlphaSignal</div>
          <div class='hdr-sub'>Paper Trading Monitor · by Raghu · Alpaca API</div>
          <div style='display:flex;align-items:center;gap:14px;margin-top:8px;font-size:11px;color:var(--muted);'>
            <span><span class='live-dot'></span> {now_utc.strftime("%d %b %Y  %H:%M:%S")} UTC</span>
            <span>· {len(ALL_SYMBOLS)} Symbols</span>
            <span>· Refresh #{st.session_state.refresh_count}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("⟳ Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.session_state.last_refresh = time.time()
            st.session_state.refresh_count += 1
            st.rerun()

    # ── AUTO-REFRESH CONTROL ─────────────────────────────────
    st.markdown("<div class='sec'>⏱ Auto-Refresh</div>", unsafe_allow_html=True)

    r1, r2, r3 = st.columns([2, 2, 3])

    with r1:
        auto_on = st.toggle("Enable Auto-Refresh", value=False)

    with r2:
        interval_choice = st.selectbox(
            "Refresh Every",
            options=[30, 60, 120, 300, 600],
            format_func=lambda x: f"{x}s — {x//60}min {x%60}s" if x >= 60 else f"{x} seconds",
            index=1,
            disabled=not auto_on
        )

    with r3:
        if auto_on:
            elapsed  = time.time() - st.session_state.last_refresh
            remaining = max(0, interval_choice - elapsed)
            pct       = min(100, (elapsed / interval_choice) * 100)
            st.markdown(f"""
            <div class='refresh-bar'>
              <div>
                <div class='refresh-label'>Next refresh in</div>
                <div class='refresh-count'>{int(remaining)}s</div>
              </div>
              <div>
                <div class='refresh-label' style='margin-bottom:6px;'>Progress</div>
                <div class='progress-wrap'>
                  <div class='progress-fill' style='width:{pct:.0f}%;'></div>
                </div>
              </div>
              <div style='font-size:11px;color:var(--muted);'>
                Scans: {st.session_state.refresh_count}<br>
                Interval: {interval_choice}s
              </div>
            </div>""", unsafe_allow_html=True)

            # Trigger rerun when interval reached
            if elapsed >= interval_choice:
                st.cache_data.clear()
                st.session_state.last_refresh = time.time()
                st.session_state.refresh_count += 1
                time.sleep(0.1)
                st.rerun()
            else:
                # Keep re-checking every second to update countdown
                time.sleep(1)
                st.rerun()
        else:
            st.markdown("""
            <div class='refresh-bar'>
              <div>
                <div class='refresh-label'>Auto-Refresh</div>
                <div style='font-size:14px;color:var(--muted);margin-top:4px;'>Off — Manual only</div>
              </div>
              <div style='font-size:11px;color:var(--muted);'>
                Toggle ON to enable<br>
                automatic data refresh
              </div>
            </div>""", unsafe_allow_html=True)

    # ── SHARE BANNER ─────────────────────────────────────────
    st.markdown("""
    <div class='share'>
      <div>
        <div style='font-size:11px;color:var(--muted);margin-bottom:4px;'>📤 SHARE THIS DASHBOARD</div>
        <div class='share-url'>https://alpacaintegration.streamlit.app</div>
      </div>
      <div style='font-size:11px;color:var(--muted);text-align:right;line-height:1.8;'>
        Make public: Streamlit → Settings → Sharing → Public
      </div>
    </div>""", unsafe_allow_html=True)

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

    # ── PORTFOLIO ─────────────────────────────────────────────
    st.markdown("<div class='sec'>💼 Alpaca Portfolio</div>", unsafe_allow_html=True)
    if pf:
        start = 100_000.0
        pl    = pf["value"] - start
        pl_pct = (pl/start)*100
        pl_cls = "pos" if pl >= 0 else "neg"
        sign   = "+" if pl >= 0 else ""
        p1,p2,p3,p4 = st.columns(4)
        with p1:
            st.markdown(f"""<div class='stat'><div class='stat-lbl'>Portfolio Value</div>
              <div class='stat-val gold'>${pf['value']:,.2f}</div></div>""", unsafe_allow_html=True)
        with p2:
            st.markdown(f"""<div class='stat'><div class='stat-lbl'>Cash Available</div>
              <div class='stat-val'>${pf['cash']:,.2f}</div></div>""", unsafe_allow_html=True)
        with p3:
            st.markdown(f"""<div class='stat'><div class='stat-lbl'>Open Positions</div>
              <div class='stat-val'>{len(pf['positions'])}</div></div>""", unsafe_allow_html=True)
        with p4:
            st.markdown(f"""<div class='stat'><div class='stat-lbl'>Total Return</div>
              <div class='stat-val {pl_cls}'>{sign}${pl:,.2f}
                <span style='font-size:14px;'>&nbsp;{sign}{pl_pct:.2f}%</span>
              </div></div>""", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Alpaca not connected. Add API keys in Streamlit → Settings → Secrets")

    # ── STRATEGY GUIDE ────────────────────────────────────────
    with st.expander("📚 Strategy Guide — What These Signals Mean"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""<div class='strat-box'>
              <div class='strat-title'>📈 MA CROSSOVER (Trend)</div>
              <div class='strat-desc'>
                Fast MA(5) crosses above Slow MA(15) → <b style='color:#0dff8c;'>BUY</b><br>
                Fast MA(5) crosses below Slow MA(15) → <b style='color:#ff3d5a;'>SELL</b><br><br>
                Tells you: Direction of trend
              </div>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown("""<div class='strat-box'>
              <div class='strat-title'>📊 RSI (Timing)</div>
              <div class='strat-desc'>
                RSI below 40 → Stock oversold → <b style='color:#0dff8c;'>BUY</b><br>
                RSI above 60 → Stock overbought → <b style='color:#ff3d5a;'>SELL</b><br><br>
                Tells you: When to enter/exit
              </div>
            </div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown("""<div class='strat-box'>
              <div class='strat-title'>🔄 PAIR TRADING (Spread)</div>
              <div class='strat-desc'>
                Stock version of "spread" strategy.<br>
                Long outperformer + Short underperformer.<br><br>
                Tells you: Relative strength between 2 stocks
              </div>
            </div>""", unsafe_allow_html=True)

    # ── SIGNALS ───────────────────────────────────────────────
    st.markdown(f"<div class='sec'>🎯 Live Signals · {len(ALL_SYMBOLS)} Symbols · Alpaca Data</div>",
                unsafe_allow_html=True)

    with st.spinner(f"Loading {len(ALL_SYMBOLS)} symbols from Alpaca..."):
        data = analyze_all()

    if not data:
        st.warning("No data from Alpaca. Market may be closed or check API keys.")
        return

    buys  = [r for r in data if r["signal"] == "BUY"]
    sells = [r for r in data if r["signal"] == "SELL"]
    holds = [r for r in data if r["signal"] == "HOLD"]

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""<div class='sc'><div class='sc-lbl'>Buy Signals</div>
          <div class='sc-n buy'>{len(buys)}</div></div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class='sc'><div class='sc-lbl'>Sell Signals</div>
          <div class='sc-n sell'>{len(sells)}</div></div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""<div class='sc'><div class='sc-lbl'>Monitoring</div>
          <div class='sc-n hold'>{len(holds)}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def sig_card(r, side):
        cc  = "pos" if r["chg"] >= 0 else "neg"
        sgn = "+" if r["chg"] >= 0 else ""
        mac  = f"a{side}" if r["ma_sig"]  == side.upper() else ""
        rsic = f"a{side}" if r["rsi_sig"] == side.upper() else ""
        lbl  = "▲ LONG · BUY" if side == "buy" else "▼ SHORT · SELL"
        return f"""
        <div class='sig {side}'>
          <div class='sig-top'>
            <div><div class='sig-sym'>{r['sym']}</div><div class='sig-act {side}'>{lbl}</div></div>
            <div><div class='sig-px'>${r['price']:.2f}</div>
                 <div class='sig-chg {cc}'>{sgn}{r['chg']:.2f}%</div></div>
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

    # ── PAIR TRADING ─────────────────────────────────────────
    st.markdown("<div class='sec'>🔄 Pair Trading — Stock Spreads (Stock Version of Spreads)</div>",
                unsafe_allow_html=True)

    pairs_data = analyze_pairs()
    if pairs_data:
        active_pairs = [p for p in pairs_data if p["color"] != "hold"]
        neutral_pairs = [p for p in pairs_data if p["color"] == "hold"]

        if active_pairs:
            pc1, pc2 = st.columns(2)
            for i, p in enumerate(active_pairs):
                col = pc1 if i % 2 == 0 else pc2
                sgn_a = "+" if p["chg_a"] >= 0 else ""
                sgn_b = "+" if p["chg_b"] >= 0 else ""
                clr_a = "var(--green)" if p["chg_a"] >= 0 else "var(--red)"
                clr_b = "var(--green)" if p["chg_b"] >= 0 else "var(--red)"
                spread_clr = "var(--green)" if p["spread"] > 0 else "var(--red)"

                with col:
                    st.markdown(f"""
                    <div class='pair-card {p["color"]}'>
                      <div style='display:flex;justify-content:space-between;align-items:start;'>
                        <div>
                          <div class='pair-label'>{p['label']}</div>
                          <div class='pair-signal {p["color"]}'>{p['signal']}</div>
                          <div style='font-size:11px;color:var(--muted);margin-top:4px;'>{p['detail']}</div>
                        </div>
                        <div style='text-align:right;font-size:11px;color:var(--muted);'>
                          Spread<br>
                          <span style='font-size:16px;font-weight:700;color:{spread_clr};'>
                            {p['spread']:+.2f}%
                          </span>
                        </div>
                      </div>
                      <div class='pair-stocks'>
                        <div class='pair-stock'>
                          <div class='pair-sym'>{p['sym_a']}</div>
                          <div class='pair-px'>${p['price_a']:.2f}
                            <span style='color:{clr_a};margin-left:6px;'>{sgn_a}{p['chg_a']:.2f}%</span>
                          </div>
                        </div>
                        <div class='pair-stock'>
                          <div class='pair-sym'>{p['sym_b']}</div>
                          <div class='pair-px'>${p['price_b']:.2f}
                            <span style='color:{clr_b};margin-left:6px;'>{sgn_b}{p['chg_b']:.2f}%</span>
                          </div>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)

        if neutral_pairs:
            neutral_html = "".join([f"<span class='wp'>{p['sym_a']}/{p['sym_b']}</span>" for p in neutral_pairs])
            st.markdown(f"<div style='font-size:11px;color:var(--muted);margin-top:8px;'>Neutral pairs: <div class='ww' style='display:inline-flex;margin-left:8px;'>{neutral_html}</div></div>",
                        unsafe_allow_html=True)

    # ── POSITIONS ─────────────────────────────────────────────
    if pf and pf["positions"]:
        st.markdown("<div class='sec'>📂 Open Positions</div>", unsafe_allow_html=True)
        st.markdown("""<div class='ph'>
          <span>SYMBOL</span><span>QTY</span><span>ENTRY</span>
          <span>VALUE</span><span>P/L $</span><span>P/L %</span>
        </div>""", unsafe_allow_html=True)
        for p in pf["positions"]:
            cl   = "var(--green)" if p["pl"] >= 0 else "var(--red)"
            sign = "+" if p["pl"] >= 0 else ""
            st.markdown(f"""<div class='pr'>
              <span class='pr-sym'>{p['sym']}</span>
              <span>{p['qty']:.0f}</span>
              <span>${p['entry']:.2f}</span>
              <span>${p['val']:,.2f}</span>
              <span style='color:{cl};'>{sign}${p['pl']:.2f}</span>
              <span style='color:{cl};'>{sign}{p['plpct']:.2f}%</span>
            </div>""", unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────
    st.markdown(f"""
    <div class='ftr'>
      <div><span class='ftr-brand'>⚡ AlphaSignal</span>
        &nbsp;·&nbsp; Paper Only · Not Financial Advice
      </div>
      <div>Data: Alpaca API · MA({MA_FAST}/{MA_SLOW}) + RSI({RSI_PERIOD}) + Pairs · {len(ALL_SYMBOLS)} symbols</div>
    </div>""", unsafe_allow_html=True)


render()