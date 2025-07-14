# North Star Attorney Notes Schema

**Date:** 2025-01-09  
**Version:** 1.0  
**Status:** Production Standard

## Overview

This document defines the universal labeling system for attorney notes across all FCRA cases. It eliminates redundancy, ensures consistency, and provides complete information for automated complaint generation.

## Core Philosophy

1. **Single Source of Truth**: Firm information comes from `dashboard/config/settings.json`
2. **Structured Consistency**: All cases use identical labeling structure
3. **Legal Completeness**: All necessary elements for complaint generation included
4. **Scalable Design**: Easy to add new cases with proper structure

## Universal Label Schema

### **Section 1: Client Information (REQUIRED)**

```
NAME: [Full legal name of plaintiff]
ADDRESS: 
[Street address]
[City, State ZIP]
PHONE: [Contact phone number]
RESIDENCY: [Legal residency for jurisdiction - e.g., "State of New York, borough of Manhattan"]
```

**Purpose**: Establishes plaintiff identity and jurisdiction basis

### **Section 2: Case Information (REQUIRED)**

```
CASE_NUMBER: [Court case number - e.g., "1:25-cv-01987"]
COURT_NAME: [Full court name - e.g., "UNITED STATES DISTRICT COURT"]
COURT_DISTRICT: [Court district - e.g., "EASTERN DISTRICT OF NEW YORK"]
FILING_DATE: [Filing date - e.g., "April 9, 2025"]
```

**Purpose**: Establishes court jurisdiction and case identification

### **Section 3: Attorney Information (REMOVED)**

**Note**: ALL attorney information (name, firm, address, phone, email) comes from `dashboard/config/settings.json`. Attorney notes should NOT include any attorney information as this is set once in the config page by the lawyer.

**Purpose**: Eliminates redundancy - attorney configures firm information once in settings

### **Section 3: Defendants (REQUIRED)**

```
DEFENDANTS:
- [DEFENDANT 1 FULL NAME] ([State] corporation, authorized to do business in [State])
- [DEFENDANT 2 FULL NAME] ([State] corporation, authorized to do business in [State])
- [Continue for all defendants...]
```

**Purpose**: Establishes all parties and their business status for service

### **Section 4: Background (REQUIRED)**

```
BACKGROUND:
1. [First factual allegation]
2. [Second factual allegation]
3. [Continue numbering sequentially...]
```

**Purpose**: Provides numbered factual allegations for complaint body

### **Section 5: Key Dates (REQUIRED)**

```
KEY_DATES:
- [Event Type]: [Date - e.g., "Account Opening: July 2023"]
- [Event Type]: [Date - e.g., "Dispute Date: December 9, 2024"]
- [Continue for all significant dates...]
```

**Purpose**: Establishes timeline for chronological validation

### **Section 6: Damages (REQUIRED)**

```
DAMAGES:
Financial Harm:
- [Specific financial damage]
- [Additional financial damages...]

Reputational Harm:
- [Specific reputational damage]
- [Additional reputational damages...]

Emotional Harm:
- [Specific emotional damage]
- [Additional emotional damages...]

Personal Costs:
- [Specific personal costs]
- [Additional personal costs...]
```

**Purpose**: Structured damages for prayer for relief

### **Section 7: Legal Claims (COMPLEX CASES)**

```
LEGAL_CLAIMS:
Count [#] - [Claim Type]:
- [Citation]: [Description] ([Defendants affected])
- [Citation]: [Description] ([Defendants affected])
- [Continue for all claims...]
```

**Purpose**: Detailed legal citations for complex cases

### **Section 8: Relief Sought (COMPLEX CASES)**

```
RELIEF_SOUGHT:
- [Type of relief requested]
- [Additional relief...]
- [Jury trial demanded: Yes/No]
```

**Purpose**: Prayer for relief elements

## Label Rules and Standards

### **Formatting Requirements**

1. **Label Format**: All labels must be in ALL CAPS followed by colon
2. **Consistent Spacing**: Single blank line between sections
3. **Numbering**: Use sequential numbering for BACKGROUND allegations
4. **Dates**: Use consistent date format (Month Day, Year)
5. **Legal Citations**: Use standard legal citation format

### **Content Standards**

1. **Completeness**: All REQUIRED sections must be present
2. **Accuracy**: All information must be legally accurate
3. **Consistency**: Use identical phrasing for similar elements across cases
4. **Specificity**: Provide specific details, not general statements

### **Validation Checklist**

- [ ] All REQUIRED sections present
- [ ] NAME matches legal documents
- [ ] ADDRESS is complete with state and ZIP
- [ ] CASE_NUMBER follows court format
- [ ] FILING_DATE is accurate
- [ ] DEFENDANTS include business incorporation details
- [ ] BACKGROUND has numbered allegations
- [ ] KEY_DATES include all significant events
- [ ] DAMAGES are categorized properly
- [ ] No firm information redundancy (leverages settings.json)

## Integration with Tiger Service

### **Expected Extraction Points**

The Tiger service will extract:
- **Client data** from Section 1
- **Case metadata** from Section 2
- **Defendant information** from Section 3
- **Factual allegations** from Section 4
- **Timeline events** from Section 5
- **Damage categories** from Section 6
- **Legal claims** from Section 7 (if present)
- **Relief elements** from Section 8 (if present)

### **Firm Information Merger**

Tiger service will automatically merge:
- Attorney name from settings.json
- Firm name from settings.json
- Firm address from settings.json
- Firm phone from settings.json
- Firm email from settings.json

## Migration Strategy

### **Phase 1: Schema Implementation**
1. Create master template based on this schema
2. Update existing cases to match new structure
3. Remove redundant firm information

### **Phase 2: Tiger Service Updates**
1. Update case consolidator for new labels
2. Implement firm information merger
3. Test extraction accuracy

### **Phase 3: Validation and Testing**
1. Validate all cases generate complete complaints
2. Test chronological validation with KEY_DATES
3. Ensure no missing information

## Benefits

1. **Consistency**: Identical structure across all cases
2. **Efficiency**: No redundant data entry
3. **Completeness**: All legal elements captured
4. **Maintainability**: Single source for firm information
5. **Scalability**: Easy to add new cases
6. **Quality**: Standardized legal formatting

## Version History

- **v1.0** (2025-01-09): Initial North Star schema definition
- **Future**: Will be updated based on testing and real-world usage