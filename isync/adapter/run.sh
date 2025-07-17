#!/bin/bash
# This script runs the TM iSync Adapter

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to that directory
cd "$DIR"

# Echo a professional startup message
echo "=================================================="
echo "  Starting Tiger-Monkey iCloud Sync Service v1.1  "
echo "=================================================="
echo " "
echo "Service initiated at: $(date)"
echo "Monitoring iCloud folder for new cases..."
echo "Press Ctrl+C to stop the service."
echo " "

# Run the Go application
./tm-isync-adapter
