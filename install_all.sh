#!/bin/bash

# Tiger-Monkey Legal Document Processing System - Automated Installation
# This script automates the complete installation process from a fresh repository clone

set -e

# Color output functions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Banner
echo ""
echo -e "${PURPLE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    TIGER-MONKEY SYSTEM                        ║${NC}"
echo -e "${PURPLE}║              Legal Document Processing Platform               ║${NC}"
echo -e "${PURPLE}║                  Automated Installation                       ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Navigate to script directory
cd "$(dirname "$0")"
INSTALL_DIR=$(pwd)
log "Installation directory: $INSTALL_DIR"

# Check operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    error "Unsupported operating system: $OSTYPE"
    exit 1
fi
info "Detected operating system: $OS"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
step "Checking prerequisites..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        success "Python $PYTHON_VERSION detected"
    else
        error "Python 3.8+ required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    success "Node.js $NODE_VERSION detected"
else
    error "Node.js not found. Please install Node.js 16+"
    if [[ "$OS" == "macOS" ]]; then
        echo "Install with: brew install node"
    elif [[ "$OS" == "Linux" ]]; then
        echo "Install with: sudo apt install nodejs npm"
    fi
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    success "npm $NPM_VERSION detected"
else
    error "npm not found. Please install npm"
    exit 1
fi

# Check pip
if command_exists pip3; then
    success "pip3 detected"
else
    error "pip3 not found. Please install pip3"
    exit 1
fi

# System-specific dependency checks
if [[ "$OS" == "macOS" ]]; then
    if command_exists brew; then
        success "Homebrew detected"
    else
        warn "Homebrew not detected. Some dependencies may be missing."
    fi
fi

echo ""
step "Starting installation process..."

# Phase 1: Shared Schema Foundation
echo ""
log "Phase 1: Installing Shared Schema Foundation"
echo "=============================================="

if [ -d "shared-schema" ]; then
    cd shared-schema
    info "Installing shared schema package..."
    pip3 install -e . || {
        error "Failed to install shared schema"
        exit 1
    }
    cd ..
    success "Shared schema installed successfully"
    
    # Verify installation
    if python3 -c "from satori_schema.hydrated_json_schema import HydratedJSON; print('Schema import successful')" 2>/dev/null; then
        success "Shared schema verification passed"
    else
        warn "Shared schema verification failed - continuing anyway"
    fi
else
    error "shared-schema directory not found"
    exit 1
fi

# Phase 2: Tiger Service Installation
echo ""
log "Phase 2: Installing Tiger Service (ML Document Analysis)"
echo "========================================================="

if [ -d "tiger" ]; then
    cd tiger
    info "Installing Tiger service with ML dependencies..."
    
    # Make install script executable
    chmod +x install.sh
    
    # Run Tiger installation
    ./install.sh || {
        error "Tiger installation failed"
        exit 1
    }
    
    cd ..
    success "Tiger service installed successfully"
    
    # Verify Tiger installation
    cd tiger
    if ./run.sh info >/dev/null 2>&1; then
        success "Tiger service verification passed"
    else
        warn "Tiger service verification failed - continuing anyway"
    fi
    cd ..
else
    error "tiger directory not found"
    exit 1
fi

# Phase 3: Monkey Service Installation
echo ""
log "Phase 3: Installing Monkey Service (Document Generation)"
echo "========================================================="

if [ -d "monkey" ]; then
    cd monkey
    info "Installing Monkey service with template engine..."
    
    # Make install script executable
    chmod +x install.sh
    
    # Run Monkey installation
    ./install.sh || {
        error "Monkey installation failed"
        exit 1
    }
    
    cd ..
    success "Monkey service installed successfully"
    
    # Verify Monkey installation
    cd monkey
    if ./run.sh --help >/dev/null 2>&1; then
        success "Monkey service verification passed"
    else
        warn "Monkey service verification failed - continuing anyway"
    fi
    cd ..
else
    error "monkey directory not found"
    exit 1
fi

# Phase 4: Dashboard Service Installation
echo ""
log "Phase 4: Installing Dashboard Service (Web Interface)"
echo "====================================================="

if [ -d "dashboard" ]; then
    cd dashboard
    info "Installing Dashboard service (Python + Node.js hybrid)..."
    
    # Make install script executable
    chmod +x install.sh
    
    # Run Dashboard installation
    ./install.sh || {
        error "Dashboard installation failed"
        exit 1
    }
    
    # Fix Critical Issue 1: Install missing python-multipart dependency
    info "Installing critical missing dependency: python-multipart..."
    ./venv/bin/pip install python-multipart || {
        warn "Failed to install python-multipart - dashboard may not start"
    }
    
    # Fix Critical Issue 2: Create missing outputs directory
    info "Creating required outputs directory..."
    mkdir -p outputs
    
    cd ..
    success "Dashboard service installed successfully with critical fixes"
    
    # Verify Dashboard installation
    if [ -d "dashboard/venv" ] && [ -d "dashboard/node_modules" ] && [ -d "dashboard/outputs" ]; then
        success "Dashboard service verification passed"
        
        # Verify python-multipart is installed
        if dashboard/venv/bin/python -c "import multipart" 2>/dev/null; then
            success "python-multipart dependency verified"
        else
            warn "python-multipart verification failed"
        fi
    else
        warn "Dashboard service verification failed - missing required components"
    fi
else
    error "dashboard directory not found"
    exit 1
fi

# Phase 5: Browser Service Installation
echo ""
log "Phase 5: Installing Browser Service (PDF Generation)"
echo "===================================================="

if [ -d "browser" ]; then
    cd browser
    info "Installing Browser service (Puppeteer/Chromium)..."
    
    # Install Node.js dependencies
    npm install || {
        error "Browser service installation failed"
        exit 1
    }
    
    cd ..
    success "Browser service installed successfully"
    
    # Verify Browser installation
    if [ -d "browser/node_modules" ]; then
        success "Browser service verification passed"
    else
        warn "Browser service verification failed - missing node_modules"
    fi
else
    warn "browser directory not found - PDF generation will not be available"
fi

# Phase 6: Create outputs directory
echo ""
log "Phase 6: Setting up output directories"
echo "======================================"

mkdir -p outputs/{tiger,monkey,browser,tests}
success "Output directories created"

# Phase 7: Make all shell scripts executable
echo ""
log "Phase 7: Setting script permissions"
echo "==================================="

find . -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
success "Shell scripts made executable"

# Installation Summary
echo ""
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    INSTALLATION COMPLETE!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Display installation results
echo -e "${CYAN}📋 Installation Summary:${NC}"
echo "========================"

# Check each service
if [ -d "tiger/venv" ]; then
    echo -e "🐅 Tiger Service:    ${GREEN}✅ Installed${NC} (ML Document Analysis)"
else
    echo -e "🐅 Tiger Service:    ${RED}❌ Failed${NC}"
fi

if [ -d "monkey/venv" ]; then
    echo -e "🐒 Monkey Service:   ${GREEN}✅ Installed${NC} (Document Generation)"
else
    echo -e "🐒 Monkey Service:   ${RED}❌ Failed${NC}"
fi

if [ -d "dashboard/venv" ] && [ -d "dashboard/node_modules" ]; then
    echo -e "🖥️  Dashboard Service: ${GREEN}✅ Installed${NC} (Web Interface)"
else
    echo -e "🖥️  Dashboard Service: ${RED}❌ Failed${NC}"
fi

if [ -d "browser/node_modules" ]; then
    echo -e "🌐 Browser Service:  ${GREEN}✅ Installed${NC} (PDF Generation)"
else
    echo -e "🌐 Browser Service:  ${YELLOW}⚠️  Not Available${NC}"
fi

echo ""
echo -e "${CYAN}🚀 Quick Start:${NC}"
echo "==============="
echo "1. Start the dashboard:"
echo "   cd dashboard && ./start.sh"
echo ""
echo "2. Access the web interface:"
echo "   http://127.0.0.1:8000"
echo ""
echo "3. Test with sample cases:"
echo "   - Youssef case: test-data/sync-test-cases/youssef/"
echo "   - Rodriguez case: test-data/sync-test-cases/Rodriguez/"
echo ""

echo -e "${CYAN}📚 Documentation:${NC}"
echo "=================="
echo "- Installation Guide: CLAUDE_INSTALL_INSTRUCTIONS.md"
echo "- System Overview:    CLAUDE.md"
echo "- Service Details:    tiger/CLAUDE.md, monkey/CLAUDE.md, dashboard/CLAUDE.md"
echo ""

echo -e "${CYAN}🔧 Manual Service Commands:${NC}"
echo "==========================="
echo "Tiger:     cd tiger && ./run.sh info"
echo "Monkey:    cd monkey && ./run.sh --help"
echo "Dashboard: cd dashboard && ./start.sh"
echo "Browser:   cd browser && node pdf-generator.js --test"
echo ""

echo -e "${CYAN}📁 Directory Structure:${NC}"
echo "======================"
echo "- tiger/venv/         Python virtual environment for Tiger"
echo "- monkey/venv/        Python virtual environment for Monkey"
echo "- dashboard/venv/     Python virtual environment for Dashboard"
echo "- dashboard/node_modules/  Node.js dependencies for Dashboard"
echo "- browser/node_modules/    Node.js dependencies for Browser"
echo "- shared-schema/      Common data models"
echo "- outputs/           Generated documents and data"
echo ""

# Final status
if [ -d "tiger/venv" ] && [ -d "monkey/venv" ] && [ -d "dashboard/venv" ] && [ -d "dashboard/node_modules" ]; then
    echo -e "${GREEN}🎉 Tiger-Monkey System is ready for legal document processing!${NC}"
    echo ""

    # Post-Installation Verification and Dashboard Startup
    echo -e "${CYAN}🚀 Starting Dashboard Automatically...${NC}"
    echo "=================================="

    cd dashboard
    info "Starting dashboard with automatic verification..."

    # Start dashboard
    ./start.sh

    # Wait for startup
    sleep 5

    # Verify dashboard is responding
    info "Verifying dashboard accessibility..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 2>/dev/null || echo "000")

    if [ "$response" = "302" ] || [ "$response" = "200" ]; then
        success "Dashboard is running and accessible!"
        echo -e "${GREEN}🌐 Access your dashboard at: http://127.0.0.1:8000${NC}"
    elif [ "$response" = "000" ]; then
        warn "Dashboard may still be starting up or curl is not available"
        echo -e "${YELLOW}🌐 Try accessing: http://127.0.0.1:8000${NC}"
        echo -e "${YELLOW}💡 If it doesn't work, check: cat dashboard/start_server.log${NC}"
    else
        warn "Dashboard returned HTTP $response - may not be fully ready"
        echo -e "${YELLOW}🌐 Try accessing: http://127.0.0.1:8000${NC}"
    fi

    echo ""
    echo -e "${CYAN}📋 Quick Verification Commands:${NC}"
    echo "==============================="
    echo "Check dashboard status:    curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1:8000"
    echo "View dashboard logs:       cat dashboard/start_server.log"
    echo "Test Tiger service:        cd tiger && ./run.sh info"
    echo "Test Monkey service:       cd monkey && ./run.sh --help"
    echo "Test Browser service:      cd browser && node pdf-generator.js --test"

    cd ..
else
    echo -e "${RED}⚠️  Some services failed to install. Check the error messages above.${NC}"
    echo ""
    echo -e "${CYAN}🔧 Try the manual fix commands:${NC}"
    echo "cd dashboard"
    echo "./venv/bin/pip install python-multipart"
    echo "mkdir -p outputs"
    echo "./start.sh"
    exit 1
fi

echo ""