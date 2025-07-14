#!/bin/bash

# This script performs the one-time installation for the dashboard.

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "--- Creating Python virtual environment ---"
python3 -m venv venv

echo "--- Installing Python dependencies ---"
source venv/bin/activate
pip install -r requirements.txt

echo "--- Installing Node.js dependencies ---"
npm install

echo "--- Building CSS for production ---"
npm run build:css

echo "--- Installation complete ---"
echo "You can now run the dashboard using ./start.sh"
