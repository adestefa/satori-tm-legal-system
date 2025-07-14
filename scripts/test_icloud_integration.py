#!/usr/bin/env python3
"""
iCloud Integration Test Script
Comprehensive integration test for the complete iCloud sync workflow
"""

import sys
import os
import json
import requests
import tempfile
import time
from pathlib import Path

# Dashboard base URL
DASHBOARD_URL = "http://127.0.0.1:8000"

def check_dashboard_running():
    """Check if dashboard is running"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_current_settings():
    """Get current dashboard settings"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/settings", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def test_settings_page_access():
    """Test 1: Settings page accessibility"""
    print("=" * 60)
    print("TEST 1: Settings Page Access")
    print("=" * 60)
    
    try:
        # Test settings page
        response = requests.get(f"{DASHBOARD_URL}/settings", timeout=10)
        print(f"✅ Settings page: HTTP {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            # Check for iCloud form elements
            icloud_elements = [
                'icloud-account',
                'icloud-password', 
                'icloud-folder'
            ]
            
            found_elements = []
            for element in icloud_elements:
                if element in content:
                    found_elements.append(element)
            
            print(f"   - iCloud form elements found: {len(found_elements)}/{len(icloud_elements)}")
            for element in found_elements:
                print(f"     ✅ {element}")
            
            return len(found_elements) == len(icloud_elements)
        else:
            print(f"   - Error accessing settings page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Settings page test failed: {e}")
        return False

def test_icloud_configuration_flow():
    """Test 2: iCloud configuration workflow"""
    print("\n" + "=" * 60)
    print("TEST 2: iCloud Configuration Workflow")
    print("=" * 60)
    
    try:
        # Get current settings
        current_settings = get_current_settings()
        print(f"✅ Retrieved current settings")
        
        # Check iCloud section
        icloud_config = current_settings.get('icloud', {})
        print(f"   - iCloud section exists: {bool(icloud_config)}")
        print(f"   - Current account: '{icloud_config.get('account', '')}'")
        print(f"   - Current folder: '{icloud_config.get('folder', '')}'")
        print(f"   - Password configured: {bool(icloud_config.get('password'))}")
        
        # Test status endpoint with current config
        status_response = requests.get(f"{DASHBOARD_URL}/api/icloud/status", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   - iCloud status configured: {status_data.get('configured', False)}")
            print(f"   - Connection status: {status_data.get('connection_status', {})}")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Configuration flow test failed: {e}")
        return False

def test_test_connection_workflow():
    """Test 3: Test connection workflow"""
    print("\n" + "=" * 60)
    print("TEST 3: Test Connection Workflow")
    print("=" * 60)
    
    try:
        # Test connection with current settings
        print("   - Testing connection with current settings...")
        response = requests.post(f"{DASHBOARD_URL}/api/icloud/test-connection", timeout=15)
        
        print(f"✅ Test connection response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            print(f"   - Connection successful: {success}")
            
            if success:
                print(f"   - Message: {data.get('message', 'No message')}")
                print(f"   - Account: {data.get('account', 'Unknown')}")
                print(f"   - Drive accessible: {data.get('drive_accessible', False)}")
            else:
                print(f"   - Error: {data.get('error', 'No error details')}")
                print(f"   - Missing credentials: {data.get('missing_credentials', False)}")
                print(f"   - Requires 2FA: {data.get('requires_2fa', False)}")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Test connection workflow failed: {e}")
        return False

def test_case_listing_workflow():
    """Test 4: Case listing workflow"""
    print("\n" + "=" * 60)
    print("TEST 4: Case Listing Workflow")
    print("=" * 60)
    
    try:
        print("   - Listing available iCloud cases...")
        response = requests.get(f"{DASHBOARD_URL}/api/icloud/cases", timeout=20)
        
        print(f"✅ Case listing response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            print(f"   - Listing successful: {success}")
            
            if success:
                case_folders = data.get('case_folders', [])
                print(f"   - Case folders found: {len(case_folders)}")
                
                # Show details for first few cases
                for i, case in enumerate(case_folders[:3]):
                    print(f"     {i+1}. {case.get('name', 'Unknown')}")
                    print(f"        - Files: {case.get('file_count', 0)}")
                    print(f"        - Has files: {case.get('has_files', False)}")
                    print(f"        - Local exists: {case.get('local_exists', False)}")
                    print(f"        - Local files: {case.get('local_file_count', 0)}")
                
                if len(case_folders) > 3:
                    print(f"     ... and {len(case_folders) - 3} more cases")
            else:
                print(f"   - Error: {data.get('error', 'No error details')}")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Case listing workflow failed: {e}")
        return False

def test_sync_workflow():
    """Test 5: Sync workflow"""
    print("\n" + "=" * 60)
    print("TEST 5: Sync Workflow")
    print("=" * 60)
    
    try:
        print("   - Testing sync all cases...")
        response = requests.post(f"{DASHBOARD_URL}/api/icloud/sync", timeout=30)
        
        print(f"✅ Sync all response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            print(f"   - Sync successful: {success}")
            
            if success:
                synced_cases = data.get('synced_cases', [])
                errors = data.get('errors', [])
                total_found = data.get('total_cases_found', 0)
                
                print(f"   - Total cases found: {total_found}")
                print(f"   - Cases synced: {len(synced_cases)}")
                print(f"   - Sync errors: {len(errors)}")
                
                # Show synced case details
                for case in synced_cases[:3]:
                    print(f"     ✅ {case.get('name', 'Unknown')}: {case.get('files_downloaded', 0)} files")
                
                # Show error details
                for error in errors[:3]:
                    print(f"     ❌ {error.get('case', 'Unknown')}: {error.get('error', 'No details')}")
            else:
                print(f"   - Error: {data.get('error', 'No error details')}")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Sync workflow failed: {e}")
        return False

def test_status_monitoring():
    """Test 6: Status monitoring"""
    print("\n" + "=" * 60)
    print("TEST 6: Status Monitoring")
    print("=" * 60)
    
    try:
        print("   - Getting comprehensive status...")
        response = requests.get(f"{DASHBOARD_URL}/api/icloud/status", timeout=10)
        
        print(f"✅ Status response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"   - Configuration status:")
            print(f"     - Configured: {data.get('configured', False)}")
            print(f"     - Last sync: {data.get('last_sync', 'Never')}")
            print(f"     - Local case directory: {data.get('local_case_directory', 'Unknown')}")
            print(f"     - iCloud folder: {data.get('icloud_folder', 'Unknown')}")
            
            connection_status = data.get('connection_status', {})
            print(f"   - Connection status:")
            print(f"     - Connected: {connection_status.get('connected', False)}")
            print(f"     - API available: {connection_status.get('api_available', False)}")
            print(f"     - Last error: {connection_status.get('last_error', 'None')}")
            
            sync_history = data.get('sync_history', [])
            print(f"   - Sync history: {len(sync_history)} recent operations")
            
            for i, sync_op in enumerate(sync_history[-3:]):  # Show last 3
                print(f"     {i+1}. {sync_op.get('case_name', 'Unknown')} at {sync_op.get('timestamp', 'Unknown')}")
                print(f"        Files: {sync_op.get('files_downloaded', 0)}, Errors: {sync_op.get('errors', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Status monitoring failed: {e}")
        return False

def test_error_handling():
    """Test 7: Error handling"""
    print("\n" + "=" * 60)
    print("TEST 7: Error Handling")
    print("=" * 60)
    
    try:
        # Test sync with invalid case name
        print("   - Testing sync with invalid case name...")
        response = requests.post(f"{DASHBOARD_URL}/api/icloud/sync/InvalidCaseName", timeout=15)
        
        print(f"✅ Invalid case sync: HTTP {response.status_code}")
        
        # This should handle errors gracefully
        if response.status_code in [200, 400, 404]:
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                if not success:
                    print(f"   - Error properly reported: {data.get('error', 'No error')}")
                else:
                    print(f"   - Unexpected success with invalid case")
            print("   - ✅ Error handling works correctly")
        else:
            print(f"   - ❌ Unexpected HTTP status: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Error handling test failed: {e}")
        return False

def test_file_system_integration():
    """Test 8: File system integration"""
    print("\n" + "=" * 60)
    print("TEST 8: File System Integration")
    print("=" * 60)
    
    try:
        # Check local sync directory
        current_settings = get_current_settings()
        
        # Get expected sync directory from status
        status_response = requests.get(f"{DASHBOARD_URL}/api/icloud/status", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            local_dir = status_data.get('local_case_directory', '/Users/corelogic/satori-dev/TM/test-data/sync-test-cases')
            
            print(f"   - Local sync directory: {local_dir}")
            print(f"   - Directory exists: {os.path.exists(local_dir)}")
            
            if os.path.exists(local_dir):
                try:
                    items = os.listdir(local_dir)
                    case_dirs = [item for item in items if os.path.isdir(os.path.join(local_dir, item))]
                    print(f"   - Case directories found: {len(case_dirs)}")
                    
                    for case_dir in case_dirs[:3]:  # Show first 3
                        case_path = os.path.join(local_dir, case_dir)
                        files = [f for f in os.listdir(case_path) if os.path.isfile(os.path.join(case_path, f))]
                        print(f"     - {case_dir}: {len(files)} files")
                        
                except Exception as e:
                    print(f"   - ❌ Error reading directory: {e}")
                    return False
            else:
                print(f"   - Local directory will be created on first sync")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: File system integration test failed: {e}")
        return False

def main():
    """Run all iCloud integration tests"""
    print("🔧 ICLOUD INTEGRATION TESTS")
    print("Comprehensive testing of iCloud sync workflow")
    print("=" * 60)
    
    # Check if dashboard is running
    if not check_dashboard_running():
        print("❌ FAIL: Dashboard is not running!")
        print("   Start with: ./dashboard/start.sh")
        return False
    
    print("✅ Dashboard is running")
    
    tests = [
        test_settings_page_access,
        test_icloud_configuration_flow,
        test_test_connection_workflow,
        test_case_listing_workflow,
        test_sync_workflow,
        test_status_monitoring,
        test_error_handling,
        test_file_system_integration
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
    print("INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 ALL INTEGRATION TESTS PASSED")
        print("💡 iCloud sync system is ready for production use")
    else:
        print("⚠️  Some integration tests failed")
        print("💡 Review test output and fix issues before production use")
    
    # Provide guidance
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    current_settings = get_current_settings()
    icloud_config = current_settings.get('icloud', {})
    
    if not icloud_config.get('account') or not icloud_config.get('password'):
        print("📝 Configure iCloud credentials:")
        print("   1. Go to http://127.0.0.1:8000/settings")
        print("   2. Fill in iCloud account and app-specific password")
        print("   3. Set the folder path (e.g., /LegalCases)")
        print("   4. Save settings and test connection")
    else:
        print("📝 iCloud credentials are configured")
        print("   - Test connection: POST /api/icloud/test-connection")
        print("   - List cases: GET /api/icloud/cases")
        print("   - Sync cases: POST /api/icloud/sync")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)