# OCR Test Data - Scanned Documents

This directory contains test documents for OCR processing validation and testing.

## Test Document Types

### High Quality Scanned Documents
- **civil_cover_sheet_scanned.pdf** - Clean scan of civil cover sheet form
- **summons_scanned.pdf** - High quality summons document scan
- **adverse_action_scanned.pdf** - Well-scanned adverse action letter

### Medium Quality Scanned Documents  
- **mixed_quality_scan.pdf** - Document with varying quality sections
- **rotated_document.pdf** - Slightly rotated document requiring correction

### Poor Quality Scanned Documents
- **poor_quality_scan.pdf** - Low resolution scan with artifacts
- **faded_document.pdf** - Document with faded text and poor contrast
- **handwritten_notes.pdf** - Document with handwritten annotations

### Edge Cases
- **multi_language.pdf** - Document with English and Spanish text
- **table_heavy.pdf** - Document with complex table structures
- **watermarked.pdf** - Document with watermarks or background elements

## OCR Testing Scenarios

### Quality Validation Tests
1. **High Quality Processing** (>0.8 quality score expected)
   - Clear text extraction with minimal artifacts
   - High confidence scores across all elements
   - Proper language detection

2. **Medium Quality Processing** (0.6-0.8 quality score expected)
   - Acceptable text extraction with some noise
   - Mixed confidence scores
   - May require text cleaning

3. **Poor Quality Processing** (<0.6 quality score expected)
   - Significant OCR artifacts present
   - Low confidence scores
   - Requires retry with enhanced settings
   - May trigger fallback processing

### Performance Benchmarks
- **Single page processing**: < 10 seconds
- **Multi-page processing**: < 30 seconds for 3 pages, < 60 seconds for 10 pages
- **Batch processing**: < 60 seconds for 20 documents
- **Memory usage**: < 2GB for large documents

### Integration Tests
- Document classification after OCR processing
- Data extraction from OCR results
- Cross-validation between OCR and existing extraction methods
- End-to-end workflow validation

## Usage

These test files are automatically created by the test suite when needed. To manually test OCR functionality:

```bash
# Run OCR tests
cd app
go test ./services -run TestOCR

# Run performance benchmarks  
go test ./services -run TestOCRPerformance

# Run integration tests
go test ./services -run TestEndToEndOCRWorkflow
```

## Quality Expectations

### Text Extraction
- Minimum 85% accuracy for structured legal documents
- Proper handling of legal terminology and case numbers
- Accurate extraction of names, dates, and monetary amounts

### Document Quality Analysis
- Automatic detection of scanned vs. native documents
- Quality scoring with actionable recommendations
- Confidence assessment for manual review decisions

### Language Support
- Primary support for English legal documents
- Basic support for Spanish text detection
- Extensible language model system

## Notes

- Test files are created as needed by the test suite
- Mock data simulates various document quality scenarios
- Real scanned documents should be added for comprehensive testing
- OCR results should be validated against known ground truth data