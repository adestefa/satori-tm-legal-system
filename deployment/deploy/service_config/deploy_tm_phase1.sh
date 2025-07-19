#!/bin/bash

# Fresh TM Deployment to legal-agent-vps
# Complete deployment from repo to production SSL

set -e

VPS_HOST="legal-agent-vps"
DOMAIN="legal.satori-ai-tech.com"
TENANT="mallon"
EMAIL="admin@satori-ai-tech.com"

echo "🚀 Fresh TM Deployment Starting"
echo "VPS: $VPS_HOST"
echo "Domain: $DOMAIN"
echo "Tenant: $TENANT"

# Test SSH connection first
echo ""
echo "🔍 Testing SSH connection..."
if ! ssh $VPS_HOST "echo 'SSH connection successful - $(date)'"; then
    echo "❌ SSH connection failed. Check your SSH config for $VPS_HOST"
    exit 1
fi

echo ""
echo "📦 Step 1: System setup and dependencies..."
ssh $VPS_HOST "
    echo '📦 Updating system packages...'
    apt update && apt upgrade -y
    
    echo '📦 Installing dependencies...'
    apt install -y git python3 python3-pip python3-venv nodejs npm nginx certbot curl wget htop tree
    
    echo '👥 Creating TM user and directories...'
    groupadd -f tm
    useradd -r -g tm -d /opt/tm -s /bin/bash tm 2>/dev/null || true
    mkdir -p /opt/tm
    chown tm:tm /opt/tm
    
    echo '✅ System setup complete'
"

echo ""
echo "📁 Step 2: Uploading TM source code..."
# We'll upload the TM directory from your local machine
echo "Uploading TM source files..."

# Upload the entire TM directory (this will take a moment)
cd /Users/corelogic/satori-dev
tar -czf TM.tar.gz TM/ --exclude='TM/node_modules' --exclude='TM/.git' --exclude='TM/*/venv' --exclude='TM/*/__pycache__'
scp TM.tar.gz $VPS_HOST:/tmp/

ssh $VPS_HOST "
    echo '📁 Extracting TM source...'
    cd /opt
    tar -xzf /tmp/TM.tar.gz
    mv TM/* tm/ 2>/dev/null || true
    rmdir TM 2>/dev/null || true
    chown -R tm:tm /opt/tm
    rm /tmp/TM.tar.gz
    
    echo '📁 Creating additional directories...'
    mkdir -p /opt/tm/{logs,config,uploads}
    mkdir -p /opt/tm/test-data/sync-test-cases
    mkdir -p /opt/tm/outputs/{tests,tiger,monkey,browser}
    chown -R tm:tm /opt/tm
    
    echo '✅ TM source uploaded and organized'
"

echo ""
echo "🔧 Step 3: Installing TM services..."
ssh $VPS_HOST "
    echo '🐍 Setting up Python virtual environments...'
    cd /opt/tm
    
    # Tiger service
    if [ -d 'tiger' ]; then
        echo 'Installing Tiger service...'
        cd tiger
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn python-multipart aiofiles
        cd ..
    fi
    
    # Monkey service
    if [ -d 'monkey' ]; then
        echo 'Installing Monkey service...'
        cd monkey
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn jinja2 pydantic
        cd ..
    fi
    
    # Dashboard service
    if [ -d 'dashboard' ]; then
        echo 'Installing Dashboard service...'
        cd dashboard
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn websockets python-multipart aiofiles
        
        # Install npm dependencies if package.json exists
        if [ -f 'package.json' ]; then
            npm install
        fi
        cd ..
    fi
    
    chown -R tm:tm /opt/tm
    echo '✅ TM services installed'
"

echo ""
echo "⚙️ Step 4: Configuration setup..."
# Upload our config files
scp tm.env tm-dashboard.service nginx-tm-legal.conf $VPS_HOST:/tmp/

ssh $VPS_HOST "
    echo '⚙️ Setting up environment configuration...'
    cp /tmp/tm.env /opt/tm/.env
    
    # Generate secure session secret
    SESSION_SECRET=\$(openssl rand -hex 32)
    sed -i \"s/your-secure-session-secret-here/\$SESSION_SECRET/\" /opt/tm/.env
    
    # Update tenant and domain settings
    sed -i 's/TENANT_NAME=mallon/TENANT_NAME=$TENANT/' /opt/tm/.env
    sed -i 's/DOMAIN=legal.satori-ai-tech.com/DOMAIN=$DOMAIN/' /opt/tm/.env
    
    chown tm:tm /opt/tm/.env
    chmod 600 /opt/tm/.env
    
    echo '🔧 Setting up systemd service...'
    cp /tmp/tm-dashboard.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable tm-dashboard
    
    echo '✅ Configuration complete'
"

echo ""
echo "🚀 Step 5: Testing TM service..."
ssh $VPS_HOST "
    echo '🚀 Starting TM dashboard service...'
    systemctl start tm-dashboard
    sleep 5
    
    echo '📊 Service status:'
    systemctl status tm-dashboard --no-pager || true
    
    echo '🌐 Testing local access...'
    curl -s http://127.0.0.1:8000 >/dev/null && echo '✅ TM responding on port 8000' || echo '❌ TM not responding'
    
    echo '📝 Recent logs:'
    journalctl -u tm-dashboard --no-pager -n 10 || true
"

# Clean up local tar file
rm -f /Users/corelogic/satori-dev/TM.tar.gz

echo ""
echo "✅ Phase 1 Complete - TM Installation and Basic Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 TM Location: /opt/tm/"
echo "👥 TM User: tm:tm"
echo "⚙️ Environment: /opt/tm/.env"
echo "🔧 Service: systemctl status tm-dashboard"
echo "🌐 Local access: curl http://127.0.0.1:8000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 Next: SSL setup with ./deploy_ssl_phase.sh"
echo ""
echo "🔍 To debug any issues:"
echo "  ssh $VPS_HOST 'journalctl -u tm-dashboard -f'"
echo "  ssh $VPS_HOST 'systemctl status tm-dashboard'"
