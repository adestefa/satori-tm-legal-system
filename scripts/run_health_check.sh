#!/bin/bash

# --- Initialization ---

echo "🐅 Satori Tiger - Health Check"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "❌ Error: Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# --- Test Execution ---
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    echo -n "$test_name... "
    
    if $test_command > /tmp/health_check_output 2>&1; then
        echo "✅ PASS"
    else
        echo "❌ FAIL"
        cat /tmp/health_check_output
        ((FAILED_TESTS++))
    fi
}

echo "📋 Running health check tests..."
echo ""

run_test "1. Core Extraction" "python3 -m unittest -q tests.test_legal_extraction.TestLegalEntityExtractor.test_extract_case_number_federal"
run_test "2. Integration" "python3 -m unittest -q tests.test_legal_extraction.TestIntegrationScenarios.test_fcra_case_workflow"  
run_test "3. Data Validation" "python3 -m unittest -q tests.test_data_validation.TestComplaintJsonValidation.test_valid_complaint_json_structure"
run_test "4. Performance" "python3 -m unittest -q tests.test_performance.TestPerformance.test_extraction_performance_small_document"
run_test "5. Attorney Notes (DOCX)" "python3 -m unittest -q tests.test_process_attorney_notes"
run_test "6. Summons (PDF)" "python3 -m unittest -q tests.test_process_summons"
run_test "7. Text File (TXT)" "python3 -m unittest -q tests.test_process_text_file"
run_test "8. Real-World Case Consolidation" "python3 -m unittest -q tests.test_real_case_consolidation"
run_test "9. Banana Template Generator" "./scripts/test_banana.sh"




# --- Summary ---
echo ""
if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 Health check complete - All tests passed!"
else
    echo "⚠️  Health check complete - $FAILED_TESTS test(s) failed"
fi

# --- Deactivation ---
deactivate

# Clean up temp file
rm -f /tmp/health_check_output

exit $FAILED_TESTS

