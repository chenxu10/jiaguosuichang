# YFinance Framework Guide

## Overview
YFinance is a Python library that provides a simple interface to download market data from Yahoo Finance.

## Key Classes and Methods

### Ticker Class
The main class for accessing stock data:

```python
import yfinance as yf
ticker = yf.Ticker('AAPL')
```

### Important Properties

#### `info` - Comprehensive stock information
- Contains detailed company information
- Key financial metrics available:
  - `priceToBook`: Price-to-book ratio (direct calculation)
  - `bookValue`: Book value per share  
  - `currentPrice`: Current stock price
  - `marketCap`: Market capitalization
  - Company details like sector, industry, employees, etc.

#### `fast_info` - Quick access to basic metrics
- Lightweight access to key metrics:
  - `lastPrice`: Most recent price
  - `marketCap`: Market capitalization
  - `dayHigh`, `dayLow`: Daily price range
  - `yearHigh`, `yearLow`: 52-week range
  - `shares`: Outstanding shares

### Financial Statements
- `balance_sheet`: Annual balance sheet data
- `income_stmt`: Annual income statement
- `cash_flow`: Annual cash flow statement
- `quarterly_*`: Quarterly versions of above

### Historical Data
- `history()`: Historical price and volume data
- `dividends`: Dividend history
- `splits`: Stock split history

## Key Finding for P/B Calculator
The `info` property contains a `priceToBook` field that directly provides the price-to-book ratio, eliminating the need to calculate it manually from `currentPrice / bookValue`.

## Usage Pattern
```python
import yfinance as yf

ticker = yf.Ticker('SYMBOL')
pb_ratio = ticker.info.get('priceToBook')
```

## Other Useful Classes
- `Tickers`: Handle multiple tickers at once
- `Lookup`: Search for tickers by name
- `EquityQuery`/`FundQuery`: Advanced screening capabilities
- `Market`: Market status and summary information