"""
ALPACA_INTEGRATION.PY - Alpaca Paper Trading Integration
=========================================================
Connects your trading bot to Alpaca for:
1. Real-time data (instead of Yahoo Finance)
2. Paper trading execution
3. Portfolio tracking

Setup:
1. Sign up at https://alpaca.markets (free)
2. Get API keys from dashboard
3. Add to .env file:
   ALPACA_API_KEY=your_key
   ALPACA_SECRET_KEY=your_secret
   ALPACA_BASE_URL=https://paper-api.alpaca.markets

Usage:
    from alpaca_integration import AlpacaTrader
    trader = AlpacaTrader()
    trader.get_price('AAPL')
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd

try:
    from alpaca_trade_api import REST
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️  Alpaca library not installed. Run: pip install alpaca-trade-api")


# Load environment variables
load_dotenv()


class AlpacaTrader:
    """Alpaca paper trading integration."""
    
    def __init__(self):
        """Initialize Alpaca connection."""
        if not ALPACA_AVAILABLE:
            raise ImportError("Alpaca library not installed")
        
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API keys not found in .env file")
        
        # Initialize API
        self.api = REST(
            key_id=self.api_key,
            secret_key=self.secret_key,
            base_url=self.base_url
        )
        
        print("✅ Connected to Alpaca Paper Trading")
    
    def test_connection(self):
        """Test if Alpaca connection works."""
        try:
            account = self.api.get_account()
            print(f"✅ Alpaca connection successful!")
            print(f"   Account status: {account.status}")
            print(f"   Portfolio value: ${float(account.portfolio_value):,.2f}")
            print(f"   Buying power: ${float(account.buying_power):,.2f}")
            return True
        except Exception as e:
            print(f"❌ Alpaca connection failed: {e}")
            return False
    
    def get_account(self):
        """Get account information."""
        return self.api.get_account()
    
    def get_price(self, symbol):
        """Get current price for a symbol."""
        try:
            quote = self.api.get_latest_trade(symbol)
            return float(quote.price)
        except Exception as e:
            print(f"❌ Error getting price for {symbol}: {e}")
            return None
    
    def get_bars(self, symbol, timeframe='1Day', limit=100):
        """
        Get historical bars (OHLCV data).
        
        Args:
            symbol (str): Stock symbol
            timeframe (str): '1Min', '5Min', '15Min', '1Hour', '1Day'
            limit (int): Number of bars to fetch
        
        Returns:
            pandas.DataFrame: OHLCV data
        """
        try:
            # Get bars
            bars = self.api.get_bars(
                symbol,
                timeframe,
                limit=limit
            ).df
            
            # Rename columns to match your bot's format
            bars = bars.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            return bars
        
        except Exception as e:
            print(f"❌ Error getting bars for {symbol}: {e}")
            return None
    
    def get_position(self, symbol):
        """Get current position for a symbol."""
        try:
            position = self.api.get_position(symbol)
            return {
                'symbol': symbol,
                'qty': float(position.qty),
                'avg_entry_price': float(position.avg_entry_price),
                'market_value': float(position.market_value),
                'unrealized_pl': float(position.unrealized_pl),
                'unrealized_plpc': float(position.unrealized_plpc)
            }
        except:
            return None  # No position
    
    def get_all_positions(self):
        """Get all open positions."""
        try:
            positions = self.api.list_positions()
            return [{
                'symbol': p.symbol,
                'qty': float(p.qty),
                'avg_entry_price': float(p.avg_entry_price),
                'market_value': float(p.market_value),
                'unrealized_pl': float(p.unrealized_pl),
                'unrealized_plpc': float(p.unrealized_plpc)
            } for p in positions]
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def buy(self, symbol, qty=None, notional=None):
        """
        Place a BUY order.
        
        Args:
            symbol (str): Stock symbol
            qty (int): Number of shares (optional)
            notional (float): Dollar amount to buy (optional)
        
        Returns:
            dict: Order details
        """
        try:
            if qty:
                # Buy specific number of shares
                order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            elif notional:
                # Buy dollar amount
                order = self.api.submit_order(
                    symbol=symbol,
                    notional=notional,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            else:
                raise ValueError("Must provide either qty or notional")
            
            print(f"✅ BUY order placed: {symbol}")
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'status': order.status
            }
        
        except Exception as e:
            print(f"❌ Error placing BUY order for {symbol}: {e}")
            return None
    
    def sell(self, symbol, qty=None):
        """
        Place a SELL order.
        
        Args:
            symbol (str): Stock symbol
            qty (int): Number of shares (optional, defaults to all)
        
        Returns:
            dict: Order details
        """
        try:
            if qty is None:
                # Sell all shares
                position = self.get_position(symbol)
                if not position:
                    print(f"⚠️  No position to sell for {symbol}")
                    return None
                qty = abs(int(position['qty']))
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
            
            print(f"✅ SELL order placed: {symbol}")
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'status': order.status
            }
        
        except Exception as e:
            print(f"❌ Error placing SELL order for {symbol}: {e}")
            return None
    
    def get_orders(self, status='all', limit=50):
        """Get recent orders."""
        try:
            orders = self.api.list_orders(status=status, limit=limit)
            return [{
                'id': o.id,
                'symbol': o.symbol,
                'qty': o.qty,
                'side': o.side,
                'type': o.type,
                'status': o.status,
                'filled_qty': o.filled_qty,
                'filled_avg_price': o.filled_avg_price
            } for o in orders]
        except Exception as e:
            print(f"❌ Error getting orders: {e}")
            return []
    
    def cancel_all_orders(self):
        """Cancel all open orders."""
        try:
            self.api.cancel_all_orders()
            print("✅ All orders cancelled")
            return True
        except Exception as e:
            print(f"❌ Error cancelling orders: {e}")
            return False
    
    def get_portfolio_value(self):
        """Get total portfolio value."""
        try:
            account = self.api.get_account()
            return float(account.portfolio_value)
        except Exception as e:
            print(f"❌ Error getting portfolio value: {e}")
            return 0.0
    
    def get_buying_power(self):
        """Get available buying power."""
        try:
            account = self.api.get_account()
            return float(account.buying_power)
        except Exception as e:
            print(f"❌ Error getting buying power: {e}")
            return 0.0


# Test function
def test_alpaca():
    """Test Alpaca integration."""
    print("\n" + "="*60)
    print("🧪 TESTING ALPACA INTEGRATION")
    print("="*60)
    
    try:
        trader = AlpacaTrader()
        
        # Test connection
        print("\n1️⃣ Testing connection...")
        trader.test_connection()
        
        # Get account info
        print("\n2️⃣ Getting account info...")
        account = trader.get_account()
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Portfolio value: ${float(account.portfolio_value):,.2f}")
        
        # Get current price
        print("\n3️⃣ Getting current price...")
        price = trader.get_price('AAPL')
        print(f"   AAPL price: ${price:.2f}")
        
        # Get historical data
        print("\n4️⃣ Getting historical data...")
        bars = trader.get_bars('AAPL', '1Day', 10)
        if bars is not None:
            print(f"   Got {len(bars)} bars")
            print(f"   Latest close: ${bars['Close'].iloc[-1]:.2f}")
        
        # Get positions
        print("\n5️⃣ Getting positions...")
        positions = trader.get_all_positions()
        print(f"   Open positions: {len(positions)}")
        for pos in positions:
            print(f"   - {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
        
        print("\n" + "="*60)
        print("✅ ALPACA INTEGRATION WORKING!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    test_alpaca()
