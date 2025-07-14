# Tiger-Monkey Legal Document Processing System
## Comprehensive Project Documentation & Architecture Guide (Version 3.0)

## Executive Summary

Tiger-Monkey (TM) is a comprehensive legal document processing system designed for consumer protection attorneys, transforming raw case documents into court-ready legal filings. The system is structured as a dual-service application with Tiger handling document extraction and Monkey generating legal documents.

**Current Status**: The Tiger and Monkey services have been successfully extracted from a monolithic system into a new, cleaner project structure located at `/Users/corelogic/satori-dev/TM/`. The focus is now on ensuring robust, independent operation and clear testing protocols.

---

## Architecture Overview

### 🏗️ **Current Service-Oriented Architecture**

The project is organized into two primary services, `tiger` and `monkey`, within a single repository. This separation facilitates independent development and future microservice extraction.

```
┌───────────���────────┐      ┌──────────────────────┐
│ TM/ (Project Root) │      │                      │
│ │                  │      │                      │
│ ├── 🐅 tiger/      │      │ ├── 🐒 monkey/       │
│ │   (Extraction)   │      │ │   (Generation)     │
│ └── 🧬 shared-schema/│      │ └── 🧬 shared-schema/│
└────────────────────┘      └──────────────────────┘

Workflow:
Legal Docs ──> [Tiger Service] ──> [Hydrated JSON] ──> [Monkey Service] ──> Court-Ready Docs
```

### 🎯 **Target Microservices Architecture (Future)**

The long-term vision remains to deploy these as fully independent, containerized microservices.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tiger Service │    │  Monkey Service │    │  Chrome Service │
│   (Extraction)  │───▶│ (Generation)    │───▶│ (PDF Rendering) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Core Services

### 🐅 Tiger Service ("The Legal Data Harvester")

**Status**: Operational and stable within the `TM/tiger/` directory.

**Purpose**: Extract and consolidate legal data from case documents into structured JSON.

**Core Capabilities**:
- **Multi-Format Processing**: PDF (via Docling OCR), DOCX (native), TXT.
- **Legal Entity Extraction**: Courts, parties, attorneys, case numbers.
- **Quality Assessment**: 0-100 scoring system for extraction confidence.
- **Structured Output**: Hydrated JSON schema compatible with the Monkey service.

### 🐒 Monkey Service ("The Court Document Builder")

**Status**: Operational and stable within the `TM/monkey/` directory.

**Purpose**: Generate court-ready legal documents from Tiger's JSON output.

**Core Capabilities**:
- **Template Engine**: Utilizes Jinja2 for document creation.
- **HTML+PDF Pipeline**: Capable of generating documents through an HTML-to-PDF rendering pipeline (requires Chrome Service for PDF output).
- **Validation**: Ensures incoming JSON conforms to the shared schema.

---

## Data Flow & Integration

### **Complete Workflow**
```
1. Case Documents (PDF/DOCX)
        ↓
2. Tiger Service Processing (`TM/tiger/`)
   • Extracts legal data
        ↓
3. Hydrated JSON Schema
   • Standardized data structure
        ↓
4. Monkey Service Generation (`TM/monkey/`)
   • Renders documents from JSON
        ↓
5. Court-Ready Legal Documents
```

### **Schema Interface** (Tiger ↔ Monkey Communication)

The `shared-schema/` directory provides the Pydantic models that define the data contract between the services, ensuring compatibility.

---

## Implementation Plan & Current Status

The project has successfully completed the initial refactoring phase by separating the monolith into the `TM` project. The next phases will focus on refining the independent services and their interaction.

**Current Priorities**:
1.  **Robust Testing**: Solidify the testing framework within `TM/scripts/` to ensure reliability.
2.  **Feature Parity**: Ensure all critical features from the original system are functional in the new structure.
3.  **Documentation**: Maintain up-to-date documentation like this PRD and the `how_to_test.md` guide.

---

## Command Line Interface

**IMPORTANT**: All service commands **must** be executed using the `run.sh` scripts located within each service's directory (e.g., `tiger/run.sh`). This ensures the correct virtual environment is activated.

### **Tiger Service Commands**
*Run from `TM/tiger/`*
```bash
# Get service information
./run.sh info

# Process a single document
./run.sh process ../test-data/documents/sample.pdf

# Validate a document
./run.sh validate ../test-data/documents/sample.pdf
```

### **Monkey Service Commands**
*Run from `TM/monkey/`*
```bash
# Generate a court-ready document from JSON
./run.sh build-complaint ../test-data/test-json/hydrated-test-0.json

# List available templates
./run.sh templates

# Validate a JSON file against the schema
./run.sh validate ../test-data/test-json/hydrated-test-0.json
```

---

## Project Structure & File Organization

### **Current `TM` Project Structure**
```
TM/
├─�� tiger/
│   ├── app/
│   ├── run.sh              # <-- MUST USE to run Tiger
│   └── venv/
├── monkey/
│   ├── core/
│   ├── run.sh              # <-- MUST USE to run Monkey
│   └── venv/
├── shared-schema/          # Data contract for both services
├── scripts/                # Automated test scripts
│   ├── t.sh                # Tiger test suite
│   ├── m.sh                # Monkey test suite
│   └── tm.sh               # Full integration test
├── test-data/
│   ├── cases-for-testing/
│   └── test-json/
├── how_to_test.md          # Developer and QA testing guide
└── prd.md                  # This document
```

---

## Testing Strategy & Quality Assurance

The primary method for testing is using the automated scripts in the `TM/scripts/` directory.

### **Automated Testing Commands**
*Run from the project root `TM/`*
```bash
# Run the Tiger test suite
./scripts/t.sh

# Run the Monkey test suite
./scripts/m.sh

# Run the end-to-end integration test
./scripts/tm.sh

# Run a quick health check of core components
./scripts/run_health_check.sh
```

### **Manual Testing**

For detailed manual testing steps, refer to the official testing guide:
```
/Users/corelogic/satori-dev/TM/how_to_test.md
```

---

## Dependencies & Technical Requirements

### **Core Dependencies**
- **Tiger Service**: `docling`, `python-docx`, `pdfplumber`, `pydantic`
- **Monkey Service**: `jinja2`, `aiohttp`, `pydantic`
- **Shared Schema**: `pydantic`, `jsonschema`

### **System Requirements**
- **Python**: 3.8+
- **`venv`**: Each service maintains its own virtual environment.

---

**Document Version**: 3.0
**Last Updated**: July 3, 2025
**Architecture**: Service-Oriented (Tiger/Monkey)
**Status**: Active Development
**Next Milestone**: Solidify independent service testing and functionality.
