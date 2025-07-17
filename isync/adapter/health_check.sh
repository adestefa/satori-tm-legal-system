#!/bin/bash

# TM iSync Adapter Health Check Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
BINARY_PATH="build/tm-isync-adapter"
CONFIG_FILE="config.json"

# Health check results
CHECKS_PASSED=0
CHECKS_TOTAL=0

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((CHECKS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

check_item() {
    ((CHECKS_TOTAL++))
    echo -n "Checking $1... "
}

# Health checks
check_go_installation() {
    check_item "Go installation"
    
    if command -v go &> /dev/null; then
        go_version=$(go version | awk '{print $3}' | sed 's/go//')
        log_success "Go $go_version installed"
    else
        log_fail "Go not found"
        return 1
    fi
}

check_binary_exists() {
    check_item "binary existence"
    
    if [ -f "$BINARY_PATH" ]; then
        log_success "Binary found at $BINARY_PATH"
    else
        log_fail "Binary not found. Run 'make build' first"
        return 1
    fi
}

check_binary_executable() {
    check_item "binary execution"
    
    if [ -x "$BINARY_PATH" ]; then
        version_output=$(./"$BINARY_PATH" -version 2>&1)
        if echo "$version_output" | grep -q "TM iSync Adapter"; then
            log_success "Binary executes correctly"
        else
            log_fail "Binary execution failed"
            return 1
        fi
    else
        log_fail "Binary not executable"
        return 1
    fi
}

check_config_file() {
    check_item "configuration file"
    
    if [ -f "$CONFIG_FILE" ]; then
        if python3 -m json.tool "$CONFIG_FILE" &> /dev/null; then
            log_success "Valid JSON configuration found"
        else
            log_fail "Invalid JSON in configuration file"
            return 1
        fi
    else
        log_warn "Configuration file not found, will create default"
        # Don't fail this check as the app creates default config
        log_success "Will create default configuration"
    fi
}

check_icloud_drive() {
    check_item "iCloud Drive availability"
    
    icloud_base="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
    if [ -d "$icloud_base" ]; then
        # Check if it's actually syncing by looking for .icloud files or other indicators
        if [ -w "$icloud_base" ]; then
            log_success "iCloud Drive found and writable"
        else
            log_warn "iCloud Drive found but not writable"
        fi
    else
        log_fail "iCloud Drive not found. Please enable iCloud Drive in System Preferences"
        return 1
    fi
}

check_tm_system() {
    check_item "TM system paths"
    
    # Get the local_tm_path from config if it exists
    if [ -f "$CONFIG_FILE" ]; then
        local_tm_path=$(grep -o '"local_tm_path"[^"]*"[^"]*"' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
    else
        local_tm_path="/Users/corelogic/satori-dev/TM/test-data/sync-test-cases"
    fi
    
    if [ -n "$local_tm_path" ] && [ -d "$local_tm_path" ]; then
        log_success "TM system path accessible: $local_tm_path"
    else
        log_fail "TM system path not found: $local_tm_path"
        return 1
    fi
}

check_dependencies() {
    check_item "Go module dependencies"
    
    if go mod verify &> /dev/null; then
        log_success "Go module dependencies verified"
    else
        log_fail "Go module dependencies verification failed"
        return 1
    fi
}

check_file_permissions() {
    check_item "file permissions"
    
    # Check if we can write to current directory
    if [ -w "." ]; then
        # Check if we can create and delete test files
        test_file=".health_check_test_$$"
        if echo "test" > "$test_file" 2>/dev/null && rm "$test_file" 2>/dev/null; then
            log_success "File permissions OK"
        else
            log_fail "Cannot create/delete files in current directory"
            return 1
        fi
    else
        log_fail "Current directory not writable"
        return 1
    fi
}

check_service_status() {
    check_item "service status"
    
    service_name="com.tm.isync.adapter"
    if launchctl list 2>/dev/null | grep -q "$service_name"; then
        log_success "Service is running"
    else
        log_warn "Service not running (this is OK for manual runs)"
        # Don't fail this check as service might not be installed
        ((CHECKS_PASSED++))
    fi
}

check_system_resources() {
    check_item "system resources"
    
    # Check available disk space (require at least 1GB)
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [ "$available_space" -gt 1000000 ]; then # 1GB in KB
        log_success "Sufficient disk space available"
    else
        log_warn "Low disk space (less than 1GB available)"
    fi
}

# Performance test
performance_test() {
    check_item "performance test"
    
    if [ -f "$BINARY_PATH" ]; then
        # Simple timing test - just check if binary responds quickly
        if timeout 5s ./"$BINARY_PATH" -version > /dev/null 2>&1; then
            log_success "Performance test passed (responds within 5s)"
        else
            log_warn "Performance test failed (timeout or error)"
        fi
    else
        log_fail "Cannot run performance test - binary not found"
        return 1
    fi
}

# Summary function
print_summary() {
    echo
    echo "=================================="
    echo "Health Check Summary"
    echo "=================================="
    echo "Checks Passed: $CHECKS_PASSED/$CHECKS_TOTAL"
    
    if [ "$CHECKS_PASSED" -eq "$CHECKS_TOTAL" ]; then
        echo -e "${GREEN}Status: HEALTHY${NC}"
        echo "The TM iSync Adapter is ready to run!"
        return 0
    elif [ "$CHECKS_PASSED" -gt $((CHECKS_TOTAL / 2)) ]; then
        echo -e "${YELLOW}Status: WARNING${NC}"
        echo "Some issues detected but adapter may still work"
        return 1
    else
        echo -e "${RED}Status: UNHEALTHY${NC}"
        echo "Major issues detected. Please fix before running"
        return 2
    fi
}

# Print recommendations
print_recommendations() {
    echo
    echo "Recommendations:"
    echo "- Run 'make build' to create the binary"
    echo "- Ensure iCloud Drive is enabled and syncing"
    echo "- Verify TM system is installed and accessible"
    echo "- Check file permissions in working directory"
    echo "- Use './run.sh run' for first-time setup"
    echo
}

# Main health check function
main() {
    echo "TM iSync Adapter Health Check"
    echo "=============================="
    echo
    
    # Core checks
    check_go_installation || true
    check_binary_exists || true
    check_binary_executable || true
    check_config_file || true
    check_dependencies || true
    
    # System checks
    check_icloud_drive || true
    check_tm_system || true
    check_file_permissions || true
    check_system_resources || true
    
    # Service checks
    check_service_status || true
    
    # Performance check
    performance_test || true
    
    # Print summary
    result=$(print_summary)
    exit_code=$?
    
    if [ "$exit_code" -ne 0 ]; then
        print_recommendations
    fi
    
    return $exit_code
}

# Run health check
main "$@"