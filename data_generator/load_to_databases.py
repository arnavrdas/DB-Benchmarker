"""
Load the generated data into all databases
"""
import pandas as pd
import psycopg2
from pymongo import MongoClient
import redis
from sqlalchemy import create_engine
import time
import json
from datetime import datetime

class DatabaseLoader:
    def __init__(self, csv_file='ecommerce_transactions.csv'):
        print(f"Loading data from {csv_file}...")
        self.df = pd.read_csv(csv_file)
        
        # Parse transaction_date back to datetime
        self.df['transaction_date'] = pd.to_datetime(self.df['transaction_date'])
        
        print(f"Loaded {len(self.df):,} records")
        
        # Database connections
        self.connections = {}
        self.setup_connections()
    
    def setup_connections(self):
        """Setup connections to all databases"""
        
        # PostgreSQL connection
        try:
            self.connections['postgresql'] = {
                'conn': psycopg2.connect(
                    host='localhost',
                    database='perfdb',
                    user='admin',
                    password='admin123',
                    port=5432
                ),
                'type': 'sql'
            }
            print("✓ Connected to PostgreSQL")
        except Exception as e:
            print(f"✗ PostgreSQL connection failed: {e}")
        
        # MongoDB connection
        try:
            mongo_client = MongoClient(
                'mongodb://admin:admin123@localhost:27017/'
            )
            self.connections['mongodb'] = {
                'conn': mongo_client,
                'db': mongo_client['perfdb'],
                'type': 'nosql'
            }
            print("✓ Connected to MongoDB")
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
        
        # Redis connection
        try:
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                password='admin123',
                decode_responses=True
            )
            self.connections['redis'] = {
                'conn': redis_client,
                'type': 'key-value'
            }
            print("✓ Connected to Redis")
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
    
    def load_to_postgresql(self):
        """Load data to PostgreSQL"""
        print("\n--- Loading to PostgreSQL ---")
        start_time = time.time()
        
        try:
            # Create SQLAlchemy engine
            engine = create_engine('postgresql://admin:admin123@localhost:5432/perfdb')
            
            # Drop table if exists
            with self.connections['postgresql']['conn'].cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS transactions")
            
            # Load data in chunks
            chunk_size = 50000
            for i in range(0, len(self.df), chunk_size):
                chunk = self.df.iloc[i:i+chunk_size]
                chunk.to_sql('transactions', engine, if_exists='append', index=False)
                print(f"  Loaded chunk {i//chunk_size + 1}: {len(chunk)} records")
            
            # Create indexes
            with self.connections['postgresql']['conn'].cursor() as cursor:
                cursor.execute("CREATE INDEX idx_user_id ON transactions(user_id)")
                cursor.execute("CREATE INDEX idx_transaction_date ON transactions(transaction_date)")
                cursor.execute("CREATE INDEX idx_product_category ON transactions(product_category)")
                self.connections['postgresql']['conn'].commit()
            
            end_time = time.time()
            print(f"✓ PostgreSQL load completed in {end_time - start_time:.2f} seconds")
            
            # Get row count
            with self.connections['postgresql']['conn'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM transactions")
                count = cursor.fetchone()[0]
                print(f"  Total records in PostgreSQL: {count:,}")
                
        except Exception as e:
            print(f"✗ PostgreSQL load failed: {e}")
    
    def load_to_mongodb(self):
        """Load data to MongoDB"""
        print("\n--- Loading to MongoDB ---")
        start_time = time.time()
        
        try:
            db = self.connections['mongodb']['db']
            
            # Drop existing collection
            db.transactions.drop()
            
            # Convert DataFrame to dictionaries
            records = self.df.to_dict('records')
            
            # Convert datetime objects to ISO format for MongoDB
            for record in records:
                record['transaction_date'] = record['transaction_date'].isoformat()
            
            # Insert in chunks
            chunk_size = 50000
            collection = db['transactions']
            
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i+chunk_size]
                collection.insert_many(chunk)
                print(f"  Loaded chunk {i//chunk_size + 1}: {len(chunk)} records")
            
            # Create indexes
            collection.create_index('user_id')
            collection.create_index('transaction_date')
            collection.create_index('product_category')
            
            end_time = time.time()
            print(f"✓ MongoDB load completed in {end_time - start_time:.2f} seconds")
            print(f"  Total records in MongoDB: {collection.count_documents({}):,}")
            
        except Exception as e:
            print(f"✗ MongoDB load failed: {e}")
    
    def load_to_redis(self):
        """Load data to Redis"""
        print("\n--- Loading to Redis ---")
        start_time = time.time()
        
        try:
            redis_client = self.connections['redis']['conn']
            
            # Clear existing data
            redis_client.flushdb()
            
            # Store data in different Redis structures
            
            # 1. Store as hash for each transaction
            print("  Loading transaction hashes...")
            for idx, row in self.df.iterrows():
                key = f"transaction:{row['transaction_id']}"
                
                # Convert row to dict, handle datetime
                data = row.to_dict()
                data['transaction_date'] = data['transaction_date'].isoformat()
                
                # Store as hash
                redis_client.hset(key, mapping=data)
                
                # Add to sets for different indexes
                redis_client.sadd(f"user:{row['user_id']}:transactions", key)
                redis_client.sadd(f"category:{row['product_category']}:transactions", key)
                redis_client.sadd(f"date:{data['transaction_date'][:10]}:transactions", key)
                
                if idx % 10000 == 0:
                    print(f"    Processed {idx:,} records...")
            
            end_time = time.time()
            print(f"✓ Redis load completed in {end_time - start_time:.2f} seconds")
            
            # Get stats
            total_keys = len(redis_client.keys('transaction:*'))
            print(f"  Total transaction keys in Redis: {total_keys:,}")
            
        except Exception as e:
            print(f"✗ Redis load failed: {e}")
    
    def load_all(self):
        """Load data to all databases"""
        print("="*50)
        print("Starting data load to all databases")
        print("="*50)
        
        if 'postgresql' in self.connections:
            self.load_to_postgresql()
        
        if 'mongodb' in self.connections:
            self.load_to_mongodb()
        
        if 'redis' in self.connections:
            self.load_to_redis()
        
        print("\n" + "="*50)
        print("Data loading complete!")
        print("="*50)

if __name__ == "__main__":
    loader = DatabaseLoader('ecommerce_transactions.csv')
    loader.load_all()