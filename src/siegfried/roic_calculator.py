def calculate_roic(ticker: str) -> dict:
    try:
        a = 2
    except Exception as e:
        roic = 9999
        return {'tikcer':ticker,'roic':roic,'e':e}