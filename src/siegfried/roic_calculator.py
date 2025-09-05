import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
from typing import Tuple, Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_financial_statements(ticker: str) -> Tuple[Any, Any]:
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet
    income_statement = stock.financials
    return balance_sheet, income_statement

def extract_financial_variables(balance_sheet: Any, income_statement: Any) -> Dict[str, float]:
    latest_balance_sheet = balance_sheet.iloc[:, 0]
    latest_income = income_statement.iloc[:, 0]
    
    return {
        'operating_income': latest_income.get('Operating Income', 0),
        'tax_expense': latest_income.get('Tax Provision', 0),
        'pretax_income': latest_income.get('Pretax Income', latest_income.get('Operating Income', 0)),
        'total_assets': latest_balance_sheet.get('Total Assets', 0),
        'cash': latest_balance_sheet.get('Cash And Cash Equivalents', 0),
        'current_liabilities': latest_balance_sheet.get('Current Liabilities', 0)
    }

def extract_financial_variables_multi_year(balance_sheet: Any, income_statement: Any) -> List[Dict[str, Any]]:
    """Extract financial variables for multiple years"""
    yearly_data = []
    
    # Get common years between balance sheet and income statement
    common_years = balance_sheet.columns.intersection(income_statement.columns)
    
    for year in common_years:
        bs_year = balance_sheet[year]
        is_year = income_statement[year]
        
        yearly_data.append({
            'year': year,
            'operating_income': is_year.get('Operating Income', 0),
            'tax_expense': is_year.get('Tax Provision', 0),
            'pretax_income': is_year.get('Pretax Income', is_year.get('Operating Income', 0)),
            'total_assets': bs_year.get('Total Assets', 0),
            'cash': bs_year.get('Cash And Cash Equivalents', 0),
            'current_liabilities': bs_year.get('Current Liabilities', 0)
        })
    
    return yearly_data

def chose_most_recent_k_years(yearly_data: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    """Choose the most recent k years from yearly financial data"""
    return sorted(yearly_data, key=lambda x: x['year'], reverse=True)[:k]

def calculate_invested_capital(total_assets: float, cash: float, current_liabilities: float) -> float:
    return total_assets - cash - current_liabilities

def calculate_nopat(operating_income: float, tax_expense: float, pretax_income: float) -> float:
    if pretax_income != 0:
        tax_rate = tax_expense / pretax_income
    else:
        tax_rate = 0.25
    return operating_income * (1 - tax_rate)

def derive_roic(nopat: float, invested_capital: float) -> float:
    if invested_capital != 0:
        return nopat / invested_capital
    else:
        return None

def calculate_roic(ticker: str) -> dict:
    try:
        balance_sheet, income_statement = get_financial_statements(ticker)
        
        if balance_sheet.empty or income_statement.empty:
            return {"ticker": ticker, "roic": None, "error": "No financial data available"}
        
        variables = extract_financial_variables(balance_sheet, income_statement)
        
        invested_capital = calculate_invested_capital(
            variables['total_assets'], 
            variables['cash'], 
            variables['current_liabilities']
        )
        
        nopat = calculate_nopat(
            variables['operating_income'], 
            variables['tax_expense'], 
            variables['pretax_income']
        )
        
        roic = derive_roic(nopat, invested_capital)
        
        return {
            "ticker": ticker,
            "roic": roic,
        }
        
    except Exception as e:
        return {"ticker": ticker, "roic": None, "error": str(e)}

def prepare_plot_data(result: Dict[str, Any]) -> Tuple[List[int], List[float]]:
    """Prepare and filter data for plotting"""
    if 'error' in result or not result['roic_data']:
        return [], []
    
    data = result['roic_data']
    years_list = [d['year'].year for d in data]
    roic_values = [d['roic'] * 100 if d['roic'] is not None else None for d in data]
    
    filtered_data = [(y, r) for y, r in zip(years_list, roic_values) if r is not None]
    if not filtered_data:
        return [], []
    
    years_clean, roic_clean = zip(*filtered_data)
    return list(years_clean), list(roic_clean)

def create_main_plot(ticker: str, years_clean: List[int], roic_clean: List[float]) -> None:
    """Create the main ROIC time series plot"""
    plt.subplot(2, 1, 1)
    plt.plot(years_clean, roic_clean, 'bo-', linewidth=2, markersize=8, label='ROIC')
    plt.title(f'{ticker} - Return on Invested Capital (ROIC) Time Series', fontsize=14, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('ROIC (%)')
    plt.grid(True, alpha=0.3)
    plt.legend()

def add_trend_line(years_clean: List[int], roic_clean: List[float]) -> None:
    """Add trend line to the main plot"""
    if len(years_clean) > 1:
        z = np.polyfit(years_clean, roic_clean, 1)
        p = np.poly1d(z)
        plt.plot(years_clean, p(years_clean), "r--", alpha=0.7, label='Trend')
        plt.legend()

def create_statistical_subplot(years_clean: List[int], roic_clean: List[float]) -> None:
    """Create the statistical analysis subplot"""
    plt.subplot(2, 1, 2)
    plt.bar(range(len(roic_clean)), roic_clean, alpha=0.7, color='skyblue')
    plt.title('ROIC Distribution', fontsize=12)
    plt.xlabel('Period')
    plt.ylabel('ROIC (%)')
    plt.xticks(range(len(years_clean)), years_clean)

def add_statistical_lines(roic_clean: List[float]) -> Tuple[float, float]:
    """Add statistical reference lines and return mean and std"""
    mean_roic = np.mean(roic_clean)
    std_roic = np.std(roic_clean)
    plt.axhline(y=mean_roic, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_roic:.2f}%')
    plt.axhline(y=mean_roic + std_roic, color='orange', linestyle=':', alpha=0.5, label=f'+1σ: {mean_roic + std_roic:.2f}%')
    plt.axhline(y=mean_roic - std_roic, color='orange', linestyle=':', alpha=0.5, label=f'-1σ: {mean_roic - std_roic:.2f}%')
    plt.legend()
    return mean_roic, std_roic

def log_summary_statistics(ticker: str, roic_clean: List[float], mean_roic: float, std_roic: float) -> None:
    """Log summary statistics for ROIC data"""
    logger.info(f"\n{ticker} ROIC Summary Statistics:")
    logger.info(f"Mean ROIC: {mean_roic:.2f}%")
    logger.info(f"Standard Deviation: {std_roic:.2f}%")
    logger.info(f"Volatility (CV): {(std_roic/abs(mean_roic)*100):.2f}%")
    logger.info(f"Min ROIC: {min(roic_clean):.2f}%")
    logger.info(f"Max ROIC: {max(roic_clean):.2f}%")
    logger.info(f"Range: {max(roic_clean) - min(roic_clean):.2f}%")

def calculate_roic_multi_year(ticker: str, years: int = 4) -> Dict[str, Any]:
    """Calculate ROIC for multiple years"""
    try:
        balance_sheet, income_statement = get_financial_statements(ticker)
        
        if balance_sheet.empty or income_statement.empty:
            return {"ticker": ticker, "roic_data": [], "error": "No financial data available"}
        
        yearly_data = extract_financial_variables_multi_year(balance_sheet, income_statement)
        yearly_data = chose_most_recent_k_years(yearly_data, years)
        
        roic_results = []
        for data in yearly_data:
            invested_capital = calculate_invested_capital(
                data['total_assets'], 
                data['cash'], 
                data['current_liabilities']
            )
            
            nopat = calculate_nopat(
                data['operating_income'], 
                data['tax_expense'], 
                data['pretax_income']
            )
            
            roic = derive_roic(nopat, invested_capital)
            
            roic_results.append({
                'year': data['year'],
                'roic': roic,
                'nopat': nopat,
                'invested_capital': invested_capital
            })
        
        return {
            "ticker": ticker,
            "roic_data": sorted(roic_results, key=lambda x: x['year'])
        }
        
    except Exception as e:
        return {"ticker": ticker, "roic_data": [], "error": str(e)}

def plot_roic_time_series(ticker: str, years: int = 4, save_plot: bool = False) -> None:
    """Plot ROIC as a time series to visualize as stochastic process"""
    result = calculate_roic_multi_year(ticker, years)
    
    years_clean, roic_clean = prepare_plot_data(result)
    
    if not years_clean:
        error_msg = result.get('error', 'No data available') if 'error' in result else 'No valid ROIC data found'
        logger.error(f"Error calculating ROIC for {ticker}: {error_msg}")
        return
    
    plt.figure(figsize=(12, 8))
    
    create_main_plot(ticker, years_clean, roic_clean)
    add_trend_line(years_clean, roic_clean)
    
    create_statistical_subplot(years_clean, roic_clean)
    mean_roic, std_roic = add_statistical_lines(roic_clean)
    
    plt.savefig(f'{ticker}_roic_analysis.png', dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved as {ticker}_roic_analysis.png")
    log_summary_statistics(ticker, roic_clean, mean_roic, std_roic)

if __name__ == "__main__":
    logger.info("Single year ROIC calculation:")
    logger.info(calculate_roic("UNH"))
    logger.info("Multi-year ROIC calculation:")
    result = calculate_roic_multi_year("UNH", 4)
    logger.info(result)
    # for data in result['roic_data']:
    #     roic_pct = data['roic'] * 100 if data['roic'] is not None else None
    #     print(f"{data['year'].year}: {roic_pct:.2f}%" if roic_pct else f"{data['year'].year}: N/A")
    # print("\nGenerating ROIC visualization...")
    # plot_roic_time_series("UNH", 4)