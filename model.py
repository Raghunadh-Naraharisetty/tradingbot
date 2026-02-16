"""
MODEL.PY - The "Brain" of Our Trading Bot
==========================================
This handles:
1. Fetching stock price data
2. Calculating Moving Averages
3. Generating BUY/SELL signals
4. Managing your portfolio (cash and positions)
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import config


class TradingModel:
    """
    This class is the core of our trading system.
    It makes all the trading decisions based on Moving Average Crossover.
    """
    
    def __init__(self):
        """
        Initialize the trading model.
        This sets up our starting conditions.
        """
        # PORTFOLIO TRACKING
        self.cash = config.INITIAL_CAPITAL  # Cash available to trade
        self.positions = {}  # Stocks we currently own
        # Example: {'AAPL': {'shares': 5, 'buy_price': 180.50}}
        
        # TRADING HISTORY
        self.trades = []  # List of all trades executed
        # Each trade: {'date', 'symbol', 'action', 'price', 'shares', 'value'}
        
        # MARKET DATA
        self.market_data = {}  # Stores price data for each symbol
        
        print(f"🚀 Trading Bot Initialized!")
        print(f"💰 Starting Capital: ${self.cash:.2f}")
        print(f"📈 Strategy: MULTI-STRATEGY SYSTEM")
        
        enabled = sum(1 for v in config.STRATEGIES_ENABLED.values() if v)
        print(f"   - {enabled} strategies enabled")
        print(f"   - Voting: {config.STRATEGY_VOTE_REQUIRED}")
        
        if config.STRATEGIES_ENABLED.get('ma_crossover'):
            print(f"   - MA: {config.MA_FAST_PERIOD}/{config.MA_SLOW_PERIOD}")
        if config.STRATEGIES_ENABLED.get('rsi'):
            print(f"   - RSI: {config.RSI_PERIOD} ({config.RSI_OVERSOLD}/{config.RSI_OVERBOUGHT})")
        if config.STRATEGIES_ENABLED.get('macd'):
            print(f"   - MACD: {config.MACD_FAST_PERIOD}/{config.MACD_SLOW_PERIOD}/{config.MACD_SIGNAL_PERIOD}")
        if config.STRATEGIES_ENABLED.get('bollinger'):
            print(f"   - Bollinger: {config.BOLLINGER_PERIOD} periods")
        if config.STRATEGIES_ENABLED.get('volume'):
            print(f"   - Volume: {config.VOLUME_SPIKE_THRESHOLD}x threshold")
        
        print("-" * 50)
    
    
    def fetch_market_data(self, symbol):
        """
        Download historical stock price data from Yahoo Finance.
        
        What data do we get?
        - Open: Opening price of the day
        - High: Highest price of the day
        - Low: Lowest price of the day
        - Close: Closing price (most important for our strategy)
        - Volume: Number of shares traded
        
        Args:
            symbol (str): Stock ticker (e.g., 'AAPL', 'MSFT')
        
        Returns:
            pandas.DataFrame: Historical price data
        """
        try:
            print(f"\n📊 Fetching data for {symbol}...")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Download historical data
            df = ticker.history(
                period=config.DATA_PERIOD,  # How far back (e.g., '6mo')
                interval=config.TIMEFRAME    # Time between data points (e.g., '1d')
            )
            
            # Check if we got data
            if df.empty:
                print(f"❌ No data found for {symbol}")
                return None
            
            # Store data in our dictionary
            self.market_data[symbol] = df
            
            print(f"✅ Downloaded {len(df)} data points for {symbol}")
            print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return None
    
    
    def calculate_moving_averages(self, symbol):
        """
        Calculate the Moving Averages for our strategy.
        
        WHAT IS A MOVING AVERAGE?
        ==========================
        - Average price over the last N periods
        - "Smooths out" price noise to see the trend
        
        Example (5-period MA):
        Prices: [100, 102, 101, 103, 105]
        MA = (100 + 102 + 101 + 103 + 105) / 5 = 102.2
        
        FAST vs SLOW MA:
        ================
        - Fast MA (short period): Reacts quickly to price changes
        - Slow MA (long period): Shows the overall trend
        
        THE CROSSOVER STRATEGY:
        =======================
        - When Fast MA crosses ABOVE Slow MA = BUY signal (Golden Cross)
          → Indicates upward momentum starting
        
        - When Fast MA crosses BELOW Slow MA = SELL signal (Death Cross)
          → Indicates downward momentum starting
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            pandas.DataFrame: Data with MA columns added
        """
        # Get the price data
        df = self.market_data.get(symbol)
        
        if df is None or df.empty:
            print(f"⚠️  No data available for {symbol}")
            return None
        
        # Calculate Fast Moving Average
        # .rolling() creates a moving window
        # .mean() calculates the average
        df['MA_Fast'] = df['Close'].rolling(window=config.MA_FAST_PERIOD).mean()
        
        # Calculate Slow Moving Average
        df['MA_Slow'] = df['Close'].rolling(window=config.MA_SLOW_PERIOD).mean()
        
        # Remove rows with NaN (not enough data for MA calculation)
        # First MA_SLOW_PERIOD-1 rows will be NaN
        df = df.dropna()
        
        # Update stored data
        self.market_data[symbol] = df
        
        print(f"✅ Moving Averages calculated for {symbol}")
        print(f"   Fast MA ({config.MA_FAST_PERIOD} periods): {df['MA_Fast'].iloc[-1]:.2f}")
        print(f"   Slow MA ({config.MA_SLOW_PERIOD} periods): {df['MA_Slow'].iloc[-1]:.2f}")
        
        return df
    
    
    def calculate_rsi(self, symbol):
        """
        Calculate RSI (Relative Strength Index).
        
        WHAT IS RSI?
        ============
        RSI measures momentum - whether a stock is overbought or oversold.
        
        Scale: 0 to 100
        - RSI < 30: Oversold (stock might bounce up soon)
        - RSI > 70: Overbought (stock might drop soon)
        - RSI 30-70: Normal range
        
        HOW IT WORKS:
        =============
        1. Calculate price changes (gains and losses)
        2. Find average gains over N periods
        3. Find average losses over N periods
        4. Calculate Relative Strength (RS) = Avg Gain / Avg Loss
        5. Convert to 0-100 scale: RSI = 100 - (100 / (1 + RS))
        
        Example:
        - If price went up 10 times and down 2 times
        - RS = 10/2 = 5 (strong upward momentum)
        - RSI = 100 - (100 / 6) = 83.3 (overbought!)
        
        WHY IT'S USEFUL:
        ================
        - Filters false MA crossover signals
        - Identifies momentum strength
        - Warns when trend might reverse
        - Confirms buy/sell decisions
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            pandas.DataFrame: Data with RSI column added
        """
        # Get the price data
        df = self.market_data.get(symbol)
        
        if df is None or df.empty:
            print(f"⚠️  No data available for {symbol}")
            return None
        
        # Step 1: Calculate price changes (delta)
        # Difference between today's close and yesterday's close
        delta = df['Close'].diff()
        
        # Step 2: Separate gains and losses
        # Gains: Keep positive changes, set negatives to 0
        gain = delta.where(delta > 0, 0)
        
        # Losses: Keep negative changes as positive numbers
        loss = -delta.where(delta < 0, 0)
        
        # Step 3: Calculate average gain and loss over RSI period
        # Using rolling window (moving average)
        avg_gain = gain.rolling(window=config.RSI_PERIOD).mean()
        avg_loss = loss.rolling(window=config.RSI_PERIOD).mean()
        
        # Step 4: Calculate Relative Strength (RS)
        # Avoid division by zero
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        
        # Step 5: Calculate RSI using the formula
        # RSI = 100 - (100 / (1 + RS))
        rsi = 100 - (100 / (1 + rs))
        
        # Add to dataframe
        df['RSI'] = rsi
        
        # Update stored data
        self.market_data[symbol] = df
        
        print(f"✅ RSI calculated for {symbol}")
        print(f"   Current RSI: {rsi.iloc[-1]:.2f}")
        
        # Interpret current RSI
        current_rsi = rsi.iloc[-1]
        if current_rsi < config.RSI_OVERSOLD:
            print(f"   📊 Status: OVERSOLD (RSI < {config.RSI_OVERSOLD}) - Potential buy opportunity")
        elif current_rsi > config.RSI_OVERBOUGHT:
            print(f"   📊 Status: OVERBOUGHT (RSI > {config.RSI_OVERBOUGHT}) - Potential sell opportunity")
        else:
            print(f"   📊 Status: NEUTRAL ({config.RSI_OVERSOLD} < RSI < {config.RSI_OVERBOUGHT})")
        
        return df
    
    
    def calculate_macd(self, symbol):
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        WHAT IS MACD?
        =============
        MACD is one of the most popular momentum indicators showing trend direction,
        strength, and potential reversals.
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            pandas.DataFrame: Data with MACD columns added
        """
        df = self.market_data.get(symbol)
        
        if df is None or df.empty:
            return None
        
        # Calculate EMAs
        ema_fast = df['Close'].ewm(span=config.MACD_FAST_PERIOD, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=config.MACD_SLOW_PERIOD, adjust=False).mean()
        
        # MACD Line = Fast EMA - Slow EMA
        macd_line = ema_fast - ema_slow
        
        # Signal Line = 9-period EMA of MACD Line
        signal_line = macd_line.ewm(span=config.MACD_SIGNAL_PERIOD, adjust=False).mean()
        
        # Histogram = MACD Line - Signal Line
        histogram = macd_line - signal_line
        
        # Add to dataframe
        df['MACD'] = macd_line
        df['MACD_Signal'] = signal_line
        df['MACD_Histogram'] = histogram
        
        self.market_data[symbol] = df
        
        print(f"✅ MACD calculated for {symbol}")
        print(f"   MACD: {macd_line.iloc[-1]:.2f}, Signal: {signal_line.iloc[-1]:.2f}")
        print(f"   Histogram: {histogram.iloc[-1]:.2f} {'🟢 BULLISH' if histogram.iloc[-1] > 0 else '🔴 BEARISH'}")
        
        return df
    
    
    def calculate_bollinger_bands(self, symbol):
        """
        Calculate Bollinger Bands for volatility analysis.
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            pandas.DataFrame: Data with Bollinger Band columns added
        """
        df = self.market_data.get(symbol)
        
        if df is None or df.empty:
            return None
        
        # Calculate Middle Band
        middle_band = df['Close'].rolling(window=config.BOLLINGER_PERIOD).mean()
        
        # Calculate Standard Deviation
        std_dev = df['Close'].rolling(window=config.BOLLINGER_PERIOD).std()
        
        # Calculate Upper and Lower Bands
        upper_band = middle_band + (std_dev * config.BOLLINGER_STD_DEV)
        lower_band = middle_band - (std_dev * config.BOLLINGER_STD_DEV)
        
        # Add to dataframe
        df['BB_Middle'] = middle_band
        df['BB_Upper'] = upper_band
        df['BB_Lower'] = lower_band
        df['BB_Width'] = (upper_band - lower_band) / middle_band
        df['BB_Position'] = (df['Close'] - lower_band) / (upper_band - lower_band)
        
        self.market_data[symbol] = df
        
        print(f"✅ Bollinger Bands calculated for {symbol}")
        position = df['BB_Position'].iloc[-1]
        status = "🟢 NEAR LOWER" if position < 0.2 else "🔴 NEAR UPPER" if position > 0.8 else "⚪ MIDDLE"
        print(f"   Position: {position:.1%} {status}")
        
        return df
    
    
    def calculate_volume_indicators(self, symbol):
        """
        Calculate Volume indicators for signal strength validation.
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            pandas.DataFrame: Data with Volume indicators added
        """
        df = self.market_data.get(symbol)
        
        if df is None or df.empty:
            return None
        
        # Calculate Volume Moving Average
        df['Volume_MA'] = df['Volume'].rolling(window=config.VOLUME_MA_PERIOD).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        df['Volume_Spike'] = df['Volume_Ratio'] > config.VOLUME_SPIKE_THRESHOLD
        
        self.market_data[symbol] = df
        
        print(f"✅ Volume indicators calculated for {symbol}")
        ratio = df['Volume_Ratio'].iloc[-1]
        status = "🔥 HIGH" if ratio >= config.VOLUME_SPIKE_THRESHOLD else "⚪ NORMAL" if ratio >= 1.0 else "⚠️  LOW"
        print(f"   Volume Ratio: {ratio:.2f}x {status}")
        
        return df
    
    
    def calculate_all_indicators(self, symbol):
        """
        Calculate ALL technical indicators for the multi-strategy system.
        
        This calculates indicators for ALL enabled strategies:
        1. Moving Averages (MA Crossover)
        2. RSI (Relative Strength Index)
        3. MACD (Moving Average Convergence Divergence)
        4. Bollinger Bands
        5. Volume indicators
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            pandas.DataFrame: Complete data with all indicators
        """
        df = self.market_data.get(symbol)
        
        if df is None or df.empty:
            print(f"⚠️  No data available for {symbol}")
            return None
        
        print(f"\n🔧 Calculating all indicators for {symbol}...")
        
        # Calculate each indicator if enabled
        if config.STRATEGIES_ENABLED.get('ma_crossover', True):
            df = self.calculate_moving_averages(symbol)
        
        if config.STRATEGIES_ENABLED.get('rsi', True):
            df = self.calculate_rsi(symbol)
        
        if config.STRATEGIES_ENABLED.get('macd', True):
            df = self.calculate_macd(symbol)
        
        if config.STRATEGIES_ENABLED.get('bollinger', True):
            df = self.calculate_bollinger_bands(symbol)
        
        if config.STRATEGIES_ENABLED.get('volume', True):
            df = self.calculate_volume_indicators(symbol)
        
        if df is None:
            return None
        
        # Remove rows with NaN values
        df = df.dropna()
        
        self.market_data[symbol] = df
        
        print(f"✅ All indicators calculated successfully")
        print(f"   Total data points: {len(df)}")
        
        return df
    
    
    def detect_crossover(self, symbol):
        """
        Detect if a Moving Average crossover happened.
        
        HOW WE DETECT CROSSOVER:
        ========================
        We compare the current and previous positions of the MAs:
        
        GOLDEN CROSS (BUY):
        Previous: Fast MA <= Slow MA
        Current:  Fast MA > Slow MA
        → Fast MA just crossed above! Buy signal!
        
        DEATH CROSS (SELL):
        Previous: Fast MA >= Slow MA
        Current:  Fast MA < Slow MA
        → Fast MA just crossed below! Sell signal!
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: 'BUY', 'SELL', or 'HOLD'
        """
        df = self.market_data.get(symbol)
        
        if df is None or len(df) < 2:
            return 'HOLD'  # Not enough data
        
        # Get last two rows to detect crossover
        current = df.iloc[-1]  # Most recent data point
        previous = df.iloc[-2]  # Previous data point
        
        # Extract Moving Average values
        ma_fast_current = current['MA_Fast']
        ma_slow_current = current['MA_Slow']
        ma_fast_previous = previous['MA_Fast']
        ma_slow_previous = previous['MA_Slow']
        
        # Current price (for logging)
        current_price = current['Close']
        
        # GOLDEN CROSS DETECTION (BUY Signal)
        # Fast MA crosses from below to above Slow MA
        golden_cross = (ma_fast_previous <= ma_slow_previous) and \
                      (ma_fast_current > ma_slow_current)
        
        if golden_cross:
            print(f"\n🟢 GOLDEN CROSS DETECTED for {symbol}!")
            print(f"   Price: ${current_price:.2f}")
            print(f"   Fast MA crossed above Slow MA")
            print(f"   → BULLISH signal (uptrend starting)")
            return 'BUY'
        
        # DEATH CROSS DETECTION (SELL Signal)
        # Fast MA crosses from above to below Slow MA
        death_cross = (ma_fast_previous >= ma_slow_previous) and \
                     (ma_fast_current < ma_slow_current)
        
        if death_cross:
            print(f"\n🔴 DEATH CROSS DETECTED for {symbol}!")
            print(f"   Price: ${current_price:.2f}")
            print(f"   Fast MA crossed below Slow MA")
            print(f"   → BEARISH signal (downtrend starting)")
            return 'SELL'
        
        # NO CROSSOVER
        # Check current relationship for status
        if ma_fast_current > ma_slow_current:
            status = "uptrend"
        else:
            status = "downtrend"
        
        print(f"\n⚪ NO CROSSOVER for {symbol}")
        print(f"   Price: ${current_price:.2f}")
        print(f"   Status: {status}")
        return 'HOLD'
    
    
    def generate_hybrid_signal(self, symbol):
        """
        Generate trading signal using HYBRID strategy.
        
        HYBRID STRATEGY LOGIC:
        ======================
        Combines TWO indicators for better accuracy:
        
        1. Moving Average Crossover (Trend Direction)
           - Identifies when trends start/end
        
        2. RSI Confirmation (Momentum Filter)
           - Filters out weak signals
           - Avoids buying overbought stocks
           - Avoids selling oversold stocks
        
        BUY SIGNAL (All conditions must be met):
        ✅ Golden Cross (Fast MA crosses above Slow MA)
        ✅ RSI > 30 (not oversold, has upward momentum)
        ✅ RSI < 70 (not overbought yet)
        
        SELL SIGNAL (All conditions must be met):
        ✅ Death Cross (Fast MA crosses below Slow MA)
        ✅ RSI < 70 (not overbought anymore)
        ✅ RSI > 30 (not oversold yet)
        
        WHY THIS WORKS BETTER:
        ======================
        - Filters ~30-40% of false MA signals
        - Only trades when both trend AND momentum align
        - Avoids buying at market tops (overbought)
        - Avoids selling at market bottoms (oversold)
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: 'BUY', 'SELL', or 'HOLD'
        """
        df = self.market_data.get(symbol)
        
        if df is None or len(df) < 2:
            return 'HOLD'
        
        # Get current data
        current = df.iloc[-1]
        current_rsi = current['RSI']
        
        # STEP 1: Check for MA Crossover
        ma_signal = self.detect_crossover(symbol)
        
        # STEP 2: Apply RSI Filter
        
        if ma_signal == 'BUY':
            # Check RSI confirmation for BUY
            rsi_confirms = (current_rsi > config.RSI_OVERSOLD and 
                           current_rsi < config.RSI_OVERBOUGHT)
            
            if rsi_confirms:
                print(f"✅ RSI CONFIRMS BUY: {current_rsi:.2f} is in healthy range")
                print(f"   → STRONG BUY signal (both indicators align)")
                return 'BUY'
            else:
                if current_rsi >= config.RSI_OVERBOUGHT:
                    print(f"⚠️  RSI REJECTS BUY: {current_rsi:.2f} is OVERBOUGHT")
                    print(f"   → Too risky to buy at this level")
                else:
                    print(f"⚠️  RSI REJECTS BUY: {current_rsi:.2f} is too weak")
                    print(f"   → Waiting for stronger momentum")
                return 'HOLD'
        
        elif ma_signal == 'SELL':
            # Check RSI confirmation for SELL
            rsi_confirms = (current_rsi < config.RSI_OVERBOUGHT and 
                           current_rsi > config.RSI_OVERSOLD)
            
            if rsi_confirms:
                print(f"✅ RSI CONFIRMS SELL: {current_rsi:.2f} shows weakness")
                print(f"   → STRONG SELL signal (both indicators align)")
                return 'SELL'
            else:
                if current_rsi <= config.RSI_OVERSOLD:
                    print(f"⚠️  RSI REJECTS SELL: {current_rsi:.2f} is OVERSOLD")
                    print(f"   → Too risky to sell at this level (might bounce)")
                else:
                    print(f"⚠️  RSI REJECTS SELL: {current_rsi:.2f} still strong")
                    print(f"   → Waiting for clearer weakness")
                return 'HOLD'
        
        # No crossover signal
        return 'HOLD'
    
    
    def check_macd_signal(self, symbol):
        """Generate signal from MACD strategy."""
        if not config.STRATEGIES_ENABLED.get('macd', False):
            return 'HOLD'
        
        df = self.market_data.get(symbol)
        if df is None or 'MACD' not in df.columns or len(df) < 2:
            return 'HOLD'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Bullish crossover
        if (previous['MACD'] <= previous['MACD_Signal'] and 
            current['MACD'] > current['MACD_Signal']):
            print(f"   📊 MACD: BUY (bullish crossover)")
            return 'BUY'
        
        # Bearish crossover
        if (previous['MACD'] >= previous['MACD_Signal'] and 
            current['MACD'] < current['MACD_Signal']):
            print(f"   📊 MACD: SELL (bearish crossover)")
            return 'SELL'
        
        return 'HOLD'
    
    
    def check_bollinger_signal(self, symbol):
        """Generate signal from Bollinger Bands."""
        if not config.STRATEGIES_ENABLED.get('bollinger', False):
            return 'HOLD'
        
        df = self.market_data.get(symbol)
        if df is None or 'BB_Position' not in df.columns:
            return 'HOLD'
        
        position = df['BB_Position'].iloc[-1]
        
        # Near lower band
        if position <= config.BOLLINGER_LOWER_THRESHOLD:
            print(f"   📊 Bollinger: BUY (near lower band)")
            return 'BUY'
        
        # Near upper band
        if position >= (1.0 - config.BOLLINGER_UPPER_THRESHOLD):
            print(f"   📊 Bollinger: SELL (near upper band)")
            return 'SELL'
        
        return 'HOLD'
    
    
    def check_volume_confirmation(self, symbol):
        """Check volume confirmation."""
        if not config.STRATEGIES_ENABLED.get('volume', False):
            return True
        
        df = self.market_data.get(symbol)
        if df is None or 'Volume_Spike' not in df.columns:
            return True
        
        has_volume = df['Volume_Spike'].iloc[-1]
        status = "✅ CONFIRMED" if has_volume else "⚠️  WEAK"
        print(f"   📊 Volume: {status}")
        return has_volume
    
    
    def check_rsi_filter(self, signal, symbol):
        """Use RSI as filter."""
        if not config.STRATEGIES_ENABLED.get('rsi', False):
            return True
        
        df = self.market_data.get(symbol)
        if df is None or 'RSI' not in df.columns:
            return True
        
        rsi = df['RSI'].iloc[-1]
        
        if signal == 'BUY' and rsi < config.RSI_OVERBOUGHT:
            print(f"   📊 RSI: ✅ PASS ({rsi:.1f})")
            return True
        elif signal == 'SELL' and rsi > config.RSI_OVERSOLD:
            print(f"   📊 RSI: ✅ PASS ({rsi:.1f})")
            return True
        else:
            print(f"   📊 RSI: ❌ REJECT ({rsi:.1f})")
            return False
    
    
    def generate_multi_strategy_signal(self, symbol):
        """
        Generate signal using MULTIPLE STRATEGIES with voting.
        
        Professional multi-strategy approach with consensus voting!
        """
        df = self.market_data.get(symbol)
        if df is None or len(df) < 2:
            return 'HOLD'
        
        print(f"\n🎯 MULTI-STRATEGY ANALYSIS for {symbol}:")
        print("=" * 60)
        
        # Collect votes
        votes = {'BUY': 0, 'SELL': 0}
        
        # MA Crossover
        if config.STRATEGIES_ENABLED.get('ma_crossover', True):
            ma_signal = self.detect_crossover(symbol)
            if ma_signal != 'HOLD':
                votes[ma_signal] += 1
        
        # MACD
        if config.STRATEGIES_ENABLED.get('macd', True):
            macd_signal = self.check_macd_signal(symbol)
            if macd_signal != 'HOLD':
                votes[macd_signal] += 1
        
        # Bollinger
        if config.STRATEGIES_ENABLED.get('bollinger', True):
            bb_signal = self.check_bollinger_signal(symbol)
            if bb_signal != 'HOLD':
                votes[bb_signal] += 1
        
        # Volume check
        volume_ok = self.check_volume_confirmation(symbol)
        
        # Count enabled
        enabled = sum(1 for v in config.STRATEGIES_ENABLED.values() if v)
        vote_req = config.STRATEGY_VOTE_REQUIRED
        
        print(f"\n📊 VOTES: BUY={votes['BUY']}, SELL={votes['SELL']}, Enabled={enabled}")
        
        # Determine signal
        signal = 'HOLD'
        if vote_req == 'all':
            if votes['BUY'] == enabled:
                signal = 'BUY'
            elif votes['SELL'] == enabled:
                signal = 'SELL'
        elif vote_req == 'majority':
            required = (enabled // 2) + 1
            if votes['BUY'] >= required:
                signal = 'BUY'
            elif votes['SELL'] >= required:
                signal = 'SELL'
        elif vote_req == 'any':
            if votes['BUY'] > 0:
                signal = 'BUY'
            elif votes['SELL'] > 0:
                signal = 'SELL'
        
        # RSI filter
        if signal != 'HOLD' and not self.check_rsi_filter(signal, symbol):
            signal = 'HOLD'
        
        # Volume filter
        if signal != 'HOLD' and config.VOLUME_REQUIRED and not volume_ok:
            print(f"⚠️  Signal REJECTED: Volume required but not present")
            signal = 'HOLD'
        
        # Output
        print(f"\n{'='*60}")
        if signal == 'BUY':
            print(f"✅ FINAL: 🟢 BUY ({votes['BUY']}/{enabled} strategies)")
        elif signal == 'SELL':
            print(f"✅ FINAL: 🔴 SELL ({votes['SELL']}/{enabled} strategies)")
        else:
            print(f"⚪ FINAL: HOLD (not enough agreement)")
        print(f"{'='*60}\n")
        
        return signal
        """
        Detect if a Moving Average crossover happened.
        
        HOW WE DETECT CROSSOVER:
        ========================
        We compare the current and previous positions of the MAs:
        
        GOLDEN CROSS (BUY):
        Previous: Fast MA <= Slow MA
        Current:  Fast MA > Slow MA
        → Fast MA just crossed above! Buy signal!
        
        DEATH CROSS (SELL):
        Previous: Fast MA >= Slow MA
        Current:  Fast MA < Slow MA
        → Fast MA just crossed below! Sell signal!
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: 'BUY', 'SELL', or 'HOLD'
        """
        df = self.market_data.get(symbol)
        
        if df is None or len(df) < 2:
            return 'HOLD'  # Not enough data
        
        # Get last two rows to detect crossover
        current = df.iloc[-1]  # Most recent data point
        previous = df.iloc[-2]  # Previous data point
        
        # Extract Moving Average values
        ma_fast_current = current['MA_Fast']
        ma_slow_current = current['MA_Slow']
        ma_fast_previous = previous['MA_Fast']
        ma_slow_previous = previous['MA_Slow']
        
        # Current price (for logging)
        current_price = current['Close']
        
        # GOLDEN CROSS DETECTION (BUY Signal)
        # Fast MA crosses from below to above Slow MA
        golden_cross = (ma_fast_previous <= ma_slow_previous) and \
                      (ma_fast_current > ma_slow_current)
        
        if golden_cross:
            print(f"\n🟢 GOLDEN CROSS DETECTED for {symbol}!")
            print(f"   Price: ${current_price:.2f}")
            print(f"   Fast MA crossed above Slow MA")
            print(f"   → BULLISH signal (uptrend starting)")
            return 'BUY'
        
        # DEATH CROSS DETECTION (SELL Signal)
        # Fast MA crosses from above to below Slow MA
        death_cross = (ma_fast_previous >= ma_slow_previous) and \
                     (ma_fast_current < ma_slow_current)
        
        if death_cross:
            print(f"\n🔴 DEATH CROSS DETECTED for {symbol}!")
            print(f"   Price: ${current_price:.2f}")
            print(f"   Fast MA crossed below Slow MA")
            print(f"   → BEARISH signal (downtrend starting)")
            return 'SELL'
        
        # NO CROSSOVER
        # Check current relationship for status
        if ma_fast_current > ma_slow_current:
            status = "uptrend"
        else:
            status = "downtrend"
        
        print(f"\n⚪ NO CROSSOVER for {symbol}")
        print(f"   Price: ${current_price:.2f}")
        print(f"   Status: {status}")
        return 'HOLD'
    
    
    def calculate_position_size(self, symbol, current_price):
        """
        Calculate how many shares to buy based on available cash.
        
        POSITION SIZING:
        ================
        - We limit each trade to MAX_POSITION_SIZE of our capital
        - This is risk management: don't bet everything on one trade!
        
        Example:
        - Capital: $100
        - Max position size: 30%
        - Max to invest: $30
        - Stock price: $150
        - Shares to buy: $30 / $150 = 0.2 shares
        - Actual: Buy 0 shares (can't buy fractional)
        
        Args:
            symbol (str): Stock ticker
            current_price (float): Current stock price
        
        Returns:
            int: Number of shares to buy (whole shares only)
        """
        # Maximum amount we can invest in this trade
        max_investment = self.cash * config.MAX_POSITION_SIZE
        
        # Calculate shares (rounded down to whole number)
        shares = int(max_investment / current_price)
        
        # Make sure we have enough cash
        total_cost = shares * current_price
        
        if total_cost > self.cash:
            shares = int(self.cash / current_price)
        
        return shares
    
    
    def execute_buy(self, symbol, current_price):
        """
        Execute a BUY order.
        
        WHAT HAPPENS WHEN WE BUY:
        =========================
        1. Check if we have enough cash
        2. Calculate how many shares to buy
        3. Deduct cash from account
        4. Add shares to positions
        5. Record the trade
        
        Args:
            symbol (str): Stock ticker
            current_price (float): Current stock price
        
        Returns:
            bool: True if trade executed, False otherwise
        """
        # Check if we already own this stock
        if symbol in self.positions:
            print(f"⚠️  Already holding {symbol}. Skipping buy.")
            return False
        
        # Calculate shares to buy
        shares = self.calculate_position_size(symbol, current_price)
        
        if shares == 0:
            print(f"⚠️  Not enough cash to buy {symbol} at ${current_price:.2f}")
            print(f"   Available cash: ${self.cash:.2f}")
            return False
        
        # Calculate total cost
        total_cost = shares * current_price
        
        # Execute trade
        self.cash -= total_cost
        self.positions[symbol] = {
            'shares': shares,
            'buy_price': current_price,
            'buy_date': datetime.now()
        }
        
        # Record trade
        trade = {
            'date': datetime.now(),
            'symbol': symbol,
            'action': 'BUY',
            'price': current_price,
            'shares': shares,
            'value': total_cost,
            'cash_after': self.cash
        }
        self.trades.append(trade)
        
        print(f"\n✅ BUY ORDER EXECUTED")
        print(f"   Symbol: {symbol}")
        print(f"   Shares: {shares}")
        print(f"   Price: ${current_price:.2f}")
        print(f"   Total Cost: ${total_cost:.2f}")
        print(f"   Cash Remaining: ${self.cash:.2f}")
        
        return True
    
    
    def execute_sell(self, symbol, current_price):
        """
        Execute a SELL order.
        
        WHAT HAPPENS WHEN WE SELL:
        ==========================
        1. Check if we own the stock
        2. Sell all shares
        3. Add proceeds to cash
        4. Calculate profit/loss
        5. Remove from positions
        6. Record the trade
        
        Args:
            symbol (str): Stock ticker
            current_price (float): Current stock price
        
        Returns:
            bool: True if trade executed, False otherwise
        """
        # Check if we own this stock
        if symbol not in self.positions:
            print(f"⚠️  Don't own {symbol}. Can't sell.")
            return False
        
        # Get position details
        position = self.positions[symbol]
        shares = position['shares']
        buy_price = position['buy_price']
        
        # Calculate proceeds
        total_proceeds = shares * current_price
        
        # Calculate profit/loss
        total_cost = shares * buy_price
        profit = total_proceeds - total_cost
        profit_percent = (profit / total_cost) * 100
        
        # Execute trade
        self.cash += total_proceeds
        del self.positions[symbol]
        
        # Record trade
        trade = {
            'date': datetime.now(),
            'symbol': symbol,
            'action': 'SELL',
            'price': current_price,
            'shares': shares,
            'value': total_proceeds,
            'profit': profit,
            'profit_percent': profit_percent,
            'cash_after': self.cash
        }
        self.trades.append(trade)
        
        # Print results
        profit_emoji = "📈" if profit > 0 else "📉"
        print(f"\n✅ SELL ORDER EXECUTED {profit_emoji}")
        print(f"   Symbol: {symbol}")
        print(f"   Shares: {shares}")
        print(f"   Buy Price: ${buy_price:.2f}")
        print(f"   Sell Price: ${current_price:.2f}")
        print(f"   Total Proceeds: ${total_proceeds:.2f}")
        print(f"   Profit/Loss: ${profit:.2f} ({profit_percent:+.2f}%)")
        print(f"   Cash After: ${self.cash:.2f}")
        
        return True
    
    
    def get_portfolio_value(self):
        """
        Calculate total portfolio value.
        
        Portfolio Value = Cash + (Value of all positions)
        
        Returns:
            float: Total portfolio value
        """
        total = self.cash
        
        for symbol, position in self.positions.items():
            df = self.market_data.get(symbol)
            if df is not None and not df.empty:
                current_price = df['Close'].iloc[-1]
                position_value = position['shares'] * current_price
                total += position_value
        
        return total
    
    
    def check_stop_loss_take_profit(self, symbol):
        """
        Check if we need to exit a position due to stop-loss or take-profit.
        
        RISK MANAGEMENT:
        ================
        Stop Loss: Exit if price drops X% below buy price
        → Limits your losses
        
        Take Profit: Exit if price rises X% above buy price  
        → Locks in your gains
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: 'SELL' if triggered, 'HOLD' otherwise
        """
        if symbol not in self.positions:
            return 'HOLD'
        
        # Get current price
        df = self.market_data.get(symbol)
        if df is None or df.empty:
            return 'HOLD'
        
        current_price = df['Close'].iloc[-1]
        buy_price = self.positions[symbol]['buy_price']
        
        # Calculate price change
        price_change_percent = ((current_price - buy_price) / buy_price) * 100
        
        # Check Stop Loss
        if price_change_percent <= -config.STOP_LOSS_PERCENT * 100:
            print(f"\n🛑 STOP LOSS TRIGGERED for {symbol}!")
            print(f"   Buy Price: ${buy_price:.2f}")
            print(f"   Current Price: ${current_price:.2f}")
            print(f"   Loss: {price_change_percent:.2f}%")
            return 'SELL'
        
        # Check Take Profit
        if price_change_percent >= config.TAKE_PROFIT_PERCENT * 100:
            print(f"\n🎯 TAKE PROFIT TRIGGERED for {symbol}!")
            print(f"   Buy Price: ${buy_price:.2f}")
            print(f"   Current Price: ${current_price:.2f}")
            print(f"   Gain: {price_change_percent:.2f}%")
            return 'SELL'
        
        return 'HOLD'
