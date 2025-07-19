#!/bin/bash

# Complete Fresh VPS Deployment
# Deploys TM from GitHub repo to production SSL

set -e

VPS_HOST="tm-fresh"
DOMAIN="legal.satori-ai-tech.com"
TENANT="mallon"
REPO_URL="https://github.com/your-username/TM.git"  # UPDATE THIS

echo "🚀 Complete Fresh TM Deployment"
echo "VPS: $VPS_HOST"
echo "Domain: $DOMAIN"
echo "Tenant: $TENANT"

# Test SSH connection
echo "🔍 Testing SSH connection..."
if ! ssh $VPS_HOST "echo 'SSH connection successful'"; then
    echo "❌ SSH connection failed. Run ./setup_fresh_vps.sh first"
    exit 1
fi

echo ""
echo "📦 Step 1: System setup and dependencies..."
ssh $VPS_HOST "
    apt update && apt upgrade -y
    apt install -y git python3 python3-pip python3-venv nginx certbot curl wget
    groupadd -f tm
    useradd -r -g tm -d /opt/tm -s /bin/bash tm || true
    mkdir -p /opt/tm
"

echo ""
echo "📁 Step 2: Cloning TM repository..."
ssh $VPS_HOST "
    cd /opt
    # If using private repo, you'll need to setup SSH keys
    # For now, assuming public or you'll manually upload
    git clone $REPO_URL tm || echo 'Manual repo setup required'
    chown -R tm:tm /opt/tm
"

echo ""
echo "🔧 Step 3: Installing TM services..."
ssh $VPS_HOST "
    cd /opt/tm
    
    # Install Tiger service
    cd tiger && ./install.sh && cd ..
    
    # Install Monkey service  
    cd monkey && ./install.sh && cd ..
    
    # Install Dashboard service
    cd dashboard && npm install && cd ..
    
    chown -R tm:tm /opt/tm
"

echo ""
echo "⚙️ Step 4: Configuration setup..."
# Upload our config files
scp tm.env tm-dashboard.service nginx-tm-legal.conf $VPS_HOST:/tmp/

ssh $VPS_HOST "
    # Setup environment
    cp /tmp/tm.env /opt/tm/.env
    SESSION_SECRET=\$(openssl rand -hex 32)
    sed -i \"s/REPLACE_WITH_SECURE_SECRET/\$SESSION_SECRET/\" /opt/tm/.env
    chown tm:tm /opt/tm/.env
    chmod 600 /opt/tm/.env
    
    # Setup systemd service
    cp /tmp/tm-dashboard.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable tm-dashboard
"

echo ""
echo "🚀 Step 5: Starting TM service..."
ssh $VPS_HOST "
    systemctl start tm-dashboard
    sleep 3
    systemctl status tm-dashboard --no-pager
"

echo ""
echo "🔒 Step 6: SSL configuration..."
scp ssl_setup.sh $VPS_HOST:/tmp/
ssh $VPS_HOST "
    cd /tmp
    chmod +x ssl_setup.sh
    ./ssl_setup.sh
"

echo ""
echo "🧪 Step 7: Health check..."
scp health_check.sh $VPS_HOST:/tmp/
ssh $VPS_HOST "cd /tmp && ./health_check.sh $DOMAIN $TENANT"

echo ""
echo "✅ Fresh TM Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Access TM at: https://$DOMAIN/$TENANT/"
echo "🔧 SSH access: ssh $VPS_HOST"
echo "📊 Health check: ssh $VPS_HOST 'cd /tmp && ./health_check.sh'"
echo "📝 View logs: ssh $VPS_HOST 'journalctl -u tm-dashboard -f'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📸 Ready to create Linode snapshot: 'TM-Legal-SSL-Master'"
echo "🔄 Current production remains untouched"
