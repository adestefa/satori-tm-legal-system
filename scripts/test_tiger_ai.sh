#!/bin/bash

# AI-friendly Tiger test script - runs essential tests without menu

echo "🐅 Tiger AI Test Suite"
echo "====================="

# Test files array for real-world case processing
TEST_FILES=(
    "Adverse_Action_Letter_Cap_One.pdf"
    "SummonsEquifax.pdf"
    "Summons_Trans Union.pdf"
)

# Test 1: Process adverse action letter
echo "📄 Test 1: Processing adverse action letter..."
TEST_FILE="${TEST_FILES[0]}"
OUTPUT_DIR="../output/tiger/ai-test-1/"

../tiger/run.sh process "../test-data/sample_case_files/$TEST_FILE" --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo "✅ Test 1 PASSED: Adverse action letter processed successfully"
    
    # Check for output files
    if [ -d "$OUTPUT_DIR/legacy/processed/" ]; then
        FILE_COUNT=$(ls -1 "$OUTPUT_DIR/legacy/processed/" | wc -l)
        echo "📊 Generated $FILE_COUNT output files"
        
        # Check for JSON file
        JSON_FILE=$(find "$OUTPUT_DIR/legacy/processed/" -name "*.json" | head -1)
        if [ -f "$JSON_FILE" ]; then
            echo "✅ JSON output file created: $(basename "$JSON_FILE")"
        else
            echo "⚠️  No JSON file found"
        fi
    else
        echo "❌ No processed output directory found"
        exit 1
    fi
else
    echo "❌ Test 1 FAILED: Adverse action letter processing failed"
    exit 1
fi

# Test 2: Process summons document
echo ""
echo "📄 Test 2: Processing summons document..."
TEST_FILE="${TEST_FILES[1]}"
OUTPUT_DIR="../output/tiger/ai-test-2/"

../tiger/run.sh process "../test-data/sample_case_files/$TEST_FILE" --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo "✅ Test 2 PASSED: Summons document processed successfully"
    
    # Check for output files
    if [ -d "$OUTPUT_DIR/legacy/processed/" ]; then
        FILE_COUNT=$(ls -1 "$OUTPUT_DIR/legacy/processed/" | wc -l)
        echo "📊 Generated $FILE_COUNT output files"
        
        # Check for JSON file
        JSON_FILE=$(find "$OUTPUT_DIR/legacy/processed/" -name "*.json" | head -1)
        if [ -f "$JSON_FILE" ]; then
            echo "✅ JSON output file created: $(basename "$JSON_FILE")"
        else
            echo "⚠️  No JSON file found"
        fi
    else
        echo "❌ No processed output directory found"
        exit 1
    fi
else
    echo "❌ Test 2 FAILED: Summons document processing failed"
    exit 1
fi

# Test 3: Process second summons for variety
echo ""
echo "📄 Test 3: Processing second summons document..."
TEST_FILE="${TEST_FILES[2]}"
OUTPUT_DIR="../output/tiger/ai-test-3/"

../tiger/run.sh process "../test-data/sample_case_files/$TEST_FILE" --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo "✅ Test 3 PASSED: Second summons processed successfully"
    
    # Check for output files
    if [ -d "$OUTPUT_DIR/legacy/processed/" ]; then
        FILE_COUNT=$(ls -1 "$OUTPUT_DIR/legacy/processed/" | wc -l)
        echo "📊 Generated $FILE_COUNT output files"
        
        # Check for JSON file
        JSON_FILE=$(find "$OUTPUT_DIR/legacy/processed/" -name "*.json" | head -1)
        if [ -f "$JSON_FILE" ]; then
            echo "✅ JSON output file created: $(basename "$JSON_FILE")"
        else
            echo "⚠️  No JSON file found"
        fi
    else
        echo "❌ No processed output directory found"
        exit 1
    fi
else
    echo "❌ Test 3 FAILED: Second summons processing failed"
    exit 1
fi

echo ""
echo "🎯 Tiger AI Test Complete"
echo "========================="
echo "✅ All 3 tests passed"
echo "📁 Outputs saved to: ../output/tiger/ai-test-{1,2,3}/"
echo "📋 Processed files:"
for i in "${!TEST_FILES[@]}"; do
    echo "  Test $((i+1)): ${TEST_FILES[$i]}"
done

exit 0
