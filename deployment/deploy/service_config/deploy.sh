#!/bin/bash

# TM Deployment Script for Linode VPS
# Complete deployment automation for TM Legal Document Processing Platform

set -e

echo "🚀 TM Legal Document Processing Platform Deployment"
echo "Deploying with SSL, systemd service, and tenant isolation"

# Configuration
TENANT_NAME="${1:-mallon}"
DOMAIN="${2:-legal.satori-ai-tech.com}"
EMAIL="${3:-admin@satori-ai-tech.com}"
TM_USER="tm"
TM_GROUP="tm"
TM_HOME="/opt/tm"

echo "Tenant: $TENANT_NAME"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"

# Create TM user and group
echo "📋 Creating TM user and directory structure..."
sudo groupadd -f $TM_GROUP
sudo useradd -r -g $TM_GROUP -d $TM_HOME -s /bin/bash $TM_USER || true
sudo mkdir -p $TM_HOME
sudo chown $TM_USER:$TM_GROUP $TM_HOME

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx certbot git curl

# Copy TM application files (assuming they're already on the system)
echo "📁 Setting up TM application structure..."
sudo mkdir -p $TM_HOME/{dashboard,tiger,monkey,shared-schema,outputs,test-data,logs}
sudo chown -R $TM_USER:$TM_GROUP $TM_HOME

# Copy environment file
echo "⚙️ Setting up environment configuration..."
sudo cp tm.env /opt/tm/.env
sudo chown $TM_USER:$TM_GROUP /opt/tm/.env
sudo chmod 600 /opt/tm/.env

# Update environment file with actual values
sudo sed -i "s/TENANT_NAME=mallon/TENANT_NAME=$TENANT_NAME/" /opt/tm/.env
sudo sed -i "s/DOMAIN=legal.satori-ai-tech.com/DOMAIN=$DOMAIN/" /opt/tm/.env

# Generate secure session secret
SESSION_SECRET=$(openssl rand -hex 32)
sudo sed -i "s/your-secure-session-secret-here/$SESSION_SECRET/" /opt/tm/.env

# Install TM systemd service
echo "🔧 Installing TM systemd service..."
sudo cp tm-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tm-dashboard

# Setup SSL and nginx
echo "🔒 Setting up SSL and nginx..."
chmod +x ssl_setup.sh
sudo ./ssl_setup.sh

# Start TM service
echo "🚀 Starting TM service..."
sudo systemctl start tm-dashboard

# Verify deployment
echo "✅ Verifying deployment..."
sleep 5

# Check service status
if sudo systemctl is-active --quiet tm-dashboard; then
    echo "✅ TM Dashboard service is running"
else
    echo "❌ TM Dashboard service failed to start"
    sudo systemctl status tm-dashboard
    exit 1
fi

# Check nginx status
if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx failed to start"
    sudo systemctl status nginx
    exit 1
fi

# Test SSL certificate
if curl -s -k "https://$DOMAIN/health" | grep -q "Healthy"; then
    echo "✅ SSL endpoint is responding"
else
    echo "⚠️ SSL endpoint may not be ready yet (DNS propagation)"
fi

echo ""
echo "🎉 TM Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Access URL: https://$DOMAIN/$TENANT_NAME/"
echo "🔒 SSL Certificate: Let's Encrypt (auto-renewing)"
echo "⚙️ Service: systemctl status tm-dashboard"
echo "📊 Logs: journalctl -u tm-dashboard -f"
echo "🔄 Restart: sudo systemctl restart tm-dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo "1. Update DNS A record: $DOMAIN → $(curl -s ifconfig.me)"
echo "2. Test access: https://$DOMAIN/$TENANT_NAME/"
echo "3. Upload case files to: $TM_HOME/test-data/sync-test-cases/"
echo "4. Configure firm settings in dashboard"
echo ""
echo "🔄 To clone for new tenants:"
echo "1. Create Linode snapshot of this VPS"
echo "2. Deploy snapshot to new VPS"
echo "3. Run: sudo ./clone_tenant.sh [new-tenant-name]"
