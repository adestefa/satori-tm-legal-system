# Tiger-Monkey Legal Document Processing System
## Comprehensive Project Documentation & Architecture Guide

## Executive Summary

Tiger-Monkey is a comprehensive legal document processing system designed for consumer protection attorneys, transforming raw case documents into court-ready legal filings. The system employs a microservices architecture with Tiger handling document extraction and Monkey generating pixel-perfect legal documents via HTML+PDF pipeline.

**Current Status**: Transitioning from monolithic text-based system to modern microservices architecture with HTML rendering engine for court-quality document generation.

---

## Architecture Overview

### 🏗️ **New Microservices Architecture (Target)**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tiger Service │    │  Monkey Service │    │  Chrome Service │
│   (Extraction)  │───▶│ (Generation)    │───▶│ (PDF Rendering) │
│                 │    │                 │    │                 │
│ • Document OCR  │    │ • HTML Templates│    │ • Headless      │
│ • Data Extract  │    │ • CSS Styling   │    │   Chrome        │
│ • Quality Score │    │ • Legal Filters │    │ • Print to PDF  │
│ • JSON Output   │    │ • Validation    │    │ • Pixel Perfect │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Hydrated JSON   │    │   HTML Content  │    │   Court-Ready   │
│ Schema v2.0     │    │   Legal Docs    │    │   PDF Files     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🏛️ **Legacy Monolithic System (Fallback)**

The current monolithic system serves as a fallback during transition:
- Single repository with tightly coupled Tiger and Beaver components
- Text-based template system (Jinja2 with limited formatting)
- Direct file output without sophisticated document management

---

## Core Services

### 🐅 Tiger Service ("The Legal Data Harvester")

**Status**: Production-ready with 100% success rate on test cases

**Purpose**: Extract and consolidate legal data from case documents into structured JSON

**Core Capabilities**:
- **Multi-Format Processing**: PDF (via Docling OCR), DOCX (native), TXT
- **Legal Entity Extraction**: Courts, parties, attorneys, case numbers, financial data
- **Case Consolidation**: Multi-document analysis with confidence scoring
- **Quality Assessment**: 0-100 scoring system for extraction confidence
- **Structured Output**: Hydrated JSON schema compatible with Monkey service

**Technical Architecture**:
```
Document Input → Format Detection → Engine Selection → Text Extraction → 
Legal Analysis → Quality Scoring → JSON Generation → Output Validation
```

**Processing Engines**:
- **Docling Engine**: ML-based OCR for PDFs, optimized for legal documents
- **DOCX Engine**: Native Word document processing with table support
- **Text Engine**: Plain text processing with legal pattern recognition

**Quality Scoring Algorithm**:
```
Total Score (0-100) = Text Length Score (0-30) + 
                      Compression Ratio Score (0-20) + 
                      Legal Indicators Score (0-50)
```

**Quality Thresholds**:
- **High Quality (≥80)**: Production ready, minimal review needed
- **Medium Quality (50-79)**: Good extraction, minor review recommended
- **Low Quality (<50)**: Requires manual review and validation

**Output Schema**: Hydrated JSON v2.0 with standardized legal document structure

### 🐒 Monkey Service ("The Court Document Builder")

**Status**: Under development - Transitioning to HTML+PDF architecture

**Purpose**: Generate court-ready legal documents from Tiger's JSON output using HTML+CSS templates rendered to PDF via headless Chrome

**Revolutionary HTML+PDF Pipeline**:
```
Tiger JSON → HTML Template Engine → CSS Styling → Chrome Rendering → PDF Output
```

**Core Architecture Components**:

#### 1. **HTML Template Engine** (`monkey/core/html_engine.py`)
- **Jinja2-based**: Advanced template system with legal document filters
- **Custom Filters**: Legal formatting (case numbers, addresses, dates, sequential numbering)
- **CSS Integration**: Tailwind CSS for utility-first styling approach
- **Template Inheritance**: Shared components for consistent legal document structure

#### 2. **Chrome PDF Service** (`monkey/core/pdf_service.py`)
- **Headless Chrome**: Leverages 20+ years of browser rendering optimization
- **Pixel-Perfect Output**: Superior PDF generation compared to custom libraries
- **Legal Document Options**: Precise margin control, typography, court-specific formatting
- **Batch Processing**: Efficient multi-document generation

#### 3. **Document Builder** (`monkey/core/document_builder_v2.py`)
- **Simplified Architecture**: Single HTML+PDF pipeline eliminates complexity
- **Async Operations**: High-performance document generation
- **Quality Integration**: Built-in validation and quality scoring
- **Format Support**: HTML, PDF, or both output formats

#### 4. **Quality Validation System** (`monkey/core/quality_validator.py`)
- **Court Compliance**: Validates federal court filing standards
- **Content Validation**: Ensures all required legal sections present
- **Visual Accuracy**: Ground truth comparison capabilities
- **Automated Scoring**: 0-100 quality assessment with court-readiness determination

**Document Types Supported**:
- **FCRA Complaints**: Complete federal court complaints with all required sections
- **Summons**: Court-formatted summons documents (planned)
- **Cover Sheets**: JS 44 Civil Cover Sheets (planned)

**Legal Document Features**:
- **Sequential Numbering**: Proper 1, 2, 3... paragraph numbering across sections
- **Court Formatting**: Precise margins, typography, decorative elements
- **Legal Citations**: Automatic formatting of statutory references
- **Multi-Defendant Support**: Proper handling of multiple defendants and entities

#### 5. **CLI Integration** (`monkey/cli/commands.py`)
- **Modern Interface**: Updated for HTML+PDF workflow
- **Async Support**: Proper async/sync integration
- **Preview Capabilities**: Real-time HTML and PDF preview
- **Validation Commands**: Quality assessment and compliance checking
- **Batch Operations**: Multi-document processing support

### 🌐 Chrome Service (PDF Rendering)

**Purpose**: Headless Chrome container for HTML to PDF conversion

**Container Configuration**:
- **Browserless Chrome**: Optimized for server-side rendering
- **Legal Fonts**: Times New Roman, court-standard typography
- **Print Optimization**: CSS @page support, exact margins
- **Resource Management**: Memory limits, connection pooling

**API Interface**:
- **Chrome DevTools Protocol**: WebSocket-based communication
- **PDF Options**: Court-specific formatting parameters
- **Health Monitoring**: Service availability and performance tracking

---

## Data Flow & Integration

### **Complete Workflow**
```
1. Case Documents (PDF/DOCX) 
        ↓
2. Tiger Service Processing
   • Format Detection
   • OCR/Text Extraction  
   • Legal Entity Extraction
   • Quality Analysis
        ↓
3. Hydrated JSON Schema v2.0
   • Standardized structure
   • Legal entity mapping
   • Confidence scores
        ↓
4. Monkey Service Generation
   • HTML Template Rendering
   • CSS Styling Application
   • Legal Format Validation
        ↓
5. Chrome PDF Service
   • HTML to PDF Conversion
   • Court-Quality Rendering
   • Precise Margin Control
        ↓
6. Court-Ready Legal Documents
```

### **Schema Interface** (Tiger ↔ Monkey Communication)

**Hydrated JSON Schema v2.0 Structure**:
```json
{
  "parties": {
    "plaintiff": {
      "name": "Eman Youssef",
      "address": {...},
      "consumer_status": "Individual consumer under FCRA"
    },
    "defendants": [
      {
        "name": "EQUIFAX INFORMATION SERVICES LLC",
        "type": "Consumer Reporting Agency",
        "address": {...}
      }
    ]
  },
  "case_information": {
    "court_district": "Eastern District of New York",
    "case_number": "1:25-cv-01987",
    "jury_demand": true
  },
  "factual_background": {
    "summary": [...],
    "events": [...],
    "preliminary_statement": [...]
  },
  "causes_of_action": [
    {
      "title": "VIOLATION OF THE FCRA",
      "against_defendants": ["Equifax Information Services LLC"],
      "allegations": [...]
    }
  ],
  "damages": {
    "summary": "...",
    "denials": [...]
  },
  "metadata": {
    "tiger_version": "1.0",
    "processing_timestamp": "2025-01-03T12:34:56",
    "quality_score": 87.5
  }
}
```

---

## Implementation Plan & Current Status

### **Phase 1: System Stability** (CRITICAL - In Progress)
**Addressing implementation fraud and missing components**

**Current Issues**:
- **DEFECT_MONKEY_10-14**: Complete output management system missing (implementation fraud)
- **RL Score**: -225 (below safety threshold)
- **System Integrity**: Requires immediate attention

**Resolution Priority**:
1. **DEFECT_MONKEY_10**: Implement missing output management modules
2. **DEFECT_MONKEY_11**: Establish verification framework
3. **DEFECT_MONKEY_12-14**: Complete core module implementation

### **Phase 2: HTML Engine Foundation** (Planned)
**Building new HTML+PDF architecture**

**Components**:
1. **TASK_HTML_1**: Core HTML Template Engine
2. **TASK_HTML_2**: FCRA Complaint HTML Template
3. **TASK_HTML_3**: Headless Chrome Integration

### **Phase 3: Service Integration** (Planned)
**Completing the HTML+PDF pipeline**

**Components**:
1. **TASK_HTML_4**: Document Builder Refactor
2. **TASK_HTML_5**: CLI Integration & Testing
3. **TASK_HTML_6**: Quality Validation System

### **Phase 4: Microservices Extraction** (Future)
**Transition to independent services**

**Execution Plan**: Based on `/Users/corelogic/satori-dev/tiger-beaver/stand_alone_services_plan.md`

---

## Command Line Interface

### **Tiger Service Commands**
```bash
# Single document processing
./satori-tiger process document.pdf

# Batch processing with quality filtering
./satori-tiger batch ./case_files/ --min-quality 70

# Case consolidation (multi-document analysis)
./satori-tiger case-extract case_folder/ --complaint-json

# Quality validation only
./satori-tiger validate document.pdf

# System health and performance
./satori-tiger info --engines
```

### **Monkey Service Commands** (HTML+PDF Pipeline)
```bash
# Generate court-ready documents
./satori-monkey generate tiger_output.json --format pdf

# Document package generation
./satori-monkey package tiger_output.json --documents complaint,summons --format both

# HTML preview for development
./satori-monkey preview tiger_output.json --auto-open

# Quality validation and compliance checking
./satori-monkey validate tiger_output.json

# System health monitoring
./satori-monkey health --chrome-endpoint http://localhost:9222

# Service information and capabilities
./satori-monkey info
```

### **Legacy Beaver Commands** (Fallback)
```bash
# Legacy text-based generation (fallback only)
./satori-beaver build-complaint fcra-simple_complaint.json --output ./case_documents/
./satori-beaver validate fcra-simple_complaint.json
./satori-beaver preview fcra-simple_complaint.json --format txt
```

---

## Project Structure & File Organization


### **Target Microservices Structure** 
```
parent_directory/
├── tiger/                                      # Independent Tiger Service
│   ├── app/                                   # Core tiger application
│   ├── outputs/production/                    # Production outputs (7-year retention)
│   ├── outputs/testing/                       # Test outputs (30-day retention)
│   ├── schemas/hydrated_json_schema.py        # Schema interface
│   └── satori-tiger                           # CLI entry point
├── monkey/                                     # Independent Monkey Service
│   ├── core/                                  # Document generation core
│   ├── templates/html/                        # HTML+CSS templates
│   ├── outputs/production/                    # Production documents
│   ├── schemas/hydrated_json_schema.py        # Schema interface
│   └── satori-monkey                          # CLI entry point
├── chrome-service/                            # Headless Chrome container
│   ├── Dockerfile                             # Chrome container config
│   └── docker-compose.yml                     # Service orchestration
└── shared-schemas/                            # Optional: Centralized schema package
    └── hydrated_json_schema.py                # Master schema definition
```

---

## Testing Strategy & Quality Assurance

### **Testing Framework**
- **Unit Tests**: Individual component testing with pytest
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Speed benchmarks and memory usage
- **Real-World Tests**: Actual legal document processing
- **Visual Regression**: HTML+PDF output comparison against ground truth

### **Quality Assurance System**
- **Reinforcement Learning QA**: Automated scoring and defect tracking (`yinsen/rl/`)
- **Document Quality Validation**: Court compliance checking
- **Ground Truth Comparison**: Pixel-perfect accuracy validation
- **Legal Standards Compliance**: Federal court filing requirements

### **Test Data Categories**
1. **Perfect Cases**: Clean, complete document sets with all required information
2. **Missing Data Cases**: Incomplete information requiring smart defaults
3. **Conflicting Data Cases**: Inconsistent information across documents
4. **Poor Quality Cases**: Low-quality scanned documents with OCR challenges
5. **Edge Cases**: Unusual formats, complex structures, multiple defendants

### **Performance Benchmarks**
- **Tiger Processing**: 7-17 seconds for court documents (96-97/100 quality)
- **Monkey Generation**: <2 seconds for HTML, <5 seconds for PDF
- **End-to-End**: <30 seconds from case folder to court-ready documents
- **Quality Standards**: >90% field extraction accuracy, >95% completeness

---

## Dependencies & Technical Requirements

### **Core Dependencies**
```python
# Tiger Service (Heavy ML/OCR Stack)
docling>=1.0.0              # Advanced OCR with ML models (500MB+)
python-docx>=0.8.11         # Word document processing
pdfplumber>=0.10.0          # Advanced PDF extraction
pandas>=2.1.0               # Data analysis and processing
fastapi>=0.104.0            # API framework for future microservice
pydantic>=2.5.0             # Data validation and schema management

# Monkey Service (Lightweight Generation)
jinja2>=3.1.2               # Template engine (both HTML and legacy text)
aiohttp>=3.8.0              # Async HTTP for Chrome communication
pydantic>=2.5.0             # Data validation

# Chrome Service
browserless/chrome:latest   # Headless Chrome container
```

### **System Requirements**
- **Python**: 3.8+ for all services
- **Docker**: For Chrome service container
- **Memory**: 2GB+ for Tiger OCR processing, 1GB+ for Chrome service
- **Network**: HTTP access to Chrome service endpoint
- **Storage**: Legal document retention policies (production: 7 years)

---

## Success Metrics & Validation

### **Tiger Service Success Criteria**
- **Accuracy**: >90% field extraction accuracy across all document types
- **Completeness**: >95% required field population in generated JSON
- **Performance**: Process complete case folder in <30 seconds
- **Robustness**: Handle 100% of document quality variations without failure
- **Quality**: Consistent quality scoring and confidence metrics

### **Monkey Service Success Criteria**
- **Court Compliance**: 100% federal court filing standard compliance
- **Visual Accuracy**: Pixel-perfect rendering matching ground truth documents
- **Performance**: <2 minutes from JSON input to court-ready document
- **Format Quality**: Professional legal document appearance and typography
- **Reliability**: 99.9% successful generation rate without manual intervention

### **End-to-End Success Criteria**
- **Lawyer Efficiency**: Reduce case preparation time by 80%
- **Error Reduction**: <1% manual corrections needed for court filing
- **Quality Consistency**: Documents ready for immediate court submission
- **Scalability**: Handle high-volume document processing for law firm operations
- **Reliability**: 99.9% uptime and successful processing across all components

---

## Data Locations & File Paths

### **Test Data**
- **Real-world case data**: `/Users/corelogic/satori-dev/tiger-beaver/test-data/sample_case_files`
- **Ground truth documents**: `/Users/corelogic/satori-dev/tiger-beaver/test-data/sample_case_files/final_output_ground_truth/`
- **Synthetic test cases**: `/Users/corelogic/satori-dev/tiger-beaver/test-data/synthetic-cases`
- **Test JSON files**: `/Users/corelogic/satori-dev/tiger-beaver/test-data/test_json`

### **Configuration & Templates**
- **HTML templates**: `/Users/corelogic/satori-dev/tiger-beaver/monkey/templates/html/`
- **CSS styling**: `/Users/corelogic/satori-dev/tiger-beaver/monkey/templates/html/shared/legal_styles.css`
- **Legacy templates**: `/Users/corelogic/satori-dev/tiger-beaver/monkey/templates/fcra/`

### **Task Management**
- **Yinsen workflow**: `/Users/corelogic/satori-dev/tiger-beaver/yinsen/`
- **Implementation plan**: `/Users/corelogic/satori-dev/tiger-beaver/yinsen/1_queue/monkey_plan.md`
- **QA system**: `/Users/corelogic/satori-dev/tiger-beaver/yinsen/rl/`

### **Documentation**
- **Project specifications**: `/Users/corelogic/satori-dev/tiger-beaver/prd/`
- **Service extraction plan**: `/Users/corelogic/satori-dev/tiger-beaver/stand_alone_services_plan.md`
- **Architecture documentation**: This file (`/Users/corelogic/satori-dev/tiger-beaver/prd/prd.md`)

---

## Development Commands & Workflow

### **Environment Setup**
```bash
source venv/bin/activate                    # Activate Python environment
./install.sh                               # Install all dependencies
./run_health_check.sh                      # Verify system health (8 core tests)
```

### **Testing Commands**
```bash
./test.sh                                  # Quick 3-test health check
./run_health_check.sh                     # Comprehensive 8-test validation
python3 -m unittest tests.test_legal_extraction  # Specific test module
python3 tests/run_all_tests.py            # Full test suite (if exists)
pytest monkey/tests/                       # New HTML pipeline tests
```

### **Development Workflow**
```bash
# Tiger development and testing
./satori-tiger process test-data/sample_case_files/Atty_Notes.docx
./satori-tiger case-extract test-data/cases/youssef/ --complaint-json

# Monkey development and testing
./satori-monkey preview test-data/test-json/hydrated-test-0.json --auto-open
./satori-monkey generate test-data/test-json/hydrated-test-0.json --format both

# Chrome service health check
curl -f http://localhost:9222/json/version || echo "Chrome service unavailable"
```

---

## Known Issues & Risk Assessment

### **Current Critical Issues**
1. **Implementation Fraud**: DEFECT_MONKEY_10-14 representing complete system fabrication
2. **RL Score**: -225 (below human safety threshold of -1000)
3. **System Instability**: Multiple missing core components affecting reliability

### **Legacy System Issues**
1. **Text Template Limitations**: Cannot achieve court-quality formatting
2. **Broken Output Management**: Missing file organization and metadata systems
3. **Schema Mismatches**: Template-data structure incompatibilities
4. **Performance Issues**: Inefficient document generation pipeline

### **Risk Mitigation**
- **Mandatory Verification**: All implementations must be verified before documentation
- **Quality Gates**: RL score monitoring at each development phase
- **Fallback System**: Legacy monolith remains available during transition
- **Comprehensive Testing**: Ground truth validation and court compliance checking

---

## Strategic Vision & Future Roadmap

### **Short-term Goals** (Next 3 months)
1. **System Stability**: Resolve implementation fraud and restore RL score
2. **HTML Pipeline**: Complete HTML+PDF document generation system
3. **Quality Validation**: Ensure court filing compliance and visual accuracy
4. **Performance Optimization**: Meet sub-30-second end-to-end processing

### **Medium-term Goals** (3-6 months)
1. **Microservices Extraction**: Independent Tiger and Monkey services
2. **Container Deployment**: Docker-based service orchestration
3. **Advanced Features**: Multi-document packages, batch processing
4. **API Development**: RESTful interfaces for service integration

### **Long-term Vision** (6+ months)
1. **Practice Area Expansion**: Support for FDCPA, state law practices
2. **Advanced AI Integration**: ML-enhanced document generation
3. **Cloud Deployment**: Scalable cloud-native architecture
4. **Partner Integration**: Third-party legal software ecosystem

---

## Business Context & Legal Practice Impact

### **Target Users**
- **Consumer Protection Attorneys**: FCRA, FDCPA specialists in NY/NJ
- **Law Firms**: Small to medium practices handling high-volume consumer cases
- **Legal Support Staff**: Paralegals and legal assistants preparing court filings

### **Business Value**
- **Efficiency**: 80% reduction in document preparation time
- **Quality**: Consistent, court-ready documents without manual formatting
- **Compliance**: Automated federal court filing standard compliance
- **Scalability**: Handle increased case volume without proportional staff increase

### **Legal Compliance**
- **Federal Court Standards**: Precise margin, typography, and formatting requirements
- **FCRA Specialization**: Consumer protection law statutory citation accuracy
- **Document Integrity**: Audit trails and version control for legal accountability
- **Professional Standards**: Attorney signature blocks and proper legal language

This comprehensive system transforms consumer protection legal practice by automating the complex, time-intensive process of creating court-ready legal documents while maintaining the highest standards of legal accuracy and professional presentation.

---

**Document Version**: 2.0  
**Last Updated**: January 3, 2025  
**Architecture**: Microservices with HTML+PDF Pipeline  
**Status**: Active Development (Phase 1: System Stability)  
**Next Milestone**: Complete implementation fraud resolution and HTML engine foundation


## Logical Priority Justification

Excellent insight. You are absolutely correct - DEFECT_MONKEY_6 is a CATEGORY 1 SYSTEM BLOCKER that must
   be resolved immediately.

  LOGICAL PRIORITY JUSTIFICATION:

  Phase 0 (CRITICAL BLOCKER):

  DEFECT_MONKEY_6 - Schema validation mismatch
  - Blocks: ALL Tiger→Monkey workflows
  - Impact: CLI completely unusable, validation impossible
  - Solution: 3.25-hour schema compatibility layer
  - Dependencies: NONE (can be implemented immediately)

  Why This Must Be First:

  Without Schema Validation:
  Tiger JSON → ❌ Validation Failure → ❌ No Document Generation → ❌ Nothing Works

  With Schema Validation:
  Tiger JSON → ✅ Validation Success → ✅ Document Generation → ✅ System Functional

  Updated Plan Summary:

  1. Phase 0: Fix schema validation (3.25 hours) - UNBLOCKS EVERYTHING
  2. Phase 1: Address implementation fraud (34-51 hours)
  3. Phase 2: Build HTML engine (10-13 hours)
  4. Phase 3: Integrate HTML pipeline (6-9 hours)
  5. Phase 4: Add production output management (12-16 hours)

  LOGICAL EFFICIENCY CALCULATION:

  Before Fix: 0% system functionality (everything blocked)
  After 3.25 hours: 100% basic functionality restored
  ROI: Maximum possible return on minimal investment

  The updated monkey_plan.md now correctly prioritizes the schema validation fix as Phase 0 - Critical 
  System Blocker, followed by Task Monkey 6 (output management) as the final Phase 4 component.

  read the plan here: /Users/corelogic/satori-dev/tiger-beaver/yinsen/1_queue/monkey_plan.md