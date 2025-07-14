#!/usr/bin/env python3
"""
Debug Authentication Transmission Script
========================================

This script debugs the exact transmission between settings file storage and PyiCloud API calls
to identify encoding/transmission issues with iCloud authentication.

User feedback: "I know 100% I am sending the correct chars in the settings file, 
I am 0% sure that is what we are physically sending on the wire in the correct encoding."
"""

import json
import sys
import os
import logging
from pathlib import Path
import binascii
from urllib.parse import quote, unquote

# Add the dashboard directory to Python path for imports
dashboard_path = Path(__file__).parent.parent / "dashboard"
sys.path.insert(0, str(dashboard_path))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def debug_settings_file_reading():
    """Debug the exact reading of credentials from settings file"""
    print("=" * 80)
    print("STEP 1: SETTINGS FILE READING DEBUG")
    print("=" * 80)
    
    settings_path = dashboard_path / "config" / "settings.json"
    print(f"Settings file path: {settings_path}")
    print(f"File exists: {settings_path.exists()}")
    
    if not settings_path.exists():
        print("❌ Settings file not found!")
        return None, None
    
    # Read raw file bytes
    with open(settings_path, 'rb') as f:
        raw_bytes = f.read()
    
    print(f"\nRaw file size: {len(raw_bytes)} bytes")
    print(f"Raw bytes (first 200): {raw_bytes[:200]}")
    print(f"Raw bytes hex: {binascii.hexlify(raw_bytes[:200]).decode()}")
    
    # Read as text with different encodings
    encodings_to_test = ['utf-8', 'ascii', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_test:
        try:
            with open(settings_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"\n✅ Successfully read with {encoding} encoding")
            print(f"Content length: {len(content)} characters")
            if len(content) < 500:
                print(f"Full content: {repr(content)}")
        except Exception as e:
            print(f"❌ Failed to read with {encoding}: {e}")
    
    # Parse JSON and extract credentials
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        icloud_settings = settings.get('icloud', {})
        account = icloud_settings.get('account', '')
        password = icloud_settings.get('password', '')
        
        print(f"\n📋 Parsed JSON credentials:")
        print(f"Account: {repr(account)}")
        print(f"Password: {repr(password)}")
        print(f"Account length: {len(account)} chars")
        print(f"Password length: {len(password)} chars")
        
        # Character analysis
        print(f"\n🔍 Character analysis:")
        print(f"Account bytes: {account.encode('utf-8')}")
        print(f"Password bytes: {password.encode('utf-8')}")
        print(f"Account hex: {binascii.hexlify(account.encode('utf-8')).decode()}")
        print(f"Password hex: {binascii.hexlify(password.encode('utf-8')).decode()}")
        
        # URL encoding test
        print(f"\n🌐 URL encoding test:")
        print(f"Account URL-encoded: {quote(account)}")
        print(f"Password URL-encoded: {quote(password)}")
        
        return account, password
        
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        return None, None

def debug_pyicloud_parameter_passing(account, password):
    """Debug how parameters are passed to PyiCloud"""
    print("\n" + "=" * 80)
    print("STEP 2: PYICLOUD PARAMETER PASSING DEBUG")
    print("=" * 80)
    
    if not account or not password:
        print("❌ No credentials to test")
        return
    
    # Test parameter representation at different stages
    print(f"📤 Parameters being passed to PyiCloudService:")
    print(f"apple_id parameter: {repr(account)}")
    print(f"password parameter: {repr(password)}")
    
    # Test what happens with different string preparations
    test_variations = [
        ("original", account, password),
        ("stripped", account.strip(), password.strip()),
        ("encoded_utf8", account.encode('utf-8').decode('utf-8'), password.encode('utf-8').decode('utf-8')),
        ("normalized", account.replace('\r', '').replace('\n', ''), password.replace('\r', '').replace('\n', '')),
    ]
    
    for name, test_account, test_password in test_variations:
        print(f"\n🧪 Testing {name} variation:")
        print(f"  Account: {repr(test_account)}")
        print(f"  Password: {repr(test_password)}")
        print(f"  Account bytes: {test_account.encode('utf-8')}")
        print(f"  Password bytes: {test_password.encode('utf-8')}")

def debug_pyicloud_internals():
    """Debug PyiCloud internal credential handling"""
    print("\n" + "=" * 80)
    print("STEP 3: PYICLOUD INTERNAL DEBUG")
    print("=" * 80)
    
    try:
        from pyicloud import PyiCloudService
        import inspect
        
        print(f"✅ PyiCloud imported successfully")
        print(f"PyiCloud version: {getattr(PyiCloudService, '__version__', 'unknown')}")
        
        # Inspect PyiCloudService constructor
        init_signature = inspect.signature(PyiCloudService.__init__)
        print(f"\n🔍 PyiCloudService.__init__ signature:")
        print(f"  {init_signature}")
        
        # Get the source file location
        source_file = inspect.getfile(PyiCloudService)
        print(f"\n📁 PyiCloud source file: {source_file}")
        
    except ImportError as e:
        print(f"❌ Failed to import PyiCloud: {e}")
        return
    except Exception as e:
        print(f"❌ PyiCloud inspection failed: {e}")
        return

def debug_monkey_patched_authentication(account, password):
    """Create a monkey-patched version of PyiCloud to capture actual transmitted data"""
    print("\n" + "=" * 80)
    print("STEP 4: MONKEY-PATCHED AUTHENTICATION DEBUG")
    print("=" * 80)
    
    if not account or not password:
        print("❌ No credentials to test")
        return
    
    try:
        from pyicloud import PyiCloudService
        import requests
        
        # Store original requests methods
        original_post = requests.Session.post
        original_get = requests.Session.get
        
        captured_requests = []
        
        def debug_post(self, url, **kwargs):
            """Capture POST requests to see exactly what's being sent"""
            print(f"\n🌐 CAPTURED POST REQUEST:")
            print(f"  URL: {url}")
            
            if 'data' in kwargs:
                print(f"  POST data: {kwargs['data']}")
                if isinstance(kwargs['data'], dict):
                    for key, value in kwargs['data'].items():
                        print(f"    {key}: {repr(value)} (type: {type(value)})")
                        if isinstance(value, str):
                            print(f"      bytes: {value.encode('utf-8')}")
                            print(f"      hex: {binascii.hexlify(value.encode('utf-8')).decode()}")
            
            if 'json' in kwargs:
                print(f"  JSON data: {kwargs['json']}")
            
            if 'headers' in kwargs:
                print(f"  Headers: {kwargs['headers']}")
            
            captured_requests.append({
                'method': 'POST',
                'url': url,
                'kwargs': kwargs
            })
            
            # Call original method
            return original_post(self, url, **kwargs)
        
        def debug_get(self, url, **kwargs):
            """Capture GET requests"""
            print(f"\n🌐 CAPTURED GET REQUEST:")
            print(f"  URL: {url}")
            
            captured_requests.append({
                'method': 'GET', 
                'url': url,
                'kwargs': kwargs
            })
            
            return original_get(self, url, **kwargs)
        
        # Apply monkey patches
        requests.Session.post = debug_post
        requests.Session.get = debug_get
        
        print(f"🔧 Monkey patching applied to capture HTTP requests")
        print(f"🧪 Attempting PyiCloud authentication with captured credentials...")
        print(f"   Account: {repr(account)}")
        print(f"   Password: {repr(password)}")
        
        try:
            # Attempt authentication
            api = PyiCloudService(apple_id=account, password=password)
            print(f"✅ PyiCloudService created successfully")
            
            if api.requires_2fa:
                print(f"🔐 2FA required")
            else:
                print(f"🎉 Authentication successful!")
                
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print(f"   Exception type: {type(e)}")
            print(f"   Exception args: {e.args}")
        
        finally:
            # Restore original methods
            requests.Session.post = original_post
            requests.Session.get = original_get
            
        print(f"\n📊 Total captured requests: {len(captured_requests)}")
        
    except Exception as e:
        print(f"❌ Monkey patch debug failed: {e}")

def debug_wire_protocol_comparison():
    """Compare what should be sent vs what actually gets sent"""
    print("\n" + "=" * 80)
    print("STEP 5: WIRE PROTOCOL COMPARISON")
    print("=" * 80)
    
    # Expected credentials based on user confirmation
    expected_account = "anthony.destefano@gmail.com"
    expected_password = "gqlv-uvis-tvze-ofhg"
    
    print(f"🎯 Expected credentials (user confirmed working):")
    print(f"   Account: {repr(expected_account)}")
    print(f"   Password: {repr(expected_password)}")
    print(f"   Account bytes: {expected_account.encode('utf-8')}")
    print(f"   Password bytes: {expected_password.encode('utf-8')}")
    print(f"   Account hex: {binascii.hexlify(expected_account.encode('utf-8')).decode()}")
    print(f"   Password hex: {binascii.hexlify(expected_password.encode('utf-8')).decode()}")
    
    # Read actual credentials from settings
    account, password = debug_settings_file_reading()
    
    if account and password:
        print(f"\n🔍 Comparison analysis:")
        print(f"   Account match: {account == expected_account}")
        print(f"   Password match: {password == expected_password}")
        
        if account != expected_account:
            print(f"   ❌ Account mismatch!")
            print(f"      Expected: {repr(expected_account)}")
            print(f"      Actual:   {repr(account)}")
            print(f"      Diff chars: {set(expected_account) - set(account)}")
        
        if password != expected_password:
            print(f"   ❌ Password mismatch!")
            print(f"      Expected: {repr(expected_password)}")
            print(f"      Actual:   {repr(password)}")
            print(f"      Diff chars: {set(expected_password) - set(password)}")
        
        if account == expected_account and password == expected_password:
            print(f"   ✅ Credentials match exactly - issue is in transmission/encoding")

def main():
    """Main debugging function"""
    print("iCloud Authentication Transmission Debug")
    print("=" * 80)
    print("This script will debug the exact transmission path from settings file to PyiCloud API")
    print("User issue: Authentication fails despite correct credentials in settings")
    print("=" * 80)
    
    # Step 1: Debug settings file reading
    account, password = debug_settings_file_reading()
    
    # Step 2: Debug parameter passing
    debug_pyicloud_parameter_passing(account, password)
    
    # Step 3: Debug PyiCloud internals
    debug_pyicloud_internals()
    
    # Step 4: Monkey patch authentication to capture wire data
    debug_monkey_patched_authentication(account, password)
    
    # Step 5: Compare expected vs actual
    debug_wire_protocol_comparison()
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)
    print("Review the output above to identify where the transmission differs")
    print("from the expected credentials.")

if __name__ == "__main__":
    main()