#!/bin/bash

# Create SSH alias for new TM VPS
# Run this on your LOCAL machine

set -e

# UPDATE THESE VALUES WITH YOUR NEW LINODE DETAILS
NEW_VPS_IP="YOUR_NEW_IP_HERE"
SSH_ALIAS="legal-agent"
SSH_USER="root"

echo "🔧 Creating SSH alias for new TM VPS"
echo "Alias: $SSH_ALIAS"
echo "IP: $NEW_VPS_IP"
echo "User: $SSH_USER"

# Check if we need to update the IP
if [ "$NEW_VPS_IP" = "YOUR_NEW_IP_HERE" ]; then
    echo ""
    echo "❌ Please update this script with your new VPS IP address:"
    echo "Edit the line: NEW_VPS_IP=\"YOUR_NEW_IP_HERE\""
    echo "Replace with: NEW_VPS_IP=\"your-actual-ip\""
    exit 1
fi

# Add SSH config entry
echo ""
echo "🔧 Adding SSH config entry..."
cat >> ~/.ssh/config << EOF

# TM Legal Agent VPS - Fresh SSL Deployment
Host $SSH_ALIAS
    HostName $NEW_VPS_IP
    User $SSH_USER
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking ask
    UserKnownHostsFile ~/.ssh/known_hosts

EOF

chmod 600 ~/.ssh/config

echo "✅ SSH config updated"
echo ""
echo "🧪 Testing connection..."
if ssh -o ConnectTimeout=10 $SSH_ALIAS "echo 'SSH connection successful'"; then
    echo "✅ SSH connection working!"
else
    echo "❌ SSH connection failed. Check:"
    echo "  - VPS IP address is correct"
    echo "  - VPS is fully booted"
    echo "  - SSH key was properly added during setup"
fi

echo ""
echo "📋 SSH Configuration Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Alias: $SSH_ALIAS"
echo "IP: $NEW_VPS_IP"
echo "Connection: ssh $SSH_ALIAS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Ready for TM deployment!"
echo "Next step: ./deploy_fresh_tm.sh"
