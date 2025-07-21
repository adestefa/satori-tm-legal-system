#!/bin/bash

# Remove Case Script - PERMANENTLY DELETE case from system
# Usage: ./rm_case.sh <case_name>
# Version: 2.1.1 - Security-hardened case deletion with localhost restriction
# WARNING: This operation is IRREVERSIBLE

set -e

# Security Gate: Restrict to localhost/development environments only
check_localhost_only() {
    local hostname=$(hostname)
    local ip_addr=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
    
    # Check if running on localhost/development machine
    if [[ "$hostname" == "localhost" ]] || \
       [[ "$hostname" == *".local" ]] || \
       [[ "$hostname" == *"Studio" ]] || \
       [[ "$hostname" == *"MacBook"* ]] || \
       [[ "$hostname" == *"iMac"* ]] || \
       [[ "$ip_addr" == "127."* ]] || \
       [[ "$ip_addr" == "192.168."* ]] || \
       [[ "$ip_addr" == "10."* ]] || \
       [[ -f "/tmp/.development_mode" ]] || \
       [[ -d "/Users" ]]; then  # macOS indicator
        return 0
    else
        echo "🚫 SECURITY: rm_case.sh is restricted to localhost/development environments only"
        echo "   Current hostname: $hostname"
        echo "   Current IP: $ip_addr"
        echo "   This script cannot run in production environments"
        echo "   To enable on this machine, create: touch /tmp/.development_mode"
        exit 1
    fi
}

# Confirmation gate for destructive operation
confirm_deletion() {
    local case_name="$1"
    echo "⚠️  WARNING: This will PERMANENTLY DELETE all data for case '$case_name'"
    echo "   This includes:"
    echo "   - Source documents in test-data/sync-test-cases/$case_name/"
    echo "   - All generated outputs and PDFs"
    echo "   - All processing history and metadata"
    echo "   - Dashboard configuration and settings"
    echo ""
    echo "   This operation is IRREVERSIBLE"
    echo ""
    read -p "Type 'DELETE' to confirm permanent removal: " confirmation
    
    if [[ "$confirmation" != "DELETE" ]]; then
        echo "❌ Operation cancelled - case was NOT deleted"
        exit 0
    fi
}

if [[ $# -eq 0 ]] || [[ "$1" == "--help" ]]; then
    echo "Usage: $0 <case_name> [--force]"
    echo "Example: $0 youssef"
    echo "  --force   Bypass interactive confirmation for automated use"
    echo ""
    echo "⚠️  WARNING: This script PERMANENTLY DELETES a case from the system"
    echo "This includes all source documents, outputs, and processing history"
    echo "This operation is IRREVERSIBLE"
    echo ""
    echo "Security: Only available on localhost/development environments"
    exit 1
fi

# Execute security gate
check_localhost_only

CASE_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TM_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🗑️  PERMANENT CASE DELETION: $CASE_NAME"
echo "Environment: $(hostname) ($(hostname -I 2>/dev/null | awk '{print $1}' || echo 'unknown'))"

# If --force is not provided, ask for confirmation
if [[ "$2" != "--force" ]]; then
    confirm_deletion "$1"
fi

# Define all directories to be cleaned. This array can be easily extended in the future.
CLEANUP_DIRS=(
    "$TM_ROOT/test-data/sync-test-cases"
    "$TM_ROOT/outputs"
    "$TM_ROOT/dashboard/outputs"
    "$TM_ROOT/tiger/outputs"
    "$TM_ROOT/monkey/outputs"
    "$TM_ROOT/project_memories"
    "$TM_ROOT/test-data/ground-truth"
)

echo ""
echo "🔥 Beginning permanent deletion of case '$CASE_NAME'..."

# Loop through the array and clean each directory
for dir in "${CLEANUP_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        # Find and delete files/dirs matching the case name (case-insensitive)
        # The -depth option ensures we delete contents before the directory itself.
        find "$dir" -depth -iname "*${CASE_NAME}*" -exec rm -rf {} +
    fi
done

# A final check for any remaining empty directories that might have matched
find "${CLEANUP_DIRS[@]}" -type d -iname "*${CASE_NAME}*" -empty -delete 2>/dev/null || true

echo "✅ All associated files and directories for '$CASE_NAME' have been removed."

echo ""
echo "🔥 PERMANENT DELETION COMPLETE"
echo "📝 Case '$CASE_NAME' has been permanently removed from the system"
echo "   - Source documents deleted from test-data/sync-test-cases/$CASE_NAME/"
echo "   - All generated outputs and PDFs removed"
echo "   - All processing history and metadata deleted"
echo "   - All service-specific outputs cleaned"
echo ""
echo "⚠️  This operation was IRREVERSIBLE"
echo ""
echo "🔄 Triggering Dashboard refresh..."

# Force Dashboard refresh via API
REFRESH_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/api/refresh" 2>/dev/null || echo "")
if [[ "$REFRESH_RESPONSE" == *"successfully"* ]]; then
    echo "✅ Dashboard refresh completed"
else
    echo "⚠️  Dashboard refresh failed - manual refresh may be required"
fi

echo ""
echo "Case '$CASE_NAME' no longer exists in the system."
echo "If dashboard still shows the case, click 'Refresh' or hard refresh browser."