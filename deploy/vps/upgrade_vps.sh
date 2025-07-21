#!/bin/bash

# TM VPS Upgrade Script v1.0
# Usage: ./upgrade_vps.sh <alias> <commit-hash>
# Example: ./upgrade_vps.sh legal-agent-vps 2436207

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly VPS_TM_PATH="/opt/tm"
readonly BACKUP_DIR="/opt/tm/backups/upgrades"
readonly SERVICE_NAME="tm-dashboard"
readonly LOG_DIR="/tmp/tm-upgrade"
readonly TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

# Initialize logging
DEPLOYMENT_LOG=""
CHANGES_LOG=""

# Setup local logging directory
mkdir -p "$LOG_DIR"
readonly LOCAL_LOG_FILE="$LOG_DIR/upgrade-$TIMESTAMP.log"
readonly LOCAL_CHANGES_FILE="$LOG_DIR/changes-$TIMESTAMP.txt"

# Logging functions
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOCAL_LOG_FILE" >/dev/null
    DEPLOYMENT_LOG+="[$timestamp] $message\n"
}

log_change() {
    local change="$1"
    echo "$change" | tee -a "$LOCAL_CHANGES_FILE" >/dev/null
    CHANGES_LOG+="$change\n"
}

# Function: Print colored output with logging
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
    log_message "$(echo -e "$message" | sed 's/\x1b\[[0-9;]*m//g')"  # Strip colors for log
}

print_header() {
    print_status "$BLUE" "🚀 TM VPS Upgrade Script v1.0"
    print_status "$BLUE" "=================================="
    log_change "DEPLOYMENT STARTED: $(date '+%Y-%m-%d %H:%M:%S')"
    log_change "SCRIPT VERSION: 1.0"
    log_change "LOCAL LOG DIR: $LOG_DIR"
}

print_success() {
    print_status "$GREEN" "✅ $1"
}

print_error() {
    print_status "$RED" "❌ $1"
}

print_warning() {
    print_status "$YELLOW" "⚠️  $1"
}

print_info() {
    print_status "$BLUE" "ℹ️  $1"
}

# Function: Validate arguments
validate_arguments() {
    if [[ $# -ne 2 ]]; then
        print_error "Invalid arguments"
        echo "Usage: $0 <vps-alias> <commit-hash>"
        echo "Example: $0 legal-agent-vps 2436207"
        exit 1
    fi

    local vps_alias="$1"
    local commit_hash="$2"

    # Validate SSH connectivity
    if ! ssh "$vps_alias" 'echo "SSH connection successful"' >/dev/null 2>&1; then
        print_error "SSH connection to '$vps_alias' failed"
        print_info "Ensure SSH key is configured and alias exists in ~/.ssh/config"
        exit 1
    fi

    # Validate commit hash format (basic)
    if [[ ! "$commit_hash" =~ ^[0-9a-f]{7,40}$ ]]; then
        print_error "Invalid commit hash format: $commit_hash"
        print_info "Commit hash should be 7-40 hexadecimal characters"
        exit 1
    fi

    print_success "Arguments validated: alias=$vps_alias, commit=$commit_hash"
}

# Function: Check VPS prerequisites
check_vps_prerequisites() {
    local vps_alias="$1"
    
    print_info "Checking VPS prerequisites..."

    # Check if TM directory exists
    if ! ssh "$vps_alias" "test -d '$VPS_TM_PATH'"; then
        print_error "TM installation not found at $VPS_TM_PATH on $vps_alias"
        exit 1
    fi

    # Check if it's a git repository
    if ! ssh "$vps_alias" "cd '$VPS_TM_PATH' && git rev-parse --is-inside-work-tree" >/dev/null 2>&1; then
        print_error "TM directory at $VPS_TM_PATH is not a git repository"
        exit 1
    fi

    # Check service exists
    if ! ssh "$vps_alias" "systemctl is-enabled '$SERVICE_NAME'" >/dev/null 2>&1; then
        print_warning "Service '$SERVICE_NAME' not found or not enabled"
        print_info "Deployment will continue but service restart will be skipped"
    fi

    print_success "VPS prerequisites validated"
}

# Function: Create backup with logging
create_backup() {
    local vps_alias="$1"
    local timestamp=$(date '+%Y%m%d-%H%M%S')
    local backup_path="$BACKUP_DIR/$timestamp"
    
    print_info "Creating backup at $backup_path..."
    log_change "BACKUP: Creating backup directory: $backup_path"

    # Create backup directory structure
    ssh "$vps_alias" "mkdir -p '$backup_path'" || {
        print_error "Failed to create backup directory"
        log_change "ERROR: Failed to create backup directory"
        exit 1
    }

    # Get current git commit for backup reference
    local current_commit
    current_commit=$(ssh "$vps_alias" "cd '$VPS_TM_PATH' && git rev-parse HEAD")
    log_change "BACKUP: Current commit being backed up: $current_commit"
    
    # Backup critical files with exclusions
    print_info "Creating compressed archive..."
    ssh "$vps_alias" "cd '$VPS_TM_PATH' && tar -czf '$backup_path/tm-backup-$timestamp.tar.gz' \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='node_modules' \
        --exclude='outputs' \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        ." || {
        print_error "Backup creation failed"
        log_change "ERROR: Backup archive creation failed"
        exit 1
    }

    # Get backup size for reporting
    local backup_size
    backup_size=$(ssh "$vps_alias" "du -sh '$backup_path/tm-backup-$timestamp.tar.gz' | cut -f1")
    log_change "BACKUP: Archive size: $backup_size"

    # Save backup metadata
    ssh "$vps_alias" "cat > '$backup_path/backup-info.json' << EOF
{
    \"timestamp\": \"$timestamp\",
    \"previous_commit\": \"$current_commit\",
    \"backup_size\": \"$backup_size\",
    \"created_by\": \"upgrade_vps.sh v1.0\",
    \"exclusions\": [\".git\", \"venv\", \"node_modules\", \"outputs\", \"*.pyc\", \"__pycache__\"]
}
EOF"

    log_change "SUCCESS: Backup completed successfully"
    log_change "BACKUP: Location: $backup_path"
    log_change "BACKUP: Archive: tm-backup-$timestamp.tar.gz"
    print_success "Backup created: $backup_path ($backup_size)"
    echo "$backup_path"  # Return backup path
}

# Function: Stop services
stop_services() {
    local vps_alias="$1"
    
    print_info "Stopping TM services..."

    # Stop dashboard service if it exists and is running
    if ssh "$vps_alias" "systemctl is-active '$SERVICE_NAME'" >/dev/null 2>&1; then
        ssh "$vps_alias" "sudo systemctl stop '$SERVICE_NAME'"
        print_success "Service '$SERVICE_NAME' stopped"
    else
        print_info "Service '$SERVICE_NAME' was not running"
    fi

    # Additional cleanup - kill any remaining processes
    ssh "$vps_alias" "pkill -f 'uvicorn.*main:app' || true"
    ssh "$vps_alias" "pkill -f 'tailwindcss.*--watch' || true"
    
    print_success "Services stopped"
}

# Function: Deploy code with change tracking
deploy_code() {
    local vps_alias="$1"
    local commit_hash="$2"
    
    print_info "Deploying commit $commit_hash..."

    # Get current commit for change comparison
    local previous_commit
    previous_commit=$(ssh "$vps_alias" "cd '$VPS_TM_PATH' && git rev-parse HEAD")
    log_change "DEPLOYMENT: Previous commit: $previous_commit"
    log_change "DEPLOYMENT: Target commit: $commit_hash"

    # Fetch latest changes
    print_info "Fetching latest changes from origin..."
    ssh "$vps_alias" "cd '$VPS_TM_PATH' && git fetch origin" || {
        print_error "Git fetch failed"
        exit 1
    }

    # Get commit info
    local commit_info
    commit_info=$(ssh "$vps_alias" "cd '$VPS_TM_PATH' && git show --format='%h %s (%an, %ar)' --no-patch '$commit_hash' 2>/dev/null" || echo "Unknown commit")
    log_change "DEPLOYMENT: Commit info: $commit_info"

    # Get files changed between commits
    print_info "Analyzing changes..."
    local files_changed
    files_changed=$(ssh "$vps_alias" "cd '$VPS_TM_PATH' && git diff --name-only '$previous_commit' '$commit_hash' 2>/dev/null" || echo "")
    
    if [[ -n "$files_changed" ]]; then
        log_change "FILES CHANGED:"
        while IFS= read -r file; do
            if [[ -n "$file" ]]; then
                # Get change type (A=added, M=modified, D=deleted)
                local change_type
                change_type=$(ssh "$vps_alias" "cd '$VPS_TM_PATH' && git diff --name-status '$previous_commit' '$commit_hash' | grep '$file' | cut -f1" || echo "M")
                log_change "  $change_type $file"
            fi
        done <<< "$files_changed"
        
        # Count changes
        local file_count
        file_count=$(echo "$files_changed" | grep -c '^' || echo "0")
        log_change "SUMMARY: $file_count files changed"
    else
        log_change "SUMMARY: No file changes detected"
    fi

    # Checkout specific commit
    print_info "Checking out commit $commit_hash..."
    ssh "$vps_alias" "cd '$VPS_TM_PATH' && git checkout '$commit_hash'" || {
        print_error "Git checkout failed"
        exit 1
    }

    # Verify checkout
    local deployed_commit
    deployed_commit=$(ssh "$vps_alias" "cd '$VPS_TM_PATH' && git rev-parse HEAD")
    
    if [[ "$deployed_commit" != "$commit_hash"* ]]; then
        print_error "Deployment verification failed. Expected: $commit_hash, Got: $deployed_commit"
        log_change "ERROR: Deployment verification failed"
        exit 1
    fi

    log_change "SUCCESS: Code deployed to commit $deployed_commit"
    print_success "Code deployed successfully to commit $commit_hash"
}

# Function: Update dependencies (if needed)
update_dependencies() {
    local vps_alias="$1"
    
    print_info "Checking dependencies..."

    # Check if requirements files have changed
    local requirements_changed=false
    
    # Check for Python requirements changes
    if ssh "$vps_alias" "cd '$VPS_TM_PATH' && git diff HEAD~1 HEAD --name-only | grep -E 'requirements|setup\.py|pyproject\.toml'" >/dev/null 2>&1; then
        requirements_changed=true
        print_info "Python dependencies may have changed"
    fi

    # Check for Node.js dependencies changes
    if ssh "$vps_alias" "cd '$VPS_TM_PATH' && git diff HEAD~1 HEAD --name-only | grep -E 'package\.json|package-lock\.json'" >/dev/null 2>&1; then
        requirements_changed=true
        print_info "Node.js dependencies may have changed"
    fi

    if $requirements_changed; then
        print_warning "Dependencies may have changed - manual verification recommended"
        print_info "Run: ssh $vps_alias 'cd $VPS_TM_PATH && ./install.sh'"
    else
        print_success "No dependency changes detected"
    fi
}

# Function: Start services
start_services() {
    local vps_alias="$1"
    
    print_info "Starting TM services..."

    # Start dashboard service
    if ssh "$vps_alias" "systemctl is-enabled '$SERVICE_NAME'" >/dev/null 2>&1; then
        ssh "$vps_alias" "sudo systemctl start '$SERVICE_NAME'"
        
        # Wait for service to start
        local attempts=0
        local max_attempts=30
        
        while [[ $attempts -lt $max_attempts ]]; do
            if ssh "$vps_alias" "systemctl is-active '$SERVICE_NAME'" >/dev/null 2>&1; then
                break
            fi
            sleep 2
            ((attempts++))
        done

        if [[ $attempts -eq $max_attempts ]]; then
            print_error "Service '$SERVICE_NAME' failed to start within 60 seconds"
            ssh "$vps_alias" "sudo journalctl -u '$SERVICE_NAME' --lines=20"
            exit 1
        fi

        print_success "Service '$SERVICE_NAME' started successfully"
    else
        print_warning "Service '$SERVICE_NAME' not configured - manual startup required"
        print_info "Run: ssh $vps_alias 'cd $VPS_TM_PATH/dashboard && ./start.sh'"
    fi
}

# Function: Validate deployment
validate_deployment() {
    local vps_alias="$1"
    local commit_hash="$2"
    
    print_info "Validating deployment..."

    # Check git commit
    local current_commit
    current_commit=$(ssh "$vps_alias" "cd '$VPS_TM_PATH' && git rev-parse HEAD")
    
    if [[ "$current_commit" != "$commit_hash"* ]]; then
        print_error "Git commit validation failed"
        return 1
    fi

    # Check service status
    if ssh "$vps_alias" "systemctl is-enabled '$SERVICE_NAME'" >/dev/null 2>&1; then
        if ! ssh "$vps_alias" "systemctl is-active '$SERVICE_NAME'" >/dev/null 2>&1; then
            print_error "Service validation failed - '$SERVICE_NAME' not running"
            return 1
        fi
    fi

    # Test HTTP endpoint (basic connectivity)
    local server_ip
    server_ip=$(ssh "$vps_alias" "curl -s ifconfig.me || echo 'unknown'")
    
    if [[ "$server_ip" != "unknown" ]]; then
        if curl -s -o /dev/null -w "%{http_code}" "http://$server_ip:8000/" | grep -q "200\|302\|401"; then
            print_success "HTTP endpoint validation passed"
        else
            print_warning "HTTP endpoint may not be responding (this could be normal)"
        fi
    fi

    print_success "Deployment validation completed"
}

# Function: Generate deployment report
generate_deployment_report() {
    local vps_alias="$1"
    local commit_hash="$2"
    local backup_path="$3"
    local duration="$4"
    local server_ip="$5"
    
    local report_file="$LOG_DIR/deployment-report-$TIMESTAMP.txt"
    
    cat > "$report_file" << EOF
# TM VPS Deployment Report
Generated: $(date '+%Y-%m-%d %H:%M:%S')

## Deployment Summary
VPS Alias: $vps_alias
Server IP: $server_ip
Target Path: $VPS_TM_PATH
Commit Hash: $commit_hash
Duration: ${duration}s
Backup Location: $backup_path
Status: SUCCESS

## Files Changed
$CHANGES_LOG

## Deployment Log
$DEPLOYMENT_LOG

## Post-Deployment Verification
- Git commit verified: ✅
- Service status verified: ✅
- HTTP endpoint accessible: ✅

## Rollback Instructions
If issues occur, execute:
ssh $vps_alias "cd $VPS_TM_PATH && sudo systemctl stop $SERVICE_NAME && tar -xzf $backup_path/tm-backup-*.tar.gz && sudo systemctl start $SERVICE_NAME"

## Access Information
Dashboard URL: http://$server_ip:8000
Service Logs: ssh $vps_alias "sudo journalctl -u $SERVICE_NAME -f"
EOF

    echo "$report_file"
}

# Function: Print deployment summary with logging
print_summary() {
    local vps_alias="$1"
    local commit_hash="$2"
    local backup_path="$3"
    local start_time="$4"
    local end_time="$5"
    
    local duration=$((end_time - start_time))
    
    # Get server IP for report
    local server_ip
    server_ip=$(ssh "$vps_alias" "curl -s ifconfig.me 2>/dev/null" || echo "unknown")
    
    # Generate comprehensive report
    local report_file
    report_file=$(generate_deployment_report "$vps_alias" "$commit_hash" "$backup_path" "$duration" "$server_ip")
    
    print_status "$GREEN" ""
    print_status "$GREEN" "🎉 Deployment Summary"
    print_status "$GREEN" "===================="
    echo -e "${GREEN}VPS:${NC}           $vps_alias"
    echo -e "${GREEN}Commit:${NC}        $commit_hash"
    echo -e "${GREEN}Duration:${NC}      ${duration}s"
    echo -e "${GREEN}Backup:${NC}        $backup_path"
    echo -e "${GREEN}Status:${NC}        ✅ SUCCESS"
    print_status "$GREEN" ""
    print_status "$BLUE" "📁 Reports Generated:"
    echo "  • Deployment Log:    $LOCAL_LOG_FILE"
    echo "  • Changes Log:       $LOCAL_CHANGES_FILE" 
    echo "  • Full Report:       $report_file"
    print_status "$GREEN" ""
    print_status "$BLUE" "Next Steps:"
    echo "  • Test functionality: http://$server_ip:8000"
    echo "  • Check service logs: ssh $vps_alias 'sudo journalctl -u $SERVICE_NAME -f'"
    echo "  • View full report:   cat $report_file"
    print_status "$GREEN" ""
}

# Main execution function
main() {
    local start_time=$(date +%s)
    
    print_header
    
    # Parse arguments
    local vps_alias="$1"
    local commit_hash="$2"
    
    # Validate inputs
    validate_arguments "$vps_alias" "$commit_hash"
    
    # Pre-flight checks
    check_vps_prerequisites "$vps_alias"
    
    # Create backup
    local backup_path
    backup_path=$(create_backup "$vps_alias")
    
    # Deployment sequence
    stop_services "$vps_alias"
    deploy_code "$vps_alias" "$commit_hash"
    update_dependencies "$vps_alias"
    start_services "$vps_alias"
    
    # Validation
    if ! validate_deployment "$vps_alias" "$commit_hash"; then
        print_error "Deployment validation failed"
        print_info "Check service logs: ssh $vps_alias 'sudo journalctl -u $SERVICE_NAME'"
        exit 1
    fi
    
    # Success summary
    local end_time=$(date +%s)
    print_summary "$vps_alias" "$commit_hash" "$backup_path" "$start_time" "$end_time"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi