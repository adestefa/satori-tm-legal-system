#!/bin/bash

# TM iSync Adapter Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
BINARY_NAME="tm-isync-adapter"
CONFIG_FILE="${CONFIG_FILE:-config.json}"
BUILD_DIR="build"
BINARY_PATH="$BUILD_DIR/$BINARY_NAME"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Go is installed
check_go() {
    if ! command -v go &> /dev/null; then
        log_error "Go is not installed. Please install Go 1.19 or later."
        exit 1
    fi
    
    go_version=$(go version | awk '{print $3}' | sed 's/go//')
    log_info "Go version: $go_version"
}

# Build the application
build_app() {
    log_info "Building $BINARY_NAME..."
    
    if ! make build; then
        log_error "Build failed"
        exit 1
    fi
    
    log_info "Build completed successfully"
}

# Check if config file exists
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_warn "Config file not found: $CONFIG_FILE"
        log_info "Creating default config file..."
        
        cat > "$CONFIG_FILE" << EOF
{
  "icloud_parent_folder": "TM_Cases",
  "local_tm_path": "/Users/corelogic/satori-dev/TM/test-data/sync-test-cases",
  "sync_interval": 30,
  "log_level": "info",
  "backup_enabled": true
}
EOF
        log_info "Default config created: $CONFIG_FILE"
    fi
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."
    
    # Check if TM path exists
    local_tm_path=$(grep -o '"local_tm_path"[^"]*"[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4)
    if [ -n "$local_tm_path" ] && [ ! -d "$local_tm_path" ]; then
        log_error "TM path does not exist: $local_tm_path"
        log_info "Please ensure the TM system is installed and the path is correct"
        exit 1
    fi
    
    # Check if iCloud Drive is available
    icloud_base="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
    if [ ! -d "$icloud_base" ]; then
        log_error "iCloud Drive not found at: $icloud_base"
        log_info "Please ensure iCloud Drive is enabled and syncing"
        exit 1
    fi
    
    log_info "Configuration validation passed"
}

# Run the application
run_app() {
    log_info "Starting $BINARY_NAME with config: $CONFIG_FILE"
    
    # Check if binary exists
    if [ ! -f "$BINARY_PATH" ]; then
        log_info "Binary not found, building first..."
        build_app
    fi
    
    # Run the application
    exec "$BINARY_PATH" -config "$CONFIG_FILE"
}

# Install service (basic launchd setup)
install_service() {
    log_info "Installing $BINARY_NAME as a macOS service..."
    
    local service_name="com.tm.isync.adapter"
    local plist_path="$HOME/Library/LaunchAgents/$service_name.plist"
    local binary_full_path="$(pwd)/$BINARY_PATH"
    local config_full_path="$(pwd)/$CONFIG_FILE"
    
    # Create launchd plist
    cat > "$plist_path" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$service_name</string>
    <key>ProgramArguments</key>
    <array>
        <string>$binary_full_path</string>
        <string>-config</string>
        <string>$config_full_path</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/tm-isync-adapter.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/tm-isync-adapter.error.log</string>
</dict>
</plist>
EOF
    
    # Load the service
    launchctl load "$plist_path"
    
    log_info "Service installed and started"
    log_info "Logs: /tmp/tm-isync-adapter.log"
    log_info "Errors: /tmp/tm-isync-adapter.error.log"
    log_info "To stop: launchctl unload $plist_path"
}

# Show help
show_help() {
    echo "TM iSync Adapter Run Script"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  run        Run the adapter (default)"
    echo "  build      Build the application"
    echo "  install    Install as macOS service"
    echo "  status     Show service status"
    echo "  stop       Stop the service"
    echo "  logs       Show service logs"
    echo "  help       Show this help"
    echo
    echo "Options:"
    echo "  CONFIG_FILE=path   Use custom config file"
    echo
    echo "Examples:"
    echo "  $0 run"
    echo "  CONFIG_FILE=custom.json $0 run"
    echo "  $0 build"
    echo "  $0 install"
    echo
}

# Show service status
show_status() {
    local service_name="com.tm.isync.adapter"
    log_info "Checking service status..."
    
    if launchctl list | grep -q "$service_name"; then
        log_info "Service is running"
    else
        log_info "Service is not running"
    fi
}

# Stop service
stop_service() {
    local service_name="com.tm.isync.adapter"
    local plist_path="$HOME/Library/LaunchAgents/$service_name.plist"
    
    log_info "Stopping service..."
    
    if [ -f "$plist_path" ]; then
        launchctl unload "$plist_path"
        log_info "Service stopped"
    else
        log_warn "Service not installed"
    fi
}

# Show logs
show_logs() {
    log_info "Showing service logs..."
    
    if [ -f "/tmp/tm-isync-adapter.log" ]; then
        tail -f /tmp/tm-isync-adapter.log
    else
        log_warn "No logs found"
    fi
}

# Main script
main() {
    local command="${1:-run}"
    
    case "$command" in
        run)
            check_go
            check_config
            validate_config
            run_app
            ;;
        build)
            check_go
            build_app
            ;;
        install)
            check_go
            check_config
            validate_config
            build_app
            install_service
            ;;
        status)
            show_status
            ;;
        stop)
            stop_service
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"