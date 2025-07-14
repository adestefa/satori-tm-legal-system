# Timeline Validation System Testing

This directory contains comprehensive test scripts to validate the MVP 1 Timeline Validation System functionality and prevent regressions during future development.

## Quick Start

### Run Quick Test (Recommended)
```bash
# Simple 4-step verification test
./quick_timeline_test.sh
```

### Run Full Test Suite
```bash
# Comprehensive 22-test validation
./test_timeline_validation.sh
```

## Test Scripts Overview

### 1. `quick_timeline_test.sh` - Development Quick Check

**Purpose:** Fast verification that timeline validation is working  
**Duration:** ~5 seconds  
**Use Case:** Before/after making code changes  

**Tests:**
- Dashboard service availability
- Timeline validation API functionality
- Review page timeline tab presence
- JavaScript integration

**Example Output:**
```
Timeline Validation Quick Test
==================================

1. Checking dashboard...
   ✓ Dashboard is running
2. Testing Rodriguez timeline validation...
   ✓ Timeline API working
     - Validation Score: 40.7/100
     - Chronologically Valid: false
     - Critical Errors: 10
3. Testing review page...
   ✓ Review page has timeline tab
4. Testing JavaScript integration...
   ✓ Timeline JavaScript loaded

🎉 All tests passed! Timeline validation system is working.
```

### 2. `test_timeline_validation.sh` - Comprehensive Test Suite

**Purpose:** Full regression testing and detailed validation  
**Duration:** ~30 seconds  
**Use Case:** Before releases, after major changes  

**Test Categories:**
- **API Endpoints (3 tests):** Service availability, timeline APIs
- **Data Structure (4 tests):** JSON schema validation, field presence
- **Validation Logic (3 tests):** Chronological business rules
- **Date Parsing (2 tests):** Flexible date format handling
- **Frontend Integration (6 tests):** UI components, JavaScript loading
- **Error Handling (2 tests):** Invalid inputs, graceful degradation

**Success Criteria:** 20+ tests pass, 0 failures, warnings acceptable

## Test Cases & Data

### Primary Test Case: Rodriguez
- **Type:** Invalid timeline with known chronological errors
- **Expected:** Low validation score (~40), multiple errors detected
- **Purpose:** Verify validation rules work correctly

### Secondary Test Case: youssef  
- **Type:** Case without timeline data (graceful handling test)
- **Expected:** `timeline_available: false`, score 0
- **Purpose:** Verify error handling for missing data

## Critical Test Scenarios

### 1. Chronological Validation Logic
**Test:** Rodriguez case application/denial date violations  
**Expected:** Detect "Application date after denial date" errors  
**Importance:** Core business rule validation

### 2. Date Format Parsing
**Test:** "June 15, 2025" text format handling  
**Expected:** No parsing errors, date properly extracted  
**Importance:** Fixed critical bug that was causing validation failures

### 3. Frontend Integration
**Test:** Timeline tab accessibility in review page  
**Expected:** Tab visible, JavaScript loads, API calls work  
**Importance:** User interface functionality

### 4. API Data Structure
**Test:** Timeline validation endpoint JSON response  
**Expected:** All required fields present, proper data types  
**Importance:** Frontend-backend compatibility

## Running Tests

### Prerequisites
```bash
# Start dashboard
./dashboard/start.sh

# Verify test cases exist
ls test-data/sync-test-cases/Rodriguez
ls test-data/sync-test-cases/youssef

# Optional: Install jq for detailed JSON validation
brew install jq
```

### Test Execution
```bash
# Quick check (daily development)
./quick_timeline_test.sh

# Full validation (before commits)  
./test_timeline_validation.sh

# Manual UI testing
open http://127.0.0.1:8000/review?case_id=Rodriguez
# Click "Timeline Validation" tab
```

## Interpreting Results

### Quick Test Results
- **All Green (✓):** System working correctly
- **Any Red (✗):** Critical issue - investigate immediately

### Full Test Suite Results
- **20+ Passed, 0 Failed:** System healthy, ready for development
- **Any Failures:** Critical regressions - must fix before proceeding
- **Warnings:** Non-critical issues - review but may proceed

### Common Issues & Fixes

#### Dashboard Not Running
```
✗ Dashboard not running - start with ./dashboard/start.sh
```
**Fix:** `./dashboard/start.sh`

#### Timeline API Errors
```
✗ Timeline API failed
```
**Fix:** Check if Rodriguez case has been processed:
```bash
ls outputs/tests/Rodriguez/hydrated_*.json
```

#### JavaScript Not Loading
```
✗ Timeline JavaScript not found
```
**Fix:** Clear browser cache or check cache-busting version numbers

#### Missing Test Data
```
✗ Timeline JSON file not found
```
**Fix:** Process test cases through Tiger service:
```bash
./tiger/run.sh hydrated-json test-data/sync-test-cases/Rodriguez
```

## Regression Prevention

### Before Making Changes
1. Run `./quick_timeline_test.sh` - establish baseline
2. Save test artifacts: `cp -r /tmp/timeline_tests baseline_artifacts/`

### After Making Changes
1. Run `./quick_timeline_test.sh` - immediate verification
2. Run `./test_timeline_validation.sh` - full validation
3. Compare results with baseline
4. Test manually: Navigate to timeline validation tab

### Critical Breakage Indicators
- **API returning 500 errors:** Backend timeline validation broken
- **Timeline tab missing:** Frontend integration broken
- **Validation logic not working:** Business rules corrupted
- **JavaScript errors in console:** Frontend timeline UI broken

## Test Artifacts

Test scripts generate artifacts in `/tmp/timeline_tests/`:
- `test_results.log` - Detailed test execution log
- `{case}_timeline.json` - Timeline validation API responses
- `{case}_review.html` - Review page HTML for inspection

**Retention:** Artifacts cleared on next test run

## Adding New Test Cases

### New Timeline Validation Rules
1. Add test in `test_validation_logic()` function
2. Update expected error counts
3. Document new business rule in TEST_CASES.md

### New Frontend Components
1. Add HTML element checks in `test_frontend_integration()`
2. Test new JavaScript functionality
3. Verify responsive design on mobile

### New API Endpoints
1. Add endpoint test in `test_api_endpoints()`
2. Validate JSON schema in `test_timeline_data_structure()`
3. Test error conditions in `test_error_handling()`

## Continuous Integration

### Daily Development Workflow
```bash
# Before coding
./quick_timeline_test.sh

# After changes
./quick_timeline_test.sh

# Before committing
./test_timeline_validation.sh
```

### Release Validation
```bash
# Full test suite
./test_timeline_validation.sh

# Manual UI verification
# 1. Navigate to each test case review page
# 2. Verify timeline tab functionality
# 3. Test validation score display
# 4. Confirm error/warning messages

# Performance verification
# - API response time < 1 second
# - Timeline UI loads without delay
# - No JavaScript errors in console
```

This testing framework ensures the timeline validation system remains functional and reliable as the codebase evolves. The quick test provides immediate feedback during development, while the comprehensive test suite prevents regressions before releases.