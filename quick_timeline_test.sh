#!/bin/bash

# Quick Timeline Validation Test
# Simple test to verify timeline validation is working correctly
# Usage: ./quick_timeline_test.sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

DASHBOARD_URL="http://127.0.0.1:8000"

echo -e "${BLUE}Timeline Validation Quick Test${NC}"
echo "=================================="
echo ""

# Check dashboard is running
echo "1. Checking dashboard..."
if curl -s "$DASHBOARD_URL" > /dev/null; then
    echo -e "   ${GREEN}✓ Dashboard is running${NC}"
else
    echo -e "   ${RED}✗ Dashboard not running - start with ./dashboard/start.sh${NC}"
    exit 1
fi

# Test Rodriguez timeline validation API
echo "2. Testing Rodriguez timeline validation..."
response=$(curl -s "$DASHBOARD_URL/api/cases/Rodriguez/validate-timeline")
if echo "$response" | jq -e '.validation_score' > /dev/null 2>&1; then
    score=$(echo "$response" | jq -r '.validation_score')
    valid=$(echo "$response" | jq -r '.is_chronologically_valid')
    errors=$(echo "$response" | jq -r '.validation_details.errors | length')
    echo -e "   ${GREEN}✓ Timeline API working${NC}"
    echo "     - Validation Score: $score/100"
    echo "     - Chronologically Valid: $valid"
    echo "     - Critical Errors: $errors"
else
    echo -e "   ${RED}✗ Timeline API failed${NC}"
    exit 1
fi

# Test review page
echo "3. Testing review page..."
if curl -s "$DASHBOARD_URL/review?case_id=Rodriguez" | grep -q "Timeline Validation"; then
    echo -e "   ${GREEN}✓ Review page has timeline tab${NC}"
else
    echo -e "   ${RED}✗ Timeline tab not found${NC}"
    exit 1
fi

# Test JavaScript integration
echo "4. Testing JavaScript integration..."
if curl -s "$DASHBOARD_URL/review?case_id=Rodriguez" | grep -q "timeline-validation.js"; then
    echo -e "   ${GREEN}✓ Timeline JavaScript loaded${NC}"
else
    echo -e "   ${RED}✗ Timeline JavaScript not found${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 All tests passed! Timeline validation system is working.${NC}"
echo ""
echo "Manual test: Navigate to $DASHBOARD_URL/review?case_id=Rodriguez"
echo "and click the 'Timeline Validation' tab to see the UI in action."