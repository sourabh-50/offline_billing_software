import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

def test_sync():
    database.init_db()
    
    # Add test stock
    model = "TEST-MODEL-X"
    database.add_stock(model, "IMEI123", 10, 1000.0)
    
    # Check initial stock
    stock = [s for s in database.get_all_stock() if s[1] == model]
    print(f"Initial Stock: {stock[0][3]}")
    
    # Decrement with different case
    database.decrement_stock(model.lower())
    
    # Check after decrement
    stock = [s for s in database.get_all_stock() if s[1] == model]
    print(f"Stock after lowercase decrement: {stock[0][3]}")
    
    if stock[0][3] == 9:
        print("Sync Test Passed!")
    else:
        print("Sync Test Failed!")

if __name__ == "__main__":
    test_sync()
