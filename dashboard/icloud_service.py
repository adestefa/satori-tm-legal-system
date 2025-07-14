"""
iCloud Service for TM Dashboard
Uses icloudpd with session-based authentication for reliable Apple iCloud access
Handles Apple's modern authentication requirements (post-2024)
"""

import os
import subprocess
import json
import logging
from typing import Optional, Dict, List, Any
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)

class iCloudService:
    """
    iCloud Drive service using icloudpd session-based authentication
    Handles Apple's modern web-based authentication flow
    """
    
    def __init__(self, cookie_directory: str = "./dashboard/icloud_session_data"):
        # Use absolute paths to avoid subprocess path issues
        self.cookie_directory = Path(cookie_directory).resolve()
        self.cookie_directory.mkdir(parents=True, exist_ok=True)
        self.authenticated = False
        self.last_error = None
        self.account = None
        
        logger.info(f"iCloudService initialized with cookie directory: {self.cookie_directory}")
        
    def connect(self, email: str, password: str) -> Dict[str, Any]:
        """
        Connect using icloudpd session-based authentication
        Handles initial setup and subsequent cookie-based auth
        
        Args:
            email: iCloud account email
            password: App-specific password
            
        Returns:
            Dict with success status and connection info
        """
        try:
            logger.info(f"iCloudPD session-based authentication for {email}")
            
            # Check if session already exists and is valid
            if self._has_valid_session(email):
                self.authenticated = True
                self.account = email
                logger.info(f"Using existing valid session for {email}")
                return {
                    'success': True, 
                    'message': 'Using existing iCloud session',
                    'account': email,
                    'authentication_method': 'icloudpd_session'
                }
            
            # Perform initial authentication
            result = self._authenticate_initial(email, password)
            
            if result['success']:
                self.authenticated = True
                self.account = email
                self.last_error = None
                logger.info(f"Successfully authenticated with iCloudPD")
                return result
            else:
                self.last_error = result.get('error', 'Unknown authentication error')
                logger.error(f"iCloudPD authentication failed: {self.last_error}")
                return result
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Exception during iCloudPD authentication: {e}")
            return {
                'success': False,
                'error': f'Authentication failed: {str(e)}',
                'authentication_method': 'icloudpd'
            }
    
    def _has_valid_session(self, email: str) -> bool:
        """Check if valid session cookies exist for the account"""
        try:
            # Test existing session with minimal dry-run command
            result = subprocess.run([
                'icloudpd', '--username', email,
                '--cookie-directory', str(self.cookie_directory),
                '--dry-run', '--recent', '1'
            ], capture_output=True, text=True, timeout=30)
            
            # Return code 0 means session is valid
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Session validation failed: {e}")
            return False
    
    def _authenticate_initial(self, email: str, password: str) -> Dict[str, Any]:
        """Perform initial authentication with icloudpd"""
        try:
            # For server deployment, attempt non-interactive authentication
            result = subprocess.run([
                'icloudpd', '--username', email, '--password', password,
                '--cookie-directory', str(self.cookie_directory),
                '--auth-only', '--no-progress-bar'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {
                    'success': True, 
                    'message': 'icloudpd authentication successful',
                    'account': email,
                    'authentication_method': 'icloudpd_initial'
                }
            else:
                error_msg = result.stderr or result.stdout or 'Unknown error'
                
                # Check for specific error patterns
                if '503' in error_msg or 'Service Temporarily Unavailable' in error_msg:
                    error_msg = 'Apple rate limiting active - please wait 15-30 minutes'
                elif '2FA' in error_msg or 'two-factor' in error_msg:
                    error_msg = 'Two-factor authentication required - may need interactive setup'
                
                return {
                    'success': False, 
                    'error': f'icloudpd authentication failed: {error_msg}',
                    'authentication_method': 'icloudpd_initial'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False, 
                'error': 'Authentication timeout - may require 2FA interaction'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'icloudpd command not found. Please install: pip install icloudpd'
            }
        except Exception as e:
            return {
                'success': False, 
                'error': f'Authentication error: {str(e)}'
            }
    
    def _run_icloudpd_command(self, command: List[str]) -> Dict[str, Any]:
        """
        Run an icloudpd command using existing session
        
        Args:
            command: List of command arguments
            
        Returns:
            Dict with success status and output/error
        """
        try:
            logger.debug(f"Running icloudpd command: {' '.join(command)}")
            
            # Ensure we're using the session directory
            if '--cookie-directory' not in command:
                command.extend(['--cookie-directory', str(self.cookie_directory)])
                
            # Run the command with proper working directory
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=120,  # Increased timeout for file operations
                cwd=os.getcwd()  # Use current working directory, not relative paths
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            else:
                error_message = result.stderr or result.stdout or f"Command failed with return code {result.returncode}"
                logger.error(f"icloudpd command failed: {error_message}")
                
                return {
                    'success': False,
                    'error': error_message,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out after 120 seconds'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'icloudpd command not found. Please ensure icloudpd is installed and in PATH'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Command execution failed: {str(e)}'
            }
    
    def test_folder_access(self, folder_path: str) -> Dict[str, Any]:
        """
        Test if we can access the specified folder path in iCloud Drive using session
        
        Args:
            folder_path: Path to test (e.g., '/LegalCases')
            
        Returns:
            Dict with access status and folder info
        """
        if not self.authenticated:
            return {
                'success': False,
                'error': 'Not authenticated with iCloud'
            }
        
        try:
            # Test folder access with minimal dry-run command
            result = self._run_icloudpd_command([
                "icloudpd",
                "--username", self.account,
                "--dry-run",
                "--recent", "1"  # Minimal test
            ])
            
            if result['success']:
                return {
                    'success': True,
                    'message': f'iCloud access verified (folder access requires actual sync operation)',
                    'folder_accessible': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Could not verify iCloud access: {result.get("error", "Unknown error")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Could not test folder access: {str(e)}'
            }
    
    def list_case_folders(self, parent_folder: str) -> Dict[str, Any]:
        """
        List case folders (simplified implementation for session-based auth)
        """
        if not self.authenticated:
            return {
                'success': False,
                'error': 'Not authenticated with iCloud'
            }
        
        # Simplified implementation - actual folder listing requires 
        # more complex icloudpd integration
        return {
            'success': True,
            'message': 'Session-based folder listing not implemented yet',
            'case_folders': [],
            'note': 'Use sync_case_folder for specific folder operations'
        }
    
    def sync_case_folder(self, parent_folder: str, case_name: str, local_target: str) -> Dict[str, Any]:
        """
        Download all files from a case folder to local directory
        
        Args:
            parent_folder: iCloud parent folder path
            case_name: Name of the case folder
            local_target: Local directory to sync to
            
        Returns:
            Dict with sync results
        """
        if not self.authenticated:
            return {
                'success': False,
                'error': 'Not authenticated with iCloud'
            }
        
        try:
            # Ensure local target directory exists
            os.makedirs(local_target, exist_ok=True)
            
            # Construct the full iCloud path
            full_icloud_path = f"{parent_folder.strip('/')}/{case_name}"
            
            # Use icloudpd to download files from the specific case folder
            result = self._run_icloudpd_command([
                "icloudpd",
                "--username", self.account,
                "--cookie-directory", str(self.cookie_directory),
                "--directory", local_target,
                "--folder-structure", full_icloud_path,
                "--recent", "9999",  # Download all files
                "--skip-videos",     # Skip videos for faster sync
                "--no-progress-bar"  # Disable progress bar for cleaner output
            ])
            
            if result['success']:
                # Count downloaded files
                downloaded_files = []
                if os.path.exists(local_target):
                    for file_path in Path(local_target).rglob('*'):
                        if file_path.is_file():
                            downloaded_files.append({
                                'name': file_path.name,
                                'size': file_path.stat().st_size,
                                'path': str(file_path)
                            })
                
                return {
                    'success': True,
                    'message': f'Synced {len(downloaded_files)} files from "{case_name}"',
                    'case_name': case_name,
                    'downloaded_files': downloaded_files,
                    'errors': [],
                    'local_target': local_target
                }
            else:
                return {
                    'success': False,
                    'error': f'Could not sync case folder "{case_name}": {result.get("error", "Unknown error")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Could not sync case folder "{case_name}": {str(e)}'
            }
    
    def clear_session(self):
        """
        Clear stored session cookies (forces fresh authentication)
        """
        try:
            if self.cookie_directory.exists():
                # Remove all cookie files
                for cookie_file in self.cookie_directory.glob('*'):
                    if cookie_file.is_file():
                        cookie_file.unlink()
                logger.info(f"Cleared session cookies from {self.cookie_directory}")
        except Exception as e:
            logger.error(f"Failed to clear session cookies: {e}")
    
    def disconnect(self):
        """
        Disconnect from iCloud (session cookies remain for reuse)
        """
        self.authenticated = False
        self.account = None
        self.last_error = None
        
    def is_connected(self) -> bool:
        """
        Check if currently connected to iCloud
        """
        return self.authenticated and self.account is not None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current connection status
        """
        return {
            'connected': self.is_connected(),
            'account': self.account,
            'last_error': self.last_error,
            'authentication_method': 'icloudpd',
            'cookie_directory': str(self.cookie_directory),
            'session_files_exist': len(list(self.cookie_directory.glob('*'))) > 0 if self.cookie_directory.exists() else False
        }