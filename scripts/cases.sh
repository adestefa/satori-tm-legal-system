#!/bin/bash

# ##################################################
# Cases Management Utility for TM Legal System
# Simple CLI for case operations and reporting
# ##################################################

VERSION="2.1.2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TM_ROOT="$(dirname "$SCRIPT_DIR")"
CASES_DIR="$TM_ROOT/test-data/sync-test-cases"

# Cross-platform compatibility: Auto-detect OS and set appropriate stat commands
detect_os_and_set_stat_commands() {
    if [[ "$OSTYPE" == "darwin"* ]] || stat -f "%m" /dev/null >/dev/null 2>&1; then
        # macOS/BSD system
        STAT_MTIME="stat -f \"%m\""
        STAT_DATE="stat -f \"%Sm\" -t \"%Y-%m-%d %H:%M\""
        STAT_DATETIME="stat -f \"%Sm\" -t \"%Y-%m-%d %H:%M:%S\""
        STAT_SIZE="stat -f \"%z\""
        OS_TYPE="darwin"
    else
        # Linux/GNU system  
        STAT_MTIME="stat -c \"%Y\""
        STAT_DATE="stat -c \"%y\" | cut -d'.' -f1"
        STAT_DATETIME="stat -c \"%y\" | cut -d'.' -f1"
        STAT_SIZE="stat -c \"%s\""
        OS_TYPE="linux"
    fi
}

# Initialize cross-platform commands
detect_os_and_set_stat_commands

# Color codes for output (borrowed from dash.sh pattern)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Show usage information
show_help() {
    clear
    echo "Cases Management Utility v$VERSION"
    echo "Simple CLI for TM Legal System case operations"
    echo ""
    echo "Usage: $0 [OPTION] [PARAMETER]"
    echo ""
    echo "Options:"
    echo "  -l                List cases (first 12, newest first) with total count"
    echo "  -i <num|name>     Inspect case by number or name"
    echo "  -c <num|name>     Clear case by number or name"
    echo "  -d <num|name>     Delete case by number or name"
    echo "  -r                Generate report.json with case metadata"
    echo "  -z                Zip cases folder for backup"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -l             # List all cases"
    echo "  $0 -i 3           # Inspect case #3"
    echo "  $0 -i youssef     # Inspect case named 'youssef'"
    echo "  $0 -c 3           # Clear case #3"
    echo "  $0 -d youssef     # Delete case 'youssef'"
    echo "  $0 -r             # Generate report"
    echo "  $0 -z             # Create backup zip"
}

# Get sorted list of case directories (newest first)
get_case_list() {
    find "$CASES_DIR" -maxdepth 1 -type d -not -name "sync-test-cases" -not -name "outputs" -not -name ".*" 2>/dev/null | \
    while read -r dir; do
        if [[ -n "$dir" && -d "$dir" ]]; then
            local mtime=$(eval $STAT_MTIME "$dir" 2>/dev/null || echo "0")
            local basename=$(basename "$dir")
            echo "$mtime|$basename|$dir"
        fi
    done | sort -rn | cut -d'|' -f2,3
}

# Resolve case identifier (number or name) to case name
resolve_case_identifier() {
    local identifier="$1"
    
    # If it's a number, get the case at that position
    if [[ "$identifier" =~ ^[0-9]+$ ]]; then
        local case_list=($(get_case_list | cut -d'|' -f1))
        local index=$((identifier - 1))
        
        if [[ $index -ge 0 && $index -lt ${#case_list[@]} ]]; then
            echo "${case_list[$index]}"
        else
            return 1
        fi
    else
        # Check if case name exists
        if [[ -d "$CASES_DIR/$identifier" ]]; then
            echo "$identifier"
        else
            return 1
        fi
    fi
}

# List cases with numbering
list_cases() {
    clear
    printf "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
    printf "${BLUE}Cases Management - TM Legal System v$VERSION${NC}\n"
    printf "${BLUE}═══════════════════════════════════════════════════════${NC}\n\n"
    
    local case_list=($(get_case_list))
    local total_cases=${#case_list[@]}
    
    if [[ $total_cases -eq 0 ]]; then
        printf "${YELLOW}No cases found in $CASES_DIR${NC}\n"
        return 0
    fi
    
    printf "${GREEN}Found $total_cases case(s) total${NC}\n"
    printf "${CYAN}Showing first 12 cases (newest first):${NC}\n\n"
    
    local display_count=12
    [[ $total_cases -lt $display_count ]] && display_count=$total_cases
    
    for ((i=0; i<display_count; i++)); do
        local case_info="${case_list[$i]}"
        local case_name=$(echo "$case_info" | cut -d'|' -f1)
        local case_path=$(echo "$case_info" | cut -d'|' -f2)
        
        # Get file count (exclude processing_manifest.txt as it's generated metadata)
        local file_count=$(find "$case_path" -type f -not -name "processing_manifest.txt" -not -name ".*" 2>/dev/null | wc -l | tr -d ' ')
        
        # Get last modified time
        local mod_time=$(eval $STAT_DATE "$case_path" 2>/dev/null || echo "unknown")
        
        # Check if case has generated files
        local has_generated_files=false
        
        # Check for Tiger outputs
        if [[ -d "$TM_ROOT/outputs/tests/$case_name" && $(find "$TM_ROOT/outputs/tests/$case_name" -type f 2>/dev/null | wc -l) -gt 0 ]]; then
            has_generated_files=true
        fi
        
        # Check for Dashboard outputs
        if [[ -d "$TM_ROOT/dashboard/outputs/$case_name" && $(find "$TM_ROOT/dashboard/outputs/$case_name" -type f 2>/dev/null | wc -l) -gt 0 ]]; then
            has_generated_files=true
        fi
        
        # Check for Browser outputs
        if [[ $(find "$TM_ROOT/outputs/browser" -name "*${case_name}*" -type f 2>/dev/null | wc -l) -gt 0 ]]; then
            has_generated_files=true
        fi
        
        # Show case with generation status indicator
        if [[ "$has_generated_files" == "true" ]]; then
            printf "${PURPLE}%2d.${NC} %-20s ${YELLOW}(%s files)${NC} ${BLUE}%s${NC} ${GREEN}*${NC}\n" \
                   $((i+1)) "$case_name" "$file_count" "$mod_time"
        else
            printf "${PURPLE}%2d.${NC} %-20s ${YELLOW}(%s files)${NC} ${BLUE}%s${NC}\n" \
                   $((i+1)) "$case_name" "$file_count" "$mod_time"
        fi
    done
    
    if [[ $total_cases -gt $display_count ]]; then
        printf "\n${YELLOW}... and $((total_cases - display_count)) more case(s)${NC}\n"
    fi
    
    printf "\n${CYAN}Use: cases.sh -i <number|name> to inspect a case${NC}\n"

}

# Inspect case details
inspect_case() {
    local identifier="$1"
    
    if [[ -z "$identifier" ]]; then
        printf "${RED}Error: Please specify case number or name${NC}\n"
        printf "Usage: $0 -i <number|name>\n"
        return 1
    fi
    
    local case_name=$(resolve_case_identifier "$identifier")
    if [[ -z "$case_name" ]]; then
        printf "${RED}Error: Case '$identifier' not found${NC}\n"
        return 1
    fi
    
    local case_path="$CASES_DIR/$case_name"
    
    clear
    printf "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
    printf "${BLUE}Case Inspection: $case_name${NC}\n"
    printf "${BLUE}═══════════════════════════════════════════════════════${NC}\n\n"
    
    printf "${GREEN}Source Directory:${NC} $case_path\n"
    printf "${GREEN}Last Modified:${NC} $(eval $STAT_DATETIME "$case_path" 2>/dev/null || echo "unknown")\n\n"
    
    # Source files
    printf "${CYAN}Source Files:${NC}\n"
    local file_counter=1
    local total_bytes=0
    
    # Process actual source files (exclude processing_manifest.txt)
    while IFS= read -r -d '' file; do
        local size=$(eval $STAT_SIZE "$file" 2>/dev/null || echo "0")
        local size_human=$(numfmt --to=iec --suffix=B $size 2>/dev/null || echo "${size}B")
        printf "  ${PURPLE}%d.${NC} ${YELLOW}$(basename "$file")${NC} (${size_human})\n" "$file_counter"
        total_bytes=$((total_bytes + size))
        ((file_counter++))
    done < <(find "$case_path" -type f -not -name "processing_manifest.txt" -not -name ".*" -print0 | sort -z)
    
    # Show processing manifest separately if it exists
    if [[ -f "$case_path/processing_manifest.txt" ]]; then
        local manifest_size=$(eval $STAT_SIZE "$case_path/processing_manifest.txt" 2>/dev/null || echo "0")
        local manifest_size_human=$(numfmt --to=iec --suffix=B $manifest_size 2>/dev/null || echo "${manifest_size}B")
        printf "\n${CYAN}Processing Metadata:${NC}\n"
        printf "  ${BLUE}•${NC} ${YELLOW}processing_manifest.txt${NC} (${manifest_size_human})\n"
    fi
    
    # Display total size
    local total_mb=$(echo "scale=2; $total_bytes / 1048576" | bc 2>/dev/null || echo "0.00")
    printf "  ${GREEN}Total: ${total_mb}MB${NC}\n"
    
    # Generated files in outputs
    printf "\n${CYAN}Generated Files:${NC}\n"
    local generated_total_bytes=0
    local has_generated_files=false
    
    # Check Tiger outputs
    local tiger_output="$TM_ROOT/outputs/tests/$case_name"
    if [[ -d "$tiger_output" ]]; then
        printf "  ${GREEN}Tiger Outputs:${NC}\n"
        while IFS= read -r -d '' file; do
            local size=$(eval $STAT_SIZE "$file" 2>/dev/null || echo "0")
            local size_human=$(numfmt --to=iec --suffix=B $size 2>/dev/null || echo "${size}B")
            printf "    ${YELLOW}$(basename "$file")${NC} (${size_human})\n"
            generated_total_bytes=$((generated_total_bytes + size))
            has_generated_files=true
        done < <(find "$tiger_output" -type f -print0 2>/dev/null | sort -z)
    fi
    
    # Check Dashboard outputs
    local dashboard_output="$TM_ROOT/dashboard/outputs/$case_name"
    if [[ -d "$dashboard_output" ]]; then
        printf "  ${GREEN}Dashboard Outputs:${NC}\n"
        while IFS= read -r -d '' file; do
            local size=$(eval $STAT_SIZE "$file" 2>/dev/null || echo "0")
            local size_human=$(numfmt --to=iec --suffix=B $size 2>/dev/null || echo "${size}B")
            printf "    ${YELLOW}$(basename "$file")${NC} (${size_human})\n"
            generated_total_bytes=$((generated_total_bytes + size))
            has_generated_files=true
        done < <(find "$dashboard_output" -type f -print0 2>/dev/null | sort -z)
    fi
    
    # Check Browser outputs  
    if [[ -d "$TM_ROOT/outputs/browser" ]]; then
        local browser_files_found=false
        while IFS= read -r -d '' file; do
            if [[ ! "$browser_files_found" == "true" ]]; then
                printf "  ${GREEN}Browser PDFs:${NC}\n"
                browser_files_found=true
            fi
            local size=$(eval $STAT_SIZE "$file" 2>/dev/null || echo "0")
            local size_human=$(numfmt --to=iec --suffix=B $size 2>/dev/null || echo "${size}B")
            printf "    ${YELLOW}$(basename "$file")${NC} (${size_human})\n"
            generated_total_bytes=$((generated_total_bytes + size))
            has_generated_files=true
        done < <(find "$TM_ROOT/outputs/browser" -name "*${case_name}*" -type f -print0 2>/dev/null | sort -z)
    fi
    
    # Display generated files total
    if [[ "$has_generated_files" == "true" ]]; then
        local generated_mb=$(echo "scale=2; $generated_total_bytes / 1048576" | bc 2>/dev/null || echo "0.00")
        printf "  ${GREEN}Generated Total: ${generated_mb}MB${NC}\n"
    else
        printf "  ${YELLOW}No generated files found${NC}\n"
    fi
}

# Clear case (delegate to existing script)
clear_case() {
    local identifier="$1"
    
    if [[ -z "$identifier" ]]; then
        printf "${RED}Error: Please specify case number or name${NC}\n"
        printf "Usage: $0 -c <number|name>\n"
        return 1
    fi
    
    local case_name=$(resolve_case_identifier "$identifier")
    if [[ -z "$case_name" ]]; then
        printf "${RED}Error: Case '$identifier' not found${NC}\n"
        return 1
    fi
    
    printf "${BLUE}Clearing case: $case_name${NC}\n"
    bash "$SCRIPT_DIR/clear_case.sh" "$case_name"
    
    # Show updated list after clear operation
    printf "\n${CYAN}Updated case list after clear operation:${NC}\n\n"
    list_cases
}

# Delete case (delegate to existing script)
delete_case() {
    local identifier="$1"
    
    if [[ -z "$identifier" ]]; then
        printf "${RED}Error: Please specify case number or name${NC}\n"
        printf "Usage: $0 -d <number|name>\n"
        return 1
    fi
    
    local case_name=$(resolve_case_identifier "$identifier")
    if [[ -z "$case_name" ]]; then
        printf "${RED}Error: Case '$identifier' not found${NC}\n"
        return 1
    fi
    
    printf "${BLUE}Deleting case: $case_name${NC}\n"
    bash "$SCRIPT_DIR/rm_case.sh" "$case_name"
    
    # Show updated list after delete operation
    printf "\n${CYAN}Updated case list after delete operation:${NC}\n\n"
    list_cases
}

# Generate JSON report
generate_report() {
    clear
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local ip_address=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "unknown")
    local hostname=$(hostname)
    
    printf "${BLUE}Generating cases report...${NC}\n"
    
    local report_file="$TM_ROOT/cases_report_$(date +%Y%m%d_%H%M%S).json"
    
    # Delegate to separate script for JSON generation
    bash "$SCRIPT_DIR/cases_report.sh" "$report_file"
    
    if [[ -f "$report_file" ]]; then
        printf "${GREEN}Report generated: $report_file${NC}\n"
        printf "${CYAN}$(wc -l < "$report_file") lines, $(eval $STAT_SIZE "$report_file" | numfmt --to=iec --suffix=B)${NC}\n"
    else
        printf "${RED}Error: Failed to generate report${NC}\n"
        return 1
    fi
}

# Create backup zip
zip_cases() {
    clear
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local ip_address=$(hostname -I 2>/dev/null | awk '{print $1}' | tr -d '.')
    local zip_file="$TM_ROOT/legal_agent_files_${ip_address}_${timestamp}.zip"
    
    printf "${BLUE}Creating cases backup zip...${NC}\n"
    
    # Delegate to separate script for zip creation
    bash "$SCRIPT_DIR/cases_zip.sh" "$zip_file"
    
    if [[ -f "$zip_file" ]]; then
        printf "${GREEN}Backup created: $zip_file${NC}\n"
        printf "${CYAN}Size: $(eval $STAT_SIZE "$zip_file" | numfmt --to=iec --suffix=B)${NC}\n"
    else
        printf "${RED}Error: Failed to create backup${NC}\n"
        return 1
    fi
}

# Main command routing (dash.sh pattern)
case "$1" in
    -l|--list)
        list_cases
        ;;
    -i|--inspect)
        inspect_case "$2"
        ;;
    -c|--clear)
        clear_case "$2"
        ;;
    -d|--delete)
        delete_case "$2"
        ;;
    -r|--report)
        generate_report
        ;;
    -z|--zip)
        zip_cases
        ;;
    -h|--help)
        show_help
        ;;
    "")
        list_cases
        ;;
    *)
        printf "${RED}Unknown option: $1${NC}\n"
        show_help
        exit 1
        ;;
esac