# TM iSync Adapter - Troubleshooting Guide

## Table of Contents
- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Authentication Problems](#authentication-problems)
- [Sync Failures](#sync-failures)
- [Performance Issues](#performance-issues)
- [Dashboard Integration](#dashboard-integration)
- [Service Management](#service-management)
- [Network Connectivity](#network-connectivity)
- [File System Issues](#file-system-issues)
- [Error Messages](#error-messages)
- [Recovery Procedures](#recovery-procedures)
- [Advanced Diagnostics](#advanced-diagnostics)

## Quick Diagnostics

### 5-Minute Health Check

Run these commands to quickly identify issues:

```bash
# 1. Check if Dashboard is running
curl -s http://127.0.0.1:8000/api/health

# 2. Check adapter service status
launchctl list | grep tm-isync

# 3. Check recent logs for errors
tail -20 ~/Library/Logs/tm-isync-adapter.log | grep ERROR

# 4. Test iCloud configuration
curl -s http://127.0.0.1:8000/api/icloud/status

# 5. Verify file permissions
ls -la /path/to/your/source/folder
```

### Status Indicators

| Indicator | Meaning | Action |
|-----------|---------|--------|
| 🟢 Green | Everything working | No action needed |
| 🟡 Yellow | Warning/degraded | Review logs, may need attention |
| 🔴 Red | Error/failure | Immediate attention required |
| ⚪ Gray | Unknown/disconnected | Check service status |

## Installation Issues

### Problem: Installation Script Fails

**Symptoms:**
- `python3 install.py` returns errors
- Service not created
- Permission denied errors

**Solutions:**

1. **Check Python Version**
   ```bash
   python3 --version
   # Should be 3.6 or later
   ```

2. **Run with Proper Permissions**
   ```bash
   # If permission errors
   sudo python3 install.py
   
   # Or fix ownership
   sudo chown -R $(whoami) /path/to/adapter/
   ```

3. **Manual Service Installation**
   ```bash
   # Copy service file manually
   cp service.plist.template ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   
   # Edit paths in the plist file
   nano ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   
   # Load service
   launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

### Problem: Binary Not Found

**Symptoms:**
- "No such file or directory" for tm-isync-adapter
- Installation completes but service won't start

**Solutions:**

1. **Build Binary**
   ```bash
   cd /path/to/TM/isync/adapter
   make build
   ```

2. **Check Binary Permissions**
   ```bash
   chmod +x build/tm-isync-adapter
   ```

3. **Verify Binary Works**
   ```bash
   ./build/tm-isync-adapter --help
   ```

### Problem: Service Plist Errors

**Symptoms:**
- launchctl errors when loading service
- Service shows as "failed" status

**Solutions:**

1. **Validate Plist Syntax**
   ```bash
   plutil -lint ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

2. **Check Paths in Plist**
   ```bash
   cat ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   # Verify all paths exist and are accessible
   ```

3. **Regenerate Plist**
   ```bash
   python3 uninstall.py
   python3 install.py
   ```

## Authentication Problems

### Problem: iCloud Login Fails

**Symptoms:**
- "Authentication failed" in Dashboard
- Sync status shows "Disconnected"
- 401/403 errors in logs

**Solutions:**

1. **Verify Credentials**
   ```bash
   # Test credentials manually (be careful with password)
   curl -X POST http://127.0.0.1:8000/api/icloud/test-connection \
     -H "Content-Type: application/json" \
     -d '{"username":"your@email.com","password":"your-password"}'
   ```

2. **Use App-Specific Password**
   - Go to [appleid.apple.com](https://appleid.apple.com)
   - Generate app-specific password
   - Use this instead of regular password

3. **Check Apple ID Status**
   - Verify account is active
   - Check for security alerts
   - Ensure 2FA is properly configured

### Problem: Two-Factor Authentication Issues

**Symptoms:**
- Login prompts for 2FA code
- "Additional authentication required" errors

**Solutions:**

1. **Generate App-Specific Password**
   ```
   1. Sign in to appleid.apple.com
   2. Go to Security section
   3. Click "Generate Password" under App-Specific Passwords
   4. Use generated password in TM Dashboard
   ```

2. **Disable 2FA Temporarily** (Not recommended)
   - Only for testing
   - Re-enable after confirming basic functionality

3. **Check iCloud Keychain**
   - Ensure iCloud Keychain is enabled
   - May help with authentication persistence

## Sync Failures

### Problem: Files Not Syncing

**Symptoms:**
- New files appear but don't sync
- Dashboard shows "Last sync" with old timestamp
- No activity in logs

**Diagnostic Steps:**

1. **Check Service Status**
   ```bash
   launchctl list com.tm.isync.adapter
   # Should show PID if running
   ```

2. **Monitor File System Events**
   ```bash
   # Watch source folder for changes
   fswatch -o /path/to/source/folder
   ```

3. **Test Manual Sync**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/icloud/sync
   ```

**Solutions:**

1. **Restart Adapter Service**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

2. **Check Folder Permissions**
   ```bash
   # Source folder should be readable
   ls -la /path/to/source/folder
   
   # Fix permissions if needed
   chmod -R 755 /path/to/source/folder
   ```

3. **Verify Configuration**
   ```bash
   cat /path/to/adapter/config.json
   # Ensure paths are correct
   ```

### Problem: Partial Sync

**Symptoms:**
- Some files sync, others don't
- Inconsistent behavior
- Error logs for specific files

**Solutions:**

1. **Check File Names**
   ```bash
   # Look for problematic characters
   find /path/to/source -name "*[<>:|\"*?]*"
   ```

2. **Check File Sizes**
   ```bash
   # Large files may timeout
   find /path/to/source -size +100M
   ```

3. **Review File Permissions**
   ```bash
   # Check individual file permissions
   find /path/to/source -not -perm -644
   ```

### Problem: Sync Conflicts

**Symptoms:**
- Duplicate files appearing
- Files with conflict suffixes
- Data inconsistencies

**Solutions:**

1. **Manual Conflict Resolution**
   ```bash
   # Find conflict files
   find /path/to/source -name "*conflict*"
   
   # Review and merge manually
   ```

2. **Clear Local Cache**
   ```bash
   # Stop service
   launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   
   # Clear any cache files (if they exist)
   rm -rf ~/.tm-isync-cache
   
   # Restart service
   launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

3. **Force Full Resync**
   ```bash
   # Backup important files first
   curl -X POST http://127.0.0.1:8000/api/icloud/sync?force=true
   ```

## Performance Issues

### Problem: Slow Sync Performance

**Symptoms:**
- Sync operations take very long
- Dashboard shows slow progress
- High CPU or memory usage

**Diagnostic Steps:**

1. **Monitor Resource Usage**
   ```bash
   # Check CPU usage
   top -pid $(pgrep tm-isync-adapter)
   
   # Check memory usage
   ps -o pid,vsz,rss,comm -p $(pgrep tm-isync-adapter)
   ```

2. **Check Network Speed**
   ```bash
   # Test iCloud connectivity
   time curl -I https://www.icloud.com
   ```

3. **Analyze File Sizes**
   ```bash
   # Find large files
   find /path/to/source -size +50M -exec ls -lh {} \;
   ```

**Solutions:**

1. **Optimize Sync Schedule**
   - Sync during off-peak hours
   - Break large operations into smaller chunks
   - Use incremental sync when possible

2. **Network Optimization**
   ```bash
   # Check for network issues
   ping -c 5 icloud.com
   
   # Test bandwidth
   curl -w "@curl-format.txt" -o /dev/null -s https://www.icloud.com
   ```

3. **Resource Optimization**
   ```bash
   # Reduce concurrent operations
   # Edit config.json to limit concurrency
   "max_concurrent_uploads": 2
   ```

### Problem: High Memory Usage

**Symptoms:**
- System slows down during sync
- Memory warnings
- Adapter process consuming excessive RAM

**Solutions:**

1. **Check for Memory Leaks**
   ```bash
   # Monitor memory usage over time
   while true; do
     ps -o rss,comm -p $(pgrep tm-isync-adapter)
     sleep 60
   done
   ```

2. **Restart Service Periodically**
   ```bash
   # Add to cron for daily restart
   0 2 * * * launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist && launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

3. **Optimize Configuration**
   ```json
   {
     "batch_size": 10,
     "memory_limit_mb": 512,
     "gc_interval_minutes": 30
   }
   ```

## Dashboard Integration

### Problem: Dashboard Shows "Disconnected"

**Symptoms:**
- iCloud status shows disconnected
- Can't access sync controls
- API calls fail

**Solutions:**

1. **Check Dashboard Health**
   ```bash
   curl http://127.0.0.1:8000/api/health
   ```

2. **Verify API Endpoints**
   ```bash
   curl http://127.0.0.1:8000/api/icloud/status
   ```

3. **Restart Dashboard**
   ```bash
   cd /path/to/TM/dashboard
   ./restart.sh
   ```

### Problem: Configuration Not Saving

**Symptoms:**
- Settings don't persist after save
- Configuration reverts to defaults
- Error messages when saving

**Solutions:**

1. **Check File Permissions**
   ```bash
   ls -la /path/to/TM/dashboard/config/
   chmod 644 /path/to/TM/dashboard/config/icloud.json
   ```

2. **Validate JSON Format**
   ```bash
   python3 -m json.tool /path/to/TM/dashboard/config/icloud.json
   ```

3. **Manual Configuration**
   ```bash
   # Edit configuration directly
   nano /path/to/TM/dashboard/config/icloud.json
   ```

## Service Management

### Problem: Service Won't Start

**Symptoms:**
- launchctl load returns errors
- Service not in process list
- No log files created

**Solutions:**

1. **Check Service File**
   ```bash
   plutil -lint ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

2. **Manual Service Start**
   ```bash
   # Try running directly
   /path/to/adapter/tm-isync-adapter --config /path/to/config.json
   ```

3. **Fix Service Paths**
   ```bash
   # Update paths in plist file
   sed -i 's|OLD_PATH|NEW_PATH|g' ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

### Problem: Service Keeps Crashing

**Symptoms:**
- Service starts then stops immediately
- Crash logs in Console.app
- Exit codes in launchctl

**Solutions:**

1. **Review Crash Logs**
   ```bash
   # Check system logs
   log show --predicate 'process == "tm-isync-adapter"' --last 1h
   
   # Check crash reports
   ls ~/Library/Logs/DiagnosticReports/tm-isync-adapter*
   ```

2. **Run in Debug Mode**
   ```bash
   # Stop service
   launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   
   # Run manually with debug
   ./tm-isync-adapter --config config.json --debug
   ```

3. **Check Dependencies**
   ```bash
   # Verify all required files exist
   ldd tm-isync-adapter  # Linux
   otool -L tm-isync-adapter  # macOS
   ```

## Network Connectivity

### Problem: Cannot Connect to iCloud

**Symptoms:**
- "Connection refused" errors
- Timeouts in logs
- Network-related error messages

**Solutions:**

1. **Basic Network Tests**
   ```bash
   # Test basic connectivity
   ping icloud.com
   
   # Test HTTPS
   curl -I https://www.icloud.com
   
   # Test DNS resolution
   nslookup icloud.com
   ```

2. **Check Firewall Settings**
   ```bash
   # macOS firewall status
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   
   # List firewall rules
   sudo pfctl -sr
   ```

3. **Proxy Configuration**
   ```bash
   # Check proxy settings
   networksetup -getwebproxy "Wi-Fi"
   networksetup -getsecurewebproxy "Wi-Fi"
   ```

### Problem: Intermittent Connectivity

**Symptoms:**
- Sync works sometimes, fails other times
- Random timeout errors
- Inconsistent behavior

**Solutions:**

1. **Monitor Network Stability**
   ```bash
   # Continuous ping test
   ping -i 5 icloud.com > network_test.log &
   
   # Monitor for drops
   tail -f network_test.log | grep "timeout"
   ```

2. **Implement Retry Logic**
   ```json
   {
     "retry_attempts": 3,
     "retry_delay_seconds": 10,
     "timeout_seconds": 30
   }
   ```

3. **Check WiFi Power Management**
   ```bash
   # Disable WiFi power management
   sudo pmset -a womp 0
   ```

## File System Issues

### Problem: Permission Denied Errors

**Symptoms:**
- "Permission denied" in logs
- Unable to read/write files
- Sync operations fail

**Solutions:**

1. **Fix File Permissions**
   ```bash
   # Fix source folder permissions
   chmod -R 755 /path/to/source/folder
   
   # Fix ownership
   chown -R $(whoami) /path/to/source/folder
   ```

2. **Check Parent Directory Permissions**
   ```bash
   # Ensure parent directories are accessible
   ls -la /path/to/source/
   ```

3. **Grant Full Disk Access** (macOS Catalina+)
   - System Preferences → Security & Privacy → Privacy
   - Select "Full Disk Access"
   - Add Terminal or the adapter binary

### Problem: Disk Space Issues

**Symptoms:**
- "No space left on device" errors
- Sync stops unexpectedly
- Performance degradation

**Solutions:**

1. **Check Available Space**
   ```bash
   df -h /path/to/source/folder
   ```

2. **Clean Up Old Files**
   ```bash
   # Find large files
   find /path/to/source -size +100M
   
   # Find old temporary files
   find /path/to/source -name "*.tmp" -mtime +7
   ```

3. **Configure Space Monitoring**
   ```json
   {
     "min_free_space_mb": 1024,
     "space_check_interval": 300
   }
   ```

## Error Messages

### Common Error Messages and Solutions

#### "Authentication failed"
**Cause:** Invalid iCloud credentials or expired session
**Solution:**
1. Verify username and password in Dashboard
2. Generate app-specific password if using 2FA
3. Check Apple ID account status

#### "File not found"
**Cause:** Source file deleted or moved during sync
**Solution:**
1. Check if file still exists
2. Restart sync operation
3. Review file deletion policies

#### "Connection timeout"
**Cause:** Network issues or slow iCloud response
**Solution:**
1. Check internet connection
2. Increase timeout values in configuration
3. Retry operation

#### "Invalid configuration"
**Cause:** Malformed config.json or missing required fields
**Solution:**
1. Validate JSON syntax
2. Check all required fields are present
3. Regenerate configuration from Dashboard

#### "Service unavailable"
**Cause:** iCloud service downtime or maintenance
**Solution:**
1. Check iCloud status at apple.com/support/systemstatus
2. Wait and retry later
3. Enable automatic retry logic

#### "Quota exceeded"
**Cause:** iCloud storage limit reached
**Solution:**
1. Check iCloud storage usage
2. Delete unnecessary files
3. Upgrade iCloud storage plan

## Recovery Procedures

### Complete System Recovery

If the entire sync system fails:

1. **Stop All Services**
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   ```

2. **Backup Current State**
   ```bash
   # Backup configuration
   cp /path/to/adapter/config.json config.json.backup
   
   # Backup source files
   rsync -av /path/to/source/ /path/to/backup/
   ```

3. **Clean Install**
   ```bash
   # Uninstall
   python3 uninstall.py
   
   # Remove all traces
   rm -rf ~/Library/LaunchAgents/com.tm.isync.adapter.plist
   rm -rf ~/Library/Logs/tm-isync-adapter.log
   
   # Fresh install
   python3 install.py
   ```

4. **Restore Configuration**
   ```bash
   # Restore config
   cp config.json.backup /path/to/adapter/config.json
   
   # Test configuration
   curl -X POST http://127.0.0.1:8000/api/icloud/test-connection
   ```

### Data Recovery

If sync data is corrupted:

1. **Identify Corruption**
   ```bash
   # Check file integrity
   find /path/to/source -name "*.pdf" -exec file {} \;
   
   # Look for zero-byte files
   find /path/to/source -size 0
   ```

2. **Restore from Backup**
   ```bash
   # Local backup
   rsync -av /path/to/backup/ /path/to/source/
   
   # iCloud restore (if available)
   # Use iCloud web interface or Time Machine
   ```

3. **Verify Restoration**
   ```bash
   # Check file counts
   find /path/to/source -type f | wc -l
   
   # Verify file sizes
   du -sh /path/to/source
   ```

## Advanced Diagnostics

### Comprehensive System Check

Run this script for a full system diagnostic:

```bash
#!/bin/bash
echo "=== TM iSync Adapter Diagnostic ==="
echo "Timestamp: $(date)"
echo

echo "1. System Information"
echo "macOS Version: $(sw_vers -productVersion)"
echo "Architecture: $(uname -m)"
echo

echo "2. Service Status"
launchctl list | grep tm-isync || echo "Service not found"
echo

echo "3. Process Information"
ps aux | grep tm-isync-adapter | grep -v grep || echo "Process not running"
echo

echo "4. Network Connectivity"
ping -c 3 icloud.com > /dev/null && echo "iCloud reachable" || echo "iCloud unreachable"
echo

echo "5. File System"
echo "Source folder: $(ls -ld /path/to/source 2>/dev/null || echo 'Not found')"
echo "Free space: $(df -h /path/to/source | tail -1 | awk '{print $4}')"
echo

echo "6. Configuration"
echo "Config exists: $(test -f /path/to/adapter/config.json && echo 'Yes' || echo 'No')"
echo "Dashboard config: $(test -f /path/to/dashboard/config/icloud.json && echo 'Yes' || echo 'No')"
echo

echo "7. Recent Errors"
tail -10 ~/Library/Logs/tm-isync-adapter.log 2>/dev/null | grep ERROR || echo "No recent errors"
echo

echo "8. Dashboard Health"
curl -s http://127.0.0.1:8000/api/health > /dev/null && echo "Dashboard responding" || echo "Dashboard not responding"
echo

echo "=== End Diagnostic ==="
```

### Log Analysis

Analyze logs for patterns:

```bash
#!/bin/bash
LOG_FILE=~/Library/Logs/tm-isync-adapter.log

echo "=== Log Analysis ==="
echo "Total log entries: $(wc -l < $LOG_FILE)"
echo "Error count: $(grep -c ERROR $LOG_FILE)"
echo "Warning count: $(grep -c WARN $LOG_FILE)"
echo

echo "Recent errors:"
grep ERROR $LOG_FILE | tail -5
echo

echo "Most common errors:"
grep ERROR $LOG_FILE | awk '{print $4}' | sort | uniq -c | sort -nr | head -5
echo

echo "Sync operations:"
grep "sync completed" $LOG_FILE | tail -5
```

### Performance Monitoring

Monitor system performance during sync:

```bash
#!/bin/bash
PID=$(pgrep tm-isync-adapter)

if [ -z "$PID" ]; then
    echo "Adapter not running"
    exit 1
fi

echo "Monitoring adapter performance (PID: $PID)"
echo "Press Ctrl+C to stop"

while true; do
    CPU=$(ps -o %cpu -p $PID | tail -1)
    MEM=$(ps -o %mem -p $PID | tail -1)
    RSS=$(ps -o rss -p $PID | tail -1)
    
    echo "$(date +'%H:%M:%S') CPU: ${CPU}% MEM: ${MEM}% RSS: ${RSS}KB"
    sleep 5
done
```

---

## Quick Reference

### Essential Commands
```bash
# Check service status
launchctl list com.tm.isync.adapter

# View logs
tail -f ~/Library/Logs/tm-isync-adapter.log

# Test connection
curl -X POST http://127.0.0.1:8000/api/icloud/test-connection

# Manual sync
curl -X POST http://127.0.0.1:8000/api/icloud/sync

# Restart service
launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
```

### Important Paths
- Service: `~/Library/LaunchAgents/com.tm.isync.adapter.plist`
- Logs: `~/Library/Logs/tm-isync-adapter.log`
- Config: `/path/to/adapter/config.json`
- Dashboard: `http://127.0.0.1:8000`

### Emergency Contacts
- Check system status: Dashboard → Settings → iCloud
- Review documentation: `USER_GUIDE.md`, `DEVELOPER.md`
- Collect logs before requesting support

---

*Last updated: 2025-07-15*
*Document version: 1.0.0*