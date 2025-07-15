# upload_service/__init__.py
"""
Standalone Case File Upload Service

This module provides a completely isolated file upload system for Tiger-Monkey
case files. It operates independently of the existing codebase with minimal
integration points.

Key Features:
- Secure ZIP file upload and validation
- Direct extraction to test-data/sync-test-cases/
- Integration with existing file watcher system
- Professional drag & drop interface
- Comprehensive error handling

Security Features:
- ZIP slip attack prevention
- File type validation
- Size limits and content verification
- Magic number validation
"""

__version__ = "1.0.0"
__author__ = "Tiger-Monkey Development Team"

from .upload_handler import StandaloneCaseUploader
from .security import ZipSecurityValidator

__all__ = ['StandaloneCaseUploader', 'ZipSecurityValidator']