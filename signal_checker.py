"""
SIGNAL_CHECKER.PY - Diagnostic Tool
====================================
Shows you exactly what signals are being generated and why.

Usage:
    python signal_checker.py
"""

import config
from model import TradingModel
import pandas as pd


def check_signals():
    """Check signals for all symbols and show details."""
    print("\n" + "="*60)
    print("🔍 SIGNAL DIAGNOSTIC TOOL")
    print("="*60)
    print(f"\nChecking {len(config.SYMBOLS)} symbols...")
    print(f"Strategies enabled: {[k for k, v in config.STRATEGIES_ENABLED.items() if v]}")
    print(f"Vote requirement: {config.STRATEGY_VOTE_REQUIRED}")
    print("="*60)
    
    model = TradingModel()
    signals_found = 0
    
    for symbol in config.SYMBOLS:
        print(f"\n📊 Analyzing {symbol}...")
        
        try:
            # Fetch data
            model.fetch_market_data(symbol)
            model.calculate_all_indicators(symbol)
            
            df = model.market_data.get(symbol)
            if df is None or df.empty:
                print(f"   ❌ No data available for {symbol}")
                continue
            
            current = df.iloc[-1]
            
            # Show current values
            print(f"   Price: ${current['Close']:.2f}")
            print(f"   MA Fast: ${current.get('MA_Fast', 0):.2f}")
            print(f"   MA Slow: ${current.get('MA_Slow', 0):.2f}")
            print(f"   RSI: {current.get('RSI', 0):.2f}")
            
            # Check individual strategies
            votes = []
            
            if config.STRATEGIES_ENABLED.get('ma_crossover'):
                ma_signal = model.detect_crossover(symbol)
                votes.append(('MA Crossover', ma_signal))
                emoji = "🟢" if ma_signal == 'BUY' else "🔴" if ma_signal == 'SELL' else "⚪"
                print(f"   {emoji} MA Crossover: {ma_signal}")
            
            if config.STRATEGIES_ENABLED.get('rsi'):
                rsi = current.get('RSI', 50)
                if rsi < 30:
                    rsi_signal = 'BUY'
                elif rsi > 70:
                    rsi_signal = 'SELL'
                else:
                    rsi_signal = 'HOLD'
                votes.append(('RSI', rsi_signal))
                emoji = "🟢" if rsi_signal == 'BUY' else "🔴" if rsi_signal == 'SELL' else "⚪"
                print(f"   {emoji} RSI: {rsi_signal} (value: {rsi:.1f})")
            
            if config.STRATEGIES_ENABLED.get('macd'):
                macd_signal = model.check_macd_signal(symbol)
                votes.append(('MACD', macd_signal))
                emoji = "🟢" if macd_signal == 'BUY' else "🔴" if macd_signal == 'SELL' else "⚪"
                print(f"   {emoji} MACD: {macd_signal}")
            
            if config.STRATEGIES_ENABLED.get('bollinger'):
                bb_signal = model.check_bollinger_signal(symbol)
                votes.append(('Bollinger', bb_signal))
                emoji = "🟢" if bb_signal == 'BUY' else "🔴" if bb_signal == 'SELL' else "⚪"
                print(f"   {emoji} Bollinger: {bb_signal}")
            
            if config.STRATEGIES_ENABLED.get('volume'):
                vol_ok = model.check_volume_confirmation(symbol)
                vol_signal = 'BUY' if vol_ok else 'HOLD'
                votes.append(('Volume', vol_signal))
                emoji = "🟢" if vol_signal == 'BUY' else "⚪"
                print(f"   {emoji} Volume: {vol_signal}")
            
            # Final signal
            final_signal = model.generate_multi_strategy_signal(symbol)
            
            # Count votes
            buy_votes = sum(1 for _, v in votes if v == 'BUY')
            sell_votes = sum(1 for _, v in votes if v == 'SELL')
            
            print(f"\n   📊 Vote Count: BUY={buy_votes}, SELL={sell_votes}")
            print(f"   📊 Requirement: {config.STRATEGY_VOTE_REQUIRED}")
            
            # Final signal
            if final_signal == 'BUY':
                print(f"   ✅ FINAL: 🟢 BUY SIGNAL!")
                signals_found += 1
            elif final_signal == 'SELL':
                print(f"   ✅ FINAL: 🔴 SELL SIGNAL!")
                signals_found += 1
            else:
                print(f"   ⚪ FINAL: HOLD (not enough agreement)")
                
                # Explain why
                if config.STRATEGY_VOTE_REQUIRED == 'all':
                    print(f"   💡 Reason: Need ALL strategies to agree, but they don't")
                elif config.STRATEGY_VOTE_REQUIRED == 'majority':
                    needed = len([v for v in votes if v]) // 2 + 1
                    print(f"   💡 Reason: Need {needed} strategies to agree")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 SUMMARY")
    print("="*60)
    print(f"Symbols analyzed: {len(config.SYMBOLS)}")
    print(f"Signals found: {signals_found}")
    
    if signals_found == 0:
        print("\n⚠️  NO SIGNALS FOUND")
        print("\nPossible reasons:")
        print("1. Market conditions don't match strategy criteria")
        print("2. Voting requirement too strict (try 'any' for testing)")
        print("3. No clear trends right now")
        print("4. Need to wait for market to move")
        print("\n💡 Suggestion: Try changing STRATEGY_VOTE_REQUIRED to 'any' in config.py")
    else:
        print(f"\n✅ Found {signals_found} signal(s)!")
        print("🎯 Your bot is working correctly!")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    check_signals()
