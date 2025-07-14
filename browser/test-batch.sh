#!/bin/bash

# TM Browser PDF Generator - Batch Processing Test Script
# Tests PDF generation with multiple HTML files simultaneously

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 TM Browser PDF Generator - Batch Processing Test${NC}"
echo "====================================================="

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

# Function to test batch processing
test_batch_processing() {
    local input_dir="$1"
    local output_dir="$2"
    local test_name="$3"
    
    echo ""
    echo -e "${YELLOW}📁 Testing: ${test_name}${NC}"
    echo "Input Directory:  $input_dir"
    echo "Output Directory: $output_dir"
    echo "----------------------------------------"
    
    if [ ! -d "$input_dir" ]; then
        echo -e "${RED}❌ Input directory not found: $input_dir${NC}"
        return 1
    fi
    
    # Count HTML files
    html_count=$(find "$input_dir" -name "*.html" -type f | wc -l)
    echo -e "${BLUE}📄 Found ${html_count} HTML files${NC}"
    
    if [ "$html_count" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No HTML files found in directory${NC}"
        return 1
    fi
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Run batch processing with timing
    echo -e "${PURPLE}🔄 Processing batch...${NC}"
    start_time=$(date +%s%N)
    
    if node pdf-generator.js --batch "$input_dir" "$output_dir"; then
        end_time=$(date +%s%N)
        total_duration=$(( (end_time - start_time) / 1000000 ))
        
        # Count generated PDFs
        pdf_count=$(find "$output_dir" -name "*.pdf" -type f | wc -l)
        
        echo ""
        echo -e "${GREEN}✅ Batch processing completed!${NC}"
        echo -e "${GREEN}   Total time: ${total_duration}ms${NC}"
        echo -e "${GREEN}   HTML files: ${html_count}${NC}"
        echo -e "${GREEN}   PDF files generated: ${pdf_count}${NC}"
        
        if [ "$pdf_count" -eq "$html_count" ]; then
            echo -e "${GREEN}   Success rate: 100%${NC}"
        else
            echo -e "${YELLOW}   Success rate: $(( pdf_count * 100 / html_count ))%${NC}"
        fi
        
        # Calculate average time per file
        if [ "$pdf_count" -gt 0 ]; then
            avg_time=$(( total_duration / pdf_count ))
            echo -e "${BLUE}   Average time per file: ${avg_time}ms${NC}"
        fi
        
        # Show file sizes
        echo ""
        echo -e "${BLUE}📊 Generated PDF files:${NC}"
        find "$output_dir" -name "*.pdf" -type f -exec ls -lh {} \; | while read -r line; do
            echo "   $line"
        done
        
    else
        echo -e "${RED}❌ Batch processing failed${NC}"
        return 1
    fi
}

# Function to test specific TM directories
test_tm_directories() {
    echo -e "${PURPLE}🏛️  Testing TM System Directories${NC}"
    
    # Test Rodriguez summons
    if [ -d "../outputs/tests/Rodriguez/summons" ]; then
        test_batch_processing \
            "../outputs/tests/Rodriguez/summons" \
            "../outputs/browser/batch/rodriguez-summons" \
            "Rodriguez Summons Collection"
    fi
    
    # Test Youssef summons
    if [ -d "../outputs/tests/youssef/summons" ]; then
        test_batch_processing \
            "../outputs/tests/youssef/summons" \
            "../outputs/browser/batch/youssef-summons" \
            "Youssef Summons Collection"
    fi
    
    # Test all summons files
    if [ -d "../outputs/tests" ]; then
        echo ""
        echo -e "${PURPLE}🔍 Searching for all HTML files in TM outputs...${NC}"
        find ../outputs/tests -name "*.html" -type f > /tmp/tm_html_files.txt
        html_file_count=$(wc -l < /tmp/tm_html_files.txt)
        
        if [ "$html_file_count" -gt 0 ]; then
            echo -e "${BLUE}Found ${html_file_count} HTML files across all TM outputs${NC}"
            
            # Create a temporary directory with all HTML files
            temp_dir="../outputs/browser/batch/all-tm-files"
            mkdir -p "$temp_dir"
            
            # Copy all HTML files to temp directory
            counter=1
            while IFS= read -r html_file; do
                if [ -f "$html_file" ]; then
                    cp "$html_file" "$temp_dir/$(printf "%03d" $counter)_$(basename "$html_file")"
                    ((counter++))
                fi
            done < /tmp/tm_html_files.txt
            
            test_batch_processing \
                "$temp_dir" \
                "../outputs/browser/batch/all-tm-outputs" \
                "Complete TM System HTML Files"
            
            # Cleanup temp files
            rm -f /tmp/tm_html_files.txt
        else
            echo -e "${YELLOW}⚠️  No HTML files found in TM outputs${NC}"
        fi
    fi
}

# Test with command line arguments
if [ $# -eq 2 ]; then
    test_batch_processing "$1" "$2" "Custom Batch"
    exit 0
elif [ $# -eq 1 ]; then
    output_dir="../outputs/browser/batch/$(basename "$1")"
    test_batch_processing "$1" "$output_dir" "Custom Directory"
    exit 0
fi

# Default test suite
echo -e "${BLUE}Running default batch test suite...${NC}"

# Create centralized browser output directory
mkdir -p ../outputs/browser/batch

# Run TM directory tests
test_tm_directories

echo ""
echo -e "${GREEN}🎯 Batch processing test suite completed!${NC}"
echo ""
echo -e "${BLUE}📊 Complete Test Results Summary:${NC}"
find ../outputs/browser/batch -name "*.pdf" -type f | wc -l | xargs echo "   Total PDFs generated:"
find ../outputs/browser/batch -name "*.pdf" -type f -exec du -ch {} \; | tail -1 | awk '{print "   Total size: " $1}'

echo ""
echo -e "${YELLOW}💡 Usage Examples:${NC}"
echo "   ./test-batch.sh path/to/html/directory"
echo "   ./test-batch.sh input/dir output/dir"
echo "   ./test-batch.sh  # Run full TM system test"

echo ""
echo -e "${BLUE}🔍 Performance Analysis:${NC}"
pdf_files=$(find ../outputs/browser/batch -name "*.pdf" -type f)
if [ -n "$pdf_files" ]; then
    echo "$pdf_files" | while read -r pdf_file; do
        pages=$(pdfinfo "$pdf_file" 2>/dev/null | grep "Pages:" | awk '{print $2}' || echo "N/A")
        size=$(du -h "$pdf_file" | cut -f1)
        echo "   $(basename "$pdf_file"): ${pages} pages, ${size}"
    done 2>/dev/null || echo "   Install pdfinfo for detailed page analysis"
fi