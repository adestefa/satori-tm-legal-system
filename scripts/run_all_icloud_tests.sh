#!/bin/bash

# Comprehensive iCloud Sync Test Suite
# Runs all iCloud-related tests in sequence

set -e  # Exit on any error

echo "🔧 COMPREHENSIVE ICLOUD SYNC TEST SUITE"
echo "========================================"
echo "Testing all iCloud sync functionality"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_script="$2"
    
    echo -e "${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}RUNNING: $test_name${NC}"
    echo -e "${BLUE}=================================================================================${NC}"
    echo ""
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Use virtual environment if available
    if [ -f "dashboard/venv/bin/activate" ]; then
        if source dashboard/venv/bin/activate && python3 "$test_script"; then
            echo ""
            echo -e "${GREEN}✅ PASSED: $test_name${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo ""
            echo -e "${RED}❌ FAILED: $test_name${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        # Fall back to system python if no venv
        if python3 "$test_script"; then
            echo ""
            echo -e "${GREEN}✅ PASSED: $test_name${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo ""
            echo -e "${RED}❌ FAILED: $test_name${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
    
    echo ""
    sleep 2  # Brief pause between tests
}

# Check if we're in the right directory
if [ ! -f "scripts/test_icloud_basic.py" ]; then
    echo -e "${RED}❌ Error: Must run from TM project root directory${NC}"
    echo "Current directory: $(pwd)"
    echo "Expected files: scripts/test_icloud_basic.py"
    exit 1
fi

echo "✅ Running from TM project root: $(pwd)"
echo ""

# Check if dashboard is running
echo "🔍 Checking dashboard status..."
if curl -s -f http://127.0.0.1:8000/api/version > /dev/null 2>&1; then
    echo "✅ Dashboard is running"
else
    echo -e "${YELLOW}⚠️  Dashboard is not running${NC}"
    echo "Some tests require the dashboard to be running."
    echo "Start with: ./dashboard/start.sh"
    echo ""
    echo "Continuing with basic tests that don't require dashboard..."
fi

echo ""

# Run all tests in sequence
run_test "Basic iCloud Service Tests" "scripts/test_icloud_basic.py"
run_test "iCloud Sync Manager Tests" "scripts/test_icloud_sync_manager.py"

# Only run API tests if dashboard is running
if curl -s -f http://127.0.0.1:8000/api/version > /dev/null 2>&1; then
    run_test "iCloud API Endpoints Tests" "scripts/test_icloud_api_endpoints.py"
    run_test "iCloud Integration Tests" "scripts/test_icloud_integration.py"
else
    echo -e "${YELLOW}⚠️  Skipping API and Integration tests (dashboard not running)${NC}"
    echo ""
fi

# Summary
echo -e "${BLUE}=================================================================================${NC}"
echo -e "${BLUE}TEST SUITE SUMMARY${NC}"
echo -e "${BLUE}=================================================================================${NC}"
echo ""
echo "📊 Total Tests Run: $TOTAL_TESTS"
echo -e "${GREEN}✅ Passed: $PASSED_TESTS${NC}"
echo -e "${RED}❌ Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ iCloud sync functionality is working correctly"
    echo "💡 System is ready for production use"
    echo ""
    echo "Next steps:"
    echo "1. Configure iCloud credentials at http://127.0.0.1:8000/settings"
    echo "2. Test with real iCloud account"
    echo "3. Sync your first case folder"
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo ""
    echo "❌ Issues found in iCloud sync functionality"
    echo "💡 Review test output above to identify problems"
    echo ""
    echo "Common issues:"
    echo "- PyiCloud library not installed: pip install pyicloud"
    echo "- Dashboard not running: ./dashboard/start.sh"
    echo "- Missing dependencies in requirements.txt"
    echo "- Permission issues with file system access"
fi

echo ""
echo -e "${BLUE}Test suite completed at $(date)${NC}"

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    exit 0
else
    exit 1
fi