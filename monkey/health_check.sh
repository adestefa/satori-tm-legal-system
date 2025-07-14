#!/bin/bash
#
# Monkey Service Health Check
# Validates document generation functionality and dependencies
#

set -e

echo "🐒 Monkey Service Health Check"
echo "=============================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📍 Activating virtual environment..."
    source venv/bin/activate
fi

# Check Python dependencies
echo "🔍 Checking dependencies..."
python3 -c "import jinja2; print('✅ Jinja2 available')" 2>/dev/null || echo "❌ Jinja2 missing"
python3 -c "from satori_schema import HydratedJSONSchema; print('✅ Shared schema available')" 2>/dev/null || echo "❌ Shared schema missing"
python3 -c "import pydantic; print('✅ Pydantic available')" 2>/dev/null || echo "❌ Pydantic missing"

# Check core modules
echo "🔍 Checking core modules..."
python3 -c "from core.document_builder import BeaverDocumentBuilder; print('✅ Document builder available')" 2>/dev/null || echo "❌ Document builder missing"
python3 -c "from core.validators import DocumentValidator; print('✅ Validator available')" 2>/dev/null || echo "❌ Validator missing"
python3 -c "from core.template_engine import TemplateEngine; print('✅ Template engine available')" 2>/dev/null || echo "❌ Template engine missing"

# Check templates
echo "🔍 Checking templates..."
[ -f "templates/fcra/complaint.jinja2" ] && echo "✅ FCRA complaint template available" || echo "❌ FCRA complaint template missing"
[ -f "templates/fcra/summons.jinja2" ] && echo "✅ Summons template available" || echo "❌ Summons template missing"

# Check CLI functionality
echo "🔍 Checking CLI..."
./run.sh --help > /dev/null 2>&1 && echo "✅ CLI functional" || echo "❌ CLI not working"

# Check output directories
echo "🔍 Checking output structure..."
mkdir -p outputs/{production,testing,development}
[ -d "outputs/production" ] && echo "✅ Production directory ready" || echo "❌ Production directory missing"
[ -d "outputs/testing" ] && echo "✅ Testing directory ready" || echo "❌ Testing directory missing"

echo ""
echo "Health check complete. Monkey service status:"
echo "- Install dependencies with: ./install.sh"
echo "- Activate environment: source venv/bin/activate"  
echo "- Run Monkey: ./satori-monkey build complaint.json"