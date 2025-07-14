# Timeline Validation System Test Cases

This document outlines critical test cases for the MVP 1 Timeline Validation System to ensure functionality and prevent regressions.

## Test Script Usage

```bash
# Run the complete test suite
./test_timeline_validation.sh

# Prerequisites
- Dashboard must be running: ./dashboard/start.sh
- Test cases Rodriguez and youssef must exist in test-data/sync-test-cases/
- jq tool recommended for detailed JSON validation
```

## Critical Test Cases

### 1. **API Endpoint Availability**

**Purpose:** Ensure all timeline validation APIs are accessible and responding correctly.

**Test Cases:**
- `GET /api/cases` - Returns list of available cases
- `GET /api/cases/{case_id}/validate-timeline` - Returns timeline validation data
- `GET /review?case_id={case_id}` - Loads review page with timeline tab

**Success Criteria:**
- All endpoints return HTTP 200
- JSON responses contain required fields
- Review page loads without errors

**Failure Indicators:**
- HTTP 500/404 errors indicate backend issues
- Missing JSON fields suggest schema problems
- Review page errors indicate frontend integration issues

### 2. **Timeline Data Structure Validation**

**Purpose:** Verify timeline validation API returns properly structured data.

**Required Fields:**
```json
{
  "case_id": "string",
  "timeline_available": "boolean", 
  "is_chronologically_valid": "boolean",
  "validation_score": "number (0-100)",
  "timeline_confidence": "number (0-100)",
  "key_dates": {
    "discovery_date": "string|null",
    "dispute_date": "string|null", 
    "filing_date": "string|null"
  },
  "validation_details": {
    "errors": ["array of strings"],
    "warnings": ["array of strings"]
  },
  "summary": {
    "key_dates_present": "number",
    "document_dates_extracted": "number",
    "critical_errors": "number",
    "warnings": "number"
  }
}
```

**Success Criteria:**
- All required fields present
- Validation score 0-100 range
- Proper data types for all fields

### 3. **Chronological Validation Logic**

**Purpose:** Verify business rules for chronological validation are working correctly.

**Test Case: Rodriguez (Known Invalid Timeline)**
- **Expected:** `is_chronologically_valid: false`
- **Expected:** Multiple errors in `validation_details.errors`
- **Expected:** Validation score < 50
- **Specific Rule:** Application dates after denial dates should be flagged

**Test Case: Youssef (More Valid Timeline)**
- **Expected:** Higher validation score than Rodriguez
- **Expected:** Fewer chronological errors
- **Expected:** Key dates properly extracted

**Critical Business Rules Tested:**
1. **Application < Denial Rule:** Application dates must be before denial dates
2. **Discovery < Dispute Rule:** Discovery date must be before dispute date (if both present)
3. **Damage < Filing Rule:** All damage events must be before filing date
4. **Future Date Detection:** No dates should be in the future
5. **Reasonable Date Range:** Dates should be post-1990

### 4. **Date Parsing Improvements**

**Purpose:** Verify the flexible date parser handles various date formats correctly.

**Critical Date Formats Tested:**
- `"June 15, 2025"` - Full month name format (previously failed)
- `"Jun 15, 2025"` - Abbreviated month format
- `"06/15/2025"` - Numeric format with slashes
- `"06-15-2025"` - Numeric format with dashes
- `"2025-06-15"` - ISO format

**Success Criteria:**
- Filing dates extracted correctly for both test cases
- No parsing errors in validation details
- June 15 format specifically handled (Rodriguez case)

### 5. **Frontend Integration**

**Purpose:** Ensure timeline validation UI is properly integrated into review page.

**Visual Components Tested:**
- **Timeline Validation Tab:** Present in review page navigation
- **Timeline Validation Badge:** Shows validation score with color coding
- **Key Dates Summary:** Discovery, dispute, filing dates with status
- **Validation Issues:** Error and warning messages display
- **Timeline Chart:** Visual representation of chronological sequence
- **Document Dates Table:** Extracted dates with source information

**JavaScript Integration:**
- `timeline-validation.js` script loaded
- `TimelineValidationUI` class initialized
- API calls to `/api/cases/{case_id}/validate-timeline` working
- Tab switching functionality working

### 6. **Error Handling & Edge Cases**

**Purpose:** Verify system handles errors gracefully.

**Test Cases:**
- **Invalid Case ID:** Should return 404 or handle gracefully
- **Missing Timeline Data:** Should show appropriate message
- **API Connection Failure:** Should display error state
- **Malformed JSON:** Should not crash frontend

**Success Criteria:**
- No JavaScript errors in browser console
- User-friendly error messages displayed
- System remains stable with invalid inputs

## Regression Prevention

### Before Making Changes

1. **Run Full Test Suite:** `./test_timeline_validation.sh`
2. **Document Baseline:** Save test results for comparison
3. **Manual Testing:** Verify UI functionality in browser

### After Making Changes

1. **Re-run Test Suite:** Ensure no regressions
2. **Compare Results:** Check for any newly failing tests
3. **UI Verification:** Test timeline tab functionality manually
4. **Performance Check:** Verify API response times acceptable

### Critical Breakage Indicators

**Backend Issues:**
- Timeline validation API returns 500 errors
- Missing required fields in JSON response
- Validation logic not detecting known errors

**Frontend Issues:**
- Timeline tab not visible in review page
- JavaScript errors in browser console
- Timeline data not loading or displaying

**Integration Issues:**
- API calls failing from frontend
- Timeline data structure mismatches
- Cache-busting not working (old JavaScript loading)

## Manual Test Checklist

### Dashboard Navigation Test
- [ ] Navigate to dashboard: `http://127.0.0.1:8000`
- [ ] Verify Rodriguez and youssef cases listed
- [ ] Click "Review" for Rodriguez case
- [ ] Timeline Validation tab visible and clickable

### Timeline Validation UI Test  
- [ ] Click Timeline Validation tab
- [ ] Validation badge shows score (e.g., "✗ Issues Found (40.7/100)")
- [ ] Key dates summary shows dispute and filing dates
- [ ] Validation issues section shows multiple errors
- [ ] Timeline chart displays chronological sequence
- [ ] Document dates table shows extracted dates

### Cross-Case Comparison
- [ ] Test youssef case timeline validation
- [ ] Compare validation scores (youssef should be higher)
- [ ] Verify different error patterns between cases
- [ ] Confirm timeline chart differences

## Test Data Requirements

### Required Test Cases
1. **Rodriguez:** Case with known chronological violations
2. **youssef:** Case with better timeline validation
3. Both cases must have generated hydrated JSON files

### Required File Structure
```
test-data/sync-test-cases/
├── Rodriguez/
│   ├── [case documents]
│   └── outputs/tests/Rodriguez/hydrated_*.json
└── youssef/
    ├── [case documents] 
    └── outputs/tests/youssef/hydrated_*.json
```

## Debugging Failed Tests

### API Endpoint Failures
1. Check dashboard is running: `curl http://127.0.0.1:8000`
2. Verify case files exist in test-data directory
3. Check Tiger service processed cases correctly
4. Review dashboard logs for errors

### Timeline Data Issues
1. Verify hydrated JSON files exist in outputs directory
2. Check timeline validation endpoint directly in browser
3. Use `jq` to inspect JSON structure: `jq '.' timeline_response.json`
4. Review case_consolidator.py for parsing errors

### Frontend Integration Problems
1. Check browser console for JavaScript errors
2. Verify timeline-validation.js loaded correctly
3. Test API calls in browser network tab
4. Confirm cache-busting working (hard refresh)

### Validation Logic Issues
1. Review chronological validation rules in case_consolidator.py
2. Check document date extraction accuracy
3. Verify business rule implementation
4. Test with known good/bad timeline data

This test suite provides comprehensive coverage of the timeline validation system and serves as a regression prevention mechanism for future development.