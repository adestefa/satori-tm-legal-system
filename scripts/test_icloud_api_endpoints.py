#!/usr/bin/env python3
"""
iCloud API Endpoints Test Script
Tests the Dashboard API endpoints for iCloud functionality
"""

import sys
import json
import requests
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

def test_icloud_test_connection_endpoint():
    """Test 1: /api/icloud/test-connection endpoint"""
    print("=" * 60)
    print("TEST 1: iCloud Test Connection Endpoint")
    print("=" * 60)
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/icloud/test-connection", timeout=10)
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Message: {data.get('message', 'No message')}")
            if not data.get('success'):
                print(f"   - Error: {data.get('error', 'No error details')}")
        else:
            print(f"   - Error: HTTP {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
        
        return response.status_code in [200, 400]  # 400 is OK for missing credentials
    except Exception as e:
        print(f"❌ FAIL: Request failed: {e}")
        return False

def test_icloud_status_endpoint():
    """Test 2: /api/icloud/status endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: iCloud Status Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/icloud/status", timeout=10)
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Response keys: {list(data.keys())}")
            print(f"   - Configured: {data.get('configured', 'Unknown')}")
            print(f"   - Connection status: {data.get('connection_status', 'Unknown')}")
            print(f"   - Local case directory: {data.get('local_case_directory', 'Unknown')}")
        else:
            print(f"   - Error: HTTP {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ FAIL: Request failed: {e}")
        return False

def test_icloud_cases_endpoint():
    """Test 3: /api/icloud/cases endpoint"""
    print("\n" + "=" * 60)
    print("TEST 3: iCloud Cases List Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/icloud/cases", timeout=15)
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Message: {data.get('message', 'No message')}")
            
            if data.get('success'):
                case_folders = data.get('case_folders', [])
                print(f"   - Case folders found: {len(case_folders)}")
                for i, case in enumerate(case_folders[:3]):  # Show first 3
                    print(f"     {i+1}. {case.get('name')} ({case.get('file_count', 0)} files)")
            else:
                print(f"   - Error: {data.get('error', 'No error details')}")
        else:
            print(f"   - Error: HTTP {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
        
        return response.status_code in [200, 400]  # 400 is OK for missing credentials
    except Exception as e:
        print(f"❌ FAIL: Request failed: {e}")
        return False

def test_icloud_sync_all_endpoint():
    """Test 4: /api/icloud/sync (all cases) endpoint"""
    print("\n" + "=" * 60)
    print("TEST 4: iCloud Sync All Cases Endpoint")
    print("=" * 60)
    
    try:
        # This test should be quick since we don't have real credentials
        response = requests.post(f"{DASHBOARD_URL}/api/icloud/sync", timeout=15)
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Message: {data.get('message', 'No message')}")
            
            if data.get('success'):
                synced_cases = data.get('synced_cases', [])
                print(f"   - Cases synced: {len(synced_cases)}")
                errors = data.get('errors', [])
                print(f"   - Errors: {len(errors)}")
            else:
                print(f"   - Error: {data.get('error', 'No error details')}")
        else:
            print(f"   - Error: HTTP {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
        
        return response.status_code in [200, 400]  # 400 is OK for missing credentials
    except Exception as e:
        print(f"❌ FAIL: Request failed: {e}")
        return False

def test_icloud_sync_specific_endpoint():
    """Test 5: /api/icloud/sync/{case_name} endpoint"""
    print("\n" + "=" * 60)
    print("TEST 5: iCloud Sync Specific Case Endpoint")
    print("=" * 60)
    
    try:
        # Test with a dummy case name
        test_case_name = "TestCase"
        response = requests.post(f"{DASHBOARD_URL}/api/icloud/sync/{test_case_name}", timeout=15)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"   - Test case name: {test_case_name}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Message: {data.get('message', 'No message')}")
            
            if data.get('success'):
                downloaded_files = data.get('downloaded_files', [])
                print(f"   - Files downloaded: {len(downloaded_files)}")
                errors = data.get('errors', [])
                print(f"   - Errors: {len(errors)}")
            else:
                print(f"   - Error: {data.get('error', 'No error details')}")
        else:
            print(f"   - Error: HTTP {response.status_code}")
            print(f"   - Response: {response.text[:200]}...")
        
        return response.status_code in [200, 400, 404]  # Various errors are expected
    except Exception as e:
        print(f"❌ FAIL: Request failed: {e}")
        return False

def test_api_response_times():
    """Test 6: API response times"""
    print("\n" + "=" * 60)
    print("TEST 6: API Response Times")
    print("=" * 60)
    
    endpoints = [
        ("GET", "/api/icloud/status", "Status"),
        ("POST", "/api/icloud/test-connection", "Test Connection"),
        ("GET", "/api/icloud/cases", "List Cases")
    ]
    
    all_fast = True
    
    for method, endpoint, name in endpoints:
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(f"{DASHBOARD_URL}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{DASHBOARD_URL}{endpoint}", timeout=10)
            
            elapsed = time.time() - start_time
            
            print(f"   - {name}: {elapsed:.2f}s (HTTP {response.status_code})")
            
            if elapsed > 10:
                print(f"     ⚠️  Slow response (>{10}s)")
                all_fast = False
            else:
                print(f"     ✅ Good response time")
                
        except Exception as e:
            print(f"   - {name}: FAILED ({e})")
            all_fast = False
    
    return all_fast

def test_settings_integration():
    """Test 7: Settings integration"""
    print("\n" + "=" * 60)
    print("TEST 7: Settings Integration")
    print("=" * 60)
    
    try:
        # Get current settings
        response = requests.get(f"{DASHBOARD_URL}/api/settings", timeout=10)
        
        print(f"✅ Settings retrieval: HTTP {response.status_code}")
        
        if response.status_code == 200:
            settings = response.json()
            icloud_settings = settings.get('icloud', {})
            
            print(f"   - iCloud section exists: {bool(icloud_settings)}")
            print(f"   - Account configured: {bool(icloud_settings.get('account'))}")
            print(f"   - Password configured: {bool(icloud_settings.get('password'))}")
            print(f"   - Folder configured: {bool(icloud_settings.get('folder'))}")
            
            # Test if settings affect iCloud status
            status_response = requests.get(f"{DASHBOARD_URL}/api/icloud/status", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                configured = status_data.get('configured', False)
                print(f"   - iCloud configured in status: {configured}")
                
                has_credentials = bool(icloud_settings.get('account') and icloud_settings.get('password'))
                if configured == has_credentials:
                    print("   - ✅ Settings and status are consistent")
                    return True
                else:
                    print("   - ❌ Settings and status inconsistent")
                    return False
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ FAIL: Settings integration test failed: {e}")
        return False

def main():
    """Run all iCloud API endpoint tests"""
    print("🔧 ICLOUD API ENDPOINTS TESTS")
    print("Testing Dashboard iCloud API integration")
    print("=" * 60)
    
    # Check if dashboard is running
    if not check_dashboard_running():
        print("❌ FAIL: Dashboard is not running!")
        print("   Start with: ./dashboard/start.sh")
        return False
    
    print("✅ Dashboard is running")
    
    tests = [
        test_icloud_test_connection_endpoint,
        test_icloud_status_endpoint,
        test_icloud_cases_endpoint,
        test_icloud_sync_all_endpoint,
        test_icloud_sync_specific_endpoint,
        test_api_response_times,
        test_settings_integration
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
    print("API ENDPOINTS TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 ALL API ENDPOINT TESTS PASSED")
        return True
    else:
        print("⚠️  Some API endpoint tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)