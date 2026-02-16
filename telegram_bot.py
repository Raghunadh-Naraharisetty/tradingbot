"""
TELEGRAM_BOT.PY - Telegram Integration
=======================================
Send trading signals and alerts to your Telegram.

Setup:
1. Create bot with @BotFather on Telegram
2. Get your bot token
3. Create .env file with: TELEGRAM_BOT_TOKEN=your_token_here
4. Get your chat ID by messaging bot, then run: python telegram_bot.py get_chat_id
5. Add TELEGRAM_CHAT_ID=your_chat_id to .env file

Usage:
    python telegram_bot.py          # Start bot (listens for commands)
    python telegram_bot.py test     # Send test message
    python telegram_bot.py signal   # Send current signals for all symbols
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import asyncio

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  Telegram library not installed. Run: pip install python-telegram-bot")

import config
from model import TradingModel


# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class TelegramNotifier:
    """Handles sending messages to Telegram."""
    
    def __init__(self, token=None, chat_id=None):
        """Initialize notifier."""
        self.token = token or BOT_TOKEN
        self.chat_id = chat_id or CHAT_ID
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    async def send_message(self, text, parse_mode='HTML'):
        """Send a text message."""
        if not TELEGRAM_AVAILABLE:
            print("❌ Telegram not available")
            return False
        
        try:
            from telegram import Bot
            bot = Bot(token=self.token)
            
            if self.chat_id:
                await bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode
                )
                return True
            else:
                print("⚠️  No chat ID configured")
                return False
        
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    async def send_signal(self, symbol, signal, price, indicators=None):
        """Send trading signal alert."""
        emoji = "🟢" if signal == 'BUY' else "🔴" if signal == 'SELL' else "⚪"
        
        message = f"""
{emoji} <b>TRADING SIGNAL</b>

<b>Symbol:</b> {symbol}
<b>Signal:</b> {signal}
<b>Price:</b> ${price:.2f}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<b>Indicators:</b>
• RSI: {indicators.get('rsi', 'N/A')}
• MACD: {indicators.get('macd', 'N/A')}
• MA: {indicators.get('ma', 'N/A')}
• Bollinger: {indicators.get('bollinger', 'N/A')}

<i>Developed by Raghu with Claude</i>
        """.strip()
        
        await self.send_message(message)
    
    async def send_simple_signal(self, symbol, signal, price):
        """
        Send SIMPLE trading signal - Just the essentials!
        
        Perfect for quick mobile alerts.
        """
        if signal == 'BUY':
            message = f"🟢 <b>BUY {symbol} at ${price:.2f}</b>"
        elif signal == 'SELL':
            message = f"🔴 <b>SELL {symbol} at ${price:.2f}</b>"
        else:
            return  # Don't send HOLD signals
        
        # Add timestamp
        message += f"\n<i>{datetime.now().strftime('%H:%M:%S')}</i>"
        
        await self.send_message(message)
    
    async def send_portfolio_update(self, cash, positions, total_value, return_pct):
        """Send portfolio status update."""
        message = f"""
💼 <b>PORTFOLIO UPDATE</b>

<b>Cash:</b> ${cash:.2f}
<b>Total Value:</b> ${total_value:.2f}
<b>Return:</b> {return_pct:+.2f}%

<b>Open Positions:</b> {len(positions)}
        """.strip()
        
        for symbol, pos in positions.items():
            unrealized = (pos.get('current_price', 0) - pos.get('buy_price', 0)) * pos.get('shares', 0)
            message += f"\n• {symbol}: {pos.get('shares', 0)} shares @ ${pos.get('buy_price', 0):.2f}"
            message += f" (P/L: ${unrealized:+.2f})"
        
        message += f"\n\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        await self.send_message(message)
    
    async def send_trade_execution(self, symbol, action, shares, price, total):
        """Send trade execution notification."""
        emoji = "✅" if action == 'BUY' else "💰"
        
        message = f"""
{emoji} <b>TRADE EXECUTED</b>

<b>Action:</b> {action}
<b>Symbol:</b> {symbol}
<b>Shares:</b> {shares}
<b>Price:</b> ${price:.2f}
<b>Total:</b> ${total:.2f}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        await self.send_message(message)
    
    async def send_daily_summary(self, trades_today, win_rate, best_trade, worst_trade):
        """Send daily performance summary."""
        message = f"""
📊 <b>DAILY SUMMARY</b>

<b>Trades Today:</b> {trades_today}
<b>Win Rate:</b> {win_rate:.1f}%
<b>Best Trade:</b> ${best_trade:+.2f}
<b>Worst Trade:</b> ${worst_trade:+.2f}

<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

<i>Keep up the good work! 🚀</i>
        """.strip()
        
        await self.send_message(message)


# Telegram Bot Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_text = """
👋 <b>Welcome to Multi-Strategy Trading Bot!</b>

Available commands:
/signal - Get current signals for all stocks
/portfolio - View portfolio status
/help - Show this help message

<i>Developed by Raghu with Claude</i>
    """.strip()
    
    await update.message.reply_text(welcome_text, parse_mode='HTML')


async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /signal command."""
    await update.message.reply_text("🔍 Analyzing symbols...")
    
    try:
        model = TradingModel()
        signals_text = "<b>📈 CURRENT SIGNALS</b>\n\n"
        
        for symbol in config.SYMBOLS[:5]:  # Limit to first 5
            try:
                model.fetch_market_data(symbol)
                model.calculate_all_indicators(symbol)
                
                df = model.market_data.get(symbol)
                if df is not None and not df.empty:
                    signal = model.generate_multi_strategy_signal(symbol)
                    current_price = df['Close'].iloc[-1]
                    rsi = df.get('RSI', pd.Series([0])).iloc[-1]
                    
                    emoji = "🟢" if signal == 'BUY' else "🔴" if signal == 'SELL' else "⚪"
                    signals_text += f"{emoji} <b>{symbol}</b>: {signal}\n"
                    signals_text += f"   Price: ${current_price:.2f} | RSI: {rsi:.1f}\n\n"
            
            except Exception as e:
                signals_text += f"⚠️ {symbol}: Error\n\n"
        
        signals_text += f"<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        await update.message.reply_text(signals_text, parse_mode='HTML')
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /portfolio command."""
    # This would connect to your actual portfolio tracking
    await update.message.reply_text(
        "💼 <b>PORTFOLIO STATUS</b>\n\n"
        "This feature connects to your running bot instance.\n"
        "Currently showing demo data.\n\n"
        "<i>Configure portfolio tracking in main.py</i>",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
<b>📚 AVAILABLE COMMANDS</b>

/start - Welcome message
/signal - Get current signals for all stocks
/portfolio - View portfolio status
/help - Show this help

<b>🔔 Automatic Notifications:</b>
• Trading signals (BUY/SELL)
• Trade executions
• Portfolio updates
• Daily summaries

<i>Bot developed by Raghu with Claude</i>
    """.strip()
    
    await update.message.reply_text(help_text, parse_mode='HTML')


def start_bot():
    """Start the Telegram bot."""
    if not TELEGRAM_AVAILABLE:
        print("❌ Telegram library not installed")
        print("Run: pip install python-telegram-bot")
        return
    
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        print("\nSetup instructions:")
        print("1. Create bot with @BotFather on Telegram")
        print("2. Copy the token")
        print("3. Create .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    print("🤖 Starting Telegram bot...")
    print(f"Token: {BOT_TOKEN[:10]}...")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("help", help_command))
    
    print("✅ Bot started! Press Ctrl+C to stop.")
    print("\nAvailable commands:")
    print("  /start - Welcome message")
    print("  /signal - Get current signals")
    print("  /portfolio - Portfolio status")
    print("  /help - Show help")
    
    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)


async def test_message():
    """Send a test message."""
    if not CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID not found in .env file")
        print("\nTo get your chat ID:")
        print("1. Start your bot on Telegram")
        print("2. Send it a message")
        print("3. Run: python telegram_bot.py get_chat_id")
        return
    
    notifier = TelegramNotifier()
    print("📤 Sending test message...")
    
    success = await notifier.send_message(
        "🎉 <b>Test Message</b>\n\n"
        "Your Telegram bot is working!\n\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "<i>Developed by Raghu with Claude</i>"
    )
    
    if success:
        print("✅ Test message sent successfully!")
    else:
        print("❌ Failed to send message")


async def send_current_signals():
    """Send signals for all configured symbols."""
    if not CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID not configured")
        return
    
    notifier = TelegramNotifier()
    model = TradingModel()
    
    print("🔍 Analyzing symbols and sending to Telegram...")
    
    # Send header message
    await notifier.send_message(
        f"📊 <b>Signal Scan Started</b>\n"
        f"Checking {len(config.SYMBOLS)} symbols...\n"
        f"{datetime.now().strftime('%H:%M:%S')}"
    )
    
    signals_sent = 0
    
    for symbol in config.SYMBOLS:
        try:
            print(f"  Analyzing {symbol}...")
            model.fetch_market_data(symbol)
            model.calculate_all_indicators(symbol)
            
            df = model.market_data.get(symbol)
            if df is not None and not df.empty:
                signal = model.generate_multi_strategy_signal(symbol)
                
                if signal != 'HOLD':  # Only send BUY/SELL signals
                    current_price = df['Close'].iloc[-1]
                    
                    # Use simple format
                    await notifier.send_simple_signal(
                        symbol,
                        signal,
                        current_price
                    )
                    
                    signals_sent += 1
                    print(f"  ✅ Sent {signal} signal for {symbol}")
                    await asyncio.sleep(1)  # Rate limiting
        
        except Exception as e:
            print(f"  ❌ Error with {symbol}: {e}")
    
    # Send summary
    if signals_sent == 0:
        await notifier.send_message("✅ Scan complete. No signals found.")
    else:
        await notifier.send_message(
            f"✅ <b>Scan Complete</b>\n"
            f"Found {signals_sent} signal(s)"
        )
    
    print(f"✅ Finished! Sent {signals_sent} signal(s)")


async def get_chat_id():
    """Get your Telegram chat ID."""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not configured")
        return
    
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)
    
    print("📱 Getting chat ID...")
    print("\n1. Send a message to your bot on Telegram")
    print("2. Wait a moment...")
    
    await asyncio.sleep(2)
    
    try:
        updates = await bot.get_updates()
        
        if updates:
            for update in updates[-3:]:  # Show last 3
                if update.message:
                    chat_id = update.message.chat.id
                    username = update.message.from_user.username
                    print(f"\n✅ Found chat ID: {chat_id}")
                    print(f"   Username: @{username}")
                    print(f"\nAdd this to your .env file:")
                    print(f"TELEGRAM_CHAT_ID={chat_id}")
        else:
            print("\n❌ No messages found")
            print("Make sure you've sent a message to your bot!")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            asyncio.run(test_message())
        
        elif command == 'signal':
            asyncio.run(send_current_signals())
        
        elif command == 'get_chat_id':
            asyncio.run(get_chat_id())
        
        elif command == 'help':
            print("""
Telegram Bot Commands:
======================

python telegram_bot.py              Start bot (listens for commands)
python telegram_bot.py test         Send test message
python telegram_bot.py signal       Send current signals
python telegram_bot.py get_chat_id  Get your Telegram chat ID

Setup:
1. Create bot with @BotFather
2. Get token and add to .env: TELEGRAM_BOT_TOKEN=your_token
3. Get chat ID: python telegram_bot.py get_chat_id
4. Add to .env: TELEGRAM_CHAT_ID=your_chat_id
            """)
        
        else:
            print(f"Unknown command: {command}")
            print("Run: python telegram_bot.py help")
    
    else:
        # Start bot
        start_bot()


if __name__ == "__main__":
    main()
