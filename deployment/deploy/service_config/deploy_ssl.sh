#!/bin/bash

# SSL Deployment Script
# Run this after deploy_complete.sh succeeds

set -e

VPS_HOST="tm-legal"
DOMAIN="legal.satori-ai-tech.com"

echo "🔒 TM VPS SSL Deployment"
echo "Domain: $DOMAIN"
echo "VPS: $VPS_HOST"

echo ""
echo "🌐 Step 1: Checking DNS resolution..."
RESOLVED_IP=$(dig +short $DOMAIN)
VPS_IP=$(ssh $VPS_HOST "curl -s ifconfig.me")

echo "DNS points to: $RESOLVED_IP"
echo "VPS IP is: $VPS_IP"

if [ "$RESOLVED_IP" != "$VPS_IP" ]; then
    echo "⚠️ WARNING: DNS may not be pointing to your VPS yet"
    echo "Update your DNS A record: $DOMAIN → $VPS_IP"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Update DNS first."
        exit 1
    fi
fi

echo ""
echo "🔒 Step 2: Running SSL setup..."
ssh $VPS_HOST "cd /tmp && sudo ./ssl_setup.sh"

echo ""
echo "🧪 Step 3: Running health check..."
ssh $VPS_HOST "cd /tmp && ./health_check.sh $DOMAIN mallon"

echo ""
echo "🌐 Step 4: Testing SSL endpoints..."
echo "Testing health endpoint..."
curl -k "https://$DOMAIN/health" || echo "Health endpoint not responding"

echo ""
echo "Testing TM dashboard..."
curl -k "https://$DOMAIN/mallon/" || echo "TM dashboard not responding"

echo ""
echo "✅ SSL Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Access TM at: https://$DOMAIN/mallon/"
echo "🔧 Service management: ssh $VPS_HOST 'sudo systemctl status tm-dashboard'"
echo "📊 Health check: ssh $VPS_HOST './health_check.sh'"
echo "📝 View logs: ssh $VPS_HOST 'journalctl -u tm-dashboard -f'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📸 Ready to create Linode snapshot for cloning!"
