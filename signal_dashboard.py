"""
SIGNAL_DASHBOARD.PY — Enhanced with Confidence + News
======================================================
Shows:
  ✅ Confidence score (0-10) per signal
  ✅ WEAK / MEDIUM / STRONG badge
  ✅ All 5 indicator votes visible
  ✅ News sentiment per symbol
  ✅ Earnings warnings
  ✅ Auto-refresh (no dimming)
  ✅ 100% Alpaca data
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os

st.set_page_config(
    page_title="AlphaSignal — Raghu",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Secrets ───────────────────────────────────────────────────
def get_secret(key, default=""):
    try:    return st.secrets.get(key, default)
    except:
        try:
            from dotenv import load_dotenv; load_dotenv()
        except: pass
        return os.getenv(key, default)

ALPACA_KEY    = get_secret("ALPACA_API_KEY")
ALPACA_SECRET = get_secret("ALPACA_SECRET_KEY")
ALPACA_URL    = get_secret("ALPACA_BASE_URL","https://paper-api.alpaca.markets")

ALL_SYMBOLS = [
    "AAPL","MSFT","GOOGL","META","NVDA","TSLA",
    "AMD","INTC","AMZN","NFLX","CRM","ORCL",
    "UNH","JNJ","LLY","PFE",
    "JPM","BAC","GS","MS",
    "XOM","CVX","SPY","QQQ","IWM","VXX",
]

MARKETS = [
    {"name":"NEW YORK","short":"NYSE","flag":"🇺🇸","tz":"America/New_York","open":(9,30),"close":(16,0)},
    {"name":"MUMBAI",  "short":"NSE", "flag":"🇮🇳","tz":"Asia/Kolkata",    "open":(9,15),"close":(15,30)},
    {"name":"LONDON",  "short":"LSE", "flag":"🇬🇧","tz":"Europe/London",   "open":(8,0), "close":(16,30)},
    {"name":"TOKYO",   "short":"TSE", "flag":"🇯🇵","tz":"Asia/Tokyo",      "open":(9,0), "close":(15,30)},
]

REFRESH_OPTIONS = {"Off":0,"30 sec":30_000,"1 min":60_000,"5 min":300_000,"10 min":600_000}

# Indicator settings
MA_FAST=5; MA_SLOW=15; RSI_PERIOD=14; RSI_BUY=40; RSI_SELL=60
MACD_FAST=12; MACD_SLOW=26; MACD_SIG=9; BB_PERIOD=20; BB_STD=2.0

@st.cache_resource
def get_alpaca():
    if not (ALPACA_KEY and ALPACA_SECRET): return None
    try:
        from alpaca_trade_api import REST
        return REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_URL)
    except: return None

@st.cache_data(ttl=20, show_spinner=False)
def get_portfolio():
    api = get_alpaca()
    if not api: return None
    try:
        acc = api.get_account()
        pos = api.list_positions()
        return {
            "value": float(acc.portfolio_value), "cash": float(acc.cash),
            "positions": [{"sym":p.symbol,"qty":float(p.qty),
                "entry":float(p.avg_entry_price),"val":float(p.market_value),
                "pl":float(p.unrealized_pl),"plpct":float(p.unrealized_plpc)*100}
                for p in pos]
        }
    except: return None

@st.cache_data(ttl=90, show_spinner=False)
def get_bars(symbol):
    api = get_alpaca()
    if not api: return None
    try:
        b = api.get_bars(symbol,"1Day",limit=80).df
        return None if b.empty else b.rename(columns={"open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"})
    except: return None

@st.cache_data(ttl=90, show_spinner=False)
def full_analyze(symbol):
    df = get_bars(symbol)
    if df is None or len(df) < MACD_SLOW+5: return None

    close = df["Close"].squeeze().astype(float)
    vol   = df["Volume"].squeeze().astype(float) if "Volume" in df.columns else None

    # All indicators
    df["maf"] = close.rolling(MA_FAST).mean()
    df["mas"] = close.rolling(MA_SLOW).mean()

    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
    loss  = (-delta.clip(upper=0)).rolling(RSI_PERIOD).mean()
    df["rsi"] = 100 - (100/(1+gain/loss.replace(0,np.nan)))

    ema_f = close.ewm(span=MACD_FAST,adjust=False).mean()
    ema_s = close.ewm(span=MACD_SLOW,adjust=False).mean()
    macd  = ema_f - ema_s
    msig  = macd.ewm(span=MACD_SIG,adjust=False).mean()
    df["macd_hist"] = macd - msig

    bb_m  = close.rolling(BB_PERIOD).mean()
    bb_s  = close.rolling(BB_PERIOD).std()
    df["bb_up"]  = bb_m + BB_STD*bb_s
    df["bb_lo"]  = bb_m - BB_STD*bb_s
    df["bb_pct"] = (close - df["bb_lo"]) / (df["bb_up"] - df["bb_lo"])

    if vol is not None:
        df["vol_ratio"] = vol / vol.rolling(20).mean()
    else:
        df["vol_ratio"] = 1.0

    c = df.iloc[-1]; p = df.iloc[-2]
    price   = float(c["Close"])
    prev_p  = float(p["Close"])
    chg_pct = (price-prev_p)/prev_p*100

    def safe(col): return float(c[col]) if not np.isnan(c[col]) else 0.0

    maf=safe("maf"); mas=safe("mas"); rsi=safe("rsi") or 50.0
    bb_pct=safe("bb_pct"); vol_ratio=safe("vol_ratio") or 1.0

    # Individual signals
    ind = {}
    ind["MA"]   = "BUY" if maf>mas else "SELL" if maf<mas else "HOLD"
    ind["RSI"]  = "BUY" if rsi<RSI_BUY else "SELL" if rsi>RSI_SELL else "HOLD"
    mhist=safe("macd_hist"); pmhist=float(p["macd_hist"]) if not np.isnan(p["macd_hist"]) else 0
    ind["MACD"] = "BUY" if mhist>0 else "SELL" if mhist<0 else "HOLD"
    ind["BB"]   = "BUY" if bb_pct<0.1 else "SELL" if bb_pct>0.9 else "HOLD"
    # Volume is a filter, not a directional signal — included in score
    
    # Confidence calculation
    buys  = sum(1 for v in ind.values() if v=="BUY")
    sells = sum(1 for v in ind.values() if v=="SELL")
    total = len(ind)

    if buys > sells:
        direction = "BUY"; agree = buys
    elif sells > buys:
        direction = "SELL"; agree = sells
    else:
        return {"sym":symbol,"price":price,"chg":chg_pct,"signal":"HOLD",
                "confidence":"HOLD","score":0,"ind":ind,
                "rsi":rsi,"maf":maf,"mas":mas,"vol_ratio":vol_ratio,"bb_pct":bb_pct}

    base_score = (agree/total)*8
    vol_boost  = 2.0 if vol_ratio>=1.5 else 1.0 if vol_ratio>=1.0 else -1.0 if vol_ratio<0.5 else 0.0
    score      = min(10, max(0, base_score+vol_boost))

    if score>=7 and vol_ratio>=1.0: conf="STRONG"
    elif score>=4.5:                conf="MEDIUM"
    elif score>=2:                  conf="WEAK"
    else: direction="HOLD"; conf="HOLD"

    return {"sym":symbol,"price":price,"chg":chg_pct,"signal":direction,
            "confidence":conf,"score":score,"ind":ind,
            "rsi":rsi,"maf":maf,"mas":mas,"vol_ratio":vol_ratio,"bb_pct":bb_pct}

@st.cache_data(ttl=90, show_spinner=False)
def analyze_all():
    return [r for r in (full_analyze(s) for s in ALL_SYMBOLS) if r]

@st.cache_data(ttl=180, show_spinner=False)
def get_news_for(symbol):
    api = get_alpaca()
    if not api: return None
    try:
        from datetime import timedelta
        end   = datetime.now(pytz.utc)
        start = end - timedelta(days=2)
        items = api.get_news(symbol,start=start.isoformat(),end=end.isoformat(),limit=5)
        if not items: return None
        POS={"surge","soar","beat","record","strong","growth","profit","gain","rise","bullish","upgrade","deal"}
        NEG={"fall","drop","miss","weak","loss","decline","down","bearish","downgrade","lawsuit","probe","layoff","fine","recall"}
        pos=neg=0
        headlines=[]
        for it in items:
            h = it.headline if hasattr(it,'headline') else str(it)
            hl = h.lower()
            p=sum(1 for w in POS if w in hl); n=sum(1 for w in NEG if w in hl)
            if p>n: pos+=1; sent="🟢"
            elif n>p: neg+=1; sent="🔴"
            else: sent="⚪"
            headlines.append(f"{sent} {h[:80]}")
        score=(pos-neg)/len(items)*10 if items else 0
        overall="POSITIVE" if score>2 else "NEGATIVE" if score<-2 else "NEUTRAL"
        return {"overall":overall,"score":round(score,1),"headlines":headlines[:3],"pos":pos,"neg":neg}
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_earnings(symbol):
    try:
        import yfinance as yf
        import pandas as pd2
        cal = yf.Ticker(symbol).calendar
        if cal is None or cal.empty: return None
        if "Earnings Date" not in cal.index: return None
        ed = cal.loc["Earnings Date"]
        next_e = ed.iloc[0] if hasattr(ed,'__len__') else ed
        if not isinstance(next_e, pd2.Timestamp): next_e = pd2.Timestamp(next_e)
        now = pd2.Timestamp.now(tz=next_e.tz)
        days = (next_e-now).days
        warn = days<=2
        msg = ("⚠️ EARNINGS TODAY" if days<=0 else
               f"⚠️ Earnings tomorrow" if days==1 else
               f"⚠️ Earnings in {days}d" if days<=2 else
               f"📅 Earnings {next_e.strftime('%d %b')} ({days}d)")
        return {"warning":warn,"days":days,"msg":msg,"date":next_e.strftime("%d %b %Y")}
    except: return None

def market_status(m):
    tz=pytz.timezone(m["tz"]); now=datetime.now(tz); wd=now.weekday()<5
    oh,om=m["open"]; ch,cm=m["close"]
    ot=now.replace(hour=oh,minute=om,second=0,microsecond=0)
    ct=now.replace(hour=ch,minute=cm,second=0,microsecond=0)
    return now.strftime("%H:%M:%S"), now.strftime("%d %b"), (wd and ot<=now<=ct)


# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
:root{--bg:#060a10;--surf:#0c1220;--bdr:#162030;--bdr2:#1e3048;
    --gold:#c9a84c;--gold2:#e8c97a;--green:#0dff8c;--green2:#00c853;
    --red:#ff3d5a;--text:#c8d8e8;--muted:#4a6278;--white:#eef4ff;}
html,body,[class*="css"]{background:var(--bg)!important;color:var(--text);font-family:'DM Mono',monospace;}
.main .block-container{padding:1.5rem 2.5rem 3rem;max-width:1700px;}
#MainMenu,footer,header,.stDeployButton{display:none!important;}
[data-stale="true"]{opacity:1!important;transition:none!important;}
[data-stale="true"] *{opacity:1!important;transition:none!important;}
.stStatusWidget{display:none!important;}

.hdr{padding-bottom:1.5rem;border-bottom:1px solid var(--bdr2);margin-bottom:1.8rem;}
.hdr-brand{font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
    background:linear-gradient(135deg,var(--gold2),var(--gold),#a07830);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.live-dot{display:inline-block;width:7px;height:7px;background:var(--green);border-radius:50%;
    box-shadow:0 0 8px var(--green);animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.sec{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:3px;
    text-transform:uppercase;color:var(--gold);border-left:2px solid var(--gold);
    padding-left:10px;margin:2rem 0 1rem;}
.clk{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:18px 16px;position:relative;}
.clk::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--bdr2);}
.clk.open::before{background:var(--green2);}
.clk-name{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;letter-spacing:1.5px;
    color:var(--muted);text-transform:uppercase;margin-bottom:8px;}
.clk-time{font-size:26px;font-weight:500;color:var(--white);letter-spacing:1px;margin-bottom:3px;}
.clk-date{font-size:11px;color:var(--muted);margin-bottom:8px;}
.badge-open{font-size:10px;font-weight:700;color:var(--green);letter-spacing:1px;}
.badge-open::before{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;
    background:var(--green);box-shadow:0 0 6px var(--green);margin-right:5px;animation:blink 1.5s infinite;}
.badge-closed{font-size:10px;color:var(--muted);letter-spacing:1px;}
.stat{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:20px;}
.stat-lbl{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:10px;}
.stat-val{font-family:'Syne',sans-serif;font-size:26px;font-weight:700;color:var(--white);}
.gold{color:var(--gold2);} .pos{color:var(--green);} .neg{color:var(--red);}
.sc{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;padding:20px;text-align:center;}
.sc-lbl{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}
.sc-n{font-family:'Syne',sans-serif;font-size:38px;font-weight:800;}
.sc-n.buy{color:var(--green);} .sc-n.sell{color:var(--red);} .sc-n.hold{color:var(--muted);}

/* ENHANCED SIGNAL CARD */
.sig{background:var(--surf);border:1px solid var(--bdr);border-radius:8px;
    padding:16px 20px;margin-bottom:12px;position:relative;overflow:hidden;}
.sig::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;}
.sig.buy{border-color:#0d2818;} .sig.buy::before{background:var(--green);box-shadow:0 0 10px var(--green);}
.sig.sell{border-color:#2d0a0a;} .sig.sell::before{background:var(--red);box-shadow:0 0 10px var(--red);}
.sig-row1{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;}
.sig-sym{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:var(--white);}
.sig-act{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;}
.sig-act.buy{color:var(--green);} .sig-act.sell{color:var(--red);}
.sig-px{font-size:22px;font-weight:500;color:var(--white);text-align:right;}
.sig-chg{font-size:11px;text-align:right;}
.sig-chg.pos{color:var(--green);} .sig-chg.neg{color:var(--red);}

/* CONFIDENCE BADGE */
.conf-strong{background:#052010;border:1px solid var(--green2);border-radius:6px;
    padding:4px 12px;font-size:11px;font-weight:700;color:var(--green);letter-spacing:1px;}
.conf-medium{background:#1a1505;border:1px solid #8a6820;border-radius:6px;
    padding:4px 12px;font-size:11px;font-weight:700;color:var(--gold2);letter-spacing:1px;}
.conf-weak{background:#12121a;border:1px solid #2a3060;border-radius:6px;
    padding:4px 12px;font-size:11px;font-weight:700;color:#6080c0;letter-spacing:1px;}

/* SCORE BAR */
.score-row{display:flex;align-items:center;gap:10px;margin:8px 0;}
.score-bar-wrap{flex:1;height:5px;background:var(--bdr);border-radius:3px;overflow:hidden;}
.score-bar{height:100%;border-radius:3px;transition:width 0.5s;}
.score-bar.high{background:var(--green);}
.score-bar.med{background:var(--gold);}
.score-bar.low{background:#6080c0;}
.score-num{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:var(--white);min-width:35px;}

/* INDICATOR VOTES */
.votes{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;}
.vote{font-size:10px;border-radius:4px;padding:3px 8px;letter-spacing:0.5px;}
.vote.yes-buy{background:#051a10;border:1px solid var(--green2);color:var(--green);}
.vote.yes-sell{background:#1a0505;border:1px solid #c0392b;color:var(--red);}
.vote.no{background:#0c1825;border:1px solid var(--bdr2);color:var(--muted);}

/* NEWS SECTION */
.news-row{margin-top:10px;padding-top:10px;border-top:1px solid var(--bdr);}
.news-label{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}
.news-headline{font-size:11px;color:var(--muted);margin-bottom:3px;line-height:1.5;}
.earnings-warn{background:#1a0c00;border:1px solid #c07020;border-radius:5px;
    padding:5px 10px;font-size:11px;color:#e0a040;margin-bottom:8px;}

/* WATCHING */
.ww{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px;}
.wp{background:var(--surf);border:1px solid var(--bdr);border-radius:4px;
    padding:5px 12px;font-size:11px;letter-spacing:1px;color:var(--muted);}
.empty{background:var(--surf);border:1px dashed var(--bdr2);border-radius:8px;
    padding:40px;text-align:center;color:var(--muted);}
.ftr{margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--bdr);
    display:flex;justify-content:space-between;font-size:11px;color:var(--muted);}
.ftr-brand{font-family:'Syne',sans-serif;font-weight:700;color:var(--gold);}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════
def render():
    now_utc = datetime.now(pytz.utc)
    pf      = get_portfolio()

    # ── HEADER ───────────────────────────────────────────────
    c1,c2 = st.columns([6,1])
    with c1:
        st.markdown(f"""
        <div class='hdr'>
          <div class='hdr-brand'>⚡ AlphaSignal</div>
          <div style='font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-top:3px;'>
            Paper Trading · Raghu · 5 Indicators · News Sentiment
          </div>
          <div style='font-size:11px;color:var(--muted);margin-top:8px;'>
            <span class='live-dot'></span>
            {now_utc.strftime("%d %b %Y  %H:%M:%S")} UTC  ·  {len(ALL_SYMBOLS)} Symbols
          </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("⟳ Refresh", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    # ── AUTO-REFRESH ─────────────────────────────────────────
    r1,r2 = st.columns([1,3])
    with r1:
        rf = st.selectbox("Auto-refresh",list(REFRESH_OPTIONS.keys()),index=2,label_visibility="collapsed")
    with r2:
        ms = REFRESH_OPTIONS[rf]
        if ms>0:
            st_autorefresh(interval=ms, limit=None, key="ar")
            st.markdown(f"<span style='font-size:11px;color:var(--green);'>"
                        f"● Auto-refresh every {rf} — no dimming</span>",
                        unsafe_allow_html=True)
        else:
            st.markdown("<span style='font-size:11px;color:var(--muted);'>○ Manual refresh only</span>",
                        unsafe_allow_html=True)

    # ── MARKET CLOCKS ─────────────────────────────────────────
    st.markdown("<div class='sec'>🌍 Global Market Hours</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i,m in enumerate(MARKETS):
        t,d,is_open = market_status(m)
        badge = "<span class='badge-open'>OPEN</span>" if is_open else "<span class='badge-closed'>○ CLOSED</span>"
        with cols[i]:
            st.markdown(f"""<div class='clk {"open" if is_open else ""}'>
              <div class='clk-name'>{m['flag']} {m['name']} · {m['short']}</div>
              <div class='clk-time'>{t}</div><div class='clk-date'>{d}</div>{badge}
            </div>""", unsafe_allow_html=True)

    # ── PORTFOLIO ─────────────────────────────────────────────
    st.markdown("<div class='sec'>💼 Alpaca Portfolio</div>", unsafe_allow_html=True)
    if pf:
        start=100_000; pl=pf["value"]-start; pct=(pl/start)*100
        cl="pos" if pl>=0 else "neg"; sg="+" if pl>=0 else ""
        p1,p2,p3,p4 = st.columns(4)
        with p1: st.markdown(f"<div class='stat'><div class='stat-lbl'>Portfolio Value</div><div class='stat-val gold'>${pf['value']:,.2f}</div></div>",unsafe_allow_html=True)
        with p2: st.markdown(f"<div class='stat'><div class='stat-lbl'>Cash</div><div class='stat-val'>${pf['cash']:,.2f}</div></div>",unsafe_allow_html=True)
        with p3: st.markdown(f"<div class='stat'><div class='stat-lbl'>Positions</div><div class='stat-val'>{len(pf['positions'])}</div></div>",unsafe_allow_html=True)
        with p4: st.markdown(f"<div class='stat'><div class='stat-lbl'>Total Return</div><div class='stat-val {cl}'>{sg}${pl:,.2f} <span style='font-size:14px;'>{sg}{pct:.2f}%</span></div></div>",unsafe_allow_html=True)
    else:
        st.warning("⚠️ Add ALPACA_API_KEY + ALPACA_SECRET_KEY in Streamlit → Settings → Secrets")

    # ── SIGNALS ───────────────────────────────────────────────
    st.markdown(f"<div class='sec'>🎯 Enhanced Signals · MA · RSI · MACD · Bollinger · Volume</div>", unsafe_allow_html=True)

    with st.spinner(f"Analyzing {len(ALL_SYMBOLS)} symbols from Alpaca..."):
        data = analyze_all()

    if not data:
        st.warning("No data from Alpaca. Market may be closed."); return

    buys  = sorted([r for r in data if r["signal"]=="BUY"],  key=lambda x:-x["score"])
    sells = sorted([r for r in data if r["signal"]=="SELL"], key=lambda x:-x["score"])
    holds = [r for r in data if r["signal"]=="HOLD"]

    sc1,sc2,sc3 = st.columns(3)
    with sc1: st.markdown(f"<div class='sc'><div class='sc-lbl'>Buy Signals</div><div class='sc-n buy'>{len(buys)}</div></div>",unsafe_allow_html=True)
    with sc2: st.markdown(f"<div class='sc'><div class='sc-lbl'>Sell Signals</div><div class='sc-n sell'>{len(sells)}</div></div>",unsafe_allow_html=True)
    with sc3: st.markdown(f"<div class='sc'><div class='sc-lbl'>Monitoring</div><div class='sc-n hold'>{len(holds)}</div></div>",unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def render_signal_card(r, side):
        cc  = "pos" if r["chg"]>=0 else "neg"
        sgn = "+" if r["chg"]>=0 else ""
        lbl = "▲ LONG · BUY" if side=="buy" else "▼ SHORT · SELL"
        conf = r["confidence"]
        score = r["score"]
        ind  = r.get("ind", {})

        conf_badge = (
            f"<span class='conf-strong'>🔥 STRONG</span>" if conf=="STRONG" else
            f"<span class='conf-medium'>⚡ MEDIUM</span>" if conf=="MEDIUM" else
            f"<span class='conf-weak'>💧 WEAK</span>"
        )

        score_cls = "high" if score>=7 else "med" if score>=4 else "low"
        score_pct = score*10

        # Indicator votes
        vote_html = ""
        for ind_name, ind_sig in ind.items():
            if ind_sig == side.upper():
                vote_html += f"<span class='vote yes-{side}'>{ind_name} ✓</span>"
            else:
                vote_html += f"<span class='vote no'>{ind_name} {ind_sig}</span>"

        # News
        news = get_news_for(r["sym"])
        news_html = ""
        if news:
            news_emoji = "🟢" if news["overall"]=="POSITIVE" else "🔴" if news["overall"]=="NEGATIVE" else "⚪"
            news_html = f"""
            <div class='news-row'>
              <div class='news-label'>📰 News Sentiment: {news_emoji} {news["overall"]}
                (score {news["score"]:+.0f})</div>
              {"".join(f"<div class='news-headline'>{h}</div>" for h in news["headlines"][:2])}
            </div>"""

        # Earnings
        earnings = get_earnings(r["sym"])
        earn_html = ""
        if earnings and earnings["warning"]:
            earn_html = f"<div class='earnings-warn'>⚠️ {earnings['msg']}</div>"

        vol_color = "var(--green)" if r["vol_ratio"]>=1.5 else "var(--muted)" if r["vol_ratio"]>=1.0 else "var(--red)"
        vol_label = f"{r['vol_ratio']:.1f}x vol"

        return f"""
        <div class='sig {side}'>
          {earn_html}
          <div class='sig-row1'>
            <div>
              <div class='sig-sym'>{r['sym']}</div>
              <div class='sig-act {side}'>{lbl}</div>
              <div style='margin-top:6px;'>{conf_badge}</div>
            </div>
            <div style='text-align:right;'>
              <div class='sig-px'>${r['price']:.2f}</div>
              <div class='sig-chg {cc}'>{sgn}{r['chg']:.2f}%</div>
              <div style='font-size:11px;color:{vol_color};margin-top:4px;'>{vol_label}</div>
            </div>
          </div>
          <div class='score-row'>
            <div style='font-size:10px;color:var(--muted);min-width:45px;'>Score</div>
            <div class='score-bar-wrap'><div class='score-bar {score_cls}' style='width:{score_pct}%;'></div></div>
            <div class='score-num'>{score:.1f}<span style='font-size:10px;color:var(--muted);'>/10</span></div>
          </div>
          <div class='votes'>{vote_html}</div>
          {news_html}
        </div>"""

    lc,rc = st.columns(2)

    with lc:
        st.markdown("<div style='font-size:13px;font-weight:700;color:var(--green);font-family:Syne,sans-serif;margin-bottom:10px;'>▲ BUY OPPORTUNITIES</div>",unsafe_allow_html=True)
        if buys:
            for r in buys: st.markdown(render_signal_card(r,"buy"),unsafe_allow_html=True)
        else:
            st.markdown("""<div class='empty'><div style='font-size:26px;'>◌</div>
              <div style='margin-top:8px;font-size:13px;'>No buy signals right now</div>
              <div style='font-size:11px;opacity:.5;'>Market closed or no uptrend conditions</div>
            </div>""",unsafe_allow_html=True)

    with rc:
        st.markdown("<div style='font-size:13px;font-weight:700;color:var(--red);font-family:Syne,sans-serif;margin-bottom:10px;'>▼ SELL SIGNALS</div>",unsafe_allow_html=True)
        if sells:
            for r in sells: st.markdown(render_signal_card(r,"sell"),unsafe_allow_html=True)
        else:
            st.markdown("""<div class='empty'><div style='font-size:26px;'>◌</div>
              <div style='margin-top:8px;font-size:13px;'>No sell signals right now</div>
              <div style='font-size:11px;opacity:.5;'>No overbought conditions found</div>
            </div>""",unsafe_allow_html=True)

    # ── MONITORING ────────────────────────────────────────────
    if holds:
        st.markdown("<div class='sec'>👁 Monitoring</div>", unsafe_allow_html=True)
        pills = "".join([f"<span class='wp'>{r['sym']}</span>" for r in holds])
        st.markdown(f"<div class='ww'>{pills}</div>",unsafe_allow_html=True)

    # ── POSITIONS ─────────────────────────────────────────────
    if pf and pf["positions"]:
        st.markdown("<div class='sec'>📂 Open Positions</div>", unsafe_allow_html=True)
        rows=[]
        for p in pf["positions"]:
            rows.append({"Symbol":p["sym"],"Qty":p["qty"],
                "Entry":f"${p['entry']:.2f}","Value":f"${p['val']:,.2f}",
                "P/L $":f"${p['pl']:+.2f}","P/L %":f"{p['plpct']:+.2f}%"})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    # ── FOOTER ────────────────────────────────────────────────
    st.markdown(f"""
    <div class='ftr'>
      <div><span class='ftr-brand'>⚡ AlphaSignal</span>
        &nbsp;·&nbsp; Paper Only · Not Financial Advice
      </div>
      <div>5 Indicators · News · Earnings Guard · Alpaca API · {len(ALL_SYMBOLS)} symbols</div>
    </div>""",unsafe_allow_html=True)

render()
