#!/bin/bash
set -e

./install.sh

sleep 3
echo "Checking service status..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "FastAPI service is running. Access documentation at http://localhost:8000/docs"
else
    echo "ERROR: FastAPI service did not start correctly. Check docker-compose logs."
    exit 1
fi
