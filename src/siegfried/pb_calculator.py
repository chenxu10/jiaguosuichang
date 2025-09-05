import yfinance as yf


def calculate_pb(symbol):
    """
    Calculate the price-to-book ratio for a given stock symbol.
    
    Args:
        symbol (str): Stock ticker symbol
        
    Returns:
        float: Price-to-book ratio (current price / book value per share)
        None: If data cannot be retrieved
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        
        # Get book value per share
        book_value = info.get('bookValue')
        
        if current_price and book_value and book_value > 0:
            pb_ratio = current_price / book_value
            return pb_ratio
        else:
            return None
            
    except Exception as e:
        print(f"Error calculating P/B ratio for {symbol}: {e}")
        return None