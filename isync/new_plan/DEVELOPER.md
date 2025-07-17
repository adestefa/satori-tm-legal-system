# TM iSync Adapter - Developer Documentation

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Component Details](#component-details)
- [API Documentation](#api-documentation)
- [Configuration System](#configuration-system)
- [File System Integration](#file-system-integration)
- [Error Handling](#error-handling)
- [Testing Framework](#testing-framework)
- [Build and Deployment](#build-and-deployment)
- [Performance Considerations](#performance-considerations)
- [Security Implementation](#security-implementation)
- [Extension Points](#extension-points)
- [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

### System Components

The TM iSync Adapter consists of four main components working together to provide seamless iCloud synchronization:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TM Dashboard  │────│  iSync Adapter  │────│  iCloud Service │
│  (Web Interface)│    │  (Go Service)   │    │   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ HTTP API               │ File System           │ Network
         │                       │ Monitoring            │ Requests
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Configuration  │    │  File Watcher   │    │  Sync Engine    │
│   Management    │    │   (fsnotify)    │    │   (Custom)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

```
1. Dashboard → Configuration API → Adapter Config Update
2. File System → File Watcher → Sync Event Queue
3. Sync Engine → iCloud API → Remote File Operations
4. Status Updates → Dashboard API → Real-time UI Updates
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Core Service | Go 1.19+ | High-performance concurrent processing |
| Web Interface | Python FastAPI | REST API and configuration management |
| File Monitoring | fsnotify | Cross-platform file system events |
| Service Management | macOS launchd | System service integration |
| Configuration | JSON | Human-readable configuration format |
| Logging | Go standard library | Structured logging with levels |

## Component Details

### Go Adapter Service

#### Main Components

**main.go**
```go
// Entry point and service orchestration
func main() {
    config := loadConfiguration()
    logger := initializeLogger()
    
    // Initialize components
    watcher := NewFileWatcher(config.SourceFolder)
    syncer := NewSyncEngine(config)
    
    // Start service
    startService(watcher, syncer, logger)
}
```

**config.go**
```go
type Config struct {
    Username     string `json:"username"`
    Password     string `json:"password"`
    SourceFolder string `json:"source_folder"`
    TargetFolder string `json:"target_folder"`
    LogLevel     string `json:"log_level"`
    SyncInterval int    `json:"sync_interval_seconds"`
}

func LoadConfig(path string) (*Config, error) {
    // Configuration loading with validation
}
```

**watcher.go**
```go
type FileWatcher struct {
    watcher    *fsnotify.Watcher
    eventChan  chan FileEvent
    sourcePath string
}

func (fw *FileWatcher) Start() error {
    // Initialize file system monitoring
    // Handle create, modify, delete events
    // Filter relevant file types
}
```

**sync.go**
```go
type SyncEngine struct {
    config    *Config
    client    *iCloudClient
    eventQueue chan SyncEvent
    logger    *Logger
}

func (se *SyncEngine) ProcessEvent(event FileEvent) error {
    // Determine sync operation (upload, download, delete)
    // Execute iCloud API calls
    // Handle conflicts and retries
    // Update status and logs
}
```

**logger.go**
```go
type Logger struct {
    level   LogLevel
    output  io.Writer
    format  LogFormat
}

func (l *Logger) Info(message string, fields ...Field) {
    // Structured logging with context
}
```

#### Key Features

**Concurrent Processing**
```go
// Worker pool for parallel sync operations
func (se *SyncEngine) startWorkers(numWorkers int) {
    for i := 0; i < numWorkers; i++ {
        go se.worker()
    }
}

func (se *SyncEngine) worker() {
    for event := range se.eventQueue {
        se.processEvent(event)
    }
}
```

**Error Recovery**
```go
func (se *SyncEngine) retryOperation(op func() error, maxRetries int) error {
    for i := 0; i < maxRetries; i++ {
        if err := op(); err == nil {
            return nil
        }
        time.Sleep(time.Duration(i+1) * time.Second)
    }
    return fmt.Errorf("operation failed after %d retries", maxRetries)
}
```

**Health Monitoring**
```go
func (se *SyncEngine) healthCheck() HealthStatus {
    return HealthStatus{
        ServiceRunning:    se.isRunning,
        LastSync:         se.lastSyncTime,
        PendingOperations: len(se.eventQueue),
        ErrorCount:       se.errorCount,
    }
}
```

### Python Installation System

#### Installation Components

**install.py**
```python
class AdapterInstaller:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.service_template = "service.plist.template"
        self.target_plist = os.path.expanduser(
            "~/Library/LaunchAgents/com.tm.isync.adapter.plist"
        )
    
    def install(self) -> bool:
        """Complete installation process"""
        try:
            self.validate_prerequisites()
            self.create_service_file()
            self.load_service()
            self.verify_installation()
            return True
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            return False
    
    def create_service_file(self):
        """Generate launchd service file"""
        with open(self.service_template) as f:
            template = f.read()
        
        # Replace placeholders with actual paths
        service_content = template.format(
            adapter_path=os.path.abspath("tm-isync-adapter"),
            config_path=os.path.abspath("config.json"),
            log_path=os.path.expanduser("~/Library/Logs/tm-isync-adapter.log")
        )
        
        with open(self.target_plist, 'w') as f:
            f.write(service_content)
```

**Package Generation System**
```python
def generate_sync_package(config: dict) -> bytes:
    """Generate complete adapter package with configuration"""
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = Path(temp_dir) / "tm-isync-adapter"
        package_dir.mkdir()
        
        # Copy binary and scripts
        copy_files = [
            "tm-isync-adapter",
            "install.py",
            "uninstall.py",
            "health_check.sh",
            "service.plist.template"
        ]
        
        for file_name in copy_files:
            shutil.copy2(
                adapter_source_dir / file_name,
                package_dir / file_name
            )
        
        # Generate configuration file
        config_file = package_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create ZIP package
        return create_zip_package(package_dir)
```

### Dashboard Integration

#### API Endpoints

**Configuration Management**
```python
@app.get("/api/icloud/config")
async def get_icloud_config():
    """Retrieve current iCloud configuration"""
    try:
        config_path = get_config_path()
        if not os.path.exists(config_path):
            return {"configured": False}
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Remove sensitive data for response
        safe_config = {k: v for k, v in config.items() 
                      if k != "password"}
        
        return safe_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/icloud/config")
async def save_icloud_config(request: Request):
    """Save iCloud configuration"""
    try:
        config = await request.json()
        
        # Validate configuration
        validate_config(config)
        
        # Save to file
        config_path = get_config_path()
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {"status": "success"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Status Monitoring**
```python
@app.get("/api/icloud/status")
async def get_icloud_status():
    """Get current sync status"""
    try:
        # Query adapter service for status
        status = query_adapter_status()
        
        return {
            "connected": status.service_running,
            "last_sync": status.last_sync.isoformat() if status.last_sync else None,
            "pending_operations": status.pending_operations,
            "error_count": status.error_count,
            "sync_enabled": status.sync_enabled
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"connected": False, "error": str(e)}
```

**Sync Operations**
```python
@app.post("/api/icloud/sync")
async def trigger_sync():
    """Manually trigger sync operation"""
    try:
        # Send sync command to adapter
        result = send_sync_command()
        
        if result.success:
            return {"status": "sync_started", "operation_id": result.operation_id}
        else:
            raise HTTPException(status_code=500, detail=result.error)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## API Documentation

### Internal APIs

#### Adapter Service API

The Go adapter service doesn't expose HTTP endpoints directly but communicates through:

1. **Configuration File**: `config.json`
2. **Log File**: Structured logging output
3. **Status File**: Current service status (optional)
4. **Signal Handling**: SIGUSR1 for status, SIGUSR2 for reload

#### Dashboard Integration API

**Configuration Endpoints**
```
GET    /api/icloud/config           # Get current configuration
POST   /api/icloud/config          # Save configuration
POST   /api/icloud/test-connection # Test iCloud credentials
```

**Status Endpoints**
```
GET    /api/icloud/status          # Get sync status
GET    /api/icloud/health          # Health check
```

**Operation Endpoints**
```
POST   /api/icloud/sync            # Trigger manual sync
POST   /api/icloud/sync/{case}     # Sync specific case
GET    /api/icloud/operations      # List active operations
```

**Package Management**
```
POST   /api/icloud/download-package # Generate and download package
```

### Data Schemas

#### Configuration Schema
```json
{
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "format": "email",
      "description": "iCloud Apple ID"
    },
    "password": {
      "type": "string",
      "minLength": 8,
      "description": "iCloud password or app-specific password"
    },
    "source_folder": {
      "type": "string",
      "description": "Local source folder path"
    },
    "target_folder": {
      "type": "string",
      "description": "iCloud target folder name"
    },
    "sync_interval_seconds": {
      "type": "integer",
      "minimum": 10,
      "default": 30,
      "description": "Sync check interval"
    },
    "log_level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARN", "ERROR"],
      "default": "INFO"
    }
  },
  "required": ["username", "password", "source_folder", "target_folder"]
}
```

#### Status Schema
```json
{
  "type": "object",
  "properties": {
    "connected": {"type": "boolean"},
    "last_sync": {"type": "string", "format": "date-time"},
    "pending_operations": {"type": "integer"},
    "error_count": {"type": "integer"},
    "sync_enabled": {"type": "boolean"},
    "storage_usage": {
      "type": "object",
      "properties": {
        "used_bytes": {"type": "integer"},
        "total_bytes": {"type": "integer"},
        "available_bytes": {"type": "integer"}
      }
    }
  }
}
```

## Configuration System

### Configuration Hierarchy

1. **Default Configuration**: Built-in defaults
2. **File Configuration**: `config.json`
3. **Environment Variables**: Override specific values
4. **Dashboard Updates**: Runtime configuration changes

### Configuration Loading

```go
func LoadConfiguration() (*Config, error) {
    // Start with defaults
    config := DefaultConfig()
    
    // Load from file if exists
    if configFile, err := os.Open("config.json"); err == nil {
        defer configFile.Close()
        decoder := json.NewDecoder(configFile)
        if err := decoder.Decode(config); err != nil {
            return nil, fmt.Errorf("invalid config file: %w", err)
        }
    }
    
    // Override with environment variables
    overrideFromEnv(config)
    
    // Validate configuration
    if err := validateConfig(config); err != nil {
        return nil, fmt.Errorf("config validation failed: %w", err)
    }
    
    return config, nil
}
```

### Configuration Validation

```go
func validateConfig(config *Config) error {
    if config.Username == "" {
        return errors.New("username is required")
    }
    
    if config.Password == "" {
        return errors.New("password is required")
    }
    
    if !isValidEmail(config.Username) {
        return errors.New("username must be a valid email")
    }
    
    if !isValidPath(config.SourceFolder) {
        return errors.New("source folder must be a valid path")
    }
    
    return nil
}
```

### Runtime Configuration Updates

```go
func (se *SyncEngine) ReloadConfiguration() error {
    newConfig, err := LoadConfiguration()
    if err != nil {
        return err
    }
    
    // Update configuration atomically
    se.mu.Lock()
    defer se.mu.Unlock()
    
    oldConfig := se.config
    se.config = newConfig
    
    // Restart components if necessary
    if oldConfig.SourceFolder != newConfig.SourceFolder {
        se.restartFileWatcher()
    }
    
    se.logger.Info("Configuration reloaded successfully")
    return nil
}
```

## File System Integration

### File Monitoring

#### fsnotify Integration
```go
type FileWatcher struct {
    watcher     *fsnotify.Watcher
    sourcePath  string
    eventChan   chan FileEvent
    filterFunc  func(string) bool
}

func NewFileWatcher(sourcePath string) (*FileWatcher, error) {
    watcher, err := fsnotify.NewWatcher()
    if err != nil {
        return nil, err
    }
    
    fw := &FileWatcher{
        watcher:    watcher,
        sourcePath: sourcePath,
        eventChan:  make(chan FileEvent, 100),
        filterFunc: defaultFileFilter,
    }
    
    return fw, nil
}

func (fw *FileWatcher) Start() error {
    // Add source path to watcher
    if err := fw.watcher.Add(fw.sourcePath); err != nil {
        return err
    }
    
    // Start event processing goroutine
    go fw.processEvents()
    
    return nil
}

func (fw *FileWatcher) processEvents() {
    for {
        select {
        case event, ok := <-fw.watcher.Events:
            if !ok {
                return
            }
            
            if fw.filterFunc(event.Name) {
                fw.eventChan <- FileEvent{
                    Path:      event.Name,
                    Operation: mapFsnotifyOp(event.Op),
                    Timestamp: time.Now(),
                }
            }
            
        case err, ok := <-fw.watcher.Errors:
            if !ok {
                return
            }
            
            fw.logger.Error("File watcher error", "error", err)
        }
    }
}
```

#### File Filtering
```go
func defaultFileFilter(path string) bool {
    // Skip hidden files
    if strings.HasPrefix(filepath.Base(path), ".") {
        return false
    }
    
    // Skip temporary files
    if strings.HasSuffix(path, ".tmp") ||
       strings.HasSuffix(path, ".temp") {
        return false
    }
    
    // Skip system files
    if strings.Contains(path, ".DS_Store") ||
       strings.Contains(path, "Thumbs.db") {
        return false
    }
    
    return true
}
```

### Sync Operations

#### File Upload
```go
func (se *SyncEngine) uploadFile(localPath, remotePath string) error {
    // Read local file
    data, err := ioutil.ReadFile(localPath)
    if err != nil {
        return fmt.Errorf("failed to read local file: %w", err)
    }
    
    // Calculate checksum
    checksum := sha256.Sum256(data)
    
    // Upload to iCloud
    if err := se.client.UploadFile(remotePath, data); err != nil {
        return fmt.Errorf("failed to upload file: %w", err)
    }
    
    // Verify upload
    remoteChecksum, err := se.client.GetFileChecksum(remotePath)
    if err != nil {
        return fmt.Errorf("failed to verify upload: %w", err)
    }
    
    if !bytes.Equal(checksum[:], remoteChecksum) {
        return errors.New("file upload verification failed")
    }
    
    se.logger.Info("File uploaded successfully",
        "local_path", localPath,
        "remote_path", remotePath,
        "size", len(data))
    
    return nil
}
```

#### Conflict Resolution
```go
func (se *SyncEngine) resolveConflict(localPath, remotePath string) error {
    localInfo, err := os.Stat(localPath)
    if err != nil {
        return err
    }
    
    remoteInfo, err := se.client.GetFileInfo(remotePath)
    if err != nil {
        return err
    }
    
    // Use modification time to determine newer file
    if localInfo.ModTime().After(remoteInfo.ModTime) {
        return se.uploadFile(localPath, remotePath)
    } else {
        return se.downloadFile(remotePath, localPath)
    }
}
```

## Error Handling

### Error Categories

1. **Network Errors**: Connection timeouts, DNS failures
2. **Authentication Errors**: Invalid credentials, expired tokens
3. **File System Errors**: Permission denied, disk full
4. **Service Errors**: Configuration invalid, service crashes
5. **Data Errors**: File corruption, sync conflicts

### Error Handling Strategy

```go
type ErrorHandler struct {
    logger        *Logger
    retryPolicy   RetryPolicy
    errorCounter  map[string]int
    maxErrors     int
}

func (eh *ErrorHandler) HandleError(err error, context string) error {
    // Categorize error
    category := categorizeError(err)
    
    // Log error with context
    eh.logger.Error("Operation failed",
        "error", err,
        "context", context,
        "category", category)
    
    // Update error counter
    eh.errorCounter[category]++
    
    // Check if error count exceeds threshold
    if eh.errorCounter[category] > eh.maxErrors {
        return fmt.Errorf("too many errors of type %s: %w", category, err)
    }
    
    // Apply retry policy
    if eh.retryPolicy.ShouldRetry(err, category) {
        return NewRetryableError(err)
    }
    
    return err
}
```

### Retry Mechanisms

```go
type RetryPolicy struct {
    MaxAttempts   int
    BaseDelay     time.Duration
    MaxDelay      time.Duration
    Backoff       BackoffStrategy
}

func (rp *RetryPolicy) Execute(operation func() error) error {
    var lastErr error
    
    for attempt := 1; attempt <= rp.MaxAttempts; attempt++ {
        if err := operation(); err == nil {
            return nil
        } else {
            lastErr = err
            
            if attempt < rp.MaxAttempts {
                delay := rp.calculateDelay(attempt)
                time.Sleep(delay)
            }
        }
    }
    
    return fmt.Errorf("operation failed after %d attempts: %w", 
                     rp.MaxAttempts, lastErr)
}

func (rp *RetryPolicy) calculateDelay(attempt int) time.Duration {
    switch rp.Backoff {
    case ExponentialBackoff:
        delay := rp.BaseDelay * time.Duration(1<<uint(attempt-1))
        if delay > rp.MaxDelay {
            delay = rp.MaxDelay
        }
        return delay
    case LinearBackoff:
        return rp.BaseDelay * time.Duration(attempt)
    default:
        return rp.BaseDelay
    }
}
```

### Circuit Breaker Pattern

```go
type CircuitBreaker struct {
    state          State
    failureCount   int
    successCount   int
    failureThreshold int
    resetTimeout   time.Duration
    lastFailureTime time.Time
}

func (cb *CircuitBreaker) Execute(operation func() error) error {
    switch cb.state {
    case Open:
        if time.Since(cb.lastFailureTime) > cb.resetTimeout {
            cb.state = HalfOpen
            cb.successCount = 0
        } else {
            return errors.New("circuit breaker is open")
        }
    }
    
    err := operation()
    
    if err != nil {
        cb.recordFailure()
    } else {
        cb.recordSuccess()
    }
    
    return err
}
```

## Testing Framework

### Test Structure

```
isync/
├── test_sync.py           # Integration tests
├── test_errors.py         # Error scenario tests
├── test_cases/           # Test data and scenarios
│   ├── sample_sync_cases/
│   ├── performance_test_data/
│   └── edge_case_scenarios/
└── adapter/
    ├── *_test.go         # Go unit tests
    └── testdata/         # Test fixtures
```

### Unit Testing (Go)

```go
func TestFileWatcher(t *testing.T) {
    // Create temporary directory
    tempDir, err := ioutil.TempDir("", "filewatch_test")
    require.NoError(t, err)
    defer os.RemoveAll(tempDir)
    
    // Initialize file watcher
    watcher, err := NewFileWatcher(tempDir)
    require.NoError(t, err)
    defer watcher.Close()
    
    // Start watching
    err = watcher.Start()
    require.NoError(t, err)
    
    // Create test file
    testFile := filepath.Join(tempDir, "test.txt")
    err = ioutil.WriteFile(testFile, []byte("test content"), 0644)
    require.NoError(t, err)
    
    // Wait for event
    select {
    case event := <-watcher.EventChan():
        assert.Equal(t, testFile, event.Path)
        assert.Equal(t, Create, event.Operation)
    case <-time.After(time.Second):
        t.Fatal("Expected file event within 1 second")
    }
}
```

### Integration Testing

```python
class TestSyncIntegration:
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(self.source_dir)
        os.makedirs(self.target_dir)
    
    def test_file_sync_workflow(self):
        """Test complete file sync workflow"""
        # Create test file
        test_file = os.path.join(self.source_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Configure adapter
        config = {
            "username": "test@example.com",
            "password": "testpass",
            "source_folder": self.source_dir,
            "target_folder": "test-sync"
        }
        
        # Start sync process
        result = self.start_sync_process(config)
        assert result.success
        
        # Verify file was synced
        self.wait_for_sync()
        assert self.verify_file_synced("test.txt")
    
    def test_error_recovery(self):
        """Test error recovery scenarios"""
        # Test network failure recovery
        with self.simulate_network_failure():
            result = self.trigger_sync()
            assert not result.success
        
        # Verify recovery after network restored
        result = self.trigger_sync()
        assert result.success
```

### Performance Testing

```python
class TestSyncPerformance:
    def test_large_file_sync(self):
        """Test sync performance with large files"""
        # Create 100MB test file
        large_file = self.create_large_file(100 * 1024 * 1024)
        
        start_time = time.time()
        result = self.sync_file(large_file)
        sync_time = time.time() - start_time
        
        assert result.success
        assert sync_time < 300  # Should complete within 5 minutes
        
    def test_many_files_sync(self):
        """Test sync performance with many small files"""
        # Create 1000 small files
        files = self.create_many_files(1000, 1024)  # 1KB each
        
        start_time = time.time()
        result = self.sync_files(files)
        sync_time = time.time() - start_time
        
        assert result.success
        assert sync_time < 120  # Should complete within 2 minutes
```

### Mocking and Test Doubles

```go
// Mock iCloud client for testing
type MockiCloudClient struct {
    uploadCalls    []UploadCall
    downloadCalls  []DownloadCall
    shouldFail     bool
}

func (m *MockiCloudClient) UploadFile(path string, data []byte) error {
    m.uploadCalls = append(m.uploadCalls, UploadCall{
        Path: path,
        Size: len(data),
    })
    
    if m.shouldFail {
        return errors.New("mock upload failure")
    }
    
    return nil
}

func (m *MockiCloudClient) DownloadFile(path string) ([]byte, error) {
    m.downloadCalls = append(m.downloadCalls, DownloadCall{
        Path: path,
    })
    
    if m.shouldFail {
        return nil, errors.New("mock download failure")
    }
    
    return []byte("mock file content"), nil
}
```

## Build and Deployment

### Build System

#### Makefile
```makefile
.PHONY: build test clean install

# Build configurations
GO_VERSION := 1.19
BINARY_NAME := tm-isync-adapter
BUILD_DIR := build
LDFLAGS := -ldflags "-X main.version=$(VERSION) -X main.buildTime=$(BUILD_TIME)"

# Default target
all: build

# Build binary
build:
	@echo "Building $(BINARY_NAME)..."
	@mkdir -p $(BUILD_DIR)
	go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME) .

# Run tests
test:
	go test -v ./...
	python3 -m pytest test_sync.py -v
	python3 -m pytest test_errors.py -v

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	rm -f *.log
	rm -f test_report.txt

# Install dependencies
deps:
	go mod download
	pip3 install -r requirements.txt

# Cross-compilation targets
build-darwin-amd64:
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 .

build-darwin-arm64:
	GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-arm64 .

# Development targets
dev-build: deps test build

# Release build
release: clean test build-darwin-amd64 build-darwin-arm64
	@echo "Release build complete"
```

#### Build Script
```bash
#!/bin/bash
set -e

# Build configuration
VERSION=${VERSION:-$(git describe --tags --always)}
BUILD_TIME=$(date -u '+%Y-%m-%d_%H:%M:%S')
COMMIT_HASH=$(git rev-parse HEAD)

echo "Building TM iSync Adapter v${VERSION}"
echo "Build time: ${BUILD_TIME}"
echo "Commit: ${COMMIT_HASH}"

# Validate environment
if ! command -v go &> /dev/null; then
    echo "Go is not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    exit 1
fi

# Run tests
echo "Running tests..."
make test

# Build binary
echo "Building binary..."
make build

# Verify binary
echo "Verifying build..."
./build/tm-isync-adapter --version

echo "Build completed successfully!"
```

### Deployment Pipeline

#### CI/CD Configuration (GitHub Actions)
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: 1.19
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        make deps
    
    - name: Run tests
      run: |
        make test
    
    - name: Build
      run: |
        make build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: tm-isync-adapter
        path: build/
```

### Release Process

1. **Version Tagging**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Build Release Artifacts**
   ```bash
   make release
   ```

3. **Package Generation**
   ```bash
   # Create distribution package
   ./scripts/create-package.sh v1.0.0
   ```

4. **Deployment Verification**
   ```bash
   # Test package installation
   ./scripts/test-package.sh tm-isync-adapter-v1.0.0.zip
   ```

## Performance Considerations

### Memory Management

#### Go Memory Optimization
```go
// Use object pools for frequently allocated objects
var fileEventPool = sync.Pool{
    New: func() interface{} {
        return &FileEvent{}
    },
}

func getFileEvent() *FileEvent {
    return fileEventPool.Get().(*FileEvent)
}

func putFileEvent(event *FileEvent) {
    // Reset event fields
    event.Path = ""
    event.Operation = 0
    event.Timestamp = time.Time{}
    
    fileEventPool.Put(event)
}
```

#### Garbage Collection Tuning
```go
// Configure GC for server workload
func configureGC() {
    // Set GC target percentage
    debug.SetGCPercent(100)
    
    // Enable GC trace for monitoring
    if os.Getenv("GOMAXPROCS") != "" {
        debug.SetMaxStack(1000000)
    }
}
```

### Concurrency Optimization

#### Worker Pool Pattern
```go
type WorkerPool struct {
    workerCount int
    taskQueue   chan Task
    wg          sync.WaitGroup
}

func NewWorkerPool(workerCount int, queueSize int) *WorkerPool {
    return &WorkerPool{
        workerCount: workerCount,
        taskQueue:   make(chan Task, queueSize),
    }
}

func (wp *WorkerPool) Start() {
    for i := 0; i < wp.workerCount; i++ {
        wp.wg.Add(1)
        go wp.worker()
    }
}

func (wp *WorkerPool) worker() {
    defer wp.wg.Done()
    
    for task := range wp.taskQueue {
        task.Execute()
    }
}
```

#### Rate Limiting
```go
type RateLimiter struct {
    limiter *rate.Limiter
    burst   int
}

func NewRateLimiter(requestsPerSecond float64, burst int) *RateLimiter {
    return &RateLimiter{
        limiter: rate.NewLimiter(rate.Limit(requestsPerSecond), burst),
        burst:   burst,
    }
}

func (rl *RateLimiter) Allow() bool {
    return rl.limiter.Allow()
}

func (rl *RateLimiter) Wait(ctx context.Context) error {
    return rl.limiter.Wait(ctx)
}
```

### Network Optimization

#### Connection Pooling
```go
type HTTPClient struct {
    client *http.Client
    pool   *sync.Pool
}

func NewHTTPClient() *HTTPClient {
    transport := &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
        DisableCompression:  false,
    }
    
    return &HTTPClient{
        client: &http.Client{
            Transport: transport,
            Timeout:   30 * time.Second,
        },
    }
}
```

#### Request Batching
```go
type BatchProcessor struct {
    batchSize   int
    batchDelay  time.Duration
    buffer      []Request
    processor   func([]Request) error
    mu          sync.Mutex
}

func (bp *BatchProcessor) Add(req Request) error {
    bp.mu.Lock()
    defer bp.mu.Unlock()
    
    bp.buffer = append(bp.buffer, req)
    
    if len(bp.buffer) >= bp.batchSize {
        return bp.flush()
    }
    
    return nil
}

func (bp *BatchProcessor) flush() error {
    if len(bp.buffer) == 0 {
        return nil
    }
    
    batch := make([]Request, len(bp.buffer))
    copy(batch, bp.buffer)
    bp.buffer = bp.buffer[:0]
    
    return bp.processor(batch)
}
```

## Security Implementation

### Credential Management

#### Secure Storage
```go
type CredentialStore struct {
    keychain KeychainInterface
    encrypt  EncryptionInterface
}

func (cs *CredentialStore) StoreCredentials(username, password string) error {
    // Encrypt password before storage
    encryptedPassword, err := cs.encrypt.Encrypt([]byte(password))
    if err != nil {
        return err
    }
    
    // Store in system keychain
    return cs.keychain.SetPassword("tm-isync", username, encryptedPassword)
}

func (cs *CredentialStore) GetCredentials(username string) (string, error) {
    // Retrieve from keychain
    encryptedPassword, err := cs.keychain.GetPassword("tm-isync", username)
    if err != nil {
        return "", err
    }
    
    // Decrypt password
    password, err := cs.encrypt.Decrypt(encryptedPassword)
    if err != nil {
        return "", err
    }
    
    return string(password), nil
}
```

#### Encryption Utilities
```go
import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "crypto/sha256"
    "golang.org/x/crypto/pbkdf2"
)

type AESEncryption struct {
    key []byte
}

func NewAESEncryption(password string, salt []byte) *AESEncryption {
    key := pbkdf2.Key([]byte(password), salt, 10000, 32, sha256.New)
    return &AESEncryption{key: key}
}

func (ae *AESEncryption) Encrypt(plaintext []byte) ([]byte, error) {
    block, err := aes.NewCipher(ae.key)
    if err != nil {
        return nil, err
    }
    
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    
    nonce := make([]byte, gcm.NonceSize())
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        return nil, err
    }
    
    ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)
    return ciphertext, nil
}
```

### Input Validation

#### Path Validation
```go
func validatePath(path string) error {
    // Convert to absolute path
    absPath, err := filepath.Abs(path)
    if err != nil {
        return fmt.Errorf("invalid path: %w", err)
    }
    
    // Check if path exists
    if _, err := os.Stat(absPath); os.IsNotExist(err) {
        return fmt.Errorf("path does not exist: %s", absPath)
    }
    
    // Check for path traversal
    if strings.Contains(absPath, "..") {
        return fmt.Errorf("path traversal not allowed: %s", absPath)
    }
    
    // Check permissions
    if !isReadable(absPath) {
        return fmt.Errorf("path not readable: %s", absPath)
    }
    
    return nil
}
```

#### Configuration Sanitization
```go
func sanitizeConfig(config *Config) error {
    // Validate email format
    if !isValidEmail(config.Username) {
        return errors.New("invalid email format")
    }
    
    // Validate path security
    if err := validatePath(config.SourceFolder); err != nil {
        return fmt.Errorf("invalid source folder: %w", err)
    }
    
    // Sanitize folder names
    config.TargetFolder = sanitizeFolderName(config.TargetFolder)
    
    // Validate numeric ranges
    if config.SyncInterval < 10 || config.SyncInterval > 3600 {
        return errors.New("sync interval must be between 10 and 3600 seconds")
    }
    
    return nil
}
```

## Extension Points

### Plugin Architecture

#### Plugin Interface
```go
type Plugin interface {
    Name() string
    Version() string
    Initialize(config PluginConfig) error
    ProcessEvent(event FileEvent) error
    Shutdown() error
}

type PluginManager struct {
    plugins []Plugin
    config  map[string]PluginConfig
}

func (pm *PluginManager) LoadPlugin(pluginPath string) error {
    // Load plugin from shared library
    plugin, err := loadPlugin(pluginPath)
    if err != nil {
        return err
    }
    
    // Initialize plugin
    config := pm.config[plugin.Name()]
    if err := plugin.Initialize(config); err != nil {
        return err
    }
    
    pm.plugins = append(pm.plugins, plugin)
    return nil
}
```

#### Custom Sync Handlers
```go
type SyncHandler interface {
    CanHandle(event FileEvent) bool
    Handle(event FileEvent) error
    Priority() int
}

type SyncEngine struct {
    handlers []SyncHandler
}

func (se *SyncEngine) RegisterHandler(handler SyncHandler) {
    se.handlers = append(se.handlers, handler)
    
    // Sort by priority
    sort.Slice(se.handlers, func(i, j int) bool {
        return se.handlers[i].Priority() > se.handlers[j].Priority()
    })
}

func (se *SyncEngine) ProcessEvent(event FileEvent) error {
    for _, handler := range se.handlers {
        if handler.CanHandle(event) {
            return handler.Handle(event)
        }
    }
    
    return errors.New("no handler found for event")
}
```

### Webhook Integration

#### Webhook Support
```go
type WebhookManager struct {
    webhooks []WebhookConfig
    client   *http.Client
}

type WebhookConfig struct {
    URL     string            `json:"url"`
    Events  []string          `json:"events"`
    Headers map[string]string `json:"headers"`
    Secret  string            `json:"secret"`
}

func (wm *WebhookManager) SendWebhook(event Event) error {
    for _, webhook := range wm.webhooks {
        if wm.shouldTrigger(webhook, event) {
            go wm.sendWebhook(webhook, event)
        }
    }
    return nil
}

func (wm *WebhookManager) sendWebhook(config WebhookConfig, event Event) {
    payload, _ := json.Marshal(event)
    
    req, _ := http.NewRequest("POST", config.URL, bytes.NewBuffer(payload))
    req.Header.Set("Content-Type", "application/json")
    
    // Add custom headers
    for key, value := range config.Headers {
        req.Header.Set(key, value)
    }
    
    // Add signature if secret is provided
    if config.Secret != "" {
        signature := generateSignature(payload, config.Secret)
        req.Header.Set("X-Signature", signature)
    }
    
    wm.client.Do(req)
}
```

## Contributing Guidelines

### Development Workflow

1. **Fork and Clone**
   ```bash
   git fork https://github.com/tm/isync-adapter
   git clone https://github.com/yourusername/isync-adapter
   cd isync-adapter
   ```

2. **Setup Development Environment**
   ```bash
   make deps
   make dev-build
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Development Cycle**
   ```bash
   # Make changes
   # Run tests
   make test
   
   # Build and verify
   make build
   ./build/tm-isync-adapter --help
   ```

5. **Submit Pull Request**
   - Write clear commit messages
   - Include tests for new features
   - Update documentation
   - Ensure CI passes

### Code Standards

#### Go Code Style
- Follow `gofmt` formatting
- Use `golint` for style checking
- Include comprehensive error handling
- Write idiomatic Go code
- Add godoc comments for public APIs

#### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Include docstrings for functions
- Use meaningful variable names
- Add unit tests for new code

#### Documentation Standards
- Update relevant documentation
- Include code examples
- Document configuration changes
- Update API documentation
- Add troubleshooting information

### Testing Requirements

#### Required Tests
1. **Unit Tests**: All new functions and methods
2. **Integration Tests**: End-to-end functionality
3. **Error Tests**: Error handling scenarios
4. **Performance Tests**: Resource usage and timing

#### Test Coverage
- Maintain minimum 80% code coverage
- Include edge cases and error conditions
- Test concurrent operations
- Validate configuration handling

---

*Last updated: 2025-07-15*
*Document version: 1.0.0*