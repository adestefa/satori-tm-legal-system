#\!/bin/bash

# TM Legal System Production Deployment Guide
# ===========================================
# This script documents the complete deployment process performed on 2025-07-14
# Server: Ubuntu 24.04 LTS on Linode (198.74.59.11)
# 
# Usage: This is a DOCUMENTATION script - review and execute sections manually
# or use individual commands as needed for new deployments.

set -e

echo "🚀 TM Legal System Production Deployment Guide"
echo "=============================================="
echo "Server: Ubuntu 24.04 LTS"
echo "RAM: 4GB+ recommended"
echo "Storage: 50GB+ recommended"
echo ""

# STEP 1: Server Preparation
echo "📋 STEP 1: SERVER PREPARATION"
echo "=============================="
cat << 'STEP1'
# 1.1 Connect to fresh server as root
ssh root@<server_ip>

# 1.2 Create deployment user
useradd -m -s /bin/bash -G sudo deploy
echo "deploy:TM2025Deploy\!" | chpasswd

# 1.3 Configure passwordless sudo
echo "deploy ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/deploy
chmod 440 /etc/sudoers.d/deploy

# 1.4 Update system
apt update && apt upgrade -y

# 1.5 Install basic tools
apt install -y git curl wget software-properties-common sshpass
STEP1

# STEP 2: Clone Repository
echo ""
echo "📋 STEP 2: CLONE REPOSITORY"
echo "============================"
cat << 'STEP2'
# 2.1 Switch to deploy user
su - deploy

# 2.2 Clone TM repository
cd /home/deploy
git clone https://github.com/adestefa/satori-tm-legal-system.git
cd satori-tm-legal-system

# 2.3 Verify repository contents
ls -la
STEP2

# STEP 3: Run Installation
echo ""
echo "📋 STEP 3: RUN INSTALLATION"
echo "============================"
cat << 'STEP3'
# 3.1 Make installation script executable
chmod +x install.sh

# 3.2 Run the comprehensive installation script
./install.sh

# This script will:
# - Install Python 3.12, Node.js 18, nginx
# - Install document processing tools (poppler, tesseract, chromium)
# - Set up all 4 TM services (Tiger, Monkey, Dashboard, Browser)
# - Create virtual environments with dependencies
# - Configure systemd services
# - Set up nginx reverse proxy
# - Create output directories
STEP3

# STEP 4: Post-Installation Fixes (Applied in Production)
echo ""
echo "📋 STEP 4: POST-INSTALLATION FIXES"
echo "==================================="
cat << 'STEP4'
# 4.1 Fix file permissions for nginx static files
sudo chmod -R 755 /home/deploy/satori-tm-legal-system/dashboard/static/
sudo chmod 755 /home/deploy/satori-tm-legal-system/dashboard/
sudo chmod 755 /home/deploy/satori-tm-legal-system/

# 4.2 Create missing __init__.py for Python package structure
touch /home/deploy/satori-tm-legal-system/dashboard/__init__.py

# 4.3 Install missing FastAPI dependency
cd /home/deploy/satori-tm-legal-system/dashboard
source venv/bin/activate
pip install python-multipart
deactivate

# 4.4 Create required output directories
mkdir -p /home/deploy/satori-tm-legal-system/dashboard/outputs
mkdir -p /home/deploy/satori-tm-legal-system/outputs/tests
mkdir -p /home/deploy/satori-tm-legal-system/outputs/browser
mkdir -p /home/deploy/satori-tm-legal-system/outputs/tiger
mkdir -p /home/deploy/satori-tm-legal-system/outputs/monkey

# 4.5 Update nginx configuration (simplified - let FastAPI handle all routes)
sudo tee /etc/nginx/sites-available/tm-system > /dev/null << NGINXEOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    # Proxy everything to FastAPI
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
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/tm-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 4.6 Create and configure systemd services
sudo tee /etc/systemd/system/tm-dashboard.service > /dev/null << SERVICEEOF
[Unit]
Description=TM Dashboard Service
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/deploy/satori-tm-legal-system
Environment=PATH=/home/deploy/satori-tm-legal-system/dashboard/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/home/deploy/satori-tm-legal-system
ExecStart=/home/deploy/satori-tm-legal-system/dashboard/venv/bin/uvicorn dashboard.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo systemctl daemon-reload
sudo systemctl enable tm-dashboard
sudo systemctl start tm-dashboard
STEP4

# STEP 5: Verification
echo ""
echo "📋 STEP 5: VERIFICATION"
echo "======================="
cat << 'STEP5'
# 5.1 Check service status
sudo systemctl status tm-dashboard
sudo systemctl status nginx

# 5.2 Test web interface
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" http://localhost:8000/login

# 5.3 Test from external access
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" http://<server_ip>/login

# 5.4 Verify login credentials work
# Access: http://<server_ip>/login
# Credentials: Admin/admin or Kevin/AutoLegal2025\!
STEP5

# PRODUCTION FIXES APPLIED
echo ""
echo "📋 PRODUCTION FIXES APPLIED"
echo "============================"
cat << 'FIXES'
The following fixes were applied to the production system and are now in the GitHub repository:

1. DASHBOARD FILE FILTERING:
   - Modified main.py to exclude generated _complaint.pdf files from input lists
   - Pattern: *_complaint.pdf files are now filtered out
   - Affects lines ~797 and ~851 in dashboard/main.py

2. AUTHENTICATION ENHANCEMENT:
   - Added Kevin/AutoLegal2025\! credentials alongside Admin/admin
   - Both credential sets work for system access
   - Modified authenticate_user() function in dashboard/main.py

3. DEPENDENCY FIXES:
   - Added python-multipart package for FastAPI form handling
   - Created __init__.py for proper Python package structure
   - Fixed file permissions for nginx static file serving

4. CLEAR CASE SCRIPT:
   - scripts/clear_case.sh already worked correctly
   - Removes generated PDFs with pattern: {case_name}_complaint.pdf
   - Cleans all output directories and resets case status

5. NGINX CONFIGURATION:
   - Simplified to proxy all requests to FastAPI
   - Fixed static file serving through application
   - Added WebSocket support for real-time updates

These fixes are now committed to the GitHub repository and can be deployed to new servers.
FIXES

echo ""
echo "🎯 DEPLOYMENT COMPLETE"
echo "======================"
echo "✅ TM Legal System should now be accessible at: http://<server_ip>"
echo "✅ Login credentials: Admin/admin or Kevin/AutoLegal2025\!"
echo "✅ Test cases available: Rodriguez and Youssef"
echo "✅ All 4 services configured: Tiger, Monkey, Dashboard, Browser"
echo ""
echo "🔧 Management Commands:"
echo "  sudo systemctl status tm-dashboard    # Check service status"
echo "  sudo systemctl restart tm-dashboard   # Restart service"
echo "  sudo systemctl logs -f tm-dashboard   # View logs"
echo "  ./scripts/clear_case.sh <case_name>   # Reset case"
echo ""
echo "📁 Important directories:"
echo "  /home/deploy/satori-tm-legal-system/           # Main application"
echo "  /home/deploy/satori-tm-legal-system/dashboard/outputs/  # Case outputs"
echo "  /home/deploy/satori-tm-legal-system/test-data/sync-test-cases/  # Test cases"
echo ""
echo "🚀 Ready for production use\!"

