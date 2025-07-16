#!/bin/bash
set -e

echo "[1/3] Building Docker image..."
docker-compose build

echo "[2/3] Starting containers..."
docker-compose up -d

echo "[3/3] Environment setup complete. Containers are running."
