import yfinance as yf

def calculate_manually_using_bookvalue(info, cr_prc):
    book_value = info.get('bookValue')
    if cr_prc and book_value and book_value > 0:
        if book_value < cr_prc * 10:  
            pb_ratio = cr_prc / book_value
            return pb_ratio
        else:
            return None
    else:
        return None    

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
            
        pb_ratio = info.get('priceToBook')
        if pb_ratio and pb_ratio > 0.01:
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
        
        pb_ratio = calculate_manually_using_bookvalue(info, current_price)
        return None
            
    except Exception as e:
        print(f"Error calculating P/B ratio for {symbol}: {e}")
        return None