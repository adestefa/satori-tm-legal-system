#!/usr/bin/env python3
"""
Direct PyiCloud Authentication Test
==================================

Tests PyiCloud authentication directly with hardcoded credentials to isolate
encoding/transmission issues from the settings file layer.
"""

import sys
import logging
from pathlib import Path

# Configure logging to see PyiCloud internals
logging.basicConfig(level=logging.DEBUG)

def test_hardcoded_credentials():
    """Test with exact credentials user confirmed are working"""
    print("=" * 60)
    print("DIRECT AUTHENTICATION TEST")
    print("=" * 60)
    
    # User confirmed these exact credentials work in real iCloud login
    account = "anthony.destefano@gmail.com"
    password = "gqlv-uvis-tvze-ofhg"
    
    print(f"Testing with hardcoded credentials:")
    print(f"  Account: {account}")
    print(f"  Password: {password}")
    print(f"  Account length: {len(account)}")
    print(f"  Password length: {len(password)}")
    print()
    
    try:
        from pyicloud import PyiCloudService
        print("✅ PyiCloud imported successfully")
        
        print("🔄 Attempting authentication...")
        api = PyiCloudService(apple_id=account, password=password)
        
        print("✅ PyiCloudService created successfully")
        
        if api.requires_2fa:
            print("🔐 2FA is required - this is normal for initial setup")
            print("   This means authentication credentials are CORRECT")
            print("   The app-specific password is being accepted")
            return True
        else:
            print("🎉 Authentication successful - no 2FA required")
            print("   This means full authentication is working")
            return True
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print(f"   Exception type: {type(e)}")
        
        # Check for specific error types
        error_str = str(e).lower()
        if 'invalid email/password' in error_str or 'authentication failed' in error_str:
            print("🚨 CREDENTIAL REJECTION - This suggests encoding/transmission issue")
        elif '2fa' in error_str or 'two-factor' in error_str:
            print("✅ 2FA required - credentials are being accepted")
        else:
            print(f"❓ Unknown error pattern: {error_str}")
        
        return False

def test_settings_file_credentials():
    """Test with credentials loaded from settings file"""
    print("\n" + "=" * 60)
    print("SETTINGS FILE CREDENTIALS TEST")
    print("=" * 60)
    
    try:
        import json
        dashboard_path = Path(__file__).parent.parent / "dashboard"
        settings_path = dashboard_path / "config" / "settings.json"
        
        if not settings_path.exists():
            print(f"❌ Settings file not found: {settings_path}")
            return False
        
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        icloud_settings = settings.get('icloud', {})
        account = icloud_settings.get('account', '')
        password = icloud_settings.get('password', '')
        
        print(f"Loaded from settings file:")
        print(f"  Account: {repr(account)}")
        print(f"  Password: {repr(password)}")
        print(f"  Account length: {len(account)}")
        print(f"  Password length: {len(password)}")
        
        # Compare with expected
        expected_account = "anthony.destefano@gmail.com"
        expected_password = "gqlv-uvis-tvze-ofhg"
        
        print(f"\nComparison with expected:")
        print(f"  Account matches: {account == expected_account}")
        print(f"  Password matches: {password == expected_password}")
        
        if account != expected_account:
            print(f"  ❌ Account mismatch!")
            print(f"     Expected: {repr(expected_account)}")
            print(f"     Actual:   {repr(account)}")
        
        if password != expected_password:
            print(f"  ❌ Password mismatch!")
            print(f"     Expected: {repr(expected_password)}")
            print(f"     Actual:   {repr(password)}")
        
        # Test authentication with settings file credentials
        if account and password:
            print(f"\n🔄 Testing authentication with settings file credentials...")
            
            try:
                from pyicloud import PyiCloudService
                api = PyiCloudService(apple_id=account, password=password)
                
                print("✅ PyiCloudService created successfully")
                
                if api.requires_2fa:
                    print("🔐 2FA required - credentials accepted")
                    return True
                else:
                    print("🎉 Full authentication successful")
                    return True
                    
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return False
        else:
            print("❌ No credentials found in settings file")
            return False
            
    except Exception as e:
        print(f"❌ Settings file test failed: {e}")
        return False

def test_character_encoding_variations():
    """Test different character encoding variations"""
    print("\n" + "=" * 60)
    print("CHARACTER ENCODING VARIATIONS TEST")
    print("=" * 60)
    
    base_account = "anthony.destefano@gmail.com"
    base_password = "gqlv-uvis-tvze-ofhg"
    
    # Test variations that might occur during transmission
    variations = [
        ("original", base_account, base_password),
        ("stripped", base_account.strip(), base_password.strip()),
        ("with_newline", base_account + "\n", base_password + "\n"),
        ("with_carriage_return", base_account + "\r", base_password + "\r"),
        ("with_space", base_account + " ", base_password + " "),
        ("leading_space", " " + base_account, " " + base_password),
    ]
    
    for name, test_account, test_password in variations:
        print(f"\n🧪 Testing {name} variation:")
        print(f"   Account: {repr(test_account)}")
        print(f"   Password: {repr(test_password)}")
        
        try:
            from pyicloud import PyiCloudService
            api = PyiCloudService(apple_id=test_account, password=test_password)
            
            if api.requires_2fa:
                print(f"   ✅ {name}: 2FA required - credentials accepted")
            else:
                print(f"   ✅ {name}: Full authentication successful")
                
        except Exception as e:
            print(f"   ❌ {name}: Authentication failed - {e}")

def main():
    """Main test function"""
    print("PyiCloud Direct Authentication Debug")
    print("Testing to isolate encoding/transmission issues")
    print()
    
    # Test 1: Hardcoded credentials (should work if PyiCloud is functioning)
    hardcoded_success = test_hardcoded_credentials()
    
    # Test 2: Settings file credentials (compare with hardcoded)
    settings_success = test_settings_file_credentials()
    
    # Test 3: Character encoding variations
    test_character_encoding_variations()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if hardcoded_success and settings_success:
        print("✅ Both hardcoded and settings file credentials work")
        print("   Issue is likely NOT in credential storage/transmission")
        print("   Check other parts of the authentication flow")
    elif hardcoded_success and not settings_success:
        print("🚨 Hardcoded works but settings file fails")
        print("   Issue is in settings file storage or reading")
        print("   Check JSON encoding, file permissions, or parsing")
    elif not hardcoded_success and not settings_success:
        print("❌ Both hardcoded and settings file fail")
        print("   Issue is likely in PyiCloud library or network")
        print("   Check PyiCloud version, network connectivity, or Apple API changes")
    else:
        print("❓ Unexpected result - settings work but hardcoded fails")
        print("   This suggests an unusual environment issue")

if __name__ == "__main__":
    main()