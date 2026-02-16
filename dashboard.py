"""
DASHBOARD.PY - Interactive Web Dashboard
=========================================
Beautiful, real-time trading dashboard with charts and metrics.

Usage:
    streamlit run dashboard.py

Then open browser to: http://localhost:8501
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import config
from model import TradingModel
from datetime import datetime
import time


# Page configuration
st.set_page_config(
    page_title="Multi-Strategy Trading Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .trade-buy {
        color: #00ff00;
        font-weight: bold;
    }
    .trade-sell {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(symbol):
    """Load and calculate indicators for a symbol."""
    model = TradingModel()
    model.fetch_market_data(symbol)
    model.calculate_all_indicators(symbol)
    return model


def create_price_chart(df, symbol, trades=None):
    """Create interactive price chart with indicators."""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=('Price & Moving Averages', 'RSI', 'MACD', 'Volume')
    )
    
    # Price and MAs
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ), row=1, col=1)
    
    if 'MA_Fast' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA_Fast'],
            name=f'Fast MA ({config.MA_FAST_PERIOD})',
            line=dict(color='blue', width=1)
        ), row=1, col=1)
    
    if 'MA_Slow' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA_Slow'],
            name=f'Slow MA ({config.MA_SLOW_PERIOD})',
            line=dict(color='red', width=1)
        ), row=1, col=1)
    
    # Bollinger Bands
    if 'BB_Upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Upper'],
            name='BB Upper',
            line=dict(color='gray', width=1, dash='dash'),
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Lower'],
            name='BB Lower',
            line=dict(color='gray', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(128,128,128,0.1)',
            showlegend=False
        ), row=1, col=1)
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['RSI'],
            name='RSI',
            line=dict(color='purple', width=2)
        ), row=2, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, opacity=0.5)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1, opacity=0.5)
    
    # MACD
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD'],
            name='MACD',
            line=dict(color='blue', width=1)
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD_Signal'],
            name='Signal',
            line=dict(color='red', width=1)
        ), row=3, col=1)
        
        if 'MACD_Histogram' in df.columns:
            colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
            fig.add_trace(go.Bar(
                x=df.index, y=df['MACD_Histogram'],
                name='Histogram',
                marker_color=colors,
                showlegend=False
            ), row=3, col=1)
    
    # Volume
    colors = ['green' if close >= open else 'red' 
              for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        name='Volume',
        marker_color=colors,
        showlegend=False
    ), row=4, col=1)
    
    if 'Volume_MA' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Volume_MA'],
            name='Vol MA',
            line=dict(color='orange', width=1)
        ), row=4, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} - Multi-Strategy Analysis',
        xaxis_rangeslider_visible=False,
        height=900,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=4, col=1)
    
    return fig


def display_strategy_votes(model, symbol):
    """Display voting results from each strategy."""
    df = model.market_data.get(symbol)
    if df is None or len(df) < 2:
        return
    
    st.subheader("🎯 Strategy Votes")
    
    votes = {}
    
    # Check each strategy
    if config.STRATEGIES_ENABLED.get('ma_crossover'):
        signal = model.detect_crossover(symbol)
        votes['MA Crossover'] = signal
    
    if config.STRATEGIES_ENABLED.get('macd'):
        signal = model.check_macd_signal(symbol)
        votes['MACD'] = signal
    
    if config.STRATEGIES_ENABLED.get('bollinger'):
        signal = model.check_bollinger_signal(symbol)
        votes['Bollinger'] = signal
    
    # Display votes in columns
    cols = st.columns(len(votes))
    for col, (strategy, vote) in zip(cols, votes.items()):
        with col:
            if vote == 'BUY':
                st.metric(strategy, "BUY", delta="Bullish", delta_color="normal")
            elif vote == 'SELL':
                st.metric(strategy, "SELL", delta="Bearish", delta_color="inverse")
            else:
                st.metric(strategy, "HOLD", delta="Neutral", delta_color="off")


def main():
    """Main dashboard function."""
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # Symbol selection
    symbol_options = config.SYMBOLS if hasattr(config, 'SYMBOLS') else ['AAPL']
    selected_symbol = st.sidebar.selectbox(
        "Select Stock",
        symbol_options,
        index=0
    )
    
    # Timeframe selection
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ['1d', '1h', '15m', '5m'],
        index=0
    )
    
    # Period selection
    period = st.sidebar.selectbox(
        "Historical Period",
        ['1mo', '3mo', '6mo', '1y'],
        index=2
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
    
    # Main content
    st.title("📈 Trading Dashboard By Aghna")
    st.markdown(f"**Developed by Raghu with Claude** | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    with st.spinner(f'Loading data for {selected_symbol}...'):
        try:
            model = load_data(selected_symbol)
            df = model.market_data.get(selected_symbol)
            
            if df is None or df.empty:
                st.error(f"❌ Could not load data for {selected_symbol}")
                return
            
            # Key metrics
            current = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else current
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                price_change = current['Close'] - previous['Close']
                price_change_pct = (price_change / previous['Close']) * 100
                st.metric(
                    "Current Price",
                    f"${current['Close']:.2f}",
                    f"{price_change_pct:+.2f}%"
                )
            
            with col2:
                if 'RSI' in df.columns:
                    rsi = current['RSI']
                    rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                    st.metric("RSI", f"{rsi:.1f}", rsi_status)
            
            with col3:
                if 'MACD_Histogram' in df.columns:
                    hist = current['MACD_Histogram']
                    macd_status = "Bullish" if hist > 0 else "Bearish"
                    st.metric("MACD", f"{hist:.2f}", macd_status)
            
            with col4:
                if 'Volume_Ratio' in df.columns:
                    vol_ratio = current['Volume_Ratio']
                    vol_status = "High" if vol_ratio > 1.5 else "Normal"
                    st.metric("Volume Ratio", f"{vol_ratio:.2f}x", vol_status)
            
            with col5:
                if 'BB_Position' in df.columns:
                    bb_pos = current['BB_Position']
                    bb_status = "Lower" if bb_pos < 0.3 else "Upper" if bb_pos > 0.7 else "Middle"
                    st.metric("BB Position", f"{bb_pos:.1%}", bb_status)
            
            # Strategy votes
            display_strategy_votes(model, selected_symbol)
            
            # Final signal
            st.subheader("🎯 Final Signal")
            signal = model.generate_multi_strategy_signal(selected_symbol)
            
            if signal == 'BUY':
                st.success("🟢 **BUY SIGNAL** - Multiple strategies agree on bullish momentum")
            elif signal == 'SELL':
                st.error("🔴 **SELL SIGNAL** - Multiple strategies agree on bearish momentum")
            else:
                st.info("⚪ **HOLD** - Not enough strategy consensus")
            
            # Chart
            st.subheader("📊 Technical Analysis")
            fig = create_price_chart(df, selected_symbol)
            st.plotly_chart(fig, width='stretch')
            
            # Indicator details
            with st.expander("📋 Detailed Indicator Values"):
                indicators_df = pd.DataFrame({
                    'Indicator': ['Price', 'Fast MA', 'Slow MA', 'RSI', 'MACD', 'MACD Signal', 
                                 'BB Upper', 'BB Lower', 'Volume', 'Volume MA'],
                    'Value': [
                        f"${current['Close']:.2f}",
                        f"${current.get('MA_Fast', 0):.2f}",
                        f"${current.get('MA_Slow', 0):.2f}",
                        f"{current.get('RSI', 0):.2f}",
                        f"{current.get('MACD', 0):.2f}",
                        f"{current.get('MACD_Signal', 0):.2f}",
                        f"${current.get('BB_Upper', 0):.2f}",
                        f"${current.get('BB_Lower', 0):.2f}",
                        f"{current.get('Volume', 0):,.0f}",
                        f"{current.get('Volume_MA', 0):,.0f}"
                    ]
                })
                st.dataframe(indicators_df, hide_index=True, width='stretch')
            
            # Strategy configuration
            with st.expander("⚙️ Strategy Configuration"):
                st.json({
                    'Enabled Strategies': {k: v for k, v in config.STRATEGIES_ENABLED.items()},
                    'Vote Requirement': config.STRATEGY_VOTE_REQUIRED,
                    'Parameters': {
                        'MA Fast': config.MA_FAST_PERIOD,
                        'MA Slow': config.MA_SLOW_PERIOD,
                        'RSI Period': config.RSI_PERIOD,
                        'MACD': f"{config.MACD_FAST_PERIOD}/{config.MACD_SLOW_PERIOD}/{config.MACD_SIGNAL_PERIOD}",
                        'Bollinger': f"{config.BOLLINGER_PERIOD} periods, {config.BOLLINGER_STD_DEV} std dev"
                    }
                })
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **Tip:** Enable auto-refresh in sidebar for real-time monitoring")


if __name__ == "__main__":
    main()
