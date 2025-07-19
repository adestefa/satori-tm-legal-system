#!/bin/bash

# SSH Key Setup for TM VPS - Secure Connection Setup
# Run this on your LOCAL machine first

set -e

VPS_IP="198.74.59.11"
VPS_USER="root"
SSH_KEY_NAME="tm-legal-vps"
SSH_DIR="$HOME/.ssh"

echo "🔐 Setting up secure SSH connection to TM VPS"
echo "VPS: $VPS_IP"
echo "User: $VPS_USER"

# Create SSH directory if it doesn't exist
mkdir -p $SSH_DIR
chmod 700 $SSH_DIR

# Generate new SSH key pair specifically for TM VPS
echo "🔑 Generating new SSH key pair..."
ssh-keygen -t ed25519 -f "$SSH_DIR/$SSH_KEY_NAME" -C "tm-legal-vps-$(date +%Y%m%d)" -N ""

echo "✅ SSH key pair generated:"
echo "Private key: $SSH_DIR/$SSH_KEY_NAME"
echo "Public key: $SSH_DIR/$SSH_KEY_NAME.pub"

# Display the public key for copying
echo ""
echo "📋 Public key to copy:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$SSH_DIR/$SSH_KEY_NAME.pub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create SSH config entry
echo ""
echo "🔧 Adding SSH config entry..."
cat >> "$SSH_DIR/config" << EOF

# TM Legal VPS - Secure Connection
Host tm-legal
    HostName $VPS_IP
    User $VPS_USER
    IdentityFile $SSH_DIR/$SSH_KEY_NAME
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking ask
    UserKnownHostsFile $SSH_DIR/known_hosts

EOF

chmod 600 "$SSH_DIR/config"

echo "✅ SSH config updated"
echo ""
echo "📋 MANUAL STEPS REQUIRED:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Connect to VPS with password ONE LAST TIME:"
echo "   ssh root@$VPS_IP"
echo "   (password: Croot2160key$)"
echo ""
echo "2. On the VPS, run these commands:"
echo "   mkdir -p ~/.ssh"
echo "   chmod 700 ~/.ssh"
echo "   nano ~/.ssh/authorized_keys"
echo ""
echo "3. Paste the public key above into authorized_keys and save"
echo ""
echo "4. Set proper permissions:"
echo "   chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "5. Test the key-based connection:"
echo "   exit"
echo "   ssh tm-legal"
echo ""
echo "6. Once key auth works, disable password auth:"
echo "   sudo nano /etc/ssh/sshd_config"
echo "   Set: PasswordAuthentication no"
echo "   sudo systemctl restart sshd"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "After setup, connect with: ssh tm-legal"
