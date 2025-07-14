#!/bin/bash
#
# Test Output Cleanup Utility
# Safely purges all generated test files from the tests/output directory
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_OUTPUT_DIR="$SCRIPT_DIR/output"

echo "🧹 Satori Tiger Test Output Cleanup"
echo "=================================="

# Verify we're in the right location
if [ ! -d "$TEST_OUTPUT_DIR" ]; then
    echo "❌ Error: Test output directory not found: $TEST_OUTPUT_DIR"
    echo "   Run this script from the tests/ directory"
    exit 1
fi

# Show what will be cleaned
echo "📁 Cleaning test output directory: $TEST_OUTPUT_DIR"
echo

# Count files before cleanup
file_count=$(find "$TEST_OUTPUT_DIR" -type f | wc -l)
dir_count=$(find "$TEST_OUTPUT_DIR" -type d | wc -l)

if [ "$file_count" -eq 0 ]; then
    echo "✨ Directory already clean (0 files, $((dir_count - 1)) subdirectories)"
    exit 0
fi

echo "📊 Found $file_count files in $((dir_count - 1)) subdirectories"

# Confirm cleanup (optional safety check)
if [ "$1" != "--force" ] && [ "$1" != "-f" ]; then
    echo
    read -p "🗑️  Delete all test output files? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cleanup cancelled"
        exit 0
    fi
fi

# Perform cleanup
echo "🗑️  Removing test output files..."

# Remove all files but preserve directory structure
find "$TEST_OUTPUT_DIR" -type f -delete

# Ensure core directories exist
mkdir -p "$TEST_OUTPUT_DIR/processed"
mkdir -p "$TEST_OUTPUT_DIR/reports"
mkdir -p "$TEST_OUTPUT_DIR/metadata"
mkdir -p "$TEST_OUTPUT_DIR/failed"
mkdir -p "$TEST_OUTPUT_DIR/logs"

# Verify cleanup
remaining_files=$(find "$TEST_OUTPUT_DIR" -type f | wc -l)

if [ "$remaining_files" -eq 0 ]; then
    echo "✅ Cleanup complete! Removed $file_count files"
    echo "📁 Directory structure preserved for future tests"
else
    echo "⚠️  Warning: $remaining_files files could not be removed"
    exit 1
fi

echo
echo "🎉 Test environment ready for new test runs!"