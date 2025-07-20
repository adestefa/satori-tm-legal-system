#!/bin/bash

# ==============================================================================
# TM Legal Server Health Check & Debug Test Suite
# ==============================================================================
# Purpose: Comprehensive testing script for TM legal document processing system
# Created: July 20, 2025
# Based on: Debugging session findings and permission architecture fixes
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="legal.satori-ai-tech.com"
VPS_HOST="legal-agent-vps"
TM_PATH="/opt/tm"
TEST_CASE="johnson"  # Primary test case
TEST_CASE_2="eman_youseef"  # Secondary test case

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}TM Legal Server Health Check & Debug Test Suite${NC}"
echo -e "${BLUE}Target: ${DOMAIN} (${VPS_HOST})${NC}"
echo -e "${BLUE}Date: $(date)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${CYAN}Test ${TESTS_TOTAL}: ${test_name}${NC}"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "  ${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Function to run test with output capture
run_test_with_output() {
    local test_name="$1"
    local test_command="$2"
    local success_pattern="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${CYAN}Test ${TESTS_TOTAL}: ${test_name}${NC}"
    
    local output
    output=$(eval "$test_command" 2>&1)
    
    if echo "$output" | grep -q "$success_pattern"; then
        echo -e "  ${GREEN}✅ PASS${NC} - Found: '$success_pattern'"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "  ${RED}❌ FAIL${NC} - Expected: '$success_pattern'"
        echo -e "  ${YELLOW}Output: $output${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo -e "${PURPLE}🔍 PHASE 1: INFRASTRUCTURE TESTS${NC}"
echo "================================================"

# Test 1: SSH Connectivity
run_test "SSH Connectivity to VPS" \
    "ssh -o ConnectTimeout=10 $VPS_HOST 'echo connected'" \
    "connected"

# Test 2: HTTPS Access
run_test_with_output "HTTPS Dashboard Access" \
    "curl -s -o /dev/null -w '%{http_code}' https://$DOMAIN/" \
    "200\|302"

# Test 3: SSL Certificate Validity
run_test_with_output "SSL Certificate Validity" \
    "echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate" \
    "notAfter"

# Test 4: Health Endpoint
run_test_with_output "Health Endpoint Response" \
    "curl -s https://$DOMAIN/health" \
    "Healthy"

echo ""
echo -e "${PURPLE}🔍 PHASE 2: SERVICE ARCHITECTURE TESTS${NC}"
echo "================================================"

# Test 5: TM Directory Ownership
run_test_with_output "TM Directory Ownership (tm:tm)" \
    "ssh $VPS_HOST 'ls -ld $TM_PATH'" \
    "tm tm"

# Test 6: Dashboard Service Status
run_test_with_output "Dashboard Service Running" \
    "ssh $VPS_HOST 'systemctl is-active tm-dashboard'" \
    "active"

# Test 7: Dashboard Service User
run_test_with_output "Dashboard Service User (tm)" \
    "ssh $VPS_HOST 'systemctl show tm-dashboard -p User'" \
    "User=tm"

# Test 8: Tiger Log File Permissions
run_test_with_output "Tiger Log File Permissions" \
    "ssh $VPS_HOST 'ls -la $TM_PATH/tiger/data/logs/satori_tiger.log'" \
    "tm tm"

echo ""
echo -e "${PURPLE}🔍 PHASE 3: GIT REPOSITORY TESTS${NC}"
echo "================================================"

# Test 9: Git Branch Status
run_test_with_output "Git Branch (feature/enhanced-defendant-extraction)" \
    "ssh $VPS_HOST 'cd $TM_PATH && git branch --show-current'" \
    "feature/enhanced-defendant-extraction"

# Test 10: Git Status Clean
run_test_with_output "Git Status Clean" \
    "ssh $VPS_HOST 'cd $TM_PATH && git status --porcelain | wc -l'" \
    "0"

# Test 11: Latest Commit Hash
run_test_with_output "Latest Commit Present" \
    "ssh $VPS_HOST 'cd $TM_PATH && git log --oneline -1'" \
    "fix: Resolve critical JavaScript and API endpoint errors"

echo ""
echo -e "${PURPLE}🔍 PHASE 4: TIGER SERVICE TESTS${NC}"
echo "================================================"

# Test 12: Tiger Service Info
run_test_with_output "Tiger Service Version" \
    "ssh $VPS_HOST 'cd $TM_PATH/tiger && ./run.sh info'" \
    "Satori Tiger"

# Test 13: Tiger Test Case Processing
echo -e "${CYAN}Test 13: Tiger Case Processing (Manual)${NC}"
if ssh $VPS_HOST "cd $TM_PATH/tiger && timeout 60 ./run.sh hydrated-json $TM_PATH/test-data/sync-test-cases/$TEST_CASE -o $TM_PATH/dashboard/outputs/test_health_check" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ PASS${NC} - Tiger processing completed"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${RED}❌ FAIL${NC} - Tiger processing failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 14: Generated File Ownership
run_test_with_output "Generated File Ownership (tm:tm)" \
    "ssh $VPS_HOST 'ls -la $TM_PATH/dashboard/outputs/test_health_check/*.json 2>/dev/null | head -1'" \
    "tm tm"

echo ""
echo -e "${PURPLE}🔍 PHASE 5: API ENDPOINT TESTS${NC}"
echo "================================================"

# Test 15: Cases List API
run_test_with_output "Cases List API" \
    "curl -s https://$DOMAIN/api/cases" \
    '\[\|\{'

# Test 16: Case Data API (Johnson)
run_test_with_output "Johnson Case Data API" \
    "curl -s https://$DOMAIN/api/cases/$TEST_CASE/data" \
    "case_information\|defendants"

# Test 17: Case Data API (Eman Youseef)
run_test_with_output "Eman Youseef Case Data API" \
    "curl -s https://$DOMAIN/api/cases/$TEST_CASE_2/data" \
    "case_information\|defendants"

# Test 18: Legal Claims API (POST)
run_test_with_output "Legal Claims API (POST)" \
    "curl -s -X POST https://$DOMAIN/api/cases/$TEST_CASE/legal-claims -H 'Content-Type: application/json' -d '{\"selections\": []}'" \
    "success\|message"

echo ""
echo -e "${PURPLE}🔍 PHASE 6: DOCUMENT GENERATION TESTS${NC}"
echo "================================================"

# Test 19: Complaint Generation
echo -e "${CYAN}Test 19: Complaint Generation${NC}"
if curl -s -X POST "https://$DOMAIN/api/cases/$TEST_CASE/generate-complaint" -H "Content-Type: application/json" | grep -q "message"; then
    echo -e "  ${GREEN}✅ PASS${NC} - Complaint generation initiated"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${RED}❌ FAIL${NC} - Complaint generation failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 20: Summons Generation
echo -e "${CYAN}Test 20: Summons Generation${NC}"
if curl -s -X POST "https://$DOMAIN/api/cases/$TEST_CASE/generate-summons" -H "Content-Type: application/json" | grep -q "message\|summons"; then
    echo -e "  ${GREEN}✅ PASS${NC} - Summons generation initiated"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${RED}❌ FAIL${NC} - Summons generation failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""
echo -e "${PURPLE}🔍 PHASE 7: JAVASCRIPT & FRONTEND TESTS${NC}"
echo "================================================"

# Test 21: Review Page Access
run_test_with_output "Review Page Access" \
    "curl -s https://$DOMAIN/review?case_id=$TEST_CASE" \
    "review\|html"

# Test 22: Static Assets (JavaScript)
run_test_with_output "JavaScript Assets Loading" \
    "curl -s https://$DOMAIN/static/js/review.js" \
    "fetchCaseData\|generateComplaint"

# Test 23: WebSocket Endpoint
run_test_with_output "WebSocket Endpoint Available" \
    "curl -s -I https://$DOMAIN/ws" \
    "400\|426"  # WebSocket upgrade required

echo ""
echo -e "${PURPLE}🔍 PHASE 8: KNOWN ISSUE REGRESSION TESTS${NC}"
echo "================================================"

# Test 24: htmlResponse Variable Scope (JavaScript Fix)
echo -e "${CYAN}Test 24: JavaScript htmlResponse Fix${NC}"
if ssh $VPS_HOST "grep -q 'let htmlContent' $TM_PATH/dashboard/static/js/review.js"; then
    echo -e "  ${GREEN}✅ PASS${NC} - JavaScript variable scope fix present"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${RED}❌ FAIL${NC} - JavaScript variable scope fix missing"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 25: Duplicate API Endpoint Fix
echo -e "${CYAN}Test 25: Duplicate API Endpoint Fix${NC}"
duplicate_count=$(ssh $VPS_HOST "grep -c '@app.post.*legal-claims' $TM_PATH/dashboard/main.py" || echo "0")
if [ "$duplicate_count" -eq 1 ]; then
    echo -e "  ${GREEN}✅ PASS${NC} - Only one legal-claims endpoint found"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${RED}❌ FAIL${NC} - Found $duplicate_count legal-claims endpoints (should be 1)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 26: Cross-Platform Script Fix
run_test_with_output "Cross-Platform Script Fix (cases.sh)" \
    "ssh $VPS_HOST 'grep -q \"detect_os_and_set_stat_commands\" $TM_PATH/scripts/cases.sh'" \
    "detect_os_and_set_stat_commands"

echo ""
echo -e "${PURPLE}🔍 PHASE 9: PERMISSION ARCHITECTURE VALIDATION${NC}"
echo "================================================"

# Test 27: Service User Consistency
echo -e "${CYAN}Test 27: Service User Consistency${NC}"
dashboard_user=$(ssh $VPS_HOST "systemctl show tm-dashboard -p User --value")
file_owner=$(ssh $VPS_HOST "stat -c '%U' $TM_PATH/dashboard/outputs/")
if [ "$dashboard_user" = "$file_owner" ]; then
    echo -e "  ${GREEN}✅ PASS${NC} - Service user ($dashboard_user) matches file owner ($file_owner)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${RED}❌ FAIL${NC} - Service user ($dashboard_user) != file owner ($file_owner)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 28: New File Creation Permissions
echo -e "${CYAN}Test 28: New File Creation Permissions${NC}"
ssh $VPS_HOST "su - tm -c 'touch $TM_PATH/dashboard/outputs/permission_test.txt'" > /dev/null 2>&1
if ssh $VPS_HOST "ls -la $TM_PATH/dashboard/outputs/permission_test.txt | grep -q 'tm tm'"; then
    echo -e "  ${GREEN}✅ PASS${NC} - New files created with correct ownership"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    ssh $VPS_HOST "rm -f $TM_PATH/dashboard/outputs/permission_test.txt" > /dev/null 2>&1
else
    echo -e "  ${RED}❌ FAIL${NC} - New files created with incorrect ownership"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""
echo -e "${PURPLE}🔍 PHASE 10: PERFORMANCE & RESOURCE TESTS${NC}"
echo "================================================"

# Test 29: Memory Usage
echo -e "${CYAN}Test 29: Dashboard Memory Usage${NC}"
memory_usage=$(ssh $VPS_HOST "systemctl show tm-dashboard -p MemoryCurrent --value")
memory_mb=$((memory_usage / 1024 / 1024))
if [ $memory_mb -lt 500 ]; then
    echo -e "  ${GREEN}✅ PASS${NC} - Memory usage: ${memory_mb}MB (< 500MB limit)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${YELLOW}⚠️ WARNING${NC} - Memory usage: ${memory_mb}MB (high)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test 30: Disk Space
echo -e "${CYAN}Test 30: Disk Space Availability${NC}"
disk_usage=$(ssh $VPS_HOST "df / | awk 'NR==2 {print \$5}' | sed 's/%//'")
if [ $disk_usage -lt 80 ]; then
    echo -e "  ${GREEN}✅ PASS${NC} - Disk usage: ${disk_usage}% (< 80% limit)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "  ${YELLOW}⚠️ WARNING${NC} - Disk usage: ${disk_usage}% (high)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Cleanup test files
echo ""
echo -e "${CYAN}🧹 Cleaning up test files...${NC}"
ssh $VPS_HOST "rm -rf $TM_PATH/dashboard/outputs/test_health_check" > /dev/null 2>&1

# Final Report
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}TEST SUITE SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "📊 ${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "📊 ${RED}Tests Failed: $TESTS_FAILED${NC}"
echo -e "📊 ${CYAN}Total Tests: $TESTS_TOTAL${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED! System is fully operational.${NC}"
    echo -e "${GREEN}✅ TM Legal Document Processing Platform: HEALTHY${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️ $TESTS_FAILED test(s) failed. System requires attention.${NC}"
    echo -e "${YELLOW}📋 Review failed tests above for specific issues.${NC}"
    exit 1
fi