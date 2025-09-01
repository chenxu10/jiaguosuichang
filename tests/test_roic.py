import pytest
from src.siegfried import roic_calculator as rc

def test_calculate_roic():
    ticker = "UNH"
    assert isinstance(rc.calculate_roic(ticker),dict)


def test_yf_exception():
    with pytest.raises(Exception):
        rc.calculate_roic()