"""
MATRIX_DASHBOARD.PY - Multi-Symbol Strategy Matrix View
========================================================
Shows all symbols and all strategy signals in a color-coded table.

Perfect for monitoring many stocks at once!

Usage:
    streamlit run matrix_dashboard.py
"""

import streamlit as st
import pandas as pd
import config
from model import TradingModel
from datetime import datetime
import time


# Page configuration
st.set_page_config(
    page_title="Trading Matrix - Raghu",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colored cells
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Table styling */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    
    th {
        background-color: #262730;
        color: white;
        padding: 12px;
        text-align: center;
        font-weight: bold;
    }
    
    td {
        padding: 12px;
        text-align: center;
        border: 1px solid #ddd;
    }
    
    .buy-cell {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold;
    }
    
    .sell-cell {
        background-color: #dc3545 !important;
        color: white !important;
        font-weight: bold;
    }
    
    .hold-cell {
        background-color: #ffc107 !important;
        color: #000 !important;
        font-weight: bold;
    }
    
    .price-up {
        color: #28a745;
        font-weight: bold;
    }
    
    .price-down {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def get_signal_color(signal):
    """Return HTML color class for signal."""
    if signal == 'BUY':
        return 'buy-cell'
    elif signal == 'SELL':
        return 'sell-cell'
    else:
        return 'hold-cell'


@st.cache_data(ttl=60)  # Cache for 60 seconds
def analyze_all_symbols():
    """Analyze all symbols and return matrix data."""
    model = TradingModel()
    results = []
    
    for symbol in config.SYMBOLS:
        try:
            # Fetch and calculate
            model.fetch_market_data(symbol)
            model.calculate_all_indicators(symbol)
            
            df = model.market_data.get(symbol)
            if df is None or df.empty:
                continue
            
            current = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else current
            
            # Get individual strategy signals
            ma_signal = model.detect_crossover(symbol) if config.STRATEGIES_ENABLED.get('ma_crossover') else 'HOLD'
            macd_signal = model.check_macd_signal(symbol) if config.STRATEGIES_ENABLED.get('macd') else 'HOLD'
            bb_signal = model.check_bollinger_signal(symbol) if config.STRATEGIES_ENABLED.get('bollinger') else 'HOLD'
            
            # Volume check
            volume_ok = model.check_volume_confirmation(symbol) if config.STRATEGIES_ENABLED.get('volume') else True
            volume_signal = 'BUY' if volume_ok and current.get('Volume_Ratio', 0) > 1.5 else 'HOLD'
            
            # RSI signal
            rsi = current.get('RSI', 50)
            if rsi < 30:
                rsi_signal = 'BUY'
            elif rsi > 70:
                rsi_signal = 'SELL'
            else:
                rsi_signal = 'HOLD'
            
            # Final signal
            final_signal = model.generate_multi_strategy_signal(symbol)
            
            # Price change
            price_change = ((current['Close'] - previous['Close']) / previous['Close']) * 100
            
            results.append({
                'Symbol': symbol,
                'Price': current['Close'],
                'Change%': price_change,
                'MA Cross': ma_signal,
                'MACD': macd_signal,
                'Bollinger': bb_signal,
                'RSI': rsi_signal,
                'Volume': volume_signal,
                'Final': final_signal,
                'RSI_Value': rsi,
                'Volume_Ratio': current.get('Volume_Ratio', 1.0)
            })
        
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {e}")
            continue
    
    return pd.DataFrame(results)


def create_html_table(df):
    """Create color-coded HTML table."""
    html = '<table style="width:100%; border-collapse: collapse;">'
    
    # Header
    html += '<thead><tr>'
    html += '<th>Symbol</th>'
    html += '<th>Price</th>'
    html += '<th>Change %</th>'
    html += '<th>MA Cross</th>'
    html += '<th>MACD</th>'
    html += '<th>Bollinger</th>'
    html += '<th>RSI</th>'
    html += '<th>Volume</th>'
    html += '<th>FINAL</th>'
    html += '</tr></thead>'
    
    # Body
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        
        # Symbol
        html += f'<td style="font-weight: bold; font-size: 16px;">{row["Symbol"]}</td>'
        
        # Price
        html += f'<td style="font-weight: bold;">${row["Price"]:.2f}</td>'
        
        # Change %
        change_class = 'price-up' if row['Change%'] >= 0 else 'price-down'
        html += f'<td class="{change_class}">{row["Change%"]:+.2f}%</td>'
        
        # Strategy signals
        for col in ['MA Cross', 'MACD', 'Bollinger', 'RSI', 'Volume']:
            signal = row[col]
            color_class = get_signal_color(signal)
            html += f'<td class="{color_class}">{signal}</td>'
        
        # Final signal - larger and bold
        final_signal = row['Final']
        final_color = get_signal_color(final_signal)
        html += f'<td class="{final_color}" style="font-size: 18px; font-weight: bold;">{final_signal}</td>'
        
        html += '</tr>'
    
    html += '</tbody></table>'
    return html


def main():
    """Main dashboard function."""
    
    # Title
    st.title("📊 Multi-Symbol Strategy Matrix")
    st.markdown("**Developed by Raghu with Claude** | All symbols and strategies at a glance")
    
    # Sidebar
    st.sidebar.title("⚙️ Controls")
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("Auto-refresh (every 60s)", value=False)
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 30, 300, 60)
    
    if auto_refresh:
        st.sidebar.info(f"⏰ Auto-refreshing every {refresh_interval}s")
        time.sleep(refresh_interval)
        st.rerun()
    
    # Manual refresh
    if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Strategy filter
    st.sidebar.subheader("Strategy Filters")
    show_buy_only = st.sidebar.checkbox("Show only BUY signals")
    show_sell_only = st.sidebar.checkbox("Show only SELL signals")
    
    # Info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Color Legend")
    st.sidebar.markdown("🟢 **Green** = BUY signal")
    st.sidebar.markdown("🔴 **Red** = SELL signal")
    st.sidebar.markdown("🟡 **Yellow** = HOLD signal")
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"Monitoring {len(config.SYMBOLS)} symbols")
    st.sidebar.info(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Main content
    with st.spinner('Analyzing all symbols...'):
        df = analyze_all_symbols()
        
        if df.empty:
            st.error("No data available")
            return
        
        # Apply filters
        if show_buy_only:
            df = df[df['Final'] == 'BUY']
        elif show_sell_only:
            df = df[df['Final'] == 'SELL']
        
        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_symbols = len(df)
        buy_signals = len(df[df['Final'] == 'BUY'])
        sell_signals = len(df[df['Final'] == 'SELL'])
        hold_signals = len(df[df['Final'] == 'HOLD'])
        
        with col1:
            st.metric("Total Symbols", total_symbols)
        with col2:
            st.metric("🟢 BUY Signals", buy_signals)
        with col3:
            st.metric("🔴 SELL Signals", sell_signals)
        with col4:
            st.metric("🟡 HOLD Signals", hold_signals)
        with col5:
            active_pct = ((buy_signals + sell_signals) / total_symbols * 100) if total_symbols > 0 else 0
            st.metric("Active %", f"{active_pct:.1f}%")
        
        # Matrix table
        st.markdown("---")
        st.subheader("📊 Strategy Matrix")
        
        # Display HTML table
        html_table = create_html_table(df)
        st.markdown(html_table, unsafe_allow_html=True)
        
        # Additional details
        st.markdown("---")
        
        # BUY opportunities
        buy_df = df[df['Final'] == 'BUY']
        if not buy_df.empty:
            st.subheader("🟢 BUY Opportunities")
            for _, row in buy_df.iterrows():
                with st.expander(f"{row['Symbol']} - ${row['Price']:.2f} ({row['Change%']:+.2f}%)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**RSI:** {row['RSI_Value']:.1f}")
                        st.write(f"**Volume Ratio:** {row['Volume_Ratio']:.2f}x")
                    with col2:
                        strategies = []
                        for strat in ['MA Cross', 'MACD', 'Bollinger', 'RSI', 'Volume']:
                            if row[strat] == 'BUY':
                                strategies.append(strat)
                        st.write(f"**Agreeing Strategies:** {', '.join(strategies)}")
        
        # SELL opportunities
        sell_df = df[df['Final'] == 'SELL']
        if not sell_df.empty:
            st.subheader("🔴 SELL Opportunities")
            for _, row in sell_df.iterrows():
                with st.expander(f"{row['Symbol']} - ${row['Price']:.2f} ({row['Change%']:+.2f}%)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**RSI:** {row['RSI_Value']:.1f}")
                        st.write(f"**Volume Ratio:** {row['Volume_Ratio']:.2f}x")
                    with col2:
                        strategies = []
                        for strat in ['MA Cross', 'MACD', 'Bollinger', 'RSI', 'Volume']:
                            if row[strat] == 'SELL':
                                strategies.append(strat)
                        st.write(f"**Agreeing Strategies:** {', '.join(strategies)}")
        
        # Download option
        st.markdown("---")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"trading_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
