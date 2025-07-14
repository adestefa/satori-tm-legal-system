# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Monkey service is a lightweight document generation engine that transforms Tiger's structured JSON into court-ready legal documents using Jinja2 templates. It's part of the Tiger-Monkey (TM) legal document processing system, specifically designed for FCRA (Fair Credit Reporting Act) cases.

## Architecture

### Core Components

**CLI Interface (`cli.py`)**
- Entry point: `satori-monkey` command
- 7 main commands: `build-complaint`, `review`, `generate-summons`, `validate`, `preview`, `templates`, `test`
- Comprehensive argument parsing with help text and examples

**Document Builder (`core/document_builder.py`)**
- `MonkeyDocumentBuilder` - Main orchestrator class
- Handles document package generation (complaint, summons, cover sheet)
- Manages template rendering and format conversion
- Provides document preview capabilities

**Template Engine (`core/html_engine.py`)**
- `HtmlEngine` - Jinja2 template processor
- Auto-escaping for HTML/XML security
- Template validation and information retrieval
- Custom filter support (extensible)

**Supporting Components**
- `validators.py` - Document validation using shared schema
- `output_manager.py` - File organization and metadata management
- `pdf_service.py` - PDF generation from HTML (legacy)
- `quality_validator.py` - Document quality assessment

**Browser PDF Integration**
- **Browser Service Integration**: Seamless PDF generation via TM Browser service
- **CLI Enhancement**: `--with-pdf` flag for complaint generation with court-ready PDFs
- **Python API**: Direct integration through `BrowserPDFGenerator` class
- **Performance**: Sub-3-second PDF generation with pixel-perfect accuracy
- **Output Management**: Centralized PDF storage in `TM/outputs/browser/` directory

### Template System

**Directory Structure:**
```
templates/
├── html/
│   ├── fcra/complaint.html    # Main FCRA complaint template
│   ├── case_review.html       # Interactive case review
│   └── shared/base.html       # Base template for inheritance
└── fcra/complaint.jinja2      # Legacy template format
```

**Template Variables:**
Templates receive the full hydrated JSON structure as `hydratedjson`:
```jinja2
{{ hydratedjson.case_information.court_district }}
{{ hydratedjson.plaintiff.name }}
{% for defendant in hydratedjson.defendants %}
    {{ defendant.name }}
{% endfor %}
```

## Development Workflow

### Installation and Setup
```bash
# Install dependencies and create virtual environment
./install.sh

# Verify installation
./health_check.sh
```

### Running Commands
```bash
# Always use run.sh to activate virtual environment
./run.sh build-complaint complaint.json

# Generate complete document package
./run.sh build-complaint complaint.json --all

# Generate documents with PDF (Browser integration)
./run.sh build-complaint complaint.json --with-pdf

# Custom output directory
./run.sh build-complaint complaint.json -o /custom/output/

# Generate HTML review document
./run.sh review complaint.json -o review.html

# Validate input data
./run.sh validate complaint.json

# Preview document generation
./run.sh preview complaint.json --lines 50

# List available templates
./run.sh templates --pattern fcra
```

### Testing
```bash
# Quick service test
./run.sh test --quick

# Full service test
./run.sh test

# Service health check
./health_check.sh
```

## Data Flow

### Input Processing
1. **JSON Input** - Hydrated JSON from Tiger service
2. **Schema Validation** - Validate against shared Pydantic schema
3. **Template Selection** - Choose appropriate template based on case type
4. **Data Preparation** - Format data for template rendering

### Document Generation
1. **Template Rendering** - Jinja2 processes template with data
2. **Format Conversion** - Convert to HTML/PDF as requested
3. **Quality Validation** - Assess document completeness
4. **Output Organization** - Save to appropriate directory structure

### Output Structure
```
outputs/monkey/
├── production/     # Production-ready documents (never delete)
├── testing/        # Test documents (safe to delete)
└── development/    # Development documents (safe to delete)
```

## Schema Integration

The service uses the shared schema from `../shared-schema/` for:
- **Input Validation** - Ensure Tiger output conforms to expected structure
- **Type Safety** - Provide IDE support and error prevention
- **Template Compatibility** - Guarantee template variables are available

Schema path is automatically added to `sys.path` by the `satori-monkey` entry script.

## Key Commands Reference

### build-complaint
**Purpose:** Generate legal complaint documents
**Usage:** `./run.sh build-complaint complaint.json [options]`
**Options:**
- `--all` - Generate complete package (complaint + summons + cover sheet)
- `--with-pdf` - Generate PDF version using Browser service (court-ready output)
- `--format` - Output format (html, pdf, txt, docx)
- `--template` - Custom template override
- `-o, --output` - Custom output directory

### review
**Purpose:** Generate HTML review document for case analysis
**Usage:** `./run.sh review complaint.json [options]`
**Options:**
- `-o, --output` - Output file path (default: review.html)

### validate
**Purpose:** Validate complaint JSON data against schema
**Usage:** `./run.sh validate complaint.json`
**Returns:** Validation score, errors, warnings, and data summary

### preview
**Purpose:** Preview document without generating files
**Usage:** `./run.sh preview complaint.json [options]`
**Options:**
- `--lines` - Number of lines to show (default: 50)

### templates
**Purpose:** List and inspect available templates
**Usage:** `./run.sh templates [options]`
**Options:**
- `--pattern` - Filter templates by pattern

## Error Handling

### Common Issues
1. **Schema Validation Errors** - Input data doesn't match expected structure
2. **Template Not Found** - Missing or incorrectly named template files
3. **Virtual Environment Issues** - Dependencies not installed or activated
4. **Import Errors** - Shared schema not accessible

### Debugging Commands
```bash
# Check template availability
./run.sh templates

# Validate input data structure
./run.sh validate complaint.json

# Test service functionality
./run.sh test

# Check installation
./health_check.sh
```

## Development Best Practices

### Virtual Environment Usage
- **Always use `./run.sh`** for command execution
- **Never run `satori-monkey` directly** without virtual environment
- Use `source venv/bin/activate` only for debugging sessions

### Template Development
- Test templates with real data using preview command
- Use template inheritance for consistency
- Document template variables in comments
- Validate HTML output before finalizing

### Schema Compatibility
- Validate inputs early using validation command
- Handle missing data gracefully in templates
- Follow shared schema structure for reliability

## Integration Points

### Tiger Service Integration
- **Input:** Hydrated JSON from Tiger's consolidation process
- **Format:** JSON file with complete case information
- **Schema:** Shared Pydantic schema ensures compatibility

### Browser PDF Service Integration
- **Purpose:** Convert HTML documents to court-ready PDFs
- **Technology:** Headless Chromium via Puppeteer for pixel-perfect output
- **Integration:** Seamless Python API through `browser/print.py` wrapper
- **Performance:** Sub-3-second generation with optimized file sizes
- **Output:** Centralized storage in `TM/outputs/browser/` directory
- **CLI Enhancement:** `--with-pdf` flag for automatic PDF generation

**Integration Workflow:**
```
Monkey HTML Generation → Browser PDF Service → Court-Ready PDF
```

**Python API Usage:**
```python
# In document_builder.py
def _generate_pdf_from_html(self, html_file_path: str) -> Optional[str]:
    browser_service_path = Path(__file__).parent.parent.parent / "browser" / "print.py"
    pdf_file_path = html_file_path.replace('.html', '.pdf')
    
    result = subprocess.run([
        sys.executable, str(browser_service_path), 'single', html_file_path, pdf_file_path
    ], capture_output=True, text=True, timeout=30)
    
    return pdf_file_path if result.returncode == 0 else None
```

**Enhanced CLI Output:**
```
✅ Complaint: complaint.html
📄 Complaint PDF: complaint.pdf
📁 PDF Path: outputs/browser/complaint.pdf

📁 Document Package
==============================
📄 Complaint HTML: monkey/outputs/monkey/processed/2025-07-14/complaint.html
📄 Complaint PDF:  outputs/browser/complaint.pdf
📋 Metadata:       monkey/outputs/monkey/metadata/2025-07-14/package.json
```

### Output Integration
- **HTML Documents** - Primary output format for web viewing
- **PDF Generation** - Court-ready PDF conversion
- **Metadata Files** - Document generation information and case details

## Performance Considerations

- **Template Caching** - Jinja2 templates are compiled and cached
- **Memory Management** - Efficient processing of large JSON files
- **Generation Speed** - Optimized for typical legal document sizes
- **Error Recovery** - Graceful handling of template and data issues

The Monkey service provides a robust, template-driven approach to legal document generation with strong schema validation and flexible output options.