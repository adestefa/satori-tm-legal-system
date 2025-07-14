#!/usr/bin/env python3
"""
Test iCloudPD Authentication
===========================

Test the new icloudpd-based authentication system to verify it works
with the user's credentials.
"""

import sys
import json
from pathlib import Path

# Add dashboard to path
dashboard_path = Path(__file__).parent / "dashboard"
sys.path.insert(0, str(dashboard_path))

from icloud_service import iCloudService

def test_icloudpd_authentication():
    """Test icloudpd authentication with settings file credentials"""
    print("=" * 60)
    print("iCLOUDPD AUTHENTICATION TEST")
    print("=" * 60)
    
    # Load credentials from settings file
    settings_path = dashboard_path / "config" / "settings.json"
    
    if not settings_path.exists():
        print(f"❌ Settings file not found: {settings_path}")
        return False
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        icloud_settings = settings.get('icloud', {})
        account = icloud_settings.get('account', '')
        password = icloud_settings.get('password', '')
        
        print(f"Testing with settings file credentials:")
        print(f"  Account: {account}")
        print(f"  Password: {password}")
        print(f"  Authentication method: icloudpd")
        print()
        
        if not account or not password:
            print("❌ Missing credentials in settings file")
            return False
        
        # Create iCloud service instance
        service = iCloudService()
        
        print("🔄 Attempting icloudpd authentication...")
        result = service.connect(account, password)
        
        if result['success']:
            print("✅ Authentication successful!")
            print(f"   Message: {result['message']}")
            print(f"   Method: {result['authentication_method']}")
            print(f"   Cookie directory: {result['cookie_directory']}")
            
            # Test folder access
            print("\n🔄 Testing folder access...")
            folder_result = service.test_folder_access("/CASES")
            
            if folder_result['success']:
                print("✅ Folder access successful!")
                print(f"   Message: {folder_result['message']}")
            else:
                print(f"⚠️  Folder access failed: {folder_result['error']}")
            
            # Get status
            print("\n📊 Service status:")
            status = service.get_status()
            for key, value in status.items():
                print(f"   {key}: {value}")
            
            return True
        else:
            print(f"❌ Authentication failed: {result['error']}")
            print(f"   Method: {result.get('authentication_method', 'unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_both_passwords():
    """Test both passwords to see which one works"""
    print("\n" + "=" * 60)
    print("TESTING BOTH PASSWORDS")
    print("=" * 60)
    
    passwords_to_test = [
        ("Settings file password", "zpcc-qsrx-saut-khph"),
        ("User mentioned password", "gqlv-uvis-tvze-ofhg")
    ]
    
    account = "anthony.destefano@gmail.com"
    
    for name, password in passwords_to_test:
        print(f"\n🧪 Testing {name}: {password}")
        
        service = iCloudService()
        result = service.connect(account, password)
        
        if result['success']:
            print(f"✅ {name}: Authentication successful!")
            return True
        else:
            print(f"❌ {name}: {result['error']}")
    
    return False

def main():
    """Main test function"""
    print("iCloudPD Authentication Test")
    print("Testing modern icloudpd-based authentication")
    print()
    
    # Test 1: Settings file credentials
    settings_success = test_icloudpd_authentication()
    
    # Test 2: Both passwords to identify which works
    both_passwords_result = test_both_passwords()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if settings_success:
        print("✅ Settings file credentials work with icloudpd")
        print("   The deprecated pyicloud library was the problem")
        print("   icloudpd provides reliable, maintained iCloud authentication")
    elif both_passwords_result:
        print("✅ One of the passwords works with icloudpd")
        print("   Update the settings file with the working password")
    else:
        print("❌ Neither password works with icloudpd")
        print("   Check if icloudpd is installed: pip install icloudpd")
        print("   Verify app-specific passwords are still valid")
        print("   Check network connectivity and Apple API status")

if __name__ == "__main__":
    main()