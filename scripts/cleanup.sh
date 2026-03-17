#!/bin/bash
echo "Stopping native services..."
sudo systemctl stop postgresql mongod redis-server 2>/dev/null
sudo systemctl disable postgresql mongod redis-server 2>/dev/null

echo "Killing any processes on ports..."
sudo fuser -k 5432/tcp 2>/dev/null
sudo fuser -k 27017/tcp 2>/dev/null
sudo fuser -k 6379/tcp 2>/dev/null

echo "Cleaning up Docker..."
docker-compose down -v
docker rm -f $(docker ps -aq) 2>/dev/null

echo "Starting fresh Docker containers..."
docker-compose up -d

echo "Done! Container status:"
docker-compose ps