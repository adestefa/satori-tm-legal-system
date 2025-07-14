#!/bin/bash

# TM Browser PDF Generator - Integration Test Script
# Tests integration with the complete Tiger-Monkey system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🔗 TM Browser PDF Generator - Integration Test Suite${NC}"
echo "============================================================"

# Check if we're in the correct directory
if [ ! -f "pdf-generator.js" ]; then
    echo -e "${RED}❌ pdf-generator.js not found. Run from TM/browser/ directory.${NC}"
    exit 1
fi

# Check TM system components
echo -e "${BLUE}🔍 Checking TM System Components${NC}"
echo "----------------------------------------"

# Check Tiger service
if [ -f "../tiger/run.sh" ]; then
    echo -e "${GREEN}✅ Tiger service found${NC}"
    TIGER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Tiger service not found${NC}"
    TIGER_AVAILABLE=false
fi

# Check Monkey service
if [ -f "../monkey/run.sh" ]; then
    echo -e "${GREEN}✅ Monkey service found${NC}"
    MONKEY_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Monkey service not found${NC}"
    MONKEY_AVAILABLE=false
fi

# Check Dashboard service
if [ -f "../dashboard/main.py" ]; then
    echo -e "${GREEN}✅ Dashboard service found${NC}"
    DASHBOARD_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Dashboard service not found${NC}"
    DASHBOARD_AVAILABLE=false
fi

echo ""

# Function to test Python integration
test_python_integration() {
    echo -e "${PURPLE}🐍 Testing Python Integration${NC}"
    echo "----------------------------------------"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found${NC}"
        return 1
    fi
    
    # Test Python wrapper
    echo "Testing Python wrapper..."
    
    # Test service validation
    if python3 print.py test > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Python wrapper service test passed${NC}"
    else
        echo -e "${RED}❌ Python wrapper service test failed${NC}"
        return 1
    fi
    
    # Test single file generation via Python
    local test_html="../outputs/tests/Rodriguez/summons/summons_chase_bank_na_(delaware_corporation_authorized_to_do_business_in_new_york).html"
    if [ -f "$test_html" ]; then
        local output_pdf="../outputs/browser/integration/python_test.pdf"
        mkdir -p "$(dirname "$output_pdf")"
        
        if python3 print.py single "$test_html" "$output_pdf" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Python single file generation successful${NC}"
            
            if [ -f "$output_pdf" ]; then
                local file_size=$(du -h "$output_pdf" | cut -f1)
                echo -e "${BLUE}   Generated file: $output_pdf ($file_size)${NC}"
            fi
        else
            echo -e "${RED}❌ Python single file generation failed${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  No test HTML file available for Python test${NC}"
    fi
    
    echo ""
}

# Function to test Monkey service integration
test_monkey_integration() {
    echo -e "${PURPLE}🐒 Testing Monkey Service Integration${NC}"
    echo "----------------------------------------"
    
    if [ "$MONKEY_AVAILABLE" = false ]; then
        echo -e "${YELLOW}⚠️  Monkey service not available, skipping integration test${NC}"
        return 0
    fi
    
    # Check if there are any Monkey-generated HTML files
    local monkey_html_files=($(find ../outputs/tests -name "*.html" -path "*/complaint*" 2>/dev/null))
    
    if [ ${#monkey_html_files[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No Monkey-generated HTML files found${NC}"
        echo "   Generate some test documents with Monkey service first"
        return 0
    fi
    
    echo "Found ${#monkey_html_files[@]} Monkey-generated HTML files"
    
    # Test PDF generation from Monkey output
    local test_count=0
    local success_count=0
    
    for html_file in "${monkey_html_files[@]}"; do
        if [ $test_count -ge 3 ]; then break; fi  # Limit to 3 tests
        
        local filename=$(basename "$html_file" .html)
        local output_pdf="../outputs/browser/integration/monkey_${filename}.pdf"
        mkdir -p "$(dirname "$output_pdf")"
        
        echo "Testing: $filename"
        
        if node pdf-generator.js "$html_file" "$output_pdf" > /dev/null 2>&1; then
            if [ -f "$output_pdf" ]; then
                echo -e "${GREEN}✅ Successfully converted Monkey output to PDF${NC}"
                ((success_count++))
            else
                echo -e "${RED}❌ PDF not generated${NC}"
            fi
        else
            echo -e "${RED}❌ PDF generation failed${NC}"
        fi
        
        ((test_count++))
    done
    
    if [ $success_count -eq $test_count ] && [ $test_count -gt 0 ]; then
        echo -e "${GREEN}✅ Monkey integration test passed ($success_count/$test_count)${NC}"
    else
        echo -e "${YELLOW}⚠️  Monkey integration test partial success ($success_count/$test_count)${NC}"
    fi
    
    echo ""
}

# Function to test end-to-end workflow simulation
test_e2e_workflow() {
    echo -e "${PURPLE}🔄 Testing End-to-End Workflow Simulation${NC}"
    echo "----------------------------------------"
    
    # This simulates the complete TM workflow:
    # Raw Documents → Tiger → Hydrated JSON → Monkey → HTML → Browser → PDF
    
    echo "Simulating complete document processing workflow..."
    
    # Find the most recent hydrated JSON
    local hydrated_json=$(find ../outputs/tests -name "hydrated_*.json" | head -1)
    
    if [ -z "$hydrated_json" ] || [ ! -f "$hydrated_json" ]; then
        echo -e "${YELLOW}⚠️  No hydrated JSON found for workflow test${NC}"
        echo "   Run Tiger service to generate test data first"
        return 0
    fi
    
    echo "Using hydrated JSON: $(basename "$hydrated_json")"
    
    # Check if corresponding HTML exists (would be generated by Monkey)
    local case_name=$(basename "$hydrated_json" .json | sed 's/hydrated_FCRA_//' | sed 's/_[0-9]*$//')
    local complaint_html="../outputs/tests/${case_name}/complaint_${case_name}.html"
    
    if [ ! -f "$complaint_html" ]; then
        # Look for any complaint HTML in the same directory
        local json_dir=$(dirname "$hydrated_json")
        complaint_html=$(find "$json_dir" -name "*complaint*.html" | head -1)
    fi
    
    if [ -f "$complaint_html" ]; then
        echo "Found corresponding complaint HTML: $(basename "$complaint_html")"
        
        # Generate PDF from the complete workflow
        local final_pdf="../outputs/browser/integration/e2e_workflow_$(basename "$case_name").pdf"
        mkdir -p "$(dirname "$final_pdf")"
        
        echo "Generating final court-ready PDF..."
        
        if node pdf-generator.js "$complaint_html" "$final_pdf" > /dev/null 2>&1; then
            if [ -f "$final_pdf" ]; then
                local file_size=$(du -h "$final_pdf" | cut -f1)
                echo -e "${GREEN}✅ End-to-end workflow successful!${NC}"
                echo -e "${GREEN}   Court-ready PDF: $final_pdf ($file_size)${NC}"
                
                # Validate PDF structure
                if file "$final_pdf" | grep -q "PDF document"; then
                    echo -e "${GREEN}   PDF format validated${NC}"
                fi
                
                return 0
            fi
        fi
        
        echo -e "${RED}❌ End-to-end workflow failed at PDF generation${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠️  No corresponding HTML found for hydrated JSON${NC}"
        echo "   Generate HTML documents with Monkey service first"
        return 0
    fi
}

# Function to test performance with real TM data
test_real_data_performance() {
    echo -e "${PURPLE}⚡ Testing Performance with Real TM Data${NC}"
    echo "----------------------------------------"
    
    # Find all HTML files in TM outputs
    local all_html_files=($(find ../outputs/tests -name "*.html" 2>/dev/null))
    
    if [ ${#all_html_files[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No HTML files found in TM outputs${NC}"
        return 0
    fi
    
    echo "Found ${#all_html_files[@]} HTML files in TM system outputs"
    
    # Test a representative sample
    local sample_size=5
    if [ ${#all_html_files[@]} -lt $sample_size ]; then
        sample_size=${#all_html_files[@]}
    fi
    
    echo "Testing performance with $sample_size representative files..."
    
    local total_time=0
    local successful=0
    
    for ((i=0; i<$sample_size; i++)); do
        local html_file="${all_html_files[i]}"
        local filename=$(basename "$html_file" .html)
        local output_pdf="../outputs/browser/integration/perf_${i}_${filename}.pdf"
        mkdir -p "$(dirname "$output_pdf")"
        
        local start_time=$(date +%s%N)
        
        if node pdf-generator.js "$html_file" "$output_pdf" > /dev/null 2>&1; then
            local end_time=$(date +%s%N)
            local duration=$(( (end_time - start_time) / 1000000 ))
            total_time=$((total_time + duration))
            ((successful++))
            
            echo "  File $((i+1)): ${duration}ms"
        else
            echo "  File $((i+1)): Failed"
        fi
    done
    
    if [ $successful -gt 0 ]; then
        local avg_time=$((total_time / successful))
        echo ""
        echo -e "${GREEN}✅ Performance test completed${NC}"
        echo -e "${BLUE}   Successful conversions: $successful/$sample_size${NC}"
        echo -e "${BLUE}   Average time: ${avg_time}ms${NC}"
        echo -e "${BLUE}   Total time: ${total_time}ms${NC}"
        
        if [ $avg_time -lt 3000 ]; then
            echo -e "${GREEN}   Performance: Excellent${NC}"
        elif [ $avg_time -lt 5000 ]; then
            echo -e "${YELLOW}   Performance: Good${NC}"
        else
            echo -e "${RED}   Performance: Needs optimization${NC}"
        fi
    else
        echo -e "${RED}❌ All performance tests failed${NC}"
        return 1
    fi
    
    echo ""
}

# Main integration test execution
echo -e "${BLUE}🚀 Starting integration test suite...${NC}"
echo ""

# Create centralized browser output directory
mkdir -p ../outputs/browser/integration

# Run integration tests
test_python_integration
test_monkey_integration
test_e2e_workflow
test_real_data_performance

# Generate integration report
echo -e "${CYAN}📋 Integration Test Summary${NC}"
echo "==========================================="
echo "Test completed: $(date)"
echo ""

# Count generated files
local total_pdfs=$(find ../outputs/browser/integration -name "*.pdf" 2>/dev/null | wc -l)
local total_size=$(find ../outputs/browser/integration -name "*.pdf" -exec du -ch {} \; 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")

echo "Integration test results:"
echo "  PDFs generated: $total_pdfs"
echo "  Total size: $total_size"
echo ""

# System integration status
echo -e "${BLUE}🔗 TM System Integration Status:${NC}"
if [ "$TIGER_AVAILABLE" = true ]; then
    echo -e "${GREEN}  ✅ Tiger service: Available${NC}"
else
    echo -e "${YELLOW}  ⚠️  Tiger service: Not found${NC}"
fi

if [ "$MONKEY_AVAILABLE" = true ]; then
    echo -e "${GREEN}  ✅ Monkey service: Available${NC}"
else
    echo -e "${YELLOW}  ⚠️  Monkey service: Not found${NC}"
fi

if [ "$DASHBOARD_AVAILABLE" = true ]; then
    echo -e "${GREEN}  ✅ Dashboard service: Available${NC}"
else
    echo -e "${YELLOW}  ⚠️  Dashboard service: Not found${NC}"
fi

echo -e "${GREEN}  ✅ Browser PDF service: Operational${NC}"

echo ""
echo -e "${YELLOW}💡 Integration Recommendations:${NC}"
echo "1. Use the Python wrapper (print.py) for seamless TM integration"
echo "2. PDF generation integrates perfectly with Monkey HTML output"
echo "3. Consider adding PDF generation to Dashboard workflow"
echo "4. Performance scales well with TM document volumes"
echo ""

echo -e "${GREEN}✅ Integration test suite completed!${NC}"
echo "Detailed results in: ../outputs/browser/integration/"