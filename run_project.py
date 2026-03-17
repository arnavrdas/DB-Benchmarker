#!/usr/bin/env python3
"""
Main script to run the entire project
"""
import subprocess
import time
import os
import sys

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def run_command(command, description):
    """Run a shell command and print output"""
    print(f"\n▶ {description}...")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    
    if result.returncode == 0:
        print(f"✓ Success: {description}")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"✗ Failed: {description}")
        print(result.stderr)
        return False
    return True

def main():
    print_header("DATABASE PERFORMANCE DASHBOARD SETUP")
    
    # Step 1: Check if Docker is installed
    print_header("STEP 1: Checking Docker Installation")
    docker_check = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
    
    if docker_check.returncode != 0:
        print("✗ Docker not found. Please install Docker first.")
        print("Run: sudo apt install docker.io docker-compose-plugin")
        sys.exit(1)
    else:
        print(f"✓ Docker found: {docker_check.stdout.strip()}")
    
    # Step 2: Start Docker containers
    print_header("STEP 2: Starting Databases with Docker Compose")
    run_command("docker-compose up -d", "Starting database containers")
    
    # Wait for databases to be ready
    print("\n⏳ Waiting for databases to be ready...")
    time.sleep(10)
    
    # Step 3: Install Python requirements
    print_header("STEP 3: Installing Python Requirements")
    run_command("pip install -r requirements.txt", "Installing Python packages")
    
    # Step 4: Generate data
    print_header("STEP 4: Generating 1 Million Records")
    run_command("cd data_generator && python generate_data.py", "Generating dataset")
    
    # Step 5: Load data to databases
    print_header("STEP 5: Loading Data to All Databases")
    run_command("cd data_generator && python load_to_databases.py", "Loading data")
    
    # Step 6: Start dashboard
    print_header("STEP 6: Starting Performance Dashboard")
    print("\n✅ Setup complete! Starting dashboard...")
    print("\n📊 Dashboard will be available at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the dashboard\n")
    
    # Run streamlit dashboard
    os.system("streamlit run dashboard/performance_dashboard.py")

if __name__ == "__main__":
    main()