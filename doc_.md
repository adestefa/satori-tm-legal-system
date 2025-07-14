

Complete Tiger-Monkey System Understanding

  End-to-End Architecture Overview

  The Tiger-Monkey (TM) system is a comprehensive legal document processing platform with three main services:

  1. Tiger Service - Document Analysis Engine

  - Purpose: Extracts structured data from legal documents
  - Input: PDF, DOCX, TXT files (primarily FCRA cases)
  - Output: Structured JSON with legal entities, timelines, damages
  - Key Technology: Docling ML models for OCR, specialized legal extractors

  2. Monkey Service - Document Generation Engine

  - Purpose: Transforms structured JSON into court-ready legal documents
  - Input: Hydrated JSON from Tiger service
  - Output: HTML/PDF legal documents (complaints, summons, reviews)
  - Key Technology: Jinja2 template engine with legal document templates

  3. Dashboard Service - Web Interface & Orchestration

  - Purpose: Professional web interface for case management and workflow orchestration
  - Input: Case files via file system monitoring
  - Output: Complete case management with real-time updates
  - Key Technology: FastAPI with WebSocket, multi-theme interface

  Complete Data Flow Pipeline

  Legal Documents (PDF/DOCX) → [Dashboard UI] → [Tiger Service] → Hydrated JSON → [Dashboard Review] → [Monkey Service] → Court-Ready Documents

  Detailed Workflow:

  1. File Detection (Dashboard)
    - Dual file monitoring system watches source and output directories
    - Real-time WebSocket updates to UI
    - Classic hourglass animation during processing
  2. Document Processing (Tiger)
    - Advanced OCR using Docling ML models for PDFs
    - Native Word document processing with table extraction
    - Legal entity extraction (courts, parties, attorneys, damages)
    - Multi-document case consolidation with confidence scoring
    - Quality assessment (0-100 scoring system)
  3. Data Consolidation (Tiger)
    - Case consolidator aggregates information from multiple documents
    - Hydrated JSON consolidator generates NY FCRA-compliant JSON
    - Timeline validation with chronological error detection
    - Integration with Dashboard settings for firm information
  4. Interactive Review (Dashboard)
    - Professional review interface for legal claim selection
    - Damage review system with multi-type damage support
    - Timeline validation display with error reporting
    - Real-time progress tracking with numbered steps (1-5)
  5. Document Generation (Monkey)
    - Jinja2 template engine processes hydrated JSON
    - Multiple output formats (HTML, PDF)
    - Professional legal document formatting
    - Attorney signature blocks with firm information
  6. Quality Assurance (All Services)
    - Schema validation across all services
    - Document quality assessment and scoring
    - Error handling with graceful degradation
    - Comprehensive logging and debugging

  Integration Architecture

  Shared Schema System

  - Location: ../shared-schema/
  - Purpose: Common Pydantic models ensuring data compatibility
  - Usage: All services validate against shared schema for type safety

  Settings Integration

  - Dashboard Settings: Centralized firm configuration (name, address, phone, email)
  - Tiger Integration: Settings loader merges firm data with case-specific information
  - Document Output: Professional signature blocks in final documents

  Real-Time Communication

  - WebSocket Events: Live file processing updates from Tiger to Dashboard
  - Progress Tracking: Real-time step updates (Synced → Classified → Extracted → Reviewed → Generated)
  - Toast Notifications: Professional popup notifications for processing events

  Key Capabilities

  Tiger Service Capabilities

  - Multi-Format Processing: PDF (OCR), DOCX (native), TXT (structured)
  - Legal Entity Extraction: Courts, parties, case numbers, attorneys, damages
  - Quality Scoring: 0-100 scale with production/review/validation thresholds
  - Case Consolidation: Multi-document aggregation into single structured case
  - Timeline Validation: Chronological error detection across documents

  Monkey Service Capabilities

  - Template System: Jinja2 templates for flexible document generation
  - Multiple Outputs: HTML (primary), PDF (court-ready), preview modes
  - Document Types: Complaints, summons, case reviews, cover sheets
  - Quality Validation: Document completeness and schema compliance
  - Batch Processing: Multiple document generation with organized output

  Dashboard Service Capabilities

  - Case Management: Complete workflow from detection to document generation
  - Authentication: Session-based security with user role management
  - Template Management: Upload and configure legal document templates
  - Settings Management: Centralized firm configuration
  - Multi-Theme Interface: Professional light, dark, and lexigen themes
  - Real-Time Monitoring: WebSocket-based live updates and animations

  Production Readiness

  Enterprise Features

  - Comprehensive API: 40+ RESTful endpoints across all services
  - Error Handling: Multi-layer validation with graceful degradation
  - Security: Session-based authentication with input sanitization
  - Performance: Optimized processing with caching and quality thresholds
  - Monitoring: Health checks, logging, and real-time status updates

  Legal Practice Suitability

  - FCRA Specialization: Optimized for Fair Credit Reporting Act cases
  - Court-Ready Output: Professional legal document formatting
  - Timeline Compliance: Chronological validation for legal accuracy
  - Firm Branding: Consistent attorney signature blocks across documents
  - Quality Assurance: Multi-layer validation ensuring document reliability

  System Status

  Current Version: v1.8.27 (Dashboard), Tiger, Monkey integratedStatus: ✅ Production Ready - Enterprise-grade legal document processing
  platformDeployment: Ready for legal practice automation workflows

  The Tiger-Monkey system represents a complete, professional-grade legal document processing solution with sophisticated ML capabilities,
  real-time web interface, and enterprise-level reliability suitable for legal practice management.

--


📋 Key Features : Creditor Address Config System

  - Major credit bureaus: Pre-configured with standard defendant addresses
  - Legal entity types: Proper corporate structure information for court documents
  - Address formatting: Complete street, city, state, ZIP structure
  - Category classification: Distinguishes between CRAs and furnishers
  - Extensible: Easy to add new creditors through settings interface

  The creditor address config system is now fully operational and ready for lawyers to manage standard addresses for legal document generation.
  The system ensures consistent, accurate defendant addressing in summons and other court documents.


--

Dashboard: 



Dashboard CLAUDE.md Documentation Summary

  Key Changes Made:

  1. Updated System Status - Changed from "Critical defect" to "Production Ready v1.8.27"
  2. Enhanced Architecture Section - Updated technology stack to reflect current capabilities
  3. Expanded Core Components - Added authentication, template management, and settings components
  4. Enhanced Features Section - Updated with real-time capabilities, animations, and enterprise features
  5. Comprehensive API Documentation - Added all 40+ endpoints including authentication, settings, and templates
  6. Updated Data Flow - Enhanced pipeline with WebSocket events and validation layers
  7. Current Feature Set - Added detailed section on v1.8.27 capabilities
  8. Enhanced Development Guidelines - Updated with current best practices and integration points
  9. Updated Testing Protocol - Added WebSocket, authentication, and template testing procedures
  10. System Status Summary - Added comprehensive overview of current capabilities and production readiness

  Documentation Now Reflects:

  - Real-time WebSocket communication with file processing animations
  - Classic hourglass sand flip animation (3-second cycles)
  - Multi-theme professional interface (light, dark, lexigen)
  - Enterprise authentication system with session management
  - Template management capabilities with upload functionality
  - Centralized firm configuration via settings dashboard
  - Advanced data quality validation with defense-in-depth approach
  - Responsive flexbox layout with fixed-width cards
  - Timeline validation and chronological error detection
  - Production-ready status suitable for legal practice use

  The documentation is now comprehensive, accurate, and reflects the sophisticated legal document processing platform that the dashboard has
  become.



