import yfinance as yf

def calculate_pb(symbol):
    """
    Calculate the price-to-book ratio for a given stock symbol.
    
    Args:
        symbol (str): Stock ticker symbol
        
    Returns:
        float: Price-to-book ratio
        None: If data cannot be retrieved
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current stock price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not current_price:
            return None
            
        # First try using priceToBook field directly
        pb_ratio = info.get('priceToBook')
        if pb_ratio and pb_ratio > 0.01:  # Filter out obviously wrong values like 0.001
            return pb_ratio
        
        # Fallback: Calculate from balance sheet data
        try:
            balance_sheet = ticker.quarterly_balance_sheet
            if not balance_sheet.empty:
                # Look for stockholders equity
                equity_keys = [key for key in balance_sheet.index if 'Common Stock Equity' in key or 'Stockholders Equity' in key]
                if equity_keys:
                    latest_equity = balance_sheet.loc[equity_keys[0]].iloc[0]
                    shares_outstanding = info.get('sharesOutstanding')
                    if latest_equity and shares_outstanding and shares_outstanding > 0:
                        book_value_per_share = latest_equity / shares_outstanding
                        if book_value_per_share > 0:
                            return current_price / book_value_per_share
        except Exception:
            pass  # Continue to next fallback
        
        # Final fallback: manual calculation using bookValue field (if it seems reasonable)
        book_value = info.get('bookValue')
        if current_price and book_value and book_value > 0:
            # Check if bookValue looks like a per-share value (reasonable range)
            if book_value < current_price * 10:  # Heuristic: book value shouldn't be more than 10x price
                pb_ratio = current_price / book_value
                return pb_ratio
        
        return None
            
    except Exception as e:
        print(f"Error calculating P/B ratio for {symbol}: {e}")
        return None