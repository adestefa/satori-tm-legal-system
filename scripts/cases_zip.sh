#!/bin/bash

# Cases Zip Creator - Backup utility
# Called by cases.sh -z

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TM_ROOT="$(dirname "$SCRIPT_DIR")"
CASES_DIR="$TM_ROOT/test-data/sync-test-cases"
ZIP_FILE="$1"

if [[ -z "$ZIP_FILE" ]]; then
    echo "Usage: $0 <output_file.zip>"
    exit 1
fi

# Create zip with cases folder
cd "$TM_ROOT" || exit 1

zip -r "$ZIP_FILE" \
    "test-data/sync-test-cases" \
    -x "test-data/sync-test-cases/outputs/*" \
    -x "test-data/sync-test-cases/.*" \
    >/dev/null 2>&1

# Add metadata file to zip
TEMP_METADATA="/tmp/backup_metadata_$$.txt"
cat > "$TEMP_METADATA" << EOF
Backup Created: $(date)
Hostname: $(hostname)
IP Address: $(hostname -I 2>/dev/null | awk '{print $1}' || echo 'unknown')
TM Version: 2.1.1
Total Cases: $(find "$CASES_DIR" -maxdepth 1 -type d -not -name "sync-test-cases" -not -name "outputs" -not -name ".*" 2>/dev/null | wc -l | tr -d ' ')
Backup Tool: cases.sh -z
EOF

zip -j "$ZIP_FILE" "$TEMP_METADATA" >/dev/null 2>&1
rm -f "$TEMP_METADATA"