#!/bin/bash
#
# Tiger Service Installation Script
# Document processing and analysis engine
#

set -e

echo "🐅 Tiger Service Installation"
echo "============================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📍 Python version: $PYTHON_VERSION"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8+ required"
    exit 1
fi

# Remove existing problematic venv
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in venv
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt


# Verify installation
echo "🔍 Verifying installation..."
python3 -c "import docling; print('✅ Docling installed')" 2>/dev/null || echo "❌ Docling failed"
python3 -c "import docx; print('✅ python-docx installed')" 2>/dev/null || echo "❌ python-docx failed"
python3 -c "from satori_schema.hydrated_json_schema import HydratedJSON; print('✅ Shared schema installed')" 2>/dev/null || echo "❌ Shared schema failed"

echo "🎉 Tiger Service installation complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run Tiger service:"
echo "  ./satori-tiger info"
