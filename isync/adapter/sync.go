package main

import (
	"context"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// SyncManager handles bidirectional file synchronization
type SyncManager struct {
	config    *Config
	watcher   *FileWatcher
	syncing   bool
	syncStats SyncStats
}

// SyncStats tracks synchronization statistics
type SyncStats struct {
	FilesSync       int
	DirectoriesSync int
	Errors          int
	LastSync        time.Time
	StartTime       time.Time
}

// NewSyncManager creates a new sync manager
func NewSyncManager(config *Config) (*SyncManager, error) {
	watcher, err := NewFileWatcher(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create file watcher: %w", err)
	}

	return &SyncManager{
		config:  config,
		watcher: watcher,
		syncing: false,
		syncStats: SyncStats{
			StartTime: time.Now(),
		},
	}, nil
}

// Start begins the sync process
func (sm *SyncManager) Start(ctx context.Context) error {
	logger.Info("Starting sync manager")
	
	// Start file watcher
	err := sm.watcher.Start(ctx)
	if err != nil {
		return fmt.Errorf("failed to start file watcher: %w", err)
	}

	// Perform initial sync
	err = sm.performInitialSync()
	if err != nil {
		logger.Error("Initial sync failed", "error", err)
		// Don't return error - continue with event-based sync
	}

	// Start event processing
	go sm.processFileEvents(ctx)

	// Start periodic sync
	go sm.periodicSync(ctx)

	logger.Info("Sync manager started successfully")
	return nil
}

// performInitialSync performs a full bidirectional sync on startup
func (sm *SyncManager) performInitialSync() error {
	logger.Info("Performing initial sync")
	
	// Sync from iCloud to TM
	err := sm.syncICloudToTM()
	if err != nil {
		logger.Error("iCloud to TM sync failed", "error", err)
		return err
	}

	// Sync from TM to iCloud
	err = sm.syncTMToICloud()
	if err != nil {
		logger.Error("TM to iCloud sync failed", "error", err)
		return err
	}

	sm.syncStats.LastSync = time.Now()
	logger.Info("Initial sync completed", "files_synced", sm.syncStats.FilesSync, "dirs_synced", sm.syncStats.DirectoriesSync)
	return nil
}

// syncICloudToTM syncs files from iCloud Drive to TM test-data directory
func (sm *SyncManager) syncICloudToTM() error {
	icloudPath, err := sm.config.getICloudPath()
	if err != nil {
		return fmt.Errorf("failed to get iCloud path: %w", err)
	}

	logger.Info("Syncing from iCloud to TM", "source", icloudPath, "dest", sm.config.LocalTMPath)

	return filepath.Walk(icloudPath, func(srcPath string, info os.FileInfo, err error) error {
		if err != nil {
			logger.Warn("Error walking iCloud directory", "path", srcPath, "error", err)
			sm.syncStats.Errors++
			return nil // Continue walking
		}

		// Skip system files
		if sm.shouldSkipFile(srcPath) {
			return nil
		}

		// Calculate relative path
		relPath, err := filepath.Rel(icloudPath, srcPath)
		if err != nil {
			logger.Warn("Failed to calculate relative path", "path", srcPath, "error", err)
			sm.syncStats.Errors++
			return nil
		}

		// Calculate destination path
		destPath := filepath.Join(sm.config.LocalTMPath, relPath)

		// Sync file or directory
		if info.IsDir() {
			err = sm.syncDirectory(srcPath, destPath)
			if err != nil {
				logger.Warn("Failed to sync directory", "src", srcPath, "dest", destPath, "error", err)
				sm.syncStats.Errors++
			} else {
				sm.syncStats.DirectoriesSync++
			}
		} else {
			err = sm.syncFile(srcPath, destPath)
			if err != nil {
				logger.Warn("Failed to sync file", "src", srcPath, "dest", destPath, "error", err)
				sm.syncStats.Errors++
			} else {
				sm.syncStats.FilesSync++
			}
		}

		return nil
	})
}

// syncTMToICloud syncs files from TM outputs to iCloud Drive
func (sm *SyncManager) syncTMToICloud() error {
	outputPath := sm.config.getOutputPath()
	
	// Check if outputs directory exists
	if _, err := os.Stat(outputPath); os.IsNotExist(err) {
		logger.Info("TM outputs directory does not exist, skipping reverse sync", "path", outputPath)
		return nil
	}

	icloudPath, err := sm.config.getICloudPath()
	if err != nil {
		return fmt.Errorf("failed to get iCloud path: %w", err)
	}

	// Create outputs subdirectory in iCloud
	icloudOutputPath := filepath.Join(icloudPath, "outputs")
	err = os.MkdirAll(icloudOutputPath, 0755)
	if err != nil {
		return fmt.Errorf("failed to create iCloud outputs directory: %w", err)
	}

	logger.Info("Syncing from TM to iCloud", "source", outputPath, "dest", icloudOutputPath)

	return filepath.Walk(outputPath, func(srcPath string, info os.FileInfo, err error) error {
		if err != nil {
			logger.Warn("Error walking outputs directory", "path", srcPath, "error", err)
			sm.syncStats.Errors++
			return nil // Continue walking
		}

		// Skip system files
		if sm.shouldSkipFile(srcPath) {
			return nil
		}

		// Calculate relative path
		relPath, err := filepath.Rel(outputPath, srcPath)
		if err != nil {
			logger.Warn("Failed to calculate relative path", "path", srcPath, "error", err)
			sm.syncStats.Errors++
			return nil
		}

		// Calculate destination path
		destPath := filepath.Join(icloudOutputPath, relPath)

		// Sync file or directory
		if info.IsDir() {
			err = sm.syncDirectory(srcPath, destPath)
			if err != nil {
				logger.Warn("Failed to sync directory", "src", srcPath, "dest", destPath, "error", err)
				sm.syncStats.Errors++
			} else {
				sm.syncStats.DirectoriesSync++
			}
		} else {
			err = sm.syncFile(srcPath, destPath)
			if err != nil {
				logger.Warn("Failed to sync file", "src", srcPath, "dest", destPath, "error", err)
				sm.syncStats.Errors++
			} else {
				sm.syncStats.FilesSync++
			}
		}

		return nil
	})
}

// syncFile syncs a single file, handling conflicts with newer-file-wins policy
func (sm *SyncManager) syncFile(srcPath, destPath string) error {
	srcInfo, err := os.Stat(srcPath)
	if err != nil {
		return fmt.Errorf("failed to stat source file: %w", err)
	}

	// Check if destination exists
	destInfo, err := os.Stat(destPath)
	if err != nil {
		if !os.IsNotExist(err) {
			return fmt.Errorf("failed to stat destination file: %w", err)
		}
		// Destination doesn't exist, copy file
		return sm.copyFile(srcPath, destPath)
	}

	// Both files exist, check which is newer
	if srcInfo.ModTime().After(destInfo.ModTime()) {
		logger.Debug("Source file is newer, copying", "src", srcPath, "dest", destPath)
		return sm.copyFile(srcPath, destPath)
	} else if destInfo.ModTime().After(srcInfo.ModTime()) {
		logger.Debug("Destination file is newer, skipping", "src", srcPath, "dest", destPath)
		return nil
	}

	// Files have same modification time, check size
	if srcInfo.Size() != destInfo.Size() {
		logger.Debug("Files have different sizes, copying", "src", srcPath, "dest", destPath)
		return sm.copyFile(srcPath, destPath)
	}

	// Files appear to be the same, skip
	logger.Debug("Files appear identical, skipping", "src", srcPath, "dest", destPath)
	return nil
}

// syncDirectory ensures a directory exists at the destination
func (sm *SyncManager) syncDirectory(srcPath, destPath string) error {
	err := os.MkdirAll(destPath, 0755)
	if err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	logger.Debug("Directory synced", "src", srcPath, "dest", destPath)
	return nil
}

// copyFile copies a file from source to destination
func (sm *SyncManager) copyFile(srcPath, destPath string) error {
	// Create destination directory if it doesn't exist
	destDir := filepath.Dir(destPath)
	err := os.MkdirAll(destDir, 0755)
	if err != nil {
		return fmt.Errorf("failed to create destination directory: %w", err)
	}

	// Open source file
	src, err := os.Open(srcPath)
	if err != nil {
		return fmt.Errorf("failed to open source file: %w", err)
	}
	defer src.Close()

	// Create destination file
	dest, err := os.Create(destPath)
	if err != nil {
		return fmt.Errorf("failed to create destination file: %w", err)
	}
	defer dest.Close()

	// Copy file contents
	_, err = io.Copy(dest, src)
	if err != nil {
		return fmt.Errorf("failed to copy file contents: %w", err)
	}

	// Copy file metadata
	srcInfo, err := src.Stat()
	if err != nil {
		return fmt.Errorf("failed to get source file info: %w", err)
	}

	err = os.Chtimes(destPath, srcInfo.ModTime(), srcInfo.ModTime())
	if err != nil {
		logger.Warn("Failed to set file modification time", "path", destPath, "error", err)
	}

	logger.Debug("File copied successfully", "src", srcPath, "dest", destPath, "size", srcInfo.Size())
	return nil
}

// shouldSkipFile determines if a file should be skipped during sync
func (sm *SyncManager) shouldSkipFile(path string) bool {
	base := filepath.Base(path)
	
	// Skip system files and temporary files
	skipPatterns := []string{
		".DS_Store", "Thumbs.db", ".tmp", ".temp",
		".swp", ".swo", "~", ".lock", ".pid",
		"desktop.ini", "Icon\r",
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

// processFileEvents processes file system events from the watcher
func (sm *SyncManager) processFileEvents(ctx context.Context) {
	eventChan := sm.watcher.GetEventChannel()
	
	for {
		select {
		case <-ctx.Done():
			logger.Info("File event processing stopped")
			return

		case event, ok := <-eventChan:
			if !ok {
				logger.Info("Event channel closed")
				return
			}

			sm.handleFileEvent(event)
		}
	}
}

// handleFileEvent processes a single file event
func (sm *SyncManager) handleFileEvent(event FileEvent) {
	// Skip if already syncing to avoid loops
	if sm.syncing {
		logger.Debug("Sync in progress, skipping event", "path", event.Path)
		return
	}

	logger.Debug("Processing file event", "path", event.Path, "op", event.Operation)

	// Determine sync direction based on event path
	if sm.watcher.isInICloudPath(event.Path) {
		sm.handleICloudEvent(event)
	} else if sm.watcher.isInOutputPath(event.Path) {
		sm.handleOutputEvent(event)
	}
}

// handleICloudEvent handles events from iCloud Drive
func (sm *SyncManager) handleICloudEvent(event FileEvent) {
	icloudPath, err := sm.config.getICloudPath()
	if err != nil {
		logger.Error("Failed to get iCloud path", "error", err)
		return
	}

	// Calculate relative path
	relPath, err := filepath.Rel(icloudPath, event.Path)
	if err != nil {
		logger.Error("Failed to calculate relative path", "path", event.Path, "error", err)
		return
	}

	// Calculate destination path in TM
	destPath := filepath.Join(sm.config.LocalTMPath, relPath)

	// Handle based on operation
	if strings.Contains(event.Operation, "CREATE") || strings.Contains(event.Operation, "WRITE") {
		if event.IsDir {
			err = sm.syncDirectory(event.Path, destPath)
		} else {
			err = sm.syncFile(event.Path, destPath)
		}
		
		if err != nil {
			logger.Error("Failed to sync from iCloud", "src", event.Path, "dest", destPath, "error", err)
		} else {
			logger.Info("Synced from iCloud", "src", event.Path, "dest", destPath)
		}
	} else if strings.Contains(event.Operation, "REMOVE") {
		err = os.RemoveAll(destPath)
		if err != nil {
			logger.Error("Failed to remove file", "path", destPath, "error", err)
		} else {
			logger.Info("Removed file", "path", destPath)
		}
	}
}

// handleOutputEvent handles events from TM outputs
func (sm *SyncManager) handleOutputEvent(event FileEvent) {
	outputPath := sm.config.getOutputPath()
	
	// Calculate relative path
	relPath, err := filepath.Rel(outputPath, event.Path)
	if err != nil {
		logger.Error("Failed to calculate relative path", "path", event.Path, "error", err)
		return
	}

	// Calculate destination path in iCloud
	icloudPath, err := sm.config.getICloudPath()
	if err != nil {
		logger.Error("Failed to get iCloud path", "error", err)
		return
	}
	
	destPath := filepath.Join(icloudPath, "outputs", relPath)

	// Handle based on operation
	if strings.Contains(event.Operation, "CREATE") || strings.Contains(event.Operation, "WRITE") {
		if event.IsDir {
			err = sm.syncDirectory(event.Path, destPath)
		} else {
			err = sm.syncFile(event.Path, destPath)
		}
		
		if err != nil {
			logger.Error("Failed to sync to iCloud", "src", event.Path, "dest", destPath, "error", err)
		} else {
			logger.Info("Synced to iCloud", "src", event.Path, "dest", destPath)
		}
	} else if strings.Contains(event.Operation, "REMOVE") {
		err = os.RemoveAll(destPath)
		if err != nil {
			logger.Error("Failed to remove file", "path", destPath, "error", err)
		} else {
			logger.Info("Removed file", "path", destPath)
		}
	}
}

// periodicSync performs periodic full sync
func (sm *SyncManager) periodicSync(ctx context.Context) {
	ticker := time.NewTicker(time.Duration(sm.config.SyncInterval) * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			logger.Info("Periodic sync stopped")
			return

		case <-ticker.C:
			logger.Debug("Performing periodic sync")
			sm.syncing = true
			
			err := sm.performInitialSync()
			if err != nil {
				logger.Error("Periodic sync failed", "error", err)
			}
			
			sm.syncing = false
		}
	}
}

// Stop stops the sync manager
func (sm *SyncManager) Stop() error {
	logger.Info("Stopping sync manager")
	
	err := sm.watcher.Stop()
	if err != nil {
		return fmt.Errorf("failed to stop file watcher: %w", err)
	}
	
	logger.Info("Sync manager stopped")
	return nil
}

// GetStats returns current sync statistics
func (sm *SyncManager) GetStats() SyncStats {
	return sm.syncStats
}