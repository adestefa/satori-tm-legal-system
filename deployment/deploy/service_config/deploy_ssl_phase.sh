#!/bin/bash

# SSL Setup Phase for Fresh TM Deployment
# Configures SSL, nginx, and tests the complete system

set -e

VPS_HOST="legal-agent-vps"
DOMAIN="legal.satori-ai-tech.com"
TENANT="mallon"
EMAIL="admin@satori-ai-tech.com"

echo "🔒 TM SSL Setup Phase"
echo "VPS: $VPS_HOST"
echo "Domain: $DOMAIN"
echo "Tenant: $TENANT"

# Check if TM is running first
echo ""
echo "🔍 Checking TM service status..."
if ! ssh $VPS_HOST "systemctl is-active --quiet tm-dashboard"; then
    echo "❌ TM Dashboard service is not running. Run ./deploy_tm_phase1.sh first"
    echo "Debug with: ssh $VPS_HOST 'systemctl status tm-dashboard'"
    exit 1
fi

echo "✅ TM Dashboard service is running"

echo ""
echo "🌐 Step 1: DNS verification..."
CURRENT_IP=$(ssh $VPS_HOST "curl -s ifconfig.me")
echo "VPS IP: $CURRENT_IP"

# Check DNS resolution
RESOLVED_IP=$(dig +short $DOMAIN | head -1)
echo "DNS resolves to: $RESOLVED_IP"

if [ "$RESOLVED_IP" != "$CURRENT_IP" ]; then
    echo ""
    echo "⚠️ WARNING: DNS Configuration Issue"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "DNS currently points to: $RESOLVED_IP"
    echo "VPS IP address is: $CURRENT_IP"
    echo ""
    echo "Please update your DNS A record:"
    echo "$DOMAIN → $CURRENT_IP"
    echo ""
    echo "SSL certificate issuance will fail without proper DNS!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Update DNS first, then re-run this script."
        exit 1
    fi
else
    echo "✅ DNS correctly points to VPS"
fi

echo ""
echo "🔧 Step 2: Nginx configuration..."
ssh $VPS_HOST "
    echo '🔧 Installing nginx configuration...'
    cp /tmp/nginx-tm-legal.conf /etc/nginx/sites-available/tm-legal
    
    # Update config with correct domain and tenant
    sed -i 's/server_name legal.satori-ai-tech.com;/server_name $DOMAIN;/' /etc/nginx/sites-available/tm-legal
    sed -i 's|location /mallon/|location /$TENANT/|g' /etc/nginx/sites-available/tm-legal
    sed -i 's|rewrite ^/mallon/|rewrite ^/$TENANT/|' /etc/nginx/sites-available/tm-legal
    sed -i 's|return 301 https://\$server_name/mallon/;|return 301 https://\$server_name/$TENANT/;|' /etc/nginx/sites-available/tm-legal
    
    # Enable the site
    ln -sf /etc/nginx/sites-available/tm-legal /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    echo '✅ Nginx configuration valid'
"

echo ""
echo "🔒 Step 3: SSL certificate setup..."
ssh $VPS_HOST "
    echo '🔒 Stopping nginx for standalone certificate request...'
    systemctl stop nginx || true
    
    echo '🔒 Requesting SSL certificate from Let's Encrypt...'
    certbot certonly \
        --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --domains $DOMAIN \
        --non-interactive
    
    echo '🔒 Starting nginx with SSL configuration...'
    systemctl start nginx
    systemctl enable nginx
    
    echo '🔄 Setting up auto-renewal...'
    systemctl enable certbot.timer
    systemctl start certbot.timer
    
    echo '✅ SSL setup complete'
"

echo ""
echo "🧪 Step 4: System health check..."
# Upload and run health check
scp health_check.sh $VPS_HOST:/tmp/
ssh $VPS_HOST "
    cd /tmp
    chmod +x health_check.sh
    ./health_check.sh $DOMAIN $TENANT
"

echo ""
echo "🌐 Step 5: External connectivity tests..."
echo "Testing health endpoint..."
if curl -k -s "https://$DOMAIN/health" | grep -q "Healthy"; then
    echo "✅ Health endpoint responding"
else
    echo "❌ Health endpoint not responding"
fi

echo ""
echo "Testing TM dashboard..."
DASHBOARD_RESPONSE=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/$TENANT/" || echo "000")
if [ "$DASHBOARD_RESPONSE" = "200" ] || [ "$DASHBOARD_RESPONSE" = "302" ]; then
    echo "✅ TM Dashboard responding (HTTP $DASHBOARD_RESPONSE)"
else
    echo "❌ TM Dashboard not responding (HTTP $DASHBOARD_RESPONSE)"
fi

echo ""
echo "🔒 Step 6: SSL certificate verification..."
ssh $VPS_HOST "
    echo '📋 SSL Certificate Details:'
    certbot certificates | grep -A 5 '$DOMAIN' || echo 'Certificate not found'
    
    echo ''
    echo '📅 Certificate expiry:'
    echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null || echo 'Could not check expiry'
"

echo ""
echo "✅ TM SSL Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 TM Dashboard: https://$DOMAIN/$TENANT/"
echo "🔒 SSL Certificate: Let's Encrypt (auto-renewing)"
echo "🔧 SSH Access: ssh $VPS_HOST"
echo "📊 Health Check: ssh $VPS_HOST 'cd /tmp && ./health_check.sh'"
echo "📝 View Logs: ssh $VPS_HOST 'journalctl -u tm-dashboard -f'"
echo "🔄 Service Control: ssh $VPS_HOST 'systemctl restart tm-dashboard'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📸 Ready to create Linode snapshot: 'TM-Legal-SSL-Master-v1.9'"
echo "🎯 This will be the template for all client deployments"
echo ""
echo "📋 Final verification steps:"
echo "1. Open https://$DOMAIN/$TENANT/ in browser"
echo "2. Upload a test case file"
echo "3. Process a case end-to-end"
echo "4. Verify document generation works"
echo "5. Create Linode snapshot when satisfied"
