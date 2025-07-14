#!/bin/bash

# Deploy TM system to production server
# Usage: ./scripts/deploy_to_server.sh

SERVER="198.74.59.11"
USER="root"
TM_PATH="/home/tm/TM"

echo "🚀 Deploying TM system to production server..."

# SSH into server and run deployment commands
ssh -o StrictHostKeyChecking=no ${USER}@${SERVER} << 'EOF'
    echo "📁 Navigating to TM directory..."
    cd /home/tm/TM

    echo "📥 Pulling latest changes from GitHub..."
    sudo -u tm git pull origin main

    echo "🔄 Restarting dashboard service..."
    cd /home/tm/TM/dashboard
    sudo -u tm ./restart.sh

    echo "✅ Deployment complete!"
    echo "🌐 Server available at: http://198.74.59.11"
    echo "🔍 Test URL: http://198.74.59.11/review?case_id=youssef"
EOF

echo "🎉 Deployment script finished!"
echo ""
echo "Next steps:"
echo "1. Open browser to: http://198.74.59.11/review?case_id=youssef"
echo "2. Open developer console (F12)"
echo "3. Look for debug messages starting with 🔍"