# Creating a Desktop Icon for Satori Secure File Sync

Follow these steps to create a professional desktop application icon for Satori Secure File Sync:

## Step 1: Convert AppleScript to Application

1. **Open Script Editor**
   - Press `Cmd + Space` and type "Script Editor"
   - Press Enter to open the application

2. **Open the AppleScript**
   - In Script Editor, go to `File > Open`
   - Navigate to: `/Users/corelogic/satori-dev/TM/isync/adapter/run.applescript`
   - Click Open

3. **Export as Application**
   - Go to `File > Export...`
   - Set these options:
     - **File Format:** Application
     - **Name:** Satori Secure File Sync
     - **Where:** Desktop (or your preferred location)
     - **Options:** 
       - ✅ Stay open after run handler (if available)
       - ❌ Show startup screen (uncheck)
   - Click Save

## Step 2: Add Custom Icon (Optional)

1. **Prepare Icon Image**
   - Find or create a vault/security-themed icon (512x512 pixels recommended)
   - Save as PNG format

2. **Apply Icon to Application**
   - Right-click on "Satori Secure File Sync.app" on your Desktop
   - Select "Get Info"
   - Drag your icon image onto the small icon in the top-left of the Info window
   - The icon will update immediately

## Step 3: Usage

- **Double-click** the Satori Secure File Sync app icon to start the service
- A Terminal window will open showing real-time sync status
- Keep the Terminal window open while syncing
- Press `Ctrl+C` in the Terminal to stop the service
- Close the Terminal window when done

## Step 4: Add to Dock (Optional)

1. Drag the "Satori Secure File Sync.app" to your Dock for easy access
2. Right-click the Dock icon and select "Options > Keep in Dock"

## Alternative: Command Line Creation

If you prefer using the command line:

```bash
# Create the app using osacompile
cd /Users/corelogic/satori-dev/TM/isync/adapter/
osacompile -o ~/Desktop/Satori\ Secure\ File\ Sync.app run.applescript

# Make it executable
chmod +x ~/Desktop/Satori\ Secure\ File\ Sync.app/Contents/MacOS/applet
```

## Troubleshooting

- If the app doesn't open, check Security & Privacy settings
- You may need to right-click and select "Open" the first time
- If you see "unidentified developer" warning, go to System Preferences > Security & Privacy and click "Open Anyway"

---

**Note:** This creates a simple launcher app without Apple notarization. It's perfect for personal/team use but would need Developer ID signing for broader distribution.