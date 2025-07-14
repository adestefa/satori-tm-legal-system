#!/bin/bash
#
# Tiger Service Health Check
# Validates core functionality and dependencies
#

set -e

echo "🐅 Tiger Service Health Check"
echo "============================="

# Define the python interpreter from the venv
PYTHON_EXEC="/Users/corelogic/satori-dev/TM/tiger/venv/bin/python3"

# Check if venv exists
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh"
    exit 1
fi

# Function to check a module
check_module() {
    MODULE_NAME=$1
    FRIENDLY_NAME=$2
    if $PYTHON_EXEC -c "import $MODULE_NAME" >/dev/null 2>&1; then
        echo "✅ $FRIENDLY_NAME available"
    else
        echo "❌ $FRIENDLY_NAME missing"
    fi
}

# Function to check a module with a 'from' import
check_from_module() {
    MODULE_NAME=$1
    OBJECT_NAME=$2
    FRIENDLY_NAME=$3
    # This is a hack to get the shared schema to work
    export PYTHONPATH="/Users/corelogic/satori-dev/TM/shared-schema:/Users/corelogic/satori-dev/TM/tiger"
    if $PYTHON_EXEC -c "from $MODULE_NAME import $OBJECT_NAME" >/dev/null 2>&1; then
        echo "✅ $FRIENDLY_NAME available"
    else
        echo "❌ $FRIENDLY_NAME missing"
    fi
}

# Check Python dependencies
echo "🔍 Checking dependencies..."
check_module "docling" "Docling"
check_module "docx" "python-docx"
check_from_module "satori_schema.hydrated_json_schema" "HydratedJSON" "Shared schema"

# Check core modules
echo "🔍 Checking core modules..."
check_from_module "app.core.processors.document_processor" "DocumentProcessor" "Document processor"
check_from_module "app.engines.docling_engine" "DoclingEngine" "Docling engine"

# Check CLI functionality
echo "🔍 Checking CLI..."
/Users/corelogic/satori-dev/TM/tiger/run.sh --help > /dev/null 2>&1 && echo "✅ CLI functional" || echo "❌ CLI not working"

# Check output directories
echo "🔍 Checking output structure..."
mkdir -p /Users/corelogic/satori-dev/TM/tiger/outputs/{production,testing,development}
[ -d "/Users/corelogic/satori-dev/TM/tiger/outputs/production" ] && echo "✅ Production directory ready" || echo "❌ Production directory missing"
[ -d "/Users/corelogic/satori-dev/TM/tiger/outputs/testing" ] && echo "✅ Testing directory ready" || echo "❌ Testing directory missing"

echo ""
echo "Health check complete. Tiger service status:"
echo "- Install dependencies with: ./install.sh"
echo "- Activate environment: source venv/bin/activate"
echo "- Run Tiger: ./satori-tiger info"
