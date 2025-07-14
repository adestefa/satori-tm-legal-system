#!/bin/bash

# Navigate to the dashboard directory
cd "$(dirname "$0")"

echo "--- Restarting dashboard services ---"
./stop.sh
echo ""
./start.sh

echo "Waiting for server to initialize..."
sleep 3
