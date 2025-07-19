#!/bin/bash
# This script runs the Satori Secure File Sync service

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to that directory
cd "$DIR"

# Determine environment (default to local)
ENV="${1:-local}"
CONFIG_FILE="config-${ENV}.json"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found!"
    echo "Available configurations:"
    ls config-*.json 2>/dev/null | sed 's/config-//g' | sed 's/.json//g'
    exit 1
fi

# Echo a professional startup message
echo "=================================================="
echo "      Satori Secure File Sync v1.1.0             "
echo "=================================================="
echo " "
echo "Environment: $(echo $ENV | tr '[:lower:]' '[:upper:]')"
echo "Config: $CONFIG_FILE"
echo "Service initiated at: $(date)"
echo "Monitoring iCloud folder for new cases..."
echo "Press Ctrl+C to stop the service."
echo " "

# Run the Go application with the selected config
./satori-secure-file-sync -config "$CONFIG_FILE"
