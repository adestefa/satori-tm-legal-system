#!/usr/bin/env python3
"""
Direct test of pyicloud authentication
"""

import sys
import os

# Add dashboard to path
sys.path.insert(0, '/Users/corelogic/satori-dev/TM/dashboard')

try:
    from pyicloud import PyiCloudService
    print("✅ Successfully imported PyiCloudService")
except ImportError as e:
    print(f"❌ Failed to import PyiCloudService: {e}")
    sys.exit(1)

# Test credentials
email = "anthony.destefano@gmail.com"
password = "gqlv-uvis-tvze-ofhg"

print(f"🔍 Testing direct connection to iCloud:")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Password length: {len(password)}")

try:
    print("🔗 Creating PyiCloudService...")
    api = PyiCloudService(email, password)
    print("✅ PyiCloudService created successfully!")
    
    print(f"🔍 API attributes: {type(api)}")
    print(f"🔍 Requires 2FA: {api.requires_2fa}")
    
    if api.requires_2fa:
        print("❌ 2FA required - app-specific password may not be working")
    else:
        print("✅ No 2FA required")
        
        # Try to access drive
        print("🔗 Accessing iCloud Drive...")
        drive = api.drive
        print("✅ Drive access successful!")
        
        # Try to list root directory
        print("🔗 Listing root directory...")
        items = drive.dir()
        print(f"✅ Found {len(items)} items in root:")
        for item in items[:5]:  # Show first 5 items
            print(f"   - {item}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"❌ Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()