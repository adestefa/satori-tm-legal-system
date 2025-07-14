#!/bin/bash

# Screenshot script for Satori Legal Agent
# Usage: ./screenshot.sh <url>

# Constants
SCREENSHOT_SAVE_FOLDER="/Users/corelogic/satori-dev/TM/outputs/screenshots"
CLAUDE_PROMPT="screenshot is running…"

# Check if URL argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <url>"
    echo "Example: $0 http://127.0.0.1:8000/"
    exit 1
fi

URL="$1"


# Run claude with the screenshot command
echo "Taking screenshot of: $URL"

claude -p "/screenshot \"$URL\"" --dangerously-skip-permissions

echo "Screenshot saved to: $SCREENSHOT_SAVE_FOLDER"