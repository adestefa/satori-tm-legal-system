#!/bin/bash

# Fix SSH configuration for TM VPS

SSH_DIR="$HOME/.ssh"
VPS_IP="198.74.59.11"
SSH_KEY_NAME="tm-legal-vps"

echo "🔧 Fixing SSH configuration..."

# Fix key permissions
echo "Setting correct permissions on SSH keys..."
chmod 600 "$SSH_DIR/$SSH_KEY_NAME"
chmod 600 "$SSH_DIR/$SSH_KEY_NAME.pub"
echo "✅ SSH key permissions fixed"

# Check if SSH config exists
if [ ! -f "$SSH_DIR/config" ]; then
    echo "Creating SSH config file..."
    touch "$SSH_DIR/config"
    chmod 600 "$SSH_DIR/config"
fi

# Check if tm-legal entry exists
if ! grep -q "Host tm-legal" "$SSH_DIR/config"; then
    echo "Adding tm-legal host entry to SSH config..."
    cat >> "$SSH_DIR/config" << EOF

# TM Legal VPS - Secure Connection
Host tm-legal
    HostName $VPS_IP
    User root
    IdentityFile $SSH_DIR/$SSH_KEY_NAME
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking ask
    UserKnownHostsFile $SSH_DIR/known_hosts

EOF
    echo "✅ SSH config entry added"
else
    echo "✅ SSH config entry already exists"
fi

# Set config permissions
chmod 600 "$SSH_DIR/config"

echo ""
echo "📋 SSH Configuration Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Private key: $SSH_DIR/$SSH_KEY_NAME"
echo "Public key:  $SSH_DIR/$SSH_KEY_NAME.pub"
echo "SSH config:  $SSH_DIR/config"
echo ""
echo "Key permissions:"
ls -la "$SSH_DIR/$SSH_KEY_NAME"*
echo ""
echo "SSH config entry:"
grep -A 10 "Host tm-legal" "$SSH_DIR/config"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔄 Now try connecting:"
echo "ssh tm-legal"
echo ""
echo "If it still asks for password, the public key hasn't been installed on the VPS yet."
echo "Make sure you completed step 2 (installing public key on VPS)."
