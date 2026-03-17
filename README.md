# Multi-Database Performance Dashboard

A comprehensive performance comparison dashboard for PostgreSQL, MongoDB, and Redis. Generate 1 million records and compare query performance across different databases with real-time metrics visualization.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements
- **Ubuntu 20.04 or 22.04** (or any Linux distribution)
- **At least 8GB RAM** (16GB recommended for 1M records)
- **10GB free disk space**
- **Internet connection** (for downloading dependencies)

### Required Software
- **Python 3.8+** (check with `python3 --version`)
- **pip** (check with `pip3 --version`)
- **Docker & Docker Compose** (will be installed in setup)

### Port Availability
Ensure these ports are free:
- `5432` - PostgreSQL
- `27017` - MongoDB
- `6379` - Redis
- `8501` - Streamlit Dashboard
- `5050` - pgAdmin (optional)
- `8081` - Mongo Express (optional)
- `8082` - Redis Commander (optional)

## 🚀 Quick Start (5 minutes)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/arnavrdas/DB-Benchmarker.git
cd db-performance-dashboard

# Make the run script executable
chmod +x run_project.py
```

### Step 2: Install Docker (if not installed)

```bash
# Run the Docker installation script
./scripts/install_docker.sh
# OR install manually:
sudo apt update
sudo apt install docker.io docker-compose-plugin -y
sudo usermod -aG docker $USER
newgrp docker
```

### Step 3: Run the Project

```bash
# This single command will:
# - Start all databases in Docker
# - Install Python dependencies
# - Generate 1 million records
# - Load data into all databases
# - Launch the dashboard
python run_project.py
```

### Step 4: Access the Dashboard

Open your browser and navigate to: http://localhost:8501