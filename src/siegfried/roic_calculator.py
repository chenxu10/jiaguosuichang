import yfinance as yf

def calculate_roic(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        balance_sheet = stock.balance_sheet
        return balance_sheet
        #balance_sheet.to_csv("unh_balansheet.csv")
        #print(balance_sheet)
        #if balance_sheet.empty:
        #    return {"ticker": ticker, "roic": None, "error": "No financial data available"}
    except Exception as e:
        roic = 9999
        return {'tikcer':ticker,'roic':roic,'e':e}
    

if __name__ == "__main__":
    calculate_roic("UNH")