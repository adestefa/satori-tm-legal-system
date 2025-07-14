#!/bin/bash
#
# Tiger Service Test Script
# Tests Tiger document processing with proper virtual environment
#

set -e

echo "🐅 Tiger Service Test Suite"
echo "==========================="

# Test 1: Health Check
echo ""
echo "Test 1: Health Check"
echo "-------------------"
/Users/corelogic/satori-dev/TM/tiger/health_check.sh

# Test 2: Service Info
echo ""
echo "Test 2: Service Information"
echo "-------------------------"
/Users/corelogic/satori-dev/TM/tiger/run.sh info

# Test 3: Single Document Processing (if test documents exist)
echo ""
echo "Test 3: Document Processing"
echo "-------------------------"
if [ -f "/Users/corelogic/satori-dev/TM/test-data/documents/sample.pdf" ]; then
    echo "📄 Processing sample document..."
    /Users/corelogic/satori-dev/TM/tiger/run.sh process /Users/corelogic/satori-dev/TM/test-data/documents/sample.pdf -o /Users/corelogic/satori-dev/TM/tiger/outputs/testing/
    echo "✅ Document processing test completed"
else
    echo "⏭️ No sample document found, skipping document processing test"
fi

# Test 4: Document Validation (if test documents exist)
echo ""
echo "Test 4: Document Validation"
echo "-------------------------"
TEST_DOC=$(find /Users/corelogic/satori-dev/TM/test-data/ -name "*.pdf" -type f | head -1)
if [ -n "$TEST_DOC" ]; then
    echo "🔍 Validating document: $(basename "$TEST_DOC")"
    /Users/corelogic/satori-dev/TM/tiger/run.sh validate "$TEST_DOC"
    echo "✅ Document validation test completed"
else
    echo "⏭️ No test documents found, skipping validation test"
fi

# Test 5: Case Consolidation (if case folders exist)
echo ""
echo "Test 5: Case Consolidation"
echo "------------------------"
CASE_DIR="/Users/corelogic/satori-dev/TM/test-data/cases-for-testing/Rodriguez"
if [ -n "$CASE_DIR" ] && [ -d "$CASE_DIR" ]; then
    echo "📁 Processing case folder: $(basename "$CASE_DIR")"
    /Users/corelogic/satori-dev/TM/tiger/run.sh hydrated-json "$CASE_DIR" -o /Users/corelogic/satori-dev/TM/tiger/outputs/testing/
    echo "✅ Case consolidation test completed"
else
    echo "⏭️ No case folders found, skipping case extraction test"
fi

# Test 6: Schema Integration
echo ""
echo "Test 6: Schema Integration"
echo "------------------------"
(cd /Users/corelogic/satori-dev/TM/tiger && source venv/bin/activate && python /Users/corelogic/satori-dev/TM/tests/tiger_schema_test.py)


# Test 7: Output Structure
echo ""
echo "Test 7: Output Structure"
echo "----------------------"
echo "📁 Checking output directories..."
mkdir -p /Users/corelogic/satori-dev/TM/tiger/outputs/{production,testing,development}
echo "✅ Production directory: $(ls -ld /Users/corelogic/satori-dev/TM/tiger/outputs/production/ | awk '{print $1, $3, $4}')"
echo "✅ Testing directory: $(ls -ld /Users/corelogic/satori-dev/TM/tiger/outputs/testing/ | awk '{print $1, $3, $4}')"
echo "✅ Development directory: $(ls -ld /Users/corelogic/satori-dev/TM/tiger/outputs/development/ | awk '{print $1, $3, $4}')"

# Show output summary
echo ""
echo "📊 Tiger Test Summary"
echo "===================="
echo "🔍 Generated outputs in testing directory:"
if [ "$(ls -A /Users/corelogic/satori-dev/TM/tiger/outputs/testing/ 2>/dev/null)" ]; then
    ls -la /Users/corelogic/satori-dev/TM/tiger/outputs/testing/
else
    echo "   (No test outputs generated)"
fi

echo ""
echo "✅ Tiger service tests completed!"
echo "📋 Ready for integration with Monkey service"
echo ""
echo "Next steps:"
echo "  - Run Monkey tests: /Users/corelogic/satori-dev/TM/scripts/m.sh"
echo "  - Run integration test: /Users/corelogic/satori-dev/TM/scripts/tm.sh"