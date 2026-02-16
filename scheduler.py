"""
SCHEDULER.PY - Automated Trading Scheduler
===========================================
Runs trading bot automatically at specified intervals.

Usage:
    python scheduler.py           # Run with default config
    python scheduler.py --interval 5m   # Run every 5 minutes
    python scheduler.py --interval 1h   # Run every hour
    python scheduler.py --symbols AAPL,MSFT  # Specific symbols

Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d
"""

import schedule
import time
import argparse
from datetime import datetime
import asyncio
from dotenv import load_dotenv

import config
from model import TradingModel
from telegram_bot import TelegramNotifier


# Load environment variables
load_dotenv()


class TradingScheduler:
    """Automated trading scheduler."""
    
    def __init__(self, interval='5m', symbols=None, telegram_enabled=True):
        """
        Initialize scheduler.
        
        Args:
            interval (str): Trading interval (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            symbols (list): List of symbols to trade
            telegram_enabled (bool): Send Telegram notifications
        """
        self.interval = interval
        self.symbols = symbols or config.SYMBOLS
        self.telegram_enabled = telegram_enabled
        self.model = TradingModel()
        
        if telegram_enabled:
            try:
                self.notifier = TelegramNotifier()
                print("✅ Telegram notifications enabled")
            except Exception as e:
                print(f"⚠️  Telegram not configured: {e}")
                self.telegram_enabled = False
        
        # Set timeframe based on interval
        self.timeframe_map = {
            '1m': '1m',
            '3m': '5m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '1h',
            '1d': '1d'
        }
        config.TIMEFRAME = self.timeframe_map.get(interval, '1h')
        
        print(f"🤖 Scheduler initialized")
        print(f"   Interval: {interval}")
        print(f"   Timeframe: {config.TIMEFRAME}")
        print(f"   Symbols: {len(self.symbols)} stocks")
        print(f"   Telegram: {'Enabled' if telegram_enabled else 'Disabled'}")
    
    def run_analysis(self):
        """Run trading analysis for all symbols."""
        print(f"\n{'='*60}")
        print(f"🔄 Running analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        signals_found = []
        
        for symbol in self.symbols:
            try:
                print(f"\n📊 Analyzing {symbol}...")
                
                # Fetch and analyze
                self.model.fetch_market_data(symbol)
                self.model.calculate_all_indicators(symbol)
                
                # Generate signal
                signal = self.model.generate_multi_strategy_signal(symbol)
                
                df = self.model.market_data.get(symbol)
                if df is not None and not df.empty:
                    current = df.iloc[-1]
                    current_price = current['Close']
                    
                    # Execute trades based on signal
                    if signal == 'BUY':
                        success = self.model.execute_buy(symbol, current_price)
                        if success:
                            signals_found.append({
                                'symbol': symbol,
                                'signal': signal,
                                'price': current_price,
                                'indicators': self._get_indicators(current)
                            })
                    
                    elif signal == 'SELL':
                        success = self.model.execute_sell(symbol, current_price)
                        if success:
                            signals_found.append({
                                'symbol': symbol,
                                'signal': signal,
                                'price': current_price,
                                'indicators': self._get_indicators(current)
                            })
                    
                    # Check risk management
                    risk_signal = self.model.check_stop_loss_take_profit(symbol)
                    if risk_signal == 'SELL':
                        self.model.execute_sell(symbol, current_price)
            
            except Exception as e:
                print(f"❌ Error with {symbol}: {e}")
        
        # Send Telegram notifications
        if self.telegram_enabled and signals_found:
            asyncio.run(self._send_signals_to_telegram(signals_found))
        
        # Display portfolio status
        print(f"\n{'='*60}")
        print(f"💼 Portfolio Status:")
        print(f"   Cash: ${self.model.cash:.2f}")
        print(f"   Positions: {len(self.model.positions)}")
        print(f"   Total Value: ${self.model.get_portfolio_value():.2f}")
        print(f"{'='*60}\n")
    
    def _get_indicators(self, current):
        """Extract indicator values."""
        return {
            'rsi': f"{current.get('RSI', 0):.1f}",
            'macd': "Bullish" if current.get('MACD_Histogram', 0) > 0 else "Bearish",
            'ma': "Uptrend" if current.get('MA_Fast', 0) > current.get('MA_Slow', 0) else "Downtrend",
            'bollinger': f"{current.get('BB_Position', 0):.0%}"
        }
    
    async def _send_signals_to_telegram(self, signals):
        """Send signals to Telegram using simple format."""
        for sig in signals:
            try:
                # Use simple, concise format
                await self.notifier.send_simple_signal(
                    sig['symbol'],
                    sig['signal'],
                    sig['price']
                )
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"⚠️  Telegram error: {e}")
    
    def start(self):
        """Start the scheduler."""
        print(f"\n🚀 Starting automated trading scheduler")
        print(f"   Running every {self.interval}")
        print(f"   Press Ctrl+C to stop\n")
        
        # Send startup notification
        if self.telegram_enabled:
            try:
                asyncio.run(self.notifier.send_message(
                    f"🤖 <b>Trading Bot Started</b>\n\n"
                    f"Interval: {self.interval}\n"
                    f"Symbols: {len(self.symbols)}\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"<i>Developed by Raghu with Claude</i>"
                ))
            except:
                pass
        
        # Schedule based on interval
        if self.interval == '1m':
            schedule.every(1).minutes.do(self.run_analysis)
        elif self.interval == '3m':
            schedule.every(3).minutes.do(self.run_analysis)
        elif self.interval == '5m':
            schedule.every(5).minutes.do(self.run_analysis)
        elif self.interval == '15m':
            schedule.every(15).minutes.do(self.run_analysis)
        elif self.interval == '30m':
            schedule.every(30).minutes.do(self.run_analysis)
        elif self.interval == '1h':
            schedule.every(1).hours.do(self.run_analysis)
        elif self.interval == '4h':
            schedule.every(4).hours.do(self.run_analysis)
        elif self.interval == '1d':
            schedule.every().day.at("09:30").do(self.run_analysis)  # Market open
        
        # Run once immediately
        self.run_analysis()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Scheduler stopped by user")
            if self.telegram_enabled:
                try:
                    asyncio.run(self.notifier.send_message(
                        f"🛑 <b>Trading Bot Stopped</b>\n\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ))
                except:
                    pass


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Automated Trading Scheduler')
    
    parser.add_argument(
        '--interval',
        type=str,
        default='5m',
        choices=['1m', '3m', '5m', '15m', '30m', '1h', '4h', '1d'],
        help='Trading interval (default: 5m)'
    )
    
    parser.add_argument(
        '--symbols',
        type=str,
        help='Comma-separated list of symbols (e.g., AAPL,MSFT,GOOGL)'
    )
    
    parser.add_argument(
        '--no-telegram',
        action='store_true',
        help='Disable Telegram notifications'
    )
    
    args = parser.parse_args()
    
    # Parse symbols
    symbols = None
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
    
    # Create and start scheduler
    scheduler = TradingScheduler(
        interval=args.interval,
        symbols=symbols,
        telegram_enabled=not args.no_telegram
    )
    
    scheduler.start()


if __name__ == "__main__":
    main()
