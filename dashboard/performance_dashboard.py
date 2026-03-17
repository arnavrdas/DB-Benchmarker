"""
Streamlit Dashboard for Database Performance Comparison
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import psutil
import os
import json

# Database connections
import psycopg2
from pymongo import MongoClient
import redis

# Page config
st.set_page_config(
    page_title="Database Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

class PerformanceTester:
    def __init__(self):
        self.setup_connections()
        self.results = []
    
    def setup_connections(self):
        """Setup database connections"""
        self.connections = {}
        
        # PostgreSQL
        try:
            self.connections['PostgreSQL'] = {
                'conn': psycopg2.connect(
                    host='localhost',
                    database='perfdb',
                    user='admin',
                    password='admin123',
                    port=5432
                ),
                'type': 'sql'
            }
        except Exception as e:
            st.error(f"PostgreSQL connection failed: {e}")
        
        # MongoDB
        try:
            mongo_client = MongoClient('mongodb://admin:admin123@localhost:27017/')
            self.connections['MongoDB'] = {
                'conn': mongo_client,
                'db': mongo_client['perfdb']
            }
        except Exception as e:
            st.error(f"MongoDB connection failed: {e}")
        
        # Redis
        try:
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                password='admin123',
                decode_responses=True
            )
            self.connections['Redis'] = {
                'conn': redis_client
            }
        except Exception as e:
            st.error(f"Redis connection failed: {e}")
    
    def get_system_metrics(self):
        """Get current system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters() if psutil.disk_io_counters() else None,
            'network_io': psutil.net_io_counters() if psutil.net_io_counters() else None
        }
    
    def test_postgresql(self, filter_type, filter_value):
        """Test PostgreSQL query performance"""
        start_time = time.time()
        metrics_before = self.get_system_metrics()
        
        try:
            cursor = self.connections['PostgreSQL']['conn'].cursor()
            
            if filter_type == 'user_id':
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = %s", (int(filter_value),))
            elif filter_type == 'category':
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE product_category = %s", (filter_value,))
            elif filter_type == 'date_range':
                dates = filter_value.split(' to ')
                cursor.execute("""
                    SELECT COUNT(*) FROM transactions 
                    WHERE transaction_date BETWEEN %s AND %s
                """, (dates[0], dates[1]))
            elif filter_type == 'amount':
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE total_amount > %s", (float(filter_value),))
            
            result = cursor.fetchone()[0]
            
            end_time = time.time()
            metrics_after = self.get_system_metrics()
            
            return {
                'database': 'PostgreSQL',
                'query_time': end_time - start_time,
                'records_found': result,
                'cpu_change': metrics_after['cpu_percent'] - metrics_before['cpu_percent'],
                'memory_change': metrics_after['memory_percent'] - metrics_before['memory_percent']
            }
        except Exception as e:
            return {
                'database': 'PostgreSQL',
                'query_time': time.time() - start_time,
                'error': str(e),
                'records_found': 0
            }
    
    def test_mongodb(self, filter_type, filter_value):
        """Test MongoDB query performance"""
        start_time = time.time()
        metrics_before = self.get_system_metrics()
        
        try:
            collection = self.connections['MongoDB']['db']['transactions']
            
            if filter_type == 'user_id':
                query = {'user_id': int(filter_value)}
            elif filter_type == 'category':
                query = {'product_category': filter_value}
            elif filter_type == 'date_range':
                dates = filter_value.split(' to ')
                query = {
                    'transaction_date': {
                        '$gte': dates[0],
                        '$lte': dates[1]
                    }
                }
            elif filter_type == 'amount':
                query = {'total_amount': {'$gt': float(filter_value)}}
            
            count = collection.count_documents(query)
            
            end_time = time.time()
            metrics_after = self.get_system_metrics()
            
            return {
                'database': 'MongoDB',
                'query_time': end_time - start_time,
                'records_found': count,
                'cpu_change': metrics_after['cpu_percent'] - metrics_before['cpu_percent'],
                'memory_change': metrics_after['memory_percent'] - metrics_before['memory_percent']
            }
        except Exception as e:
            return {
                'database': 'MongoDB',
                'query_time': time.time() - start_time,
                'error': str(e),
                'records_found': 0
            }
    
    def test_redis(self, filter_type, filter_value):
        """Test Redis query performance"""
        start_time = time.time()
        metrics_before = self.get_system_metrics()
        
        try:
            redis_client = self.connections['Redis']['conn']
            
            if filter_type == 'user_id':
                # Get all transactions for user
                keys = redis_client.smembers(f"user:{filter_value}:transactions")
                count = len(keys)
            elif filter_type == 'category':
                keys = redis_client.smembers(f"category:{filter_value}:transactions")
                count = len(keys)
            else:
                # For other filters, we'd need to scan (simplified)
                count = 0
            
            end_time = time.time()
            metrics_after = self.get_system_metrics()
            
            return {
                'database': 'Redis',
                'query_time': end_time - start_time,
                'records_found': count,
                'cpu_change': metrics_after['cpu_percent'] - metrics_before['cpu_percent'],
                'memory_change': metrics_after['memory_percent'] - metrics_before['memory_percent']
            }
        except Exception as e:
            return {
                'database': 'Redis',
                'query_time': time.time() - start_time,
                'error': str(e),
                'records_found': 0
            }
    
    def run_test(self, filter_type, filter_value):
        """Run performance test on all databases"""
        results = []
        
        if 'PostgreSQL' in self.connections:
            results.append(self.test_postgresql(filter_type, filter_value))
        
        if 'MongoDB' in self.connections:
            results.append(self.test_mongodb(filter_type, filter_value))
        
        if 'Redis' in self.connections:
            results.append(self.test_redis(filter_type, filter_value))
        
        return results

# Initialize tester
tester = PerformanceTester()

# Dashboard UI
st.title("📊 Database Performance Comparison Dashboard")
st.markdown("Compare query performance across PostgreSQL, MongoDB, and Redis")

# Sidebar for filters
st.sidebar.header("Query Filters")

filter_type = st.sidebar.selectbox(
    "Filter by",
    ["user_id", "category", "date_range", "amount"]
)

filter_value = None
if filter_type == "user_id":
    filter_value = st.sidebar.number_input("User ID", min_value=1000, max_value=9999, value=5000)
elif filter_type == "category":
    filter_value = st.sidebar.selectbox(
        "Category",
        ["Electronics", "Clothing", "Books", "Home", "Sports"]
    )
elif filter_type == "date_range":
    today = datetime.now()
    start_date = st.sidebar.date_input("Start Date", today - timedelta(days=30))
    end_date = st.sidebar.date_input("End Date", today)
    filter_value = f"{start_date} to {end_date}"
elif filter_type == "amount":
    filter_value = st.sidebar.number_input("Min Amount", min_value=10, max_value=5000, value=100)

# Run test button
if st.sidebar.button("Run Performance Test", type="primary"):
    with st.spinner("Running queries across all databases..."):
        results = tester.run_test(filter_type, filter_value)
        
        # Display results
        st.header("Test Results")
        
        # Create metrics DataFrame
        results_df = pd.DataFrame(results)
        
        # Query time comparison
        col1, col2, col3 = st.columns(3)
        
        for idx, row in results_df.iterrows():
            with col1 if idx == 0 else col2 if idx == 1 else col3:
                db = row['database']
                time_ms = row['query_time'] * 1000
                
                # Color code based on performance
                if time_ms < 10:
                    color = "green"
                elif time_ms < 50:
                    color = "orange"
                else:
                    color = "red"
                
                st.metric(
                    label=f"{db} - {row['records_found']:,} records",
                    value=f"{time_ms:.2f} ms",
                    delta=f"CPU: {row.get('cpu_change', 0):.1f}%",
                    delta_color="off"
                )
        
        # Bar chart comparison
        st.subheader("Query Time Comparison (lower is better)")
        fig = px.bar(
            results_df,
            x='database',
            y='query_time',
            color='database',
            title="Query Execution Time by Database",
            labels={'query_time': 'Time (seconds)', 'database': 'Database'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Records found comparison
        st.subheader("Records Retrieved")
        fig2 = px.pie(
            results_df,
            values='records_found',
            names='database',
            title="Distribution of Records Found"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed results table
        st.subheader("Detailed Results")
        st.dataframe(results_df)

# System metrics
st.header("System Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("CPU Usage", f"{psutil.cpu_percent()}%")
with col2:
    st.metric("Memory Usage", f"{psutil.virtual_memory().percent}%")
with col3:
    st.metric("Disk Usage", f"{psutil.disk_usage('/').percent}%")

# Database status
st.header("Database Status")
status_cols = st.columns(3)

databases = ['PostgreSQL', 'MongoDB', 'Redis']
for idx, db in enumerate(databases):
    with status_cols[idx]:
        if db in tester.connections:
            st.success(f"✅ {db}: Connected")
        else:
            st.error(f"❌ {db}: Disconnected")

# Instructions
with st.expander("How to use this dashboard"):
    st.markdown("""
    1. **Select a filter type** from the sidebar (user_id, category, date_range, or amount)
    2. **Enter the filter value** based on your selection
    3. **Click "Run Performance Test"** to execute queries across all databases
    4. **View results** showing:
       - Query execution time for each database
       - Number of records found
       - CPU and memory impact
    5. **Compare performance** using the charts and metrics
    
    The dashboard automatically connects to your local databases running in Docker.
    """)

# Run the app
if __name__ == "__main__":
    # Note: Run with: streamlit run dashboard/performance_dashboard.py
    pass