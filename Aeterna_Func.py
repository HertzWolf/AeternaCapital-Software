import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def Generate_Data():
    # Valid assets and transaction types
    assets_valid = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    types_valid = ['Buy', 'Sell']
    
    # Invalid assets, types, and dates for generating dirty data
    bad_assets = ['', None, 123, 'NFLX', '']
    bad_types = ['Hold', '', None, 'Purchase', 123]
    bad_dates = ['yesterday', '2022-02-30', 'not a date', '2023-15-01', '', None]
    
    # Function to generate valid data rows
    def generate_valid_row():
        return {
            'Asset': random.choice(assets_valid),
            'Quantity': random.randint(1, 100),  # Random integer for Quantity
            'Price': round(random.uniform(100, 1500), 2),  # Random price in a reasonable range
            'Date': (datetime.today() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),  # Random valid date within the last year
            'Type': random.choice(types_valid)  # Randomly choosing between Buy or Sell
        }
    
    # Function to generate dirty data rows (invalid, missing, or incorrect values)
    def generate_dirty_row():
        return {
            'Asset': random.choice(assets_valid + bad_assets),  # May include invalid assets
            'Quantity': random.choice([random.randint(-50, 100), 'twenty', None, '', 20.5]),  # May include negative, invalid, or missing quantities
            'Price': random.choice([round(random.uniform(-200, 10000000), 2), 'free', 'NaN', None]),  # May include negative or non-numeric prices
            'Date': random.choice(bad_dates + [
                (datetime.today() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
            ]),  # May include invalid dates or None
            'Type': random.choice(types_valid + bad_types)  # May include invalid transaction types
        }
    
    # Generate 10 valid rows and 20 dirty rows
    rows = [generate_valid_row() for _ in range(10)]  # 10 valid rows
    rows += [generate_dirty_row() for _ in range(20)]  # 20 dirty rows
    random.shuffle(rows)  # Shuffle to mix valid and dirty rows
    
    # Convert the list of rows into a DataFrame and return it
    df = pd.DataFrame(rows)
    return df

