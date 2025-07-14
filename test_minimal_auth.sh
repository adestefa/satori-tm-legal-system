#!/bin/bash
# Minimal iCloud Authentication Test
# Tests the smallest possible authentication payload

echo "======================================"
echo "Minimal iCloud Authentication Test"
echo "======================================"

# Load credentials from settings file
SETTINGS_FILE="dashboard/config/settings.json"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "❌ Settings file not found: $SETTINGS_FILE"
    exit 1
fi

# Extract credentials using Python
ACCOUNT=$(python3 -c "
import json
with open('$SETTINGS_FILE', 'r') as f:
    settings = json.load(f)
print(settings.get('icloud', {}).get('account', ''))
")

PASSWORD=$(python3 -c "
import json
with open('$SETTINGS_FILE', 'r') as f:
    settings = json.load(f)
print(settings.get('icloud', {}).get('password', ''))
")

echo "Account: $ACCOUNT"
echo "Password: $PASSWORD"
echo "Password length: ${#PASSWORD}"
echo ""

if [ -z "$ACCOUNT" ] || [ -z "$PASSWORD" ]; then
    echo "❌ Missing credentials in settings file"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "dashboard/venv" ]; then
    echo "🔧 Activating virtual environment..."
    source dashboard/venv/bin/activate
fi

# Test 1: Direct icloudpd auth test (minimal command)
echo "🧪 Test 1: Minimal icloudpd authentication test..."
echo "Command: icloudpd --username '$ACCOUNT' --password '$PASSWORD' --auth-only --dry-run"
echo ""

icloudpd \
    --username "$ACCOUNT" \
    --password "$PASSWORD" \
    --auth-only \
    --dry-run

AUTH_RESULT=$?

echo ""
echo "======================================"
echo "RESULTS"
echo "======================================"

if [ $AUTH_RESULT -eq 0 ]; then
    echo "✅ Authentication successful!"
    echo "   The app-specific password is working correctly"
    echo "   Issue was with the deprecated pyicloud library"
else
    echo "❌ Authentication failed (exit code: $AUTH_RESULT)"
    echo "   Need to check which app-specific password to use"
    echo "   Try updating settings.json with the correct password"
fi

echo ""
echo "Next steps:"
echo "1. If successful: iCloud sync should work in dashboard"
echo "2. If failed: Update password in settings.json with one of:"
echo "   - Legal-Agent password"
echo "   - Legal-Mallon password"