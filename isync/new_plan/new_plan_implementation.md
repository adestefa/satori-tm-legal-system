# iCloud Sync Adapter Implementation Plan

**Date:** 2025-07-15  
**Status:** APPROVED - Ready for implementation  
**Architecture:** Go adapter with Dashboard integration

## Architecture Overview

**Core Principle**: Leverage existing TM file monitoring infrastructure rather than creating parallel systems.

**Optimal Data Flow**:
```
iCloud Drive → Go Adapter → TM/test-data/sync-test-cases/ → Existing Dashboard FileWatcher → Standard TM Processing
```

## Key Architecture Decisions

1. **Leverage Existing TM File Monitoring**: Use proven Dashboard FileWatcher system
2. **Sync TO Existing Directory Structure**: Work with TM/test-data/sync-test-cases/
3. **No API Communication Required**: Go adapter works independently
4. **Dashboard Provides Config UI**: Simple configuration and package generation

## Phase 1: Dashboard Integration (2-3 hours)

### 1.1 Create iCloud Configuration Page
- **Location**: `/icloud` page in Dashboard
- **Features**: Configuration form for iCloud folder name and sync settings
- **UI Components**: Form validation, status dashboard, download section

### 1.2 Implement API Endpoints
- `GET /api/icloud/config` - Current iCloud configuration
- `POST /api/icloud/config` - Save iCloud configuration  
- `GET /api/icloud/status` - Sync adapter status
- `GET /api/icloud/download` - Download configured app package

### 1.3 Add Navigation Integration
- **Sidebar Link**: Add iCloud link to main dashboard navigation
- **Theme Support**: Ensure compatibility with light, dark, lexigen themes

## Phase 2: Go Adapter Development (4-5 hours)

### 2.1 Core File System Monitoring
- **Library**: fsnotify for iCloud Drive monitoring
- **Target**: `~/Library/Mobile Documents/com~apple~CloudDocs/{parent_folder}`
- **Events**: CREATE, MODIFY, DELETE file events

### 2.2 Bidirectional Sync Logic
- **iCloud → TM**: Sync files to `TM/test-data/sync-test-cases/`
- **TM → iCloud**: Sync outputs from `TM/outputs/` back to iCloud
- **Folder Structure**: Maintain case folder organization

### 2.3 Service Management
- **Configuration**: Load config.json for settings
- **Logging**: Structured logging with configurable levels
- **Error Handling**: Robust error recovery and retry logic

## Phase 3: Installation System (2-3 hours)

### 3.1 Python Installation Script
- **Functionality**: Automated service setup and management
- **Service Directory**: Create `~/Library/TM-iCloud-Sync/`
- **Dependencies**: Install Go executable and config

### 3.2 macOS Service Integration
- **launchd Service**: Create macOS service for automatic startup
- **Service Management**: Start/stop/restart capabilities
- **Uninstall Support**: Clean removal of service and files

### 3.3 Package Generation
- **Zip Contents**: Go executable + config.json + install.py
- **Dashboard Integration**: Generate package via Dashboard UI
- **User Instructions**: Clear installation and usage guide

## Phase 4: Integration & Testing (2-3 hours)

### 4.1 End-to-End Testing
- **Configuration Workflow**: Test Dashboard config and download
- **File Sync Testing**: Verify bidirectional sync functionality
- **Service Management**: Test installation and service lifecycle

### 4.2 Error Scenario Testing
- **Network Issues**: Test behavior when iCloud is unavailable
- **File Conflicts**: Handle duplicate or conflicting files
- **Service Recovery**: Test automatic recovery from failures

### 4.3 Performance Validation
- **Sync Performance**: Measure sync speed and resource usage
- **File Monitoring**: Verify efficient file system monitoring
- **Memory Usage**: Ensure minimal resource footprint

## Technical Specifications

### Configuration Schema
```json
{
  "icloud_parent_folder": "TM_Cases",
  "local_tm_path": "/Users/corelogic/satori-dev/TM/test-data/sync-test-cases",
  "sync_interval": 30,
  "log_level": "info",
  "backup_enabled": true
}
```

### Go Adapter Architecture
```go
type ICloudAdapter struct {
    config          *Config
    icloudPath      string
    localTMPath     string
    fileWatcher     *fsnotify.Watcher
    syncInterval    time.Duration
}
```

## Expected Deliverables

1. **iCloud Configuration Page**: Complete Dashboard UI for setup
2. **Go Adapter Service**: File system monitoring and sync service
3. **Python Installation Script**: Automated service setup
4. **Package Generation System**: Dashboard-integrated download
5. **Documentation**: User guide and troubleshooting

## Success Criteria

- **Seamless Integration**: Works with existing TM workflow
- **Reliable Sync**: Bidirectional file synchronization
- **Easy Installation**: One-click download and setup
- **Robust Service**: Automatic startup and error recovery
- **User-Friendly**: Clear configuration and status feedback

## Risk Mitigation

- **Leverage Existing Infrastructure**: Use proven Dashboard FileWatcher
- **Simple Architecture**: Avoid over-engineering with complex solutions
- **Incremental Development**: Test each phase before proceeding
- **Fallback Mechanisms**: Manual refresh if automatic sync fails

---

**Total Estimated Time**: 10-14 hours  
**Complexity**: Medium-High (file system monitoring, service management)  
**Risk Level**: Low (leverages existing TM infrastructure)  
**Philosophy Alignment**: Meets customer where they are, infuses existing workflow