"""
SYMBOL_LOADER.PY - Load symbols from external file
===================================================
Reads symbols from symbols.txt file for easy management.
"""

import os


def load_symbols_from_file(filename='symbols.txt'):
    """
    Load stock symbols from a text file.
    
    File format:
    - One symbol per line
    - Lines starting with # are comments (ignored)
    - Empty lines are ignored
    - Symbols are automatically uppercase
    
    Args:
        filename (str): Path to symbols file
    
    Returns:
        list: List of stock symbols
    """
    symbols = []
    
    if not os.path.exists(filename):
        print(f"⚠️  Warning: {filename} not found!")
        print(f"Creating default symbols.txt file...")
        create_default_symbols_file(filename)
        return load_symbols_from_file(filename)
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Remove whitespace and comments
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Extract symbol (in case there's inline comment)
                symbol = line.split('#')[0].strip().upper()
                
                if symbol:
                    symbols.append(symbol)
        
        print(f"✅ Loaded {len(symbols)} symbols from {filename}")
        return symbols
    
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return []


def create_default_symbols_file(filename='symbols.txt'):
    """Create a default symbols.txt file."""
    default_content = """# SYMBOLS.TXT - Your Stock Watchlist
# ====================================
# Add one symbol per line
# Lines starting with # are comments (ignored)

# Default symbols
AAPL
MSFT
GOOGL
NVDA
TSLA

# Add more symbols below:
# AMD
# INTC
# META
"""
    
    try:
        with open(filename, 'w') as f:
            f.write(default_content)
        print(f"✅ Created default {filename}")
    except Exception as e:
        print(f"❌ Error creating {filename}: {e}")


def add_symbol(symbol, filename='symbols.txt'):
    """
    Add a symbol to the file.
    
    Args:
        symbol (str): Symbol to add
        filename (str): Path to symbols file
    """
    symbol = symbol.strip().upper()
    
    # Check if already exists
    existing = load_symbols_from_file(filename)
    if symbol in existing:
        print(f"⚠️  {symbol} already in list")
        return False
    
    try:
        with open(filename, 'a') as f:
            f.write(f"\n{symbol}\n")
        print(f"✅ Added {symbol} to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error adding symbol: {e}")
        return False


def remove_symbol(symbol, filename='symbols.txt'):
    """
    Remove a symbol from the file (by commenting it out).
    
    Args:
        symbol (str): Symbol to remove
        filename (str): Path to symbols file
    """
    symbol = symbol.strip().upper()
    
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines:
            if line.strip().upper() == symbol:
                new_lines.append(f"# {line}")  # Comment out
                modified = True
            else:
                new_lines.append(line)
        
        if modified:
            with open(filename, 'w') as f:
                f.writelines(new_lines)
            print(f"✅ Removed (commented out) {symbol}")
            return True
        else:
            print(f"⚠️  {symbol} not found in list")
            return False
    
    except Exception as e:
        print(f"❌ Error removing symbol: {e}")
        return False


def list_symbols(filename='symbols.txt'):
    """Display all symbols from file."""
    symbols = load_symbols_from_file(filename)
    
    if symbols:
        print(f"\n📊 Active Symbols ({len(symbols)}):")
        print("=" * 40)
        for i, symbol in enumerate(symbols, 1):
            print(f"{i:2}. {symbol}")
        print("=" * 40)
    else:
        print("⚠️  No active symbols found")
    
    return symbols


# Command-line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("\nSymbol Manager Commands:")
        print("========================")
        print("python symbol_loader.py list           - Show all symbols")
        print("python symbol_loader.py add AAPL       - Add symbol")
        print("python symbol_loader.py remove AAPL    - Remove symbol")
        print("python symbol_loader.py check          - Validate symbols")
        print()
        list_symbols()
    
    else:
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_symbols()
        
        elif command == 'add' and len(sys.argv) > 2:
            symbol = sys.argv[2]
            add_symbol(symbol)
            list_symbols()
        
        elif command == 'remove' and len(sys.argv) > 2:
            symbol = sys.argv[2]
            remove_symbol(symbol)
            list_symbols()
        
        elif command == 'check':
            symbols = load_symbols_from_file()
            print(f"\n✅ Found {len(symbols)} valid symbols")
            list_symbols()
        
        else:
            print(f"❌ Unknown command: {command}")
