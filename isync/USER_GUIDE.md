# TM iSync Adapter - Complete User Guide

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Installation](#installation)
- [Using the Sync Adapter](#using-the-sync-adapter)
- [Monitoring and Management](#monitoring-and-management)
- [File Organization](#file-organization)
- [Best Practices](#best-practices)
- [FAQ](#faq)
- [Support](#support)

## Overview

The TM iSync Adapter provides seamless two-way synchronization between your local Tiger-Monkey case files and iCloud storage. This enables:

- **Automatic Case Syncing**: New case folders automatically sync from iCloud to your local TM system
- **Real-time Monitoring**: Dashboard interface shows sync status and file operations
- **Bidirectional Sync**: Changes in local files sync back to iCloud
- **Professional Integration**: Seamless integration with TM Dashboard and case processing workflow

### Key Benefits
- 📁 **Centralized Storage**: All case files accessible across devices via iCloud
- 🔄 **Automatic Sync**: No manual file copying required
- 📊 **Dashboard Integration**: Monitor sync status from TM Dashboard
- 🛡️ **Reliable**: Built-in error handling and recovery
- 🖥️ **macOS Native**: Leverages macOS service architecture

## System Requirements

### Hardware Requirements
- **Mac**: macOS 10.15 (Catalina) or later
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for adapter and case files
- **Network**: Stable internet connection for iCloud access

### Software Requirements
- **iCloud Account**: Active iCloud account with sufficient storage
- **TM Dashboard**: Running TM Dashboard (v1.9.0 or later)
- **Go Runtime**: Automatically included in package
- **Python 3**: For installation scripts (usually pre-installed on macOS)

### iCloud Configuration
- iCloud Drive must be enabled
- Sufficient iCloud storage for case files
- Two-factor authentication may be required

## Getting Started

### Step 1: Access iCloud Configuration

1. **Open TM Dashboard**
   ```
   http://127.0.0.1:8000
   ```

2. **Navigate to Settings**
   - Click "Settings" in the main navigation
   - Select "iCloud Integration" tab

3. **Configure iCloud Settings**
   - Enter your iCloud credentials
   - Set source and target folders
   - Test connection

### Step 2: Download and Install

1. **Generate Adapter Package**
   - Click "Download iSync Adapter" in Dashboard
   - Package automatically includes your configuration
   - Save the downloaded ZIP file

2. **Install the Adapter**
   - Extract the ZIP file
   - Run the installation script
   - Follow setup prompts

### Step 3: Verify Installation

1. **Check Service Status**
   - Service should start automatically
   - Verify in Dashboard iCloud status page
   - Monitor initial sync operations

## Configuration

### Dashboard Configuration

Access the iCloud configuration page in TM Dashboard:

#### Required Settings

**iCloud Credentials**
```
Username: your-apple-id@email.com
Password: your-icloud-password
```

**Folder Configuration**
```
Source Folder: /Users/yourname/Documents/TM-Cases
Target Folder: TM-Cases
```

#### Configuration Options

| Setting | Description | Example |
|---------|-------------|---------|
| Username | iCloud Apple ID | `user@icloud.com` |
| Password | iCloud password or app-specific password | `abcd-efgh-ijkl-mnop` |
| Source Folder | Local TM case directory | `/Users/john/Documents/TM-Cases` |
| Target Folder | iCloud folder name | `TM-Cases` |

### Advanced Configuration

#### App-Specific Passwords
For accounts with two-factor authentication:

1. **Generate App-Specific Password**
   - Go to [appleid.apple.com](https://appleid.apple.com)
   - Sign in and go to "Security" section
   - Generate app-specific password
   - Use this password instead of your regular password

2. **Configure in Dashboard**
   - Use your Apple ID as username
   - Use app-specific password as password

#### Folder Path Guidelines

**Source Folder Best Practices:**
```bash
# Good examples
/Users/john/Documents/TM-Cases
/Users/lawfirm/Desktop/Cases
/Volumes/External/TM-Cases

# Avoid
/tmp/cases                    # Temporary directory
/System/Library/Cases         # System directory
Cases                         # Relative path
```

**Target Folder Guidelines:**
- Use simple names (no spaces or special characters)
- Should not conflict with existing iCloud folders
- Will be created automatically if it doesn't exist

## Installation

### Automatic Installation (Recommended)

1. **Download Package from Dashboard**
   ```
   TM Dashboard → Settings → iCloud → Download iSync Adapter
   ```

2. **Extract and Install**
   ```bash
   # Extract downloaded package
   unzip tm-isync-adapter.zip
   cd tm-isync-adapter
   
   # Run installation
   python3 install.py
   ```

3. **Follow Installation Prompts**
   - Confirm installation paths
   - Grant necessary permissions
   - Service will start automatically

### Manual Installation

If automatic installation fails:

1. **Build from Source**
   ```bash
   cd /path/to/TM/isync/adapter
   make build
   ```

2. **Configure Manually**
   ```bash
   # Copy configuration
   cp config.json.template config.json
   # Edit config.json with your settings
   ```

3. **Install Service**
   ```bash
   python3 install.py --manual
   ```

### Installation Verification

#### Check Service Status
```bash
# Check if service is running
launchctl list | grep tm-isync

# View service logs
tail -f ~/Library/Logs/tm-isync-adapter.log

# Test adapter directly
./tm-isync-adapter --help
```

#### Verify Dashboard Integration
1. Open Dashboard
2. Go to Settings → iCloud
3. Check "Sync Status" - should show "Active"
4. Review "Last Sync" timestamp

## Using the Sync Adapter

### Daily Workflow

#### Starting Your Day
1. **Check Sync Status** in Dashboard
2. **Review New Cases** that may have synced overnight
3. **Verify File Integrity** of recently synced cases

#### Working with Cases
1. **Add New Cases** to your local source folder
2. **Monitor Auto-Sync** via Dashboard interface
3. **Process Cases** through normal TM workflow
4. **Generated Documents** automatically sync back to iCloud

#### End of Day
1. **Verify All Cases Synced** via Dashboard status
2. **Review Sync Logs** for any errors
3. **Check iCloud Storage** usage if needed

### Sync Operations

#### Automatic Sync Triggers
- **New files** added to source folder
- **File modifications** in existing cases
- **File deletions** (handled carefully)
- **Periodic scan** (every 30 seconds)

#### Manual Sync Operations
```bash
# Force immediate sync
curl -X POST http://127.0.0.1:8000/api/icloud/sync

# Sync specific case
curl -X POST http://127.0.0.1:8000/api/icloud/sync/case-name
```

### File Organization

#### Recommended Folder Structure
```
TM-Cases/                     # iCloud root folder
├── Active-Cases/             # Currently being worked on
│   ├── Smith-vs-Equifax/     # Individual case folders
│   ├── Johnson-FCRA/
│   └── Rodriguez-Complex/
├── Completed-Cases/          # Finished cases
│   ├── 2024-Q1/             # Organized by quarter
│   ├── 2024-Q2/
│   └── Archive/
└── Templates/                # Shared templates and forms
    ├── Attorney-Notes/
    └── Standard-Forms/
```

#### File Naming Conventions
```bash
# Good examples
Smith_John_Atty_Notes.txt
Credit_Report_Equifax_20240315.pdf
Dispute_Letter_TransUnion.docx

# Avoid
notes.txt                     # Too generic
John's file (copy).pdf        # Spaces and parentheses
temp_file_123456.tmp          # Temporary files
```

## Monitoring and Management

### Dashboard Monitoring

#### iCloud Status Page
Access via `Dashboard → Settings → iCloud`:

- **Connection Status**: Connected/Disconnected
- **Last Sync Time**: When sync last completed
- **Files Synced**: Count of files processed
- **Sync Errors**: Any recent errors
- **Storage Usage**: iCloud space utilization

#### Real-time Monitoring
- **File Operations**: Live view of sync operations
- **Progress Indicators**: Visual progress for large operations
- **Error Notifications**: Toast notifications for issues
- **Success Confirmations**: Confirmation of completed syncs

### Service Management

#### Service Commands
```bash
# Check service status
launchctl list com.tm.isync.adapter

# Stop service
launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist

# Start service
launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist

# Restart service
launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
```

#### Log Management
```bash
# View current logs
tail -f ~/Library/Logs/tm-isync-adapter.log

# View error logs
grep ERROR ~/Library/Logs/tm-isync-adapter.log

# Rotate logs (if they get large)
mv ~/Library/Logs/tm-isync-adapter.log ~/Library/Logs/tm-isync-adapter.log.old
```

### Health Checks

#### Automated Health Checks
```bash
# Run health check script
cd /path/to/adapter
./health_check.sh
```

#### Manual Health Verification
1. **Service Running**: Check launchctl status
2. **Network Connectivity**: Test iCloud access
3. **File Permissions**: Verify folder access
4. **Disk Space**: Ensure adequate storage
5. **Dashboard Integration**: Test API endpoints

## Best Practices

### Security Best Practices

#### Credential Management
- ✅ Use app-specific passwords for 2FA accounts
- ✅ Store credentials securely in Dashboard
- ✅ Regularly rotate passwords
- ❌ Don't share credentials in plain text
- ❌ Don't use shared Apple IDs

#### File Security
- ✅ Use encrypted folders for sensitive cases
- ✅ Regular backups beyond iCloud
- ✅ Monitor access logs
- ❌ Don't sync confidential files to shared iCloud accounts

### Performance Best Practices

#### File Organization
- ✅ Organize cases into logical folders
- ✅ Remove unnecessary files regularly
- ✅ Use consistent naming conventions
- ❌ Don't create deeply nested folder structures
- ❌ Don't sync system or temporary files

#### Sync Optimization
- ✅ Sync during off-peak hours for large operations
- ✅ Monitor bandwidth usage
- ✅ Use file compression when appropriate
- ❌ Don't sync while processing large cases
- ❌ Don't interrupt sync operations

### Workflow Best Practices

#### Case Management
1. **Standardize Folder Names**: Use consistent naming conventions
2. **Organize by Status**: Separate active and completed cases
3. **Regular Cleanup**: Archive old cases periodically
4. **Document Standards**: Maintain consistent file types and formats

#### Error Handling
1. **Monitor Regularly**: Check Dashboard status daily
2. **Investigate Errors**: Don't ignore sync failures
3. **Backup Important Cases**: Don't rely solely on sync
4. **Test Connectivity**: Verify iCloud access periodically

## FAQ

### Common Questions

**Q: How often does sync occur?**
A: The adapter monitors for changes every 30 seconds and syncs immediately when changes are detected.

**Q: What file types are supported?**
A: All file types are supported. The adapter syncs files regardless of type or extension.

**Q: What happens if my internet goes down?**
A: The adapter will queue changes and sync when connectivity is restored. No data is lost.

**Q: Can I use this with multiple Macs?**
A: Yes, but each Mac needs its own adapter installation. They can sync to the same iCloud folder.

**Q: How much iCloud storage do I need?**
A: Depends on your case volume. A typical case with 5-10 documents requires 10-50MB. Plan for growth.

### Configuration Issues

**Q: "Authentication failed" error?**
A: 
1. Verify credentials in Dashboard
2. Try app-specific password if using 2FA
3. Check iCloud account status
4. Test connection via Dashboard

**Q: Files not syncing?**
A:
1. Check service status: `launchctl list | grep tm-isync`
2. Verify folder permissions
3. Check available disk space
4. Review logs for errors

**Q: Sync is slow?**
A:
1. Check internet connection speed
2. Verify iCloud account status
3. Reduce concurrent file operations
4. Consider syncing during off-peak hours

### Technical Issues

**Q: Service won't start?**
A:
1. Check installation: `ls ~/Library/LaunchAgents/com.tm.isync.adapter.plist`
2. Verify permissions: `ls -la /path/to/adapter/tm-isync-adapter`
3. Review logs: `tail ~/Library/Logs/tm-isync-adapter.log`
4. Reinstall if necessary

**Q: Dashboard shows "Disconnected"?**
A:
1. Verify adapter service is running
2. Check network connectivity
3. Test iCloud credentials
4. Restart adapter service

## Support

### Getting Help

#### Documentation Resources
- **User Guide**: This document
- **Troubleshooting Guide**: `TROUBLESHOOTING.md`
- **Developer Documentation**: `DEVELOPER.md`
- **API Documentation**: TM Dashboard API reference

#### Log Collection
When requesting support, include:

```bash
# Collect service logs
cp ~/Library/Logs/tm-isync-adapter.log support-logs/

# Check service status
launchctl list com.tm.isync.adapter > support-logs/service-status.txt

# Dashboard configuration (remove credentials)
curl http://127.0.0.1:8000/api/icloud/config > support-logs/config.json

# System information
system_profiler SPSoftwareDataType > support-logs/system-info.txt
```

#### Contact Information
- **Documentation Issues**: Check latest version
- **Bug Reports**: Include logs and reproduction steps
- **Feature Requests**: Describe use case and requirements

### Self-Help Resources

#### Common Solutions
1. **Restart Service**: Often resolves connectivity issues
2. **Check Credentials**: Verify iCloud login information
3. **Review Logs**: Most issues are logged with solutions
4. **Test Connection**: Use Dashboard test connection feature

#### Community Resources
- Review similar configurations
- Check for known issues
- Share best practices
- Contribute improvements

---

## Appendix

### File Paths Reference

| Component | Default Path |
|-----------|--------------|
| Adapter Binary | `/path/to/TM/isync/adapter/build/tm-isync-adapter` |
| Configuration | `/path/to/TM/isync/adapter/config.json` |
| Service Plist | `~/Library/LaunchAgents/com.tm.isync.adapter.plist` |
| Logs | `~/Library/Logs/tm-isync-adapter.log` |
| Dashboard Config | `/path/to/TM/dashboard/config/icloud.json` |

### Port and URL Reference

| Service | URL | Purpose |
|---------|-----|---------|
| TM Dashboard | `http://127.0.0.1:8000` | Main interface |
| iCloud API | `http://127.0.0.1:8000/api/icloud/*` | Configuration and status |
| Health Check | `http://127.0.0.1:8000/api/health` | Service health |

### Version Information

This guide is current for:
- **TM iSync Adapter**: v1.0.0
- **TM Dashboard**: v1.9.0
- **macOS**: 10.15+ (Catalina and later)

---

*Last updated: 2025-07-15*
*Document version: 1.0.0*