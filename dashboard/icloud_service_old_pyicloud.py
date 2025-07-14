"""
Modern iCloud Service for TM Dashboard
Updated to use cookie-based session authentication that works with current Apple security
"""

import os
import logging
from typing import Optional, Dict, List, Any
from pathlib import Path
import tempfile
import shutil
# Using PyiCloud with proper cookie-based session management (like icloudpd does)
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudException

logger = logging.getLogger(__name__)

class iCloudService:
    """
    Modern iCloud Drive service using cookie-based session authentication
    Updated to work with Apple's current security requirements
    """
    
    def __init__(self, cookie_directory: str = "./dashboard/icloud_session_data"):
        self.cookie_directory = Path(cookie_directory)
        self.api: Optional[PyiCloudService] = None
        self.drive = None
        self.authenticated = False
        self.last_error = None
        
        # Ensure cookie directory exists
        self.cookie_directory.mkdir(parents=True, exist_ok=True)
        
    def connect(self, email: str, password: str) -> Dict[str, Any]:
        """
        Connect to iCloud using modern cookie-based authentication
        
        Args:
            email: iCloud account email
            password: App-specific password
            
        Returns:
            Dict with success status and connection info
        """
        try:
            print(f"DEBUG: Modern iCloud connection attempt")
            print(f"   Email: '{email}'")
            print(f"   Password: '{password}'")
            print(f"   Cookie directory: {self.cookie_directory}")
            
            # Check for existing session cookies
            cookie_file = self.cookie_directory / f"{email}.cookies"
            session_file = self.cookie_directory / f"{email}.session"
            
            print(f"DEBUG: Session status - Cookie exists: {cookie_file.exists()}, Session exists: {session_file.exists()}")
            
            # Try to use existing session first
            if cookie_file.exists() or session_file.exists():
                print(f"DEBUG: Attempting session reuse...")
                try:
                    self.api = PyiCloudService(
                        apple_id=email,
                        cookie_directory=str(self.cookie_directory)
                    )
                    
                    # Test the connection
                    if hasattr(self.api, 'drive'):
                        test_result = self.api.drive.dir()
                        print(f"SUCCESS: Session reuse successful!")
                        self.authenticated = True
                        self.drive = self.api.drive
                        
                        return {
                            'success': True,
                            'message': 'Connected using existing session',
                            'account': email,
                            'session_reused': True,
                            'drive_accessible': True
                        }
                except Exception as session_e:
                    print(f"WARNING: Session reuse failed: {session_e}")
                    print(f"DEBUG: Will attempt fresh authentication...")
            
            # Fresh authentication required
            print(f"DEBUG: Performing fresh authentication...")
            
            self.api = PyiCloudService(
                apple_id=email,
                password=password,
                cookie_directory=str(self.cookie_directory)
            )
            
            print(f"SUCCESS: PyiCloudService created with cookie support")
            
            # Check if 2FA is required
            if self.api.requires_2fa:
                return {
                    'success': False,
                    'error': 'Two-factor authentication required. Please complete 2FA setup interactively first.',
                    'requires_2fa': True,
                    'interactive_setup_needed': True
                }
            
            # Test connection by accessing drive
            self.drive = self.api.drive
            
            # Verify we can access the drive
            try:
                root_contents = self.drive.dir()
                self.authenticated = True
                self.last_error = None
                
                print(f"SUCCESS: Drive access successful - found {len(root_contents)} items")
                
                return {
                    'success': True,
                    'message': 'Successfully connected to iCloud Drive with fresh authentication',
                    'account': email,
                    'session_reused': False,
                    'drive_accessible': True,
                    'root_items_count': len(root_contents)
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Could not access iCloud Drive: {str(e)}',
                    'drive_accessible': False
                }
                
        except PyiCloudException as e:
            self.last_error = str(e)
            logger.error(f"PyiCloudException during authentication: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            
            # Check for specific error types
            error_str = str(e).lower()
            if 'invalid email/password' in error_str or 'authentication failed' in error_str:
                return {
                    'success': False,
                    'error': f'iCloud authentication failed: {str(e)}. This usually means you need a fresh App-Specific Password. Generate one at https://appleid.apple.com/',
                    'requires_2fa': False,
                    'app_specific_password_needed': True
                }
            elif '2fa' in error_str or 'two-factor' in error_str:
                return {
                    'success': False,
                    'error': 'Two-factor authentication required. Please complete 2FA setup interactively first.',
                    'requires_2fa': True,
                    'interactive_setup_needed': True
                }
            
            return {
                'success': False,
                'error': f'iCloud authentication failed: {str(e)}',
                'requires_2fa': False
            }
        except Exception as e:
            self.last_error = str(e)
            return {
                'success': False,
                'error': f'Connection failed: {str(e)}',
                'requires_2fa': False
            }
    
    def test_folder_access(self, folder_path: str) -> Dict[str, Any]:
        """
        Test if we can access the specified folder path
        
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
            # Navigate to the folder
            current_dir = self.drive
            
            # Handle root folder
            if folder_path == '/' or folder_path == '':
                folders = current_dir.dir()
                return {
                    'success': True,
                    'message': f'Successfully accessed root folder',
                    'folder_count': len([f for f in folders if f.type == 'folder']),
                    'file_count': len([f for f in folders if f.type == 'file']),
                    'items': [f.name for f in folders[:10]]  # Show first 10 items
                }
            
            # Navigate to specified folder
            folder_parts = folder_path.strip('/').split('/')
            for part in folder_parts:
                if part:
                    found = False
                    for item in current_dir.dir():
                        if item.name == part and item.type == 'folder':
                            current_dir = item
                            found = True
                            break
                    
                    if not found:
                        return {
                            'success': False,
                            'error': f'Folder "{part}" not found in path "{folder_path}"'
                        }
            
            # List contents of target folder
            contents = current_dir.dir()
            folders = [f for f in contents if f.type == 'folder']
            files = [f for f in contents if f.type == 'file']
            
            return {
                'success': True,
                'message': f'Successfully accessed folder "{folder_path}"',
                'folder_count': len(folders),
                'file_count': len(files),
                'folders': [f.name for f in folders[:10]],  # Show first 10 folders
                'files': [f.name for f in files[:10]]  # Show first 10 files
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Could not access folder "{folder_path}": {str(e)}'
            }
    
    def list_case_folders(self, parent_folder: str) -> Dict[str, Any]:
        """
        List all potential case folders in the parent directory
        
        Args:
            parent_folder: Path to parent folder containing case folders
            
        Returns:
            Dict with folder list and metadata
        """
        if not self.authenticated:
            return {
                'success': False,
                'error': 'Not authenticated with iCloud'
            }
        
        try:
            # Navigate to parent folder
            current_dir = self.drive
            
            if parent_folder and parent_folder != '/':
                folder_parts = parent_folder.strip('/').split('/')
                for part in folder_parts:
                    if part:
                        found = False
                        for item in current_dir.dir():
                            if item.name == part and item.type == 'folder':
                                current_dir = item
                                found = True
                                break
                        
                        if not found:
                            return {
                                'success': False,
                                'error': f'Parent folder "{parent_folder}" not found'
                            }
            
            # List all folders (potential case folders)
            contents = current_dir.dir()
            case_folders = []
            
            for item in contents:
                if item.type == 'folder':
                    # Get folder info
                    try:
                        folder_contents = item.dir()
                        file_count = len([f for f in folder_contents if f.type == 'file'])
                        case_folders.append({
                            'name': item.name,
                            'file_count': file_count,
                            'has_files': file_count > 0
                        })
                    except:
                        # If we can't access the folder, still list it
                        case_folders.append({
                            'name': item.name,
                            'file_count': 0,
                            'has_files': False,
                            'access_error': True
                        })
            
            return {
                'success': True,
                'message': f'Found {len(case_folders)} potential case folders',
                'parent_folder': parent_folder,
                'case_folders': case_folders
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Could not list case folders: {str(e)}'
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
            # Navigate to parent folder
            current_dir = self.drive
            
            if parent_folder and parent_folder != '/':
                folder_parts = parent_folder.strip('/').split('/')
                for part in folder_parts:
                    if part:
                        found = False
                        for item in current_dir.dir():
                            if item.name == part and item.type == 'folder':
                                current_dir = item
                                found = True
                                break
                        
                        if not found:
                            return {
                                'success': False,
                                'error': f'Parent folder "{parent_folder}" not found'
                            }
            
            # Find the case folder
            case_folder = None
            for item in current_dir.dir():
                if item.name == case_name and item.type == 'folder':
                    case_folder = item
                    break
            
            if not case_folder:
                return {
                    'success': False,
                    'error': f'Case folder "{case_name}" not found'
                }
            
            # Create local target directory
            os.makedirs(local_target, exist_ok=True)
            
            # Download all files from case folder
            downloaded_files = []
            errors = []
            
            for item in case_folder.dir():
                if item.type == 'file':
                    try:
                        # Download file to local target
                        local_file_path = os.path.join(local_target, item.name)
                        
                        # Download file data
                        with item.open(stream=True) as response:
                            with open(local_file_path, 'wb') as f:
                                shutil.copyfileobj(response.raw, f)
                        
                        downloaded_files.append({
                            'name': item.name,
                            'size': os.path.getsize(local_file_path),
                            'path': local_file_path
                        })
                        
                    except Exception as e:
                        errors.append({
                            'file': item.name,
                            'error': str(e)
                        })
            
            return {
                'success': True,
                'message': f'Synced {len(downloaded_files)} files from "{case_name}"',
                'case_name': case_name,
                'downloaded_files': downloaded_files,
                'errors': errors,
                'local_target': local_target
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
                shutil.rmtree(self.cookie_directory)
                self.cookie_directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Cleared session cookies from {self.cookie_directory}")
        except Exception as e:
            logger.error(f"Failed to clear session cookies: {e}")
    
    def disconnect(self):
        """
        Disconnect from iCloud (session cookies remain for reuse)
        """
        self.api = None
        self.drive = None
        self.authenticated = False
        self.last_error = None
        
    def is_connected(self) -> bool:
        """
        Check if currently connected to iCloud
        """
        return self.authenticated and self.api is not None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current connection status
        """
        return {
            'connected': self.is_connected(),
            'last_error': self.last_error,
            'api_available': self.api is not None,
            'cookie_directory': str(self.cookie_directory),
            'session_files_exist': any(self.cookie_directory.glob('*.cookies')) or any(self.cookie_directory.glob('*.session'))
        }