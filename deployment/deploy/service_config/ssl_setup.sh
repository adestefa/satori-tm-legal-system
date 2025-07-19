#!/bin/bash

# TM SSL Setup Script for Linode VPS
# Sets up SSL for legal.satori-ai-tech.com/mallon/ tenant structure

set -e

DOMAIN="legal.satori-ai-tech.com"
TENANT="mallon"
EMAIL="admin@satori-ai-tech.com"

echo "🔧 Setting up SSL for TM Legal Document Processing Platform"
echo "Domain: $DOMAIN"
echo "Tenant: $TENANT"

# Update system
sudo apt update && sudo apt upgrade -y

# Install certbot (native, no Docker)
sudo apt install -y certbot nginx

# Create nginx configuration for TM
sudo tee /etc/nginx/sites-available/tm-legal > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL Configuration (certbot will populate these)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_private_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    # TM Dashboard proxy with tenant path
    location /$TENANT/ {
        # Remove tenant prefix and proxy to TM dashboard
        rewrite ^/$TENANT/(.*) /\$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for real-time updates
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    
    # Root redirect to tenant
    location = / {
        return 301 https://\$server_name/$TENANT/;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "TM Legal Platform Healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/tm-legal /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Stop nginx temporarily for certbot standalone
sudo systemctl stop nginx

# Get SSL certificate
sudo certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Setup auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test SSL renewal
sudo certbot renew --dry-run

echo "✅ SSL setup complete!"
echo "🌐 Access TM at: https://$DOMAIN/$TENANT/"
echo "🔄 Auto-renewal configured via systemd timer"

# Show renewal status
sudo systemctl status certbot.timer --no-pager
