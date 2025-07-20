# Damages Display Documentation
**Tiger-Monkey Legal Document Processing System**  
**Date**: July 19, 2025  
**Component**: Dashboard Damages Review Interface  
**Version**: v1.9.0

## Overview

The Tiger-Monkey Dashboard implements an intelligent damages display system that adapts its interface based on data source confidence and extraction method. The system automatically determines whether to display damages as static information (high-confidence document extractions) or interactive checkboxes (manual attorney input requiring validation).

## Display Modes

### 1. Static Information Display (Document-Extracted)
**Appearance**: Non-interactive cards showing extracted damage information  
**Use Case**: High-confidence extractions from actual legal documents

### 2. Interactive Checkbox Display (Attorney Input)
**Appearance**: Selectable damage categories with checkboxes  
**Use Case**: Manual attorney input requiring validation and selection

## Determining Factors

The Dashboard rendering logic evaluates the following JSON structure elements to determine display mode:

### Primary Decision Logic
```javascript
// From damages-review.js lines 87-97
const structuredDamages = this.damages.structured_damages || [];
const categorizedDamages = this.damages.categorized_damages || {};

if (structuredDamages.length === 0) {
    // Render static document-extracted damages
    renderDocumentExtractedDamages();
} else {
    // Render interactive checkbox interface
    renderInteractiveDamages();
}
```

## JSON Structure Analysis

### Static Display Triggers

**Required JSON Structure:**
```json
{
  "damages": {
    "structured_damages": [],  // EMPTY ARRAY - Key indicator
    "actual_damages": {
      "description": "Plaintiff has suffered actual damages...",
      "categories": [...],
      "specific_denials": [     // POPULATED - Document extractions
        {
          "source_document": "adverse_action_letter_cap_one.pdf",
          "creditor": "Capital One",
          "date": "February 24, 2025",
          "credit_score": "577",
          "reasons": [...]
        }
      ]
    },
    "statutory_damages": {...},
    "punitive_damages": {...}
  }
}
```

**Key Indicators:**
- `structured_damages: []` - Empty array
- `specific_denials: [...]` - Populated with document extractions
- Source attribution for each denial
- High extraction confidence scores

### Interactive Display Triggers

**Required JSON Structure:**
```json
{
  "damages": {
    "structured_damages": [    // POPULATED ARRAY - Key indicator
      {
        "category": "actual",
        "type": "credit_denial",
        "selected": false,
        "confidence": 0.65,
        "evidence_available": false
      }
    ],
    "categorized_damages": {   // POPULATED - Manual categorization
      "actual": [...],
      "statutory": [...],
      "punitive": [...]
    }
  }
}
```

**Key Indicators:**
- `structured_damages: [...]` - Populated array
- `categorized_damages: {...}` - Manual damage categorization
- Lower confidence scores requiring validation
- `selected: false` flags indicating user input needed

## Data Source Confidence Levels

### High Confidence (Static Display)
**Source**: Direct document extraction from legal filings
- **Adverse Action Letters**: PDF extractions with creditor, date, credit score
- **Denial Letters**: DOCX extractions with specific reasons
- **Court Documents**: Formal legal document extractions

**Characteristics:**
- 100% confidence in extracted content
- Verifiable source attribution
- Specific denial details with dates and scores
- No user validation required

### Medium/Low Confidence (Interactive Display)
**Source**: Attorney notes interpretation and damage inference
- **Narrative Text**: Unstructured attorney notes
- **Inferred Damages**: System-suggested damage categories
- **Manual Input**: Attorney-provided damage lists

**Characteristics:**
- Requires attorney validation
- Confidence scores 50-85%
- User selection needed for legal strategy
- Manual review and approval workflow

## Rendering Implementation

### Static Display Rendering
**File**: `dashboard/static/js/damages-review.js` lines 273-320

```javascript
// Special handling for specific denials array
if (key === 'specific_denials' && Array.isArray(value)) {
    html += `<div><strong>${label}:</strong></div>`;
    html += `<div class="ml-4 space-y-3 mt-2">`;
    value.forEach((denial, index) => {
        html += `
            <div class="border-l-4 border-red-300 pl-4 py-2 bg-red-50">
                <div class="text-sm">
                    <strong>Denial ${index + 1}:</strong> ${denial.creditor}
                    ${denial.date ? ` (${denial.date})` : ''}
                    ${denial.credit_score ? ` - Credit Score: ${denial.credit_score}` : ''}
                </div>
                <div class="text-xs text-gray-600 mt-1">
                    <strong>Reasons:</strong> ${denial.reasons.join('; ')}
                </div>
                <div class="text-xs text-gray-500 mt-1">
                    Source: ${denial.source_document}
                </div>
            </div>`;
    });
}
```

### Interactive Display Rendering
**File**: `dashboard/static/js/damages-review.js` lines 126-200

```javascript
// Render interactive checkboxes for each damage category
renderDamageItem(damage, categoryKey, index) {
    return `
        <div class="damage-item border rounded-lg p-4 ${damage.selected ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'}">
            <div class="flex items-start space-x-3">
                <input type="checkbox" 
                       id="damage-${categoryKey}-${index}" 
                       ${damage.selected ? 'checked' : ''}
                       onchange="window.damageReview.updateDamageSelection('${categoryKey}', ${index}, this.checked)"
                       class="mt-1 h-4 w-4 text-blue-600">
                <label for="damage-${categoryKey}-${index}" class="flex-1">
                    <div class="font-medium text-gray-900">${damage.type || damage.description}</div>
                </label>
            </div>
        </div>`;
}
```

## Attorney Notes Impact

### Static Display Format (Current Implementation)
**Attorney Notes Structure:**
```
Eman Youssef
347.891.5584
Client lives in Queens
TD Bank Credit Card
$7,500 in fraudulent charges in one week
Disputed to TD Bank, claim was denied
```

**Result**: Static display because:
- No formal "DAMAGES:" section
- System extracts from actual denial documents
- High confidence in document-based evidence

### Interactive Display Format (Alternative)
**Attorney Notes Structure:**
```
DEFENDANTS:
- TD Bank, N.A.
- Capital One, N.A.
- Barclays Bank Delaware

DAMAGES:
- Actual damages for credit denial
- Statutory damages under FCRA  
- Punitive damages for willful violations
- Attorney fees and costs
```

**Result**: Interactive display because:
- Formal "DAMAGES:" section present
- Manual attorney categorization
- Requires validation and selection

## Case Study: Eman Youseef

### Current State Analysis
**Data Source**: Mixed document extraction + attorney notes

**JSON Evidence:**
```json
"structured_damages": [],  // Empty - triggers static display
"specific_denials": [
  {
    "source_document": "adverse_action_letter_cap_one.pdf",
    "creditor": "Capital One",
    "date": "February 24, 2025", 
    "credit_score": "577",
    "reasons": ["too many missed minimum payments..."]
  },
  {
    "source_document": "barclays_applicaiton_denial_2.docx",
    "creditor": "Barclays Bank",
    "credit_score": "608",
    "reasons": ["Recent delinquency indicated on credit bureau"]
  }
]
```

**Display Result**: Static informational cards showing:
- 3 specific denials with full details
- Source document attribution
- Credit scores and exact reasons
- Non-interactive presentation

**Confidence Level**: 100% - based on actual document extractions

## System Benefits

### Static Display Advantages
1. **High Confidence**: Based on actual document evidence
2. **Source Attribution**: Clear traceability to original documents
3. **Detailed Information**: Specific dates, scores, and reasons
4. **No User Error**: Cannot accidentally deselect valid evidence
5. **Legal Accuracy**: Preserves exact denial language

### Interactive Display Advantages
1. **Flexibility**: Attorney can select applicable damages
2. **Strategy Control**: Legal team decides damage approach
3. **Case Customization**: Adapt to specific case circumstances
4. **Review Process**: Built-in validation and approval workflow
5. **Manual Override**: Attorney judgment over system suggestions

## Development Guidelines

### When to Expect Static Display
- Document extraction pipelines (Tiger v1.9.0+)
- High-confidence OCR results
- Formal legal document processing
- Denial letters, adverse actions, court filings

### When to Expect Interactive Display
- Attorney note-based workflows
- Manual damage specification
- Strategic legal planning phases
- Low-confidence extractions requiring validation

### Testing Scenarios

**Static Display Test:**
1. Process case with actual denial documents
2. Verify `structured_damages: []`
3. Confirm `specific_denials` populated
4. Check static rendering with source attribution

**Interactive Display Test:**
1. Create attorney notes with formal DAMAGES section
2. Verify `structured_damages` populated
3. Confirm checkbox rendering
4. Test selection state management

## Code Locations

### Primary Rendering Logic
- **File**: `dashboard/static/js/damages-review.js`
- **Lines**: 87-97 (decision logic), 273-320 (static rendering)

### Data Processing
- **File**: `tiger/app/core/processors/case_consolidator.py`
- **Method**: `_extract_damages_from_documents()`

### Template Integration
- **File**: `dashboard/static/js/review-data.js`
- **Function**: `renderDamagesSection()`

## Future Enhancements

### Hybrid Display Mode
**Concept**: Combine static document evidence with interactive attorney additions
- Show document-extracted damages as static
- Allow attorney to add additional damage categories
- Maintain source attribution for all claims

### Confidence Scoring Display
**Concept**: Visual confidence indicators
- Color-coding for confidence levels
- Hover tooltips with extraction details
- Override capabilities for attorney review

### Smart Suggestions
**Concept**: AI-suggested damages based on case facts
- Analyze case patterns for damage recommendations
- Suggest applicable statutory damage amounts
- Provide legal precedent context

---

**Documentation Status**: Complete  
**Last Updated**: July 19, 2025  
**Author**: Claude (Dr. Spock) - TM System Analysis  
**Review Required**: Legal team validation for accuracy