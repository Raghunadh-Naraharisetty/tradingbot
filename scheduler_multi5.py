"""
SCHEDULER_MULTI5.PY - Multi5 System Scheduler
==============================================
Automated trading scheduler for the 5-strategy system.

This is completely separate from your main scheduler.py
You can run BOTH at the same time to compare results!

Usage:
    python scheduler_multi5.py --interval 1h
"""

import schedule
import time
import argparse
from datetime import datetime
import asyncio
from dotenv import load_dotenv

import config_multi5 as config  # ← Uses Multi5 config!
from model import TradingModel
from telegram_bot import TelegramNotifier


# Load environment variables
load_dotenv()


class Multi5Scheduler:
    """Scheduler for 5-strategy system."""
    
    def __init__(self, interval='5m', symbols=None, telegram_enabled=True):
        """
        Initialize Multi5 scheduler.
        
        Args:
            interval (str): Trading interval
            symbols (list): Symbols to trade
            telegram_enabled (bool): Send Telegram notifications
        """
        self.interval = interval
        self.symbols = symbols or config.SYMBOLS
        self.telegram_enabled = telegram_enabled
        self.model = TradingModel()
        
        # Use Multi5 Telegram bot if configured
        if telegram_enabled:
            try:
                # Try to use separate Multi5 bot
                token = config.TELEGRAM_BOT_TOKEN_MULTI5 if hasattr(config, 'TELEGRAM_BOT_TOKEN_MULTI5') else None
                chat_id = config.TELEGRAM_CHAT_ID_MULTI5 if hasattr(config, 'TELEGRAM_CHAT_ID_MULTI5') else None
                
                if token:
                    self.notifier = TelegramNotifier(token=token, chat_id=chat_id)
                    print("✅ Using separate Multi5 Telegram bot")
                else:
                    self.notifier = TelegramNotifier()
                    print("✅ Using default Telegram bot (consider creating separate bot for Multi5)")
            except Exception as e:
                print(f"⚠️  Telegram not configured: {e}")
                self.telegram_enabled = False
        
        # Set timeframe
        self.timeframe_map = {
            '1m': '1m', '3m': '5m', '5m': '5m', '15m': '15m',
            '30m': '30m', '1h': '1h', '4h': '1h', '1d': '1d'
        }
        config.TIMEFRAME = self.timeframe_map.get(interval, '1h')
        
        print(f"🤖 Multi5 Scheduler Initialized")
        print(f"   System: {config.SYSTEM_NAME} ({config.SYSTEM_VERSION})")
        print(f"   Interval: {interval}")
        print(f"   Timeframe: {config.TIMEFRAME}")
        print(f"   Symbols: {len(self.symbols)} stocks")
        print(f"   Strategies: 5 (MA, RSI, MACD, Bollinger, Volume)")
        print(f"   Voting: {config.STRATEGY_VOTE_REQUIRED}")
        print(f"   Telegram: {'Enabled' if telegram_enabled else 'Disabled'}")
    
    def run_analysis(self):
        """Run Multi5 analysis for all symbols."""
        print(f"\n{'='*60}")
        print(f"🔄 Multi5 Analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        signals_found = []
        
        for symbol in self.symbols:
            try:
                print(f"\n📊 Analyzing {symbol} [Multi5]...")
                
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
                                'price': current_price
                            })
                    
                    elif signal == 'SELL':
                        success = self.model.execute_sell(symbol, current_price)
                        if success:
                            signals_found.append({
                                'symbol': symbol,
                                'signal': signal,
                                'price': current_price
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
        print(f"💼 Multi5 Portfolio Status:")
        print(f"   Cash: ${self.model.cash:.2f}")
        print(f"   Positions: {len(self.model.positions)}")
        print(f"   Total Value: ${self.model.get_portfolio_value():.2f}")
        print(f"{'='*60}\n")
    
    async def _send_signals_to_telegram(self, signals):
        """Send signals to Telegram with Multi5 prefix."""
        for sig in signals:
            try:
                # Send with Multi5 prefix to distinguish from 2-strategy system
                message = f"[Multi5] "
                if sig['signal'] == 'BUY':
                    message += f"🟢 BUY {sig['symbol']} at ${sig['price']:.2f}"
                else:
                    message += f"🔴 SELL {sig['symbol']} at ${sig['price']:.2f}"
                
                message += f"\n<i>{datetime.now().strftime('%H:%M:%S')}</i>"
                
                await self.notifier.send_message(message)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"⚠️  Telegram error: {e}")
    
    def start(self):
        """Start the Multi5 scheduler."""
        print(f"\n🚀 Starting Multi5 Automated Trading")
        print(f"   Running every {self.interval}")
        print(f"   Press Ctrl+C to stop\n")
        
        # Send startup notification
        if self.telegram_enabled:
            try:
                asyncio.run(self.notifier.send_message(
                    f"🤖 <b>Multi5 Trading Bot Started</b>\n\n"
                    f"Interval: {self.interval}\n"
                    f"Symbols: {len(self.symbols)}\n"
                    f"Strategies: 5 (MA+RSI+MACD+BB+Vol)\n"
                    f"Voting: {config.STRATEGY_VOTE_REQUIRED}\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"<i>Multi5 System - Maximum Filtering</i>"
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
            schedule.every().day.at("09:30").do(self.run_analysis)
        
        # Run once immediately
        self.run_analysis()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Multi5 Scheduler stopped by user")
            if self.telegram_enabled:
                try:
                    asyncio.run(self.notifier.send_message(
                        f"🛑 <b>Multi5 Bot Stopped</b>\n\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ))
                except:
                    pass


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Multi5 Automated Trading Scheduler')
    
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
        help='Comma-separated list of symbols'
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
    scheduler = Multi5Scheduler(
        interval=args.interval,
        symbols=symbols,
        telegram_enabled=not args.no_telegram
    )
    
    scheduler.start()


if __name__ == "__main__":
    main()
