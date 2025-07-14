#!/usr/bin/env python3
"""
Interactive iCloud test with 2FA support
Based on research showing that modern authentication requires interactive 2FA setup
"""

import os
import sys
import json
from pathlib import Path

def interactive_icloud_test():
    """
    Test iCloud connection with interactive 2FA support
    """
    print("=" * 80)
    print("Interactive iCloud Authentication Test")
    print("=" * 80)
    
    # Load credentials
    settings_path = "../dashboard/config/settings.json"
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        icloud_config = settings.get('icloud', {})
        email = icloud_config.get('account', '')
        password = icloud_config.get('password', '')
        cookie_dir = Path(icloud_config.get('cookie_directory', './icloud_session_data'))
        
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Cookie directory: {cookie_dir}")
        
        # Create cookie directory
        cookie_dir.mkdir(parents=True, exist_ok=True)
        
        # Import PyiCloud
        from pyicloud import PyiCloudService
        from pyicloud.exceptions import PyiCloudException
        
        print("\nAttempting PyiCloud connection...")
        print("NOTE: If 2FA is required, you will be prompted for a code")
        
        try:
            # Try connection with cookie directory support
            api = PyiCloudService(
                apple_id=email,
                password=password,
                cookie_directory=str(cookie_dir)
            )
            
            print("SUCCESS: PyiCloudService created")
            
            # Check 2FA status
            if api.requires_2fa:
                print("2FA REQUIRED: You should see a prompt for 2FA code")
                print("Check your Apple devices for the verification code")
                
                # The PyiCloud library should handle the 2FA prompt automatically
                # If it doesn't, we may need to implement manual code entry
                
                # Try to validate the 2FA
                try:
                    # This should trigger the 2FA flow
                    devices = api.trusted_devices
                    print(f"Trusted devices available: {len(devices)}")
                    
                    if devices:
                        device = devices[0]
                        if not api.send_verification_code(device):
                            print("Failed to send verification code")
                        else:
                            print("Verification code sent to device")
                            code = input("Enter the verification code: ")
                            if not api.validate_verification_code(device, code):
                                print("Invalid verification code")
                            else:
                                print("2FA validation successful!")
                except Exception as e2fa:
                    print(f"2FA error: {e2fa}")
            
            # Test drive access
            print("Testing drive access...")
            drive = api.drive
            root_items = drive.dir()
            
            print(f"SUCCESS: Drive access successful!")
            print(f"Root directory contains {len(root_items)} items:")
            for item in root_items[:5]:  # Show first 5 items
                print(f"  - {item.name} ({item.type})")
            
            # Save session information
            print(f"\nSession should be saved to: {cookie_dir}")
            session_files = list(cookie_dir.glob('*'))
            print(f"Session files created: {[f.name for f in session_files]}")
            
            return True
            
        except PyiCloudException as e:
            print(f"PyiCloud error: {e}")
            error_str = str(e).lower()
            
            if '2fa' in error_str or 'two-factor' in error_str:
                print("This appears to be a 2FA issue")
                print("You may need to:")
                print("1. Use an app-specific password")
                print("2. Complete 2FA setup interactively")
                print("3. Ensure trusted device is available")
            elif 'invalid email/password' in error_str:
                print("Credential validation failed")
                print("This could be:")
                print("1. Incorrect app-specific password")
                print("2. Apple account locked/restricted")
                print("3. Rate limiting from previous attempts")
            
            return False
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def test_without_password():
    """
    Test PyiCloud with only cookie directory (no password)
    This simulates using a saved session
    """
    print("\n" + "=" * 80)
    print("Testing Saved Session (No Password)")
    print("=" * 80)
    
    settings_path = "../dashboard/config/settings.json"
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        icloud_config = settings.get('icloud', {})
        email = icloud_config.get('account', '')
        cookie_dir = Path(icloud_config.get('cookie_directory', './icloud_session_data'))
        
        # Check if session files exist
        session_files = list(cookie_dir.glob('*'))
        print(f"Existing session files: {[f.name for f in session_files]}")
        
        if not session_files:
            print("No session files found - skipping session test")
            return False
        
        from pyicloud import PyiCloudService
        
        print("Attempting connection with saved session (no password)...")
        
        # Try to connect using only email and cookie directory
        api = PyiCloudService(
            apple_id=email,
            cookie_directory=str(cookie_dir)
        )
        
        print("SUCCESS: Connected using saved session")
        
        # Test drive access
        drive = api.drive
        root_items = drive.dir()
        print(f"Drive access successful with {len(root_items)} items")
        
        return True
        
    except Exception as e:
        print(f"Session test failed: {e}")
        return False

def main():
    """
    Run comprehensive iCloud authentication tests
    """
    print("Starting comprehensive iCloud authentication tests...")
    
    # Test 1: Interactive authentication with password
    success1 = interactive_icloud_test()
    
    # Test 2: Session reuse without password
    success2 = test_without_password()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Interactive auth: {'SUCCESS' if success1 else 'FAILED'}")
    print(f"Session reuse: {'SUCCESS' if success2 else 'FAILED'}")
    
    if success1 or success2:
        print("\nAt least one authentication method worked!")
        print("You can now use the working method in your application.")
    else:
        print("\nBoth authentication methods failed.")
        print("This suggests a fundamental issue with:")
        print("1. Apple account status")
        print("2. App-specific password validity")
        print("3. Network/firewall restrictions")
        print("4. Apple service availability")

if __name__ == "__main__":
    main()