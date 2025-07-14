# Tiger Service

Document processing and analysis engine for legal document extraction.

## Purpose

Tiger service processes legal documents (PDFs, Word docs, text files) and extracts structured data including:
- Case information (court, case numbers, parties)
- Legal entities (attorneys, defendants, plaintiffs)
- Factual information and timelines
- Quality metrics and confidence scores

## Features

- Advanced OCR using Docling ML models
- Native Word document processing
- Legal entity extraction and validation
- Multi-document case consolidation
- Hydrated JSON output for Monkey service

## Installation

```bash
./install.sh
source venv/bin/activate
```

## Usage

### Single Document Processing
```bash
./satori-tiger process document.pdf
```

### Batch Processing
```bash
./satori-tiger batch ./documents/ -o ./outputs/
```

### Case Consolidation
```bash
./satori-tiger case-extract ./case_folder/ --hydrated-json
```

### Health Check
```bash
./satori-tiger info --health
```

## Output Structure

- `outputs/production/` - Production outputs (never delete)
- `outputs/testing/` - Test outputs (safe to delete)
- `outputs/development/` - Development outputs (safe to delete)

## Quality Thresholds

- **High Quality (≥80)**: Production ready
- **Medium Quality (50-79)**: Review recommended  
- **Low Quality (<50)**: Manual validation required

## Dependencies

- Python 3.8+
- Docling ML models
- Shared Satori Schema package