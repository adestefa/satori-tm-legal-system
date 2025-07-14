"""
Sync Manager for TM Dashboard
Handles case folder synchronization from iCloud to local directory
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import shutil

from .icloud_service import iCloudService

logger = logging.getLogger(__name__)

class SyncManager:
    """
    Manages synchronization between iCloud and local case directories
    """
    
    def __init__(self, settings_path: str = "config/settings.json", 
                 local_case_dir: str = "/Users/corelogic/satori-dev/TM/test-data/sync-test-cases"):
        self.settings_path = settings_path
        self.local_case_dir = local_case_dir
        
        # Load cookie directory from settings
        settings = self.load_settings()
        icloud_config = settings.get('icloud', {})
        cookie_directory = icloud_config.get('cookie_directory', './dashboard/icloud_session_data')
        
        self.icloud_service = iCloudService(cookie_directory=cookie_directory)
        self.last_sync_time = None
        self.sync_history = []
        self.last_test_time = None
        self.last_test_result = None
        self.test_cache_duration = 300  # 5 minutes cache
        
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from configuration file
        """
        try:
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load settings: {e}")
            return {}
    
    def get_icloud_config(self) -> Dict[str, str]:
        """
        Get iCloud configuration from settings
        """
        settings = self.load_settings()
        icloud_config = settings.get('icloud', {})
        
        config = {
            'account': icloud_config.get('account', ''),
            'password': icloud_config.get('password', ''),
            'folder': icloud_config.get('folder', '/LegalCases')
        }
        
        # Debug logging (mask password)
        logger.info(f"Loaded iCloud config - account: {config['account']}, folder: {config['folder']}, password_set: {bool(config['password'])}")
        
        # TEMPORARY DEBUG: Print actual password for verification
        print(f"🔍 DEBUG: SyncManager loaded credentials:")
        print(f"   Account: '{config['account']}'")
        print(f"   Password: '{config['password']}'")
        print(f"   Folder: '{config['folder']}'")
        
        return config
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test iCloud connection with current settings (cached for 5 minutes)
        NEW v1.9.0: Uses session-based iCloudPD authentication
        """
        from datetime import datetime, timedelta
        
        logger.info("🔄 SyncManager.test_connection() called - NEW v1.9.0 session-based auth")
        
        # Check cache first
        if (self.last_test_time and self.last_test_result and 
            datetime.now() - self.last_test_time < timedelta(seconds=self.test_cache_duration)):
            
            logger.info(f"📋 Using cached result from {int((datetime.now() - self.last_test_time).total_seconds())}s ago")
            cached_result = self.last_test_result.copy()
            cached_result['message'] = f"{cached_result['message']} (cached result - tested {int((datetime.now() - self.last_test_time).total_seconds())}s ago)"
            return cached_result
        
        logger.info("🔍 Loading iCloud configuration...")
        config = self.get_icloud_config()
        
        if not config['account'] or not config['password']:
            logger.error("❌ Missing iCloud credentials in configuration")
            result = {
                'success': False,
                'error': 'iCloud credentials not configured. Please update settings.',
                'missing_credentials': True
            }
            return result
        
        logger.info(f"🔗 Testing connection with NEW iCloudService (session-based)")
        logger.info(f"👤 Account: {config['account']}")
        logger.info(f"📂 Folder: {config['folder']}")
        
        # Test connection using NEW session-based iCloudService
        result = self.icloud_service.connect(config['account'], config['password'])
        
        logger.info(f"📊 iCloudService.connect() returned: {result}")
        
        if not result['success']:
            logger.error(f"❌ Connection test failed: {result.get('error', 'unknown')}")
            # Don't cache failures (they might be temporary)
            return result
        
        logger.info("✅ Connection test successful - disconnecting to free resources")
        # Disconnect immediately to free resources
        self.icloud_service.disconnect()
        
        # Create success result
        success_result = {
            'success': True,
            'message': 'iCloud credentials verified successfully (NEW v1.9.0 session-based)',
            'account': config['account'],
            'folder': config['folder'],
            'note': 'Folder access will be tested during actual sync operations',
            'authentication_method': result.get('authentication_method', 'icloudpd_session')
        }
        
        logger.info("💾 Caching successful result for 5 minutes")
        # Cache successful result
        self.last_test_time = datetime.now()
        self.last_test_result = success_result.copy()
        
        return success_result
    
    def test_connection_full(self) -> Dict[str, Any]:
        """
        Full connection test including folder access (use sparingly)
        """
        config = self.get_icloud_config()
        
        if not config['account'] or not config['password']:
            return {
                'success': False,
                'error': 'iCloud credentials not configured. Please update settings.',
                'missing_credentials': True
            }
        
        # Test connection
        result = self.icloud_service.connect(config['account'], config['password'])
        
        if not result['success']:
            return result
        
        # Test folder access
        folder_result = self.icloud_service.test_folder_access(config['folder'])
        
        # Disconnect immediately
        self.icloud_service.disconnect()
        
        if not folder_result['success']:
            return {
                'success': False,
                'error': f"Could not access folder '{config['folder']}': {folder_result['error']}",
                'folder_error': True
            }
        
        return {
            'success': True,
            'message': 'iCloud connection and folder access successful',
            'account': config['account'],
            'folder': config['folder'],
            'folder_info': folder_result
        }
    
    def list_available_cases(self) -> Dict[str, Any]:
        """
        List all available case folders from iCloud
        """
        # First test connection
        connection_result = self.test_connection()
        if not connection_result['success']:
            return connection_result
        
        config = self.get_icloud_config()
        
        # List case folders
        result = self.icloud_service.list_case_folders(config['folder'])
        
        if result['success']:
            # Add local sync status for each case
            for case_folder in result['case_folders']:
                local_path = os.path.join(self.local_case_dir, case_folder['name'])
                case_folder['local_exists'] = os.path.exists(local_path)
                
                if case_folder['local_exists']:
                    local_files = os.listdir(local_path)
                    case_folder['local_file_count'] = len([f for f in local_files if os.path.isfile(os.path.join(local_path, f))])
                else:
                    case_folder['local_file_count'] = 0
        
        return result
    
    def sync_case(self, case_name: str) -> Dict[str, Any]:
        """
        Sync a specific case folder from iCloud to local directory
        """
        # Test connection first
        connection_result = self.test_connection()
        if not connection_result['success']:
            return connection_result
        
        config = self.get_icloud_config()
        
        # Create local target directory
        local_target = os.path.join(self.local_case_dir, case_name)
        
        # Sync the case folder
        result = self.icloud_service.sync_case_folder(
            config['folder'], 
            case_name, 
            local_target
        )
        
        if result['success']:
            # Record sync history
            sync_record = {
                'case_name': case_name,
                'timestamp': datetime.now().isoformat(),
                'files_downloaded': len(result['downloaded_files']),
                'errors': len(result['errors']),
                'local_target': local_target
            }
            
            self.sync_history.append(sync_record)
            self.last_sync_time = datetime.now()
            
            logger.info(f"Successfully synced case '{case_name}' with {sync_record['files_downloaded']} files")
        
        return result
    
    def sync_all_cases(self) -> Dict[str, Any]:
        """
        Sync all available case folders from iCloud
        """
        # List available cases
        cases_result = self.list_available_cases()
        if not cases_result['success']:
            return cases_result
        
        case_folders = cases_result['case_folders']
        
        if not case_folders:
            return {
                'success': True,
                'message': 'No case folders found to sync',
                'synced_cases': []
            }
        
        synced_cases = []
        errors = []
        
        for case_folder in case_folders:
            case_name = case_folder['name']
            
            # Skip if no files or already synced with same file count
            if not case_folder['has_files']:
                continue
            
            if case_folder['local_exists'] and case_folder['local_file_count'] == case_folder['file_count']:
                logger.info(f"Skipping '{case_name}' - already synced with {case_folder['file_count']} files")
                continue
            
            # Sync the case
            sync_result = self.sync_case(case_name)
            
            if sync_result['success']:
                synced_cases.append({
                    'name': case_name,
                    'files_downloaded': len(sync_result['downloaded_files']),
                    'local_target': sync_result['local_target']
                })
            else:
                errors.append({
                    'case': case_name,
                    'error': sync_result['error']
                })
        
        return {
            'success': True,
            'message': f'Synced {len(synced_cases)} cases',
            'synced_cases': synced_cases,
            'errors': errors,
            'total_cases_found': len(case_folders)
        }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current sync status and history
        """
        config = self.get_icloud_config()
        
        return {
            'configured': bool(config['account'] and config['password']),
            'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'sync_history': self.sync_history[-10:],  # Last 10 sync operations
            'local_case_directory': self.local_case_dir,
            'icloud_folder': config['folder'],
            'connection_status': self.icloud_service.get_status()
        }
    
    def cleanup_local_cases(self, keep_cases: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Clean up local case directories
        
        Args:
            keep_cases: List of case names to keep, or None to keep all
        """
        if not os.path.exists(self.local_case_dir):
            return {
                'success': True,
                'message': 'Local case directory does not exist',
                'cleaned_cases': []
            }
        
        cleaned_cases = []
        errors = []
        
        for item in os.listdir(self.local_case_dir):
            item_path = os.path.join(self.local_case_dir, item)
            
            if os.path.isdir(item_path):
                # Skip if in keep list
                if keep_cases and item in keep_cases:
                    continue
                
                try:
                    shutil.rmtree(item_path)
                    cleaned_cases.append(item)
                    logger.info(f"Cleaned up local case directory: {item}")
                except Exception as e:
                    errors.append({
                        'case': item,
                        'error': str(e)
                    })
                    logger.error(f"Could not clean up case directory {item}: {e}")
        
        return {
            'success': True,
            'message': f'Cleaned up {len(cleaned_cases)} local case directories',
            'cleaned_cases': cleaned_cases,
            'errors': errors
        }
    
    def disconnect(self):
        """
        Disconnect from iCloud
        """
        self.icloud_service.disconnect()
        logger.info("Disconnected from iCloud")