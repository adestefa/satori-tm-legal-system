#!/bin/bash
# Test script for modern iCloud authentication
# Uses the updated cookie-based session authentication

echo "=============================================="
echo "Modern iCloud Authentication Test"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "../debug_env" ]; then
    echo "ERROR: Virtual environment not found at ../debug_env"
    echo "Please run: python3 -m venv ../debug_env && source ../debug_env/bin/activate && pip install pyicloud"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../debug_env/bin/activate

# Check if icloudpd is installed
echo "🔍 Checking icloudpd installation..."
python3 -c "import icloudpd; print(f'icloudpd available')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ icloudpd not installed. Installing..."
    pip install icloudpd
fi

# Test modern authentication
echo ""
echo "🧪 Testing modern iCloud authentication..."
echo ""

if [ -f "modern_icloud_service.py" ]; then
    python3 modern_icloud_service.py
else
    echo "❌ modern_icloud_service.py not found"
    echo "Available files:"
    ls -la *.py
fi

echo ""
echo "✅ Test complete!"