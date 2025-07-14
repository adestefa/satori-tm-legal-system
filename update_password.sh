#!/bin/bash
# Update iCloud password in settings.json

echo "======================================"
echo "Update iCloud Password in Settings"
echo "======================================"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <new_app_specific_password>"
    echo ""
    echo "Example:"
    echo "  $0 abcd-efgh-ijkl-mnop"
    echo ""
    echo "Use one of your active app-specific passwords:"
    echo "  - Legal-Agent"
    echo "  - Legal-Mallon"
    exit 1
fi

NEW_PASSWORD="$1"
SETTINGS_FILE="dashboard/config/settings.json"

echo "New password: $NEW_PASSWORD"
echo "Settings file: $SETTINGS_FILE"
echo ""

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "❌ Settings file not found: $SETTINGS_FILE"
    exit 1
fi

# Backup the current settings
cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup created: ${SETTINGS_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

# Update the password using Python
python3 -c "
import json

# Read current settings
with open('$SETTINGS_FILE', 'r') as f:
    settings = json.load(f)

# Update the password
if 'icloud' not in settings:
    settings['icloud'] = {}

settings['icloud']['password'] = '$NEW_PASSWORD'

# Write back to file
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(settings, f, indent=2)

print('✅ Password updated successfully')
"

echo ""
echo "======================================"
echo "TESTING NEW PASSWORD"
echo "======================================"
echo ""

# Test the new password
./test_minimal_auth.sh