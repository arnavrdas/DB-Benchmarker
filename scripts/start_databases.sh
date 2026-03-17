#!/bin/bash

echo "Starting databases..."

# Stop and remove any existing containers
docker stop perf_postgres perf_mongodb perf_redis 2>/dev/null
docker rm perf_postgres perf_mongodb perf_redis 2>/dev/null

# Start PostgreSQL
echo "Starting PostgreSQL..."
docker run -d \
  --name perf_postgres \
  -e POSTGRES_DB=perfdb \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin123 \
  -p 5432:5432 \
  postgres:15

# Start MongoDB
echo "Starting MongoDB..."
docker run -d \
  --name perf_mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  -e MONGO_INITDB_DATABASE=perfdb \
  -p 27017:27017 \
  mongo:6

# Start Redis
echo "Starting Redis..."
docker run -d \
  --name perf_redis \
  -p 6379:6379 \
  redis:7-alpine redis-server --requirepass admin123

echo "Waiting for databases to be ready..."
sleep 10

# Test connections
echo "Testing connections..."
docker exec perf_postgres pg_isready -U admin -d perfdb && echo "✓ PostgreSQL ready"
docker exec perf_mongodb mongosh -u admin -p admin123 --eval "db.runCommand({ping:1})" && echo "✓ MongoDB ready"
docker exec perf_redis redis-cli -a admin123 ping && echo "✓ Redis ready"

echo "All databases started!"