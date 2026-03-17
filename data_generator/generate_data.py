"""
Data Generator for Performance Testing
Generates 1 million records with realistic e-commerce data
"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import time
import os

class DataGenerator:
    def __init__(self, num_records=1000000):
        self.num_records = num_records
        self.fake = Faker()
        # Set seed for reproducibility
        Faker.seed(42)
        np.random.seed(42)
        random.seed(42)
        
    def generate_dataset(self):
        """Generate 1 million records of e-commerce transactions"""
        print(f"Generating {self.num_records:,} records...")
        start_time = time.time()
        
        # Generate data in chunks to manage memory
        chunk_size = 100000
        num_chunks = self.num_records // chunk_size
        
        all_data = []
        
        for chunk_num in range(num_chunks):
            print(f"Generating chunk {chunk_num + 1}/{num_chunks}")
            
            # Generate chunk data
            chunk_data = {
                'transaction_id': [str(self.fake.uuid4()) for _ in range(chunk_size)],
                'user_id': [self.fake.random_int(min=1000, max=9999) for _ in range(chunk_size)],
                'product_id': [f"PROD_{self.fake.random_int(min=100, max=999)}" for _ in range(chunk_size)],
                'product_category': [random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports']) for _ in range(chunk_size)],
                'price': [round(random.uniform(10, 1000), 2) for _ in range(chunk_size)],
                'quantity': [random.randint(1, 5) for _ in range(chunk_size)],
                'total_amount': [0] * chunk_size,  # Will calculate
                'payment_method': [random.choice(['Credit Card', 'PayPal', 'Debit Card', 'Cash']) for _ in range(chunk_size)],
                'transaction_date': [self.fake.date_time_between(start_date='-1y', end_date='now') for _ in range(chunk_size)],
                'customer_country': [self.fake.country() for _ in range(chunk_size)],
                'customer_city': [self.fake.city() for _ in range(chunk_size)],
                'is_returned': [random.random() < 0.05 for _ in range(chunk_size)],  # 5% returns
                'rating': [random.randint(1, 5) if random.random() < 0.7 else None for _ in range(chunk_size)]  # 70% rated
            }
            
            # Create DataFrame for this chunk
            chunk_df = pd.DataFrame(chunk_data)
            
            # Calculate total amount
            chunk_df['total_amount'] = chunk_df['price'] * chunk_df['quantity']
            
            all_data.append(chunk_df)
        
        # Combine all chunks
        final_df = pd.concat(all_data, ignore_index=True)
        
        end_time = time.time()
        print(f"Data generation completed in {end_time - start_time:.2f} seconds")
        print(f"Generated {len(final_df):,} records with {len(final_df.columns)} columns")
        print(f"Memory usage: {final_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return final_df
    
    def save_to_csv(self, df, filename='dataset.csv'):
        """Save dataset to CSV"""
        print(f"Saving to {filename}...")
        df.to_csv(filename, index=False)
        print(f"Saved {len(df):,} records to {filename}")
        return filename

# Main execution
if __name__ == "__main__":
    generator = DataGenerator(num_records=1000000)  # 1 million records
    df = generator.generate_dataset()
    
    # Save to CSV
    csv_file = generator.save_to_csv(df, 'ecommerce_transactions.csv')
    
    # Display sample
    print("\nSample data (first 5 rows):")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)