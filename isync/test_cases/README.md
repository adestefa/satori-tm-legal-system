# TM iSync Test Cases

This directory contains test cases and sample data for comprehensive testing of the TM iSync adapter system.

## Directory Structure

```
test_cases/
├── sample_sync_cases/          # Sample case folders for sync testing
│   ├── TestCase_Simple/        # Simple FCRA case with basic documents
│   └── TestCase_Complex/       # Complex multi-defendant case
├── performance_test_data/      # Large files for performance testing
├── edge_case_scenarios/        # Edge cases and corner scenarios
└── validation_configs/         # Test configurations for validation
```

## Test Case Categories

### 1. Sample Sync Cases
Real-world case examples for testing file synchronization:

- **TestCase_Simple**: Basic FCRA case with standard documents
  - Attorney notes (TXT format)
  - Credit report (PDF format)
  - Clear violation patterns for Tiger processing

- **TestCase_Complex**: Multi-defendant case with multiple document types
  - Attorney notes (DOCX format)
  - Identity theft documentation
  - Dispute correspondence history
  - Multiple defendants and violation types

### 2. Performance Test Data
Files designed to test system performance and resource handling:

- Large PDF files (>10MB)
- Many small files in single case
- Files with special characters in names
- Deeply nested directory structures

### 3. Edge Case Scenarios
Unusual situations to test system robustness:

- Empty case folders
- Files with no extensions
- Corrupted or unreadable files
- Cases with missing attorney notes
- Files with unicode characters

### 4. Validation Configs
Test configurations for validation testing:

- Valid iCloud configurations
- Invalid credential combinations
- Malformed configuration files
- Edge case folder paths

## Usage in Testing

### Integration Testing
```bash
# Run integration tests with sample cases
python3 test_sync.py --test sync

# Use specific test case
export TEST_CASE_DIR="/path/to/test_cases/sample_sync_cases/TestCase_Simple"
python3 test_sync.py --test sync
```

### Error Scenario Testing
```bash
# Test error handling with edge cases
python3 test_errors.py --scenario filesystem

# Test with performance data
python3 test_errors.py --scenario resource
```

### Manual Testing
1. Copy test cases to your sync folder
2. Configure Dashboard with test credentials
3. Monitor sync behavior through Dashboard interface
4. Verify Tiger processing of test documents
5. Check Monkey document generation

## Test Case Validation

Each test case should contain:
- ✅ Attorney notes (TXT or DOCX)
- ✅ At least one supporting document (PDF)
- ✅ Clear legal case structure
- ✅ Realistic client information
- ✅ Proper violation categories

## Adding New Test Cases

To add new test cases:

1. Create new directory under `sample_sync_cases/`
2. Add attorney notes file
3. Add supporting documents
4. Update this README
5. Test with both Tiger and integration tests

## Security Note

All test cases use fictional data:
- Client names and contact information are not real
- Account numbers are fake
- Legal case details are for testing only
- Do not use real client data in test cases

## Performance Benchmarks

Expected performance for test cases:
- **TestCase_Simple**: Tiger processing < 5 seconds
- **TestCase_Complex**: Tiger processing < 15 seconds
- **Sync operations**: < 10 seconds for small cases
- **Package generation**: < 30 seconds including test cases