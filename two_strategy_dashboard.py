"""
TWO_STRATEGY_DASHBOARD.PY - Simplified Trading Dashboard
=========================================================
Shows ONLY the 2 best strategies for cash trading:
1. MA Crossover (Trend)
2. RSI (Timing)

Clean, focused, and actionable!

Usage:
    streamlit run two_strategy_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import config
from model import TradingModel
from datetime import datetime
import time


st.set_page_config(
    page_title="2-Strategy Trading - Raghu",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .buy-box {
        background-color: #28a745;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .sell-box {
        background-color: #dc3545;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .hold-box {
        background-color: #6c757d;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .strategy-agree {
        color: #28a745;
        font-weight: bold;
    }
    .strategy-disagree {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def analyze_with_two_strategies():
    """Analyze using only MA + RSI."""
    model = TradingModel()
    results = []
    
    for symbol in config.SYMBOLS:
        try:
            model.fetch_market_data(symbol)
            model.calculate_all_indicators(symbol)
            
            df = model.market_data.get(symbol)
            if df is None or df.empty:
                continue
            
            current = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else current
            
            # Strategy 1: MA Crossover
            ma_signal = model.detect_crossover(symbol)
            
            # Strategy 2: RSI
            rsi = current.get('RSI', 50)
            if rsi < 30:
                rsi_signal = 'BUY'
            elif rsi > 70:
                rsi_signal = 'SELL'
            else:
                rsi_signal = 'HOLD'
            
            # Final signal: Both must agree
            if ma_signal == 'BUY' and rsi_signal == 'BUY':
                final = 'BUY'
            elif ma_signal == 'SELL' and rsi_signal == 'SELL':
                final = 'SELL'
            else:
                final = 'HOLD'
            
            # Additional info
            price_change = ((current['Close'] - previous['Close']) / previous['Close']) * 100
            ma_fast = current.get('MA_Fast', 0)
            ma_slow = current.get('MA_Slow', 0)
            
            results.append({
                'Symbol': symbol,
                'Price': current['Close'],
                'Change%': price_change,
                'MA_Signal': ma_signal,
                'RSI_Signal': rsi_signal,
                'Final': final,
                'RSI': rsi,
                'MA_Fast': ma_fast,
                'MA_Slow': ma_slow,
                'Trend': 'Uptrend' if ma_fast > ma_slow else 'Downtrend'
            })
        
        except Exception as e:
            continue
    
    return pd.DataFrame(results)


def main():
    # Header
    st.title("🎯 2-Strategy Trading Dashboard")
    st.caption(f"MA Crossover + RSI | Developed by Raghu | {datetime.now().strftime('%H:%M:%S')}")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        auto_refresh = st.checkbox("Auto-refresh (60s)")
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Strategy Info")
        st.info("""
        **MA Crossover:** Trend direction
        - Fast MA > Slow MA = Uptrend (BUY)
        - Fast MA < Slow MA = Downtrend (SELL)
        
        **RSI:** Entry timing
        - RSI < 30 = Oversold (BUY)
        - RSI > 70 = Overbought (SELL)
        - RSI 30-70 = Neutral (HOLD)
        
        **Signal:** BOTH must agree!
        """)
        
        st.markdown("---")
        st.info(f"Monitoring: {len(config.SYMBOLS)} symbols")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(60)
        st.rerun()
    
    # Analysis
    with st.spinner('Analyzing...'):
        df = analyze_with_two_strategies()
        
        if df.empty:
            st.error("No data available")
            return
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        
        buy_count = len(df[df['Final'] == 'BUY'])
        sell_count = len(df[df['Final'] == 'SELL'])
        hold_count = len(df[df['Final'] == 'HOLD'])
        agreement_rate = ((buy_count + sell_count) / len(df) * 100) if len(df) > 0 else 0
        
        with col1:
            st.metric("Total Symbols", len(df))
        with col2:
            st.metric("🟢 BUY", buy_count, delta="Strong signals")
        with col3:
            st.metric("🔴 SELL", sell_count, delta="Exit signals")
        with col4:
            st.metric("Agreement", f"{agreement_rate:.0f}%")
        
        st.markdown("---")
        
        # BUY Signals
        buy_df = df[df['Final'] == 'BUY']
        if not buy_df.empty:
            st.subheader("🟢 BUY Opportunities")
            
            for _, row in buy_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"### {row['Symbol']}")
                        st.write(f"**Price:** ${row['Price']:.2f} ({row['Change%']:+.2f}%)")
                        st.write(f"**Trend:** {row['Trend']}")
                    
                    with col2:
                        st.markdown("**Strategy Agreement:**")
                        st.markdown(f"MA Crossover: <span class='strategy-agree'>✅ {row['MA_Signal']}</span>", unsafe_allow_html=True)
                        st.markdown(f"RSI: <span class='strategy-agree'>✅ {row['RSI_Signal']}</span> (RSI: {row['RSI']:.1f})", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("<div class='buy-box'>🟢 BUY</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
        
        # SELL Signals
        sell_df = df[df['Final'] == 'SELL']
        if not sell_df.empty:
            st.subheader("🔴 SELL Signals")
            
            for _, row in sell_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"### {row['Symbol']}")
                        st.write(f"**Price:** ${row['Price']:.2f} ({row['Change%']:+.2f}%)")
                        st.write(f"**Trend:** {row['Trend']}")
                    
                    with col2:
                        st.markdown("**Strategy Agreement:**")
                        st.markdown(f"MA Crossover: <span class='strategy-agree'>✅ {row['MA_Signal']}</span>", unsafe_allow_html=True)
                        st.markdown(f"RSI: <span class='strategy-agree'>✅ {row['RSI_Signal']}</span> (RSI: {row['RSI']:.1f})", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("<div class='sell-box'>🔴 SELL</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
        
        # HOLD / Disagreement
        hold_df = df[df['Final'] == 'HOLD']
        if not hold_df.empty:
            with st.expander(f"📊 Monitoring ({len(hold_df)} symbols) - Strategies disagree"):
                for _, row in hold_df.iterrows():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**{row['Symbol']}** - ${row['Price']:.2f} ({row['Change%']:+.2f}%)")
                    
                    with col2:
                        st.write(f"MA: {row['MA_Signal']} | RSI: {row['RSI_Signal']} (RSI: {row['RSI']:.0f})")
        
        # Footer
        st.markdown("---")
        st.caption("💡 **Signals only appear when BOTH strategies agree** - Ensures high-quality trades")


if __name__ == "__main__":
    main()
