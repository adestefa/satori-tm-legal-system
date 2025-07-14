#!/bin/bash

# TM Browser PDF Generator - Cleanup and Maintenance Script
# Manages test outputs, temporary files, and system maintenance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 TM Browser PDF Generator - Cleanup & Maintenance${NC}"
echo "======================================================"

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --all             Clean all test outputs and temporary files"
    echo "  --test-outputs    Clean test output directories only"
    echo "  --benchmarks      Clean benchmark results only"
    echo "  --node-modules    Clean and reinstall Node.js dependencies"
    echo "  --logs            Clean any log files"
    echo "  --dry-run         Show what would be cleaned without deleting"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./cleanup.sh --all                 # Clean everything"
    echo "  ./cleanup.sh --test-outputs        # Clean test outputs only"
    echo "  ./cleanup.sh --dry-run --all       # Preview cleanup without deleting"
}

# Function to get directory size
get_dir_size() {
    if [ -d "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1
    else
        echo "0B"
    fi
}

# Function to clean test outputs
clean_test_outputs() {
    echo -e "${YELLOW}🗂️  Cleaning test outputs...${NC}"
    
    local dirs_to_clean=(
        "test-outputs"
        "benchmark-results"
        "../outputs/browser"
    )
    
    for dir in "${dirs_to_clean[@]}"; do
        if [ -d "$dir" ]; then
            local size=$(get_dir_size "$dir")
            echo "  $dir/ ($size)"
            
            if [ "$DRY_RUN" != "true" ]; then
                rm -rf "$dir"
                echo -e "${GREEN}    ✅ Cleaned${NC}"
            else
                echo -e "${BLUE}    📋 Would be cleaned${NC}"
            fi
        else
            echo "  $dir/ (not found)"
        fi
    done
}

# Function to clean benchmark results
clean_benchmarks() {
    echo -e "${YELLOW}📊 Cleaning benchmark results...${NC}"
    
    local benchmark_dirs=(
        "benchmark-results"
        "../outputs/browser/benchmarks"
    )
    
    for dir in "${benchmark_dirs[@]}"; do
        if [ -d "$dir" ]; then
            local size=$(get_dir_size "$dir")
            echo "  $dir/ ($size)"
            
            if [ "$DRY_RUN" != "true" ]; then
                rm -rf "$dir"
                echo -e "${GREEN}    ✅ Cleaned${NC}"
            else
                echo -e "${BLUE}    📋 Would be cleaned${NC}"
            fi
        else
            echo "  $dir/ (not found)"
        fi
    done
}

# Function to clean Node.js dependencies
clean_node_modules() {
    echo -e "${YELLOW}📦 Cleaning Node.js dependencies...${NC}"
    
    if [ -d "node_modules" ]; then
        local size=$(get_dir_size "node_modules")
        echo "  node_modules/ ($size)"
        
        if [ "$DRY_RUN" != "true" ]; then
            rm -rf node_modules
            echo -e "${GREEN}    ✅ Cleaned${NC}"
            
            echo "  Reinstalling dependencies..."
            if npm install > /dev/null 2>&1; then
                echo -e "${GREEN}    ✅ Dependencies reinstalled${NC}"
            else
                echo -e "${RED}    ❌ Failed to reinstall dependencies${NC}"
                return 1
            fi
        else
            echo -e "${BLUE}    📋 Would be cleaned and reinstalled${NC}"
        fi
    else
        echo "  node_modules/ (not found)"
    fi
}

# Function to clean log files
clean_logs() {
    echo -e "${YELLOW}📝 Cleaning log files...${NC}"
    
    local log_patterns=(
        "*.log"
        "npm-debug.log*"
        ".npm"
    )
    
    for pattern in "${log_patterns[@]}"; do
        local files=$(find . -maxdepth 1 -name "$pattern" 2>/dev/null)
        if [ -n "$files" ]; then
            echo "$files" | while read -r file; do
                if [ -f "$file" ] || [ -d "$file" ]; then
                    local size=$(du -sh "$file" 2>/dev/null | cut -f1)
                    echo "  $file ($size)"
                    
                    if [ "$DRY_RUN" != "true" ]; then
                        rm -rf "$file"
                        echo -e "${GREEN}    ✅ Cleaned${NC}"
                    else
                        echo -e "${BLUE}    📋 Would be cleaned${NC}"
                    fi
                fi
            done
        fi
    done
}

# Function to clean temporary files
clean_temp_files() {
    echo -e "${YELLOW}🗃️  Cleaning temporary files...${NC}"
    
    local temp_patterns=(
        "*.tmp"
        "*.temp"
        ".DS_Store"
        "Thumbs.db"
    )
    
    for pattern in "${temp_patterns[@]}"; do
        local files=$(find . -name "$pattern" 2>/dev/null)
        if [ -n "$files" ]; then
            echo "$files" | while read -r file; do
                if [ -f "$file" ]; then
                    echo "  $file"
                    
                    if [ "$DRY_RUN" != "true" ]; then
                        rm -f "$file"
                        echo -e "${GREEN}    ✅ Cleaned${NC}"
                    else
                        echo -e "${BLUE}    📋 Would be cleaned${NC}"
                    fi
                fi
            done
        fi
    done
}

# Function to show current disk usage
show_disk_usage() {
    echo -e "${PURPLE}💾 Current disk usage:${NC}"
    
    local dirs=(
        "test-outputs"
        "benchmark-results"
        "../outputs/browser"
        "node_modules"
    )
    
    local total_size=0
    
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            local size=$(get_dir_size "$dir")
            echo "  $dir/: $size"
        fi
    done
    
    # Show PDF files
    local pdf_count=$(find . -name "*.pdf" 2>/dev/null | wc -l)
    if [ $pdf_count -gt 0 ]; then
        local pdf_size=$(find . -name "*.pdf" -exec du -ch {} \; 2>/dev/null | tail -1 | awk '{print $1}' || echo "0B")
        echo "  PDF files: $pdf_count files, $pdf_size"
    fi
}

# Function to run maintenance checks
run_maintenance() {
    echo -e "${PURPLE}🔧 Running maintenance checks...${NC}"
    
    # Check Node.js installation
    if command -v node &> /dev/null; then
        local node_version=$(node --version)
        echo -e "${GREEN}  ✅ Node.js: $node_version${NC}"
    else
        echo -e "${RED}  ❌ Node.js not found${NC}"
    fi
    
    # Check npm packages
    if [ -f "package.json" ] && [ -d "node_modules" ]; then
        local npm_outdated=$(npm outdated --json 2>/dev/null || echo "{}")
        if [ "$npm_outdated" = "{}" ]; then
            echo -e "${GREEN}  ✅ npm packages up to date${NC}"
        else
            echo -e "${YELLOW}  ⚠️  npm packages have updates available${NC}"
            echo "      Run 'npm update' to update packages"
        fi
    fi
    
    # Check for corrupted PDFs
    local corrupted=0
    while IFS= read -r -d '' pdf_file; do
        if ! file "$pdf_file" | grep -q "PDF document"; then
            echo -e "${RED}  ❌ Corrupted PDF: $pdf_file${NC}"
            ((corrupted++))
        fi
    done < <(find . -name "*.pdf" -print0 2>/dev/null)
    
    if [ $corrupted -eq 0 ]; then
        echo -e "${GREEN}  ✅ All PDF files are valid${NC}"
    fi
    
    # Check disk space
    local available_space=$(df . 2>/dev/null | tail -1 | awk '{print $4}' || echo "Unknown")
    if [ "$available_space" != "Unknown" ] && [ $available_space -lt 1000000 ]; then  # Less than ~1GB
        echo -e "${YELLOW}  ⚠️  Low disk space: $(df -h . | tail -1 | awk '{print $4}') available${NC}"
    else
        echo -e "${GREEN}  ✅ Sufficient disk space available${NC}"
    fi
}

# Parse command line arguments
DRY_RUN=false
CLEAN_ALL=false
CLEAN_TEST_OUTPUTS=false
CLEAN_BENCHMARKS=false
CLEAN_NODE_MODULES=false
CLEAN_LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --test-outputs)
            CLEAN_TEST_OUTPUTS=true
            shift
            ;;
        --benchmarks)
            CLEAN_BENCHMARKS=true
            shift
            ;;
        --node-modules)
            CLEAN_NODE_MODULES=true
            shift
            ;;
        --logs)
            CLEAN_LOGS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# If no specific options, show usage
if [ "$CLEAN_ALL" = false ] && [ "$CLEAN_TEST_OUTPUTS" = false ] && [ "$CLEAN_BENCHMARKS" = false ] && [ "$CLEAN_NODE_MODULES" = false ] && [ "$CLEAN_LOGS" = false ]; then
    show_usage
    exit 1
fi

# Show current status
echo ""
show_disk_usage
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}🔍 DRY RUN MODE - No files will be deleted${NC}"
    echo ""
fi

# Execute cleanup operations
if [ "$CLEAN_ALL" = true ]; then
    clean_test_outputs
    clean_benchmarks
    clean_logs
    clean_temp_files
elif [ "$CLEAN_TEST_OUTPUTS" = true ]; then
    clean_test_outputs
elif [ "$CLEAN_BENCHMARKS" = true ]; then
    clean_benchmarks
elif [ "$CLEAN_NODE_MODULES" = true ]; then
    clean_node_modules
elif [ "$CLEAN_LOGS" = true ]; then
    clean_logs
fi

echo ""

# Run maintenance checks
run_maintenance

echo ""

if [ "$DRY_RUN" = false ]; then
    echo -e "${GREEN}✅ Cleanup completed successfully!${NC}"
    echo ""
    show_disk_usage
else
    echo -e "${BLUE}🔍 Dry run completed - no files were deleted${NC}"
fi