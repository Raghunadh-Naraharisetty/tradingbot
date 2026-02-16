"""
VIEW.PY - The "Display" of Our Trading Bot
===========================================
This handles:
1. Displaying results to the user
2. Creating charts and visualizations
3. Formatting output nicely
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import config


class TradingView:
    """
    This class handles all the visual output of our trading bot.
    It shows you what's happening in an easy-to-understand way.
    """
    
    def __init__(self):
        """Initialize the view."""
        print("👁️  Trading View initialized")
    
    
    def display_welcome(self):
        """
        Display welcome message with ASCII art.
        """
        print("\n" + "="*60)
        print("     📈 MULTI-STRATEGY TRADING BOT 📉")
        print("     Professional Consensus System")
        print("="*60)
        print("\nWelcome to your advanced trading bot!")
        print("This bot uses MULTIPLE strategies working together:")
        
        enabled_strats = [name.replace('_', ' ').title() for name, enabled in config.STRATEGIES_ENABLED.items() if enabled]
        for strat in enabled_strats:
            print(f"  ✓ {strat}")
        
        print(f"\nVoting: {config.STRATEGY_VOTE_REQUIRED.upper()}")
        print(f"Mode: {'📝 PAPER TRADING (Simulated)' if config.PAPER_TRADING else '💰 LIVE TRADING'}")
        print("="*60 + "\n")
    
    
    def display_strategy_explanation(self):
        """
        Explain the Multi-Strategy System.
        """
        print("\n" + "-"*60)
        print("📚 STRATEGY EXPLANATION")
        print("-"*60)
        print("\n🎯 MULTI-STRATEGY SYSTEM (Professional Approach!):")
        print("   Instead of one indicator, we use MULTIPLE strategies:")
        
        enabled = [name.replace('_', ' ').title() for name, enabled in config.STRATEGIES_ENABLED.items() if enabled]
        for i, strategy in enumerate(enabled, 1):
            print(f"   {i}. {strategy}")
        
        print(f"\n⚖️  VOTING SYSTEM: '{config.STRATEGY_VOTE_REQUIRED}'")
        if config.STRATEGY_VOTE_REQUIRED == 'all':
            print("   → ALL strategies must agree (most conservative)")
        elif config.STRATEGY_VOTE_REQUIRED == 'majority':
            print("   → MAJORITY must agree (balanced - recommended)")
        elif config.STRATEGY_VOTE_REQUIRED == 'any':
            print("   → ANY strategy can trigger (most aggressive)")
        
        print("\n📈 How It Works:")
        print("   • Each enabled strategy votes BUY, SELL, or HOLD")
        print("   • Votes are counted and compared to requirement")
        print("   • RSI acts as final filter (rejects bad timing)")
        print("   • Volume confirms signal strength (optional)")
        
        print("\n💡 Why Multi-Strategy Works Better:")
        print("   • Filters 50-70% of false signals")
        print("   • Only trades when multiple indicators align")
        print("   • More robust across market conditions")
        print("   • Professional institutional approach")
        
        print("\n💡 Risk Management:")
        print(f"   • Stop Loss: {config.STOP_LOSS_PERCENT*100}% below buy price")
        print(f"   • Take Profit: {config.TAKE_PROFIT_PERCENT*100}% above buy price")
        print(f"   • Max Position: {config.MAX_POSITION_SIZE*100}% of capital")
        print("-"*60 + "\n")
    
    
    def display_market_data_summary(self, symbol, df):
        """
        Display summary of market data.
        
        Args:
            symbol (str): Stock ticker
            df (DataFrame): Market data with indicators
        """
        if df is None or df.empty:
            print(f"⚠️  No data to display for {symbol}")
            return
        
        latest = df.iloc[-1]
        
        print(f"\n📊 MARKET DATA SUMMARY - {symbol}")
        print("-" * 40)
        print(f"Date: {latest.name.date()}")
        print(f"Close Price: ${latest['Close']:.2f}")
        print(f"Fast MA ({config.MA_FAST_PERIOD}): ${latest['MA_Fast']:.2f}")
        print(f"Slow MA ({config.MA_SLOW_PERIOD}): ${latest['MA_Slow']:.2f}")
        
        # Show RSI if available
        if 'RSI' in df.columns:
            rsi_value = latest['RSI']
            print(f"RSI ({config.RSI_PERIOD}): {rsi_value:.2f}", end="")
            
            # Add RSI interpretation
            if rsi_value < config.RSI_OVERSOLD:
                print(" 🟢 OVERSOLD")
            elif rsi_value > config.RSI_OVERBOUGHT:
                print(" 🔴 OVERBOUGHT")
            else:
                print(" ⚪ NEUTRAL")
        
        # Show trend
        if latest['MA_Fast'] > latest['MA_Slow']:
            print("Current Trend: 🟢 BULLISH (Fast > Slow)")
        else:
            print("Current Trend: 🔴 BEARISH (Fast < Slow)")
        
        print("-" * 40)
    
    
    def display_portfolio_status(self, model):
        """
        Display current portfolio status.
        
        Args:
            model (TradingModel): The trading model instance
        """
        portfolio_value = model.get_portfolio_value()
        total_return = portfolio_value - config.INITIAL_CAPITAL
        return_percent = (total_return / config.INITIAL_CAPITAL) * 100
        
        print(f"\n💼 PORTFOLIO STATUS")
        print("=" * 50)
        print(f"Cash Available: ${model.cash:.2f}")
        print(f"Initial Capital: ${config.INITIAL_CAPITAL:.2f}")
        print(f"Current Value: ${portfolio_value:.2f}")
        print(f"Total Return: ${total_return:.2f} ({return_percent:+.2f}%)")
        
        # Display positions
        if model.positions:
            print(f"\n📦 Open Positions: {len(model.positions)}")
            for symbol, position in model.positions.items():
                df = model.market_data.get(symbol)
                current_price = df['Close'].iloc[-1] if df is not None else 0
                position_value = position['shares'] * current_price
                unrealized_pl = position_value - (position['shares'] * position['buy_price'])
                unrealized_pl_percent = (unrealized_pl / (position['shares'] * position['buy_price'])) * 100
                
                print(f"\n   {symbol}:")
                print(f"   • Shares: {position['shares']}")
                print(f"   • Buy Price: ${position['buy_price']:.2f}")
                print(f"   • Current Price: ${current_price:.2f}")
                print(f"   • Position Value: ${position_value:.2f}")
                print(f"   • Unrealized P/L: ${unrealized_pl:.2f} ({unrealized_pl_percent:+.2f}%)")
        else:
            print("\n📦 Open Positions: None")
        
        print("=" * 50)
    
    
    def display_trade_history(self, trades):
        """
        Display trade history in a table format.
        
        Args:
            trades (list): List of trade dictionaries
        """
        if not trades:
            print("\n📋 TRADE HISTORY: No trades executed yet")
            return
        
        print(f"\n📋 TRADE HISTORY ({len(trades)} trades)")
        print("=" * 80)
        print(f"{'Date':<20} {'Symbol':<8} {'Action':<6} {'Shares':<8} {'Price':<10} {'Value':<12} {'P/L':<10}")
        print("-" * 80)
        
        for trade in trades:
            date_str = trade['date'].strftime('%Y-%m-%d %H:%M')
            symbol = trade['symbol']
            action = trade['action']
            shares = trade['shares']
            price = f"${trade['price']:.2f}"
            value = f"${trade['value']:.2f}"
            
            # P/L only for SELL trades
            if action == 'SELL' and 'profit' in trade:
                pl = f"${trade['profit']:.2f}"
                pl_emoji = "📈" if trade['profit'] > 0 else "📉"
            else:
                pl = "-"
                pl_emoji = ""
            
            print(f"{date_str:<20} {symbol:<8} {action:<6} {shares:<8} {price:<10} {value:<12} {pl:<10} {pl_emoji}")
        
        print("=" * 80)
    
    
    def plot_chart(self, symbol, df, trades=None):
        """
        Create a chart showing:
        1. Stock price
        2. Moving averages
        3. RSI indicator
        4. Buy/sell signals
        
        Args:
            symbol (str): Stock ticker
            df (DataFrame): Market data with indicators
            trades (list): List of trades for this symbol
        """
        if df is None or df.empty:
            print(f"⚠️  Cannot plot chart: No data for {symbol}")
            return
        
        # Create figure with 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), 
                                            gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # Plot 1: Price and Moving Averages
        ax1.plot(df.index, df['Close'], label='Close Price', color='black', linewidth=2)
        ax1.plot(df.index, df['MA_Fast'], label=f'Fast MA ({config.MA_FAST_PERIOD})', 
                color='blue', linewidth=1.5, alpha=0.7)
        ax1.plot(df.index, df['MA_Slow'], label=f'Slow MA ({config.MA_SLOW_PERIOD})', 
                color='red', linewidth=1.5, alpha=0.7)
        
        # Mark buy/sell points if trades provided
        if trades:
            buy_trades = [t for t in trades if t['action'] == 'BUY' and t['symbol'] == symbol]
            sell_trades = [t for t in trades if t['action'] == 'SELL' and t['symbol'] == symbol]
            
            for trade in buy_trades:
                ax1.scatter(trade['date'], trade['price'], color='green', 
                           marker='^', s=200, label='Buy Signal', zorder=5)
            
            for trade in sell_trades:
                ax1.scatter(trade['date'], trade['price'], color='red', 
                           marker='v', s=200, label='Sell Signal', zorder=5)
        
        ax1.set_title(f'{symbol} - Hybrid Strategy (MA Crossover + RSI)', 
                     fontsize=16, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: RSI
        if 'RSI' in df.columns:
            ax2.plot(df.index, df['RSI'], label=f'RSI ({config.RSI_PERIOD})', 
                    color='purple', linewidth=2)
            
            # Add overbought/oversold lines
            ax2.axhline(y=config.RSI_OVERBOUGHT, color='red', linestyle='--', 
                       linewidth=1, alpha=0.5, label='Overbought (70)')
            ax2.axhline(y=config.RSI_OVERSOLD, color='green', linestyle='--', 
                       linewidth=1, alpha=0.5, label='Oversold (30)')
            ax2.axhline(y=50, color='gray', linestyle=':', linewidth=1, alpha=0.3)
            
            # Fill overbought/oversold zones
            ax2.fill_between(df.index, config.RSI_OVERBOUGHT, 100, 
                            color='red', alpha=0.1)
            ax2.fill_between(df.index, 0, config.RSI_OVERSOLD, 
                            color='green', alpha=0.1)
            
            ax2.set_ylabel('RSI', fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: Volume
        ax3.bar(df.index, df['Volume'], color='gray', alpha=0.5)
        ax3.set_ylabel('Volume', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        filename = f'{symbol}_chart.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n📊 Chart saved: {filename}")
        
        plt.close()
    
    
    def display_performance_metrics(self, model):
        """
        Calculate and display performance metrics.
        
        Args:
            model (TradingModel): The trading model instance
        """
        if not model.trades:
            print("\n📊 PERFORMANCE METRICS: No trades to analyze")
            return
        
        # Calculate metrics
        completed_trades = [t for t in model.trades if t['action'] == 'SELL']
        
        if not completed_trades:
            print("\n📊 PERFORMANCE METRICS: No completed trades yet")
            return
        
        total_trades = len(completed_trades)
        winning_trades = len([t for t in completed_trades if t['profit'] > 0])
        losing_trades = len([t for t in completed_trades if t['profit'] < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_profit = sum([t['profit'] for t in completed_trades])
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        max_profit = max([t['profit'] for t in completed_trades]) if completed_trades else 0
        max_loss = min([t['profit'] for t in completed_trades]) if completed_trades else 0
        
        portfolio_value = model.get_portfolio_value()
        total_return = ((portfolio_value - config.INITIAL_CAPITAL) / config.INITIAL_CAPITAL) * 100
        
        print("\n📊 PERFORMANCE METRICS")
        print("=" * 50)
        print(f"Total Completed Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades} 🎉")
        print(f"Losing Trades: {losing_trades} 😞")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"\nTotal Profit/Loss: ${total_profit:.2f}")
        print(f"Average P/L per Trade: ${avg_profit:.2f}")
        print(f"Best Trade: ${max_profit:.2f} 📈")
        print(f"Worst Trade: ${max_loss:.2f} 📉")
        print(f"\nTotal Return: {total_return:+.2f}%")
        print("=" * 50)
        
        # Reality check message
        print("\n💡 IMPORTANT REMINDERS:")
        print("   • Past performance doesn't guarantee future results")
        print("   • This is a learning tool, not financial advice")
        print("   • Always practice with paper trading first")
        print("   • Real markets have fees, slippage, and taxes")
    
    
    def display_footer(self):
        """
        Display footer with custom message.
        """
        print("\n" + "="*60)
        print("Thank you for using the Hybrid Trading Bot!")
        print()
        print("⚠️  DISCLAIMER:")
        print("Developed by Raghu with the help of Claude.")
        print("="*60 + "\n")
