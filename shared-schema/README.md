# Satori Shared Schema

Unified JSON schema package for Tiger (document processing) and Monkey (document generation) services.

## Purpose

This package provides a single source of truth for the JSON schema that defines the interface between Tiger and Monkey services. It ensures both services use identical data structures for seamless integration.

## Schema Version

Current version: **1.0**

## Installation

```bash
pip install -e .
```

## Usage

```python
from satori_schema import validate_hydrated_json, HydratedJSONSchema

# Validate JSON data
is_valid, errors, warnings = validate_hydrated_json(data)

# Get schema version
version = HydratedJSONSchema.VERSION
```

## Schema Structure

The hydrated JSON schema defines the complete structure for legal case data:

- **case_information**: Court and case details
- **parties**: Plaintiff, defendants, and counsel information  
- **factual_background**: Case narrative and timeline
- **causes_of_action**: Legal claims and statutory basis
- **damages**: Actual, statutory, and punitive damages
- **metadata**: Processing information and versioning

## Compatibility

This schema is used by:
- **Tiger Service**: Validates output during case consolidation
- **Monkey Service**: Validates input during document generation

Both services must use the same schema version to ensure compatibility.