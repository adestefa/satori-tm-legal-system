#!/usr/bin/env python3
"""
Basic iCloud Sync Feature Test Script
Tests fundamental iCloud connectivity and service initialization
"""

import sys
import os
import json
from pathlib import Path

# Add dashboard to Python path and handle virtual environment
dashboard_path = str(Path(__file__).parent.parent / "dashboard")
sys.path.insert(0, dashboard_path)

# Try to use venv if available
venv_python = Path(__file__).parent.parent / "dashboard" / "venv" / "bin" / "python"
if venv_python.exists():
    # Running outside venv, recommend using venv
    print("💡 Tip: For best results, run with dashboard virtual environment:")
    print(f"   source dashboard/venv/bin/activate && python3 {sys.argv[0]}")
    print()

from icloud_service import iCloudService

def test_icloud_service_initialization():
    """Test 1: iCloudService class initialization"""
    print("=" * 60)
    print("TEST 1: iCloudService Initialization")
    print("=" * 60)
    
    try:
        service = iCloudService()
        print("✅ PASS: iCloudService class instantiated successfully")
        print(f"   - Service created: {service}")
        print(f"   - Initial authenticated state: {service.authenticated}")
        print(f"   - Initial connection status: {service.is_connected()}")
        return True
    except Exception as e:
        print(f"❌ FAIL: Could not instantiate iCloudService: {e}")
        return False

def test_pyicloud_import():
    """Test 2: PyiCloud library availability"""
    print("\n" + "=" * 60)
    print("TEST 2: PyiCloud Library Import")
    print("=" * 60)
    
    try:
        import pyicloud
        from pyicloud import PyiCloudService
        from pyicloud.exceptions import PyiCloudException
        print("✅ PASS: PyiCloud library imported successfully")
        print(f"   - PyiCloud module: {pyicloud}")
        print(f"   - PyiCloudService class: {PyiCloudService}")
        print(f"   - PyiCloudException class: {PyiCloudException}")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Could not import PyiCloud: {e}")
        print("   - Install with: pip install pyicloud")
        return False

def test_service_methods():
    """Test 3: Service method availability"""
    print("\n" + "=" * 60)
    print("TEST 3: Service Method Availability")
    print("=" * 60)
    
    service = iCloudService()
    
    methods_to_test = [
        'connect',
        'test_folder_access', 
        'list_case_folders',
        'sync_case_folder',
        'disconnect',
        'is_connected',
        'get_status'
    ]
    
    all_methods_exist = True
    
    for method_name in methods_to_test:
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                print(f"✅ PASS: Method '{method_name}' exists and is callable")
            else:
                print(f"❌ FAIL: Method '{method_name}' exists but is not callable")
                all_methods_exist = False
        else:
            print(f"❌ FAIL: Method '{method_name}' does not exist")
            all_methods_exist = False
    
    return all_methods_exist

def test_invalid_credentials():
    """Test 4: Invalid credentials handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Invalid Credentials Handling")
    print("=" * 60)
    
    service = iCloudService()
    
    # Test with obviously invalid credentials
    result = service.connect("invalid@example.com", "invalid_password")
    
    if result['success']:
        print("❌ FAIL: Should not succeed with invalid credentials")
        return False
    else:
        print("✅ PASS: Correctly rejected invalid credentials")
        print(f"   - Error message: {result.get('error', 'No error message')}")
        print(f"   - Requires 2FA: {result.get('requires_2fa', False)}")
        return True

def test_status_methods():
    """Test 5: Status and disconnection methods"""
    print("\n" + "=" * 60)
    print("TEST 5: Status and Disconnection Methods")
    print("=" * 60)
    
    service = iCloudService()
    
    # Test initial status
    status = service.get_status()
    print(f"✅ Initial status: {status}")
    
    # Test is_connected before connection
    connected = service.is_connected()
    print(f"✅ Initial connection state: {connected}")
    
    if connected:
        print("❌ FAIL: Should not be connected initially")
        return False
    
    # Test disconnect (should work even if not connected)
    service.disconnect()
    print("✅ PASS: Disconnect method executed without error")
    
    # Test status after disconnect
    status_after = service.get_status()
    print(f"✅ Status after disconnect: {status_after}")
    
    return True

def main():
    """Run all basic iCloud service tests"""
    print("🔧 BASIC ICLOUD SYNC FEATURE TESTS")
    print("Testing fundamental iCloud service functionality")
    print("=" * 60)
    
    tests = [
        test_pyicloud_import,
        test_icloud_service_initialization, 
        test_service_methods,
        test_invalid_credentials,
        test_status_methods
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
    print("BASIC TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 ALL BASIC TESTS PASSED - iCloud service is ready for integration testing")
        return True
    else:
        print("⚠️  Some basic tests failed - fix these before proceeding to integration tests")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)