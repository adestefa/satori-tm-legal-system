#!/bin/bash

# TM Health Check Script
# Monitors TM platform health and reports status

set -e

DOMAIN="${1:-legal.satori-ai-tech.com}"
TENANT="${2:-mallon}"

echo "🔍 TM Platform Health Check"
echo "Domain: $DOMAIN"
echo "Tenant: $TENANT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
check_service() {
    local service=$1
    if sudo systemctl is-active --quiet $service; then
        echo -e "✅ ${GREEN}$service${NC} - Running"
        return 0
    else
        echo -e "❌ ${RED}$service${NC} - Stopped"
        return 1
    fi
}

check_port() {
    local port=$1
    local name=$2
    if netstat -ln | grep -q ":$port "; then
        echo -e "✅ ${GREEN}Port $port${NC} ($name) - Listening"
        return 0
    else
        echo -e "❌ ${RED}Port $port${NC} ($name) - Not listening"
        return 1
    fi
}

check_ssl() {
    local domain=$1
    local expiry=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ -n "$expiry" ]; then
        echo -e "✅ ${GREEN}SSL Certificate${NC} - Valid (expires: $expiry)"
        return 0
    else
        echo -e "❌ ${RED}SSL Certificate${NC} - Invalid or missing"
        return 1
    fi
}

check_endpoint() {
    local url=$1
    local name=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$url" || echo "000")
    if [ "$response" = "200" ]; then
        echo -e "✅ ${GREEN}$name${NC} - HTTP $response"
        return 0
    else
        echo -e "❌ ${RED}$name${NC} - HTTP $response"
        return 1
    fi
}

# Run health checks
echo "📋 System Services"
check_service "tm-dashboard"
check_service "nginx"
check_service "certbot.timer"

echo ""
echo "🌐 Network Services"
check_port "8000" "TM Dashboard"
check_port "80" "HTTP"
check_port "443" "HTTPS"

echo ""
echo "🔒 SSL Status"
check_ssl "$DOMAIN"

echo ""
echo "🔗 Endpoint Tests"
check_endpoint "https://$DOMAIN/health" "Health Check"
check_endpoint "https://$DOMAIN/$TENANT/" "TM Dashboard"

echo ""
echo "💾 System Resources"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"

echo ""
echo "📊 Service Status Details"
echo "TM Dashboard PID: $(pgrep -f 'python.*main.py' || echo 'Not running')"
echo "Nginx PID: $(pgrep nginx | head -1 || echo 'Not running')"

# Log recent errors
echo ""
echo "🔍 Recent Errors (last 10)"
journalctl -u tm-dashboard --since "1 hour ago" --no-pager -q | grep -i error | tail -10 || echo "No recent errors"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Health check complete. Access TM at: https://$DOMAIN/$TENANT/"
