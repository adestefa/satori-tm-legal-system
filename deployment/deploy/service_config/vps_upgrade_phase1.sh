#!/bin/bash

# VPS SSL Upgrade Script
# Run this ON THE VPS after SSH keys are set up

set -e

echo "🚀 TM VPS SSL Upgrade - Phase 1"
echo "Current TM location: /home/deploy/satori-tm-legal-system/"
echo "Target location: /opt/tm/"

# Update system first
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "📦 Installing SSL and web server packages..."
apt install -y nginx certbot python3-certbot-nginx curl wget git

# Create TM user and directories
echo "👥 Setting up TM user and directory structure..."
groupadd -f tm
useradd -r -g tm -d /opt/tm -s /bin/bash tm || true
mkdir -p /opt/tm
chown tm:tm /opt/tm

# Copy existing TM installation
echo "📁 Migrating TM installation..."
if [ -d "/home/deploy/satori-tm-legal-system" ]; then
    cp -r /home/deploy/satori-tm-legal-system/* /opt/tm/
    chown -R tm:tm /opt/tm
    echo "✅ TM files migrated to /opt/tm/"
else
    echo "❌ Source directory not found: /home/deploy/satori-tm-legal-system"
    echo "Please verify the correct path and update this script"
    exit 1
fi

# Create required directories
echo "📁 Creating additional directories..."
mkdir -p /opt/tm/{logs,config,uploads}
mkdir -p /opt/tm/test-data/sync-test-cases
mkdir -p /opt/tm/outputs/{tests,tiger,monkey,browser}
chown -R tm:tm /opt/tm

# Check if TM dashboard exists and has the right structure
echo "🔍 Verifying TM installation..."
if [ -f "/opt/tm/dashboard/main.py" ]; then
    echo "✅ TM Dashboard found"
else
    echo "❌ TM Dashboard main.py not found"
    echo "Directory contents:"
    ls -la /opt/tm/
    echo "Please verify TM installation structure"
    exit 1
fi

# Create environment file template
echo "⚙️ Creating environment configuration..."
cat > /opt/tm/.env << 'EOF'
# TM Environment Configuration
TENANT_NAME=mallon
DOMAIN=legal.satori-ai-tech.com
BASE_URL=https://legal.satori-ai-tech.com/mallon

# TM Dashboard Configuration
PORT=8000
HOST=127.0.0.1
DEBUG=false
LOG_LEVEL=INFO

# Security
SESSION_SECRET=REPLACE_WITH_SECURE_SECRET
ALLOWED_HOSTS=legal.satori-ai-tech.com,127.0.0.1,localhost

# File Paths
CASE_DIRECTORY=/opt/tm/test-data/sync-test-cases
OUTPUT_DIR=/opt/tm/outputs
UPLOAD_DIR=/opt/tm/uploads

# Email (optional)
SMTP_SERVER=smtp.satori-ai-tech.com
SMTP_PORT=587
SMTP_USERNAME=tm-noreply@satori-ai-tech.com
SMTP_PASSWORD=your-smtp-password
EOF

# Generate secure session secret
SESSION_SECRET=$(openssl rand -hex 32)
sed -i "s/REPLACE_WITH_SECURE_SECRET/$SESSION_SECRET/" /opt/tm/.env
chown tm:tm /opt/tm/.env
chmod 600 /opt/tm/.env

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/tm-dashboard.service << 'EOF'
[Unit]
Description=TM Legal Document Processing Platform
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=tm
Group=tm
WorkingDirectory=/opt/tm/dashboard
Environment=PATH=/opt/tm/dashboard/venv/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/opt/tm/.env
ExecStart=/opt/tm/dashboard/venv/bin/python main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/tm
ProtectHome=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tm-dashboard

# Resource limits
LimitNOFILE=65536
MemoryLimit=2G

[Install]
WantedBy=multi-user.target
EOF

# Enable service but don't start yet
systemctl daemon-reload
systemctl enable tm-dashboard

# Check if TM virtual environment exists
echo "🐍 Checking Python virtual environment..."
if [ -d "/opt/tm/dashboard/venv" ]; then
    echo "✅ Virtual environment found"
else
    echo "❌ Virtual environment not found, creating one..."
    cd /opt/tm/dashboard
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install fastapi uvicorn
    chown -R tm:tm /opt/tm/dashboard/venv
fi

# Stop any existing TM processes
echo "🛑 Stopping existing TM processes..."
pkill -f "python.*main.py" || true
sleep 2

echo ""
echo "✅ Phase 1 Complete - TM Migration and Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 TM Location: /opt/tm/"
echo "👥 TM User: tm:tm"
echo "⚙️ Environment: /opt/tm/.env"
echo "🔧 Service: systemctl status tm-dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔄 Next Steps:"
echo "1. Verify TM can start: sudo systemctl start tm-dashboard"
echo "2. Check status: sudo systemctl status tm-dashboard"
echo "3. View logs: journalctl -u tm-dashboard -f"
echo "4. Test local access: curl http://127.0.0.1:8000"
echo "5. Then run SSL setup script"
echo ""
echo "Ready for SSL configuration!"
