# Monkey Service

Legal document generation engine that transforms Tiger's structured data into court-ready documents.

## Purpose

Monkey service (formerly Beaver) generates professional legal documents from Tiger's JSON output:
- FCRA complaints for federal and state courts
- Court summons and civil cover sheets  
- Legal briefs and pleadings
- Document packages ready for filing

## Features

- Jinja2 template engine for flexible document generation
- NY FCRA compliance built-in
- Multi-document package creation
- Legal format validation
- Template variable mapping from Tiger JSON

## Installation

```bash
./install.sh
source venv/bin/activate
```

## Usage

### Generate Complaint from Tiger JSON
```bash
./satori-monkey build complaint.json
```

### Generate Document Package
```bash
./satori-monkey package complaint.json --types complaint,summons,cover_sheet
```

### Preview Generation
```bash
./satori-monkey preview complaint.json --lines 50
```

### Validate Input Data
```bash
./satori-monkey validate complaint.json
```

## Output Structure

- `outputs/production/` - Production documents (never delete)
- `outputs/testing/` - Test documents (safe to delete)
- `outputs/development/` - Development documents (safe to delete)

## Template System

Templates are located in `templates/` directory:
- `fcra/complaint.jinja2` - Federal FCRA complaint template
- `fcra/summons.jinja2` - Court summons template
- `fcra/cover_sheet.jinja2` - Civil cover sheet template

## Schema Compatibility

Monkey validates input using the shared Satori Schema:
- Requires Tiger JSON with schema version 1.0
- Validates legal entity structure
- Ensures template variable availability

## Dependencies

- Python 3.8+
- Jinja2 template engine
- Shared Satori Schema package