"""
MAIN.PY - Entry Point of the Trading Bot
=========================================
This is the file you run to start the trading bot.

Usage:
    python main.py              # Run full backtest
    python main.py analyze AAPL # Analyze single stock
"""

import sys
from controller import TradingController


def main():
    """
    Main function - entry point of the program.
    """
    # Create controller instance
    controller = TradingController()
    
    # Check if user provided arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        # Single stock analysis mode
        if command == 'analyze' and len(sys.argv) > 2:
            symbol = sys.argv[2].upper()
            controller.run_single_analysis(symbol)
        
        # Help command
        elif command == 'help' or command == '--help' or command == '-h':
            print("\n📚 TRADING BOT COMMANDS")
            print("="*60)
            print("python main.py              - Run full backtest")
            print("python main.py analyze AAPL - Analyze single stock")
            print("python main.py help         - Show this help message")
            print("="*60 + "\n")
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python main.py help' for available commands")
    
    else:
        # Default: Run backtest
        controller.run_backtest()


if __name__ == "__main__":
    """
    This block runs when you execute the file directly.
    It's Python's way of saying "start here!"
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Bot stopped by user (Ctrl+C)")
        print("Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("If you need help, check the README.md file")
