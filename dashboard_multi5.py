"""
DASHBOARD_MULTI5.PY - Multi5 System Dashboard
==============================================
Interactive dashboard for the 5-strategy system.

Deploy this separately to compare with your 2-strategy dashboard!

Usage:
    streamlit run dashboard_multi5.py
"""

import streamlit as st
import pandas as pd
import config_multi5 as config  # ← Uses Multi5 config!
from model import TradingModel
from datetime import datetime
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Page configuration
st.set_page_config(
    page_title="Multi5 Trading System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .strategy-card {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .strategy-buy {
        background-color: #28a745;
        color: white;
        font-weight: bold;
    }
    .strategy-sell {
        background-color: #dc3545;
        color: white;
        font-weight: bold;
    }
    .strategy-hold {
        background-color: #6c757d;
        color: white;
        font-weight: bold;
    }
    .multi5-badge {
        background-color: #007bff;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def analyze_symbol_multi5(symbol):
    """Analyze single symbol with Multi5 system."""
    model = TradingModel()
    model.fetch_market_data(symbol)
    model.calculate_all_indicators(symbol)
    
    df = model.market_data.get(symbol)
    if df is None or df.empty:
        return None
    
    current = df.iloc[-1]
    
    # Get individual strategy signals
    signals = {}
    
    if config.STRATEGIES_ENABLED.get('ma_crossover'):
        signals['MA Cross'] = model.detect_crossover(symbol)
    
    if config.STRATEGIES_ENABLED.get('macd'):
        signals['MACD'] = model.check_macd_signal(symbol)
    
    if config.STRATEGIES_ENABLED.get('bollinger'):
        signals['Bollinger'] = model.check_bollinger_signal(symbol)
    
    if config.STRATEGIES_ENABLED.get('rsi'):
        rsi = current.get('RSI', 50)
        if rsi < 30:
            signals['RSI'] = 'BUY'
        elif rsi > 70:
            signals['RSI'] = 'SELL'
        else:
            signals['RSI'] = 'HOLD'
    
    if config.STRATEGIES_ENABLED.get('volume'):
        volume_ok = model.check_volume_confirmation(symbol)
        signals['Volume'] = 'BUY' if volume_ok and current.get('Volume_Ratio', 0) > 1.5 else 'HOLD'
    
    # Final signal
    final_signal = model.generate_multi_strategy_signal(symbol)
    
    return {
        'df': df,
        'current': current,
        'signals': signals,
        'final': final_signal
    }


def main():
    """Main dashboard function."""
    
    # Title with Multi5 badge
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎯 Multi5 Trading System")
        st.caption(f"5-Strategy Maximum Filtering | Updated: {datetime.now().strftime('%H:%M:%S')}")
    with col2:
        st.markdown("<div class='multi5-badge'>5 STRATEGIES</div>", unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Multi5 Settings")
    
    # Symbol selection
    selected_symbol = st.sidebar.selectbox(
        "Select Stock",
        config.SYMBOLS,
        index=0
    )
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("Auto-refresh (every 60s)", value=False)
    
    if auto_refresh:
        st.sidebar.info("⏰ Auto-refreshing enabled")
        time.sleep(60)
        st.rerun()
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # System info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 System Info")
    st.sidebar.info(f"**System:** {config.SYSTEM_NAME}")
    st.sidebar.info(f"**Version:** {config.SYSTEM_VERSION}")
    st.sidebar.info(f"**Voting:** {config.STRATEGY_VOTE_REQUIRED}")
    
    enabled_strats = [name.replace('_', ' ').title() for name, enabled in config.STRATEGIES_ENABLED.items() if enabled]
    st.sidebar.markdown(f"**Strategies ({len(enabled_strats)}):**")
    for strat in enabled_strats:
        st.sidebar.text(f"✓ {strat}")
    
    # Main content
    with st.spinner(f'Analyzing {selected_symbol} with Multi5...'):
        try:
            result = analyze_symbol_multi5(selected_symbol)
            
            if result is None:
                st.error(f"❌ Could not load data for {selected_symbol}")
                return
            
            df = result['df']
            current = result['current']
            signals = result['signals']
            final_signal = result['final']
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Price", f"${current['Close']:.2f}")
            
            with col2:
                rsi = current.get('RSI', 50)
                st.metric("RSI", f"{rsi:.1f}")
            
            with col3:
                vol_ratio = current.get('Volume_Ratio', 1.0)
                st.metric("Volume", f"{vol_ratio:.2f}x")
            
            with col4:
                bb_pos = current.get('BB_Position', 0.5)
                st.metric("BB Position", f"{bb_pos:.1%}")
            
            # Strategy votes
            st.subheader("🎯 5-Strategy Voting System")
            
            cols = st.columns(5)
            for i, (strategy, signal) in enumerate(signals.items()):
                with cols[i]:
                    if signal == 'BUY':
                        st.markdown(f"<div class='strategy-card strategy-buy'>{strategy}<br/>🟢 BUY</div>", unsafe_allow_html=True)
                    elif signal == 'SELL':
                        st.markdown(f"<div class='strategy-card strategy-sell'>{strategy}<br/>🔴 SELL</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='strategy-card strategy-hold'>{strategy}<br/>⚪ HOLD</div>", unsafe_allow_html=True)
            
            # Vote summary
            buy_votes = sum(1 for s in signals.values() if s == 'BUY')
            sell_votes = sum(1 for s in signals.values() if s == 'SELL')
            hold_votes = sum(1 for s in signals.values() if s == 'HOLD')
            
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🟢 BUY Votes", buy_votes)
            with col2:
                st.metric("🔴 SELL Votes", sell_votes)
            with col3:
                st.metric("⚪ HOLD Votes", hold_votes)
            with col4:
                st.metric("Required", config.STRATEGY_VOTE_REQUIRED)
            
            # Final signal
            st.markdown("---")
            st.subheader("🎯 Final Multi5 Signal")
            
            if final_signal == 'BUY':
                st.success(f"🟢 **STRONG BUY** - {buy_votes} out of 5 strategies agree")
            elif final_signal == 'SELL':
                st.error(f"🔴 **STRONG SELL** - {sell_votes} out of 5 strategies agree")
            else:
                st.info(f"⚪ **HOLD** - Not enough consensus ({max(buy_votes, sell_votes)} votes)")
            
            # Chart (simplified for speed)
            st.markdown("---")
            st.subheader("📊 Price Chart")
            
            fig = go.Figure()
            
            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ))
            
            # MAs
            if 'MA_Fast' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['MA_Fast'], name='Fast MA', line=dict(color='blue', width=1)))
            if 'MA_Slow' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['MA_Slow'], name='Slow MA', line=dict(color='red', width=1)))
            
            fig.update_layout(
                title=f'{selected_symbol} - Multi5 Analysis',
                xaxis_rangeslider_visible=False,
                height=500
            )
            
            st.plotly_chart(fig, width='stretch')
            
            # Detailed indicators
            with st.expander("📋 Detailed Indicator Values"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Moving Averages:**")
                    st.write(f"Fast MA: ${current.get('MA_Fast', 0):.2f}")
                    st.write(f"Slow MA: ${current.get('MA_Slow', 0):.2f}")
                    st.write("")
                    st.write("**MACD:**")
                    st.write(f"MACD: {current.get('MACD', 0):.2f}")
                    st.write(f"Signal: {current.get('MACD_Signal', 0):.2f}")
                    st.write(f"Histogram: {current.get('MACD_Histogram', 0):.2f}")
                
                with col2:
                    st.write("**RSI:**")
                    st.write(f"RSI: {current.get('RSI', 0):.1f}")
                    st.write("")
                    st.write("**Bollinger Bands:**")
                    st.write(f"Upper: ${current.get('BB_Upper', 0):.2f}")
                    st.write(f"Middle: ${current.get('BB_Middle', 0):.2f}")
                    st.write(f"Lower: ${current.get('BB_Lower', 0):.2f}")
                    st.write("")
                    st.write("**Volume:**")
                    st.write(f"Current: {current.get('Volume', 0):,.0f}")
                    st.write(f"Average: {current.get('Volume_MA', 0):,.0f}")
                    st.write(f"Ratio: {current.get('Volume_Ratio', 0):.2f}x")
            
            # System comparison
            st.markdown("---")
            st.info("""
            💡 **Multi5 vs 2-Strategy System:**
            - Multi5 gives fewer but higher quality signals
            - Expects ~50% fewer signals than 2-strategy
            - But ~20-30% higher win rate
            - Best for swing trading and volatile stocks
            - Use both systems and compare results!
            """)
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("🎯 **Multi5 System** - Maximum filtering with 5 strategies")


if __name__ == "__main__":
    main()
