#!/bin/bash

# Clear All Cases Script - Reset all cases completely to step 1
# Usage: ./clear_cases.sh [--force]

set -e

FORCE=false
if [[ "$1" == "--force" ]]; then
    FORCE=true
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TM_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUTS_DIR="$TM_ROOT/outputs/tests"

echo "Clear All Cases Script"
echo "======================"
echo ""
echo "This script will completely reset ALL cases to step 1 by removing:"
echo "- All generated files (JSON, HTML)"
echo "- All lawyer selections"
echo "- All processing history"
echo ""

if [[ "$FORCE" != "true" ]]; then
    echo "⚠️  WARNING: This will delete ALL generated case files!"
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Operation cancelled."
        exit 0
    fi
fi

echo ""
echo "Clearing all cases..."

if [[ -d "$OUTPUTS_DIR" ]]; then
    # Count directories before deletion
    CASE_COUNT=$(find "$OUTPUTS_DIR" -maxdepth 1 -type d ! -path "$OUTPUTS_DIR" | wc -l | tr -d ' ')
    
    if [[ "$CASE_COUNT" -gt 0 ]]; then
        echo "Found $CASE_COUNT case directories to clear:"
        find "$OUTPUTS_DIR" -maxdepth 1 -type d ! -path "$OUTPUTS_DIR" -exec basename {} \; | sort | sed 's/^/  - /'
        echo ""
        
        # Remove all case directories
        find "$OUTPUTS_DIR" -maxdepth 1 -type d ! -path "$OUTPUTS_DIR" -exec rm -rf {} \;
        echo "✅ Removed all case directories"
    else
        echo "ℹ️  No case directories found"
    fi
    
    # Remove any standalone JSON files
    STANDALONE_JSON=$(find "$OUTPUTS_DIR" -maxdepth 1 -name "*.json" 2>/dev/null || true)
    if [[ -n "$STANDALONE_JSON" ]]; then
        echo "Removing standalone JSON files:"
        echo "$STANDALONE_JSON" | while read -r file; do
            if [[ -f "$file" ]]; then
                rm "$file"
                echo "  Removed: $(basename "$file")"
            fi
        done
    fi
else
    echo "ℹ️  Outputs directory does not exist: $OUTPUTS_DIR"
fi

echo ""
echo "📝 ALL cases have been completely reset to step 1 (NEW status)"
echo "   - All generated files removed"
echo "   - All lawyer selections cleared"
echo "   - All processing history removed"
echo ""
echo "The file watcher will automatically detect the changes."
echo "All cases will appear as NEW status in the dashboard."