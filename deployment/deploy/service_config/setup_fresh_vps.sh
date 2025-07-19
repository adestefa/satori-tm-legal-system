#!/bin/bash

# Fresh Linode TM Deployment Script
# Complete deployment from repo to production SSL

set -e

# UPDATE THESE VALUES FOR NEW LINODE
NEW_VPS_IP="NEW_IP_HERE"
NEW_VPS_PASSWORD="NEW_PASSWORD_HERE"
DOMAIN="legal.satori-ai-tech.com"
TENANT="mallon"

echo "🚀 Fresh TM Linode Deployment"
echo "New VPS IP: $NEW_VPS_IP"
echo "Domain: $DOMAIN"
echo "Tenant: $TENANT"

# Generate SSH keys for new VPS
echo "🔑 Generating SSH keys for new VPS..."
ssh-keygen -t ed25519 -f ~/.ssh/tm-fresh-vps -C "tm-fresh-vps-$(date +%Y%m%d)" -N ""

# Add new SSH config
echo "🔧 Adding SSH config for new VPS..."
cat >> ~/.ssh/config << EOF

# TM Fresh VPS - SSL Deployment
Host tm-fresh
    HostName $NEW_VPS_IP
    User root
    IdentityFile ~/.ssh/tm-fresh-vps
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking ask

EOF

chmod 600 ~/.ssh/config

echo ""
echo "📋 Manual Steps Required:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. UPDATE THIS SCRIPT with your new Linode details:"
echo "   NEW_VPS_IP=\"your-new-ip\""
echo "   NEW_VPS_PASSWORD=\"your-new-password\""
echo ""
echo "2. Install SSH key on new VPS:"
echo "   ssh root@$NEW_VPS_IP"
echo "   mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo "   nano ~/.ssh/authorized_keys"
echo "   # Paste this public key:"
echo ""
cat ~/.ssh/tm-fresh-vps.pub
echo ""
echo "   chmod 600 ~/.ssh/authorized_keys && exit"
echo ""
echo "3. Test key authentication:"
echo "   ssh tm-fresh"
echo ""
echo "4. Update DNS A record:"
echo "   $DOMAIN → $NEW_VPS_IP"
echo ""
echo "5. Run full deployment:"
echo "   ./deploy_fresh_complete.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
