package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"
)

const (
	AppName    = "TM iSync Adapter"
	AppVersion = "1.0.0"
)

// Application represents the main application
type Application struct {
	config      *Config
	syncManager *SyncManager
	ctx         context.Context
	cancel      context.CancelFunc
}

// NewApplication creates a new application instance
func NewApplication(configPath string) (*Application, error) {
	// Initialize logger with default level first (to prevent crashes in LoadConfig)
	InitLogger("info")
	
	// Load configuration
	config, err := LoadConfig(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to load configuration: %w", err)
	}

	// Re-initialize logger with config level
	InitLogger(config.LogLevel)

	// Create sync manager
	syncManager, err := NewSyncManager(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create sync manager: %w", err)
	}

	// Create context with cancellation
	ctx, cancel := context.WithCancel(context.Background())

	return &Application{
		config:      config,
		syncManager: syncManager,
		ctx:         ctx,
		cancel:      cancel,
	}, nil
}

// Start starts the application
func (app *Application) Start() error {
	logger.Info("Starting TM iSync Adapter", "version", AppVersion)
	
	// Log configuration
	logger.Info("Configuration loaded",
		"icloud_parent_folder", app.config.ICloudParentFolder,
		"api_endpoint", app.config.ApiEndpoint,
		"sync_interval", app.config.SyncInterval,
		"log_level", app.config.LogLevel,
		"backup_enabled", app.config.BackupEnabled)

	// Validate paths
	err := app.validatePaths()
	if err != nil {
		return fmt.Errorf("path validation failed: %w", err)
	}

	// Start sync manager
	err = app.syncManager.Start(app.ctx)
	if err != nil {
		return fmt.Errorf("failed to start sync manager: %w", err)
	}

	logger.Info("TM iSync Adapter started successfully")
	return nil
}

// validatePaths validates that required paths exist and are accessible
func (app *Application) validatePaths() error {
	// Check iCloud path
	icloudPath, err := app.config.getICloudPath()
	if err != nil {
		return fmt.Errorf("failed to get iCloud path: %w", err)
	}

	if _, err := os.Stat(icloudPath); os.IsNotExist(err) {
		logger.Warn("iCloud path does not exist, attempting to create", "path", icloudPath)
		err = os.MkdirAll(icloudPath, 0755)
		if err != nil {
			return fmt.Errorf("failed to create iCloud directory: %w", err)
		}
		logger.Info("iCloud directory created", "path", icloudPath)
	}

	// Check outputs path (optional)
	outputPath, err := app.config.getOutputPath()
	if err != nil {
		logger.Warn("Could not determine output path", "error", err)
	} else {
		if _, err := os.Stat(outputPath); os.IsNotExist(err) {
			logger.Info("TM outputs directory does not exist, will be created when needed", "path", outputPath)
		}
	}

	return nil
}

// Stop stops the application gracefully
func (app *Application) Stop() error {
	logger.Info("Stopping TM iSync Adapter")
	
	// Cancel context to stop all goroutines
	app.cancel()

	// Stop sync manager
	err := app.syncManager.Stop()
	if err != nil {
		logger.Error("Failed to stop sync manager", "error", err)
		return err
	}

	logger.Info("TM iSync Adapter stopped successfully")
	return nil
}

// Run runs the application with signal handling
func (app *Application) Run() error {
	// Start the application
	err := app.Start()
	if err != nil {
		return err
	}

	// Set up signal handling
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Start status reporter
	go app.statusReporter()

	// Wait for signal
	sig := <-sigChan
	logger.Info("Received signal, shutting down", "signal", sig.String())

	// Stop the application
	return app.Stop()
}

// statusReporter periodically reports application status
func (app *Application) statusReporter() {
	ticker := time.NewTicker(5 * time.Minute) // Report every 5 minutes
	defer ticker.Stop()

	for {
		select {
		case <-app.ctx.Done():
			return
		case <-ticker.C:
			stats := app.syncManager.GetStats()
			logger.Info("Sync status",
				"files_uploaded", stats.FilesUploaded,
				"files_downloaded", stats.FilesDownloaded,
				"directories_synced", stats.DirectoriesSync,
				"errors", stats.Errors,
				"last_sync", stats.LastSync.Format("2006-01-02 15:04:05"),
				"uptime", time.Since(stats.StartTime).String())
		}
	}
}

// printUsage prints usage information
func printUsage() {
	fmt.Printf("%s v%s\n", AppName, AppVersion)
	fmt.Println("Usage: tm-isync-adapter [OPTIONS]")
	fmt.Println()
	fmt.Println("Options:")
	fmt.Println("  -config string    Path to configuration file (default: config.json)")
	fmt.Println("  -version          Show version information")
	fmt.Println("  -help             Show this help message")
	fmt.Println()
	fmt.Println("Environment Variables:")
	fmt.Println("  TM_ISYNC_CONFIG   Path to configuration file")
	fmt.Println()
	fmt.Println("Example:")
	fmt.Println("  tm-isync-adapter -config /path/to/config.json")
	fmt.Println()
}

// printVersion prints version information
func printVersion() {
	fmt.Printf("%s v%s\n", AppName, AppVersion)
	fmt.Println("Built with Go")
	fmt.Println("Copyright © 2025 Tiger-Monkey Legal Document Processing System")
}

// main is the application entry point
func main() {
	// Parse command line flags
	var (
		configPath = flag.String("config", "config.json", "Path to configuration file")
		version    = flag.Bool("version", false, "Show version information")
		help       = flag.Bool("help", false, "Show help message")
	)
	flag.Parse()

	// Handle version flag
	if *version {
		printVersion()
		return
	}

	// Handle help flag
	if *help {
		printUsage()
		return
	}

	// Check for config path from environment
	if envConfig := os.Getenv("TM_ISYNC_CONFIG"); envConfig != "" {
		*configPath = envConfig
	}

	// Convert to absolute path
	absConfigPath, err := filepath.Abs(*configPath)
	if err != nil {
		fmt.Printf("Error: Failed to resolve config path: %v\n", err)
		os.Exit(1)
	}

	// Create application
	app, err := NewApplication(absConfigPath)
	if err != nil {
		fmt.Printf("Error: Failed to create application: %v\n", err)
		os.Exit(1)
	}

	// Run application
	err = app.Run()
	if err != nil {
		logger.Error("Application failed", "error", err)
		os.Exit(1)
	}
}

// Health check function for external monitoring
func HealthCheck() (bool, string) {
	// Simple health check - verify we can access the file system
	tempDir := os.TempDir()
	testFile := filepath.Join(tempDir, "tm-isync-health-check")
	
	// Write test file
	err := os.WriteFile(testFile, []byte("health check"), 0644)
	if err != nil {
		return false, fmt.Sprintf("Failed to write test file: %v", err)
	}
	
	// Read test file
	_, err = os.ReadFile(testFile)
	if err != nil {
		return false, fmt.Sprintf("Failed to read test file: %v", err)
	}
	
	// Clean up
	os.Remove(testFile)
	
	return true, "Service is healthy"
}