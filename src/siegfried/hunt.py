import yfinance as yf

TICKERS = ["VZ", "BRK-B", "PDD", "TLT", "GLD", "SPY"]
THRESHOLD = 1.5


def hunt_unusual_movers(tickers=TICKERS, threshold=THRESHOLD):
    hits = find_anomalies(tickers, threshold)
    report(hits)


def find_anomalies(tickers, threshold):
    anomalies = []
    for symbol in tickers:
        anomaly = detect_anomaly(symbol, threshold)
        if anomaly:
            anomalies.append(anomaly)
    return anomalies


def detect_anomaly(symbol, threshold):
    returns = daily_returns(symbol)
    if returns is None:
        return None
    z = z_score(returns)
    if abs(z) < threshold:
        return None
    return symbol, returns.iloc[-1] * 100, z


def daily_returns(symbol, min_days=30):
    hist = yf.Ticker(symbol).history(period="max")
    if len(hist) < min_days:
        return None
    return opening_gap(hist)


def opening_gap(hist):
    return (hist["Open"] / hist["Close"].shift(1) - 1).dropna()


def z_score(returns):
    return (returns.iloc[-1] - returns.mean()) / returns.std()


def report(hits):
    if not hits:
        print("nothing unusual")
        return
    for sym, chg, z in hits:
        print(f"{sym:6s}  {chg:+.2f}%  (z={z:+.2f})")


if __name__ == "__main__":
    hunt_unusual_movers()
