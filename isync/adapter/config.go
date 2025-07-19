package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Config represents the application configuration
type Config struct {
	ICloudParentFolder string `json:"icloud_parent_folder"`
	ApiEndpoint        string `json:"api_endpoint"`
	ApiKey             string `json:"api_key"`
	SyncInterval       int    `json:"sync_interval"`
	LogLevel           string `json:"log_level"`
	BackupEnabled      bool   `json:"backup_enabled"`
}

// DefaultConfig returns a configuration with sensible defaults
func DefaultConfig() *Config {
	return &Config{
		ICloudParentFolder: "TM_Cases",
		ApiEndpoint:        "http://localhost:8000/api/icloud/upload",
		ApiKey:             "your_api_key_here",
		SyncInterval:       10,
		LogLevel:           "info",
		BackupEnabled:      true,
	}
}

// LoadConfig loads configuration from a JSON file
func LoadConfig(configPath string) (*Config, error) {
	// Check if config file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		logger.Warn("Config file not found, creating default config", "path", configPath)
		config := DefaultConfig()
		if err := SaveConfig(config, configPath); err != nil {
			return nil, fmt.Errorf("failed to create default config: %w", err)
		}
		return config, nil
	}

	// Read config file
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	// Parse JSON
	var config Config
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config JSON: %w", err)
	}

	// Validate configuration
	if err := validateConfig(&config); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	logger.Info("Configuration loaded successfully", "path", configPath)
	return &config, nil
}

// SaveConfig saves configuration to a JSON file
func SaveConfig(config *Config, configPath string) error {
	// Create directory if it doesn't exist
	dir := filepath.Dir(configPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	// Marshal to JSON with indentation
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config to JSON: %w", err)
	}

	// Write to file
	if err := os.WriteFile(configPath, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// validateConfig validates the configuration values
func validateConfig(config *Config) error {
	if config.ICloudParentFolder == "" {
		return fmt.Errorf("icloud_parent_folder cannot be empty")
	}

	if config.ApiEndpoint == "" {
		return fmt.Errorf("api_endpoint cannot be empty")
	}

	if config.ApiKey == "" {
		return fmt.Errorf("api_key cannot be empty")
	}

	if config.SyncInterval < 1 {
		return fmt.Errorf("sync_interval must be at least 1 second")
	}

	// Validate log level
	validLogLevels := map[string]bool{
		"debug": true,
		"info":  true,
		"warn":  true,
		"error": true,
	}
	if !validLogLevels[config.LogLevel] {
		return fmt.Errorf("invalid log_level: %s (must be debug, info, warn, or error)", config.LogLevel)
	}

	return nil
}

// getICloudPath returns the full path to the iCloud Drive folder
func (c *Config) getICloudPath() (string, error) {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("failed to get user home directory: %w", err)
	}

	icloudPath := filepath.Join(homeDir, "Library", "Mobile Documents", "com~apple~CloudDocs", c.ICloudParentFolder)
	
	// Check if iCloud Drive path exists
	if _, err := os.Stat(icloudPath); os.IsNotExist(err) {
		return "", fmt.Errorf("iCloud Drive path does not exist: %s", icloudPath)
	}

	return icloudPath, nil
}

// getOutputPath returns the path to TM outputs directory
func (c *Config) getOutputPath() (string, error) {
    homeDir, err := os.UserHomeDir()
    if err != nil {
        return "", fmt.Errorf("failed to get user home directory: %w", err)
    }
    // This is a bit of a guess, we might need a better way to configure this.
    // For now, let's assume a path relative to the user's home directory.
    // This should be updated if the TM project structure is known.
    return filepath.Join(homeDir, "satori-dev", "TM", "outputs"), nil
}