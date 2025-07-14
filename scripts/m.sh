#!/bin/bash
#
# Monkey Service Test Script  
# Tests Monkey document generation with proper virtual environment
#

set -e

echo "🐒 Monkey Service Test Suite"
echo "============================"

# Test 1: Health Check
echo ""
echo "Test 1: Health Check"
echo "-------------------"
(cd /Users/corelogic/satori-dev/TM/monkey && ./health_check.sh)

# Test 2: Template Validation
echo ""
echo "Test 2: Template Validation"
echo "-------------------------"
/Users/corelogic/satori-dev/TM/monkey/run.sh templates

# Test 3: JSON Schema Validation
echo ""
echo "Test 3: JSON Schema Validation"
echo "-----------------------------"
if [ -f "/Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json" ]; then
    echo "🔍 Validating hydrated JSON test file..."
    /Users/corelogic/satori-dev/TM/monkey/run.sh validate /Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json
    echo "✅ JSON validation test completed"
else
    echo "⏭️ No test JSON found, skipping validation test"
fi

# Test 4: Document Preview
echo ""
echo "Test 4: Document Preview"
echo "----------------------"
if [ -f "/Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json" ]; then
    echo "👁️ Generating document preview..."
    /Users/corelogic/satori-dev/TM/monkey/run.sh preview /Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json --lines 50
    echo "✅ Document preview test completed"
else
    echo "⏭️ No test JSON found, skipping preview test"
fi

# Test 5: Single Document Generation
echo ""
echo "Test 5: Single Document Generation"
echo "--------------------------------"
if [ -f "/Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json" ]; then
    echo "📄 Generating complaint document..."
    /Users/corelogic/satori-dev/TM/monkey/run.sh build-complaint /Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json -o /Users/corelogic/satori-dev/TM/monkey/outputs/testing/
    echo "✅ Single document generation test completed"
else
    echo "⏭️ No test JSON found, skipping document generation test"
fi

# Test 6: Full Document Package Generation
echo ""
echo "Test 6: Full Document Package"
echo "----------------------------"
if [ -f "/Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json" ]; then
    echo "📦 Generating full document package..."
    /Users/corelogic/satori-dev/TM/monkey/run.sh build-complaint /Users/corelogic/satori-dev/TM/test-data/test-json/hydrated-test-0.json --all -o /Users/corelogic/satori-dev/TM/monkey/outputs/testing/package/
    echo "✅ Full package generation test completed"
else
    echo "⏭️ No test JSON found, skipping package generation test"
fi

# Test 7: Schema Integration
echo ""
echo "Test 7: Schema Integration"
echo "------------------------"
(cd /Users/corelogic/satori-dev/TM/monkey && source venv/bin/activate && python -c "
try:
    from satori_schema.hydrated_json_schema import HydratedJSON
    print(f'✅ Shared schema imported successfully')
    
    from core.validators import DocumentValidator
    print(f'✅ Monkey document validator imported successfully')
    
    from core.document_builder import MonkeyDocumentBuilder
    print(f'✅ Monkey document builder imported successfully')
    
    from core.html_engine import HtmlEngine
    print(f'✅ Monkey html engine imported successfully')
    
    # Test template engine initialization
    html_engine = HtmlEngine()
    templates = html_engine.list_templates()
    print(f'✅ Template engine test: {len(templates)} templates found')
    
except Exception as e:
    print(f'❌ Schema integration test failed: {e}')
")

# Test 8: Tiger JSON Compatibility (if Tiger outputs exist)
echo ""
echo "Test 8: Tiger JSON Compatibility"
echo "------------------------------"
TIGER_OUTPUT=$(find /Users/corelogic/satori-dev/TM/tiger/outputs/testing/ -name "*.json" -type f 2>/dev/null | head -1)
if [ -n "$TIGER_OUTPUT" ] && [ -f "$TIGER_OUTPUT" ]; then
    echo "🔗 Testing compatibility with Tiger output: $(basename "$TIGER_OUTPUT")"
    /Users/corelogic/satori-dev/TM/monkey/run.sh validate "$TIGER_OUTPUT"
    echo "✅ Tiger JSON compatibility test completed"
else
    echo "⏭️ No Tiger outputs found, skipping compatibility test"
    echo "   Run /Users/corelogic/satori-dev/TM/scripts/t.sh first to generate Tiger outputs"
fi

# Test 9: Output Structure
echo ""
echo "Test 9: Output Structure"
echo "----------------------"
echo "📁 Checking output directories..."
mkdir -p /Users/corelogic/satori-dev/TM/monkey/outputs/{production,testing,development}
echo "✅ Production directory: $(ls -ld /Users/corelogic/satori-dev/TM/monkey/outputs/production/ | awk '{print $1, $3, $4}')"
echo "✅ Testing directory: $(ls -ld /Users/corelogic/satori-dev/TM/monkey/outputs/testing/ | awk '{print $1, $3, $4}')"
echo "✅ Development directory: $(ls -ld /Users/corelogic/satori-dev/TM/monkey/outputs/development/ | awk '{print $1, $3, $4}')"

# Show output summary
echo ""
echo "📊 Monkey Test Summary"
echo "====================="
echo "🔍 Generated outputs in testing directory:"
if [ "$(ls -A /Users/corelogic/satori-dev/TM/monkey/outputs/testing/ 2>/dev/null)" ]; then
    find /Users/corelogic/satori-dev/TM/monkey/outputs/testing/ -type f -exec ls -la {} \;
else
    echo "   (No test outputs generated)"
fi

echo ""
echo "📋 Template availability:"
if [ -d "/Users/corelogic/satori-dev/TM/monkey/templates/fcra/" ]; then
    ls -la /Users/corelogic/satori-dev/TM/monkey/templates/fcra/
else
    echo "   ❌ FCRA templates directory not found"
fi

echo ""
echo "✅ Monkey service tests completed!"
echo "📋 Ready for integration with Tiger service"
echo ""
echo "Next steps:"
echo "  - Run Tiger tests: /Users/corelogic/satori-dev/TM/scripts/t.sh"
echo "  - Run integration test: /Users/corelogic/satori-dev/TM/scripts/tm.sh"
