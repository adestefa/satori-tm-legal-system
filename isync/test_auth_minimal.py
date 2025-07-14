#!/usr/bin/env python3
"""
Minimal test to isolate the authentication issue
"""

import sys
import os
import time
sys.path.insert(0, '/Users/corelogic/satori-dev/TM/dashboard')

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException, PyiCloudAPIResponseException

# Test credentials
email = "anthony.destefano@gmail.com"
password = "gqlv-uvis-tvze-ofhg"

print(f"🔍 Minimal authentication test:")
print(f"   Email: {email}")
print(f"   App-specific password: {password}")

try:
    print("🔗 Attempting authentication with small delay...")
    time.sleep(2)  # Small delay in case of rate limiting
    
    # Try with some additional parameters that might help
    api = PyiCloudService(
        apple_id=email,
        password=password,
        # cookie_directory="/tmp",  # Use temp directory for cookies
        # verify=True  # Verify SSL certificates
    )
    
    print("✅ Authentication successful!")
    print(f"   User: {api.user}")
    print(f"   Requires 2FA: {api.requires_2fa}")
    
except PyiCloudFailedLoginException as e:
    print(f"❌ Login failed: {e}")
    print("💡 This suggests the app-specific password is not working")
    print("💡 Try:")
    print("   1. Generate a new app-specific password")
    print("   2. Wait 5-10 minutes for it to activate") 
    print("   3. Make sure 2FA is enabled on your Apple ID")
    
except PyiCloudAPIResponseException as e:
    print(f"❌ API Error: {e}")
    print("💡 This might be rate limiting or server issues")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"   Type: {type(e).__name__}")