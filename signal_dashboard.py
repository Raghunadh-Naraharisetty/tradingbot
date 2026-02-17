"""
SIGNAL_DASHBOARD.PY - Clean Signal Dashboard with Timezones
============================================================
Replaces the overwhelming matrix dashboard.

Shows:
1. Live market clocks (US, India, London, Tokyo)
2. Active signals only (BUY/SELL - no clutter)
3. Portfolio status from Alpaca
4. Clean, simple layout

Usage:
    streamlit run signal_dashboard.py
"""

import streamlit as st
from datetime import datetime
import pytz
import config
from model import TradingModel
import pandas as pd

try:
    from alpaca_integration import AlpacaTrader
    ALPACA_AVAILABLE = True
except:
    ALPACA_AVAILABLE = False


st.set_page_config(
    page_title="Raghu Trading Signals",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean dark theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #e0e0e0;
    }

    .main { padding: 1rem 2rem; }

    /* Market clock cards */
    .clock-card {
        background: #1a1d27;
        border: 1px solid #2d3045;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        margin: 4px;
    }
    .clock-open {
        border-color: #00c853;
        box-shadow: 0 0 12px rgba(0,200,83,0.15);
    }
    .clock-closed {
        border-color: #37474f;
        opacity: 0.7;
    }
    .clock-name {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #78909c;
        margin-bottom: 4px;
    }
    .clock-time {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 700;
        color: #e0e0e0;
        margin-bottom: 4px;
    }
    .clock-status-open {
        font-size: 11px;
        color: #00c853;
        font-weight: 600;
    }
    .clock-status-closed {
        font-size: 11px;
        color: #546e7a;
    }

    /* Signal cards */
    .signal-buy {
        background: linear-gradient(135deg, #0d2818 0%, #1a3a22 100%);
        border: 1px solid #00c853;
        border-left: 4px solid #00c853;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 8px 0;
    }
    .signal-sell {
        background: linear-gradient(135deg, #2d0a0a 0%, #3d1212 100%);
        border: 1px solid #ff5252;
        border-left: 4px solid #ff5252;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 8px 0;
    }
    .signal-symbol {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #ffffff;
    }
    .signal-action-buy { color: #00c853; font-size: 14px; font-weight: 600; }
    .signal-action-sell { color: #ff5252; font-size: 14px; font-weight: 600; }
    .signal-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 20px;
        font-weight: 700;
        color: #e0e0e0;
    }
    .signal-detail { font-size: 12px; color: #78909c; margin-top: 6px; }

    /* Section headers */
    .section-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #546e7a;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e2130;
    }

    /* Portfolio cards */
    .portfolio-card {
        background: #1a1d27;
        border: 1px solid #2d3045;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .portfolio-label {
        font-size: 11px;
        color: #546e7a;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .portfolio-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 20px;
        font-weight: 700;
        color: #e0e0e0;
    }
    .portfolio-positive { color: #00c853; }
    .portfolio-negative { color: #ff5252; }

    /* Watching card */
    .watching-card {
        background: #1a1d27;
        border: 1px solid #2d3045;
        border-radius: 8px;
        padding: 10px 14px;
        display: inline-block;
        margin: 3px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #90a4ae;
    }

    /* No signal state */
    .no-signal {
        background: #1a1d27;
        border: 1px dashed #2d3045;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        color: #546e7a;
        font-size: 14px;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# MARKET CLOCK DATA
# ─────────────────────────────────────────

MARKETS = [
    {
        'name': 'US (NYSE)',
        'tz': 'America/New_York',
        'open': (9, 30),
        'close': (16, 0),
        'days': range(0, 5),
        'flag': '🇺🇸'
    },
    {
        'name': 'India (NSE)',
        'tz': 'Asia/Kolkata',
        'open': (9, 15),
        'close': (15, 30),
        'days': range(0, 5),
        'flag': '🇮🇳'
    },
    {
        'name': 'London (LSE)',
        'tz': 'Europe/London',
        'open': (8, 0),
        'close': (16, 30),
        'days': range(0, 5),
        'flag': '🇬🇧'
    },
    {
        'name': 'Tokyo (TSE)',
        'tz': 'Asia/Tokyo',
        'open': (9, 0),
        'close': (15, 30),
        'days': range(0, 5),
        'flag': '🇯🇵'
    },
]


def get_market_status(market):
    """Get current time and open/closed status for a market."""
    tz = pytz.timezone(market['tz'])
    now = datetime.now(tz)
    
    is_weekday = now.weekday() in market['days']
    open_h, open_m = market['open']
    close_h, close_m = market['close']
    
    open_time = now.replace(hour=open_h, minute=open_m, second=0)
    close_time = now.replace(hour=close_h, minute=close_m, second=0)
    
    is_open = is_weekday and open_time <= now <= close_time
    
    return {
        'time': now.strftime('%H:%M:%S'),
        'date': now.strftime('%d %b'),
        'is_open': is_open,
        'name': market['name'],
        'flag': market['flag']
    }


# ─────────────────────────────────────────
# SIGNAL ANALYSIS
# ─────────────────────────────────────────

@st.cache_data(ttl=60)
def get_signals():
    """Get current signals for all symbols."""
    results = []
    model = TradingModel()

    for symbol in config.SYMBOLS:
        try:
            model.fetch_market_data(symbol)
            model.calculate_all_indicators(symbol)

            df = model.market_data.get(symbol)
            if df is None or df.empty:
                continue

            current = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else current

            # Individual strategy signals
            ma_signal = model.detect_crossover(symbol) if config.STRATEGIES_ENABLED.get('ma_crossover') else 'HOLD'

            rsi = current.get('RSI', 50)
            if rsi < config.RSI_OVERSOLD:
                rsi_signal = 'BUY'
            elif rsi > config.RSI_OVERBOUGHT:
                rsi_signal = 'SELL'
            else:
                rsi_signal = 'HOLD'

            final_signal = model.generate_multi_strategy_signal(symbol)

            price_change = ((current['Close'] - previous['Close']) / previous['Close']) * 100

            results.append({
                'symbol': symbol,
                'price': current['Close'],
                'change_pct': price_change,
                'signal': final_signal,
                'ma_signal': ma_signal,
                'rsi_signal': rsi_signal,
                'rsi': rsi,
                'ma_fast': current.get('MA_Fast', 0),
                'ma_slow': current.get('MA_Slow', 0),
            })

        except:
            continue

    return results


@st.cache_data(ttl=30)
def get_alpaca_portfolio():
    """Get portfolio from Alpaca."""
    if not ALPACA_AVAILABLE:
        return None
    try:
        trader = AlpacaTrader()
        account = trader.get_account()
        positions = trader.get_all_positions()
        return {
            'portfolio_value': float(account.portfolio_value),
            'cash': float(account.cash),
            'buying_power': float(account.buying_power),
            'equity': float(account.equity),
            'positions': positions
        }
    except:
        return None


# ─────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────

def main():
    # Title
    st.markdown("""
    <div style='display:flex; align-items:center; gap:12px; margin-bottom:4px;'>
        <span style='font-size:28px; font-weight:700; color:#ffffff;'>📈 Trading Signals</span>
        <span style='font-size:13px; color:#546e7a; font-family:JetBrains Mono;'>by Raghu</span>
    </div>
    """, unsafe_allow_html=True)

    # Last updated
    st.markdown(f"""
    <div style='font-size:12px; color:#546e7a; margin-bottom:20px;
                font-family:JetBrains Mono;'>
        Last updated: {datetime.now().strftime('%H:%M:%S')}  •  
        Alpaca Paper Trading  •  {len(config.SYMBOLS)} symbols
    </div>
    """, unsafe_allow_html=True)

    # ── MARKET CLOCKS ──────────────────────────────────────────
    st.markdown("<div class='section-title'>🌍 Market Clocks</div>", unsafe_allow_html=True)

    cols = st.columns(4)
    for i, market in enumerate(MARKETS):
        status = get_market_status(market)
        card_class = "clock-open" if status['is_open'] else "clock-closed"
        status_class = "clock-status-open" if status['is_open'] else "clock-status-closed"
        status_text = "● OPEN" if status['is_open'] else "○ CLOSED"

        with cols[i]:
            st.markdown(f"""
            <div class='clock-card {card_class}'>
                <div class='clock-name'>{status['flag']} {status['name']}</div>
                <div class='clock-time'>{status['time']}</div>
                <div class='clock-name' style='font-size:10px;'>{status['date']}</div>
                <div class='{status_class}'>{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── ALPACA PORTFOLIO ────────────────────────────────────────
    portfolio = get_alpaca_portfolio()
    if portfolio:
        st.markdown("<div class='section-title'>💼 Alpaca Portfolio</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)

        start_capital = 100000.00
        total_pl = portfolio['portfolio_value'] - start_capital
        pl_class = "portfolio-positive" if total_pl >= 0 else "portfolio-negative"
        pl_sign = "+" if total_pl >= 0 else ""

        with c1:
            st.markdown(f"""
            <div class='portfolio-card'>
                <div class='portfolio-label'>Portfolio Value</div>
                <div class='portfolio-value'>${portfolio['portfolio_value']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='portfolio-card'>
                <div class='portfolio-label'>Cash Available</div>
                <div class='portfolio-value'>${portfolio['cash']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class='portfolio-card'>
                <div class='portfolio-label'>Open Positions</div>
                <div class='portfolio-value'>{len(portfolio['positions'])}</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class='portfolio-card'>
                <div class='portfolio-label'>Total P/L</div>
                <div class='portfolio-value {pl_class}'>{pl_sign}${total_pl:,.2f}</div>
            </div>""", unsafe_allow_html=True)

    # ── SIGNALS ─────────────────────────────────────────────────
    with st.spinner("Analyzing signals..."):
        all_results = get_signals()

    buy_signals = [r for r in all_results if r['signal'] == 'BUY']
    sell_signals = [r for r in all_results if r['signal'] == 'SELL']
    hold_count = len([r for r in all_results if r['signal'] == 'HOLD'])

    # Signal summary
    st.markdown("<div class='section-title'>🎯 Active Signals</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.markdown(f"""
        <div class='portfolio-card'>
            <div class='portfolio-label'>BUY Signals</div>
            <div class='portfolio-value portfolio-positive'>{len(buy_signals)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='portfolio-card'>
            <div class='portfolio-label'>SELL Signals</div>
            <div class='portfolio-value portfolio-negative'>{len(sell_signals)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='portfolio-card'>
            <div class='portfolio-label'>Monitoring (HOLD)</div>
            <div class='portfolio-value' style='font-size:16px; color:#546e7a;'>
                {hold_count} symbols watching
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # BUY signals
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("<div style='font-size:13px; font-weight:600; color:#00c853; margin-bottom:10px;'>🟢 BUY OPPORTUNITIES</div>", unsafe_allow_html=True)

        if buy_signals:
            for r in buy_signals:
                change_color = "#00c853" if r['change_pct'] >= 0 else "#ff5252"
                sign = "+" if r['change_pct'] >= 0 else ""
                
                # Which strategies agree
                agrees = []
                if r['ma_signal'] == 'BUY': agrees.append("MA✓")
                if r['rsi_signal'] == 'BUY': agrees.append("RSI✓")
                agree_text = "  ".join(agrees)

                st.markdown(f"""
                <div class='signal-buy'>
                    <div style='display:flex; justify-content:space-between; align-items:start;'>
                        <div>
                            <div class='signal-symbol'>{r['symbol']}</div>
                            <div class='signal-action-buy'>▲ BUY SIGNAL</div>
                        </div>
                        <div style='text-align:right;'>
                            <div class='signal-price'>${r['price']:.2f}</div>
                            <div style='font-size:12px; color:{change_color};'>{sign}{r['change_pct']:.2f}% today</div>
                        </div>
                    </div>
                    <div class='signal-detail'>
                        RSI: {r['rsi']:.1f}  •  MA Fast: ${r['ma_fast']:.2f}  •  MA Slow: ${r['ma_slow']:.2f}  •  <b style='color:#00c853;'>{agree_text}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='no-signal'>
                <div style='font-size:20px; margin-bottom:8px;'>⚪</div>
                No BUY signals right now<br>
                <span style='font-size:12px;'>Market may be closed or no clear trends</span>
            </div>""", unsafe_allow_html=True)

    # SELL signals
    with right_col:
        st.markdown("<div style='font-size:13px; font-weight:600; color:#ff5252; margin-bottom:10px;'>🔴 SELL SIGNALS</div>", unsafe_allow_html=True)

        if sell_signals:
            for r in sell_signals:
                change_color = "#00c853" if r['change_pct'] >= 0 else "#ff5252"
                sign = "+" if r['change_pct'] >= 0 else ""
                
                agrees = []
                if r['ma_signal'] == 'SELL': agrees.append("MA✓")
                if r['rsi_signal'] == 'SELL': agrees.append("RSI✓")
                agree_text = "  ".join(agrees)

                st.markdown(f"""
                <div class='signal-sell'>
                    <div style='display:flex; justify-content:space-between; align-items:start;'>
                        <div>
                            <div class='signal-symbol'>{r['symbol']}</div>
                            <div class='signal-action-sell'>▼ SELL SIGNAL</div>
                        </div>
                        <div style='text-align:right;'>
                            <div class='signal-price'>${r['price']:.2f}</div>
                            <div style='font-size:12px; color:{change_color};'>{sign}{r['change_pct']:.2f}% today</div>
                        </div>
                    </div>
                    <div class='signal-detail'>
                        RSI: {r['rsi']:.1f}  •  MA Fast: ${r['ma_fast']:.2f}  •  MA Slow: ${r['ma_slow']:.2f}  •  <b style='color:#ff5252;'>{agree_text}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='no-signal'>
                <div style='font-size:20px; margin-bottom:8px;'>⚪</div>
                No SELL signals right now<br>
                <span style='font-size:12px;'>No overbought conditions detected</span>
            </div>""", unsafe_allow_html=True)

    # ── WATCHING LIST ────────────────────────────────────────────
    hold_symbols = [r['symbol'] for r in all_results if r['signal'] == 'HOLD']
    if hold_symbols:
        st.markdown("<div class='section-title'>👁 Watching (No Signal Yet)</div>", unsafe_allow_html=True)
        symbols_html = "".join([f"<span class='watching-card'>{s}</span>" for s in hold_symbols])
        st.markdown(f"<div style='margin-bottom:16px;'>{symbols_html}</div>", unsafe_allow_html=True)

    # ── ALPACA OPEN POSITIONS ────────────────────────────────────
    if portfolio and portfolio['positions']:
        st.markdown("<div class='section-title'>📂 Open Positions (Alpaca)</div>", unsafe_allow_html=True)
        
        pos_data = []
        for p in portfolio['positions']:
            pl_pct = p['unrealized_plpc'] * 100
            pos_data.append({
                'Symbol': p['symbol'],
                'Shares': p['qty'],
                'Entry Price': f"${p['avg_entry_price']:.2f}",
                'Market Value': f"${p['market_value']:.2f}",
                'Unrealized P/L': f"${p['unrealized_pl']:+.2f}",
                'P/L %': f"{pl_pct:+.2f}%"
            })
        
        st.dataframe(pd.DataFrame(pos_data), use_container_width=True, hide_index=True)

    # ── FOOTER ──────────────────────────────────────────────────
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div style='font-size:11px; color:#37474f;'>
        ⚠️ Paper trading only — No real money involved  •  
        Data from Yahoo Finance (dashboard) & Alpaca (scheduler)  •  
        Not financial advice
        </div>""", unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


if __name__ == "__main__":
    main()
