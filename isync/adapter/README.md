# Satori Secure File Sync

A professional file synchronization service that monitors your iCloud Drive CASES folder and automatically uploads new legal documents to your Tiger-Monkey (TM) Dashboard.

## Quick Start

### For Local Testing (Default)
Double-click `run-local.applescript` or run:
```bash
./run.sh local
```
This syncs to your local TM Dashboard at http://127.0.0.1:8000

### For Production (Linode Server)
Double-click `run-production.applescript` or run:
```bash
./run.sh production
```
This syncs to your production TM Dashboard at http://198.74.59.11

## Configuration

The service uses separate configuration files for each environment:

- **config-local.json** - For local development/testing
- **config-production.json** - For production Linode server

### Configuration Options

```json
{
  "icloud_parent_folder": "CASES",           // iCloud folder to monitor
  "api_endpoint": "http://...",              // Dashboard upload endpoint
  "api_key": "your-api-key",                 // Authentication key
  "sync_interval": 30,                       // Sync check interval (seconds)
  "log_level": "info",                       // Logging level
  "backup_enabled": false,                   // Enable/disable backups
  "environment": "local"                     // Environment name
}
```

## Usage

### GUI Method (Recommended)

1. **Create Desktop Icons** (one-time setup):
   - Open `run-local.applescript` in Script Editor
   - Export as Application → Save to Desktop as "Sync to Local"
   - Open `run-production.applescript` in Script Editor  
   - Export as Application → Save to Desktop as "Sync to Linode"

2. **Run the Service**:
   - Double-click the appropriate desktop icon
   - A Terminal window opens showing sync status
   - Files are uploaded as they appear in iCloud

3. **Stop the Service**:
   - Press `Ctrl+C` in the Terminal window
   - Close the Terminal window

### Command Line Method

```bash
# Run with specific environment
./run.sh local        # Sync to local Dashboard
./run.sh production   # Sync to Linode server

# Or use the convenience scripts
./run-local.sh        # Quick local sync
./run-production.sh   # Quick production sync
```

## How It Works

1. **File Detection**: Monitors your iCloud Drive `CASES` folder for new files
2. **Automatic Upload**: Uploads files to the configured TM Dashboard endpoint
3. **Real-time Status**: Shows upload progress in Terminal window
4. **Folder Structure**: Maintains the same folder structure on the server

## Troubleshooting

### Service won't start
- Check that Dashboard is running (for local testing)
- Verify the API endpoint in config file
- Ensure iCloud Drive is enabled and synced

### Files not uploading
- Check Terminal for error messages
- Verify network connectivity
- Ensure proper API key in configuration

### Permission errors
- First run may require security approval
- Right-click app and select "Open" if you see "unidentified developer"

## Security Notes

- API keys are stored in local config files
- Use different API keys for local vs production
- Config files should not be committed to git
- All uploads use secure HTTP POST with authentication

## Support

For issues or questions, contact the Tiger-Monkey development team.
