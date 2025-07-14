#!/bin/bash

# TM Browser PDF Generator - Single File Test Script
# Tests PDF generation with individual HTML files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 TM Browser PDF Generator - Single File Test${NC}"
echo "=================================================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js first.${NC}"
    exit 1
fi

# Check if pdf-generator.js exists
if [ ! -f "pdf-generator.js" ]; then
    echo -e "${RED}❌ pdf-generator.js not found. Run from TM/browser/ directory.${NC}"
    exit 1
fi

# Function to test single file
test_single_file() {
    local input_file="$1"
    local output_file="$2"
    local test_name="$3"
    
    echo ""
    echo -e "${YELLOW}📄 Testing: ${test_name}${NC}"
    echo "Input:  $input_file"
    echo "Output: $output_file"
    echo "----------------------------------------"
    
    if [ ! -f "$input_file" ]; then
        echo -e "${RED}❌ Input file not found: $input_file${NC}"
        return 1
    fi
    
    # Create output directory if needed
    mkdir -p "$(dirname "$output_file")"
    
    # Run PDF generation with timing
    start_time=$(date +%s%N)
    
    if node pdf-generator.js "$input_file" "$output_file"; then
        end_time=$(date +%s%N)
        duration=$(( (end_time - start_time) / 1000000 ))
        
        # Check if PDF was created
        if [ -f "$output_file" ]; then
            file_size=$(du -h "$output_file" | cut -f1)
            echo -e "${GREEN}✅ Success! Generated in ${duration}ms, Size: ${file_size}${NC}"
            
            # Validate PDF format
            if file "$output_file" | grep -q "PDF document"; then
                echo -e "${GREEN}✅ Valid PDF format confirmed${NC}"
            else
                echo -e "${RED}❌ Invalid PDF format${NC}"
                return 1
            fi
        else
            echo -e "${RED}❌ PDF file not created${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ PDF generation failed${NC}"
        return 1
    fi
}

# Test with command line argument
if [ $# -eq 1 ]; then
    input_file="$1"
    output_file="../outputs/browser/$(basename "$input_file" .html).pdf"
    test_single_file "$input_file" "$output_file" "Custom File"
    exit 0
elif [ $# -eq 2 ]; then
    test_single_file "$1" "$2" "Custom File"
    exit 0
fi

# Default test suite
echo -e "${BLUE}Running default test suite...${NC}"

# Create centralized browser output directory
mkdir -p ../outputs/browser

# Test 1: Rodriguez Chase summons
test_single_file \
    "../outputs/tests/Rodriguez/summons/summons_chase_bank_na_(delaware_corporation_authorized_to_do_business_in_new_york).html" \
    "../outputs/browser/rodriguez_chase_summons.pdf" \
    "Rodriguez Chase Bank Summons"

# Test 2: Youssef Equifax summons  
test_single_file \
    "../outputs/tests/youssef/summons/summons_equifax_information_services_llc_(georgia_corporation_authorized_to_do_business_in_new_york).html" \
    "../outputs/browser/youssef_equifax_summons.pdf" \
    "Youssef Equifax Summons"

# Test 3: Youssef TD Bank summons
test_single_file \
    "../outputs/tests/youssef/summons/summons_td_bank_na_(delaware_corporation_authorized_to_do_business_in_new_york).html" \
    "../outputs/browser/youssef_td_bank_summons.pdf" \
    "Youssef TD Bank Summons"

# Test 4: Rodriguez Experian summons
test_single_file \
    "../outputs/tests/Rodriguez/summons/summons_experian_information_solutions_inc_(ohio_corporation_authorized_to_do_business_in_new_york).html" \
    "../outputs/browser/rodriguez_experian_summons.pdf" \
    "Rodriguez Experian Summons"

echo ""
echo -e "${GREEN}🎯 Single file test suite completed!${NC}"
echo ""
echo -e "${BLUE}📊 Test Results Summary:${NC}"
ls -lh ../outputs/browser/*.pdf 2>/dev/null | while read -r line; do
    echo "   $line"
done

echo ""
echo -e "${YELLOW}💡 Usage Examples:${NC}"
echo "   ./test-single.sh path/to/file.html"
echo "   ./test-single.sh input.html output.pdf" 
echo "   ./test-single.sh  # Run full test suite"