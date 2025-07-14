#!/bin/bash

# Simple Case Reset Script
# Usage: ./reset_case.sh <case_name>

set -e

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <case_name>"
    echo "Example: $0 youssef"
    exit 1
fi

CASE_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TM_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUTS_DIR="$TM_ROOT/outputs/tests"
CASE_OUTPUT_DIR="$OUTPUTS_DIR/$CASE_NAME"

echo "Resetting case: $CASE_NAME"

if [[ -d "$CASE_OUTPUT_DIR" ]]; then
    echo "Removing generated files from: $CASE_OUTPUT_DIR"
    rm -rf "$CASE_OUTPUT_DIR"
    echo "✅ Case reset complete"
    echo ""
    echo "The system will automatically detect the changes and reset the case to NEW status."
    echo "You can now reprocess the case from the dashboard."
else
    echo "⚠️  No generated files found for case '$CASE_NAME'"
    echo "Case appears to already be reset or never processed."
fi