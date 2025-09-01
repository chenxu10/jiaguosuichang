from src.siegfried import roic_calculator as rc


def test_calculate_roic():
    ticker = "UNH"
    assert rc.calculate_roic(ticker) == {}