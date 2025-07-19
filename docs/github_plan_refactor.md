# TM Output Refactoring for Shadow Git Repository Architecture

## Executive Summary

This document outlines the comprehensive refactoring of the Tiger-Monkey (TM) system to implement a git-based audit trail architecture where each case processing milestone is committed to a private firm repository, with sensitive files deleted from the production server for enhanced security while maintaining full dashboard functionality through manifest-based caching.

## Current State Analysis

### Existing Problems
- **Scattered Outputs**: Files spread across multiple timestamp-based directories
- **Security Vulnerability**: Sensitive legal documents stored permanently on server
- **No Audit Trail**: Limited processing history and rollback capability
- **Redundant Storage**: Duplicate processing artifacts across services
- **Poor Organization**: `Unknown_Case_*` directories with no logical structure

### Current Structure (Problematic)
```
TM/
├── tiger/outputs/tiger/cases/Unknown_Case_20250714_122107/
├── dashboard/outputs/youssef/
├── monkey/outputs/monkey/processed/2025-07-14/
└── browser/test-outputs/
```

## Target Architecture

### Git Repository Structure (Per Law Firm)

Each law firm will have a private shadow git repository with the following structure:

```
firm-cases-repo/
├── .git/                           # Complete audit history
├── cases/
│   ├── youssef/
│   │   ├── source/                 # Commit 1: Original input files
│   │   │   ├── youssef_complaint.pdf
│   │   │   ├── Atty_Notes.docx
│   │   │   ├── Barclays_Application_Denial_1.docx
│   │   │   ├── Barclays_Application_Denial_2.docx
│   │   │   └── Adverse_Action_Letter_Cap_One.pdf
│   │   ├── processing/             # Commit 2: Tiger analysis results
│   │   │   ├── raw_text/
│   │   │   │   ├── complaint.txt
│   │   │   │   ├── atty_notes.txt
│   │   │   │   └── adverse_action.txt
│   │   │   ├── extracted_entities.json
│   │   │   ├── metadata.json
│   │   │   ├── quality_scores.json
│   │   │   └── timeline_validation.json
│   │   ├── documents/              # Commit 3: Final legal packet
│   │   │   ├── complaint.html
│   │   │   ├── complaint.pdf
│   │   │   └── summons/
│   │   │       ├── equifax.html
│   │   │       ├── equifax.pdf
│   │   │       ├── experian.html
│   │   │       ├── experian.pdf
│   │   │       ├── td_bank.html
│   │   │       ├── td_bank.pdf
│   │   │       ├── trans_union.html
│   │   │       └── trans_union.pdf
│   │   ├── data/
│   │   │   ├── hydrated_case.json  # Complete structured case data
│   │   │   └── case_timeline.json  # Chronological processing log
│   │   └── case_manifest.json      # Dashboard cache metadata
│   └── garcia/                     # Additional cases...
├── templates/                      # Firm-specific templates
│   ├── complaint_templates/
│   └── summons_templates/
├── config/                         # Firm configuration
│   ├── firm_settings.json
│   └── attorney_signatures.json
└── audit/                          # Processing audit logs
    ├── processing_history.json
    └── quality_metrics.json
```

### Server Structure (Minimal - No Sensitive Files)

```
TM/outputs/
├── manifests/                      # Case manifest cache for dashboard
│   ├── youssef_manifest.json
│   └── garcia_manifest.json
├── temp/                          # Temporary processing workspace
│   └── current_case_id/           # Deleted after commit
└── git_repos/                     # Git repository management
    ├── firm_alpha/                # Firm-specific repo clones
    └── firm_beta/
```

## Processing Workflow with Git Milestones

### Stage 1: File Synchronization & Initial Commit
```
User uploads files → TM/temp/{case_id}/source/
↓
Git: Add source files
Git: Commit "Initial case files for {case_name}"
↓
Update case_manifest.json with source file metadata
```

### Stage 2: Tiger Processing & Metadata Commit
```
Tiger processes source files → TM/temp/{case_id}/processing/
↓
Generate processing artifacts (JSON, raw text, quality scores)
Git: Add processing files
Git: Commit "Processing complete for {case_name} - Quality: {score}%"
↓
Update case_manifest.json with processing metadata
```

### Stage 3: Document Generation & Final Commit
```
Monkey generates documents → TM/temp/{case_id}/documents/
Browser creates PDFs → TM/temp/{case_id}/documents/
↓
Git: Add final documents
Git: Commit "Legal packet ready for {case_name} - {doc_count} documents"
↓
Update case_manifest.json with document metadata
```

### Stage 4: Secure Cleanup
```
Push all commits to private firm repository
↓
Copy case_manifest.json to TM/outputs/manifests/
↓
Delete entire TM/temp/{case_id}/ directory
↓
No sensitive files remain on server
```

## Case Manifest Structure

### Manifest File Schema

Each case will have a comprehensive manifest file that caches all necessary metadata for dashboard display without requiring actual files:

```json
{
  "case_id": "youssef",
  "case_name": "YOUSSEF EMAN",
  "case_type": "FCRA",
  "status": "complete",
  "created_date": "2025-07-16T10:49:00Z",
  "last_updated": "2025-07-16T10:52:00Z",
  "git_repository": "firm-alpha-cases",
  "git_commits": [
    {
      "stage": "sync",
      "commit_hash": "abc123def456",
      "timestamp": "2025-07-16T10:49:00Z",
      "message": "Initial case files for youssef",
      "author": "TM-System",
      "files_added": 5
    },
    {
      "stage": "process", 
      "commit_hash": "def456ghi789",
      "timestamp": "2025-07-16T10:50:30Z",
      "message": "Processing complete for youssef - Quality: 87%",
      "author": "Tiger-Service",
      "files_added": 8
    },
    {
      "stage": "generate",
      "commit_hash": "ghi789jkl012",
      "timestamp": "2025-07-16T10:52:00Z", 
      "message": "Legal packet ready for youssef - 9 documents",
      "author": "Monkey-Service",
      "files_added": 9
    }
  ],
  "source_files": [
    {
      "name": "youssef_complaint.pdf",
      "size": 28850,
      "type": "pdf",
      "git_path": "cases/youssef/source/youssef_complaint.pdf",
      "checksum": "sha256:abc123..."
    },
    {
      "name": "Atty_Notes.docx", 
      "size": 8424,
      "type": "docx",
      "git_path": "cases/youssef/source/Atty_Notes.docx",
      "checksum": "sha256:def456..."
    }
  ],
  "generated_documents": [
    {
      "name": "complaint.pdf",
      "size": 145234,
      "type": "pdf", 
      "git_path": "cases/youssef/documents/complaint.pdf",
      "checksum": "sha256:ghi789..."
    },
    {
      "name": "equifax_summons.pdf",
      "size": 98765,
      "type": "pdf",
      "git_path": "cases/youssef/documents/summons/equifax.pdf", 
      "checksum": "sha256:jkl012..."
    }
  ],
  "processing_metadata": {
    "tiger_quality_score": 87,
    "entities_extracted": 15,
    "confidence_average": 0.92,
    "timeline_errors": 0,
    "processing_time_seconds": 45
  },
  "legal_metadata": {
    "plaintiff": "YOUSSEF EMAN",
    "defendants": ["Equifax", "Experian", "TD Bank", "Trans Union"],
    "case_type": "FCRA",
    "damages_claimed": 15000,
    "court_jurisdiction": "NY"
  },
  "file_statistics": {
    "total_source_files": 5,
    "total_source_size": 224094,
    "total_generated_files": 9,
    "total_generated_size": 892156,
    "processing_artifacts": 8
  }
}
```

## Implementation Components

### 1. Git Integration Service

**File**: `TM/services/git_manager.py`

**Responsibilities**:
- Initialize firm-specific private repositories
- Handle automated commit workflows
- Manage repository authentication and access
- Provide file restoration capabilities
- Maintain audit trail integrity

**Key Methods**:
```python
class GitManager:
    def initialize_firm_repo(self, firm_id: str) -> str
    def commit_stage(self, case_id: str, stage: str, message: str) -> str
    def push_to_remote(self, firm_id: str) -> bool
    def restore_file(self, firm_id: str, git_path: str) -> bytes
    def get_commit_history(self, case_id: str) -> List[Dict]
```

### 2. Enhanced Case Processing Pipeline

**Modified Services**:

**Tiger Service Updates**:
- Output to standardized `temp/{case_id}/processing/` structure
- Generate comprehensive metadata JSON files
- Trigger git commit after processing completion
- Clean up local files after commit

**Monkey Service Updates**:
- Output to standardized `temp/{case_id}/documents/` structure
- Generate both HTML and PDF simultaneously
- Maintain consistent file naming conventions
- Coordinate with Browser service for PDF generation

**Dashboard Service Updates**:
- Read case data from manifest files instead of scanning directories
- Display git commit history in case timeline
- Provide file restoration interface
- Maintain real-time processing status

### 3. Manifest Management System

**File**: `TM/services/manifest_manager.py`

**Responsibilities**:
- Generate comprehensive case manifests
- Maintain manifest cache for dashboard
- Update manifests during processing stages
- Provide fast case data access

**Key Methods**:
```python
class ManifestManager:
    def create_manifest(self, case_id: str) -> Dict
    def update_manifest(self, case_id: str, stage: str, data: Dict) -> bool
    def get_case_data(self, case_id: str) -> Dict
    def list_all_cases(self) -> List[Dict]
    def search_cases(self, query: str) -> List[Dict]
```

### 4. File Restoration Service

**File**: `TM/services/file_restoration.py`

**Responsibilities**:
- Restore files from git repository on-demand
- Serve files to users temporarily
- Clean up temporary files after serving
- Maintain file integrity and security

**Workflow**:
```
User requests file download
↓
Authenticate user access
↓ 
Git checkout file to temp location
↓
Serve file via HTTP response
↓
Delete temp file immediately
↓
Log access for audit trail
```

## Security Enhancements

### Data Protection
- **No Permanent Storage**: Sensitive files never stored permanently on server
- **Git Encryption**: Private repositories with encrypted storage
- **Access Control**: Firm-specific repository isolation
- **Audit Logging**: Complete access and modification history

### File Integrity
- **Checksums**: SHA-256 verification for all files
- **Git History**: Immutable commit history prevents tampering
- **Backup Redundancy**: Distributed git repositories across multiple servers
- **Version Control**: Ability to rollback to any processing stage

## Dashboard Enhancements

### Manifest-Based Case Cards

**Enhanced Case Card Display**:
- Case status from manifest metadata
- File listings from manifest arrays
- Processing progress from git commit history
- Quality scores and metrics from cached data

**New Features**:
- **Git Timeline**: Visual commit history with rollback options
- **File Downloads**: On-demand file restoration from git
- **Audit Trail**: Complete processing history display
- **Quality Metrics**: Processing performance analytics

### Real-Time Updates

**WebSocket Integration**:
- Live processing status updates
- Git commit notifications
- Manifest updates broadcasted to dashboard
- File restoration status tracking

## Migration Strategy

### Phase 1: Infrastructure Setup
1. Create git repository templates
2. Implement GitManager service
3. Set up manifest management system
4. Configure firm-specific repositories

### Phase 2: Processing Pipeline Updates
1. Modify Tiger service for new output structure
2. Update Monkey service for standardized generation
3. Enhance Dashboard for manifest-based operation
4. Implement file restoration capabilities

### Phase 3: Data Migration
1. Create migration scripts for existing cases
2. Convert current outputs to new structure
3. Generate manifests for historical cases
4. Validate data integrity and completeness

### Phase 4: Security Implementation
1. Implement file deletion after git commits
2. Set up encrypted git repositories
3. Configure access controls and authentication
4. Test complete security workflow

## Performance Considerations

### Git Repository Optimization
- **Large File Storage**: Git LFS for PDF files over 100MB
- **Repository Pruning**: Automated cleanup of old branches
- **Compression**: Git pack optimization for storage efficiency
- **Indexing**: Fast commit lookup and search capabilities

### Dashboard Performance
- **Manifest Caching**: In-memory manifest cache for fast access
- **Lazy Loading**: Load file details on-demand
- **Background Updates**: Asynchronous manifest updates
- **Pagination**: Efficient handling of large case sets

## Monitoring and Alerting

### Git Repository Health
- **Commit Verification**: Automated integrity checks
- **Repository Size Monitoring**: Storage usage alerts
- **Backup Status**: Redundancy verification
- **Access Logging**: Security audit trails

### Processing Pipeline Monitoring
- **Stage Completion**: Processing milestone tracking
- **Error Detection**: Failed commit recovery
- **Performance Metrics**: Processing time analytics
- **Quality Assurance**: Automated quality checks

## Deployment Architecture

### Multi-Firm Support
```
Production Server (Linode)
├── TM Application (No sensitive files)
├── Git Repository Manager
├── Manifest Cache
└── Temporary Processing Workspace

Private Git Repositories (Separate Servers)
├── Firm Alpha Repository (firm-alpha-cases.git)
├── Firm Beta Repository (firm-beta-cases.git)
└── Firm Gamma Repository (firm-gamma-cases.git)
```

### Scalability Considerations
- **Horizontal Scaling**: Multiple processing servers sharing git repos
- **Load Balancing**: Repository access distribution
- **Database Optimization**: Manifest storage in fast database
- **CDN Integration**: Git repository distribution network

## Testing Strategy

### Unit Testing
- Git integration workflows
- Manifest generation and updates
- File restoration processes
- Security and access controls

### Integration Testing
- End-to-end case processing pipeline
- Multi-firm repository isolation
- Dashboard manifest synchronization
- File integrity verification

### Security Testing
- Penetration testing of file access
- Git repository security validation
- Access control verification
- Data encryption testing

## Success Metrics

### Security Metrics
- Zero sensitive files on production server
- Complete audit trail for all cases
- Successful file restoration rate
- Access control effectiveness

### Performance Metrics
- Processing pipeline efficiency
- Git commit and push times
- Dashboard response times
- File restoration speed

### Quality Metrics
- Data integrity verification
- Processing accuracy maintenance
- User experience improvement
- System reliability metrics

## Risk Mitigation

### Data Loss Prevention
- Multiple git repository backups
- Automated integrity verification
- Recovery procedures documentation
- Regular backup testing

### Security Risk Management
- Access control implementation
- Encryption at rest and in transit
- Regular security audits
- Incident response procedures

### Operational Risk Management
- Monitoring and alerting systems
- Automated failover procedures
- Documentation and training
- Regular system maintenance

---

**Document Version**: 1.0  
**Last Updated**: July 15, 2025  
**Author**: TM Development Team  
**Status**: Planning Phase

This document serves as the comprehensive guide for implementing the git-based audit trail architecture that will transform the TM system into a secure, auditable, and scalable legal document processing platform.