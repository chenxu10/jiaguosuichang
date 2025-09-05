from src.siegfried import pb_calculator as pc

def test_calculate_pb():
    expected_brkb_price_book_current = 1.64
    print(pc.calculate_pb("UNH"))
    
    
    #assert pc.calculate_pb("BRK-B") == expected_brkb_price_book_current

    # expected_brkb_price_book_current = 2.97
    # assert pc.calculate_pb("UNH") == expected_brkb_price_book_current



if __name__ == "__main__":
    test_calculate_pb()