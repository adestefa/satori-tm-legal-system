# TM iSync Adapter - Complete iCloud Synchronization System

## Overview

The TM iSync Adapter provides seamless two-way synchronization between your local Tiger-Monkey case files and iCloud storage. This professional-grade system enables automatic case file management with real-time monitoring through the TM Dashboard interface.

### 🚀 Key Features

- **🔄 Automatic Synchronization**: Bidirectional sync between local TM cases and iCloud
- **📊 Dashboard Integration**: Full integration with TM Dashboard for configuration and monitoring
- **🛡️ Enterprise Security**: Secure credential management with app-specific password support
- **⚡ High Performance**: Concurrent file processing with intelligent error recovery
- **🖥️ macOS Native**: Leverages macOS service architecture for reliable background operation
- **📱 Real-time Monitoring**: Live status updates and progress tracking through web interface

## Quick Start

### 1. Prerequisites

- macOS 10.15 (Catalina) or later
- Active iCloud account with sufficient storage
- Running TM Dashboard (v1.9.0+)
- Stable internet connection

### 2. Installation

1. **Configure iCloud in Dashboard**
   ```
   Open TM Dashboard → Settings → iCloud Integration
   Enter your iCloud credentials and folder settings
   ```

2. **Download and Install**
   ```
   Click "Download iSync Adapter" in Dashboard
   Extract the ZIP file and run: python3 install.py
   ```

3. **Verify Installation**
   ```
   Check Dashboard iCloud status page
   Verify service is running and syncing
   ```

### 3. Basic Usage

Once installed, the adapter runs automatically in the background:

- **Add case files** to your configured source folder
- **Monitor sync progress** through Dashboard interface  
- **Access files** from any device via iCloud
- **Process cases** through normal TM workflow

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TM Dashboard  │────│  iSync Adapter  │────│  iCloud Service │
│  (Web Interface)│    │  (Go Service)   │    │   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
    HTTP API/Config         File Monitoring         Network Sync
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Configuration  │    │  File Watcher   │    │  Sync Engine    │
│   Management    │    │   (fsnotify)    │    │   (Custom)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Dashboard Integration** | Python FastAPI | Configuration management and monitoring |
| **Go Adapter Service** | Go 1.19+ | High-performance file synchronization |
| **File Monitoring** | fsnotify | Real-time file system event detection |
| **Service Management** | macOS launchd | System service integration |
| **Package System** | Python + Shell | Installation and deployment |

## Documentation

### 📚 User Documentation
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user guide with step-by-step instructions
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Comprehensive troubleshooting guide
- **[test_cases/README.md](test_cases/README.md)** - Test data and validation information

### 🔧 Technical Documentation  
- **[DEVELOPER.md](DEVELOPER.md)** - Technical implementation details and API documentation
- **[adapter/README.md](adapter/README.md)** - Go adapter service documentation
- **[adapter/INSTALL.md](adapter/INSTALL.md)** - Installation and build instructions

## Testing and Validation

### 🧪 Comprehensive Test Suite

The system includes extensive testing capabilities:

#### Integration Tests
```bash
# Run complete integration test suite
python3 test_sync.py --test all

# Test specific components
python3 test_sync.py --test dashboard
python3 test_sync.py --test sync
python3 test_sync.py --test performance
```

#### Error Scenario Tests
```bash
# Test error handling and recovery
python3 test_errors.py --scenario all

# Test specific error types
python3 test_errors.py --scenario network
python3 test_errors.py --scenario auth
python3 test_errors.py --scenario filesystem
```

#### Complete Test Runner
```bash
# Run all tests with comprehensive reporting
python3 run_all_tests.py

# Quick essential tests only
python3 run_all_tests.py --quick

# Performance benchmarks only
python3 run_all_tests.py --performance
```

### 📊 Test Coverage

- **Integration Tests**: End-to-end workflow validation
- **Error Scenarios**: Network, authentication, filesystem, and service failures
- **Performance Tests**: Response times, throughput, and resource usage
- **Build Tests**: Compilation, binary validation, and packaging
- **Documentation Tests**: Completeness and accuracy validation

## Configuration

### Dashboard Configuration

Configure through TM Dashboard interface:

```json
{
  "username": "your-apple-id@email.com",
  "password": "app-specific-password",
  "source_folder": "/Users/yourname/Documents/TM-Cases",
  "target_folder": "TM-Cases"
}
```

### Advanced Configuration Options

- **Sync Interval**: How often to check for changes (default: 30 seconds)
- **Log Level**: DEBUG, INFO, WARN, ERROR (default: INFO)
- **Retry Policy**: Automatic retry configuration for failed operations
- **Concurrent Operations**: Number of parallel sync operations

## Monitoring and Management

### Dashboard Interface

Access comprehensive monitoring through TM Dashboard:

- **Real-time Status**: Connection state and sync progress
- **File Operations**: Live view of sync activities
- **Error Reporting**: Detailed error logs with resolution suggestions
- **Performance Metrics**: Sync speeds and success rates
- **Storage Usage**: iCloud space utilization tracking

### Service Management

```bash
# Check service status
launchctl list com.tm.isync.adapter

# View logs
tail -f ~/Library/Logs/tm-isync-adapter.log

# Restart service
launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
```

### Health Monitoring

```bash
# Run comprehensive health check
cd adapter && ./health_check.sh

# Test connectivity
curl -X POST http://127.0.0.1:8000/api/icloud/test-connection
```

## Security

### Credential Security

- **App-Specific Passwords**: Support for 2FA-enabled accounts
- **Secure Storage**: Credentials encrypted at rest
- **Session Management**: Automatic token refresh and validation
- **Audit Logging**: Comprehensive security event logging

### File Security

- **Permission Validation**: Strict file system permission checking
- **Path Sanitization**: Protection against path traversal attacks
- **Content Validation**: File type and size validation
- **Secure Transport**: Encrypted communication with iCloud

## Performance

### Optimization Features

- **Concurrent Processing**: Parallel file operations for maximum throughput
- **Intelligent Batching**: Optimized upload/download batching
- **Delta Sync**: Only sync changed files to minimize bandwidth
- **Compression**: Automatic file compression for large transfers
- **Caching**: Intelligent metadata caching for faster operations

### Performance Benchmarks

| Operation | Target Performance |
|-----------|-------------------|
| Dashboard API Response | < 100ms |
| Small File Sync (< 1MB) | < 5 seconds |
| Large File Sync (100MB) | < 5 minutes |
| Case Folder Sync | < 30 seconds |
| Service Startup | < 10 seconds |

## File Organization

### Recommended Structure

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

### File Naming Best Practices

- Use consistent naming conventions
- Avoid special characters and spaces
- Include dates in YYYYMMDD format
- Use descriptive but concise names
- Organize by case status and date

## Troubleshooting

### Common Issues

#### "Authentication Failed"
- Verify iCloud credentials in Dashboard
- Generate app-specific password for 2FA accounts
- Check Apple ID account status

#### "Files Not Syncing"
- Check service status: `launchctl list com.tm.isync.adapter`
- Verify folder permissions and disk space
- Review logs for specific errors

#### "Slow Performance"
- Check internet connection speed
- Verify iCloud account status and storage
- Reduce concurrent operations if needed

### Getting Help

1. **Check Documentation**: Review relevant guides above
2. **Run Diagnostics**: Use built-in health check tools
3. **Collect Logs**: Gather system logs and error information
4. **Review Status**: Check Dashboard monitoring interface

## Development and Contributing

### Development Setup

```bash
# Clone and setup
git clone <repository>
cd TM/isync

# Install dependencies
cd adapter && make deps

# Build and test
make build
make test

# Run integration tests
python3 run_all_tests.py --quick
```

### Build Requirements

- Go 1.19 or later
- Python 3.8 or later  
- Make build system
- macOS development tools

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## Version Information

- **Current Version**: 1.0.0
- **TM Dashboard Compatibility**: v1.9.0+
- **macOS Compatibility**: 10.15+ (Catalina and later)
- **Go Version**: 1.19+
- **Python Version**: 3.8+

## File Structure

```
isync/
├── README.md                 # This file
├── USER_GUIDE.md            # Complete user documentation
├── TROUBLESHOOTING.md       # Problem resolution guide
├── DEVELOPER.md             # Technical implementation details
├── test_sync.py             # Integration testing framework
├── test_errors.py           # Error scenario testing
├── run_all_tests.py         # Comprehensive test runner
├── test_cases/              # Test data and scenarios
│   ├── README.md
│   └── sample_sync_cases/
├── adapter/                 # Go service implementation
│   ├── README.md
│   ├── INSTALL.md
│   ├── Makefile
│   ├── main.go
│   ├── config.go
│   ├── sync.go
│   ├── watcher.go
│   ├── logger.go
│   ├── install.py
│   ├── uninstall.py
│   └── health_check.sh
└── documentation/           # Additional documentation
```

## License

This software is part of the Tiger-Monkey legal document processing system. All rights reserved.

---

## Quick Reference

### Essential Commands
```bash
# Check status
curl http://127.0.0.1:8000/api/icloud/status

# Trigger manual sync
curl -X POST http://127.0.0.1:8000/api/icloud/sync

# View logs
tail -f ~/Library/Logs/tm-isync-adapter.log

# Run tests
python3 run_all_tests.py --quick

# Restart service
launchctl unload ~/Library/LaunchAgents/com.tm.isync.adapter.plist
launchctl load ~/Library/LaunchAgents/com.tm.isync.adapter.plist
```

### Important URLs
- **Dashboard**: http://127.0.0.1:8000
- **iCloud Config**: http://127.0.0.1:8000/settings (iCloud tab)
- **API Status**: http://127.0.0.1:8000/api/icloud/status

### Support Resources
- **Documentation**: All .md files in this directory
- **Test Suite**: Run `python3 run_all_tests.py` for validation
- **Health Check**: Use Dashboard status page or `./health_check.sh`

---

*For detailed installation, configuration, and troubleshooting information, see the respective documentation files listed above.*

*Last updated: 2025-07-15*
*Document version: 1.0.0*