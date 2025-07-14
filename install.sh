#!/bin/bash

# TM Legal System Master Installation Script
# Production deployment script for Ubuntu 24.04

set -e

echo "🚀 Installing TM Legal Document Processing System..."
echo "=============================================="

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Run as regular user with sudo access."
   exit 1
fi

log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

log "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    curl \
    git \
    unzip \
    software-properties-common

log "Installing document processing dependencies..."
sudo apt install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libmagic1 \
    libmagic-dev \
    chromium-browser \
    fonts-liberation \
    fonts-dejavu-core

log "Creating TM system user and directories..."
sudo useradd -m -s /bin/bash tm-system || true
sudo mkdir -p /opt/tm-system
sudo chown $(whoami):$(whoami) /opt/tm-system

log "Installing Tiger service..."
if [ -d "tiger" ]; then
    cd tiger
    if [ -f "install.sh" ]; then
        chmod +x install.sh
        ./install.sh
    else
        warn "Tiger install.sh not found, installing manually..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
    fi
    cd ..
    success "Tiger service installed"
else
    error "Tiger directory not found"
    exit 1
fi

log "Installing Monkey service..."
if [ -d "monkey" ]; then
    cd monkey
    if [ -f "install.sh" ]; then
        chmod +x install.sh
        ./install.sh
    else
        warn "Monkey install.sh not found, installing manually..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
    fi
    cd ..
    success "Monkey service installed"
else
    error "Monkey directory not found"
    exit 1
fi

log "Installing Dashboard service..."
if [ -d "dashboard" ]; then
    cd dashboard
    if [ -f "install.sh" ]; then
        chmod +x install.sh
        ./install.sh
    else
        warn "Dashboard install.sh not found, installing manually..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
    fi
    cd ..
    success "Dashboard service installed"
else
    error "Dashboard directory not found"
    exit 1
fi

log "Installing Browser service..."
if [ -d "browser" ]; then
    cd browser
    if [ -f "package.json" ]; then
        npm install
    else
        warn "Browser package.json not found"
    fi
    cd ..
    success "Browser service installed"
else
    error "Browser directory not found"
    exit 1
fi

log "Installing shared schema..."
if [ -d "shared-schema" ]; then
    cd shared-schema
    pip3 install -e .
    cd ..
    success "Shared schema installed"
fi

log "Creating systemd services..."
sudo tee /etc/systemd/system/tm-dashboard.service > /dev/null <<EOF
[Unit]
Description=TM Dashboard Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)/dashboard
Environment=PATH=$(pwd)/dashboard/venv/bin
ExecStart=$(pwd)/dashboard/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/tm-browser.service > /dev/null <<EOF
[Unit]
Description=TM Browser PDF Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)/browser
Environment=NODE_ENV=production
ExecStart=/usr/bin/node pdf-generator.js
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

log "Configuring nginx..."
sudo tee /etc/nginx/sites-available/tm-system > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout       300;
        proxy_send_timeout          300;
        proxy_read_timeout          300;
        send_timeout                300;
    }
    
    location /static/ {
        alias $(pwd)/dashboard/static/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
    
    location /browser/ {
        proxy_pass http://127.0.0.1:8003/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/tm-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

log "Reloading systemd and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable tm-dashboard tm-browser nginx
sudo systemctl restart nginx

log "Starting TM services..."
sudo systemctl start tm-dashboard
sudo systemctl start tm-browser

# Wait for services to start
sleep 5

# Check service status
log "Checking service status..."
if sudo systemctl is-active --quiet tm-dashboard; then
    success "TM Dashboard service is running"
else
    error "TM Dashboard service failed to start"
    sudo systemctl status tm-dashboard
fi

if sudo systemctl is-active --quiet tm-browser; then
    success "TM Browser service is running"
else
    warn "TM Browser service failed to start (this is optional)"
    sudo systemctl status tm-browser
fi

if sudo systemctl is-active --quiet nginx; then
    success "Nginx is running"
else
    error "Nginx failed to start"
    sudo systemctl status nginx
fi

echo ""
echo "=============================================="
success "TM Legal System installation completed!"
echo ""
echo "🌐 Access the system at: http://$(curl -s ifconfig.me || hostname -I | awk '{print $1}')"
echo "📁 Installation directory: $(pwd)"
echo "📋 Service management:"
echo "   sudo systemctl status tm-dashboard"
echo "   sudo systemctl status tm-browser"
echo "   sudo systemctl logs -f tm-dashboard"
echo ""
echo "Test cases available:"
echo "   - Youssef case: test-data/sync-test-cases/youssef/"
echo "   - Rodriguez case: test-data/sync-test-cases/Rodriguez/"
echo ""
echo "Happy legal document processing! ⚖️"