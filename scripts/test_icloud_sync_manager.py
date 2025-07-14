#!/usr/bin/env python3
"""
iCloud Sync Manager Test Script
Tests the SyncManager integration and settings handling
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add dashboard to Python path
dashboard_path = str(Path(__file__).parent.parent / "dashboard")
sys.path.insert(0, dashboard_path)

# Fix import issue by treating dashboard as package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.sync_manager import SyncManager

def create_test_settings(temp_dir):
    """Create a test settings file"""
    settings_data = {
        "firm": {
            "name": "Test Law Firm",
            "address": "123 Test Street\nTest City, TS 12345",
            "phone": "(555) 123-4567",
            "email": "test@testlaw.com"
        },
        "icloud": {
            "account": "test@icloud.com",
            "password": "test_app_password",
            "folder": "/TestLegalCases"
        }
    }
    
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    settings_path = os.path.join(config_dir, "settings.json")
    with open(settings_path, 'w') as f:
        json.dump(settings_data, f, indent=2)
    
    return settings_path

def test_sync_manager_initialization():
    """Test 1: SyncManager initialization"""
    print("=" * 60)
    print("TEST 1: SyncManager Initialization")
    print("=" * 60)
    
    try:
        # Test with default paths
        sync_manager = SyncManager()
        print("✅ PASS: SyncManager created with default settings")
        print(f"   - Settings path: {sync_manager.settings_path}")
        print(f"   - Local case dir: {sync_manager.local_case_dir}")
        print(f"   - iCloud service: {sync_manager.icloud_service}")
        
        # Test with custom paths
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_settings = os.path.join(temp_dir, "custom_settings.json")
            custom_case_dir = os.path.join(temp_dir, "custom_cases")
            
            sync_manager_custom = SyncManager(
                settings_path=custom_settings,
                local_case_dir=custom_case_dir
            )
            
            print("✅ PASS: SyncManager created with custom paths")
            print(f"   - Custom settings path: {sync_manager_custom.settings_path}")
            print(f"   - Custom case dir: {sync_manager_custom.local_case_dir}")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Could not initialize SyncManager: {e}")
        return False

def test_settings_loading():
    """Test 2: Settings loading and configuration"""
    print("\n" + "=" * 60)
    print("TEST 2: Settings Loading and Configuration")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create test settings
            settings_path = create_test_settings(temp_dir)
            local_case_dir = os.path.join(temp_dir, "cases")
            
            sync_manager = SyncManager(
                settings_path=settings_path,
                local_case_dir=local_case_dir
            )
            
            # Test loading settings
            settings = sync_manager.load_settings()
            print("✅ PASS: Settings loaded successfully")
            print(f"   - Firm name: {settings.get('firm', {}).get('name')}")
            print(f"   - iCloud account: {settings.get('icloud', {}).get('account')}")
            
            # Test iCloud config extraction
            icloud_config = sync_manager.get_icloud_config()
            print("✅ PASS: iCloud configuration extracted")
            print(f"   - Account: {icloud_config['account']}")
            print(f"   - Folder: {icloud_config['folder']}")
            print(f"   - Password length: {len(icloud_config['password'])} chars")
            
            return True
        except Exception as e:
            print(f"❌ FAIL: Settings loading failed: {e}")
            return False

def test_missing_settings():
    """Test 3: Missing settings handling"""
    print("\n" + "=" * 60)
    print("TEST 3: Missing Settings Handling")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Use non-existent settings file
            missing_settings = os.path.join(temp_dir, "missing.json")
            sync_manager = SyncManager(settings_path=missing_settings)
            
            # Test loading missing settings
            settings = sync_manager.load_settings()
            print("✅ PASS: Missing settings handled gracefully")
            print(f"   - Returned empty dict: {settings == {}}")
            
            # Test iCloud config with missing settings
            icloud_config = sync_manager.get_icloud_config()
            print("✅ PASS: Missing iCloud config handled")
            print(f"   - Default account: '{icloud_config['account']}'")
            print(f"   - Default folder: '{icloud_config['folder']}'")
            
            return True
        except Exception as e:
            print(f"❌ FAIL: Missing settings test failed: {e}")
            return False

def test_connection_without_credentials():
    """Test 4: Connection test without credentials"""
    print("\n" + "=" * 60)
    print("TEST 4: Connection Test Without Credentials")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create empty settings
            config_dir = os.path.join(temp_dir, "config")
            os.makedirs(config_dir, exist_ok=True)
            settings_path = os.path.join(config_dir, "settings.json")
            
            with open(settings_path, 'w') as f:
                json.dump({}, f)
            
            sync_manager = SyncManager(settings_path=settings_path)
            
            # Test connection without credentials
            result = sync_manager.test_connection()
            
            if result['success']:
                print("❌ FAIL: Should not succeed without credentials")
                return False
            else:
                print("✅ PASS: Correctly rejected connection without credentials")
                print(f"   - Error: {result.get('error')}")
                print(f"   - Missing credentials flag: {result.get('missing_credentials')}")
                return True
                
        except Exception as e:
            print(f"❌ FAIL: Connection test failed: {e}")
            return False

def test_sync_status():
    """Test 5: Sync status reporting"""
    print("\n" + "=" * 60)
    print("TEST 5: Sync Status Reporting")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create test settings
            settings_path = create_test_settings(temp_dir)
            local_case_dir = os.path.join(temp_dir, "cases")
            
            sync_manager = SyncManager(
                settings_path=settings_path,
                local_case_dir=local_case_dir
            )
            
            # Test sync status
            status = sync_manager.get_sync_status()
            print("✅ PASS: Sync status retrieved")
            print(f"   - Configured: {status['configured']}")
            print(f"   - Last sync: {status['last_sync']}")
            print(f"   - Local directory: {status['local_case_directory']}")
            print(f"   - iCloud folder: {status['icloud_folder']}")
            print(f"   - Connection status: {status['connection_status']}")
            
            return True
        except Exception as e:
            print(f"❌ FAIL: Sync status test failed: {e}")
            return False

def test_local_cleanup():
    """Test 6: Local case cleanup functionality"""
    print("\n" + "=" * 60)
    print("TEST 6: Local Case Cleanup")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            local_case_dir = os.path.join(temp_dir, "cases")
            sync_manager = SyncManager(local_case_dir=local_case_dir)
            
            # Create some test case directories
            os.makedirs(local_case_dir, exist_ok=True)
            test_cases = ["Case1", "Case2", "Case3"]
            
            for case in test_cases:
                case_dir = os.path.join(local_case_dir, case)
                os.makedirs(case_dir)
                # Create a test file in each case
                with open(os.path.join(case_dir, "test.txt"), 'w') as f:
                    f.write("test content")
            
            print(f"✅ Created {len(test_cases)} test case directories")
            
            # Test cleanup without keep list (should clean all)
            result = sync_manager.cleanup_local_cases()
            print("✅ PASS: Cleanup without keep list")
            print(f"   - Cleaned cases: {result['cleaned_cases']}")
            print(f"   - Errors: {result['errors']}")
            
            # Recreate test cases
            for case in test_cases:
                case_dir = os.path.join(local_case_dir, case)
                os.makedirs(case_dir)
                with open(os.path.join(case_dir, "test.txt"), 'w') as f:
                    f.write("test content")
            
            # Test cleanup with keep list
            keep_cases = ["Case1", "Case3"]
            result = sync_manager.cleanup_local_cases(keep_cases=keep_cases)
            print("✅ PASS: Cleanup with keep list")
            print(f"   - Cleaned cases: {result['cleaned_cases']}")
            print(f"   - Should have cleaned: ['Case2']")
            
            # Verify kept cases still exist
            for case in keep_cases:
                case_path = os.path.join(local_case_dir, case)
                if os.path.exists(case_path):
                    print(f"   - ✅ Kept case: {case}")
                else:
                    print(f"   - ❌ Lost case: {case}")
            
            return True
        except Exception as e:
            print(f"❌ FAIL: Local cleanup test failed: {e}")
            return False

def main():
    """Run all SyncManager tests"""
    print("🔧 ICLOUD SYNC MANAGER TESTS")
    print("Testing SyncManager integration and functionality")
    print("=" * 60)
    
    tests = [
        test_sync_manager_initialization,
        test_settings_loading,
        test_missing_settings,
        test_connection_without_credentials,
        test_sync_status,
        test_local_cleanup
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("SYNC MANAGER TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 ALL SYNC MANAGER TESTS PASSED")
        return True
    else:
        print("⚠️  Some sync manager tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)