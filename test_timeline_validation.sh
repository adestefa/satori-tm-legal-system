#!/bin/bash

# Timeline Validation System Test Suite
# Tests the complete MVP 1 timeline validation functionality
# Usage: ./test_timeline_validation.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
DASHBOARD_URL="http://127.0.0.1:8000"
VALID_TIMELINE_CASES=("Rodriguez")  # Cases with known good timeline data
ALL_TEST_CASES=("Rodriguez" "youssef")  # All cases to test basic functionality
TEMP_DIR="/tmp/timeline_tests"
LOG_FILE="$TEMP_DIR/test_results.log"

# Create temp directory
mkdir -p "$TEMP_DIR"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Timeline Validation System Test Suite${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to print test result
print_result() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗ FAIL${NC}: $test_name"
        if [ -n "$details" ]; then
            echo -e "  ${RED}Details: $details${NC}"
        fi
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠ WARN${NC}: $test_name"
        if [ -n "$details" ]; then
            echo -e "  ${YELLOW}Details: $details${NC}"
        fi
    fi
    
    echo "$status: $test_name - $details" >> "$LOG_FILE"
}

# Function to check if dashboard is running
check_dashboard() {
    echo "Checking if dashboard is running..."
    
    if curl -s "$DASHBOARD_URL" > /dev/null; then
        print_result "Dashboard Service Availability" "PASS" "Dashboard responding at $DASHBOARD_URL"
        return 0
    else
        print_result "Dashboard Service Availability" "FAIL" "Dashboard not responding at $DASHBOARD_URL"
        echo -e "${RED}Please start the dashboard with: ./dashboard/start.sh${NC}"
        exit 1
    fi
}

# Function to test API endpoint availability
test_api_endpoints() {
    echo ""
    echo -e "${BLUE}Testing API Endpoints...${NC}"
    
    # Test cases API
    response=$(curl -s -w "%{http_code}" "$DASHBOARD_URL/api/cases" -o "$TEMP_DIR/cases_response.json")
    if [ "$response" = "200" ]; then
        print_result "Cases API Endpoint" "PASS" "GET /api/cases returns 200"
    else
        print_result "Cases API Endpoint" "FAIL" "Expected 200, got $response"
    fi
    
    # Test timeline validation API for each case
    for case_id in "${ALL_TEST_CASES[@]}"; do
        response=$(curl -s -w "%{http_code}" "$DASHBOARD_URL/api/cases/$case_id/validate-timeline" -o "$TEMP_DIR/${case_id}_timeline.json")
        if [ "$response" = "200" ]; then
            print_result "Timeline API - $case_id" "PASS" "GET /api/cases/$case_id/validate-timeline returns 200"
        else
            print_result "Timeline API - $case_id" "FAIL" "Expected 200, got $response"
        fi
    done
}

# Function to test timeline validation data structure
test_timeline_data_structure() {
    echo ""
    echo -e "${BLUE}Testing Timeline Data Structure...${NC}"
    
    for case_id in "${ALL_TEST_CASES[@]}"; do
        local file="$TEMP_DIR/${case_id}_timeline.json"
        
        if [ ! -f "$file" ]; then
            print_result "Timeline Data - $case_id" "FAIL" "Timeline JSON file not found"
            continue
        fi
        
        # Check required fields using jq
        if ! command -v jq &> /dev/null; then
            print_result "JSON Parsing Tool" "WARN" "jq not installed, skipping detailed JSON validation"
            continue
        fi
        
        # Check if timeline is available first
        local timeline_available=$(jq -r '.timeline_available' "$file" 2>/dev/null || echo "null")
        
        if [ "$timeline_available" = "false" ]; then
            # For cases without timeline data, check basic fields
            local basic_fields=("case_id" "timeline_available" "validation_score")
            local missing_fields=()
            
            for field in "${basic_fields[@]}"; do
                if ! jq "has(\"$field\")" "$file" | grep -q "true"; then
                    missing_fields+=("$field")
                fi
            done
            
            if [ ${#missing_fields[@]} -eq 0 ]; then
                print_result "Basic Data Structure - $case_id" "PASS" "Basic fields present for non-timeline case"
            else
                print_result "Basic Data Structure - $case_id" "FAIL" "Missing basic fields: ${missing_fields[*]}"
            fi
        else
            # For cases with timeline data, check full structure
            local required_fields=("case_id" "timeline_available" "is_chronologically_valid" "validation_score" "key_dates" "validation_details")
            local missing_fields=()
            
            for field in "${required_fields[@]}"; do
                if ! jq "has(\"$field\")" "$file" | grep -q "true"; then
                    missing_fields+=("$field")
                fi
            done
            
            if [ ${#missing_fields[@]} -eq 0 ]; then
                print_result "Timeline Data Structure - $case_id" "PASS" "All required fields present"
            else
                print_result "Timeline Data Structure - $case_id" "FAIL" "Missing fields: ${missing_fields[*]}"
            fi
        fi
        
        # Check validation score is numeric and in range 0-100
        local score=$(jq -r '.validation_score' "$file" 2>/dev/null || echo "null")
        if [[ "$score" =~ ^[0-9]+\.?[0-9]*$ ]] && (( $(echo "$score >= 0 && $score <= 100" | bc -l) )); then
            print_result "Validation Score Range - $case_id" "PASS" "Score: $score (valid range 0-100)"
        else
            print_result "Validation Score Range - $case_id" "FAIL" "Invalid score: $score"
        fi
    done
}

# Function to test specific validation logic
test_validation_logic() {
    echo ""
    echo -e "${BLUE}Testing Validation Logic...${NC}"
    
    # Test Rodriguez case (known to have chronological errors)
    local rodriguez_file="$TEMP_DIR/Rodriguez_timeline.json"
    if [ -f "$rodriguez_file" ]; then
        local is_valid=$(jq -r '.is_chronologically_valid' "$rodriguez_file")
        local error_count=$(jq -r '.validation_details.errors | length' "$rodriguez_file")
        
        if [ "$is_valid" = "false" ] && [ "$error_count" -gt 0 ]; then
            print_result "Rodriguez Chronological Validation" "PASS" "Correctly detected $error_count chronological errors"
        else
            print_result "Rodriguez Chronological Validation" "FAIL" "Should detect chronological errors (valid: $is_valid, errors: $error_count)"
        fi
        
        # Check for specific error pattern
        local app_denial_errors=$(jq -r '.validation_details.errors[] | select(contains("Application date") and contains("denial date"))' "$rodriguez_file" | wc -l)
        if [ "$app_denial_errors" -gt 0 ]; then
            print_result "Application/Denial Date Logic" "PASS" "Detected $app_denial_errors application after denial errors"
        else
            print_result "Application/Denial Date Logic" "WARN" "No application/denial date errors found"
        fi
    fi
    
    # Test Youssef case (may not have timeline data)
    local youssef_file="$TEMP_DIR/youssef_timeline.json"
    if [ -f "$youssef_file" ]; then
        local timeline_available=$(jq -r '.timeline_available' "$youssef_file")
        if [ "$timeline_available" = "false" ]; then
            print_result "Youssef Timeline Handling" "PASS" "Correctly handles case without timeline data"
        else
            local score=$(jq -r '.validation_score' "$youssef_file")
            if (( $(echo "$score > 50" | bc -l) )); then
                print_result "Youssef Timeline Quality" "PASS" "Good validation score: $score"
            else
                print_result "Youssef Timeline Quality" "WARN" "Lower validation score than expected: $score"
            fi
        fi
    fi
}

# Function to test frontend integration
test_frontend_integration() {
    echo ""
    echo -e "${BLUE}Testing Frontend Integration...${NC}"
    
    # Check if review page loads
    for case_id in "${ALL_TEST_CASES[@]}"; do
        response=$(curl -s -w "%{http_code}" "$DASHBOARD_URL/review?case_id=$case_id" -o "$TEMP_DIR/${case_id}_review.html")
        if [ "$response" = "200" ]; then
            print_result "Review Page - $case_id" "PASS" "Review page loads successfully"
            
            # Check if timeline validation tab exists in HTML
            if grep -q "Timeline Validation" "$TEMP_DIR/${case_id}_review.html"; then
                print_result "Timeline Tab - $case_id" "PASS" "Timeline Validation tab found in HTML"
            else
                print_result "Timeline Tab - $case_id" "FAIL" "Timeline Validation tab not found in HTML"
            fi
            
            # Check if timeline validation JavaScript is loaded
            if grep -q "timeline-validation.js" "$TEMP_DIR/${case_id}_review.html"; then
                print_result "Timeline JavaScript - $case_id" "PASS" "Timeline validation script included"
            else
                print_result "Timeline JavaScript - $case_id" "FAIL" "Timeline validation script not found"
            fi
        else
            print_result "Review Page - $case_id" "FAIL" "Expected 200, got $response"
        fi
    done
}

# Function to test date parsing fixes
test_date_parsing() {
    echo ""
    echo -e "${BLUE}Testing Date Parsing Improvements...${NC}"
    
    # Test that June 15, 2025 format is properly parsed
    for case_id in "${VALID_TIMELINE_CASES[@]}"; do
        local file="$TEMP_DIR/${case_id}_timeline.json"
        if [ -f "$file" ] && command -v jq &> /dev/null; then
            # Check for filing date parsing
            local filing_date=$(jq -r '.key_dates.filing_date' "$file")
            if [ "$filing_date" != "null" ] && [ "$filing_date" != "" ]; then
                print_result "Filing Date Extraction - $case_id" "PASS" "Filing date extracted: $filing_date"
            else
                print_result "Filing Date Extraction - $case_id" "WARN" "No filing date found"
            fi
            
            # Check for June 15, 2025 specific format in document dates
            local june_dates=$(jq -r '.case_timeline.document_dates[]? | select(.raw_text | contains("June 15")) | .raw_text' "$file" 2>/dev/null | head -1)
            if [ -n "$june_dates" ]; then
                print_result "June Date Format - $case_id" "PASS" "June 15 format successfully processed"
            else
                print_result "June Date Format - $case_id" "WARN" "No June 15 format dates found"
            fi
        fi
    done
}

# Function to test error handling
test_error_handling() {
    echo ""
    echo -e "${BLUE}Testing Error Handling...${NC}"
    
    # Test invalid case ID
    response=$(curl -s -w "%{http_code}" "$DASHBOARD_URL/api/cases/INVALID_CASE/validate-timeline" -o /dev/null)
    if [ "$response" = "404" ]; then
        print_result "Invalid Case ID Handling" "PASS" "Returns 404 for invalid case"
    else
        print_result "Invalid Case ID Handling" "WARN" "Expected 404 for invalid case, got $response"
    fi
    
    # Test review page with invalid case
    response=$(curl -s -w "%{http_code}" "$DASHBOARD_URL/review?case_id=INVALID_CASE" -o /dev/null)
    if [ "$response" = "200" ]; then
        print_result "Review Page Error Handling" "PASS" "Review page handles invalid case gracefully"
    else
        print_result "Review Page Error Handling" "WARN" "Review page response: $response"
    fi
}

# Function to generate summary report
generate_summary() {
    echo ""
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}           TEST SUMMARY${NC}"
    echo -e "${BLUE}======================================${NC}"
    
    local total_tests=$(grep -c ":" "$LOG_FILE")
    local passed_tests=$(grep -c "PASS:" "$LOG_FILE")
    local failed_tests=$(grep -c "FAIL:" "$LOG_FILE")
    local warned_tests=$(grep -c "WARN:" "$LOG_FILE")
    
    echo "Total Tests: $total_tests"
    echo -e "${GREEN}Passed: $passed_tests${NC}"
    echo -e "${RED}Failed: $failed_tests${NC}"
    echo -e "${YELLOW}Warnings: $warned_tests${NC}"
    echo ""
    
    if [ "$failed_tests" -eq 0 ]; then
        echo -e "${GREEN}🎉 All critical tests passed! Timeline validation system is working correctly.${NC}"
        if [ "$warned_tests" -gt 0 ]; then
            echo -e "${YELLOW}Note: $warned_tests warnings found - review test details above.${NC}"
        fi
    else
        echo -e "${RED}❌ $failed_tests critical tests failed. Please review and fix issues before proceeding.${NC}"
    fi
    
    echo ""
    echo "Detailed log saved to: $LOG_FILE"
    echo ""
    echo -e "${BLUE}Test Cases Available:${NC}"
    for case_id in "${ALL_TEST_CASES[@]}"; do
        echo "- Review $case_id: $DASHBOARD_URL/review?case_id=$case_id"
    done
}

# Main test execution
main() {
    echo "Timeline Validation Test Suite Started: $(date)" > "$LOG_FILE"
    echo ""
    
    check_dashboard
    test_api_endpoints
    test_timeline_data_structure
    test_validation_logic
    test_date_parsing
    test_frontend_integration
    test_error_handling
    generate_summary
    
    # Save test data for inspection
    echo ""
    echo -e "${BLUE}Test artifacts saved in: $TEMP_DIR${NC}"
    echo "- Timeline JSON files: *_timeline.json"
    echo "- Review page HTML: *_review.html"
    echo "- Test log: test_results.log"
}

# Run the test suite
main "$@"