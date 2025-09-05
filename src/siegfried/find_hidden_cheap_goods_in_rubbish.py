"""
This is an implementation of Mark Spitznagel's Dao of Capital Chapter 10 idea

Idea is to find companies with high 10 year rolling average of return on invested capital
and low p/b

Author: xu.shen<xs286@cornell.edu>

TODO: The BRKB's calculation is not correct and needs to modify
"""

import pandas as pd
import requests
import logging
from datetime import date
from typing import List, Dict, Any
from tqdm import tqdm
from src.siegfried.roic_calculator import calculate_roic_multi_year
from src.siegfried.pb_calculator import calculate_pb

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_top_k_companies(k=100):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url, headers=headers)
    sp500 = pd.read_html(response.content)[0]
    tickers = sp500['Symbol'].tolist()[:k]
    return [ticker.replace('.', '-') for ticker in tickers]

def load_all_symbols(k=100) -> List[str]:
    return get_top_k_companies(k)

def calculate_four_year_rolling_roic(ticker: str) -> Dict[str, Any]:
    return calculate_roic_multi_year(ticker, years=4)

def validate_input_values(values: List[float]) -> bool:
    if not values or any(v is None for v in values):
        return False
    return True

def filter_valid_values(values: List[float]) -> List[float]:
    valid_values = [v for v in values if v is not None and v > 0]
    return valid_values

def calculate_geometric_mean(valid_values: List[float]) -> float:
    product = 1.0
    for value in valid_values:
        product *= (1 + value)
    
    return (product ** (1.0 / len(valid_values))) - 1

def compute_geometric_average(values: List[float]) -> float:
    if not validate_input_values(values):
        return None
    
    valid_values = filter_valid_values(values)
    if not valid_values:
        return None
    
    return calculate_geometric_mean(valid_values)

def append_geometric_mean_roic_results(results, ticker, roic_values):
    if len(roic_values) >= 2:
        geo_avg_roic = compute_geometric_average(roic_values)
        results.append({
                        'Symbol': ticker,
                        '4Y_Geometric_Avg_ROIC': geo_avg_roic,
                        'Status': 'Success',
                        'Years_Available': len(roic_values)
                    })
    else:
        results.append({
                        'Symbol': ticker,
                        '4Y_Geometric_Avg_ROIC': None,
                        'Status': f'Insufficient Data ({len(roic_values)} years)'
                    })
        
def process_all_symbols_and_build_table(symbols: List[str]) -> pd.DataFrame:
    results = []
    
    for ticker in tqdm(symbols, desc="Analyzing symbols", unit="symbol"):
        try:
            roic_data = calculate_four_year_rolling_roic(ticker)
            if 'error' in roic_data or not roic_data.get('roic_data'):
                results.append({
                    'Symbol': ticker,
                    '4Y_Geometric_Avg_ROIC': None,
                    'Status': 'Error/No Data'
                })
            else:
                roic_values = [d['roic'] for d in roic_data['roic_data'] if d['roic'] is not None]
                append_geometric_mean_roic_results(results, ticker, roic_values)
                
        except Exception as e:
            results.append({
                'Symbol': ticker,
                '4Y_Geometric_Avg_ROIC': None,
                'Status': f'Error: {str(e)}'
            })
    
    return pd.DataFrame(results)

def apply_pb_calculator_to_all_symbols(result_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply pb_calculator's calculate_pb function to all symbols in result_df.
    
    Args:
        result_df (pd.DataFrame): DataFrame containing symbols with ROIC analysis results
        
    Returns:
        pd.DataFrame: DataFrame with added P/B ratio column
    """
    pb_ratios = []
    
    for symbol in tqdm(result_df['Symbol'], desc="Calculating P/B ratios", unit="symbol"):
        try:
            pb_ratio = calculate_pb(symbol)
            pb_ratios.append(pb_ratio)
        except Exception as e:
            logger.warning(f"Failed to calculate P/B ratio for {symbol}: {e}")
            pb_ratios.append(None)
    
    result_df['PB_Ratio'] = pb_ratios
    return result_df

def main_roic_analysis(k=100) -> pd.DataFrame:
    def format_geometric_mean_roic_to_percentage(df):
        df['4Y_Geometric_Avg_ROIC_Pct'] = df['4Y_Geometric_Avg_ROIC'].apply(lambda x: f"{x*100:.2f}%" if x is not None else "N/A")
        return df
    
    def sort_by_pb_and_roic(df):
        df_sorted = df.sort_values(['PB_Ratio', '4Y_Geometric_Avg_ROIC'], 
                                 ascending=[True, False], na_position='last')
        return df_sorted
    
    symbols = load_all_symbols(k)
    logger.info(f"Analyzing {len(symbols)} symbols for 4-year rolling geometric average ROIC...")
    
    df = process_all_symbols_and_build_table(symbols)
    df = apply_pb_calculator_to_all_symbols(df)
    df = format_geometric_mean_roic_to_percentage(df)
    df = sort_by_pb_and_roic(df)
    return df

if __name__ == "__main__":
    results_df = main_roic_analysis(499)
    logger.info("\n4-Year Rolling Geometric Average ROIC Analysis")
    logger.info("=" * 60)
    #logger.info(f"\n{results_df[['Symbol', '4Y_Geometric_Avg_ROIC_Pct', 'Years_Available', 'Status']].head(20).to_string()}")
    logger.info(f"\n{results_df[['Symbol', '4Y_Geometric_Avg_ROIC', 'PB_Ratio', 'Years_Available', 'Status']].head(20).to_string()}")
    
    successful_analysis = results_df[results_df['Status'] == 'Success']
    successful_analysis.to_csv("src/report/high_roic_company_{}.csv".format(date.today().strftime("%Y%m%d")))
    logger.info(f"Successfully analyzed: {len(successful_analysis)} out of {len(results_df)} symbols")