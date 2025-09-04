import yfinance as yf

def calculate_roic(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        balance_sheet = stock.balance_sheet
        income_statement = stock.financials
        
        if balance_sheet.empty or income_statement.empty:
            return {"ticker": ticker, "roic": None, "error": "No financial data available"}
        
        # Get the most recent year's data (first column)
        latest_balance_sheet = balance_sheet.iloc[:, 0]
        latest_income = income_statement.iloc[:, 0]
        
        # Calculate NOPAT (Net Operating Profit After Tax)
        # NOPAT = Operating Income * (1 - Tax Rate)
        operating_income = latest_income.get('Operating Income', 0)
        tax_expense = latest_income.get('Tax Provision', 0)
        pretax_income = latest_income.get('Pretax Income', operating_income)
        
        # Calculate effective tax rate
        if pretax_income != 0:
            tax_rate = tax_expense / pretax_income
        else:
            tax_rate = 0.25  # Default assumption
            
        nopat = operating_income * (1 - tax_rate)
        
        # Calculate Invested Capital
        # Invested Capital = Total Assets - Cash - Non-interest bearing current liabilities
        total_assets = latest_balance_sheet.get('Total Assets', 0)
        cash = latest_balance_sheet.get('Cash And Cash Equivalents', 0)
        
        # For simplicity, we'll use Total Current Liabilities as proxy for non-interest bearing current liabilities
        current_liabilities = latest_balance_sheet.get('Current Liabilities', 0)
        
        invested_capital = total_assets - cash - current_liabilities
        
        # Calculate ROIC
        if invested_capital != 0:
            roic = nopat / invested_capital
        else:
            roic = None
            
        return {
            "ticker": ticker,
            "roic": roic,
            "nopat": nopat,
            "invested_capital": invested_capital,
            "operating_income": operating_income,
            "tax_rate": tax_rate
        }
        
    except Exception as e:
        return {"ticker": ticker, "roic": None, "error": str(e)}
    

if __name__ == "__main__":
    print(calculate_roic("UNH"))