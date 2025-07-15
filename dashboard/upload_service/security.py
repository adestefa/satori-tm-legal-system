# upload_service/security.py
"""
ZIP Security Validation Module

Provides comprehensive security validation for uploaded ZIP files including:
- File header validation (magic numbers)
- ZIP slip attack prevention
- File size and content validation
- Path sanitization and safety checks
"""

import os
import zipfile
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ZipSecurityValidator:
    """Standalone security validation for uploaded ZIP files"""
    
    # Security limits
    MAX_FILE_SIZE = 50 * 1024 * 1024      # 50MB upload limit
    MAX_EXTRACTED_SIZE = 100 * 1024 * 1024 # 100MB extracted limit
    MAX_FILES = 1000                       # Maximum files in ZIP
    MAX_PATH_LENGTH = 255                  # Maximum path length
    
    # Allowed file extensions for case documents
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.doc'}
    
    # ZIP file magic numbers
    ZIP_MAGIC_NUMBERS = [
        b'PK\x03\x04',  # Standard ZIP
        b'PK\x05\x06',  # Empty ZIP
        b'PK\x07\x08',  # Spanned ZIP
    ]
    
    def __init__(self):
        self.validation_errors = []
        
    def validate_upload(self, file_content: bytes, filename: str) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of uploaded file
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            (is_valid, error_messages)
        """
        self.validation_errors = []
        
        # Basic validations
        if not self._validate_file_size(file_content):
            return False, self.validation_errors
            
        if not self._validate_file_header(file_content):
            return False, self.validation_errors
            
        if not self._validate_filename(filename):
            return False, self.validation_errors
            
        # ZIP-specific validations
        try:
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                
                if not self._validate_zip_structure(temp_file.name):
                    return False, self.validation_errors
                    
        except Exception as e:
            self.validation_errors.append(f"ZIP validation failed: {str(e)}")
            return False, self.validation_errors
            
        return True, []
    
    def _validate_file_size(self, content: bytes) -> bool:
        """Validate file size is within limits"""
        if len(content) > self.MAX_FILE_SIZE:
            size_mb = len(content) / (1024 * 1024)
            limit_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            self.validation_errors.append(
                f"File too large: {size_mb:.1f}MB exceeds {limit_mb}MB limit"
            )
            return False
        return True
    
    def _validate_file_header(self, content: bytes) -> bool:
        """Validate ZIP file magic number"""
        if len(content) < 4:
            self.validation_errors.append("File too small to be a valid ZIP")
            return False
            
        header = content[:4]
        for magic in self.ZIP_MAGIC_NUMBERS:
            if header.startswith(magic):
                return True
                
        self.validation_errors.append("Invalid file format: Not a ZIP file")
        return False
    
    def _validate_filename(self, filename: str) -> bool:
        """Validate filename safety"""
        if not filename.lower().endswith('.zip'):
            self.validation_errors.append("File must have .zip extension")
            return False
            
        # Check for dangerous characters
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in filename:
                self.validation_errors.append(f"Filename contains unsafe character: {char}")
                return False
                
        return True
    
    def _validate_zip_structure(self, zip_path: str) -> bool:
        """Validate ZIP internal structure and content"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Test ZIP integrity
                bad_file = zip_file.testzip()
                if bad_file:
                    self.validation_errors.append(f"Corrupt ZIP file: {bad_file}")
                    return False
                
                members = zip_file.namelist()
                
                # Check file count
                if len(members) > self.MAX_FILES:
                    self.validation_errors.append(f"Too many files: {len(members)} exceeds {self.MAX_FILES} limit")
                    return False
                
                # Check total extracted size
                total_size = sum(zip_file.getinfo(name).file_size for name in members)
                if total_size > self.MAX_EXTRACTED_SIZE:
                    size_mb = total_size / (1024 * 1024)
                    limit_mb = self.MAX_EXTRACTED_SIZE / (1024 * 1024)
                    self.validation_errors.append(
                        f"Extracted content too large: {size_mb:.1f}MB exceeds {limit_mb}MB limit"
                    )
                    return False
                
                # Validate each member
                case_folders = set()
                for member in members:
                    if not self._validate_zip_member(member):
                        return False
                        
                    # Track case folders
                    if '/' in member:
                        case_folder = member.split('/')[0]
                        case_folders.add(case_folder)
                
                # Ensure we have at least one case folder
                if not case_folders:
                    self.validation_errors.append("ZIP must contain at least one case folder")
                    return False
                
                logger.info(f"ZIP validation passed: {len(case_folders)} case folders, {len(members)} total files")
                return True
                
        except zipfile.BadZipFile:
            self.validation_errors.append("Invalid or corrupt ZIP file")
            return False
        except Exception as e:
            self.validation_errors.append(f"ZIP validation error: {str(e)}")
            return False
    
    def _validate_zip_member(self, member_path: str) -> bool:
        """Validate individual ZIP member"""
        # Check for zip slip attack
        if not self._check_zip_slip_safety(member_path):
            return False
            
        # Check path length
        if len(member_path) > self.MAX_PATH_LENGTH:
            self.validation_errors.append(f"Path too long: {member_path}")
            return False
        
        # Skip macOS system files - these are automatically added by macOS
        if self._is_system_file(member_path):
            return True
            
        # If it's a file (not directory), validate extension
        if not member_path.endswith('/'):
            file_ext = Path(member_path).suffix.lower()
            if file_ext and file_ext not in self.ALLOWED_EXTENSIONS:
                self.validation_errors.append(f"Unsupported file type: {file_ext} in {member_path}")
                return False
        
        return True
    
    def _check_zip_slip_safety(self, member_path: str) -> bool:
        """Prevent ZIP slip attacks"""
        # Normalize the path
        normalized = os.path.normpath(member_path)
        
        # Check for path traversal attempts
        if normalized.startswith('../') or '/../' in normalized or normalized.startswith('/'):
            self.validation_errors.append(f"Unsafe path detected: {member_path}")
            return False
            
        # Check for absolute paths
        if os.path.isabs(normalized):
            self.validation_errors.append(f"Absolute path not allowed: {member_path}")
            return False
            
        return True
    
    def _is_system_file(self, member_path: str) -> bool:
        """Check if file is a system file that should be ignored"""
        # Normalize path for checking
        path_lower = member_path.lower()
        
        # macOS system files
        if path_lower.endswith('.ds_store'):
            return True
        if '__macosx/' in path_lower:
            return True
        if member_path.startswith('._'):
            return True
            
        # Windows system files
        if path_lower.endswith('thumbs.db'):
            return True
        if path_lower.endswith('desktop.ini'):
            return True
            
        return False
    
    def get_case_folders(self, zip_path: str) -> List[str]:
        """Extract list of case folder names from ZIP"""
        case_folders = set()
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                for member in zip_file.namelist():
                    if '/' in member:
                        case_folder = member.split('/')[0]
                        # Skip hidden folders
                        if not case_folder.startswith('.'):
                            case_folders.add(case_folder)
            return sorted(list(case_folders))
        except Exception as e:
            logger.error(f"Error extracting case folder names: {e}")
            return []
    
    def sanitize_path(self, path: str) -> str:
        """Sanitize file/folder names for filesystem safety"""
        # Remove dangerous characters
        sanitized = "".join(c for c in path if c.isalnum() or c in (' ', '-', '_', '.'))
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "unnamed"
            
        return sanitized