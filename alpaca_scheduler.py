"""
ALPACA_SCHEDULER.PY — Upgraded with Enhanced Signals + News
============================================================
What's new:
  ✅ 5 indicators (MA + RSI + MACD + Bollinger + Volume)
  ✅ Confidence scoring (WEAK / MEDIUM / STRONG)
  ✅ Alpaca News sentiment filter
  ✅ Earnings calendar — auto-skip risky days
  ✅ Position sizing based on confidence
  ✅ Rich Telegram messages with score + news context
  ✅ Interval updates every scan

Usage:
    python alpaca_scheduler.py --interval 5m
"""

import argparse
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import schedule

import config
from alpaca_integration import AlpacaTrader
from enhanced_signals import analyze_symbol, get_position_size, format_signal_summary
from news_integration import NewsIntegration

try:
    from telegram_bot import TelegramNotifier
    TELEGRAM_AVAILABLE = True
except:
    TELEGRAM_AVAILABLE = False

load_dotenv()


class UpgradedScheduler:
    """
    Professional trading scheduler with full signal stack:
    5 indicators + news + earnings calendar.
    """

    def __init__(self, interval="5m", symbols=None, telegram_enabled=True,
                 news_enabled=True, base_position=2000.0):

        self.interval        = interval
        self.symbols         = symbols or config.SYMBOLS
        self.telegram_on     = telegram_enabled
        self.news_enabled    = news_enabled
        self.base_position   = base_position
        self.scan_count      = 0
        self.total_signals   = 0

        self.alpaca  = AlpacaTrader()
        self.news    = NewsIntegration(self.alpaca._api if hasattr(self.alpaca, "_api") else None)

        if telegram_enabled and TELEGRAM_AVAILABLE:
            try:
                self.notifier = TelegramNotifier()
                print("✅ Telegram enabled")
            except:
                self.telegram_on = False
        else:
            self.telegram_on = False

        print(f"\n🚀 Upgraded Scheduler ready")
        print(f"   Interval: {interval}")
        print(f"   Symbols:  {len(self.symbols)}")
        print(f"   News:     {'✅' if news_enabled else '❌'}")
        print(f"   Position: ${base_position:,.0f} base (scales with confidence)")
        print(f"   ─────────────────────────────────")
        print(f"   STRONG signal → ${base_position:,.0f}")
        print(f"   MEDIUM signal → ${base_position*0.6:,.0f}")
        print(f"   WEAK signal   → ${base_position*0.3:,.0f} (caution)")

    # ─────────────────────────────────────────────────────────
    # MAIN SCAN
    # ─────────────────────────────────────────────────────────

    def run_scan(self):
        self.scan_count += 1
        now = datetime.now()

        print(f"\n{'═'*60}")
        print(f"  Scan #{self.scan_count}  |  {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'═'*60}")

        signals_this_scan = []
        checked = 0
        skipped_earnings = []
        errors = 0

        for symbol in self.symbols:
            try:
                print(f"\n  📊 {symbol}...")

                # ── Get price data from Alpaca ────────────────
                bars = self.alpaca.get_bars(symbol, "1Day", 100)
                if bars is None or bars.empty:
                    print(f"     ⚠️  No data")
                    errors += 1
                    continue

                checked += 1

                # ── Enhanced signal analysis ──────────────────
                result = analyze_symbol(symbol, bars)
                if not result:
                    print(f"     ⚠️  Analysis failed")
                    continue

                signal     = result["signal"]
                confidence = result["confidence"]
                score      = result["score"]

                # ── News + earnings context ───────────────────
                news_note = ""
                if self.news_enabled and signal != "HOLD":
                    context = self.news.get_full_context(symbol)

                    # Block on earnings warnings
                    if context["should_skip"]:
                        skipped_earnings.append(symbol)
                        print(f"     🚫 SKIPPED: {context['skip_reason']}")
                        continue

                    # Adjust signal based on news
                    signal, confidence, score, news_note = self.news.apply_news_to_signal(
                        signal, confidence, score, context
                    )

                    if signal == "HOLD":
                        print(f"     ⬇️  Downgraded by news: {news_note}")
                        continue

                # ── Final signal decision ─────────────────────
                if signal == "HOLD":
                    print(f"     ⚪ HOLD  (score: {score}/10)")
                    continue

                icon = "🟢" if signal == "BUY" else "🔴"
                conf_icon = {"STRONG":"🔥","MEDIUM":"⚡","WEAK":"💧"}.get(confidence,"")
                print(f"     {icon} {signal} | {confidence} {conf_icon} | Score: {score}/10")
                if news_note:
                    print(f"     📰 {news_note}")

                # ── Execute trade ─────────────────────────────
                position_size = get_position_size(confidence, self.base_position)
                executed      = False

                if signal == "BUY" and position_size > 0:
                    order = self.alpaca.buy(symbol, notional=position_size)
                    if order:
                        executed = True
                        print(f"     ✅ BUY executed: ${position_size:,.0f}")

                elif signal == "SELL":
                    position = self.alpaca.get_position(symbol)
                    if position:
                        order = self.alpaca.sell(symbol)
                        if order:
                            executed = True
                            print(f"     ✅ SELL executed")

                signals_this_scan.append({
                    **result,
                    "signal":     signal,
                    "confidence": confidence,
                    "score":      score,
                    "news_note":  news_note,
                    "executed":   executed,
                    "position_size": position_size,
                })

                self.total_signals += 1

            except Exception as e:
                print(f"     ❌ Error: {e}")
                errors += 1

        # ── Portfolio snapshot ────────────────────────────────
        portfolio_value = self.alpaca.get_portfolio_value()
        buying_power    = self.alpaca.get_buying_power()
        positions       = self.alpaca.get_all_positions()

        print(f"\n  {'─'*56}")
        print(f"  💼 Portfolio: ${portfolio_value:,.2f}  |  Positions: {len(positions)}")
        if skipped_earnings:
            print(f"  ⚠️  Skipped (earnings): {', '.join(skipped_earnings)}")
        print(f"  {'─'*56}")

        # ── Send Telegram update ──────────────────────────────
        if self.telegram_on:
            asyncio.run(self._send_telegram_update(
                signals_this_scan, checked, errors,
                portfolio_value, buying_power,
                len(positions), skipped_earnings, now
            ))

    # ─────────────────────────────────────────────────────────
    # TELEGRAM
    # ─────────────────────────────────────────────────────────

    async def _send_telegram_update(self, signals, checked, errors,
                                     portfolio_value, buying_power,
                                     positions, skipped, now):
        try:
            # Individual signal alerts
            for sig in signals:
                try:
                    msg = format_signal_summary(sig)
                    if msg:
                        await self.notifier.send_message(msg)
                        await asyncio.sleep(0.3)
                except:
                    pass

            # Scan summary
            if signals:
                sig_lines = "\n".join([
                    f"  {'🟢' if s['signal']=='BUY' else '🔴'} {s['signal']} "
                    f"{s['symbol']} | {s['confidence']} {s['score']}/10 | "
                    f"${s['price']:.2f}"
                    for s in signals
                ])
                sig_section = f"\n\n<b>🎯 Signals:</b>\n{sig_lines}"
            else:
                sig_section = "\n\n⚪ <i>No signals this scan</i>"

            skipped_text = ""
            if skipped:
                skipped_text = f"\n⚠️ Earnings skip: {', '.join(skipped)}"

            summary = (
                f"📊 <b>Scan #{self.scan_count}</b>  ·  "
                f"🕐 {now.strftime('%H:%M:%S')}\n"
                f"{'─'*28}\n"
                f"✅ Checked: {checked}/{len(self.symbols)}\n"
                f"🎯 Signals: {len(signals)}{skipped_text}"
                f"{sig_section}\n\n"
                f"{'─'*28}\n"
                f"💼 Portfolio: <b>${portfolio_value:,.2f}</b>\n"
                f"💵 Cash: ${buying_power/2:,.2f}\n"
                f"📈 Positions: {positions}\n"
                f"📊 Total signals today: {self.total_signals}"
            )

            await self.notifier.send_message(summary)

        except Exception as e:
            print(f"  ⚠️  Telegram error: {e}")

    # ─────────────────────────────────────────────────────────
    # START
    # ─────────────────────────────────────────────────────────

    def start(self):
        print(f"\n🚀 Starting scheduler  |  Every {self.interval}")
        print(f"   Press Ctrl+C to stop\n")

        if not self.alpaca.test_connection():
            print("❌ Alpaca connection failed")
            return

        # Startup Telegram message
        if self.telegram_on:
            try:
                asyncio.run(self.notifier.send_message(
                    f"🤖 <b>Enhanced Bot Started</b>\n\n"
                    f"⏱ Interval: {self.interval}\n"
                    f"📊 Watching: {len(self.symbols)} symbols\n"
                    f"🔬 5 Indicators: MA · RSI · MACD · Bollinger · Volume\n"
                    f"📰 News filter: {'✅' if self.news_enabled else '❌'}\n"
                    f"📅 Earnings guard: ✅\n"
                    f"💰 Position: ${self.base_position:,.0f} base\n"
                    f"🕐 {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"<i>Scan summary sent every {self.interval}</i>"
                ))
            except:
                pass

        # First scan immediately
        self.run_scan()

        # Schedule repeating
        interval_map = {
            "1m":15, "5m":5, "15m":15, "30m":30, "1h":60, "4h":240
        }
        minutes = interval_map.get(self.interval, 15)
        schedule.every(minutes).minutes.do(self.run_scan)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⛔ Bot stopped")
            if self.telegram_on:
                try:
                    pv = self.alpaca.get_portfolio_value()
                    pos = self.alpaca.get_all_positions()
                    asyncio.run(self.notifier.send_message(
                        f"🛑 <b>Bot Stopped</b>\n\n"
                        f"📊 Scans: {self.scan_count}\n"
                        f"🎯 Total signals: {self.total_signals}\n"
                        f"💼 Final portfolio: ${pv:,.2f}\n"
                        f"📈 Open positions: {len(pos)}\n"
                        f"🕐 {datetime.now().strftime('%H:%M:%S')}"
                    ))
                except:
                    pass


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Enhanced Alpaca Scheduler")
    parser.add_argument("--interval", default="5m",
                        choices=["1m","5m","15m","30m","1h","4h"])
    parser.add_argument("--symbols",  type=str,
                        help="Comma separated: AAPL,MSFT,NVDA")
    parser.add_argument("--position", type=float, default=2000.0,
                        help="Base position size in dollars (default: 2000)")
    parser.add_argument("--no-news",  action="store_true",
                        help="Disable news integration")
    parser.add_argument("--no-telegram", action="store_true")
    args = parser.parse_args()

    symbols = None
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]

    try:
        bot = UpgradedScheduler(
            interval        = args.interval,
            symbols         = symbols,
            telegram_enabled= not args.no_telegram,
            news_enabled    = not args.no_news,
            base_position   = args.position,
        )
        bot.start()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
