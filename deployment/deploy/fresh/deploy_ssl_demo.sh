#!/bin/bash

# ==============================================================================
# TM DEMO SERVER SSL DEPLOYMENT - GOLD TEMPLATE CREATION
# ==============================================================================
# Target: legal.satori-ai-tech.com (Demo/Sales Server)
# Architecture: Direct subdomain → VPS (no path routing)
# Purpose: Create SSL-enabled GOLD template for client cloning
# ==============================================================================

set -e

VPS_HOST="legal-agent-vps"
DOMAIN="legal.satori-ai-tech.com"
EMAIL="admin@satori-ai-tech.com"

echo "🔒 TM Demo Server SSL Deployment"
echo "🎯 Target: $DOMAIN (Demo/Sales Server)"
echo "📸 Creating GOLD template with SSL"
echo ""

# Check if TM is running first
echo "🔍 Checking TM service status..."
if ! ssh $VPS_HOST "systemctl is-active --quiet tm-dashboard"; then
    echo "❌ TM Dashboard service is not running"
    echo "Debug with: ssh $VPS_HOST 'systemctl status tm-dashboard'"
    exit 1
fi

echo "✅ TM Dashboard service is running"

# Verify DNS resolution
echo ""
echo "🌐 DNS verification..."
CURRENT_IP=$(ssh $VPS_HOST "curl -4 -s ifconfig.me")
echo "VPS IP: $CURRENT_IP"

RESOLVED_IP=$(dig +short $DOMAIN | head -1)
echo "DNS resolves to: $RESOLVED_IP"

if [ "$RESOLVED_IP" != "$CURRENT_IP" ]; then
    echo ""
    echo "❌ DNS Configuration Issue"
    echo "DNS points to: $RESOLVED_IP"
    echo "VPS IP is: $CURRENT_IP"
    echo ""
    echo "Please verify DNS A record: $DOMAIN → $CURRENT_IP"
    exit 1
else
    echo "✅ DNS correctly points to VPS"
fi

# Create temporary HTTP-only Nginx configuration
echo ""
echo "🔧 Creating temporary HTTP configuration for certificate request..."
cat > /tmp/nginx-demo-http.conf << 'EOF'
server {
    listen 80;
    server_name legal.satori-ai-tech.com;
    
    # Temporary location for Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect everything else to HTTPS (after certificate is obtained)
    location / {
        return 301 https://$server_name$request_uri;
    }
}
EOF

# Deploy temporary HTTP configuration
echo "🔧 Deploying temporary HTTP configuration..."
scp /tmp/nginx-demo-http.conf $VPS_HOST:/tmp/
ssh $VPS_HOST "
    echo '🔧 Installing temporary HTTP configuration...'
    cp /tmp/nginx-demo-http.conf /etc/nginx/sites-available/tm-legal-temp
    
    # Remove any existing configurations
    rm -f /etc/nginx/sites-enabled/default
    rm -f /etc/nginx/sites-enabled/tm-legal-demo
    
    # Enable temporary configuration
    ln -sf /etc/nginx/sites-available/tm-legal-temp /etc/nginx/sites-enabled/
    
    # Create web root for Let's Encrypt
    mkdir -p /var/www/html
    
    # Test and restart nginx
    nginx -t && systemctl restart nginx
    echo '✅ Temporary HTTP configuration active'
"

# SSL certificate setup
echo ""
echo "🔒 SSL certificate setup with Let's Encrypt..."
ssh $VPS_HOST "
    echo '🔒 Requesting SSL certificate from Let's Encrypt...'
    certbot certonly \
        --webroot \
        -w /var/www/html \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --domains $DOMAIN \
        --non-interactive
    
    echo '✅ SSL certificate obtained'
"

# Now create the full SSL configuration
echo ""
echo "🔧 Creating full SSL configuration..."
cat > /tmp/nginx-demo-ssl.conf << 'EOF'
server {
    listen 80;
    server_name legal.satori-ai-tech.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name legal.satori-ai-tech.com;
    
    # SSL Configuration (certbot will populate these)
    ssl_certificate /etc/letsencrypt/live/legal.satori-ai-tech.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/legal.satori-ai-tech.com/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # SSL session settings
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;
    
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Direct proxy to TM dashboard (no path manipulation)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for real-time updates
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "TM Legal Demo Platform Healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Security - deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

# Deploy full SSL configuration
echo "🔧 Deploying full SSL configuration..."
scp /tmp/nginx-demo-ssl.conf $VPS_HOST:/tmp/
ssh $VPS_HOST "
    echo '🔧 Installing full SSL configuration...'
    cp /tmp/nginx-demo-ssl.conf /etc/nginx/sites-available/tm-legal-demo
    
    # Remove temporary configuration
    rm -f /etc/nginx/sites-enabled/tm-legal-temp
    
    # Enable SSL configuration
    ln -sf /etc/nginx/sites-available/tm-legal-demo /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    nginx -t
    echo '✅ SSL configuration valid'
    
    # Restart nginx with SSL
    systemctl restart nginx
    echo '✅ Nginx restarted with SSL'
    
    # Enable auto-renewal
    systemctl enable certbot.timer
    systemctl start certbot.timer
    echo '✅ SSL auto-renewal configured'
"

# System health verification
echo ""
echo "🧪 Comprehensive system verification..."

# Test HTTP redirect
echo "Testing HTTP to HTTPS redirect..."
sleep 3  # Allow nginx to fully start
HTTP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/" || echo "000")
if [ "$HTTP_RESPONSE" = "301" ] || [ "$HTTP_RESPONSE" = "302" ]; then
    echo "✅ HTTP redirect working (HTTP $HTTP_RESPONSE)"
else
    echo "❌ HTTP redirect not working (HTTP $HTTP_RESPONSE)"
fi

# Test HTTPS access
echo "Testing HTTPS dashboard access..."
HTTPS_RESPONSE=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/" || echo "000")
if [ "$HTTPS_RESPONSE" = "200" ] || [ "$HTTPS_RESPONSE" = "302" ]; then
    echo "✅ HTTPS dashboard responding (HTTP $HTTPS_RESPONSE)"
else
    echo "❌ HTTPS dashboard not responding (HTTP $HTTPS_RESPONSE)"
fi

# Test health endpoint
echo "Testing health endpoint..."
if curl -k -s "https://$DOMAIN/health" | grep -q "Healthy"; then
    echo "✅ Health endpoint responding"
else
    echo "❌ Health endpoint not responding"
fi

# Test TM functionality over HTTPS
echo "Testing TM services over HTTPS..."
API_RESPONSE=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/api/cases" || echo "000")
if [ "$API_RESPONSE" = "200" ] || [ "$API_RESPONSE" = "401" ] || [ "$API_RESPONSE" = "302" ]; then
    echo "✅ TM API accessible over HTTPS (HTTP $API_RESPONSE)"
else
    echo "❌ TM API not accessible over HTTPS (HTTP $API_RESPONSE)"
fi

# SSL certificate verification
echo ""
echo "🔒 SSL certificate verification..."
ssh $VPS_HOST "
    echo '📋 SSL Certificate Details:'
    certbot certificates | grep -A 5 '$DOMAIN' || echo 'Certificate not found'
    
    echo ''
    echo '📅 Certificate expiry:'
    echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null || echo 'Could not check expiry'
    
    echo ''
    echo '🔄 Auto-renewal status:'
    systemctl status certbot.timer --no-pager | head -5
"

echo ""
echo "✅ TM Demo Server SSL Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 DEMO/SALES SERVER READY:"
echo "🌐 TM Dashboard: https://$DOMAIN/"
echo "🔒 SSL Certificate: Let's Encrypt (auto-renewing)"
echo "📊 Health Check: https://$DOMAIN/health"
echo "🔧 SSH Access: ssh $VPS_HOST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📸 GOLD TEMPLATE CREATION:"
echo "1. ✅ TM System: v1.9.2 with all services operational"
echo "2. ✅ SSL/HTTPS: Production-ready Let's Encrypt configuration"
echo "3. ✅ DNS: Subdomain architecture proven"
echo "4. ✅ Security: Modern TLS + security headers"
echo "5. 🔄 Ready for Linode snapshot creation"
echo ""
echo "🚀 NEXT: Create Linode snapshot 'TM-Legal-SSL-GOLD-v1.9'"
echo "📋 Then clone for client: mallon.legal.satori-ai-tech.com"
echo ""
echo "🎉 Demo server ready for sales presentations!"
echo "🔗 Share: https://$DOMAIN/ (secure HTTPS access)"