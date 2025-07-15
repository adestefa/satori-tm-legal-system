# upload_service/upload_handler.py
"""
Standalone Case Upload Handler

Provides secure, isolated case file upload processing with:
- ZIP file validation and extraction
- Integration with existing file watcher system
- Comprehensive error handling and logging
- Direct integration with test-data/sync-test-cases directory
"""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from fastapi import UploadFile, HTTPException
from .security import ZipSecurityValidator

# Configure logging
logger = logging.getLogger(__name__)

class StandaloneCaseUploader:
    """Self-contained case file upload processor"""
    
    def __init__(self, target_directory: str):
        """
        Initialize uploader with target directory
        
        Args:
            target_directory: Path to test-data/sync-test-cases
        """
        self.target_dir = target_directory
        self.security_validator = ZipSecurityValidator()
        self.temp_base_dir = tempfile.gettempdir()
        
        # Ensure target directory exists
        os.makedirs(self.target_dir, exist_ok=True)
        
        logger.info(f"Uploader initialized: target={self.target_dir}")
    
    async def process_upload(self, zip_file: UploadFile) -> Dict[str, Any]:
        """
        Main upload processing pipeline
        
        Args:
            zip_file: FastAPI UploadFile object
            
        Returns:
            Dict with success status, messages, and extracted case names
        """
        upload_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = None
        
        try:
            logger.info(f"Processing upload {upload_id}: {zip_file.filename}")
            
            # Read file content
            file_content = await zip_file.read()
            logger.info(f"Upload {upload_id}: Read {len(file_content)} bytes")
            
            # Security validation
            is_valid, errors = self.security_validator.validate_upload(
                file_content, zip_file.filename
            )
            
            if not is_valid:
                logger.warning(f"Upload {upload_id}: Security validation failed")
                for error in errors:
                    logger.warning(f"  - {error}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "File validation failed",
                        "details": errors
                    }
                )
            
            # Create temporary directory for processing
            temp_dir = tempfile.mkdtemp(prefix=f"upload_{upload_id}_")
            logger.info(f"Upload {upload_id}: Created temp dir {temp_dir}")
            
            # Save uploaded file temporarily
            temp_zip_path = os.path.join(temp_dir, "upload.zip")
            with open(temp_zip_path, 'wb') as f:
                f.write(file_content)
            
            # Extract ZIP file safely
            extract_dir = os.path.join(temp_dir, "extracted")
            case_folders = self._extract_zip_safely(temp_zip_path, extract_dir)
            
            if not case_folders:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "No valid case folders found in ZIP",
                        "details": ["ZIP must contain directories with legal documents"]
                    }
                )
            
            # Validate case structure
            validated_cases = self._validate_case_structure(extract_dir, case_folders)
            
            if not validated_cases:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "No valid cases found",
                        "details": ["Case folders must contain legal documents (.pdf, .docx, .txt)"]
                    }
                )
            
            # Move cases to target directory
            moved_cases = self._move_cases_to_target(extract_dir, validated_cases)
            
            # Success response
            result = {
                "success": True,
                "message": f"Successfully uploaded {len(moved_cases)} case(s)",
                "cases": moved_cases,
                "upload_id": upload_id,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Upload {upload_id}: Success - {len(moved_cases)} cases processed")
            return result
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
            
        except Exception as e:
            logger.error(f"Upload {upload_id}: Unexpected error - {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Upload processing failed",
                    "details": [f"Internal error: {str(e)}"]
                }
            )
            
        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Upload {upload_id}: Cleaned up temp dir")
                except Exception as e:
                    logger.warning(f"Upload {upload_id}: Cleanup failed - {str(e)}")
    
    def _extract_zip_safely(self, zip_path: str, extract_to: str) -> List[str]:
        """
        Safely extract ZIP file with security checks
        
        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract to
            
        Returns:
            List of extracted case folder names
        """
        os.makedirs(extract_to, exist_ok=True)
        case_folders = set()
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                for member in zip_file.namelist():
                    # Security check for each member
                    if not self.security_validator._check_zip_slip_safety(member):
                        continue
                    
                    # Skip system files during extraction
                    if self.security_validator._is_system_file(member):
                        continue
                        
                    # Extract member safely
                    member_path = os.path.join(extract_to, member)
                    
                    # Ensure parent directory exists
                    os.makedirs(os.path.dirname(member_path), exist_ok=True)
                    
                    # Extract file
                    if not member.endswith('/'):
                        with zip_file.open(member) as source, open(member_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                    
                    # Track case folders
                    if '/' in member:
                        case_folder = member.split('/')[0]
                        if not case_folder.startswith('.'):
                            case_folders.add(case_folder)
            
            logger.info(f"Extracted {len(case_folders)} case folders")
            return sorted(list(case_folders))
            
        except Exception as e:
            logger.error(f"ZIP extraction failed: {str(e)}")
            raise Exception(f"Failed to extract ZIP file: {str(e)}")
    
    def _validate_case_structure(self, extract_dir: str, case_folders: List[str]) -> List[Dict[str, Any]]:
        """
        Validate extracted case folder structure
        
        Args:
            extract_dir: Directory containing extracted files
            case_folders: List of case folder names
            
        Returns:
            List of validated case information
        """
        validated_cases = []
        
        for case_name in case_folders:
            case_path = os.path.join(extract_dir, case_name)
            
            if not os.path.isdir(case_path):
                logger.warning(f"Skipping non-directory: {case_name}")
                continue
            
            # Count legal documents
            legal_files = []
            try:
                for file_name in os.listdir(case_path):
                    file_path = os.path.join(case_path, file_name)
                    if os.path.isfile(file_path):
                        file_ext = Path(file_name).suffix.lower()
                        if file_ext in self.security_validator.ALLOWED_EXTENSIONS:
                            legal_files.append(file_name)
                
                if legal_files:
                    case_info = {
                        "name": case_name,
                        "files": legal_files,
                        "file_count": len(legal_files),
                        "path": case_path
                    }
                    validated_cases.append(case_info)
                    logger.info(f"Validated case '{case_name}': {len(legal_files)} files")
                else:
                    logger.warning(f"Case '{case_name}' has no legal documents")
                    
            except Exception as e:
                logger.error(f"Error validating case '{case_name}': {str(e)}")
                continue
        
        return validated_cases
    
    def _move_cases_to_target(self, extract_dir: str, validated_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Move validated cases to target directory
        
        Args:
            extract_dir: Directory containing extracted files
            validated_cases: List of validated case information
            
        Returns:
            List of successfully moved cases
        """
        moved_cases = []
        
        for case_info in validated_cases:
            case_name = case_info["name"]
            source_path = case_info["path"]
            target_path = os.path.join(self.target_dir, case_name)
            
            try:
                # Handle existing case directory
                if os.path.exists(target_path):
                    # Create backup name with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{case_name}_backup_{timestamp}"
                    backup_path = os.path.join(self.target_dir, backup_name)
                    
                    logger.info(f"Moving existing case '{case_name}' to backup: {backup_name}")
                    shutil.move(target_path, backup_path)
                
                # Move new case to target
                shutil.move(source_path, target_path)
                
                # Update case info with final path
                case_info["final_path"] = target_path
                case_info["status"] = "moved"
                moved_cases.append(case_info)
                
                logger.info(f"Successfully moved case '{case_name}' to {target_path}")
                
            except Exception as e:
                logger.error(f"Failed to move case '{case_name}': {str(e)}")
                case_info["status"] = "failed"
                case_info["error"] = str(e)
        
        return moved_cases
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """Get upload service statistics"""
        try:
            case_count = len([d for d in os.listdir(self.target_dir) 
                            if os.path.isdir(os.path.join(self.target_dir, d))])
            return {
                "target_directory": self.target_dir,
                "total_cases": case_count,
                "status": "ready"
            }
        except Exception as e:
            return {
                "target_directory": self.target_dir,
                "status": "error",
                "error": str(e)
            }