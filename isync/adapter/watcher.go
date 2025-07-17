package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/fsnotify/fsnotify"
)

// FileEvent represents a file system event
type FileEvent struct {
	Path      string
	Operation string
	IsDir     bool
	Timestamp time.Time
}

// FileWatcher handles file system monitoring
type FileWatcher struct {
	watcher   *fsnotify.Watcher
	config    *Config
	eventChan chan FileEvent
	done      chan bool
}

// NewFileWatcher creates a new file watcher
func NewFileWatcher(config *Config) (*FileWatcher, error) {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		return nil, fmt.Errorf("failed to create file watcher: %w", err)
	}

	return &FileWatcher{
		watcher:   watcher,
		config:    config,
		eventChan: make(chan FileEvent, 100), // Buffer for events
		done:      make(chan bool),
	}, nil
}

// Start begins monitoring file system events
func (fw *FileWatcher) Start(ctx context.Context) error {
	// Get iCloud path
	icloudPath, err := fw.config.getICloudPath()
	if err != nil {
		return fmt.Errorf("failed to get iCloud path: %w", err)
	}

	// Add iCloud directory to watcher
	err = fw.addDirectoryRecursive(icloudPath)
	if err != nil {
		return fmt.Errorf("failed to add iCloud directory to watcher: %w", err)
	}

	// Also watch TM outputs directory for reverse sync
	outputPath, err := fw.config.getOutputPath()
	if err != nil {
		logger.Warn("Could not get output path, reverse sync might not work", "error", err)
	} else {
		if _, err := os.Stat(outputPath); err == nil {
			err = fw.addDirectoryRecursive(outputPath)
			if err != nil {
				logger.Warn("Failed to add outputs directory to watcher", "path", outputPath, "error", err)
			}
		}
		logger.Info("File watcher started", "icloud_path", icloudPath, "output_path", outputPath)
	}

	// Start event processing goroutine
	go fw.processEvents(ctx)

	return nil
}

// addDirectoryRecursive adds a directory and all its subdirectories to the watcher
func (fw *FileWatcher) addDirectoryRecursive(root string) error {
	return filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			logger.Warn("Error walking directory", "path", path, "error", err)
			return nil // Continue walking despite errors
		}

		if info.IsDir() {
			// Skip certain directories
			if fw.shouldSkipDirectory(path) {
				logger.Debug("Skipping directory", "path", path)
				return filepath.SkipDir
			}

			err = fw.watcher.Add(path)
			if err != nil {
				logger.Warn("Failed to add directory to watcher", "path", path, "error", err)
				return nil // Continue despite errors
			}
			logger.Debug("Added directory to watcher", "path", path)
		}

		return nil
	})
}

// shouldSkipDirectory determines if a directory should be skipped
func (fw *FileWatcher) shouldSkipDirectory(path string) bool {
	base := filepath.Base(path)
	
	// Skip hidden directories and common temp/system directories
	skipDirs := []string{
		".git", ".svn", ".hg",
		"node_modules", "__pycache__", ".pytest_cache",
		"venv", ".venv", "env", ".env",
		".DS_Store", "Thumbs.db",
		".tmp", "tmp", "temp",
		".Trash", ".Trashes",
	}

	for _, skip := range skipDirs {
		if base == skip || strings.HasPrefix(base, ".") && len(base) > 1 {
			return true
		}
	}

	return false
}

// processEvents processes file system events
func (fw *FileWatcher) processEvents(ctx context.Context) {
	defer close(fw.eventChan)

	for {
		select {
		case <-ctx.Done():
			logger.Info("File watcher stopped")
			return

		case <-fw.done:
			logger.Info("File watcher shutdown requested")
			return

		case event, ok := <-fw.watcher.Events:
			if !ok {
				logger.Error("Watcher events channel closed")
				return
			}

			fw.handleEvent(event)

		case err, ok := <-fw.watcher.Errors:
			if !ok {
				logger.Error("Watcher errors channel closed")
				return
			}

			logger.Error("File watcher error", "error", err)
		}
	}
}

// handleEvent processes a single file system event
func (fw *FileWatcher) handleEvent(event fsnotify.Event) {
	// Skip temporary files and system files
	if fw.shouldSkipFile(event.Name) {
		logger.Debug("Skipping file event", "path", event.Name, "op", event.Op.String())
		return
	}

	// Get file info
	fileInfo, err := os.Stat(event.Name)
	isDir := false
	if err == nil {
		isDir = fileInfo.IsDir()
	}

	// Create our custom event
	fileEvent := FileEvent{
		Path:      event.Name,
		Operation: event.Op.String(),
		IsDir:     isDir,
		Timestamp: time.Now(),
	}

	logger.Info("File event detected", 
		"path", event.Name, 
		"operation", event.Op.String(), 
		"is_dir", isDir)

	// Handle directory creation - add to watcher
	if event.Op&fsnotify.Create == fsnotify.Create && isDir {
		err := fw.addDirectoryRecursive(event.Name)
		if err != nil {
			logger.Warn("Failed to add new directory to watcher", "path", event.Name, "error", err)
		}
	}

	// Send event to channel for processing
	select {
	case fw.eventChan <- fileEvent:
		// Event sent successfully
	default:
		logger.Warn("Event channel full, dropping event", "path", event.Name)
	}
}

// shouldSkipFile determines if a file event should be skipped
func (fw *FileWatcher) shouldSkipFile(path string) bool {
	base := filepath.Base(path)
	
	// Skip temporary files and system files
	skipPatterns := []string{
		".DS_Store", "Thumbs.db", ".tmp", ".temp",
		".swp", ".swo", "~", ".lock", ".pid",
	}

	for _, pattern := range skipPatterns {
		if strings.Contains(base, pattern) || strings.HasSuffix(base, pattern) {
			return true
		}
	}

	// Skip files starting with ._
	if strings.HasPrefix(base, "._") {
		return true
	}

	return false
}

// GetEventChannel returns the channel for receiving file events
func (fw *FileWatcher) GetEventChannel() <-chan FileEvent {
	return fw.eventChan
}

// Stop stops the file watcher
func (fw *FileWatcher) Stop() error {
	logger.Info("Stopping file watcher")
	
	// Close the done channel to signal shutdown
	close(fw.done)
	
	// Close the underlying watcher
	err := fw.watcher.Close()
	if err != nil {
		return fmt.Errorf("failed to close file watcher: %w", err)
	}
	
	logger.Info("File watcher stopped successfully")
	return nil
}

// isInICloudPath checks if a path is within the iCloud directory
func (fw *FileWatcher) isInICloudPath(path string) bool {
	icloudPath, err := fw.config.getICloudPath()
	if err != nil {
		return false
	}
	
	absPath, err := filepath.Abs(path)
	if err != nil {
		return false
	}
	
	absICloudPath, err := filepath.Abs(icloudPath)
	if err != nil {
		return false
	}
	
	return strings.HasPrefix(absPath, absICloudPath)
}

// isInOutputPath checks if a path is within the TM outputs directory
func (fw *FileWatcher) isInOutputPath(path string) bool {
	outputPath, err := fw.config.getOutputPath()
	if err != nil {
		logger.Warn("Could not get output path for checking", "error", err)
		return false
	}

	absPath, err := filepath.Abs(path)
	if err != nil {
		return false
	}

	absOutputPath, err := filepath.Abs(outputPath)
	if err != nil {
		return false
	}

	return strings.HasPrefix(absPath, absOutputPath)
}