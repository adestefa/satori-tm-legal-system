# TM iSync Adapter Makefile

# Variables
APP_NAME := tm-isync-adapter
VERSION := 1.0.0
BUILD_DIR := build
BINARY := $(BUILD_DIR)/$(APP_NAME)

# Go build flags
LDFLAGS := -ldflags "-X main.AppVersion=$(VERSION)"
BUILDFLAGS := -v

# Default target
.PHONY: all
all: build

# Build the application
.PHONY: build
build: clean
	@echo "Building $(APP_NAME) v$(VERSION)..."
	@mkdir -p $(BUILD_DIR)
	go build $(BUILDFLAGS) $(LDFLAGS) -o $(BINARY) .
	@echo "Build complete: $(BINARY)"

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)

# Install dependencies
.PHONY: deps
deps:
	@echo "Installing dependencies..."
	go mod download
	go mod tidy

# Run the application
.PHONY: run
run: build
	@echo "Running $(APP_NAME)..."
	./$(BINARY)

# Run with custom config
.PHONY: run-config
run-config: build
	@echo "Running $(APP_NAME) with config..."
	./$(BINARY) -config $(CONFIG)

# Install the binary to system
.PHONY: install
install: build
	@echo "Installing $(APP_NAME) to /usr/local/bin..."
	sudo cp $(BINARY) /usr/local/bin/$(APP_NAME)
	@echo "Installation complete"

# Uninstall the binary from system
.PHONY: uninstall
uninstall:
	@echo "Uninstalling $(APP_NAME)..."
	sudo rm -f /usr/local/bin/$(APP_NAME)
	@echo "Uninstallation complete"

# Format code
.PHONY: fmt
fmt:
	@echo "Formatting code..."
	go fmt ./...

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	go test -v ./...

# Build for multiple platforms
.PHONY: build-all
build-all: clean
	@echo "Building for multiple platforms..."
	@mkdir -p $(BUILD_DIR)
	GOOS=darwin GOARCH=amd64 go build $(BUILDFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(APP_NAME)-darwin-amd64 .
	GOOS=darwin GOARCH=arm64 go build $(BUILDFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(APP_NAME)-darwin-arm64 .
	GOOS=linux GOARCH=amd64 go build $(BUILDFLAGS) $(LDFLAGS) -o $(BUILD_DIR)/$(APP_NAME)-linux-amd64 .
	@echo "Cross-compilation complete"

# Create distribution package
.PHONY: dist
dist: build-all
	@echo "Creating distribution package..."
	@mkdir -p $(BUILD_DIR)/dist
	@cp config.json $(BUILD_DIR)/dist/
	@cp README.md $(BUILD_DIR)/dist/
	@tar -czf $(BUILD_DIR)/$(APP_NAME)-$(VERSION).tar.gz -C $(BUILD_DIR) dist $(APP_NAME)-*
	@echo "Distribution package created: $(BUILD_DIR)/$(APP_NAME)-$(VERSION).tar.gz"

# Development mode with file watching
.PHONY: dev
dev:
	@echo "Starting development mode..."
	@if command -v fswatch >/dev/null 2>&1; then \
		fswatch -o . | while read f; do \
			echo "Files changed, rebuilding..."; \
			make build && ./$(BINARY) -config config.json; \
		done; \
	else \
		echo "fswatch not found. Install with: brew install fswatch"; \
		exit 1; \
	fi

# Help target
.PHONY: help
help:
	@echo "TM iSync Adapter Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  build      - Build the application"
	@echo "  clean      - Clean build artifacts"
	@echo "  deps       - Install dependencies"
	@echo "  run        - Build and run the application"
	@echo "  run-config - Build and run with custom config (use CONFIG=path)"
	@echo "  install    - Install binary to system"
	@echo "  uninstall  - Remove binary from system"
	@echo "  fmt        - Format code"
	@echo "  test       - Run tests"
	@echo "  build-all  - Build for multiple platforms"
	@echo "  dist       - Create distribution package"
	@echo "  dev        - Development mode with file watching"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make run"
	@echo "  make run-config CONFIG=./custom-config.json"
	@echo "  make install"