#!/usr/bin/env python3
"""
iCloud Authentication Debug Tool
Deep debugging of credential transmission and encoding issues

Usage: python debug_icloud_auth.py
"""

import os
import sys
import json
import base64
import urllib.parse
import binascii
from typing import Dict, Any

# Add shared schema to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared-schema'))

def debug_credential_encoding(email: str, password: str) -> Dict[str, Any]:
    """
    Comprehensive credential encoding analysis
    """
    results = {
        'email_analysis': {},
        'password_analysis': {},
        'transmission_tests': {},
        'encoding_variations': {}
    }
    
    # Email Analysis
    print(f"🔍 EMAIL ANALYSIS")
    print(f"   Raw email: '{email}'")
    print(f"   Length: {len(email)}")
    print(f"   Type: {type(email)}")
    print(f"   UTF-8 bytes: {email.encode('utf-8')}")
    print(f"   ASCII safe: {email.isascii()}")
    print(f"   URL encoded: {urllib.parse.quote(email)}")
    
    results['email_analysis'] = {
        'raw': email,
        'length': len(email),
        'type': str(type(email)),
        'utf8_bytes': str(email.encode('utf-8')),
        'ascii_safe': email.isascii(),
        'url_encoded': urllib.parse.quote(email)
    }
    
    print(f"\n🔐 PASSWORD ANALYSIS")
    print(f"   Raw password: '{password}'")
    print(f"   Length: {len(password)}")
    print(f"   Type: {type(password)}")
    print(f"   UTF-8 bytes: {password.encode('utf-8')}")
    print(f"   ASCII safe: {password.isascii()}")
    print(f"   Contains hyphens: {'-' in password}")
    print(f"   URL encoded: {urllib.parse.quote(password)}")
    print(f"   Base64 encoded: {base64.b64encode(password.encode('utf-8')).decode('ascii')}")
    
    results['password_analysis'] = {
        'raw': password,
        'length': len(password),
        'type': str(type(password)),
        'utf8_bytes': str(password.encode('utf-8')),
        'ascii_safe': password.isascii(),
        'contains_hyphens': '-' in password,
        'url_encoded': urllib.parse.quote(password),
        'base64_encoded': base64.b64encode(password.encode('utf-8')).decode('ascii')
    }
    
    # Character-by-character analysis
    print(f"\n🔤 CHARACTER-BY-CHARACTER ANALYSIS")
    for i, char in enumerate(password):
        print(f"   [{i}] '{char}' (U+{ord(char):04X}) ASCII: {ord(char) < 128}")
    
    # Test various encoding scenarios
    print(f"\n🧪 ENCODING VARIATION TESTS")
    
    # Test 1: Direct string
    test1_email = email
    test1_password = password
    print(f"   Test 1 (Direct): email='{test1_email}' password='{test1_password}'")
    
    # Test 2: UTF-8 encode/decode cycle
    test2_email = email.encode('utf-8').decode('utf-8')
    test2_password = password.encode('utf-8').decode('utf-8')
    print(f"   Test 2 (UTF-8 cycle): email='{test2_email}' password='{test2_password}'")
    
    # Test 3: JSON serialize/deserialize cycle
    test_data = {'email': email, 'password': password}
    json_str = json.dumps(test_data)
    parsed_data = json.loads(json_str)
    test3_email = parsed_data['email']
    test3_password = parsed_data['password']
    print(f"   Test 3 (JSON cycle): email='{test3_email}' password='{test3_password}'")
    
    # Test 4: URL encode/decode cycle
    encoded_email = urllib.parse.quote(email)
    encoded_password = urllib.parse.quote(password)
    test4_email = urllib.parse.unquote(encoded_email)
    test4_password = urllib.parse.unquote(encoded_password)
    print(f"   Test 4 (URL cycle): email='{test4_email}' password='{test4_password}'")
    
    # Test 5: Base64 encode/decode cycle
    b64_email = base64.b64encode(email.encode('utf-8')).decode('ascii')
    b64_password = base64.b64encode(password.encode('utf-8')).decode('ascii')
    test5_email = base64.b64decode(b64_email).decode('utf-8')
    test5_password = base64.b64decode(b64_password).decode('utf-8')
    print(f"   Test 5 (Base64 cycle): email='{test5_email}' password='{test5_password}'")
    
    results['encoding_variations'] = {
        'direct': {'email': test1_email, 'password': test1_password},
        'utf8_cycle': {'email': test2_email, 'password': test2_password},
        'json_cycle': {'email': test3_email, 'password': test3_password},
        'url_cycle': {'email': test4_email, 'password': test4_password},
        'base64_cycle': {'email': test5_email, 'password': test5_password}
    }
    
    return results

def test_settings_loading() -> Dict[str, Any]:
    """
    Test actual settings loading from dashboard config
    """
    print(f"\n📁 SETTINGS FILE LOADING TEST")
    
    settings_path = "dashboard/config/settings.json"
    
    if not os.path.exists(settings_path):
        print(f"   ❌ Settings file not found: {settings_path}")
        return {'error': f'Settings file not found: {settings_path}'}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            print(f"   📄 Raw file content length: {len(raw_content)} bytes")
            print(f"   📄 Raw file encoding check: {raw_content.encode('utf-8')[:100]}...")
            
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            print(f"   ✅ JSON parsed successfully")
            
        icloud_config = settings.get('icloud', {})
        email = icloud_config.get('account', '')
        password = icloud_config.get('password', '')
        
        print(f"   🔍 Loaded email: '{email}'")
        print(f"   🔍 Loaded password: '{password}'")
        print(f"   🔍 Email length: {len(email)}")
        print(f"   🔍 Password length: {len(password)}")
        
        return {
            'success': True,
            'email': email,
            'password': password,
            'raw_content_length': len(raw_content),
            'settings_data': settings
        }
        
    except Exception as e:
        print(f"   ❌ Error loading settings: {e}")
        return {'error': str(e)}

def debug_pyicloud_construction(email: str, password: str) -> Dict[str, Any]:
    """
    Debug PyiCloud object construction step by step
    """
    print(f"\n🐍 PYICLOUD CONSTRUCTION DEBUG")
    
    try:
        # Import PyiCloud
        print(f"   📦 Importing PyiCloud...")
        from pyicloud import PyiCloudService
        from pyicloud.exceptions import PyiCloudException
        print(f"   ✅ PyiCloud imported successfully")
        
        # Check what we're about to send
        print(f"   🔍 About to construct PyiCloudService with:")
        print(f"       email type: {type(email)}")
        print(f"       email value: '{email}'")
        print(f"       email repr: {repr(email)}")
        print(f"       password type: {type(password)}")
        print(f"       password value: '{password}'")
        print(f"       password repr: {repr(password)}")
        
        # Attempt construction with detailed error capture
        print(f"   🚀 Attempting PyiCloudService construction...")
        
        try:
            # This is the exact line that's failing
            api = PyiCloudService(email, password)
            print(f"   ✅ PyiCloudService constructed successfully!")
            return {
                'success': True,
                'api_object': str(api),
                'api_type': str(type(api))
            }
            
        except PyiCloudException as e:
            print(f"   ❌ PyiCloudException during construction: {e}")
            print(f"   ❌ Exception type: {type(e).__name__}")
            print(f"   ❌ Exception args: {e.args}")
            return {
                'success': False,
                'error_type': 'PyiCloudException',
                'error_message': str(e),
                'error_args': str(e.args)
            }
            
        except Exception as e:
            print(f"   ❌ General exception during construction: {e}")
            print(f"   ❌ Exception type: {type(e).__name__}")
            print(f"   ❌ Exception args: {e.args}")
            return {
                'success': False,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'error_args': str(e.args)
            }
            
    except ImportError as e:
        print(f"   ❌ Failed to import PyiCloud: {e}")
        return {
            'success': False,
            'error_type': 'ImportError',
            'error_message': str(e)
        }

def main():
    """
    Main debugging workflow
    """
    print("=" * 80)
    print("🐛 iCloud Authentication Debug Tool")
    print("=" * 80)
    
    # Test 1: Load credentials from settings file
    print("\n🧪 TEST 1: SETTINGS FILE LOADING")
    settings_result = test_settings_loading()
    
    if 'error' in settings_result:
        print(f"❌ Cannot proceed - settings loading failed: {settings_result['error']}")
        return
    
    email = settings_result['email']
    password = settings_result['password']
    
    if not email or not password:
        print(f"❌ Cannot proceed - missing credentials in settings file")
        print(f"   Email: '{email}'")
        print(f"   Password: '{password}'")
        return
    
    # Test 2: Analyze credential encoding
    print("\n🧪 TEST 2: CREDENTIAL ENCODING ANALYSIS")
    encoding_results = debug_credential_encoding(email, password)
    
    # Test 3: Debug PyiCloud construction
    print("\n🧪 TEST 3: PYICLOUD CONSTRUCTION")
    construction_results = debug_pyicloud_construction(email, password)
    
    # Test 4: Test with hardcoded known-good credentials
    print("\n🧪 TEST 4: HARDCODED CREDENTIALS TEST")
    hardcoded_email = "anthony.destefano@gmail.com"
    hardcoded_password = "gqlv-uvis-tvze-ofhg"
    
    print(f"   🔍 Testing with hardcoded credentials...")
    print(f"   Email: '{hardcoded_email}'")
    print(f"   Password: '{hardcoded_password}'")
    
    hardcoded_encoding = debug_credential_encoding(hardcoded_email, hardcoded_password)
    hardcoded_construction = debug_pyicloud_construction(hardcoded_email, hardcoded_password)
    
    # Summary Report
    print("\n" + "=" * 80)
    print("📊 DEBUGGING SUMMARY REPORT")
    print("=" * 80)
    
    print(f"\n📁 Settings File Status:")
    print(f"   ✅ Loaded: {settings_result.get('success', False)}")
    print(f"   📧 Email: '{email}'")
    print(f"   🔐 Password: '{password}'")
    
    print(f"\n🔤 Encoding Analysis:")
    print(f"   📧 Email ASCII: {encoding_results['email_analysis']['ascii_safe']}")
    print(f"   🔐 Password ASCII: {encoding_results['password_analysis']['ascii_safe']}")
    print(f"   🔗 URL Safe: Email={encoding_results['email_analysis']['url_encoded'] == email}, Password={encoding_results['password_analysis']['url_encoded'] == password}")
    
    print(f"\n🐍 PyiCloud Construction:")
    print(f"   📁 Settings Creds: {construction_results.get('success', False)}")
    if not construction_results.get('success', False):
        print(f"   ❌ Error: {construction_results.get('error_message', 'Unknown')}")
    
    print(f"   💾 Hardcoded Creds: {hardcoded_construction.get('success', False)}")
    if not hardcoded_construction.get('success', False):
        print(f"   ❌ Error: {hardcoded_construction.get('error_message', 'Unknown')}")
    
    # Next Steps Recommendation
    print(f"\n🎯 NEXT STEPS RECOMMENDATION:")
    
    if construction_results.get('success', False):
        print(f"   ✅ Settings credentials work! Issue may be intermittent or network-related")
    elif hardcoded_construction.get('success', False):
        print(f"   🔍 Hardcoded works, settings fail - encoding issue in settings file")
    else:
        print(f"   ❌ Both fail - deeper PyiCloud library issue or network problem")
        print(f"   🔧 Recommended: Check network connectivity, Apple ID status, 2FA settings")
    
    print(f"\n💾 Raw debug data saved to: debug_icloud_results.json")
    
    # Save detailed results
    debug_data = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'settings_loading': settings_result,
        'encoding_analysis': encoding_results,
        'construction_test': construction_results,
        'hardcoded_test': {
            'encoding': hardcoded_encoding,
            'construction': hardcoded_construction
        }
    }
    
    with open('debug_icloud_results.json', 'w') as f:
        json.dump(debug_data, f, indent=2, default=str)

if __name__ == "__main__":
    main()