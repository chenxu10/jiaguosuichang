import pytest
from src.siegfried import roic_calculator as rc

def test_calculate_roic():


    actual_roic = calculate_roic(net_profit_after_tax/invested_capital)
    assert actual_roic == 100 / 90000000
    ticker = "UNH"
    assert isinstance(rc.calculate_roic(ticker),dict)