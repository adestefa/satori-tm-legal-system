#!/bin/bash

# Clone TM tenant for new client
# This script configures a cloned Linode VPS for a new tenant

set -e

NEW_TENANT="${1}"
NEW_DOMAIN="${2:-legal.satori-ai-tech.com}"
EMAIL="${3:-admin@satori-ai-tech.com}"

if [ -z "$NEW_TENANT" ]; then
    echo "Usage: $0 <tenant-name> [domain] [email]"
    echo "Example: $0 smith-law legal.satori-ai-tech.com admin@satori-ai-tech.com"
    exit 1
fi

echo "🔄 Cloning TM tenant configuration"
echo "New Tenant: $NEW_TENANT"
echo "Domain: $NEW_DOMAIN" 
echo "Email: $EMAIL"

# Stop TM service
echo "🛑 Stopping TM service..."
sudo systemctl stop tm-dashboard

# Update environment file
echo "⚙️ Updating tenant configuration..."
sudo sed -i "s/TENANT_NAME=.*/TENANT_NAME=$NEW_TENANT/" /opt/tm/.env
sudo sed -i "s/DOMAIN=.*/DOMAIN=$NEW_DOMAIN/" /opt/tm/.env
sudo sed -i "s|BASE_URL=.*|BASE_URL=https://$NEW_DOMAIN/$NEW_TENANT|" /opt/tm/.env

# Generate new session secret
SESSION_SECRET=$(openssl rand -hex 32)
sudo sed -i "s/SESSION_SECRET=.*/SESSION_SECRET=$SESSION_SECRET/" /opt/tm/.env

# Update nginx configuration
echo "🌐 Updating nginx configuration..."
sudo sed -i "s/server_name .*/server_name $NEW_DOMAIN;/" /etc/nginx/sites-available/tm-legal
sudo sed -i "s|location /.*/ {|location /$NEW_TENANT/ {|" /etc/nginx/sites-available/tm-legal
sudo sed -i "s|rewrite ^/.*/(.*)|rewrite ^/$NEW_TENANT/(.*)|" /etc/nginx/sites-available/tm-legal
sudo sed -i "s|return 301 https://\$server_name/.*/;|return 301 https://\$server_name/$NEW_TENANT/;|" /etc/nginx/sites-available/tm-legal

# Test nginx configuration
sudo nginx -t

# Remove old SSL certificates
echo "🔒 Setting up SSL for new tenant..."
sudo certbot delete --cert-name $NEW_DOMAIN || true

# Get new SSL certificate
sudo systemctl stop nginx
sudo certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $NEW_DOMAIN

# Start services
sudo systemctl start nginx
sudo systemctl start tm-dashboard

# Clear old case data (optional - comment out if you want to preserve)
echo "🧹 Clearing old case data..."
sudo rm -rf /opt/tm/test-data/sync-test-cases/*
sudo rm -rf /opt/tm/outputs/*
sudo mkdir -p /opt/tm/test-data/sync-test-cases
sudo chown -R tm:tm /opt/tm/test-data /opt/tm/outputs

# Reset firm settings
echo "⚙️ Resetting firm settings..."
sudo rm -f /opt/tm/dashboard/config/settings.json

echo ""
echo "✅ Tenant clone complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 New URL: https://$NEW_DOMAIN/$NEW_TENANT/"
echo "🔒 SSL Certificate: Let's Encrypt"
echo "⚙️ Service Status: $(sudo systemctl is-active tm-dashboard)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Required DNS Update:"
echo "Create A record: $NEW_DOMAIN → $(curl -s ifconfig.me)"
echo ""
echo "🔄 Service Management:"
echo "Status: sudo systemctl status tm-dashboard"
echo "Restart: sudo systemctl restart tm-dashboard"
echo "Logs: journalctl -u tm-dashboard -f"
