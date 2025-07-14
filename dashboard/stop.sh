#!/bin/bash

# This script stops the dashboard services.

echo "--- Stopping dashboard services ---"

# Find and kill the Tailwind CSS watcher process
PGREP_OUTPUT_TAILWIND=$(pgrep -f "tailwindcss")
if [ -n "$PGREP_OUTPUT_TAILWIND" ]; then
    echo "Stopping Tailwind CSS watcher process..."
    pkill -f "tailwindcss"
else
    echo "Tailwind CSS watcher process not found."
fi

# Find and kill the Uvicorn server process
PGREP_OUTPUT_UVICORN=$(pgrep -f "uvicorn dashboard.main:app")
if [ -n "$PGREP_OUTPUT_UVICORN" ]; then
    echo "Stopping Uvicorn server process..."
    pkill -f "uvicorn dashboard.main:app"
else
    echo "Uvicorn server process not found."
fi

# Remove the .pids file if it exists
if [ -f ".pids" ]; then
    rm .pids
fi

echo "--- Services stopped ---"