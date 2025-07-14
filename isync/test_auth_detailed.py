#!/usr/bin/env python3
"""
Detailed authentication test with more error info
"""

import sys
import os
import requests
import time
sys.path.insert(0, '/Users/corelogic/satori-dev/TM/dashboard')

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException, PyiCloudAPIResponseException

# Test credentials
email = "anthony.destefano@gmail.com"
password = "gqlv-uvis-tvze-ofhg"  # Replace with new password when generated

print(f"🔍 Detailed authentication test:")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Password type: {type(password)}")
print(f"   Password repr: {repr(password)}")

# Test 1: Basic connectivity
print("\n📡 Testing basic connectivity to Apple...")
try:
    response = requests.get("https://idmsa.apple.com", timeout=10)
    print(f"✅ Apple ID servers reachable: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot reach Apple servers: {e}")

# Test 2: Check for hidden characters
print(f"\n🔍 Password analysis:")
print(f"   Length: {len(password)}")
print(f"   Characters: {[c for c in password]}")
print(f"   ASCII values: {[ord(c) for c in password]}")

# Test 3: Try authentication with verbose error handling
print(f"\n🔐 Attempting authentication...")
try:
    # Create API instance with more specific error handling
    api = PyiCloudService(email, password)
    
    print("✅ Authentication successful!")
    print(f"   User info: {api.user}")
    print(f"   Available services: {list(api._service_names_list)}")
    
except PyiCloudFailedLoginException as e:
    print(f"❌ Login failed: {e}")
    print("🔍 This is definitely an authentication issue")
    
except PyiCloudAPIResponseException as e:
    print(f"❌ API Error: {e}")
    print(f"   Status code: {getattr(e, 'code', 'Unknown')}")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"   Type: {type(e).__name__}")
    import traceback
    print("📝 Full traceback:")
    traceback.print_exc()

print(f"\n💡 Recommendations:")
print(f"   1. Generate a fresh app-specific password")
print(f"   2. Ensure no extra spaces or characters")
print(f"   3. Try testing within 2-3 minutes of generation")
print(f"   4. Verify the Apple ID doesn't have regional restrictions")