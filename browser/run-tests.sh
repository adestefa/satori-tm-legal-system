#!/bin/bash

# TM Browser PDF Generator - Master Test Runner
# Orchestrates all testing scripts for comprehensive validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🎯 TM Browser PDF Generator - Master Test Suite${NC}"
echo "======================================================="

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [TEST_SUITE]"
    echo ""
    echo "Test Suites:"
    echo "  quick         Run quick validation tests"
    echo "  full          Run complete test suite (default)"
    echo "  single        Run single file tests only"
    echo "  batch         Run batch processing tests only"
    echo "  benchmark     Run performance benchmarks only"
    echo "  integration   Run integration tests only"
    echo "  python        Test Python wrapper only"
    echo ""
    echo "Options:"
    echo "  --verbose     Show detailed output from all tests"
    echo "  --clean       Clean test outputs before running"
    echo "  --report      Generate detailed test report"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run-tests.sh                    # Run full test suite"
    echo "  ./run-tests.sh quick              # Quick validation"
    echo "  ./run-tests.sh benchmark --clean  # Clean benchmark run"
    echo "  ./run-tests.sh --verbose --report # Full suite with report"
}

# Function to run a test script and capture results
run_test_script() {
    local script_name="$1"
    local test_description="$2"
    local show_output="$3"
    
    echo -e "\n${YELLOW}🧪 $test_description${NC}"
    echo "$(printf '=%.0s' {1..50})"
    
    local start_time=$(date +%s)
    local success=true
    
    if [ "$show_output" = "true" ]; then
        if ! ./"$script_name"; then
            success=false
        fi
    else
        if ! ./"$script_name" > /tmp/test_output_$$ 2>&1; then
            success=false
        fi
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [ "$success" = true ]; then
        echo -e "${GREEN}✅ $test_description completed successfully (${duration}s)${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_description failed (${duration}s)${NC}"
        if [ "$show_output" = false ] && [ -f "/tmp/test_output_$$" ]; then
            echo -e "${RED}Error output:${NC}"
            cat /tmp/test_output_$$
        fi
        return 1
    fi
}

# Function to test Python wrapper
test_python_wrapper() {
    echo -e "\n${PURPLE}🐍 Testing Python Wrapper${NC}"
    echo "$(printf '=%.0s' {1..30})"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found${NC}"
        return 1
    fi
    
    # Test Python wrapper functionality
    echo "Testing Python service validation..."
    if python3 print.py test > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Python wrapper service test passed${NC}"
    else
        echo -e "${RED}❌ Python wrapper service test failed${NC}"
        return 1
    fi
    
    return 0
}

# Parse command line arguments
VERBOSE=false
CLEAN_BEFORE=false
GENERATE_REPORT=false
TEST_SUITE="full"

while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --clean)
            CLEAN_BEFORE=true
            shift
            ;;
        --report)
            GENERATE_REPORT=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        quick|full|single|batch|benchmark|integration|python)
            TEST_SUITE="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Check if we're in the correct directory
if [ ! -f "pdf-generator.js" ]; then
    echo -e "${RED}❌ pdf-generator.js not found. Run from TM/browser/ directory.${NC}"
    exit 1
fi

# System information
echo -e "${BLUE}🖥️  Test Environment${NC}"
echo "----------------------------------------"
echo "Date: $(date)"
echo "OS: $(uname -s -r)"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not found')"
echo "Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "Test Suite: $TEST_SUITE"
echo "Verbose: $VERBOSE"
echo ""

# Clean before testing if requested
if [ "$CLEAN_BEFORE" = true ]; then
    echo -e "${BLUE}🧹 Cleaning test outputs...${NC}"
    if [ -f "cleanup.sh" ]; then
        ./cleanup.sh --test-outputs > /dev/null 2>&1 || true
        echo -e "${GREEN}✅ Test outputs cleaned${NC}"
    fi
fi

# Initialize test results tracking
declare -a test_results
declare -a test_names
declare -a test_durations

# Function to track test results
track_test_result() {
    local name="$1"
    local result="$2"
    local duration="$3"
    
    test_names+=("$name")
    test_results+=("$result")
    test_durations+=("$duration")
}

# Run test suites based on selection
case $TEST_SUITE in
    quick)
        echo -e "${BLUE}🚀 Running Quick Test Suite${NC}"
        
        # Quick Node.js service test
        start_time=$(date +%s)
        if node pdf-generator.js --test > /dev/null 2>&1; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Node.js Service Test" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Node.js Service Test" "❌ FAIL" "$duration"
        fi
        
        # Python wrapper test
        if command -v python3 &> /dev/null; then
            start_time=$(date +%s)
            if test_python_wrapper > /dev/null 2>&1; then
                duration=$(($(date +%s) - start_time))
                track_test_result "Python Wrapper Test" "✅ PASS" "$duration"
            else
                duration=$(($(date +%s) - start_time))
                track_test_result "Python Wrapper Test" "❌ FAIL" "$duration"
            fi
        fi
        ;;
        
    single)
        echo -e "${BLUE}🚀 Running Single File Tests${NC}"
        start_time=$(date +%s)
        if run_test_script "test-single.sh" "Single File PDF Generation" "$VERBOSE"; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Single File Tests" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Single File Tests" "❌ FAIL" "$duration"
        fi
        ;;
        
    batch)
        echo -e "${BLUE}🚀 Running Batch Processing Tests${NC}"
        start_time=$(date +%s)
        if run_test_script "test-batch.sh" "Batch PDF Processing" "$VERBOSE"; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Batch Processing Tests" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Batch Processing Tests" "❌ FAIL" "$duration"
        fi
        ;;
        
    benchmark)
        echo -e "${BLUE}🚀 Running Performance Benchmarks${NC}"
        start_time=$(date +%s)
        if run_test_script "benchmark.sh" "Performance Benchmarks" "$VERBOSE"; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Performance Benchmarks" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Performance Benchmarks" "❌ FAIL" "$duration"
        fi
        ;;
        
    integration)
        echo -e "${BLUE}🚀 Running Integration Tests${NC}"
        start_time=$(date +%s)
        if run_test_script "test-integration.sh" "TM System Integration" "$VERBOSE"; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Integration Tests" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Integration Tests" "❌ FAIL" "$duration"
        fi
        ;;
        
    python)
        echo -e "${BLUE}🚀 Running Python Wrapper Tests${NC}"
        start_time=$(date +%s)
        if test_python_wrapper; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Python Wrapper Tests" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Python Wrapper Tests" "❌ FAIL" "$duration"
        fi
        ;;
        
    full)
        echo -e "${BLUE}🚀 Running Complete Test Suite${NC}"
        
        # Single file tests
        start_time=$(date +%s)
        if run_test_script "test-single.sh" "Single File PDF Generation" "$VERBOSE"; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Single File Tests" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Single File Tests" "❌ FAIL" "$duration"
        fi
        
        # Batch processing tests
        start_time=$(date +%s)
        if run_test_script "test-batch.sh" "Batch PDF Processing" "$VERBOSE"; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Batch Processing Tests" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Batch Processing Tests" "❌ FAIL" "$duration"
        fi
        
        # Python wrapper tests
        if command -v python3 &> /dev/null; then
            start_time=$(date +%s)
            if test_python_wrapper; then
                duration=$(($(date +%s) - start_time))
                track_test_result "Python Wrapper Tests" "✅ PASS" "$duration"
            else
                duration=$(($(date +%s) - start_time))
                track_test_result "Python Wrapper Tests" "❌ FAIL" "$duration"
            fi
        fi
        
        # Integration tests
        start_time=$(date +%s)
        if run_test_script "test-integration.sh" "TM System Integration" "$VERBOSE"; then
            duration=$(($(date +%s) - start_time))
            track_test_result "Integration Tests" "✅ PASS" "$duration"
        else
            duration=$(($(date +%s) - start_time))
            track_test_result "Integration Tests" "❌ FAIL" "$duration"
        fi
        
        # Performance benchmarks (optional for full suite)
        if [ -f "benchmark.sh" ]; then
            echo -e "\n${YELLOW}⚡ Running performance benchmarks (this may take a while)...${NC}"
            start_time=$(date +%s)
            if run_test_script "benchmark.sh" "Performance Benchmarks" "false"; then
                duration=$(($(date +%s) - start_time))
                track_test_result "Performance Benchmarks" "✅ PASS" "$duration"
            else
                duration=$(($(date +%s) - start_time))
                track_test_result "Performance Benchmarks" "❌ FAIL" "$duration"
            fi
        fi
        ;;
esac

# Generate test summary
echo -e "\n${CYAN}📊 Test Results Summary${NC}"
echo "==========================================="

total_tests=${#test_names[@]}
passed_tests=0
failed_tests=0
total_time=0

for ((i=0; i<$total_tests; i++)); do
    echo "  ${test_names[i]}: ${test_results[i]} (${test_durations[i]}s)"
    
    if [[ "${test_results[i]}" == *"PASS"* ]]; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    
    total_time=$((total_time + test_durations[i]))
done

echo ""
echo "Total Tests: $total_tests"
echo "Passed: $passed_tests"
echo "Failed: $failed_tests"
echo "Total Time: ${total_time}s"

if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed successfully!${NC}"
    final_result=0
else
    echo -e "\n${RED}❌ $failed_tests test(s) failed${NC}"
    final_result=1
fi

# Generate detailed report if requested
if [ "$GENERATE_REPORT" = true ]; then
    report_file="test-report-$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# TM Browser PDF Generator - Test Report

**Generated:** $(date)
**Test Suite:** $TEST_SUITE
**Environment:** $(uname -s -r)
**Node.js:** $(node --version 2>/dev/null || echo 'Not found')
**Python:** $(python3 --version 2>/dev/null || echo 'Not found')

## Test Results

| Test Name | Result | Duration |
|-----------|--------|----------|
EOF

    for ((i=0; i<$total_tests; i++)); do
        echo "| ${test_names[i]} | ${test_results[i]} | ${test_durations[i]}s |" >> "$report_file"
    done

    cat >> "$report_file" << EOF

## Summary

- **Total Tests:** $total_tests
- **Passed:** $passed_tests  
- **Failed:** $failed_tests
- **Total Time:** ${total_time}s
- **Success Rate:** $(( passed_tests * 100 / total_tests ))%

## Generated Files

EOF

    # List generated PDF files
    if [ -d "test-outputs" ]; then
        echo "### PDF Files Generated" >> "$report_file"
        find test-outputs -name "*.pdf" -exec ls -lh {} \; | while read -r line; do
            echo "- $line" >> "$report_file"
        done
    fi

    echo -e "\n${BLUE}📋 Detailed report generated: $report_file${NC}"
fi

# Cleanup
rm -f /tmp/test_output_$$

exit $final_result