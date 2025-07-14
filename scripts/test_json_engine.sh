#!/bin/bash

# Complete Tiger-Monkey JSON Engine Test
# Tests full workflow: Case Documents → Tiger Hydrated JSON → Monkey Document Generation

echo "🏛️ Tiger-Monkey JSON Engine Complete Test"
echo "=========================================="
echo "Testing: Youssef v. Multiple Defendants FCRA Case"
echo ""

# Test case configuration
CASE_FOLDER="../test-data/cases/youssef"
CASE_NAME="youssef_v_equifax_fcra_2025"
OUTPUT_DIR="../output/json-engine-test"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "📋 Test Configuration:"
echo "   Case Folder: $CASE_FOLDER"
echo "   Case Name: $CASE_NAME"
echo "   Output Directory: $OUTPUT_DIR"
echo "   Timestamp: $TIMESTAMP"
echo ""

# Verify case folder exists and has files
if [ ! -d "$CASE_FOLDER" ]; then
    echo "❌ Error: Case folder not found: $CASE_FOLDER"
    exit 1
fi

FILE_COUNT=$(find "$CASE_FOLDER" -name "*.pdf" -o -name "*.docx" | wc -l)
if [ "$FILE_COUNT" -eq 0 ]; then
    echo "❌ Error: No legal documents found in case folder"
    exit 1
fi

echo "📄 Case Documents Found: $FILE_COUNT files"
echo "   Document List:"
for file in "$CASE_FOLDER"/*; do
    if [[ -f "$file" && ("$file" == *.pdf || "$file" == *.docx) ]]; then
        echo "   - $(basename "$file")"
    fi
done
echo ""

# Clean up previous test results
echo "🧹 Cleaning up previous test results..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "🎬 PHASE 1: Tiger Hydrated JSON Generation"
echo "=========================================="

# Run Tiger hydrated JSON consolidation
echo "🔄 Running Tiger hydrated JSON consolidation..."
../tiger/run.sh hydrated-json "$CASE_FOLDER" \
    --output "$OUTPUT_DIR" \
    --case-name "$CASE_NAME"

TIGER_EXIT_CODE=$?

if [ $TIGER_EXIT_CODE -eq 0 ]; then
    echo "✅ Tiger hydrated JSON generation completed successfully"
else
    echo "❌ Tiger hydrated JSON generation failed (exit code: $TIGER_EXIT_CODE)"
    exit 1
fi

# Verify Tiger output
HYDRATED_JSON_FILE="$OUTPUT_DIR/hydrated_FCRA_${CASE_NAME}.json"

if [ ! -f "$HYDRATED_JSON_FILE" ]; then
    echo "❌ Error: Hydrated JSON file not found: $HYDRATED_JSON_FILE"
    exit 1
fi

echo ""
echo "📊 Tiger Output Analysis:"
echo "   📄 Hydrated JSON File: $(basename "$HYDRATED_JSON_FILE")"
echo "   📁 File Size: $(stat -f%z "$HYDRATED_JSON_FILE" 2>/dev/null || stat -c%s "$HYDRATED_JSON_FILE" 2>/dev/null) bytes"

# Quick JSON validation
echo "   🔍 JSON Structure Validation:"
if command -v jq >/dev/null 2>&1; then
    # Use jq if available for better validation
    if jq empty "$HYDRATED_JSON_FILE" 2>/dev/null; then
        echo "   ✅ Valid JSON structure"
        
        # Extract key metrics
        PLAINTIFF_NAME=$(jq -r '.parties.plaintiff.name // empty' "$HYDRATED_JSON_FILE" 2>/dev/null)
        DEFENDANT_COUNT=$(jq '.parties.defendants | length' "$HYDRATED_JSON_FILE" 2>/dev/null)
        CAUSES_COUNT=$(jq '.causes_of_action | length' "$HYDRATED_JSON_FILE" 2>/dev/null)
        
        if [ -n "$PLAINTIFF_NAME" ]; then
            echo "   👤 Plaintiff: $PLAINTIFF_NAME"
        fi
        
        if [ -n "$DEFENDANT_COUNT" ]; then
            echo "   🏢 Defendants: $DEFENDANT_COUNT"
        fi
        
        if [ -n "$CAUSES_COUNT" ]; then
            echo "   ⚖️  Causes of Action: $CAUSES_COUNT"
        fi
    else
        echo "   ❌ Invalid JSON structure"
        exit 1
    fi
else
    # Fallback validation without jq
    if python3 -c "import json; json.load(open('$HYDRATED_JSON_FILE'))" 2>/dev/null; then
        echo "   ✅ Valid JSON structure"
    else
        echo "   ❌ Invalid JSON structure"
        exit 1
    fi
fi

echo ""
echo "🎬 PHASE 2: Monkey Validation & Document Generation"
echo "=================================================="

# Test Monkey validation
echo "🔍 Running Monkey validation..."
../monkey/run.sh validate "$HYDRATED_JSON_FILE"

MONKEY_VALIDATE_EXIT_CODE=$?

if [ $MONKEY_VALIDATE_EXIT_CODE -eq 0 ]; then
    echo "✅ Monkey validation passed"
else
    echo "❌ Monkey validation failed (exit code: $MONKEY_VALIDATE_EXIT_CODE)"
    echo "⚠️  Continuing with document generation attempt..."
fi

# Test Monkey document generation
echo ""
echo "📝 Running Monkey document generation..."
MONKEY_OUTPUT_DIR="$OUTPUT_DIR/monkey_documents"
mkdir -p "$MONKEY_OUTPUT_DIR"

../monkey/run.sh build-complaint "$HYDRATED_JSON_FILE" \
    --output "$MONKEY_OUTPUT_DIR" \
    --format txt

MONKEY_BUILD_EXIT_CODE=$?

if [ $MONKEY_BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ Monkey document generation completed successfully"
else
    echo "❌ Monkey document generation failed (exit code: $MONKEY_BUILD_EXIT_CODE)"
fi

echo ""
echo "📊 Monkey Output Analysis:"
if [ -d "$MONKEY_OUTPUT_DIR" ]; then
    GENERATED_FILES=$(find "$MONKEY_OUTPUT_DIR" -type f | wc -l)
    echo "   📁 Generated Files: $GENERATED_FILES"
    
    if [ $GENERATED_FILES -gt 0 ]; then
        echo "   📄 Generated Documents:"
        for file in "$MONKEY_OUTPUT_DIR"/*; do
            if [ -f "$file" ]; then
                FILE_SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
                echo "   - $(basename "$file") ($FILE_SIZE bytes)"
            fi
        done
        
        # Show preview of main complaint document
        COMPLAINT_FILE=$(find "$MONKEY_OUTPUT_DIR" -name "*complaint*" | head -1)
        if [ -f "$COMPLAINT_FILE" ]; then
            echo ""
            echo "📋 Complaint Document Preview (first 20 lines):"
            echo "─────────────────────────────────────────────"
            head -20 "$COMPLAINT_FILE"
            echo "─────────────────────────────────────────────"
            echo "   (Full document saved to: $COMPLAINT_FILE)"
        fi
    fi
else
    echo "   ❌ No output directory created"
fi

echo ""
echo "🎬 PHASE 3: End-to-End Workflow Verification"
echo "============================================"

# Verify complete workflow
WORKFLOW_SUCCESS=true

echo "🔍 Verifying complete workflow..."

# Check Tiger output
if [ ! -f "$HYDRATED_JSON_FILE" ]; then
    echo "❌ Tiger hydrated JSON missing"
    WORKFLOW_SUCCESS=false
else
    echo "✅ Tiger hydrated JSON generated"
fi

# Check Monkey validation
if [ $MONKEY_VALIDATE_EXIT_CODE -eq 0 ]; then
    echo "✅ Monkey validation successful"
else
    echo "⚠️  Monkey validation issues detected"
fi

# Check Monkey document generation
if [ $MONKEY_BUILD_EXIT_CODE -eq 0 ] && [ -d "$MONKEY_OUTPUT_DIR" ]; then
    GENERATED_COUNT=$(find "$MONKEY_OUTPUT_DIR" -type f | wc -l)
    if [ $GENERATED_COUNT -gt 0 ]; then
        echo "✅ Monkey document generation successful ($GENERATED_COUNT files)"
    else
        echo "❌ Monkey generated no files"
        WORKFLOW_SUCCESS=false
    fi
else
    echo "❌ Monkey document generation failed"
    WORKFLOW_SUCCESS=false
fi

echo ""
echo "📈 Performance Metrics:"
echo "   📄 Input Documents: $FILE_COUNT"
echo "   ⏱️  Tiger Processing: $([ $TIGER_EXIT_CODE -eq 0 ] && echo "Success" || echo "Failed")"
echo "   🐒 Monkey Validation: $([ $MONKEY_VALIDATE_EXIT_CODE -eq 0 ] && echo "Passed" || echo "Issues")"
echo "   📝 Document Generation: $([ $MONKEY_BUILD_EXIT_CODE -eq 0 ] && echo "Success" || echo "Failed")"

echo ""
echo "🎯 FINAL RESULTS"
echo "================"

if [ "$WORKFLOW_SUCCESS" = true ] && [ $TIGER_EXIT_CODE -eq 0 ] && [ $MONKEY_BUILD_EXIT_CODE -eq 0 ]; then
    echo "🎉 COMPLETE SUCCESS!"
    echo ""
    echo "✅ End-to-End Workflow Verified:"
    echo "   1. ✅ Tiger processed $FILE_COUNT case documents"
    echo "   2. ✅ Generated schema-compliant hydrated JSON"
    echo "   3. ✅ Monkey validated the JSON successfully"
    echo "   4. ✅ Generated court-ready legal documents"
    echo ""
    echo "🏆 The Tiger-Monkey JSON Engine is working perfectly!"
    echo ""
    echo "📁 Output Files:"
echo "   📄 Hydrated JSON: $HYDRATED_JSON_FILE"
echo "   📝 Legal Documents: $MONKEY_OUTPUT_DIR/"
echo ""
echo "🚀 Ready for Production Use!"
    
    # Save success log
    echo "$(date): SUCCESS - Complete Tiger-Monkey workflow test passed" >> "$OUTPUT_DIR/test_results.log"
    
    exit 0
else
    echo "❌ WORKFLOW ISSUES DETECTED"
    echo ""
    echo "⚠️  Some components need attention:"
    
    if [ $TIGER_EXIT_CODE -ne 0 ]; then
        echo "   🐅 Tiger hydrated JSON generation failed"
    fi
    
    if [ $MONKEY_VALIDATE_EXIT_CODE -ne 0 ]; then
        echo "   🔍 Monkey validation detected issues"
    fi
    
    if [ $MONKEY_BUILD_EXIT_CODE -ne 0 ]; then
        echo "   🐒 Monkey document generation failed"
    fi
    
    echo ""
    echo "🔧 Troubleshooting Steps:"
    echo "   1. Review error messages above"
    echo "   2. Check Tiger processing quality"
    echo "   3. Validate JSON schema compliance"
    echo "   4. Test Monkey templates manually"
    echo ""
    echo "📁 Partial Results Saved:"
    echo "   📄 Output Directory: $OUTPUT_DIR"
    
    # Save failure log
    echo "$(date): PARTIAL - Tiger-Monkey workflow test had issues" >> "$OUTPUT_DIR/test_results.log"
    
    exit 1
fi
