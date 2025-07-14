#!/usr/bin/env python3
"""
HTTP Request Monitor for PyiCloud Authentication
Captures actual wire-level HTTP requests and responses

Usage: python monitor_http_requests.py
"""

import os
import sys
import json
import requests
import urllib3
from datetime import datetime
from typing import Dict, Any, List
import logging

# Add shared schema to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared-schema'))

class HTTPRequestMonitor:
    """
    Monitor HTTP requests made by PyiCloud to capture authentication payload
    """
    
    def __init__(self):
        self.captured_requests = []
        self.original_request = None
        
    def setup_request_monitoring(self):
        """
        Monkey patch requests to capture HTTP calls
        """
        self.original_request = requests.Session.request
        
        def monitored_request(session_self, method, url, **kwargs):
            """
            Intercept and log all HTTP requests
            """
            request_data = {
                'timestamp': datetime.now().isoformat(),
                'method': method,
                'url': url,
                'headers': dict(kwargs.get('headers', {})),
                'params': kwargs.get('params', {}),
                'data': None,
                'json_data': kwargs.get('json', {}),
                'auth': str(kwargs.get('auth', None)),
                'response_status': None,
                'response_headers': {},
                'response_text': None,
                'error': None
            }
            
            # Capture request body/data
            if 'data' in kwargs:
                if isinstance(kwargs['data'], (str, bytes)):
                    request_data['data'] = str(kwargs['data'])
                else:
                    request_data['data'] = str(kwargs['data'])
            
            print(f"🌐 HTTP Request Captured:")
            print(f"   Method: {method}")
            print(f"   URL: {url}")
            print(f"   Headers: {dict(kwargs.get('headers', {}))}")
            
            if 'data' in kwargs:
                print(f"   Data: {kwargs['data']}")
            if 'json' in kwargs:
                print(f"   JSON: {kwargs['json']}")
            if 'params' in kwargs:
                print(f"   Params: {kwargs['params']}")
            
            try:
                # Make the actual request
                response = self.original_request(session_self, method, url, **kwargs)
                
                request_data['response_status'] = response.status_code
                request_data['response_headers'] = dict(response.headers)
                
                # Capture response text (be careful with large responses)
                try:
                    response_text = response.text[:2000]  # First 2000 chars
                    request_data['response_text'] = response_text
                except:
                    request_data['response_text'] = "[Could not decode response text]"
                
                print(f"   Response Status: {response.status_code}")
                print(f"   Response Headers: {dict(response.headers)}")
                print(f"   Response Text (first 200 chars): {response_text[:200]}...")
                
                self.captured_requests.append(request_data)
                return response
                
            except Exception as e:
                request_data['error'] = str(e)
                print(f"   ❌ Request Error: {e}")
                self.captured_requests.append(request_data)
                raise
        
        # Apply the monkey patch
        requests.Session.request = monitored_request
        
    def restore_request_monitoring(self):
        """
        Restore original request method
        """
        if self.original_request:
            requests.Session.request = self.original_request
    
    def get_captured_requests(self) -> List[Dict[str, Any]]:
        """
        Return all captured requests
        """
        return self.captured_requests
    
    def save_captured_requests(self, filename: str = "captured_http_requests.json"):
        """
        Save captured requests to JSON file
        """
        with open(filename, 'w') as f:
            json.dump(self.captured_requests, f, indent=2, default=str)
        print(f"💾 Captured requests saved to: {filename}")

def load_credentials_from_settings() -> Dict[str, str]:
    """
    Load credentials from dashboard settings
    """
    settings_path = "dashboard/config/settings.json"
    
    if not os.path.exists(settings_path):
        return {'error': f'Settings file not found: {settings_path}'}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        icloud_config = settings.get('icloud', {})
        return {
            'email': icloud_config.get('account', ''),
            'password': icloud_config.get('password', '')
        }
    except Exception as e:
        return {'error': str(e)}

def test_pyicloud_with_monitoring(email: str, password: str, monitor: HTTPRequestMonitor) -> Dict[str, Any]:
    """
    Test PyiCloud authentication with HTTP monitoring
    """
    print(f"\n🐍 TESTING PYICLOUD WITH HTTP MONITORING")
    print(f"   Email: '{email}'")
    print(f"   Password: '{password}'")
    
    try:
        # Setup monitoring
        monitor.setup_request_monitoring()
        
        # Import and test PyiCloud
        from pyicloud import PyiCloudService
        from pyicloud.exceptions import PyiCloudException
        
        print(f"\n🚀 Creating PyiCloudService object...")
        
        try:
            # This should trigger HTTP requests that we'll capture
            api = PyiCloudService(email, password)
            
            print(f"✅ PyiCloudService created successfully!")
            
            # Try to access something to trigger more requests
            print(f"🔍 Testing drive access...")
            try:
                drive = api.drive
                root_contents = drive.dir()
                print(f"✅ Drive access successful - found {len(root_contents)} items")
                
                return {
                    'success': True,
                    'drive_accessible': True,
                    'root_items_count': len(root_contents)
                }
            except Exception as drive_e:
                print(f"⚠️ Drive access failed: {drive_e}")
                return {
                    'success': True,
                    'drive_accessible': False,
                    'drive_error': str(drive_e)
                }
                
        except PyiCloudException as e:
            print(f"❌ PyiCloudException: {e}")
            return {
                'success': False,
                'error_type': 'PyiCloudException',
                'error_message': str(e)
            }
        except Exception as e:
            print(f"❌ General Exception: {e}")
            return {
                'success': False,
                'error_type': type(e).__name__,
                'error_message': str(e)
            }
    
    finally:
        # Always restore monitoring
        monitor.restore_request_monitoring()

def analyze_authentication_requests(requests_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze captured requests for authentication patterns
    """
    print(f"\n🔍 ANALYZING CAPTURED REQUESTS")
    
    analysis = {
        'total_requests': len(requests_list),
        'authentication_requests': [],
        'apple_requests': [],
        'post_requests': [],
        'credential_usage': [],
        'errors': []
    }
    
    for i, req in enumerate(requests_list):
        print(f"\nRequest {i+1}:")
        print(f"   {req['method']} {req['url']}")
        print(f"   Status: {req.get('response_status', 'No response')}")
        
        # Look for Apple/iCloud related URLs
        if any(domain in req['url'] for domain in ['apple.com', 'icloud.com', 'me.com']):
            analysis['apple_requests'].append(req)
            print(f"   🍎 Apple-related request detected")
        
        # Look for authentication endpoints
        if any(keyword in req['url'].lower() for keyword in ['auth', 'login', 'signin', 'validate']):
            analysis['authentication_requests'].append(req)
            print(f"   🔐 Authentication-related request detected")
        
        # Look for POST requests (likely authentication)
        if req['method'] == 'POST':
            analysis['post_requests'].append(req)
            print(f"   📤 POST request detected")
        
        # Look for credential usage in request data
        req_data_str = str(req.get('data', '')) + str(req.get('json_data', ''))
        if 'password' in req_data_str.lower() or 'anthony.destefano' in req_data_str:
            analysis['credential_usage'].append(req)
            print(f"   🔑 Credential usage detected")
        
        # Check for errors
        if req.get('error') or (req.get('response_status', 0) >= 400):
            analysis['errors'].append(req)
            print(f"   ❌ Error detected: {req.get('error', f'HTTP {req.get('response_status')}')}")
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   Total requests: {analysis['total_requests']}")
    print(f"   Apple requests: {len(analysis['apple_requests'])}")
    print(f"   Auth requests: {len(analysis['authentication_requests'])}")
    print(f"   POST requests: {len(analysis['post_requests'])}")
    print(f"   Credential usage: {len(analysis['credential_usage'])}")
    print(f"   Errors: {len(analysis['errors'])}")
    
    return analysis

def main():
    """
    Main monitoring workflow
    """
    print("=" * 80)
    print("🌐 HTTP Request Monitor for PyiCloud Authentication")
    print("=" * 80)
    
    # Load credentials
    print("\n📁 Loading credentials from settings...")
    creds = load_credentials_from_settings()
    
    if 'error' in creds:
        print(f"❌ Failed to load credentials: {creds['error']}")
        return
    
    email = creds['email']
    password = creds['password']
    
    if not email or not password:
        print(f"❌ Missing credentials - Email: '{email}', Password: '{password}'")
        return
    
    print(f"✅ Credentials loaded - Email: '{email}', Password: '{password}'")
    
    # Setup HTTP monitoring
    monitor = HTTPRequestMonitor()
    
    # Test with monitoring
    result = test_pyicloud_with_monitoring(email, password, monitor)
    
    # Get captured requests
    captured_requests = monitor.get_captured_requests()
    
    # Analyze requests
    analysis = analyze_authentication_requests(captured_requests)
    
    # Save results
    monitor.save_captured_requests()
    
    # Save analysis
    full_results = {
        'timestamp': datetime.now().isoformat(),
        'credentials': {'email': email, 'password': password},
        'test_result': result,
        'captured_requests': captured_requests,
        'analysis': analysis
    }
    
    with open('http_monitoring_results.json', 'w') as f:
        json.dump(full_results, f, indent=2, default=str)
    
    print(f"\n💾 Full results saved to: http_monitoring_results.json")
    
    # Summary
    print(f"\n" + "=" * 80)
    print("📊 MONITORING SUMMARY")
    print("=" * 80)
    
    print(f"🧪 Test Result: {'✅ Success' if result.get('success') else '❌ Failed'}")
    if not result.get('success'):
        print(f"   Error: {result.get('error_message', 'Unknown')}")
    
    print(f"🌐 HTTP Requests Captured: {len(captured_requests)}")
    print(f"🍎 Apple Requests: {len(analysis['apple_requests'])}")
    print(f"🔐 Auth Requests: {len(analysis['authentication_requests'])}")
    print(f"❌ Error Requests: {len(analysis['errors'])}")
    
    if analysis['errors']:
        print(f"\n🚨 ERROR DETAILS:")
        for error_req in analysis['errors'][:3]:  # Show first 3 errors
            print(f"   {error_req['method']} {error_req['url']}")
            print(f"   Status: {error_req.get('response_status', 'No response')}")
            print(f"   Error: {error_req.get('error', 'HTTP error')}")

if __name__ == "__main__":
    main()