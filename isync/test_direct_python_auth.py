#!/usr/bin/env python3
"""
Direct Python iCloud Authentication Test
Uses the Python API directly instead of command line
"""

import sys
import os
from pathlib import Path

# Add dashboard to Python path
dashboard_path = Path(__file__).parent / "dashboard"
sys.path.insert(0, str(dashboard_path))

def test_direct_python_auth():
    """Test authentication using Python API directly"""
    print("=" * 50)
    print("DIRECT PYTHON iCLOUD AUTHENTICATION TEST")
    print("=" * 50)
    
    account = "anthony.destefano@gmail.com"
    password = "btzp-duba-fpyf-fviy"
    
    print(f"Account: {account}")
    print(f"Password: {password}")
    print()
    
    try:
        # Try using the updated iCloud service directly
        from icloud_service import iCloudService
        
        print("🔄 Testing with updated iCloudService (icloudpd-based)...")
        service = iCloudService()
        result = service.connect(account, password)
        
        if result['success']:
            print("✅ SUCCESS! iCloudPD-based authentication working!")
            print(f"   Message: {result['message']}")
            print(f"   Method: {result['authentication_method']}")
            return True
        else:
            print(f"❌ iCloudPD failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ iCloudPD exception: {e}")
    
    # Try direct pyicloud as fallback
    try:
        print("\n🔄 Testing with direct pyicloud import...")
        
        # Import the actual pyicloud library that's installed
        import sys
        venv_path = "/Users/corelogic/satori-dev/TM/dashboard/venv/lib/python3.13/site-packages"
        sys.path.insert(0, venv_path)
        
        from pyicloud import PyiCloudService
        
        print("📦 Creating PyiCloudService instance...")
        api = PyiCloudService(apple_id=account, password=password)
        
        print("✅ SUCCESS! Direct PyiCloud authentication working!")
        print(f"   Authenticated user: {api.apple_id}")
        
        if api.requires_2fa:
            print("🔐 2FA required but authentication succeeded")
        else:
            print("🎉 Full authentication without 2FA prompt")
            
        return True
        
    except Exception as e:
        print(f"❌ Direct PyiCloud failed: {e}")
        
        # Check if it's the same 503 error
        if "503" in str(e) or "Service Temporarily Unavailable" in str(e):
            print("🚨 Getting same 503 error with direct Python - this suggests Apple server issue")
        elif "20101" in str(e) or "Invalid email/password" in str(e):
            print("🚨 Password rejected - app-specific password may be invalid")
        else:
            print(f"🚨 Unknown error pattern: {str(e)}")
    
    return False

def test_network_connectivity():
    """Test basic network connectivity to Apple servers"""
    print("\n" + "=" * 50)
    print("NETWORK CONNECTIVITY TEST")
    print("=" * 50)
    
    import requests
    
    apple_endpoints = [
        "https://idmsa.apple.com",
        "https://www.icloud.com", 
        "https://setup.icloud.com"
    ]
    
    for endpoint in apple_endpoints:
        try:
            print(f"🌐 Testing {endpoint}...")
            response = requests.get(endpoint, timeout=10)
            print(f"   ✅ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    success = test_direct_python_auth()
    test_network_connectivity()
    
    print("\n" + "=" * 50)
    print("CONCLUSION")
    print("=" * 50)
    
    if success:
        print("✅ Authentication working - iCloud sync should function")
    else:
        print("❌ Authentication still failing")
        print("   This suggests either:")
        print("   1. Apple server issues (503 errors)")
        print("   2. App-specific password still invalid")
        print("   3. Network/firewall blocking Apple services")
        print("   4. 2FA configuration issue")