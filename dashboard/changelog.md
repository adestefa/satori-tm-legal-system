# Dashboard Changelog

All notable changes to the TM Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.2] - 2025-07-09

### Added
- **Changelog Display System**: Complete changelog integration in settings page
  - Added `/api/changelog` API endpoint to serve changelog content
  - Implemented changelog section in settings page with professional styling  
  - Added markdown to HTML conversion with syntax highlighting
  - Real-time version and last updated information display
  - Loading states and error handling for changelog content
  - Responsive design with proper typography and spacing

### Changed
- Updated version synchronization to v1.6.2 across all components
- Enhanced cache-busting parameters for JavaScript imports
- Improved settings page layout with comprehensive changelog display

## [1.6.1] - 2025-01-09

### Fixed
- **Document Preview Tab Switching**: Resolved issue where Document Preview component was appearing simultaneously with Timeline Validation content
  - Fixed conflicting JavaScript tab handling between `review.js` and `timeline-validation.js`
  - Enhanced `setupTabSwitching()` function to properly manage all three tabs (Review Data, Timeline Validation, Preview Document)
  - Removed conflicting event handlers from `timeline-validation.js`
  - Updated cache-busting parameters to ensure JavaScript changes load properly

### Confirmed
- **Processing Spinner System**: Validated that comprehensive processing animations are working correctly
  - Multi-state spinner system: 🔍 Validating → ⛔ Processing → ✅ Complete / ❌ Error
  - Real-time validation feedback with quality scores
  - Detailed error messages with actionable recommendations
  - Recovery options with "Refresh after fixing" functionality

### Changed
- Updated version synchronization across all components to v1.6.1
- Enhanced JavaScript cache-busting for reliable updates
- Improved tab navigation reliability

## [1.6.0] - 2025-01-09

### Added
- **Template Upload System (MVP Tasks 2.1 & 2.2)**
  - Professional drag-and-drop interface for .docx template uploads
  - File validation (type, size, format checking)
  - Template preview and management functionality
  - Comprehensive placeholder variable schema with documentation
  - Backend API endpoints for template CRUD operations
  - Integration with existing settings system

### Fixed
- **Critical System Crash**: Resolved missing `python-multipart` dependency
  - Added required package for file upload functionality
  - Restored full dashboard functionality after template upload implementation
  - Fixed FastAPI server startup issues

### Enhanced
- **Settings Page**: Added Document Templates section
  - Template upload interface with real-time status updates
  - Placeholder variable help documentation
  - Template action buttons (preview, remove)
  - Professional styling with drag-and-drop support

## [1.5.34] - 2025-01-08

### Added
- **Settings-Based Attorney Information System**
  - Centralized firm information management through dashboard settings
  - Separation of firm constants from case-specific variables
  - Complete settings page with validation and auto-save
  - Integration with Tiger service for automatic attorney data population
  - Professional signature block generation in complaint documents

### Enhanced
- **Tiger Service Integration**: Added settings loader for firm configuration
- **Monkey Templates**: Enhanced complaint template with attorney signature blocks
- **Data Flow**: Streamlined attorney information from settings to final documents

## [1.5.11] - 2025-01-07

### Added
- **Dual File Monitoring System**
  - Real-time monitoring of both source files and generated output files
  - Automatic detection of file creation, modification, and deletion
  - Eliminated need for server restarts during development

### Enhanced
- **Manual Refresh Functionality**: Added `/api/refresh` endpoint and UI button
  - On-demand case state recovery without server restart
  - User-friendly refresh button with loading states
  - Toast notifications for operation feedback

### Improved
- **Development Workflow**: Enhanced reset script with comprehensive file cleanup
- **File Detection**: Real-time state synchronization across all file operations

## [1.5.3] - 2025-01-07

### Fixed
- **Factual Background Formatting**: Resolved double numbering issue in review page
  - Fixed JavaScript numbering logic to detect existing numbered content
  - Prevented duplicate numbering (e.g., "11. 1. Plaintiff...")
  - Maintained professional legal document formatting

### Enhanced
- **Cache-Busting**: Updated JavaScript imports with proper version parameters
- **Review Page**: Improved readability with intelligent numbering detection

## [1.5.1] - 2025-01-07

### Added
- **Defense in Depth Validation System**
  - Multi-layer validation preventing bypass of data quality checks
  - Comprehensive backend API validation enforcement
  - Frontend UI enhancement for error state handling
  - Smart polling management during validation errors

### Fixed
- **Critical Validation Bypass**: Resolved cases with inadequate data proceeding to generation
  - Added mandatory validation checks in process endpoint
  - Enhanced error handling for all case states
  - Eliminated Chen John case type failures

### Enhanced
- **User Experience**: Persistent error display with detailed feedback
- **System Reliability**: Zero validation bypass pathways implemented

## [1.4.6] - 2025-01-06

### Enhanced
- **Progress Indicators**: Replaced simple dots with numbered circular indicators
  - Clear step tracking (1-5) with visual status indication
  - Improved accessibility with larger, numbered circles
  - Professional styling with green/gray color coding

### Added
- **File Status Display**: Enhanced file listing for case states
  - NEW cases show "Files to Process:" with checkboxes
  - Processed cases show "Files Processed:" with checkmarks
  - Smart filtering excludes system files for cleaner display

### Improved
- **Version Management**: Synchronized version tracking across all components
- **Cache-Busting**: Query parameters on JavaScript imports for reliable updates

## [1.0.0] - 2025-01-01

### Added
- **Initial Dashboard Release**
  - FastAPI-based web application with comprehensive case management
  - Real-time file system monitoring and background processing
  - Interactive review page for legal claim selection and validation
  - Multi-theme support (light, dark, lexigen)
  - Native integration with Tiger and Monkey services

### Features
- **Case Management**: Visual case tracking with progress indicators
- **Service Integration**: Direct Tiger/Monkey service execution
- **Multi-Theme Support**: Professional interface themes
- **Real-Time Updates**: Live file monitoring and status updates

---

## Version Format

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.6.1)
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Backup Policy

- Automatic backup created before each version increment
- Backup format: `TM-backup-YYYY-MM-DD-HH-MM-SS-vX.X.X.zip`
- Stored in `TM/backups/` directory
- Manifest updated with version description

## Links

- [Dashboard Documentation](CLAUDE.md)
- [Project Root](../README.md)
- [Backup Directory](../backups/)