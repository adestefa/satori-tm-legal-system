# TM iSync Adapter Installation Guide

**Professional macOS Service for Tiger-Monkey Legal Document Processing**

## Overview

The TM iSync Adapter creates a seamless bridge between your local Tiger-Monkey installation and iCloud Drive, automatically synchronizing case files and integrating with the Dashboard workflow.

## System Requirements

- **macOS 10.14+** (Mojave or later)
- **Python 3.8+** for installation scripts
- **iCloud Drive** enabled and configured
- **Tiger-Monkey Dashboard** running locally
- **Terminal/command line** access
- **Go 1.19+** (if building from source)

## Installation Methods

### Method 1: Dashboard Package Download (Recommended)

1. **Configure in Dashboard**:
   - Open TM Dashboard → Settings → iCloud
   - Configure your iCloud folder settings
   - Click "Download Adapter Package"

2. **Extract and Install**:
   ```bash
   tar -xzf tm-isync-adapter-*.tar.gz
   cd tm-isync-adapter/
   python3 install.py
   ```

### Method 2: Build from Source

1. **Clone/Navigate to Source**:
   ```bash
   cd /path/to/TM/isync/adapter/
   ```

2. **Build Binary**:
   ```bash
   make build
   ```

3. **Install**:
   ```bash
   python3 install.py
   ```

## Installation Process

The Python installer (`install.py`) performs these steps:

1. **System Requirements Check**:
   - Verifies macOS version
   - Checks for required files
   - Validates Python version

2. **Directory Creation**:
   - `~/Library/TM-iCloud-Sync/` (main installation)
   - `~/Library/TM-iCloud-Sync/logs/` (service logs)
   - `~/Library/LaunchAgents/` (service registration)

3. **File Installation**:
   - Copies Go binary with executable permissions
   - Installs configuration file
   - Sets up service template

4. **Service Registration**:
   - Creates macOS launchd service
   - Registers for automatic startup
   - Starts service immediately

5. **Verification**:
   - Tests binary execution
   - Verifies service registration
   - Confirms file permissions

## Installation Verification

After installation, verify everything is working:

```bash
# Check service is loaded
launchctl list com.tm.isync.adapter

# Verify installation directory
ls -la ~/Library/TM-iCloud-Sync/

# Monitor real-time logs
tail -f ~/Library/TM-iCloud-Sync/logs/adapter.log

# Test service status
launchctl print user/$(id -u)/com.tm.isync.adapter
```

## Configuration

### Default Configuration

The installer creates `~/Library/TM-iCloud-Sync/config.json`:

```json
{
  "icloud_parent_folder": "TM_Cases",
  "local_tm_path": "/Users/username/TM/test-data/sync-test-cases",
  "sync_interval": 30,
  "log_level": "info",
  "backup_enabled": true
}
```

### Configuration Options

- **`icloud_parent_folder`**: iCloud Drive folder name for cases
- **`local_tm_path`**: Local TM directory path
- **`sync_interval`**: Sync frequency in seconds (minimum: 10)
- **`log_level`**: Logging level (`debug`, `info`, `warn`, `error`)
- **`backup_enabled`**: Create backups before sync operations

### Updating Configuration

1. **Edit configuration**:
   ```bash
   nano ~/Library/TM-iCloud-Sync/config.json
   ```

2. **Restart service**:
   ```bash
   launchctl stop com.tm.isync.adapter
   launchctl start com.tm.isync.adapter
   ```

## Service Management

### Manual Service Control

```bash
# Start service
launchctl start com.tm.isync.adapter

# Stop service
launchctl stop com.tm.isync.adapter

# Restart service
launchctl stop com.tm.isync.adapter && launchctl start com.tm.isync.adapter

# Check service status
launchctl list com.tm.isync.adapter

# View service details
launchctl print user/$(id -u)/com.tm.isync.adapter
```

### Automatic Startup

The service is configured to start automatically:
- **At login** (user-level LaunchAgent)
- **After crashes** (KeepAlive enabled)
- **With throttling** (10-second intervals to prevent rapid restarts)

### Log Management

Log files are located in `~/Library/TM-iCloud-Sync/logs/`:

- **`adapter.log`**: Main service output
- **`adapter.error.log`**: Error messages and stack traces
- **`install.log`**: Installation process log

```bash
# View current logs
tail -f ~/Library/TM-iCloud-Sync/logs/adapter.log

# View error logs
cat ~/Library/TM-iCloud-Sync/logs/adapter.error.log

# View installation log
cat ~/Library/TM-iCloud-Sync/logs/install.log
```

## Architecture Details

### Service Structure

```
~/Library/TM-iCloud-Sync/
├── tm-isync-adapter          # Go binary
├── config.json               # Configuration
├── service.plist             # Generated service definition
├── logs/                     # Service logs
│   ├── adapter.log           # stdout
│   ├── adapter.error.log     # stderr
│   └── install.log           # installer log
└── README.md                 # User documentation
```

### Integration Points

1. **iCloud Drive**: `~/Library/Mobile Documents/com~apple~CloudDocs/`
2. **TM Directory**: Configured local path for Tiger-Monkey
3. **Dashboard**: Real-time case detection and processing
4. **macOS Services**: Integrated with launchd for reliability

### Security Considerations

- **User-level service**: Runs with user permissions only
- **Local file access**: Only accesses configured directories
- **No network access**: Works entirely with local file system
- **Audit logging**: All operations logged for transparency

## Troubleshooting

### Common Issues

#### Service Won't Start

**Symptoms**: Service shows as not loaded
```bash
launchctl list com.tm.isync.adapter
# No output or error
```

**Solutions**:
1. Check error logs:
   ```bash
   cat ~/Library/TM-iCloud-Sync/logs/adapter.error.log
   ```

2. Verify file permissions:
   ```bash
   ls -la ~/Library/TM-iCloud-Sync/tm-isync-adapter
   # Should show: -rwxr-xr-x
   ```

3. Test binary manually:
   ```bash
   ~/Library/TM-iCloud-Sync/tm-isync-adapter -version
   ```

4. Reinstall service:
   ```bash
   python3 uninstall.py
   python3 install.py
   ```

#### Files Not Syncing

**Symptoms**: No files appear in TM directory
```bash
ls ~/TM/test-data/sync-test-cases/
# Directory empty or missing new cases
```

**Solutions**:
1. Verify iCloud Drive path:
   ```bash
   ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/TM_Cases/
   ```

2. Check sync interval in config (may be too long)
3. Monitor logs for sync attempts:
   ```bash
   tail -f ~/Library/TM-iCloud-Sync/logs/adapter.log | grep -i sync
   ```

4. Verify local TM path exists and is writable:
   ```bash
   ls -la ~/TM/test-data/sync-test-cases/
   touch ~/TM/test-data/sync-test-cases/test.txt
   ```

#### Permission Denied Errors

**Symptoms**: Errors in logs about file permissions
```
Error: permission denied accessing /path/to/file
```

**Solutions**:
1. Check iCloud Drive permissions:
   ```bash
   ls -la ~/Library/Mobile\ Documents/com~apple~CloudDocs/
   ```

2. Verify TM directory permissions:
   ```bash
   ls -la ~/TM/test-data/
   chmod 755 ~/TM/test-data/sync-test-cases/
   ```

3. Full reinstall:
   ```bash
   python3 uninstall.py
   python3 install.py
   ```

#### Configuration Issues

**Symptoms**: Service starts but doesn't sync correctly

**Solutions**:
1. Validate JSON syntax:
   ```bash
   python3 -m json.tool ~/Library/TM-iCloud-Sync/config.json
   ```

2. Check all paths exist:
   ```bash
   # iCloud path
   ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/TM_Cases/
   
   # Local TM path
   ls ~/TM/test-data/sync-test-cases/
   ```

3. Reset to defaults:
   ```bash
   cp config.json ~/Library/TM-iCloud-Sync/config.json
   launchctl restart com.tm.isync.adapter
   ```

### Advanced Debugging

#### Enable Debug Logging

1. Edit config file:
   ```json
   {
     "log_level": "debug"
   }
   ```

2. Restart service:
   ```bash
   launchctl restart com.tm.isync.adapter
   ```

3. Monitor detailed logs:
   ```bash
   tail -f ~/Library/TM-iCloud-Sync/logs/adapter.log
   ```

#### Manual Testing

Run the adapter manually for testing:

```bash
# Stop the service
launchctl stop com.tm.isync.adapter

# Run manually with verbose output
~/Library/TM-iCloud-Sync/tm-isync-adapter -config ~/Library/TM-iCloud-Sync/config.json

# Start service again
launchctl start com.tm.isync.adapter
```

## Uninstallation

### Complete Removal

To completely remove the adapter:

```bash
python3 uninstall.py
```

This removes:
- All installed files (`~/Library/TM-iCloud-Sync/`)
- Service registration (`~/Library/LaunchAgents/com.tm.isync.adapter.plist`)
- Log files (optional - can be preserved)

### Verification

After uninstallation:

```bash
# Verify service is unloaded
launchctl list com.tm.isync.adapter
# Should show: No such process

# Verify files are removed
ls ~/Library/TM-iCloud-Sync/
# Should show: No such file or directory

# Verify service file is removed
ls ~/Library/LaunchAgents/com.tm.isync.adapter.plist
# Should show: No such file or directory
```

### Uninstall Options

```bash
# Standard uninstall
python3 uninstall.py

# Preserve log files
python3 uninstall.py --preserve-logs

# Force uninstall without confirmation
python3 uninstall.py --force

# Verbose output
python3 uninstall.py --verbose
```

## Support and Maintenance

### Log Rotation

Logs are automatically managed by macOS. For manual cleanup:

```bash
# Archive old logs
cd ~/Library/TM-iCloud-Sync/logs/
gzip adapter.log.old

# Clear current logs (service will recreate)
> adapter.log
> adapter.error.log
```

### Performance Monitoring

Monitor service performance:

```bash
# Check memory usage
ps aux | grep tm-isync-adapter

# Monitor file operations
fs_usage -w -f filesys tm-isync-adapter

# Check service health
launchctl print user/$(id -u)/com.tm.isync.adapter | grep -E "(state|exit)"
```

### Updates

To update the adapter:

1. **Download new package** from Dashboard
2. **Stop current service**:
   ```bash
   launchctl stop com.tm.isync.adapter
   ```
3. **Backup configuration**:
   ```bash
   cp ~/Library/TM-iCloud-Sync/config.json ~/Desktop/tm-config-backup.json
   ```
4. **Uninstall old version**:
   ```bash
   python3 uninstall.py --preserve-logs
   ```
5. **Install new version**:
   ```bash
   python3 install.py
   ```
6. **Restore configuration**:
   ```bash
   cp ~/Desktop/tm-config-backup.json ~/Library/TM-iCloud-Sync/config.json
   launchctl restart com.tm.isync.adapter
   ```

---

For additional support, check the service logs and verify your configuration matches the expected format. The adapter is designed to be robust and self-healing, automatically retrying failed operations and logging detailed information for troubleshooting.