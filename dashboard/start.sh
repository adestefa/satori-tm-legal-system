#!/bin/bash

# This script starts the dashboard services.
# It assumes you have already run install.sh once.

# Navigate to the script's directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Add project root to PYTHONPATH to allow for absolute imports
export PYTHONPATH=$PYTHONPATH:$(dirname "$PWD")


echo "--- Starting services in the background ---"

# Run Tailwind CSS watcher in the background
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch > /dev/null 2>&1 &
TAILWIND_PID=$!
echo "Started CSS watcher in background."

# Start the FastAPI server in the background using venv python
venv/bin/python -m uvicorn dashboard.main:app --host 0.0.0.0 --port 8000 > start_server.log 2>&1 &
echo "Started FastAPI server in background."

echo "--- Dashboard is running ---"
echo "Access it at: http://127.0.0.1:8000"