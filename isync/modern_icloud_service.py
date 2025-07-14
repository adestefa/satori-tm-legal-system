#!/usr/bin/env python3
"""
Modern iCloud Service Implementation using icloudpd
Replaces obsolete pyicloud with cookie-based session authentication
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
            print("DEBUG: Importing icloudpd library...")
            from pyicloud import PyiCloudService
            from pyicloud.exceptions import PyiCloudException
            
            print("SUCCESS: icloudpd imported successfully")
            
            # Check for existing session cookies
            cookie_file = self.cookie_directory / f"{email}.cookies"
            session_file = self.cookie_directory / f"{email}.session"
            
            print("DEBUG: Checking for existing session...")
            print(f"   Cookie file: {cookie_file}")
            print(f"   Session file: {session_file}")
            print(f"   Cookie exists: {cookie_file.exists()}")
            print(f"   Session exists: {session_file.exists()}")
            
            # Try to use existing session first
            if cookie_file.exists() or session_file.exists():
                print("DEBUG: Found existing session, attempting reuse...")
                try:
                    # Try to create PyiCloud service with session directory
                    self.api = PyiCloudService(
                        apple_id=email,
                        cookie_directory=str(self.cookie_directory)
                    )
                    
                    # Test the connection
                    if hasattr(self.api, 'drive'):
                        test_result = self.api.drive.dir()
                        print("SUCCESS: Session reuse successful!")
                        self.authenticated = True
                        
                        return {
                            'success': True,
                            'message': 'Connected using existing session',
                            'account': email,
                            'session_reused': True,
                            'drive_accessible': True
                        }
                except Exception as session_e:
                    print(f"WARNING: Session reuse failed: {session_e}")
                    print("DEBUG: Will attempt fresh authentication...")
            
            # Fresh authentication required
            print("DEBUG: Performing fresh authentication...")
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
                
                print("SUCCESS: PyiCloudService created with cookie support")
                
                # Check if 2FA is required
                if self.api.requires_2fa:
                    print("INFO: 2FA required - this needs interactive input")
                    return {
                        'success': False,
                        'error': 'Two-factor authentication required. Please run initial setup interactively.',
                        'requires_2fa': True,
                        'interactive_setup_needed': True
                    }
                
                # Test drive access
                print("DEBUG: Testing drive access...")
                drive = self.api.drive
                root_contents = drive.dir()
                
                print(f"SUCCESS: Drive access successful - found {len(root_contents)} items")
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
                print(f"ERROR: PyiCloudException: {e}")
                
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
            print(f"ERROR: Failed to import icloudpd: {e}")
            return {
                'success': False,
                'error': f'icloudpd library not available: {str(e)}',
                'error_type': 'import_error'
            }
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            self.last_error = str(e)
            return {
                'success': False,
                'error': f'Unexpected connection error: {str(e)}',
                'error_type': 'unexpected_error'
            }
    
    def disconnect(self):
        """
        Disconnect from iCloud (session cookies remain for reuse)
        """
        self.api = None
        self.authenticated = False
        self.last_error = None
        logger.info("Disconnected from iCloud (session cookies preserved)")
    
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
    print("Testing Modern iCloud Service Implementation")
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
            print("ERROR: Missing credentials in settings file")
            return
        
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Cookie directory: {cookie_dir}")
        
        # Test connection
        service = ModerniCloudService(cookie_directory=cookie_dir)
        result = service.connect(email, password)
        
        print(f"\nConnection Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")

if __name__ == "__main__":
    main()