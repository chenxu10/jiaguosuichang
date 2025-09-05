
import yfinance as yf
import pandas as pd
import requests

def get_top_k_companies(k=100):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url, headers=headers)
    sp500 = pd.read_html(response.content)[0]
    tickers = sp500['Symbol'].tolist()[:k]
    return [ticker.replace('.', '-') for ticker in tickers]
