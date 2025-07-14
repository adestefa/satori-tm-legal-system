#!/bin/bash
#
# Test script for the Banana Template Generator
#

set -e

echo "🍌 Banana Template Generator Test"
echo "=================================="

OUTPUT_DIR="tests/output"
OUTPUT_FILE="$OUTPUT_DIR/banana_test_output.html"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

echo "🚀 Running banana.py to generate a test template..."
./run_banana.sh \
    --schema-file shared-schema/satori_schema/hydrated_json_schema.py \
    --schema-class HydratedJSON \
    --json-file test-data/test-json/ground_truth_complaint.json \
    --output-file "$OUTPUT_FILE"

# Check if the output file was created
if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Test Passed: Output file '$OUTPUT_FILE' created successfully."
    # Clean up the generated file
    rm "$OUTPUT_FILE"
    echo "🧹 Cleaned up test file."
else
    echo "❌ Test Failed: Output file '$OUTPUT_FILE' was not created."
    exit 1
fi
