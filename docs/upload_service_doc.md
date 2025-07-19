# Tiger-Monkey Case File Upload Service - Implementation Plan

## Overview

Replace iCloud sync functionality with a standalone file upload system that allows users to upload ZIP files containing case folders. The system will extract these files directly into the `test-data/sync-test-cases/` directory for immediate processing by the existing Tiger-Monkey pipeline.

## Core Design Philosophy: **Minimal Impact, Maximum Isolation**

This implementation follows a strict isolation strategy where the upload service operates as a completely independent layer, requiring minimal changes to the existing codebase.

## Architecture Design

### Standalone Module Structure
```
TM/dashboard/upload_service/
├── __init__.py              # Module initialization
├── upload_handler.py        # Core upload processing logic
├── security.py              # ZIP validation and security checks
└── static/
    ├── upload.html          # Standalone upload interface
    ├── upload.js            # Self-contained JavaScript
    └── upload.css           # Independent styling
```

### Integration Points (Minimal)
```
TM/dashboard/
├── main.py                  # +3 lines for API routing
└── static/themes/light/
    └── index.html           # +1 line for navigation
```

## Technical Specifications

### Backend Implementation

#### Core Upload Handler (`upload_handler.py`)
```python
class StandaloneCaseUploader:
    """
    Self-contained case file upload processor
    """
    def __init__(self, target_directory: str):
        self.target_dir = target_directory  # test-data/sync-test-cases
        self.temp_dir = tempfile.mkdtemp()
        
    def process_upload(self, zip_file: UploadFile) -> Dict[str, Any]:
        """
        Main upload processing pipeline:
        1. Validate ZIP file
        2. Extract to temporary directory
        3. Validate case structure
        4. Move to target directory
        5. Trigger file detection
        """
        
    def validate_zip_file(self, file_content: bytes) -> bool:
        """ZIP file validation and security checks"""
        
    def extract_safely(self, zip_path: str, extract_to: str) -> List[str]:
        """Secure ZIP extraction with path traversal protection"""
        
    def validate_case_structure(self, extracted_path: str) -> List[str]:
        """Validate extracted content follows case folder structure"""
        
    def move_to_target(self, temp_path: str, case_names: List[str]) -> bool:
        """Move validated cases to final destination"""
```

#### Security Module (`security.py`)
```python
class ZipSecurityValidator:
    """
    Standalone security validation for uploaded files
    """
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_EXTRACTED_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    
    def validate_file_header(self, content: bytes) -> bool:
        """Validate ZIP file magic number"""
        
    def check_zip_slip(self, member_path: str) -> bool:
        """Prevent path traversal attacks"""
        
    def validate_extracted_content(self, file_path: str) -> bool:
        """Validate individual extracted files"""
```

### Frontend Implementation

#### Upload Interface (`static/upload.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Upload Cases - Tiger-Monkey</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <!-- Standalone upload interface -->
    <!-- Drag & drop zone -->
    <!-- Progress indicators -->
    <!-- Error messaging -->
    <!-- Success feedback -->
</body>
</html>
```

#### Upload JavaScript (`static/upload.js`)
```javascript
class CaseUploader {
    constructor() {
        this.setupDragDrop();
        this.setupFileInput();
        this.setupProgressTracking();
    }
    
    async uploadFile(file) {
        // Client-side validation
        // FormData creation
        // Fetch API upload with progress
        // Response handling
    }
    
    validateClientSide(file) {
        // File type checking
        // Size validation
        // Basic structure checks
    }
}
```

### API Integration (Minimal Changes)

#### Main Application (`main.py`) - 3 Lines Added
```python
# Import standalone service
from .upload_service.upload_handler import StandaloneCaseUploader

# Add routes
@app.get("/upload")
async def upload_page():
    return FileResponse("upload_service/static/upload.html")

@app.post("/api/upload/cases")
async def upload_cases(file: UploadFile = File(...)):
    uploader = StandaloneCaseUploader(CASE_DIRECTORY)
    return await uploader.process_upload(file)
```

#### Navigation (`index.html`) - 1 Line Added
```html
<!-- Add to sidebar navigation -->
<li>
    <a href="/upload" class="nav-link">
        <svg class="h-4 w-4 mr-3"><!-- upload icon --></svg>
        Upload Cases
    </a>
</li>
```

## Security Considerations

### File Upload Security
1. **Magic Number Validation**: Verify ZIP file headers
2. **Size Limits**: 50MB upload, 100MB extracted maximum
3. **Path Traversal Protection**: Prevent zip slip attacks
4. **Content Validation**: Only allow legal document types
5. **Filename Sanitization**: Clean extracted file names
6. **Temporary Directory Cleanup**: Automatic cleanup on completion

### ZIP Structure Validation
```
Accepted Structure:
cases.zip
├── case1/
│   ├── Atty_Notes.txt
│   ├── document1.pdf
│   └── document2.docx
└── case2/
    ├── Atty_Notes.docx
    └── adverse_action.pdf

Validation Rules:
- ZIP must contain only directories (case folders)
- Each directory must contain legal documents (.pdf, .docx, .txt)
- No executable files or suspicious content
- Case folder names must be filesystem-safe
- Total size limits enforced
```

## Integration Strategy

### File Watcher Integration (Passive)
- Upload extracts files to `test-data/sync-test-cases/`
- Existing `FileWatcher` automatically detects new files
- No changes needed to existing file monitoring
- Automatic case detection and processing
- Seamless integration with Tiger service

### Data Flow
```
User Upload → ZIP Validation → Secure Extraction → 
Case Validation → Move to Target → File Watcher Detection → 
Existing Processing Pipeline
```

## Error Handling Strategy

### Comprehensive Error Categories
1. **File Upload Errors**: Invalid format, size exceeded, corrupt file
2. **ZIP Validation Errors**: Not a ZIP, security issues, invalid structure
3. **Extraction Errors**: Corrupt archive, disk space, permissions
4. **Case Validation Errors**: Invalid structure, missing files, duplicate names
5. **System Errors**: Disk space, permissions, service availability

### User Feedback
- Real-time progress indicators
- Detailed error messages with resolution guidance
- Success confirmation with case names detected
- Professional toast notifications

## Testing Strategy

### Unit Testing
```python
# Test upload handler
def test_zip_validation()
def test_secure_extraction()
def test_case_structure_validation()

# Test security module
def test_zip_slip_protection()
def test_file_size_limits()
def test_content_validation()
```

### Integration Testing
- End-to-end upload workflow
- File watcher integration
- Error handling scenarios
- Security vulnerability testing

### User Experience Testing
- Drag & drop functionality
- Progress indicators
- Error message clarity
- Success flow validation

## Implementation Timeline

### Phase 1: Core Backend (45 minutes)
1. Create module structure
2. Implement upload handler
3. Implement security validation
4. Add API endpoints

### Phase 2: Frontend Interface (45 minutes)
1. Create standalone HTML page
2. Implement drag & drop interface
3. Add progress tracking
4. Implement error handling

### Phase 3: Integration (15 minutes)
1. Add navigation link
2. Update routing in main.py
3. Test end-to-end flow

### Phase 4: Testing & Polish (30 minutes)
1. Security testing
2. Error scenario testing
3. User experience validation
4. Documentation updates

**Total Estimated Time**: 2.25 hours

## Rollback Strategy

### Complete Removal Process
1. Delete `upload_service/` directory
2. Remove navigation link from `index.html`
3. Remove 3 lines from `main.py`
4. System returns to exact previous state

### Zero Risk Assessment
- No existing functionality modified
- No shared dependencies
- No database changes
- No configuration modifications
- Complete isolation maintained

## Benefits Analysis

### ✅ Immediate Benefits
- **Replace iCloud dependency**: Eliminate Apple authentication issues
- **Simplified workflow**: Direct file upload vs. complex sync setup
- **Offline capability**: No internet dependency for case management
- **Better control**: Direct file management without third-party limitations

### ✅ Technical Benefits
- **Zero disruption**: Existing system continues unchanged
- **Isolated development**: Can be enhanced independently
- **Easy maintenance**: Self-contained module
- **Future-proof**: Can evolve without affecting core system

### ✅ User Experience Benefits
- **Familiar interface**: Standard file upload paradigm
- **Immediate feedback**: Real-time progress and status
- **Error recovery**: Clear error messages with guidance
- **Professional presentation**: Consistent with existing dashboard

## Risk Assessment: **LOW**

### Technical Risks
- **File system permissions**: Mitigated by proper directory setup
- **Disk space limitations**: Handled by size limits and cleanup
- **Concurrent uploads**: Handled by temporary directory isolation

### Security Risks
- **Malicious uploads**: Mitigated by comprehensive validation
- **Path traversal**: Prevented by secure extraction logic
- **Resource exhaustion**: Prevented by size and time limits

### Operational Risks
- **User adoption**: Mitigated by familiar interface design
- **Data loss**: Prevented by validation before permanent storage
- **Service disruption**: Minimized by standalone architecture

## Success Metrics

### Functional Success
- [ ] Upload ZIP files successfully
- [ ] Extract to correct directory structure
- [ ] Trigger automatic case detection
- [ ] Process cases through existing pipeline
- [ ] Maintain all existing functionality

### Quality Success
- [ ] Zero security vulnerabilities
- [ ] Professional user interface
- [ ] Comprehensive error handling
- [ ] Complete documentation
- [ ] Successful rollback capability

## Future Enhancement Opportunities

### Phase 2 Enhancements (Post-MVP)
1. **Bulk upload progress**: Enhanced progress tracking for large uploads
2. **Preview functionality**: Show case contents before final extraction
3. **Automatic case naming**: Smart case name detection and suggestions
4. **Upload history**: Track and manage previous uploads
5. **Validation reports**: Detailed case structure analysis

### Long-term Enhancements
1. **Microservice extraction**: Move to independent service
2. **Cloud storage integration**: Support multiple cloud providers
3. **API expansion**: REST API for external integrations
4. **Advanced security**: Virus scanning, content analysis
5. **Analytics**: Upload metrics and usage tracking

## Conclusion

This implementation provides a robust, secure, and user-friendly replacement for iCloud sync functionality while maintaining complete isolation from the existing codebase. The standalone architecture ensures zero risk to current operations while providing immediate value to users who need to upload case files for processing.

The design emphasizes simplicity, security, and maintainability, creating a solid foundation for future enhancements while solving the immediate need for case file upload capability.

---

**Implementation Status**: ✅ Ready for Development
**Risk Level**: 🟢 LOW  
**Integration Complexity**: 🟢 MINIMAL
**User Impact**: 🟢 POSITIVE
**Maintenance Burden**: 🟢 LOW