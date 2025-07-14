# Tiger Test Output Management

This directory provides a clean testing environment for Tiger document processing with easy cleanup capabilities.

## Directory Structure

```
tests/
├── output/                 # All test output goes here
│   ├── processed/         # Successfully processed documents
│   ├── reports/           # Quality and batch reports
│   ├── metadata/          # Processing metadata
│   ├── failed/            # Failed processing attempts
│   └── logs/              # Test run logs
├── cleanup.sh             # Cleanup utility script
└── README_test_output.md  # This documentation
```

## Usage

### Running Tests with Custom Output Directory

Use the `--output-dir` parameter to direct all Tiger output to the test directory:

```bash
# Process single document
./satori-tiger process document.pdf --output-dir ./tests/output/

# Process directory
./satori-tiger batch ./case_files/ --output-dir ./tests/output/

# Case extraction
./satori-tiger case-extract ./case_folder/ --output-dir ./tests/output/ --complaint-json

# Alternative short form
./satori-tiger process document.pdf -o ./tests/output/
```

### Cleanup After Testing

Clean up all test output files while preserving directory structure:

```bash
# From project root
cd tests && ./cleanup.sh

# Force cleanup (no confirmation prompt)
cd tests && ./cleanup.sh --force
```

The cleanup utility:
- ✅ Removes all generated test files
- ✅ Preserves directory structure for future tests
- ✅ Shows file count before and after cleanup
- ✅ Confirms successful cleanup

## Benefits

1. **Isolated Testing**: Test output separated from production data
2. **Easy Cleanup**: Single command to purge all test files
3. **Preserved Structure**: Directory layout maintained for consistent testing
4. **Safe Operations**: No impact on existing production workflows

## Examples

### Complete Test Workflow

```bash
# 1. Run test with custom output
./satori-tiger case-extract test-data/synthetic-cases/fcra-simple/ --output-dir ./tests/output/ --complaint-json

# 2. Verify results
ls -la tests/output/processed/
cat tests/output/_complaint.json

# 3. Clean up for next test
cd tests && ./cleanup.sh --force

# 4. Ready for next test run
```

### Integration with Test Scripts

```bash
# In your test scripts, use:
OUTPUT_DIR="./tests/output"
./satori-tiger process "$TEST_FILE" --output-dir "$OUTPUT_DIR"

# Clean up after test suite
cd tests && ./cleanup.sh --force
```

This testing infrastructure ensures clean, isolated test runs with minimal setup and easy maintenance.