# TM iSync Adapter Installation Instructions

## Prerequisites

- macOS 10.14 or later
- Python 3.8 or later
- iCloud Drive enabled and syncing
- Terminal/command line access

## Installation Steps

### 1. Extract Package
```bash
tar -xzf tm-isync-adapter.tar.gz
cd tm-isync-adapter/
```

### 2. Verify Files
You should see:
- `tm-isync-adapter` (executable)
- `config.json` (configuration)
- `install.py` (installer)
- `uninstall.py` (uninstaller)
- `service.plist.template` (service template)

### 3. Run Installation
```bash
python3 install.py
```

The installer will:
- Create service directory: `~/Library/TM-iCloud-Sync/`
- Copy files to installation directory
- Register macOS service with launchd
- Start service automatically

### 4. Verify Installation
```bash
# Check service is loaded
launchctl list com.tm.isync.adapter

# View real-time logs
tail -f ~/Library/TM-iCloud-Sync/logs/adapter.log
```

## Configuration

### Update Settings
Edit: `~/Library/TM-iCloud-Sync/config.json`

```json
{
    "icloud_parent_folder": "CASES",
    "local_tm_path": "/Users/corelogic/satori-dev/TM/test-data/sync-test-cases",
    "sync_interval": 30,
    "log_level": "info",
    "backup_enabled": false
}
```

### Restart After Changes
```bash
launchctl stop com.tm.isync.adapter
launchctl start com.tm.isync.adapter
```

## Troubleshooting

### Service Won't Start
1. Check logs: `cat ~/Library/TM-iCloud-Sync/logs/adapter.error.log`
2. Verify iCloud Drive path exists
3. Check file permissions: `ls -la ~/Library/TM-iCloud-Sync/`

### Files Not Syncing
1. Verify iCloud folder exists: `ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/`
2. Check sync interval setting in config
3. Monitor logs for error messages

### Permission Issues
1. Uninstall: `python3 uninstall.py`
2. Reinstall: `python3 install.py`

## Uninstallation

To completely remove the adapter:

```bash
python3 uninstall.py
```

This removes:
- All installed files
- Service registration
- Log files (optional)
- Configuration files

## Support

- **Logs**: `~/Library/TM-iCloud-Sync/logs/`
- **Config**: `~/Library/TM-iCloud-Sync/config.json`
- **Service**: `~/Library/LaunchAgents/com.tm.isync.adapter.plist`
