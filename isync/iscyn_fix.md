Your investigation was spot-on. You correctly identified the failing components and asked all the right questions. The core issue is that pyicloud is a casualty of Apple's evolving security, and your project now requires a more modern tool to keep pace. Due to its reliance on deprecated private APIs and lack of maintenance, pyicloud is no longer a reliable choice for production systems. The constant risk of Apple making breaking changes without notice is too high.

 The most robust alternative is icloudpd. While its name suggests it's only for photos, its underlying authentication logic is the most up-to-date and is used by many to script interactions with iCloud Drive. It successfully handles the modern 2FA and web session authentication that pyicloud cannot.

 Is the OAuth Client ID still valid? (Hardcoded in library)

Likely not in this context. Apple's new authentication flow is more sophisticated. It expects a full browser-like session and generates tokens differently. The simple, hardcoded client ID is a relic of the older, now-defunct authentication method.

Do we need different authentication for production vs development?

No, the authentication method is the same. The key is using a library that can handle Apple's current method, regardless of the environment.

Apple Service Assumptions
Is idmsa.apple.com the correct endpoint for app-specific passwords?

It was the primary endpoint for the SRP handshake. However, Apple now requires a multi-step flow that involves other endpoints and likely requires session cookies obtained from a web-like login, making a direct call to this single endpoint insufficient.

Are app-specific passwords supposed to work with PyiCloud?

They were the correct way to use pyicloud. The failure is not in the password itself, but in the entire authentication protocol the library attempts to use.

Does Apple require different authentication for server applications?

Apple does not officially support this kind of third-party server application access to user iCloud data. The CloudKit Web Services are the "official" way, but they are for an application to access its own container, not a user's general iCloud Drive. Therefore, any library you use is essentially mimicking a web browser, and must be updated as the web login process changes.

Are there rate limits or usage restrictions we're hitting?

Yes. The HTTP 503 Service Temporarily Unavailable error you are seeing is almost certainly a temporary lockout from Apple's servers after repeated failed authentication attempts. This is a security measure. Once you switch to a working method, these should disappear.

By switching to icloudpd and adapting to its cookie-based session management, you will move from a broken, frustrating experience to a stable, reliable connection for your client's application.


Recommended New Approach: Using icloudpd
The community has largely coalesced around the authentication methods used in icloudpd as the most reliable way to connect to iCloud from Python. It handles the complex, cookie-based session authentication required now.

How it Works
Instead of a simple username/password function call, the process involves:

Initial Login: On the very first run, icloudpd will prompt for the Apple ID, password, and the 2FA code.

Session Cookie Storage: Upon successful login, it saves the session cookies to a specified location (e.g., a ./.icloud_session file).

Subsequent Logins: For all future connections, you provide the username and the path to the cookie file, bypassing the need for the password and 2FA prompts. This is ideal for automated scripts.

Updated Implementation Example
First, you need to install the library:

pip install icloudpd


Next, you'll need to refactor your iCloudService to use this new library.
/Users/corelogic/satori-dev/TM/isync/icloudpd.py


How to Adapt Your Workflow
Update settings.json: Add a path for the cookies.

`{
  "icloud": {
    "account": "anthony.destefano@gmail.com",
    "password": "gqlv-uvis-tvze-ofhg", 
    "folder": "/LegalCases",
    "cookie_directory": "./icloud_session_data"
  }
}`


Perform Initial Interactive Login: The first time you run your application with a new Apple ID, you must do it from a command line where you can type. The library will prompt you:

Enter the 2FA code:



Once you enter the code, it will save the session in the cookie_directory. Every subsequent run will be non-interactive.

Modify sync_manager.py: Update your manager to pass the cookie directory.

/Users/corelogic/satori-dev/TM/isync/sync_manager_update.py


By switching to icloudpd and adapting to its cookie-based session management, you will move from a broken, frustrating experience to a stable, reliable connection for your client's application.