#!/usr/bin/env python3
"""
Modern iCloud Service Implementation using icloudpd
Replaces obsolete pyicloud with cookie-based session authentication

Based on research findings that pyicloud is broken due to Apple's evolving security.
icloudpd uses modern authentication methods that work with current Apple APIs.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# Add shared schema to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared-schema'))

logger = logging.getLogger(__name__)

class ModerniCloudService:
    """
    Modern iCloud Drive service using icloudpd library
    
    Key differences from old PyiCloud approach:
    1. Uses cookie-based session authentication
    2. Handles modern 2FA requirements
    3. Requires initial interactive login, then automated
    4. More reliable with current Apple security
    """
    
    def __init__(self, cookie_directory: str = "./icloud_session_data"):
        self.cookie_directory = Path(cookie_directory)
        self.authenticated = False
        self.last_error = None
        self.api = None
        
        # Ensure cookie directory exists
        self.cookie_directory.mkdir(parents=True, exist_ok=True)
        
    def connect(self, email: str, password: str) -> Dict[str, Any]:
        """
        Connect to iCloud using modern cookie-based authentication
        
        Args:
            email: iCloud account email
            password: App-specific password (still needed for initial auth)
            
        Returns:
            Dict with success status and connection info
        """
        try:
            # Import icloudpd components
            print(f"= Importing icloudpd library...")
            from icloudpd.base import main as icloudpd_main
            from pyicloud import PyiCloudService
            from pyicloud.exceptions import PyiCloudException
            
            print(f" icloudpd imported successfully")
            
            # Check for existing session cookies
            cookie_file = self.cookie_directory / f"{email}.cookies"
            session_file = self.cookie_directory / f"{email}.session"
            
            print(f"= Checking for existing session...")
            print(f"   Cookie file: {cookie_file}")
            print(f"   Session file: {session_file}")
            print(f"   Cookie exists: {cookie_file.exists()}")
            print(f"   Session exists: {session_file.exists()}")
            
            # Try to use existing session first
            if cookie_file.exists() or session_file.exists():
                print(f"=Â Found existing session, attempting reuse...")
                try:
                    # Try to create PyiCloud service with session directory
                    self.api = PyiCloudService(
                        apple_id=email,
                        cookie_directory=str(self.cookie_directory)
                    )
                    
                    # Test the connection
                    if hasattr(self.api, 'drive'):
                        test_result = self.api.drive.dir()
                        print(f" Session reuse successful!")
                        self.authenticated = True
                        
                        return {
                            'success': True,
                            'message': 'Connected using existing session',
                            'account': email,
                            'session_reused': True,
                            'drive_accessible': True
                        }
                except Exception as session_e:
                    print(f"  Session reuse failed: {session_e}")
                    print(f"= Will attempt fresh authentication...")
            
            # Fresh authentication required
            print(f"= Performing fresh authentication...")
            print(f"   Email: '{email}'")
            print(f"   Password: '{password}'")
            print(f"   Cookie directory: {self.cookie_directory}")
            
            try:
                # Create new PyiCloud service with cookie persistence
                self.api = PyiCloudService(
                    apple_id=email,
                    password=password,
                    cookie_directory=str(self.cookie_directory)
                )
                
                print(f" PyiCloudService created with cookie support")
                
                # Check if 2FA is required
                if self.api.requires_2fa:
                    print(f"= 2FA required - this needs interactive input")
                    return {
                        'success': False,
                        'error': 'Two-factor authentication required. Please run initial setup interactively.',
                        'requires_2fa': True,
                        'interactive_setup_needed': True
                    }
                
                # Test drive access
                print(f"= Testing drive access...")
                drive = self.api.drive
                root_contents = drive.dir()
                
                print(f" Drive access successful - found {len(root_contents)} items")
                self.authenticated = True
                self.last_error = None
                
                return {
                    'success': True,
                    'message': 'Successfully connected to iCloud Drive with fresh authentication',
                    'account': email,
                    'session_reused': False,
                    'drive_accessible': True,
                    'root_items_count': len(root_contents)
                }
                
            except PyiCloudException as e:
                error_str = str(e).lower()
                print(f"L PyiCloudException: {e}")
                
                if 'invalid email/password' in error_str:
                    return {
                        'success': False,
                        'error': f'Authentication failed: {str(e)}. Verify app-specific password is correct.',
                        'error_type': 'authentication_failed'
                    }
                elif '2fa' in error_str or 'two-factor' in error_str:
                    return {
                        'success': False,
                        'error': 'Two-factor authentication required. Please run initial setup interactively.',
                        'requires_2fa': True,
                        'interactive_setup_needed': True
                    }
                else:
                    return {
                        'success': False,
                        'error': f'iCloud connection failed: {str(e)}',
                        'error_type': 'pyicloud_exception'
                    }
                
        except ImportError as e:
            print(f"L Failed to import icloudpd: {e}")
            return {
                'success': False,
                'error': f'icloudpd library not available: {str(e)}',
                'error_type': 'import_error'
            }
        except Exception as e:
            print(f"L Unexpected error: {e}")
            self.last_error = str(e)
            return {
                'success': False,
                'error': f'Unexpected connection error: {str(e)}',
                'error_type': 'unexpected_error'
            }
    
    def test_folder_access(self, folder_path: str) -> Dict[str, Any]:
        """
        Test access to specific folder path
        """
        if not self.authenticated or not self.api:
            return {
                'success': False,
                'error': 'Not authenticated with iCloud'
            }
        
        try:
            drive = self.api.drive
            
            # Handle root folder
            if folder_path == '/' or folder_path == '':
                items = drive.dir()
                return {
                    'success': True,
                    'message': f'Successfully accessed root folder',
                    'folder_count': len([item for item in items if item.type == 'folder']),
                    'file_count': len([item for item in items if item.type == 'file']),
                    'items': [item.name for item in items[:10]]
                }
            
            # Navigate to specific folder
            current_dir = drive
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
            
            # List contents
            contents = current_dir.dir()
            folders = [item for item in contents if item.type == 'folder']
            files = [item for item in contents if item.type == 'file']
            
            return {
                'success': True,
                'message': f'Successfully accessed folder "{folder_path}"',
                'folder_count': len(folders),
                'file_count': len(files),
                'folders': [f.name for f in folders[:10]],
                'files': [f.name for f in files[:10]]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Could not access folder "{folder_path}": {str(e)}'
            }
    
    def list_case_folders(self, parent_folder: str) -> Dict[str, Any]:
        """
        List all potential case folders in parent directory
        """
        if not self.authenticated or not self.api:
            return {
                'success': False,
                'error': 'Not authenticated with iCloud'
            }
        
        try:
            drive = self.api.drive
            current_dir = drive
            
            # Navigate to parent folder
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
                    try:
                        folder_contents = item.dir()
                        file_count = len([f for f in folder_contents if f.type == 'file'])
                        case_folders.append({
                            'name': item.name,
                            'file_count': file_count,
                            'has_files': file_count > 0
                        })
                    except:
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
        Download all files from case folder to local directory
        """
        if not self.authenticated or not self.api:
            return {
                'success': False,
                'error': 'Not authenticated with iCloud'
            }
        
        try:
            drive = self.api.drive
            current_dir = drive
            
            # Navigate to parent folder
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
            
            # Find case folder
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
            
            # Download files
            downloaded_files = []
            errors = []
            
            for item in case_folder.dir():
                if item.type == 'file':
                    try:
                        local_file_path = os.path.join(local_target, item.name)
                        
                        # Download file
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
    
    def disconnect(self):
        """
        Disconnect from iCloud (session cookies remain for reuse)
        """
        self.api = None
        self.authenticated = False
        self.last_error = None
        logger.info("Disconnected from iCloud (session cookies preserved)")
    
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

def main():
    """
    Test the modern iCloud service implementation
    """
    print("=" * 80)
    print(">ê Testing Modern iCloud Service Implementation")
    print("=" * 80)
    
    # Load credentials from settings
    settings_path = "../dashboard/config/settings.json"
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        icloud_config = settings.get('icloud', {})
        email = icloud_config.get('account', '')
        password = icloud_config.get('password', '')
        cookie_dir = icloud_config.get('cookie_directory', './icloud_session_data')
        
        if not email or not password:
            print(f"L Missing credentials in settings file")
            return
        
        print(f"=ç Email: {email}")
        print(f"= Password: {password}")
        print(f"=Â Cookie directory: {cookie_dir}")
        
        # Test connection
        service = ModerniCloudService(cookie_directory=cookie_dir)
        result = service.connect(email, password)
        
        print(f"\n=Ê Connection Result:")
        print(json.dumps(result, indent=2))
        
        if result['success']:
            print(f"\n= Testing folder access...")
            folder_result = service.test_folder_access('/LegalCases')
            print(json.dumps(folder_result, indent=2))
        
    except Exception as e:
        print(f"L Test failed: {e}")

if __name__ == "__main__":
    main()