import yfinance as yf

def calculate_roic(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        print(balance_sheet)
        if income_stmt.empty or balance_sheet.empty:
            return {"ticker": ticker, "roic": None, "error": "No financial data available"}
    except Exception as e:
        roic = 9999
        return {'tikcer':ticker,'roic':roic,'e':e}