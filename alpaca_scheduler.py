"""
ALPACA_SCHEDULER.PY - Updated with Interval Telegram Updates
=============================================================
Sends Telegram message EVERY scan showing:
- Scan number and time
- Symbols checked
- Signals found (or no signals)
- Portfolio value

Usage:
    python alpaca_scheduler.py --interval 15m
"""

import argparse
import time
from datetime import datetime
import asyncio
from dotenv import load_dotenv
import schedule

import config
from model import TradingModel
from alpaca_integration import AlpacaTrader

try:
    from telegram_bot import TelegramNotifier
    TELEGRAM_AVAILABLE = True
except:
    TELEGRAM_AVAILABLE = False

load_dotenv()


class AlpacaScheduler:

    def __init__(self, interval='15m', symbols=None, telegram_enabled=True):
        self.interval = interval
        self.symbols = symbols or config.SYMBOLS
        self.telegram_enabled = telegram_enabled
        self.scan_count = 0

        self.model = TradingModel()
        self.alpaca = AlpacaTrader()

        if telegram_enabled and TELEGRAM_AVAILABLE:
            try:
                self.notifier = TelegramNotifier()
                print("✅ Telegram notifications enabled")
            except:
                self.telegram_enabled = False

        print(f"\n🤖 Alpaca Scheduler initialized")
        print(f"   Interval: {interval}")
        print(f"   Symbols: {len(self.symbols)} stocks")
        print(f"   Telegram: {'Enabled' if self.telegram_enabled else 'Disabled'}")

    def run_analysis(self):
        """Run trading analysis and send Telegram interval update."""
        self.scan_count += 1
        now = datetime.now()

        print(f"\n{'='*60}")
        print(f"🔄 Scan #{self.scan_count} at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        signals_found = []
        symbols_checked = 0
        errors = 0

        for symbol in self.symbols:
            try:
                print(f"\n📊 Analyzing {symbol}...")

                bars = self.alpaca.get_bars(symbol, '1Day', 100)
                if bars is None or bars.empty:
                    print(f"   ⚠️  No data for {symbol}")
                    errors += 1
                    continue

                symbols_checked += 1
                self.model.market_data[symbol] = bars
                self.model.calculate_all_indicators(symbol)

                signal = self.model.generate_multi_strategy_signal(symbol)
                current_price = self.alpaca.get_price(symbol)

                if signal == 'BUY':
                    print(f"   🟢 BUY signal!")
                    buying_power = self.alpaca.get_buying_power()
                    position_size = buying_power * config.MAX_POSITION_SIZE
                    order = self.alpaca.buy(symbol, notional=position_size)
                    if order:
                        signals_found.append({
                            'symbol': symbol, 'signal': 'BUY', 'price': current_price
                        })

                elif signal == 'SELL':
                    print(f"   🔴 SELL signal!")
                    position = self.alpaca.get_position(symbol)
                    if position:
                        order = self.alpaca.sell(symbol)
                        if order:
                            signals_found.append({
                                'symbol': symbol, 'signal': 'SELL', 'price': current_price
                            })
                else:
                    print(f"   ⚪ HOLD")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                errors += 1

        # Get portfolio status
        portfolio_value = self.alpaca.get_portfolio_value()
        buying_power = self.alpaca.get_buying_power()
        positions = self.alpaca.get_all_positions()

        print(f"\n{'='*60}")
        print(f"💼 Portfolio: ${portfolio_value:,.2f} | Positions: {len(positions)}")
        print(f"{'='*60}")

        # Send Telegram update every interval
        if self.telegram_enabled:
            asyncio.run(self._send_interval_update(
                scan_count=self.scan_count,
                symbols_checked=symbols_checked,
                signals_found=signals_found,
                portfolio_value=portfolio_value,
                positions=len(positions),
                buying_power=buying_power,
                errors=errors,
                now=now
            ))

    async def _send_interval_update(self, scan_count, symbols_checked,
                                     signals_found, portfolio_value,
                                     positions, buying_power, errors, now):
        """Send status update + signal alerts every interval."""

        # Send individual BUY/SELL alerts first
        for sig in signals_found:
            try:
                await self.notifier.send_simple_signal(
                    sig['symbol'], sig['signal'], sig['price']
                )
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"⚠️  Signal alert error: {e}")

        # Send scan summary
        try:
            if signals_found:
                signal_lines = '\n'.join([
                    f"{'🟢' if s['signal'] == 'BUY' else '🔴'} "
                    f"{s['signal']} {s['symbol']} @ ${s['price']:.2f}"
                    for s in signals_found
                ])
                signals_text = f"\n🎯 <b>Signals:</b>\n{signal_lines}"
            else:
                signals_text = "\n⚪ No signals this scan"

            message = (
                f"📊 <b>Scan #{scan_count}</b>  |  "
                f"🕐 {now.strftime('%H:%M:%S')}\n"
                f"{'─'*28}\n"
                f"✅ Checked: {symbols_checked}/{len(self.symbols)} symbols\n"
                f"🔍 Signals: {len(signals_found)}"
                f"{signals_text}\n"
                f"{'─'*28}\n"
                f"💼 Portfolio: <b>${portfolio_value:,.2f}</b>\n"
                f"💵 Cash: ${buying_power/2:,.2f}\n"
                f"📈 Positions: {positions}"
            )

            await self.notifier.send_message(message)

        except Exception as e:
            print(f"⚠️  Interval update error: {e}")

    def start(self):
        """Start the scheduler."""
        print(f"\n🚀 Starting Alpaca scheduler | Every {self.interval}")
        print(f"   Press Ctrl+C to stop\n")

        if not self.alpaca.test_connection():
            print("❌ Alpaca connection failed. Check API keys in .env")
            return

        # Startup Telegram message
        if self.telegram_enabled:
            try:
                asyncio.run(self.notifier.send_message(
                    f"🤖 <b>Trading Bot Started</b>\n\n"
                    f"⏱ Interval: Every {self.interval}\n"
                    f"📊 Watching: {len(self.symbols)} stocks\n"
                    f"🌐 Platform: Alpaca Paper Trading\n"
                    f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"<i>Status update every {self.interval} ✅</i>"
                ))
            except:
                pass

        # Run first scan immediately
        self.run_analysis()

        # Schedule repeating scans
        interval_map = {
            '1m': 1, '5m': 5, '15m': 15,
            '30m': 30, '1h': 60, '4h': 240
        }
        minutes = interval_map.get(self.interval, 15)
        schedule.every(minutes).minutes.do(self.run_analysis)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⚠️  Scheduler stopped")
            if self.telegram_enabled:
                try:
                    portfolio_value = self.alpaca.get_portfolio_value()
                    positions = self.alpaca.get_all_positions()
                    asyncio.run(self.notifier.send_message(
                        f"🛑 <b>Trading Bot Stopped</b>\n\n"
                        f"📊 Total scans run: {self.scan_count}\n"
                        f"💼 Final portfolio: ${portfolio_value:,.2f}\n"
                        f"📈 Open positions: {len(positions)}\n"
                        f"🕐 Stopped: {datetime.now().strftime('%H:%M:%S')}"
                    ))
                except:
                    pass


def main():
    parser = argparse.ArgumentParser(description='Alpaca Trading Scheduler')
    parser.add_argument('--interval', type=str, default='15m',
                        choices=['1m', '5m', '15m', '30m', '1h', '4h'])
    parser.add_argument('--symbols', type=str)
    parser.add_argument('--no-telegram', action='store_true')
    args = parser.parse_args()

    symbols = None
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]

    try:
        scheduler = AlpacaScheduler(
            interval=args.interval,
            symbols=symbols,
            telegram_enabled=not args.no_telegram
        )
        scheduler.start()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
