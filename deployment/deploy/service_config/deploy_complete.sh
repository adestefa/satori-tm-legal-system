#!/bin/bash

# Complete TM VPS Deployment Script
# Run this from your local Mac to deploy everything

set -e

echo "🚀 TM VPS Complete Deployment"
echo "This script will upload files and run the deployment on your VPS"

VPS_HOST="tm-legal"
CONFIG_DIR="/Users/corelogic/satori-dev/TM/deployment/deploy/service_config"

# Check if we're in the right directory
if [ ! -f "vps_upgrade_phase1.sh" ]; then
    echo "❌ Please run this from: $CONFIG_DIR"
    exit 1
fi

echo ""
echo "📤 Step 1: Uploading deployment files to VPS..."
scp *.sh *.env *.service *.conf $VPS_HOST:/tmp/

echo ""
echo "✅ Files uploaded. Verifying..."
ssh $VPS_HOST "ls -la /tmp/*.sh /tmp/*.env /tmp/*.service /tmp/*.conf"

echo ""
echo "🔧 Step 2: Running VPS migration and setup..."
ssh $VPS_HOST "cd /tmp && chmod +x *.sh && sudo ./vps_upgrade_phase1.sh"

echo ""
echo "🧪 Step 3: Testing TM service..."
ssh $VPS_HOST "sudo systemctl start tm-dashboard"
sleep 3
ssh $VPS_HOST "sudo systemctl status tm-dashboard --no-pager"

echo ""
echo "🌐 Step 4: Testing local TM access..."
ssh $VPS_HOST "curl -s http://127.0.0.1:8000 || echo 'TM not responding yet'"

echo ""
echo "✅ Phase 1 Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 NEXT STEPS FOR SSL:"
echo "1. Verify DNS: legal.satori-ai-tech.com → 198.74.59.11"
echo "2. Run SSL setup: ssh tm-legal 'cd /tmp && sudo ./ssl_setup.sh'"
echo "3. Test SSL: ssh tm-legal './health_check.sh legal.satori-ai-tech.com mallon'"
echo ""
echo "Or run the SSL setup automatically:"
echo "./deploy_ssl.sh"
