# FCRA Simple Test Case

**Purpose**: Test basic FCRA case processing with clean, complete documents

## Case Profile
- **Plaintiff**: Sarah Johnson
- **Practice Area**: FCRA Credit Reporting Violations
- **Complexity**: Simple
- **Defendants**: 1 Bank + 3 Credit Agencies
- **Timeline**: 6 months of disputes

## Expected Documents
1. `Civil_Cover_Sheet.pdf` - Basic court filing information
2. `Summons_First_National_Bank.pdf` - Bank defendant summons
3. `Summons_Equifax.pdf` - Credit agency summons  
4. `Summons_Experian.pdf` - Credit agency summons
5. `Summons_TransUnion.pdf` - Credit agency summons
6. `Attorney_Notes.docx` - Case timeline and facts
7. `Credit_Denial_Letter.pdf` - Evidence of harm

## Test Objectives
- ✅ Perfect document quality (no OCR errors)
- ✅ Complete information extraction
- ✅ All required fields populated
- ✅ Consistent data across documents
- ✅ High confidence scores (>90%)

This case serves as the baseline for Tiger engine performance validation.