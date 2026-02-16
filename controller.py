"""
CONTROLLER.PY - The "Conductor" of Our Trading Bot
===================================================
This orchestrates everything:
1. Coordinates Model and View
2. Runs the trading logic
3. Makes decisions when to buy/sell
4. Controls the flow of the program
"""

import time
from datetime import datetime
import config
from model import TradingModel
from view import TradingView


class TradingController:
    """
    The controller manages the entire trading bot workflow.
    It tells the Model what to do and the View what to display.
    """
    
    def __init__(self):
        """
        Initialize the controller with Model and View.
        """
        self.model = TradingModel()
        self.view = TradingView()
    
    
    def run_backtest(self):
        """
        Run a backtest on historical data.
        
        WHAT IS BACKTESTING?
        ====================
        Testing your strategy on past data to see how it would have performed.
        
        PROCESS:
        1. Download historical data
        2. Calculate indicators
        3. Go through each day
        4. Check for signals
        5. Execute trades
        6. Track performance
        
        This helps you understand if your strategy works before risking real money!
        """
        # Display welcome and strategy info
        self.view.display_welcome()
        self.view.display_strategy_explanation()
        
        print("\n🔄 STARTING BACKTEST...")
        print("="*60)
        
        # Process each symbol
        for symbol in config.SYMBOLS:
            print(f"\n📈 Processing {symbol}...")
            print("-"*60)
            
            # Step 1: Fetch market data
            df = self.model.fetch_market_data(symbol)
            
            if df is None or df.empty:
                print(f"❌ Skipping {symbol}: No data available")
                continue
            
            # Step 2: Calculate ALL Indicators (MA + RSI)
            df = self.model.calculate_all_indicators(symbol)
            
            if df is None:
                print(f"❌ Skipping {symbol}: Error calculating indicators")
                continue
            
            # Display current market data
            self.view.display_market_data_summary(symbol, df)
            
            # Step 3: Simulate trading through historical data
            print(f"\n🔄 Simulating trades for {symbol}...")
            self.simulate_trading(symbol, df)
        
        # Display final results
        print("\n" + "="*60)
        print("✅ BACKTEST COMPLETE!")
        print("="*60)
        
        self.view.display_portfolio_status(self.model)
        self.view.display_trade_history(self.model.trades)
        self.view.display_performance_metrics(self.model)
        
        # Generate charts for each symbol
        print("\n📊 Generating charts...")
        for symbol in config.SYMBOLS:
            df = self.model.market_data.get(symbol)
            if df is not None:
                self.view.plot_chart(symbol, df, self.model.trades)
        
        self.view.display_footer()
    
    
    def simulate_trading(self, symbol, df):
        """
        Simulate trading day-by-day through historical data.
        
        This goes through the data point by point, as if we were
        trading in real-time, checking for signals and executing trades.
        
        Args:
            symbol (str): Stock ticker
            df (DataFrame): Market data with indicators
        """
        # We need at least 2 data points to detect crossover
        if len(df) < 2:
            print(f"⚠️  Not enough data to trade {symbol}")
            return
        
        # Iterate through the data day by day
        # Start from the second day (we need previous day to detect crossover)
        for i in range(1, len(df)):
            # Get data up to current point (simulating real-time)
            current_df = df.iloc[:i+1]
            
            # Update model with current data
            self.model.market_data[symbol] = current_df
            
            # Get current price
            current_price = current_df['Close'].iloc[-1]
            current_date = current_df.index[-1]
            
            # Check for risk management signals first (stop-loss/take-profit)
            risk_signal = self.model.check_stop_loss_take_profit(symbol)
            
            if risk_signal == 'SELL':
                self.model.execute_sell(symbol, current_price)
                continue
            
            # Check for crossover signals with multi-strategy consensus
            signal = self.model.generate_multi_strategy_signal(symbol)
            
            # Execute trades based on signal
            if signal == 'BUY':
                self.model.execute_buy(symbol, current_price)
            
            elif signal == 'SELL':
                self.model.execute_sell(symbol, current_price)
    
    
    def run_live_monitoring(self):
        """
        Run live monitoring mode (for real-time trading).
        
        WARNING: This would connect to real markets!
        For now, we'll just show how it would work.
        
        LIVE TRADING WORKFLOW:
        1. Continuously fetch latest data
        2. Calculate indicators
        3. Check for signals
        4. Execute trades automatically
        5. Monitor positions
        6. Repeat every X minutes
        """
        print("\n⚠️  LIVE TRADING MODE")
        print("="*60)
        print("This feature would connect to real markets.")
        print("For learning purposes, please use backtest mode.")
        print("="*60)
        
        # Example structure for live trading (not implemented)
        """
        while True:
            for symbol in config.SYMBOLS:
                # Fetch latest data
                self.model.fetch_market_data(symbol)
                
                # Calculate indicators
                self.model.calculate_moving_averages(symbol)
                
                # Check signals
                signal = self.model.detect_crossover(symbol)
                
                # Execute trades
                if signal == 'BUY':
                    self.model.execute_buy(symbol, current_price)
                elif signal == 'SELL':
                    self.model.execute_sell(symbol, current_price)
                
                # Check risk management
                risk_signal = self.model.check_stop_loss_take_profit(symbol)
                if risk_signal == 'SELL':
                    self.model.execute_sell(symbol, current_price)
            
            # Display status
            self.view.display_portfolio_status(self.model)
            
            # Wait before next check
            time.sleep(300)  # Check every 5 minutes
        """
    
    
    def run_single_analysis(self, symbol):
        """
        Analyze a single stock and show current signal.
        
        This is useful for checking what the strategy says
        about a stock right now without running full backtest.
        
        Args:
            symbol (str): Stock ticker to analyze
        """
        self.view.display_welcome()
        
        print(f"\n🔍 ANALYZING {symbol}...")
        print("="*60)
        
        # Fetch and analyze
        df = self.model.fetch_market_data(symbol)
        
        if df is None:
            print(f"❌ Could not fetch data for {symbol}")
            return
        
        df = self.model.calculate_all_indicators(symbol)
        
        if df is None:
            print(f"❌ Could not calculate indicators for {symbol}")
            return
        
        # Show market data
        self.view.display_market_data_summary(symbol, df)
        
        # Check current multi-strategy signal
        signal = self.model.generate_multi_strategy_signal(symbol)
        
        current_price = df['Close'].iloc[-1]
        
        print(f"\n📊 CURRENT SIGNAL: {signal}")
        
        if signal == 'BUY':
            shares = self.model.calculate_position_size(symbol, current_price)
            investment = shares * current_price
            print(f"   Recommended: Buy {shares} shares")
            print(f"   Investment needed: ${investment:.2f}")
        elif signal == 'SELL':
            print(f"   Recommended: Sell or avoid buying")
        else:
            print(f"   Recommended: Wait for clearer signal")
        
        # Generate chart
        self.view.plot_chart(symbol, df)
        
        print("\n" + "="*60)
