"""
SECTOR_VIEWER.PY - View Available Sectors and Symbols
======================================================
This utility helps you explore available stocks and sectors.

Usage:
    python sector_viewer.py                  # Show all sectors
    python sector_viewer.py tech             # Show tech stocks
    python sector_viewer.py current          # Show currently configured stocks
"""

import sys
import config


def display_sector(sector_name, symbols):
    """Display stocks in a sector."""
    print(f"\n{'='*60}")
    print(f"  {sector_name.upper()}")
    print(f"{'='*60}")
    print(f"Total Stocks: {len(symbols)}\n")
    
    # Display in columns
    for i in range(0, len(symbols), 4):
        row = symbols[i:i+4]
        print("  ".join(f"{sym:6}" for sym in row))
    
    print(f"\n{'='*60}\n")


def show_all_sectors():
    """Show all available sectors."""
    print("\n" + "="*60)
    print("  📊 AVAILABLE SECTORS AND STOCKS")
    print("="*60)
    
    sectors = {
        "Technology / IT": config.TECH_SYMBOLS,
        "Semiconductors / Chips": config.CHIP_SYMBOLS,
        "Healthcare": config.HEALTHCARE_SYMBOLS,
        "Pharmaceuticals": config.PHARMA_SYMBOLS,
        "Financial Services": config.FINANCE_SYMBOLS,
        "Energy": config.ENERGY_SYMBOLS,
        "Consumer / Retail": config.CONSUMER_SYMBOLS
    }
    
    for sector_name, symbols in sectors.items():
        print(f"\n{sector_name} ({len(symbols)} stocks)")
        print("-" * 60)
        
        # Show first 10 stocks
        display_symbols = symbols[:10]
        for i in range(0, len(display_symbols), 5):
            row = display_symbols[i:i+5]
            print("  " + "  ".join(f"{sym:6}" for sym in row))
        
        if len(symbols) > 10:
            print(f"  ... and {len(symbols) - 10} more")
    
    print("\n" + "="*60)
    print("\nTo see detailed sector info:")
    print("  python sector_viewer.py tech")
    print("  python sector_viewer.py healthcare")
    print("  python sector_viewer.py chips")
    print("="*60 + "\n")


def show_current_config():
    """Show currently configured symbols."""
    print("\n" + "="*60)
    print("  📈 CURRENTLY CONFIGURED SYMBOLS")
    print("="*60)
    print(f"\nTotal Stocks: {len(config.SYMBOLS)}")
    print(f"Initial Capital: ${config.INITIAL_CAPITAL}")
    print(f"\nSymbols:")
    print("-" * 60)
    
    for i in range(0, len(config.SYMBOLS), 5):
        row = config.SYMBOLS[i:i+5]
        print("  " + "  ".join(f"{sym:6}" for sym in row))
    
    print("\n" + "="*60)
    print("\nStrategy Parameters:")
    print(f"  Fast MA: {config.MA_FAST_PERIOD} periods")
    print(f"  Slow MA: {config.MA_SLOW_PERIOD} periods")
    print(f"  RSI: {config.RSI_PERIOD} periods ({config.RSI_OVERSOLD}/{config.RSI_OVERBOUGHT})")
    print(f"  Stop Loss: {config.STOP_LOSS_PERCENT*100}%")
    print(f"  Take Profit: {config.TAKE_PROFIT_PERCENT*100}%")
    print("="*60 + "\n")


def show_sector_details(sector_key):
    """Show detailed info for a specific sector."""
    sectors_map = {
        'tech': ("Technology / IT", config.TECH_SYMBOLS),
        'technology': ("Technology / IT", config.TECH_SYMBOLS),
        'it': ("Technology / IT", config.TECH_SYMBOLS),
        
        'chip': ("Semiconductors / Chips", config.CHIP_SYMBOLS),
        'chips': ("Semiconductors / Chips", config.CHIP_SYMBOLS),
        'semiconductor': ("Semiconductors / Chips", config.CHIP_SYMBOLS),
        'semiconductors': ("Semiconductors / Chips", config.CHIP_SYMBOLS),
        
        'health': ("Healthcare", config.HEALTHCARE_SYMBOLS),
        'healthcare': ("Healthcare", config.HEALTHCARE_SYMBOLS),
        
        'pharma': ("Pharmaceuticals", config.PHARMA_SYMBOLS),
        'pharmaceutical': ("Pharmaceuticals", config.PHARMA_SYMBOLS),
        'pharmaceuticals': ("Pharmaceuticals", config.PHARMA_SYMBOLS),
        
        'finance': ("Financial Services", config.FINANCE_SYMBOLS),
        'financial': ("Financial Services", config.FINANCE_SYMBOLS),
        'bank': ("Financial Services", config.FINANCE_SYMBOLS),
        'banks': ("Financial Services", config.FINANCE_SYMBOLS),
        
        'energy': ("Energy", config.ENERGY_SYMBOLS),
        'oil': ("Energy", config.ENERGY_SYMBOLS),
        
        'consumer': ("Consumer / Retail", config.CONSUMER_SYMBOLS),
        'retail': ("Consumer / Retail", config.CONSUMER_SYMBOLS),
    }
    
    sector_key = sector_key.lower()
    
    if sector_key in sectors_map:
        sector_name, symbols = sectors_map[sector_key]
        display_sector(sector_name, symbols)
        
        # Show how to use in config
        print("To trade these stocks, add to config.py:")
        print("-" * 60)
        
        sector_var = {
            "Technology / IT": "TECH_SYMBOLS",
            "Semiconductors / Chips": "CHIP_SYMBOLS",
            "Healthcare": "HEALTHCARE_SYMBOLS",
            "Pharmaceuticals": "PHARMA_SYMBOLS",
            "Financial Services": "FINANCE_SYMBOLS",
            "Energy": "ENERGY_SYMBOLS",
            "Consumer / Retail": "CONSUMER_SYMBOLS"
        }[sector_name]
        
        print(f"\n# Trade top 5 from {sector_name}")
        print(f"SYMBOLS = {sector_var}[:5]\n")
        
        print(f"# Trade all {len(symbols)} stocks")
        print(f"SYMBOLS = {sector_var}\n")
        
        print(f"# Trade specific stocks")
        print(f"SYMBOLS = ['{symbols[0]}', '{symbols[1]}', '{symbols[2]}']\n")
        
        print("="*60 + "\n")
    else:
        print(f"\n❌ Unknown sector: {sector_key}")
        print("\nAvailable sectors:")
        print("  tech, chips, healthcare, pharma, finance, energy, consumer")
        print("\nUsage: python sector_viewer.py <sector_name>\n")


def show_statistics():
    """Show overall statistics."""
    total_symbols = (len(config.TECH_SYMBOLS) + 
                    len(config.CHIP_SYMBOLS) + 
                    len(config.HEALTHCARE_SYMBOLS) + 
                    len(config.PHARMA_SYMBOLS) + 
                    len(config.FINANCE_SYMBOLS) + 
                    len(config.ENERGY_SYMBOLS) + 
                    len(config.CONSUMER_SYMBOLS))
    
    print("\n" + "="*60)
    print("  📊 TRADING BOT STATISTICS")
    print("="*60)
    print(f"\nTotal Available Stocks: {total_symbols}")
    print(f"Currently Configured: {len(config.SYMBOLS)}")
    print(f"Available Sectors: 7")
    print("\nSector Breakdown:")
    print(f"  • Technology/IT:         {len(config.TECH_SYMBOLS)} stocks")
    print(f"  • Semiconductors/Chips:  {len(config.CHIP_SYMBOLS)} stocks")
    print(f"  • Healthcare:            {len(config.HEALTHCARE_SYMBOLS)} stocks")
    print(f"  • Pharmaceuticals:       {len(config.PHARMA_SYMBOLS)} stocks")
    print(f"  • Financial Services:    {len(config.FINANCE_SYMBOLS)} stocks")
    print(f"  • Energy:                {len(config.ENERGY_SYMBOLS)} stocks")
    print(f"  • Consumer/Retail:       {len(config.CONSUMER_SYMBOLS)} stocks")
    print("="*60 + "\n")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        # No arguments - show all sectors
        show_all_sectors()
        show_statistics()
    else:
        command = sys.argv[1].lower()
        
        if command in ['current', 'config', 'configured']:
            show_current_config()
        
        elif command in ['stats', 'statistics', 'info']:
            show_statistics()
        
        elif command in ['help', '-h', '--help']:
            print("\n" + "="*60)
            print("  SECTOR VIEWER - HELP")
            print("="*60)
            print("\nCommands:")
            print("  python sector_viewer.py              # Show all sectors")
            print("  python sector_viewer.py current      # Show current config")
            print("  python sector_viewer.py stats        # Show statistics")
            print("  python sector_viewer.py tech         # Show tech stocks")
            print("  python sector_viewer.py chips        # Show chip stocks")
            print("  python sector_viewer.py healthcare   # Show healthcare stocks")
            print("  python sector_viewer.py pharma       # Show pharma stocks")
            print("  python sector_viewer.py finance      # Show finance stocks")
            print("  python sector_viewer.py energy       # Show energy stocks")
            print("  python sector_viewer.py consumer     # Show consumer stocks")
            print("="*60 + "\n")
        
        else:
            # Try to show specific sector
            show_sector_details(command)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Viewer stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
