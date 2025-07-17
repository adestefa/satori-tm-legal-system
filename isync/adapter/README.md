# TM iSync Adapter

A robust Go service for bidirectional file synchronization between iCloud Drive and the Tiger-Monkey (TM) legal document processing system.

## Overview

The TM iSync Adapter monitors iCloud Drive folders and synchronizes files with the local TM system in real-time. It provides:

- **Bidirectional Sync**: Files flow from iCloud → TM and TM outputs → iCloud
- **Real-time Monitoring**: Uses fsnotify for immediate file change detection
- **Conflict Resolution**: Newer file wins policy for handling conflicts
- **Robust Error Handling**: Graceful degradation and comprehensive logging
- **Simple Configuration**: JSON-based configuration with sensible defaults

## Architecture

- **iCloud Drive**: `~/Library/Mobile Documents/com~apple~CloudDocs/{parent_folder}`
- **TM Input**: `TM/test-data/sync-test-cases/`
- **TM Output**: `TM/outputs/` → `iCloud/outputs/`

## Installation

### Prerequisites

- Go 1.19 or later
- macOS (for iCloud Drive support)
- Access to iCloud Drive

### Build from Source

```bash
# Clone and build
cd /Users/corelogic/satori-dev/TM/isync/adapter
make deps
make build

# Or build and run
make run
```

### System Installation

```bash
# Install to /usr/local/bin
make install

# Run from anywhere
tm-isync-adapter -config /path/to/config.json
```

## Configuration

The service uses a JSON configuration file with the following structure:

```json
{
  "icloud_parent_folder": "TM_Cases",
  "local_tm_path": "/Users/corelogic/satori-dev/TM/test-data/sync-test-cases",
  "sync_interval": 30,
  "log_level": "info",
  "backup_enabled": true
}
```

### Configuration Options

- **icloud_parent_folder**: Folder name in iCloud Drive (default: "TM_Cases")
- **local_tm_path**: Path to TM test-data directory
- **sync_interval**: Periodic sync interval in seconds (default: 30)
- **log_level**: Logging level (debug, info, warn, error)
- **backup_enabled**: Enable backup functionality (default: true)

## Usage

### Basic Usage

```bash
# Use default config.json
./tm-isync-adapter

# Use custom config
./tm-isync-adapter -config /path/to/config.json

# Show version
./tm-isync-adapter -version

# Show help
./tm-isync-adapter -help
```

### Environment Variables

- **TM_ISYNC_CONFIG**: Path to configuration file

```bash
export TM_ISYNC_CONFIG=/path/to/config.json
./tm-isync-adapter
```

### Service Management

The adapter runs as a long-running service with proper signal handling:

- **SIGINT/SIGTERM**: Graceful shutdown
- **Status Reports**: Periodic sync statistics every 5 minutes
- **Health Monitoring**: Built-in health check functionality

## Sync Logic

### iCloud → TM Sync

1. Monitor iCloud Drive folder for changes
2. Copy new/modified files to `TM/test-data/sync-test-cases/`
3. Maintain folder structure (case folders)
4. Handle file conflicts (newer file wins)

### TM → iCloud Sync

1. Monitor `TM/outputs/` directory for new documents
2. Copy outputs to `iCloud/outputs/`
3. Preserve folder structure and metadata
4. Real-time sync on file creation

### Conflict Resolution

- **Newer File Wins**: Compare modification timestamps
- **Size Check**: Verify file sizes for identical timestamps
- **Graceful Fallback**: Continue operation despite errors

## Logging

The adapter provides structured logging with configurable levels:

```
[2025-07-15 10:30:45] INFO main.go:123 - Starting TM iSync Adapter | version=1.0.0
[2025-07-15 10:30:45] INFO sync.go:89 - File synced successfully | src=/path/to/source dest=/path/to/dest
[2025-07-15 10:30:45] WARN watcher.go:156 - Skipping system file | path=.DS_Store
```

### Log Levels

- **DEBUG**: Detailed operation logs
- **INFO**: General operation info
- **WARN**: Warnings and non-critical errors
- **ERROR**: Critical errors and failures

## Error Handling

The adapter implements comprehensive error handling:

- **Graceful Degradation**: Continue operation despite individual file failures
- **Retry Logic**: Automatic retry for transient errors
- **Error Reporting**: Detailed error messages with context
- **Recovery**: Automatic recovery from common error conditions

## Performance

- **Efficient Monitoring**: Uses fsnotify for low-overhead file watching
- **Incremental Sync**: Only syncs changed files
- **Parallel Processing**: Concurrent file operations where safe
- **Memory Efficient**: Minimal memory footprint

## Security

- **Local Operation**: No external network communication
- **File Permissions**: Respects system file permissions
- **Safe Paths**: Validates all file paths before operations
- **Signal Handling**: Secure shutdown on system signals

## Development

### Building

```bash
# Install dependencies
make deps

# Build application
make build

# Run tests
make test

# Format code
make fmt

# Development mode with file watching
make dev
```

### Cross-Platform Building

```bash
# Build for multiple platforms
make build-all

# Create distribution package
make dist
```

### Project Structure

```
adapter/
├── main.go       # Application entry point
├── config.go     # Configuration management
├── logger.go     # Structured logging system
├── watcher.go    # File system monitoring
├── sync.go       # Bidirectional sync logic
├── go.mod        # Go module definition
├── config.json   # Example configuration
├── Makefile      # Build system
└── README.md     # Documentation
```

## Integration with TM System

The adapter integrates seamlessly with the TM system:

1. **File Detection**: New files in iCloud automatically appear in TM
2. **Processing**: TM processes files normally through Tiger/Monkey services
3. **Output Sync**: Generated documents sync back to iCloud
4. **Dashboard**: Works independently - no API communication needed

## Troubleshooting

### Common Issues

**iCloud Drive not found**
```bash
# Check iCloud Drive path
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/
```

**Permission errors**
```bash
# Check file permissions
ls -la /Users/corelogic/satori-dev/TM/test-data/sync-test-cases/
```

**Sync not working**
```bash
# Increase log level for debugging
./tm-isync-adapter -config config.json # with log_level: "debug"
```

### Health Check

The adapter includes a health check function for external monitoring:

```go
healthy, message := HealthCheck()
```

## License

Part of the Tiger-Monkey Legal Document Processing System.
Copyright © 2025 Satori Development.

## Support

For issues and support, check the TM system documentation or contact the development team.