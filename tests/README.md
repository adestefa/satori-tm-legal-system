# Tiger Legal Extraction System - Test Suite

Comprehensive testing suite for the Tiger Legal Extraction System, designed to validate the accuracy, performance, and reliability of legal document processing and case consolidation capabilities.

## Test Structure

### Core Test Modules

1. **`test_legal_extraction.py`** - Core extraction functionality
   - Legal entity extraction (case numbers, courts, parties)
   - Case consolidation across multiple documents
   - Integration scenarios with complete legal workflows
   - Edge cases and error handling

2. **`test_performance.py`** - Performance and scalability
   - Processing speed benchmarks
   - Memory usage monitoring
   - Batch processing efficiency
   - Concurrent processing simulation
   - Scalability limits testing

3. **`test_data_validation.py`** - Data integrity and compliance
   - Complaint.json schema validation
   - Data consistency across pipeline
   - Legal document standards compliance
   - FCRA-specific requirements

4. **`run_all_tests.py`** - Comprehensive test runner
   - Orchestrates all test suites
   - Generates detailed reports
   - Performance metrics collection
   - Exit codes for CI/CD integration

## Quick Start

### Run Core Tests (Recommended)
```bash
cd tests/
PYTHONPATH=/Users/corelogic/satori-dev/test-app python3 run_simple_tests.py
```

### Run Comprehensive Tests  
```bash
cd tests/
PYTHONPATH=/Users/corelogic/satori-dev/test-app python3 test_comprehensive.py
```

### Run All Tests (Advanced - requires fixing imports)
```bash
cd tests/
python run_all_tests.py
```

### Run Specific Test Suites
```bash
# Core extraction tests
python -m unittest test_legal_extraction -v

# Performance tests
python -m unittest test_performance -v

# Data validation tests
python -m unittest test_data_validation -v
```

### Run Individual Test Cases
```bash
# Test legal entity extraction
python -m unittest test_legal_extraction.TestLegalEntityExtractor -v

# Test case consolidation
python -m unittest test_legal_extraction.TestCaseConsolidator -v

# Test performance benchmarks
python -m unittest test_performance.TestPerformance -v
```

## Test Categories

### 🔍 **Extraction Tests**
- **Case Number Extraction**: Federal and state court formats
- **Court Identification**: District courts, jurisdictions
- **Party Recognition**: Plaintiffs, defendants, multiple parties
- **Legal Entity Parsing**: Addresses, corporate entities
- **Date Extraction**: Various date formats in legal documents

### 🔄 **Integration Tests**
- **Complete FCRA Workflow**: End-to-end case processing
- **Multi-Document Cases**: Consolidation across summons, complaints, notes
- **Complaint.json Generation**: Structured legal data output
- **Tiger + Beaver Pipeline**: Full document generation workflow

### ⚡ **Performance Tests**
- **Document Size Scaling**: 5KB to 5MB+ documents
- **Batch Processing**: 10-100+ documents
- **Memory Efficiency**: Leak detection, resource usage
- **Concurrent Processing**: Multi-threaded simulation
- **Regex Performance**: Pattern matching optimization

### ✅ **Validation Tests**
- **Schema Compliance**: Complaint.json structure validation
- **Data Consistency**: Cross-document information matching
- **Legal Standards**: FCRA requirements, federal court formats
- **Confidence Scoring**: Extraction quality metrics

### 🚫 **Edge Case Tests**
- **Malformed Documents**: Invalid case numbers, corrupted text
- **Empty Content**: Missing files, blank documents
- **Mixed Content**: Legal + non-legal document combinations
- **Conflicting Information**: Inconsistent data across documents

## Test Data

The test suite uses both synthetic and real-world-inspired test data:

### Synthetic Test Cases
- **FCRA Simple Case**: Basic credit reporting dispute
- **Multi-Party Case**: Complex litigation with multiple defendants
- **State Court Case**: Non-federal jurisdiction testing
- **Large Document Case**: Performance testing with substantial content

### Performance Benchmarks
- **Small Documents**: < 10KB (target: < 1s processing)
- **Medium Documents**: 50-100KB (target: < 3s processing)
- **Large Documents**: 500KB+ (target: < 10s processing)
- **Batch Processing**: 10+ docs (target: > 2 docs/second)

## Success Criteria

### Core Functionality
- ✅ **95%+ extraction accuracy** on well-formatted legal documents
- ✅ **Case number recognition** for federal and state formats
- ✅ **Party identification** in standard legal document formats
- ✅ **Court jurisdiction parsing** for major US district courts

### Performance Standards
- ✅ **< 1 second** processing for documents under 10KB
- ✅ **< 10 seconds** processing for documents under 1MB
- ✅ **> 2 documents/second** batch processing throughput
- ✅ **< 100MB** memory usage for typical case folders

### Data Quality
- ✅ **Valid complaint.json** structure for all processed cases
- ✅ **Consistent data** across multi-document consolidation
- ✅ **Legal compliance** with FCRA and federal court requirements
- ✅ **Confidence scoring** accurately reflects extraction quality

## CI/CD Integration

The test runner provides appropriate exit codes for automated testing:

```bash
# Success (exit code 0): >= 80% test success rate
# Failure (exit code 1): < 80% test success rate
```

### Test Reports
- **Console Output**: Real-time test execution feedback
- **JSON Reports**: `test_results.json` with detailed metrics
- **Performance Metrics**: Execution times, memory usage
- **Failure Analysis**: Categorized issue breakdown

## Development Workflow

### Before Committing
```bash
# Run full test suite
python tests/run_all_tests.py

# Verify no regressions
python -m unittest tests.test_legal_extraction.TestIntegrationScenarios -v
```

### Performance Monitoring
```bash
# Run performance benchmarks
python -m unittest tests.test_performance.TestPerformance -v

# Check for memory leaks
python -m unittest tests.test_performance.TestPerformance.test_memory_leak_detection -v
```

### Adding New Tests

1. **For new extractors**: Add tests to `test_legal_extraction.py`
2. **For performance**: Add benchmarks to `test_performance.py`
3. **For validation**: Add schema tests to `test_data_validation.py`
4. **Update test runner**: Add new test classes to `run_all_tests.py`

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the correct directory
cd /Users/corelogic/satori-dev/test-app/tests/

# Check Python path
export PYTHONPATH="/Users/corelogic/satori-dev/test-app:$PYTHONPATH"
```

**Missing Dependencies**
```bash
# Install test dependencies
pip install psutil  # For performance monitoring
```

**Test Data Issues**
```bash
# Verify test data exists
ls ../test-data/synthetic-cases/
```

### Performance Issues

If tests are running slowly:
- Check available system memory
- Reduce test document sizes
- Run individual test suites instead of full suite
- Monitor system resource usage during tests

## Contributing

When adding new legal extraction capabilities:

1. **Write tests first** - Define expected behavior
2. **Include edge cases** - Test malformed inputs
3. **Add performance tests** - Ensure scalability
4. **Validate output** - Check legal compliance
5. **Update documentation** - Keep README current

## Legal Compliance Note

All test data is synthetic and designed for testing purposes only. No real case information or personal data is used in the test suite. The testing framework validates compliance with legal document standards but does not constitute legal advice.