

import pandas as pd
import requests
from unittest.mock import patch, Mock
from src.siegfried import find_hidden_cheap_goods_in_rubbish as fhc

def get_top_k_companies(k=100):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url, headers=headers)
    sp500 = pd.read_html(response.content)[0]
    tickers = sp500['Symbol'].tolist()[:k]
    return [ticker.replace('.', '-') for ticker in tickers]

@patch('requests.get')
@patch('pandas.read_html')
def test_download_top_ticker(mock_read_html, mock_requests_get):
    # Mock the requests.get response
    mock_response = Mock()
    mock_response.content = b"<html>mock content</html>"
    mock_requests_get.return_value = mock_response
    mock_df = pd.DataFrame({
        'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'] * 20
    })
    mock_read_html.return_value = [mock_df]
    tickers = fhc.get_top_k_companies(100)
    assert 0 < len(tickers) <= 100
    assert isinstance(tickers, list)
