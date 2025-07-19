# Repository Synchronization & Defendant Extraction Fix Plan
**Date**: July 19, 2025  
**Objective**: Synchronize local and VPS TM repositories to fix defendant extraction defect  
**Target**: Enable enhanced defendant extraction from unstructured attorney notes

## Current State Analysis

### Local Repository Status
- **Location**: `/Users/corelogic/satori-dev/TM/`
- **Branch**: `gemini-sync-upload`
- **Tiger Version**: Enhanced (post v1.8.3)
- **Status**: Working defendant extraction from narrative attorney notes

### VPS Repository Status
- **Location**: `/opt/tm/`
- **Deployment**: Git clone from fresh repository
- **Tiger Version**: v1.8.3
- **Status**: Basic defendant extraction (formal sections only)

### Gap Analysis
The VPS system is missing enhanced defendant extraction logic that can parse defendants from unstructured text formats.

## Enhancement Requirements

### Core Enhancement: Multi-Pattern Defendant Recognition
**Objective**: Extract defendants from various document formats and text patterns

**Current Pattern (VPS v1.8.3):**
```python
# Only matches formal sections
match = re.search(r'DEFENDANTS:\s*([\s\S]*?)(?=\n\n|\Z|BACKGROUND:)', text, re.IGNORECASE)
```

**Enhanced Patterns Needed:**
1. **Bank Mentions**: "TD Bank Credit Card" → "TD BANK, N.A."
2. **Denial Letters**: "Creditor: Capital One N.A." → "CAPITAL ONE, N.A."
3. **Issuer References**: "issued by Barclays Bank Delaware" → "BARCLAYS BANK DELAWARE"
4. **Context Recognition**: Financial institution identification in narrative text

## Implementation Plan

### Phase 1: Code Enhancement Development
**Branch Strategy**: Create feature branch for defendant extraction improvements

**Files to Enhance:**
```
tiger/app/core/processors/case_consolidator.py
├── _extract_defendants_from_atty_notes() - Enhanced pattern recognition
├── _extract_defendants_from_denial_letters() - NEW METHOD
├── _normalize_bank_names() - NEW METHOD
└── _consolidate_parties() - Enhanced logic

tiger/app/core/extractors/legal_entity_extractor.py
├── _extract_defendants() - Improved bank recognition
└── Enhanced regex patterns for financial institutions

tiger/app/cli/commands.py
└── Version bump to v1.9.0
```

### Phase 2: Pull Request Creation
**Branch**: `feature/enhanced-defendant-extraction`  
**Target**: `main` branch  
**Title**: "feat(tiger): Enhanced defendant extraction from unstructured text"

**PR Description Template:**
```markdown
## Enhancement Summary
Upgrades Tiger defendant extraction from basic pattern matching to comprehensive multi-source recognition.

## Problem Solved
- VPS Tiger v1.8.3 failed to extract defendants from Eman Youseef case
- Only worked with formal "DEFENDANTS:" sections
- Real attorney notes use narrative format

## Solution Implemented
- Multi-pattern bank recognition
- Denial letter creditor extraction  
- Context-aware defendant identification
- Normalized bank naming

## Test Case Validation
- Eman Youseef case: 0 → 3+ defendants extracted
- Enhanced coverage for TD Bank, Capital One, Barclays
- Backward compatible with existing test cases

## Version Update
Tiger v1.8.3 → v1.9.0
```

### Phase 3: VPS Deployment
**Deployment Method**: Git-based update via SSH

**Deployment Steps:**
```bash
# 1. Connect to VPS
ssh legal-agent-vps

# 2. Navigate to TM directory
cd /opt/tm

# 3. Pull latest changes
git fetch origin
git checkout main
git pull origin main

# 4. Restart Tiger-dependent services
sudo systemctl restart tm-dashboard

# 5. Verify version update
cd tiger && ./run.sh info
# Should show: Tiger v1.9.0

# 6. Test enhanced extraction
cd tiger && ./run.sh hydrated-json /opt/tm/test-data/sync-test-cases/Eman_Youseef/ -o /opt/tm/outputs/
```

## Enhanced Defendant Extraction Logic

### New Method: Multi-Source Recognition
```python
def _extract_defendants_from_atty_notes(self, text: str) -> List[str]:
    """Enhanced defendant extraction from multiple text patterns"""
    defendants = []
    
    # 1. Original formal section pattern
    formal_match = re.search(r'DEFENDANTS:\s*([\s\S]*?)(?=\n\n|\Z|BACKGROUND:)', text, re.IGNORECASE)
    if formal_match:
        defendants_block = formal_match.group(1).strip()
        defendants.extend([line.strip().lstrip('-').strip() for line in defendants_block.split('\n') if line.strip()])
    
    # 2. NEW: Bank mention patterns
    bank_patterns = [
        r'(TD Bank)',
        r'(Capital One)',
        r'(Barclays)',
        # ... additional patterns
    ]
    
    for pattern in bank_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            bank_name = self._normalize_bank_name(re.search(pattern, text, re.IGNORECASE).group(1))
            if bank_name not in defendants:
                defendants.append(bank_name)
    
    return defendants

def _normalize_bank_name(self, raw_name: str) -> str:
    """Normalize bank names to legal entity format"""
    normalization_map = {
        'TD Bank': 'TD BANK, N.A.',
        'Capital One': 'CAPITAL ONE, N.A.',
        'Barclays': 'BARCLAYS BANK DELAWARE',
        # ... additional mappings
    }
    return normalization_map.get(raw_name, raw_name.upper())
```

### New Method: Denial Letter Processing
```python
def _extract_defendants_from_denial_letters(self, extraction_results: List[ExtractionResult]) -> List[str]:
    """Extract creditors from denial letters and adverse action notices"""
    defendants = []
    
    for result in extraction_results:
        text = result.extracted_text
        
        # Pattern: "Creditor: BANK NAME"
        creditor_match = re.search(r'Creditor:\s*([A-Z][A-Za-z\s,\.&]+)', text)
        if creditor_match:
            creditor = self._normalize_bank_name(creditor_match.group(1).strip())
            if creditor not in defendants:
                defendants.append(creditor)
        
        # Pattern: "issued by BANK NAME"
        issuer_match = re.search(r'issued by\s+([A-Z][A-Za-z\s,\.&]+)', text, re.IGNORECASE)
        if issuer_match:
            issuer = self._normalize_bank_name(issuer_match.group(1).strip())
            if issuer not in defendants:
                defendants.append(issuer)
    
    return defendants
```

## Testing & Validation Plan

### Pre-Deployment Testing (Local)
```bash
# 1. Test enhanced extraction locally
cd /Users/corelogic/satori-dev/TM/tiger
./run.sh hydrated-json ../test-data/sync-test-cases/Eman_Youseef/ -o ../outputs/

# 2. Verify defendants array populated
cat ../outputs/hydrated_FCRA_*.json | jq '.defendants'
# Expected: Array with TD Bank, Capital One, Barclays

# 3. Test summons generation
cd ../monkey
./run.sh generate-summons ../outputs/hydrated_FCRA_*.json -o ../outputs/
# Expected: Summons files for each defendant
```

### Post-Deployment Validation (VPS)
```bash
# 1. Process test case on VPS
ssh legal-agent-vps "cd /opt/tm/tiger && ./run.sh hydrated-json /opt/tm/test-data/sync-test-cases/Eman_Youseef/ -o /opt/tm/outputs/"

# 2. Check defendants extraction
ssh legal-agent-vps "cat /opt/tm/outputs/hydrated_FCRA_*.json | jq '.defendants'"

# 3. Test via Dashboard UI
# Process Eman Youseef case through web interface
# Verify summons generation works

# 4. End-to-end workflow test
# Tiger → Dashboard → Monkey → Browser pipeline
```

## Risk Assessment & Mitigation

### Risk Level: LOW
**Rationale**: Additive enhancement with backward compatibility

### Potential Risks
1. **Regression**: Existing test cases fail
   - **Mitigation**: Comprehensive test suite execution
   
2. **Performance**: Additional pattern matching overhead
   - **Mitigation**: Efficient regex compilation, early exit patterns
   
3. **False Positives**: Incorrect defendant identification
   - **Mitigation**: Conservative patterns, normalization validation

### Rollback Plan
```bash
# If issues arise, quick rollback:
ssh legal-agent-vps "cd /opt/tm && git checkout HEAD~1 && sudo systemctl restart tm-dashboard"
```

## Success Metrics

### Before Enhancement (Current VPS State)
```json
{
  "defendants": [],
  "extraction_confidence": 45.2,
  "warnings": ["No defendants identified"]
}
```

### After Enhancement (Target State)
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
  ],
  "extraction_confidence": 78.5,
  "warnings": []
}
```

### Workflow Success Indicators
- ✅ **Tiger**: Defendants array populated (3+ entities)
- ✅ **Dashboard**: Review shows defendant information
- ✅ **Monkey**: Complaint generated with proper party names
- ✅ **Monkey**: Summons generated for each defendant
- ✅ **Browser**: PDF generation for all documents

## Timeline & Execution

### Phase 1: Development (Local) - 30 minutes
- Enhance defendant extraction methods
- Add multi-pattern recognition
- Test with Eman Youseef case
- Verify backward compatibility

### Phase 2: PR Creation - 10 minutes  
- Create feature branch
- Commit enhanced extraction logic
- Submit pull request with detailed description
- Request review (if applicable)

### Phase 3: VPS Deployment - 15 minutes
- SSH to VPS
- Git pull latest changes
- Restart affected services
- Validate enhancement working

### Phase 4: Testing & Validation - 20 minutes
- Process test cases through Dashboard UI
- Verify complete workflow (Tiger → Summons)
- Document success metrics
- Update deployment status

**Total Estimated Time**: 75 minutes

## Next Steps

1. **[HIGH]** Develop enhanced defendant extraction locally
2. **[HIGH]** Create PR with comprehensive testing
3. **[HIGH]** Deploy to VPS and validate
4. **[MEDIUM]** Proceed with SSL deployment once confirmed
5. **[LOW]** Document lessons learned for future deployments

---

**Plan Status**: Ready for execution  
**Dependencies**: None (local development can begin immediately)  
**Success Criteria**: Eman Youseef case produces 3+ defendants and enables summons generation