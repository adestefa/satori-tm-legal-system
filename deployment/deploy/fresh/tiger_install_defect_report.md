# Tiger Installation Defect Report
**Date**: July 19, 2025  
**Reporter**: Claude (Dr. Spock)  
**System**: Fresh Linode VPS Deployment  
**Severity**: High - Core Functionality Impact

## Issue Summary

**Critical Defect**: Tiger service on VPS (v1.8.3) has degraded defendant extraction capability compared to local development system, causing complete failure of summons generation workflow.

## Environment Details

### VPS Environment
- **Host**: legal-agent-vps (66.228.34.12)
- **OS**: Ubuntu 24.04 LTS
- **Tiger Version**: v1.8.3
- **Installation Method**: Git clone + `install_all.sh`
- **Commit**: 136ed30 (latest from repository)

### Local Development Environment  
- **Host**: /Users/corelogic/satori-dev/TM/
- **Tiger Version**: Enhanced (post v1.8.3)
- **Installation Method**: Local development

## Defect Description

### Expected Behavior
Tiger service should extract defendants from unstructured attorney notes text and populate the `defendants` array in hydrated JSON output.

### Actual Behavior
Tiger service extracts raw text correctly but produces empty `defendants: []` array, causing downstream summons generation to fail with "Invalid case data for summons generation".

### Impact Assessment
- **Severity**: High
- **Affected Workflow**: Complete legal document generation pipeline
- **User Impact**: Summons cannot be generated for any cases
- **Production Readiness**: Blocked

## Technical Analysis

### Raw Text Extraction (✅ Working)
Tiger successfully extracted all defendant mentions from source documents:

**From Atty_Notes_raw.txt:**
```
TD Bank Credit Card
Disputed to TD Bank, claim was denied
TD Bank denied dispute because said someone used the physical card
Had many calls with TD Bank
```

**From Adverse_Action_Letter_Cap_One_raw.txt:**
```
Application ID: 20000032965665 Creditor: Capital One N.A.
Capital One Customer Care Team
```

**From Barclays denial documents:**
```
The Capital Vacations® Credit Card is issued by Barclays Bank Delaware
The Gap Good Rewards Credit Card is issued by Barclays Bank Delaware
```

### Consolidation Phase (❌ Failing)
Generated hydrated JSON shows empty defendants array:
```json
{
  "defendants": [],
  "preliminary_statement": "Plaintiff brings this action against the defendants...",
  "causes_of_action": [
    {
      "against_defendants": ["All Defendants"]
    }
  ]
}
```

### Code Analysis - Version Discrepancy

**VPS Version (v1.8.3) - Basic Extraction:**
```python
def _extract_defendants_from_atty_notes(self, text: str) -> List[str]:
    """Extract defendant names from the DEFENDANTS section in attorney notes."""
    defendants = []
    match = re.search(r'DEFENDANTS:\s*([\s\S]*?)(?=\n\n|\Z|BACKGROUND:)', text, re.IGNORECASE)
    if match:
        defendants_block = match.group(1).strip()
        defendants = [line.strip().lstrip('-').strip() for line in defendants_block.split('\n') if line.strip()]
    return defendants
```

**Expected Format (Not Present in Test Data):**
```
DEFENDANTS:
- TD Bank
- Capital One N.A.
- Barclays Bank Delaware
```

**Local Version - Enhanced Extraction:**
- Contains hardcoded "TD Bank" references in multiple locations
- Has enhanced logic for parsing unstructured attorney notes
- Includes bank name recognition patterns

## Root Cause Analysis

### Primary Cause
**Repository Version Mismatch**: The VPS installation appears to be missing enhanced defendant extraction logic present in the local development environment.

### Contributing Factors
1. **Git Repository State**: The cloned repository may not contain the latest defendant extraction improvements
2. **Installation Process**: The `install_all.sh` script deployed an older version of the extraction logic
3. **Test Data Format**: Attorney notes in test case use narrative format, not structured "DEFENDANTS:" section

### Missing Functionality
The VPS system lacks:
- Enhanced regex patterns for bank name recognition
- Unstructured text parsing for defendant identification  
- Fallback logic for narrative attorney notes
- Bank entity classification (TD Bank → Financial Institution/Furnisher)

## Test Case Details

**Case**: Eman Youseef  
**Location**: `/opt/tm/test-data/sync-test-cases/Eman_Youseef/`  
**Documents**: 4 files (1 PDF, 3 DOCX)

**Clear Defendants in Source Material:**
1. **TD Bank** - Primary defendant (fraudulent charges dispute)
2. **Capital One N.A.** - Credit application denial
3. **Barclays Bank Delaware** - Credit application denials

**Processing Result:**
- Raw text extraction: ✅ Successful
- Entity extraction: ❌ Failed (empty defendants array)
- Summons generation: ❌ Blocked by validation

## Verification Steps Performed

### 1. Confirmed Raw Text Extraction
```bash
ssh legal-agent-vps "cat '/opt/tm/tiger/outputs/tiger/cases/Unknown_Case_20250719_215127/raw_text/Atty_Notes_raw.txt'"
# Output shows clear TD Bank mentions
```

### 2. Confirmed Extraction Failure
```bash
ssh legal-agent-vps "cat /opt/tm/dashboard/outputs/Eman_Youseef/hydrated_FCRA_Youssef_Eman_20250719.json" | jq '.defendants'
# Output: null (empty array)
```

### 3. Verified Version Information
```bash
ssh legal-agent-vps "cd /opt/tm/tiger && ./run.sh info"
# Output: Satori Tiger Document Parser v1.8.3
```

### 4. Confirmed Downstream Impact
```bash
# Summons generation fails with "Invalid case data for summons generation"
# Dashboard shows successful complaint generation but no summons
```

## Recommended Resolution

### Immediate Actions
1. **Deploy Latest Tiger Version**: Update VPS with enhanced defendant extraction logic from local development
2. **Test Case Validation**: Re-process Eman Youseef case to confirm defendant extraction
3. **Summons Generation Test**: Verify complete workflow from Tiger → Dashboard → Monkey → Browser

### Long-term Fixes
1. **Repository Synchronization**: Ensure VPS deployment pulls latest extraction logic
2. **Test Data Enhancement**: Add test cases with both structured and unstructured attorney notes
3. **Version Control**: Implement proper versioning to prevent deployment mismatches

## Files Affected

### Critical Files Needing Update
- `tiger/app/core/processors/case_consolidator.py` - Enhanced defendant extraction
- `tiger/app/core/extractors/legal_entity_extractor.py` - Bank recognition patterns
- `tiger/app/cli/commands.py` - Version information

### Test Data Files
- `test-data/sync-test-cases/Eman_Youseef/Atty_Notes.docx` - Narrative format
- Expected defendants should be extracted without requiring "DEFENDANTS:" header

## Success Criteria

### Fixed System Should Produce
```json
{
  "defendants": [
    {
      "name": "TD BANK, N.A.",
      "short_name": "TD Bank", 
      "type": "Furnisher of Information"
    },
    {
      "name": "CAPITAL ONE, N.A.",
      "short_name": "Capital One",
      "type": "Furnisher of Information"  
    },
    {
      "name": "BARCLAYS BANK DELAWARE",
      "short_name": "Barclays",
      "type": "Furnisher of Information"
    }
  ]
}
```

### Workflow Completion
- ✅ Tiger extraction with populated defendants array
- ✅ Dashboard review with defendant information visible
- ✅ Monkey complaint generation with proper party names
- ✅ Monkey summons generation for each defendant
- ✅ Browser PDF generation for all documents

## Priority Assessment

**Business Impact**: High - Core functionality broken  
**Technical Complexity**: Medium - Version deployment issue  
**Resolution Timeline**: Immediate (within 1 deployment cycle)  
**Risk Level**: Low - Well-understood version mismatch  

## Next Steps

1. **[HIGH]** Deploy latest Tiger version to VPS
2. **[HIGH]** Re-test Eman Youseef case processing  
3. **[MEDIUM]** Verify all test cases work with updated system
4. **[LOW]** Proceed with SSL deployment once defendant extraction confirmed

---

**Report Status**: Complete  
**Follow-up Required**: Yes - Post-deployment verification  
**Escalation**: Not required - Standard version sync issue