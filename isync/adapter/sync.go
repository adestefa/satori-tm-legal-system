package main

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
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
	FilesUploaded   int
	FilesDownloaded int
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

	// Perform initial sync
	err := sm.performInitialSync()
	if err != nil {
		logger.Error("Initial sync failed", "error", err)
		// Don't return error - continue with event-based sync
	}

	// Start file watcher
	err = sm.watcher.Start(ctx)
	if err != nil {
		return fmt.Errorf("failed to start file watcher: %w", err)
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
	logger.Info("Performing initial sync...")

	// Sync from iCloud to Server
	err := sm.uploadICloudFiles()
	if err != nil {
		logger.Error("iCloud to Server sync failed", "error", err)
		return err
	}

	// Sync from TM to iCloud (for processed files)
	err = sm.syncTMToICloud()
	if err != nil {
		logger.Error("TM to iCloud sync failed", "error", err)
		return err
	}

	sm.syncStats.LastSync = time.Now()
	logger.Info("Initial sync completed", "files_uploaded", sm.syncStats.FilesUploaded, "files_downloaded", sm.syncStats.FilesDownloaded, "dirs_synced", sm.syncStats.DirectoriesSync)
	return nil
}

// uploadICloudFiles syncs files from iCloud Drive to the remote server
func (sm *SyncManager) uploadICloudFiles() error {
	icloudPath, err := sm.config.getICloudPath()
	if err != nil {
		return fmt.Errorf("failed to get iCloud path: %w", err)
	}

	logger.Info("Checking for files to upload from iCloud...", "source", icloudPath)

	return filepath.Walk(icloudPath, func(srcPath string, info os.FileInfo, err error) error {
		if err != nil {
			logger.Warn("Error walking iCloud directory", "path", srcPath, "error", err)
			sm.syncStats.Errors++
			return nil // Continue walking
		}

		if info.IsDir() || sm.shouldSkipFile(srcPath) {
			return nil
		}

		// Calculate relative path
		relPath, err := filepath.Rel(icloudPath, srcPath)
		if err != nil {
			logger.Warn("Failed to calculate relative path", "path", srcPath, "error", err)
			sm.syncStats.Errors++
			return nil
		}

		err = sm.uploadFile(srcPath, relPath)
		if err != nil {
			logger.Warn("Failed to upload file", "path", srcPath, "error", err)
			sm.syncStats.Errors++
		} else {
			sm.syncStats.FilesUploaded++
			logger.Info("Successfully uploaded file", "file", relPath)
		}

		return nil
	})
}

// uploadFile uploads a single file to the remote server
func (sm *SyncManager) uploadFile(filePath, relativePath string) error {
	logger.Info("Uploading file...", "file", relativePath)

	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("could not open file: %w", err)
	}
	defer file.Close()

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("file", filepath.Base(filePath))
	if err != nil {
		return fmt.Errorf("could not create form file: %w", err)
	}

	_, err = io.Copy(part, file)
	if err != nil {
		return fmt.Errorf("could not copy file to buffer: %w", err)
	}

	// Add relative path so the server knows where to save it
	_ = writer.WriteField("relative_path", relativePath)

	err = writer.Close()
	if err != nil {
		return fmt.Errorf("could not close multipart writer: %w", err)
	}

	req, err := http.NewRequest("POST", sm.config.ApiEndpoint, body)
	if err != nil {
		return fmt.Errorf("could not create request: %w", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("Authorization", "Bearer "+sm.config.ApiKey)

	client := &http.Client{Timeout: time.Second * 30}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("upload failed with status %d: %s", resp.StatusCode, string(respBody))
	}

	logger.Info("File uploaded successfully", "file", relativePath)
	return nil
}

// syncTMToICloud syncs files from TM outputs to iCloud Drive
func (sm *SyncManager) syncTMToICloud() error {
	outputPath, err := sm.config.getOutputPath()
	if err != nil {
		return fmt.Errorf("failed to get output path: %w", err)
	}

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
				sm.syncStats.FilesDownloaded++
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

	// Handle based on operation
	if strings.Contains(event.Operation, "CREATE") || strings.Contains(event.Operation, "WRITE") {
		if !event.IsDir {
			err = sm.uploadFile(event.Path, relPath)
			if err != nil {
				logger.Error("Failed to upload from iCloud", "path", event.Path, "error", err)
			}
		}
	} else if strings.Contains(event.Operation, "REMOVE") {
		// TODO: Implement file deletion on the server if needed
		logger.Info("File removed in iCloud, no action taken on server", "path", relPath)
	}
}

// handleOutputEvent handles events from TM outputs
func (sm *SyncManager) handleOutputEvent(event FileEvent) {
	outputPath, err := sm.config.getOutputPath()
	if err != nil {
		logger.Error("Failed to get output path", "error", err)
		return
	}

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
