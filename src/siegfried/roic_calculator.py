def calculate_roic(ticker: str) -> dict:
    try:
        return {}
    except Exception as e:
        roic = 9999
        return {'tikcer':ticker,'roic':roic,'e':e}