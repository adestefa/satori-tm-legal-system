# Tiger-Monkey Legal Document Processing System

This file provides comprehensive guidance to Claude Code when working with the complete Tiger-Monkey (TM) system.

## System Overview

**Tiger-Monkey (TM)** is a production-ready, enterprise-grade legal document processing platform designed specifically for FCRA (Fair Credit Reporting Act) cases. The system transforms raw legal documents into court-ready legal filings through a sophisticated four-service architecture with ML-powered document analysis, professional web interface, template-driven document generation, and headless browser PDF rendering.

**Current Status**: ✅ Production Ready v1.9.2 - Enterprise-grade system with unified case file structure and direct PDF serving

## Four-Service Architecture

### 1. Tiger Service - Advanced Document Analysis Engine
**Location**: `tiger/`  
**Purpose**: ML-powered extraction of structured data from legal documents  
**Technology**: Docling ML models, specialized legal extractors, quality scoring

**Key Capabilities**:
- **Advanced OCR**: Docling ML models for complex PDF document processing with confidence scoring
- **Multi-Format Support**: PDF (OCR), DOCX (native), TXT (structured parsing)
- **Legal Entity Extraction**: Courts, parties, case numbers, attorneys, damages, timelines with confidence metrics
- **Case Consolidation**: Multi-document aggregation into single structured case with intelligent merging
- **Quality Assessment**: 0-100 scoring system with production thresholds (>75 for production, 50-75 for review)
- **Timeline Validation**: Chronological error detection across documents with visual reporting
- **Real-time Events**: WebSocket broadcasting to Dashboard for live file-by-file processing updates
- **Performance Benchmarks**: Processing time tracking, memory usage optimization, parallel processing support

**Advanced Features**:
- **Schema Export**: Full JSON schema export for external system integration
- **Benchmark Mode**: Performance testing with detailed metrics and timing analysis
- **Quality Validation**: Document completeness assessment with detailed scoring breakdown
- **Entity Confidence Scoring**: ML confidence levels for all extracted legal entities
- **Production Thresholds**: Configurable quality gates for automated vs. manual review workflows

**CLI Commands**:
```bash
# Process single document
./run.sh process document.pdf -o output/

# Generate case hydrated JSON (primary workflow)
./run.sh hydrated-json case_folder/ -o output/

# Validate document quality with detailed scoring
./run.sh validate document.pdf

# Performance benchmarking with metrics
./run.sh benchmark case_folder/ --iterations 5

# Export JSON schema for integration
./run.sh export-schema -o schema.json

# Quality assessment check
./run.sh quality-check case_folder/ --threshold 75

# Health check with system diagnostics
./health_check.sh

# Service information and version
./run.sh info
```

### 2. Monkey Service - Document Generation Engine
**Location**: `monkey/`  
**Purpose**: Template-driven generation of court-ready legal documents  
**Technology**: Jinja2 template engine, schema validation, multi-format output

**Key Capabilities**:
- **Advanced Template System**: Schema-driven Jinja2 template selection with inheritance and includes
- **Document Types**: Complaints, summons, case reviews, cover sheets, motions, discovery documents
- **Multi-Format Output**: HTML (primary), PDF (court-ready), preview modes, clean URLs for printing
- **Schema Validation**: Comprehensive input validation against shared Pydantic schema with detailed error reporting
- **Quality Assurance**: Document completeness checking, legal format compliance, template validation
- **Attorney Integration**: Professional signature blocks with firm information and bar admission details
- **Template Management**: Dynamic template loading, validation, and version control

**Advanced Features**:
- **Clean URL System**: Optimized URLs for PDF generation and court filing (/complaint/case_id)
- **Template Inheritance**: Base templates with specialized extensions for different document types
- **Output Management**: Versioned document output with metadata tracking and storage organization
- **Preview System**: Real-time template preview with syntax validation and error highlighting
- **Performance Optimization**: Template caching, optimized rendering pipeline, memory management

**CLI Commands**:
```bash
# Generate complaint document with all templates
./run.sh build-complaint complaint.json --all

# Generate specific template type
./run.sh build-complaint complaint.json --template complaint_ny_fcra.html

# Generate summons for all defendants
./run.sh generate-summons complaint.json -o output/

# Generate case review with interactive claims
./run.sh review complaint.json -o review.html

# Validate input data against schema
./run.sh validate complaint.json

# Preview generation with line limits
./run.sh preview complaint.json --lines 50

# List available templates
./run.sh list-templates

# Validate template syntax and schema
./run.sh validate-template template.html

# Preview template with sample data
./run.sh preview-template template.html --sample

# Service information and diagnostics
./run.sh info

# Health check with template validation
./health_check.sh
```

### 3. Dashboard Service - Professional Web Interface
**Location**: `dashboard/`  
**Purpose**: Web-based case management and workflow orchestration  
**Technology**: FastAPI with WebSocket, multi-theme interface, real-time monitoring

**Key Capabilities**:
- **Real-time Case Management**: WebSocket-based live updates with dual file monitoring (source + output)
- **Professional Multi-Theme Interface**: Light, dark, and lexigen themes with responsive design
- **Enterprise Authentication**: Session-based security with HTTP cookies and 8-hour timeout
- **Template Management**: Upload, validate, and configure legal document templates
- **Centralized Settings**: Firm configuration management with auto-save and validation
- **Real-time Animations**: Classic hourglass sand flip animation with 3-second cycles
- **Interactive Review**: Legal claim selection, damage configuration, and timeline validation
- **Timeline Validation**: Visual chronological error detection with detailed reporting
- **Document Editing**: In-browser complaint editing with version management and live preview
- **iCloud Integration**: Synchronization capabilities with connection testing and status monitoring

**Advanced Features**:
- **52 REST API Endpoints**: Comprehensive API coverage for all functionality
- **WebSocket Communication**: Real-time bidirectional communication with automatic reconnection
- **Defense-in-Depth Validation**: Multi-layer data quality validation with detailed error reporting
- **Professional UI Components**: Toast notifications, progress indicators, file status displays
- **Attorney Tools**: Template upload, creditor address management, firm settings configuration
- **Case Lifecycle Management**: Complete workflow from file detection to document generation
- **Performance Optimization**: Grid caching, smart polling, version-controlled asset delivery

**Server Commands**:
```bash
# Start dashboard
./start.sh

# Stop dashboard
./stop.sh

# Restart dashboard
./restart.sh
```

### 4. Browser Service - Court-Ready PDF Generation Engine
**Location**: `browser/`  
**Purpose**: Headless browser service for pixel-perfect HTML-to-PDF conversion  
**Technology**: Puppeteer with Chromium engine, Node.js runtime, Python integration wrapper

**Key Capabilities**:
- **Pixel-Perfect PDF Generation**: Chromium-based rendering identical to browser print-to-PDF functionality
- **Court-Ready Formatting**: A4 format with standard 1-inch margins compliant with legal filing requirements
- **Superior Performance**: Sub-3-second generation times with <50MB memory footprint
- **Professional Output**: Vector-based fonts, preserved graphics, optimized file sizes (300-500KB)
- **Monkey Integration**: Seamless Python API integration with `--with-pdf` CLI flag support
- **Batch Processing**: Multi-document processing capabilities with performance scaling
- **Error Recovery**: Comprehensive error handling with graceful degradation and detailed diagnostics

**Advanced Features**:
- **Puppeteer Engine**: Google's Chromium automation for enterprise-grade reliability
- **Python Wrapper**: Drop-in integration with existing TM Python services via `print.py`
- **Performance Monitoring**: Built-in benchmarking with processing time and memory usage metrics
- **Quality Assurance**: Court-ready output validation and legal format compliance checking
- **Centralized Output**: All PDFs saved to `TM/outputs/browser/` for organized file management
- **Testing Framework**: Comprehensive test suite including single-file, batch, and integration testing

**CLI Commands**:
```bash
# Single PDF generation (auto-outputs to TM/outputs/browser/)
node pdf-generator.js complaint.html

# Python wrapper for TM integration
python3 print.py single complaint.html complaint.pdf

# Performance benchmarking
./benchmark.sh

# Comprehensive testing
./run-tests.sh full

# Service health check
./test-integration.sh
```

## Complete Data Flow Pipeline

```
Legal Documents → Dashboard UI → Tiger Analysis → Hydrated JSON → Interactive Review → Monkey Generation → Browser PDF → Court-Ready Documents
```

### Detailed Professional Workflow

#### 1. **Case Initialization & File Detection** (Dashboard)
- **Dual File Monitoring**: Real-time watching of source files (`test-data/sync-test-cases/`) and output files (`outputs/tests/`)
- **Automatic Case Discovery**: New case folders automatically detected and initialized
- **File Validation**: Document type validation (PDF, DOCX, TXT) with size and format checks
- **Progress Initialization**: 5-step progress tracking (Synced → Classified → Extracted → Reviewed → Generated)
- **WebSocket Broadcasting**: Real-time updates to all connected Dashboard clients

#### 2. **ML-Powered Document Analysis** (Tiger)
- **Advanced OCR Processing**: Docling ML models process complex PDF layouts with table extraction
- **Multi-Format Intelligence**: Native DOCX parsing, structured TXT processing, OCR PDF analysis
- **Legal Entity Extraction**: 
  - Court names with jurisdiction validation
  - Party identification (plaintiff/defendants) with role classification
  - Case numbers with format validation
  - Attorney information with bar admission details
  - Damage amounts with categorization (actual, statutory, punitive)
  - Timeline extraction with chronological validation
- **Confidence Scoring**: ML confidence levels (0.0-1.0) for all extracted entities
- **Quality Assessment**: Overall document quality score (0-100) with production thresholds

#### 3. **Intelligent Case Consolidation** (Tiger)
- **Multi-Document Aggregation**: Information from all case documents merged intelligently
- **Conflict Resolution**: Automatic resolution of conflicting information with confidence weighting
- **Timeline Validation**: Chronological consistency checking across all documents
- **Entity Deduplication**: Smart merging of duplicate entities with confidence preservation
- **Schema Generation**: FCRA/NY FCRA compliant structured JSON output
- **Settings Integration**: Automatic merger with Dashboard firm settings for complete attorney information

#### 4. **Interactive Legal Review** (Dashboard)
- **Professional Review Interface**: Responsive design at `/review?case_id=<case_name>`
- **Legal Claim Selection**: Interactive selection of applicable FCRA/NY FCRA violations
- **Damage Configuration**: Categorization and configuration of actual, statutory, and punitive damages
- **Timeline Validation Display**: Visual representation of case chronology with error highlighting
- **Real-time Updates**: Live progress tracking with numbered step indicators (1-5)
- **Quality Feedback**: Visual indicators of data completeness and extraction confidence

#### 5. **Court-Ready Document Generation** (Monkey)
- **Template Selection**: Schema-driven selection of appropriate legal document templates
- **Professional Formatting**: Court-compliant formatting with proper legal citations
- **Attorney Signature Blocks**: Professional signature blocks with firm information and bar admissions
- **HTML Generation**: Primary document format for web review and browser PDF processing
- **Version Management**: Document versioning with metadata tracking
- **Compliance Validation**: Final document compliance checking against legal standards

#### 6. **Professional PDF Generation** (Browser)
- **Pixel-Perfect Rendering**: Chromium-based conversion from HTML to court-ready PDF format
- **Legal Format Compliance**: A4 format with standard 1-inch margins for court filing requirements
- **Vector Graphics**: High-quality typography and preserved signature blocks and letterheads
- **Automated Processing**: Seamless integration with Monkey via `--with-pdf` CLI flag
- **Performance Optimization**: Sub-3-second generation with minimal memory footprint
- **Quality Assurance**: Output validation ensuring court-ready document standards

#### 7. **Comprehensive Quality Assurance** (All Services)
- **Defense-in-Depth Validation**: Multi-layer validation at all service boundaries
- **Schema Enforcement**: Shared Pydantic schema validation across all data exchanges
- **Error Recovery**: Graceful degradation with detailed error reporting and recovery suggestions
- **Performance Monitoring**: Real-time tracking of processing times, success rates, and error patterns
- **Audit Logging**: Comprehensive logging for compliance and debugging purposes
- **Production Readiness**: Quality gates ensuring only high-confidence documents proceed to generation

## Shared Architecture Components

### Shared Schema System
**Location**: `shared-schema/`  
**Purpose**: Common Pydantic models ensuring data compatibility across all services  
**Integration**: Automatically added to Python path by service entry scripts

### Settings Integration
- **Dashboard Configuration**: Centralized firm settings (name, address, phone, email)
- **Tiger Integration**: Settings loader merges firm data with case-specific information
- **Document Output**: Professional attorney signature blocks in final legal documents

### Real-Time Communication
- **WebSocket Events**: Live file processing updates from Tiger to Dashboard
- **Progress Tracking**: Real-time step updates (Synced → Classified → Extracted → Reviewed → Generated)
- **Toast Notifications**: Professional popup notifications for processing events

## Development Setup

### System Installation
```bash
# Install all services from TM/ directory
./install.sh

# Individual service installation
./tiger/install.sh
./monkey/install.sh
# Dashboard uses npm for frontend dependencies
# Browser service auto-installs Puppeteer dependencies on first use
```

### Running the Complete System

**Primary Interface (Recommended)**:
```bash
# Start Dashboard web interface
./dashboard/start.sh
# Access at http://127.0.0.1:8000
```

**Direct Service Commands**:
```bash
# Tiger: Process case to hydrated JSON
./tiger/run.sh hydrated-json case_folder/ -o outputs/

# Monkey: Generate documents from JSON (HTML only)
./monkey/run.sh build-complaint hydrated.json --all

# Monkey: Generate documents with PDF
./monkey/run.sh build-complaint hydrated.json --with-pdf

# Monkey: Generate case review
./monkey/run.sh review hydrated.json -o review.html

# Browser: Generate PDF from HTML
./browser/print.py single complaint.html complaint.pdf
```

### Testing Framework
```bash
# Run all services test suite
./scripts/tm.sh

# Individual service tests
./scripts/t.sh    # Tiger service
./scripts/m.sh    # Monkey service

# Browser service tests
./browser/run-tests.sh full    # Complete PDF test suite
./browser/benchmark.sh         # Performance testing

# Dashboard testing via web interface
./dashboard/start.sh
```

## Production Architecture

### System Requirements
**Hardware Specifications**:
- **CPU**: Minimum 4 cores, 8+ cores recommended for parallel processing
- **RAM**: 8GB minimum, 16GB+ recommended for large document processing
- **Storage**: 50GB minimum, SSD recommended for performance
- **Network**: Stable internet connection for iCloud sync and updates

**Software Dependencies**:
- **Python**: 3.8+ with virtual environment support
- **Node.js**: 16+ for Dashboard frontend dependencies
- **PDF Processing**: Poppler utils for advanced PDF handling
- **ML Libraries**: Docling models with GPU acceleration support (optional)

### Security Architecture
**Authentication & Authorization**:
- **Session Management**: HTTP cookie-based sessions with 8-hour timeout
- **Password Security**: Configurable authentication with secure defaults
- **API Security**: All endpoints protected except public routes (/login, /)
- **Input Validation**: Comprehensive validation at all service boundaries
- **File Security**: Secure file handling with type validation and size limits

**Data Protection**:
- **Local Storage**: All case data stored locally with configurable backup
- **Encryption**: File system level encryption recommended for production
- **Access Control**: Role-based access with audit logging
- **GDPR Compliance**: Data retention policies and removal capabilities

### Performance & Monitoring
**Processing Performance**:
- **Tiger Service**: 2-5 seconds per document depending on complexity
- **Monkey Service**: <1 second document generation with template caching
- **Dashboard**: Sub-100ms API response times with WebSocket real-time updates
- **Parallel Processing**: Multi-document processing with progress tracking

**Health Monitoring**:
- **Service Health Checks**: Built-in diagnostics for all three services
- **Quality Metrics**: Processing success rates, error detection, confidence scoring
- **Performance Tracking**: Processing times, memory usage, error rates
- **Real-time Monitoring**: WebSocket connection health, API endpoint status

### Backup & Recovery
**Data Backup Strategy**:
- **Automated Backups**: Version-controlled backup system with timestamps
- **Case Data**: Complete case preservation including source files and outputs
- **Configuration**: Settings and template backup with versioning
- **Recovery Scripts**: Automated restoration from backup archives

**Disaster Recovery**:
- **Service Recovery**: Individual service restart capabilities
- **Data Recovery**: Point-in-time recovery from versioned backups
- **Configuration Recovery**: Settings restoration with validation
- **Documentation**: Complete recovery procedures and troubleshooting guides

## API Architecture

### Dashboard API (52 Verified Endpoints)
**Core API Categories**:
- **Authentication** (3 endpoints): `/api/auth/*` - Session-based security
- **Case Management** (22 endpoints): `/api/cases/*` - Complete case lifecycle management
- **Document Generation** (8 endpoints): `/api/cases/{id}/generate-*` - Monkey service integration
- **Settings & Configuration** (4 endpoints): `/api/settings`, `/api/templates/*` - Firm management
- **iCloud Integration** (5 endpoints): `/api/icloud/*` - Synchronization capabilities
- **Static Routes** (5 endpoints): `/`, `/review`, `/settings`, `/help`, `/login`
- **WebSocket** (1 endpoint): `/ws` - Real-time bidirectional communication

### Service Integration Architecture
**Inter-Service Communication**:
- **Tiger → Dashboard**: Real-time WebSocket events during file processing
- **Dashboard → Monkey**: RESTful API calls for document generation
- **Shared Schema**: Pydantic models ensuring data compatibility across services
- **Event Broadcasting**: WebSocket-based real-time updates to all connected clients

**External Integration Points**:
- **RESTful APIs**: 52 endpoints for external system integration
- **WebSocket Events**: Real-time processing updates and status changes
- **File System Integration**: Automated file monitoring and processing
- **Template System**: Configurable document templates with validation

## Professional Features

### Enterprise-Grade Capabilities
- **52 RESTful API Endpoints**: Comprehensive interface covering all functionality
- **Defense-in-Depth Validation**: Multi-layer data quality assurance with detailed error reporting
- **Enterprise Authentication**: Session-based security with 8-hour timeout and audit logging
- **Real-Time Communication**: WebSocket-based live updates with automatic reconnection
- **Professional UI/UX**: Multi-theme responsive interface (light, dark, lexigen) with accessibility support
- **Advanced Template Management**: Upload, validate, and version control legal document templates
- **iCloud Integration**: Professional synchronization with connection testing and status monitoring
- **Document Editing**: In-browser editing with version management and live preview capabilities
- **Timeline Validation**: Chronological error detection with visual reporting and correction suggestions
- **Attorney Tools**: Comprehensive suite including template management, creditor addresses, firm settings

### Legal Practice Optimization
- **FCRA Specialization**: Optimized for Fair Credit Reporting Act cases
- **Court-Ready Output**: Professional legal document formatting standards
- **Timeline Compliance**: Chronological validation for legal accuracy
- **Firm Branding**: Consistent attorney signature blocks across all documents
- **Quality Assurance**: Multi-layer validation ensuring document reliability

### Performance & Reliability
- **ML-Powered Processing**: Docling models for accurate OCR and entity extraction with confidence scoring
- **Production Quality Scoring**: 0-100 scale with configurable thresholds (>75 production, 50-75 review, <50 manual)
- **Comprehensive Error Recovery**: Graceful degradation with detailed error reporting and recovery suggestions
- **Advanced Caching**: Template caching, grid state caching, asset versioning for optimal performance
- **Real-Time Health Monitoring**: Service diagnostics, WebSocket connection health, API endpoint monitoring
- **Performance Benchmarking**: Built-in performance testing with detailed metrics and timing analysis
- **Parallel Processing**: Multi-document processing with progress tracking and resource optimization

## Directory Structure

```
TM/
├── tiger/                     # Document analysis engine
│   ├── app/
│   │   ├── engines/          # Document processing (PDF/DOCX/TXT)
│   │   ├── core/
│   │   │   ├── extractors/   # Legal entity extraction
│   │   │   ├── processors/   # Case consolidation
│   │   │   └── services/     # Hydrated JSON generation
│   │   └── cli/              # Command interface
│   ├── venv/                 # Isolated Python environment
│   └── run.sh               # Entry point script
├── monkey/                   # Document generation engine
│   ├── core/                # Document building and templating
│   ├── templates/           # Jinja2 legal document templates
│   ├── venv/               # Isolated Python environment
│   └── run.sh              # Entry point script
├── dashboard/               # Professional web interface
│   ├── main.py             # FastAPI application (40+ endpoints)
│   ├── static/
│   │   ├── themes/         # Multi-theme frontend (light/dark/lexigen)
│   │   ├── review/         # Interactive case review interface
│   │   ├── settings/       # Firm configuration management
│   │   └── templates/      # Template upload and management
│   ├── config/             # Persistent configuration
│   └── start.sh           # Web server startup
├── shared-schema/          # Common Pydantic data models
├── scripts/               # Testing and utility scripts
├── outputs/              # Generated documents and data
│   ├── tiger/           # Structured JSON output
│   ├── monkey/          # Generated legal documents
│   └── tests/           # Test outputs
└── test-data/           # Test cases and ground truth data
```

## Integration with External Systems

### Input Sources
- **File System Monitoring**: Automatic detection of new case files
- **Manual Upload**: Drag-and-drop interface for document upload
- **API Integration**: RESTful endpoints for external system integration

### Output Formats
- **Structured JSON**: Hydrated JSON for downstream processing
- **HTML Documents**: Web-optimized legal documents for review
- **PDF Generation**: Court-ready PDF documents for filing
- **Metadata Files**: Processing information and case details

## Development Best Practices

### Tiger Service Development
- **Virtual Environment**: Always use `./run.sh` scripts for proper Python path and virtual environment activation
- **ML Model Integration**: Docling models require proper initialization and GPU acceleration when available
- **Quality Thresholds**: Implement production thresholds (>75 auto-process, 50-75 review, <50 manual)
- **Entity Extraction**: Use confidence scoring (0.0-1.0) for all extracted legal entities
- **Performance Optimization**: Implement parallel processing for multi-document cases
- **Schema Compliance**: All output must validate against shared Pydantic schema with detailed error reporting

### Monkey Service Development
- **Template System**: Use schema-driven template selection with Jinja2 inheritance and includes
- **Template Validation**: Implement comprehensive template syntax and schema validation
- **Output Management**: Version control for generated documents with metadata tracking
- **Clean URLs**: Optimize URLs for PDF generation and court filing requirements
- **Performance**: Template caching and optimized rendering pipeline for sub-second generation
- **Quality Assurance**: Document completeness checking and legal format compliance validation

### Dashboard Development
- **Multi-Theme Consistency**: Maintain visual consistency across light, dark, and lexigen themes
- **Real-time Architecture**: Implement WebSocket handlers with automatic reconnection and error recovery
- **Version Synchronization**: Keep APP_VERSION, SATORI_VERSION, and cache-busting parameters synchronized
- **Defense-in-Depth Validation**: Multi-layer data quality validation with detailed user feedback
- **Performance Optimization**: Grid caching, smart polling, and optimized asset delivery
- **Authentication Security**: Session-based authentication with secure cookie handling and timeout management

### Cross-Service Integration
- **Schema Enforcement**: Use shared Pydantic models for all data exchange between services
- **Real-time Communication**: WebSocket events for live status updates and processing notifications
- **Error Handling**: Comprehensive error handling with graceful degradation and detailed user feedback
- **Settings Integration**: Centralized firm configuration management with automatic propagation
- **Quality Gates**: Implement validation checkpoints at all service boundaries
- **Performance Monitoring**: Track processing times, success rates, and error patterns across all services

## Current System Status

**Version**: Tiger-Monkey v1.9.0 - Production Ready Legal Document Processing Platform with Browser PDF Integration  
**Status**: ✅ FULLY OPERATIONAL - Enterprise-grade system ready for legal practice use

### Production Readiness Indicators
- **Complete Feature Set**: All major functionality implemented and tested
- **Enterprise Security**: Session-based authentication with comprehensive validation
- **Professional Interface**: Multi-theme responsive web interface
- **Real-time Capabilities**: WebSocket-based live updates and animations
- **Quality Assurance**: Multi-layer validation and error handling
- **Documentation**: Comprehensive documentation across all services

### Next Enhancement Opportunities
1. **Advanced Analytics**: Reporting and metrics dashboard
2. **Batch Processing**: Multi-case processing capabilities
3. **External Integration**: Legal database and filing system integration
4. **Advanced Templates**: Custom template builder interface
5. **PDF Digital Signatures**: Automated signing and certification

---

**Documentation Status**: ✅ COMPREHENSIVE - Updated for v1.9.0 as of 2025-07-14

## Agent Memory Hydration Strategy

### Complete System Understanding (Recommended)
**For New Contributors, Major Features, or Architecture Changes:**
1. Read **TM/CLAUDE.md** (this file) - Complete system overview with all technical details
2. Reference individual service CLAUDE.md files only for specific deep-dive requirements

### Service-Specific Development (Efficient)
**For Single-Service Tasks or Bug Fixes:**
1. Read **TM/CLAUDE.md** (foundational understanding)
2. Read specific service **CLAUDE.md** only if additional context needed

### Progressive Context Loading (Balanced)
**For Most Development Scenarios:**
1. Start with **TM/CLAUDE.md** (comprehensive foundation)
2. Add service-specific documentation based on task complexity
3. Reference **shared-schema/** for data contract details

**Conclusion**: This unified TM/CLAUDE.md now contains all critical information from individual service documentation files, providing complete system understanding in a single comprehensive document. Individual service CLAUDE.md files remain available for specialized deep-dive requirements, but this main file serves as the complete technical reference for the Tiger-Monkey legal document processing platform.

---

**Documentation Status**: ✅ COMPLETE & COMPREHENSIVE - Updated for v1.9.0 as of 2025-07-14

The Tiger-Monkey system represents a complete, production-ready enterprise-grade legal document processing solution with sophisticated ML capabilities, professional multi-theme web interface, real-time processing monitoring, comprehensive API architecture, and enterprise-level security and reliability suitable for professional legal practice automation workflows.