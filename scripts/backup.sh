#!/bin/bash

# Create a backup of the TM project with manifest tracking
# Usage: ./backup.sh "commit message"

# Ensure we're running from the TM project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || {
    echo "Error: Could not change to project root directory: $PROJECT_ROOT"
    exit 1
}

echo "Working from TM project root: $(pwd)"

# Check if commit message is provided
if [ -z "$1" ]; then
    echo "Usage: ./scripts/backup.sh \"commit message\""
    echo "Example: ./scripts/backup.sh \"Fixed Tiger service integration issues\""
    exit 1
fi

COMMIT_MSG="$1"
TIMESTAMP=$(date +%Y-%m-%d-%H-%M-%S)

# Get version from dashboard HTML file or default to "v_"
VERSION="v_"
if [ -f "dashboard/static/themes/light/index.html" ]; then
    VERSION=$(grep -o 'const SATORI_VERSION = "[^"]*"' dashboard/static/themes/light/index.html 2>/dev/null | sed 's/const SATORI_VERSION = "\(.*\)"/\1/')
    if [ -z "$VERSION" ]; then
        VERSION="v_"
    fi
fi

BACKUP_NAME="TM-backup-${TIMESTAMP}-v${VERSION}"

echo "Creating backup: $BACKUP_NAME.zip"

# Create backups directory if it doesn't exist
mkdir -p "backups"

# Create zip archive excluding venv directories and other build artifacts
zip -r "$BACKUP_NAME.zip" . \
    -x "venv/*" \
    -x "*/venv/*" \
    -x "tiger/venv/*" \
    -x "monkey/venv/*" \
    -x "dashboard/venv/*" \
    -x "*/.git/*" \
    -x "*/node_modules/*" \
    -x "*/__pycache__/*" \
    -x "*.pyc" \
    -x "backups/*" \
    -x "views/*" \
    -x "*/outputs/*" > /dev/null

# Move backup to backups directory
mv "$BACKUP_NAME.zip" "backups/"

# Update manifest
MANIFEST_FILE="backups/manifest.md"
if [ ! -f "$MANIFEST_FILE" ]; then
    echo "# TM Project Backup Manifest" > "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"
    echo "| Filename | Date | Time | Version | Message |" >> "$MANIFEST_FILE"
    echo "|----------|------|------|---------|---------|" >> "$MANIFEST_FILE"
fi

# Append new entry to manifest
echo "| $BACKUP_NAME.zip | $(date +%Y-%m-%d) | $(date +%H:%M:%S) | $VERSION | $COMMIT_MSG |" >> "$MANIFEST_FILE"

echo "Backup created: backups/$BACKUP_NAME.zip"
echo "Size of backup:"
du -h "backups/$BACKUP_NAME.zip"
echo ""
echo "Manifest updated with message: $COMMIT_MSG"