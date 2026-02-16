"""
QUICK_START.PY - Test Your Installation
========================================
Run this file to verify everything is installed correctly.

Usage: python quick_start.py
"""

def test_imports():
    """Test if all required packages are installed."""
    print("🔍 Testing package installations...\n")
    
    packages = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computations',
        'yfinance': 'Stock data fetching',
        'matplotlib': 'Chart creation'
    }
    
    all_good = True
    
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package:15} - {description}")
        except ImportError:
            print(f"❌ {package:15} - NOT INSTALLED")
            all_good = False
    
    print()
    
    if all_good:
        print("🎉 All packages installed successfully!")
        print("You're ready to run the trading bot!")
        return True
    else:
        print("⚠️  Some packages are missing.")
        print("Run: pip install -r requirements.txt")
        return False


def test_config():
    """Test if config file loads correctly."""
    print("\n🔍 Testing configuration...\n")
    
    try:
        import config
        print(f"✅ Initial Capital: ${config.INITIAL_CAPITAL}")
        print(f"✅ Symbols: {config.SYMBOLS}")
        print(f"✅ Fast MA Period: {config.MA_FAST_PERIOD}")
        print(f"✅ Slow MA Period: {config.MA_SLOW_PERIOD}")
        print(f"✅ Paper Trading: {config.PAPER_TRADING}")
        print("\n🎉 Configuration loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def quick_demo():
    """Run a quick demo to show the bot works."""
    print("\n🚀 Running quick demo...\n")
    print("="*60)
    
    try:
        from model import TradingModel
        
        # Create model
        model = TradingModel()
        
        # Fetch data for Apple
        print("\n📊 Fetching Apple (AAPL) data...")
        df = model.fetch_market_data('AAPL')
        
        if df is not None:
            print(f"✅ Successfully fetched {len(df)} data points")
            
            # Calculate moving averages
            print("\n📈 Calculating moving averages...")
            df = model.calculate_moving_averages('AAPL')
            
            if df is not None:
                print("✅ Moving averages calculated")
                
                # Show latest data
                latest = df.iloc[-1]
                print(f"\n📊 Latest Data:")
                print(f"   Date: {latest.name.date()}")
                print(f"   Close: ${latest['Close']:.2f}")
                print(f"   Fast MA: ${latest['MA_Fast']:.2f}")
                print(f"   Slow MA: ${latest['MA_Slow']:.2f}")
                
                # Check signal
                signal = model.detect_crossover('AAPL')
                print(f"\n🎯 Current Signal: {signal}")
                
                print("\n" + "="*60)
                print("🎉 Demo completed successfully!")
                print("Your bot is working perfectly!")
                print("\nNext step: Run 'python main.py' for full backtest")
                return True
        
        print("❌ Demo failed - check your internet connection")
        return False
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify all packages are installed")
        print("3. Make sure all bot files are in same folder")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  🧪 TRADING BOT - INSTALLATION TEST")
    print("="*60 + "\n")
    
    # Test 1: Package imports
    if not test_imports():
        print("\n❌ Installation incomplete. Please install missing packages.")
        return
    
    # Test 2: Configuration
    if not test_config():
        print("\n❌ Configuration error. Check config.py file.")
        return
    
    # Test 3: Quick demo
    quick_demo()
    
    print("\n" + "="*60)
    print("Testing complete! Check results above.")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
