# In sync_manager.py
def run_sync(self):
    config = self.get_icloud_config()
    # It's good practice to store the cookie dir outside the main code
    cookie_dir = config.get('cookie_directory', './.icloud')

    # For automated runs, you might omit the password after the first login
    # The library will rely on the cookies.
    service = iCloudService(cookie_directory=cookie_dir)
    result = service.connect(config['account'], config['password'])

    if result['success']:
        # ... proceed with your folder syncing logic ...
        legal_cases_folder = service.drive['LegalCases'] # Example
    else:
        print(f"Error connecting to iCloud: {result['error']}")