# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tiger is a legal document processing and analysis engine that extracts structured data from legal documents (PDFs, DOCX, TXT). It's designed specifically for FCRA (Fair Credit Reporting Act) cases and generates structured JSON output for downstream processing by the Monkey service.

## Architecture

### Core Components

**Document Processing Pipeline:**
- `app/engines/`: Document processing engines for different formats
  - `docling_engine.py`: Advanced OCR for PDFs using Docling ML models
  - `docx_engine.py`: Native Word document processing with table extraction
  - `text_engine.py`: Plain text processing
  - `base_engine.py`: Common interface for all engines

**Legal Entity Extraction:**
- `app/core/extractors/`: Specialized extractors for legal entities
  - `legal_entity_extractor.py`: Courts, parties, case numbers
  - `attorney_extractor.py`: Attorney and law firm identification
  - `party_extractor.py`: Plaintiff/defendant classification
  - `court_extractor.py`: Court jurisdiction and district identification
  - `date_extractor.py`: Legal timeline extraction
  - `damage_extractor.py`: Financial damage calculations
  - `financial_extractor.py`: Financial data extraction

**Case Consolidation:**
- `app/core/processors/case_consolidator.py`: Consolidates information from multiple documents into a single case structure
- `app/core/services/hydrated_json_consolidator.py`: Generates NY FCRA-compliant hydrated JSON from consolidated cases

**Document Processor:**
- `app/core/processors/document_processor.py`: Main orchestrator that coordinates engines and extractors

### Entry Points

**Main CLI Interface:**
- `satori-tiger`: Main executable script that sets up Python paths and imports
- `run.sh`: Shell wrapper that activates virtual environment and runs `satori-tiger`
- `app/cli/commands.py`: Complete CLI command definitions and handlers

**Health Check:**
- `health_check.sh`: Validates dependencies, modules, and directory structure

## Common Development Commands

### Environment Setup
```bash
# Install dependencies and create virtual environment
./install.sh

# Activate virtual environment manually (usually not needed)
source venv/bin/activate
```

### Running Tiger Service

**IMPORTANT:** Always use `./run.sh` to run Tiger commands, not direct Python execution. This ensures proper virtual environment activation.

```bash
# Get service information and health status
./run.sh info

# Process a single document
./run.sh process /path/to/document.pdf -o /path/to/output/

# Process an entire case folder (multiple documents)
./run.sh hydrated-json /path/to/case_folder/ -o /path/to/output/

# Batch process with comprehensive reporting
./run.sh batch /path/to/documents/ -o /path/to/output/

# Validate document quality without full processing
./run.sh validate /path/to/document.pdf

# Run service tests
./run.sh test
```

### Testing Commands

```bash
# Run health check
./health_check.sh

# Run service test suite
./run.sh test

# Quick functionality test
./run.sh test --quick
```

## Data Flow

### Single Document Processing
```
Document → Engine (PDF/DOCX/TXT) → Extractors → Quality Assessment → JSON/TXT/MD Output
```

### Case Consolidation (Primary Workflow)
```
Case Folder → Multiple Documents → Individual Processing → Case Consolidator → Hydrated JSON → Monkey Service
```

The `hydrated-json` command is the primary interface for generating court-ready structured data that feeds into the Monkey service for document generation.

## Key Configuration

### Virtual Environment
Tiger uses its own isolated Python virtual environment (`venv/`) with heavy ML dependencies including Docling for OCR processing.

### Shared Schema Integration
Tiger integrates with the shared schema package located at `../shared-schema/`. The `satori-tiger` entry point automatically adds this to the Python path.

### Output Structure
- `outputs/production/`: Production outputs (permanent)
- `outputs/testing/`: Test outputs (safe to delete)
- `outputs/development/`: Development outputs (safe to delete)

## Quality Thresholds

Tiger implements a comprehensive quality scoring system:
- **High Quality (≥80)**: Production ready
- **Medium Quality (50-79)**: Review recommended
- **Low Quality (<50)**: Manual validation required

## Integration Points

### With Monkey Service
Tiger outputs hydrated JSON files that serve as input to the Monkey service for document generation.

### With Dashboard
Tiger supports real-time event broadcasting to the Dashboard service via the `--dashboard-url` parameter.

### With Shared Schema
Tiger validates all JSON output against the shared Pydantic schema to ensure data compatibility across services.

## Dependencies

**Core Processing:**
- `docling>=1.0.0`: ML-powered OCR for PDFs
- `python-docx>=0.8.11`: Word document processing
- `pandas>=2.1.0`: Data manipulation
- `pydantic>=2.5.0`: Data validation

**ML Stack:**
- `Pillow>=10.0.0`: Image processing
- `numpy>=1.24.0`: Numerical operations

## Development Notes

### Path Management
The Tiger service uses absolute imports from the service root. All imports within Tiger should be written as `from app.core.processors.document_processor import DocumentProcessor`.

### Error Handling
Tiger implements comprehensive error handling with quality metrics and confidence scoring. Failed documents are logged and can be retried.

### Legal Domain Specificity
Tiger is optimized for FCRA cases and includes specialized extractors for legal entities, damages, and timeline validation specific to consumer protection law.