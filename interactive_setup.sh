#!/bin/bash
# Interactive setup for iCloud authentication with 2FA support
# This script helps complete the initial authentication setup

echo "=============================================="
echo "Interactive iCloud Setup with 2FA Support"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "../debug_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../debug_env
    source ../debug_env/bin/activate
    pip install icloudpd
else
    echo "🔧 Activating virtual environment..."
    source ../debug_env/bin/activate
fi

echo ""
echo "📋 This script will help you complete initial iCloud authentication."
echo "   You may be prompted for 2FA codes during this process."
echo ""

# Load credentials from settings
if [ -f "../dashboard/config/settings.json" ]; then
    echo "📁 Loading credentials from dashboard settings..."
    
    # Extract credentials using Python
    ACCOUNT=$(python3 -c "
import json
with open('../dashboard/config/settings.json', 'r') as f:
    settings = json.load(f)
print(settings.get('icloud', {}).get('account', ''))
")
    
    PASSWORD=$(python3 -c "
import json
with open('../dashboard/config/settings.json', 'r') as f:
    settings = json.load(f)
print(settings.get('icloud', {}).get('password', ''))
")
    
    echo "   Account: $ACCOUNT"
    echo "   Password: $PASSWORD"
    echo ""
else
    echo "❌ Settings file not found at ../dashboard/config/settings.json"
    echo "Please ensure the dashboard is configured first."
    exit 1
fi

# Run interactive test
echo "🧪 Starting interactive authentication test..."
echo "   If 2FA is required, you will be prompted for verification codes."
echo ""

python3 interactive_icloud_test.py

echo ""
echo "✅ Interactive setup complete!"
echo ""
echo "💡 Next steps:"
echo "   1. If authentication succeeded, session cookies are saved"
echo "   2. Future connections should be automatic"
echo "   3. Test the connection in the dashboard settings page"