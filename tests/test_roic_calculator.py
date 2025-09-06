from pprint import pprint
from src.siegfried import roic_calculator as rc

def test_calculate_nopat():
    # Test with normal values
    operating_income = 1000
    tax_expense = 200
    pretax_income = 800
    expected_nopat = operating_income * (1 - (tax_expense / pretax_income))  # 1000 * (1 - 0.25) = 750
    assert rc.calculate_nopat(operating_income, tax_expense, pretax_income) == expected_nopat
    
    # Test with zero pretax income (should use default tax rate of 0.25)
    operating_income = 1000
    tax_expense = 200
    pretax_income = 0
    expected_nopat = operating_income * (1 - 0.25)  # 1000 * 0.75 = 750
    assert rc.calculate_nopat(operating_income, tax_expense, pretax_income) == expected_nopat
    
    # Test with zero tax expense
    operating_income = 1000
    tax_expense = 0
    pretax_income = 1000
    expected_nopat = operating_income * (1 - 0)  # 1000 * 1 = 1000
    assert rc.calculate_nopat(operating_income, tax_expense, pretax_income) == expected_nopat



if __name__ == "__main__":
    #print(rc.calculate_roic("MRNA"))
    #pprint(rc.calculate_roic_multi_year("MRNA",4))
    rc.plot_roic_time_series("DECK", 4)