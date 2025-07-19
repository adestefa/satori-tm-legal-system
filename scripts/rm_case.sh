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

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <case_name>"
    echo "Example: $0 youssef"
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

# Security confirmation
confirm_deletion "$CASE_NAME"

echo ""
echo "🔥 Beginning permanent deletion of case '$CASE_NAME'..."

# 1. Delete source case directory (test-data/sync-test-cases/<case_name>)
SOURCE_CASE_DIR="$TM_ROOT/test-data/sync-test-cases/$CASE_NAME"
if [[ -d "$SOURCE_CASE_DIR" ]]; then
    echo "Removing source case directory: $SOURCE_CASE_DIR"
    rm -rf "$SOURCE_CASE_DIR"
    echo "✅ Source documents deleted"
else
    echo "ℹ️  No source case directory found: $CASE_NAME"
fi

# 2. Delete main case output directory (outputs/tests/<case_name>)
OUTPUTS_DIR="$TM_ROOT/outputs/tests"
CASE_OUTPUT_DIR="$OUTPUTS_DIR/$CASE_NAME"
if [[ -d "$CASE_OUTPUT_DIR" ]]; then
    echo "Removing case output directory: $CASE_OUTPUT_DIR"
    rm -rf "$CASE_OUTPUT_DIR"
    echo "✅ Case outputs deleted"
fi

# 3. Delete dashboard output directory (dashboard/outputs/<case_name>)
DASHBOARD_OUTPUT_DIR="$TM_ROOT/dashboard/outputs/$CASE_NAME"
if [[ -d "$DASHBOARD_OUTPUT_DIR" ]]; then
    echo "Removing dashboard output directory: $DASHBOARD_OUTPUT_DIR"
    rm -rf "$DASHBOARD_OUTPUT_DIR"
    echo "✅ Dashboard outputs deleted"
fi

# 4. Delete browser service PDF outputs
BROWSER_OUTPUT_DIR="$TM_ROOT/outputs/browser"
if [[ -d "$BROWSER_OUTPUT_DIR" ]]; then
    BROWSER_PDFS=$(find "$BROWSER_OUTPUT_DIR" -name "*${CASE_NAME}*" -type f 2>/dev/null || true)
    if [[ -n "$BROWSER_PDFS" ]]; then
        echo "Removing browser service PDFs:"
        echo "$BROWSER_PDFS" | while read -r file; do
            if [[ -f "$file" ]]; then
                rm "$file"
                echo "  ✅ Deleted: $(basename "$file")"
            fi
        done
    fi
fi

# 5. Delete any standalone JSON files
STANDALONE_JSON=$(find "$OUTPUTS_DIR" -maxdepth 1 -iname "*${CASE_NAME}*.json" 2>/dev/null || true)
if [[ -n "$STANDALONE_JSON" ]]; then
    echo "Removing standalone JSON files:"
    echo "$STANDALONE_JSON" | while read -r file; do
        if [[ -f "$file" ]]; then
            rm "$file"
            echo "  ✅ Deleted: $(basename "$file")"
        fi
    done
fi

# 6. Clean any Tiger service outputs
TIGER_OUTPUT_DIR="$TM_ROOT/tiger/outputs"
if [[ -d "$TIGER_OUTPUT_DIR" ]]; then
    TIGER_FILES=$(find "$TIGER_OUTPUT_DIR" -name "*${CASE_NAME}*" -type f 2>/dev/null || true)
    if [[ -n "$TIGER_FILES" ]]; then
        echo "Removing Tiger service outputs:"
        echo "$TIGER_FILES" | while read -r file; do
            if [[ -f "$file" ]]; then
                rm "$file"
                echo "  ✅ Deleted: $(basename "$file")"
            fi
        done
    fi
fi

# 7. Clean any Monkey service outputs
MONKEY_OUTPUT_DIR="$TM_ROOT/monkey/outputs"
if [[ -d "$MONKEY_OUTPUT_DIR" ]]; then
    MONKEY_FILES=$(find "$MONKEY_OUTPUT_DIR" -name "*${CASE_NAME}*" -type f 2>/dev/null || true)
    if [[ -n "$MONKEY_FILES" ]]; then
        echo "Removing Monkey service outputs:"
        echo "$MONKEY_FILES" | while read -r file; do
            if [[ -f "$file" ]]; then
                rm "$file"
                echo "  ✅ Deleted: $(basename "$file")"
            fi
        done
    fi
fi

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