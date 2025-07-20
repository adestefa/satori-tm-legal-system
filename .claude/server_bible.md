# TM Legal Document Processing - Server Management Bible

**Author**: Claude (Dr. Spock)  
**Date**: July 20, 2025  
**Version**: v1.9.2 Production  
**Architecture**: Subdomain-based client isolation  

## 🎯 System Overview

**Tiger-Monkey (TM)** is a production-ready, enterprise-grade legal document processing platform designed specifically for FCRA (Fair Credit Reporting Act) cases. The system transforms raw legal documents into court-ready legal filings through a sophisticated four-service architecture with complete client isolation via dedicated VPS instances.

### Architecture Pattern
- **Demo/Sales Server**: `legal.satori-ai-tech.com` → Single VPS for demonstrations
- **Client Production**: `<client>.legal.satori-ai-tech.com` → Dedicated VPS per client
- **Cost Model**: $5/month per client (Linode Nanode 1GB)
- **Data Isolation**: Complete separation via individual VPS instances

## 🏗️ Four-Service Architecture

### 1. Tiger Service - ML Document Analysis Engine
**Location**: `/opt/tm/tiger/`  
**Purpose**: Advanced OCR and legal entity extraction  
**Technology**: Docling ML models, Python 3.8+  
**Port**: Internal service (no direct access)  

**Key Capabilities**:
- Advanced OCR with Docling ML models
- Legal entity extraction (courts, parties, damages)
- Multi-format support (PDF, DOCX, TXT)
- Quality scoring (0-100 scale)
- Enhanced defendant extraction from unstructured text

**Management Commands**:
```bash
# Service status and info
cd /opt/tm/tiger && ./run.sh info

# Process case documents
./run.sh hydrated-json ../test-data/sync-test-cases/Rodriguez/ -o ../outputs/

# Health check
./health_check.sh

# View logs
tail -f data/logs/satori_tiger.log
```

### 2. Monkey Service - Document Generation Engine
**Location**: `/opt/tm/monkey/`  
**Purpose**: Template-driven legal document generation  
**Technology**: Jinja2 templates, Python 3.8+  
**Port**: Internal service (no direct access)  

**Key Capabilities**:
- Court-ready document generation
- Summons generation with creditor addresses
- Template management and validation
- PDF integration via Browser service

**Management Commands**:
```bash
# Generate complaint documents
cd /opt/tm/monkey && ./run.sh build-complaint ../outputs/hydrated_*.json --all

# Generate summons for all defendants
./run.sh generate-summons ../outputs/hydrated_*.json -o ../outputs/summons/

# Generate with PDF
./run.sh build-complaint ../outputs/hydrated_*.json --with-pdf

# Service info
./run.sh info
```

### 3. Dashboard Service - Web Interface & API
**Location**: `/opt/tm/dashboard/`  
**Purpose**: Professional web interface and API endpoints  
**Technology**: FastAPI + WebSocket, Node.js frontend  
**Port**: 8000 (proxied via Nginx on 443/80)  

**Key Capabilities**:
- 52 RESTful API endpoints
- Real-time WebSocket communication
- Multi-theme interface (light, dark, lexigen)
- Session-based authentication
- File monitoring and processing orchestration

**Management Commands**:
```bash
# Service control
sudo systemctl status tm-dashboard
sudo systemctl restart tm-dashboard
sudo systemctl stop tm-dashboard
sudo systemctl start tm-dashboard

# View logs
journalctl -u tm-dashboard -f
tail -f /opt/tm/dashboard/start_server.log

# Direct startup (for debugging)
cd /opt/tm/dashboard && ./start.sh
```

### 4. Browser Service - PDF Generation Engine
**Location**: `/opt/tm/browser/`  
**Purpose**: Headless Chrome PDF generation  
**Technology**: Puppeteer + Chromium, Node.js  
**Port**: Internal service (called via API)  

**Key Capabilities**:
- Pixel-perfect HTML to PDF conversion
- Court-ready formatting (A4, 1-inch margins)
- Integration with Monkey service
- Batch processing support

**Management Commands**:
```bash
# Generate single PDF
cd /opt/tm/browser && node pdf-generator.js complaint.html

# Python wrapper integration
python3 print.py single complaint.html output.pdf

# Performance testing
./benchmark.sh

# Integration testing
./run-tests.sh full
```

## 🔒 SSL & Security Management

### Let's Encrypt SSL Certificates

**Certificate Locations**:
- **Certificate**: `/etc/letsencrypt/live/legal.satori-ai-tech.com/fullchain.pem`
- **Private Key**: `/etc/letsencrypt/live/legal.satori-ai-tech.com/privkey.pem`
- **Logs**: `/var/log/letsencrypt/letsencrypt.log`

**Certificate Management**:
```bash
# View all certificates
sudo certbot certificates

# Manual renewal (auto-renewal is configured)
sudo certbot renew

# Test renewal process
sudo certbot renew --dry-run

# Check auto-renewal status
sudo systemctl status certbot.timer

# View certificate expiry
echo | openssl s_client -servername legal.satori-ai-tech.com -connect legal.satori-ai-tech.com:443 2>/dev/null | openssl x509 -noout -enddate
```

### Nginx Configuration

**Configuration Files**:
- **Main Config**: `/etc/nginx/nginx.conf`
- **TM Site**: `/etc/nginx/sites-available/tm-legal-demo`
- **Enabled Sites**: `/etc/nginx/sites-enabled/`

**Nginx Management**:
```bash
# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Reload configuration (no downtime)
sudo systemctl reload nginx

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check nginx status
sudo systemctl status nginx
```

**Security Headers Applied**:
- Strict-Transport-Security (HSTS)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Referrer-Policy

## 🌐 DNS Management

### Current DNS Configuration
**Domain**: `satori-ai-tech.com` (managed via Linode DNS)  

**A Records**:
```
legal.satori-ai-tech.com → 66.228.34.12 (Demo/Sales Server)
mallon.legal.satori-ai-tech.com → 66.228.34.13 (Future: Mallon Client)
<client>.legal.satori-ai-tech.com → <client_vps_ip> (Per-client pattern)
```

**DNS Verification**:
```bash
# Check DNS resolution
nslookup legal.satori-ai-tech.com
dig +short legal.satori-ai-tech.com

# Check from VPS
ssh root@legal-agent-vps "curl -4 -s ifconfig.me"  # Should match DNS
```

### Adding New Client DNS
1. **Login to Linode DNS Manager**
2. **Navigate to**: `satori-ai-tech.com` domain
3. **Add A Record**:
   - Hostname: `<client>.legal`
   - IP Address: `<new_vps_ip>`
   - TTL: Default (300 seconds)
4. **Save and wait for propagation** (5-30 minutes)

## 🖥️ VPS Management

### System Specifications
**Current Demo Server** (`legal-agent-vps`):
- **Provider**: Linode Nanode 1GB
- **Cost**: $5/month
- **IP**: 66.228.34.12
- **OS**: Ubuntu 24.04 LTS
- **CPU**: 1 vCPU
- **RAM**: 1GB
- **Storage**: 25GB SSD
- **Network**: 1TB transfer

### SSH Access
```bash
# Primary access method
ssh root@legal-agent-vps

# Alternative using IP
ssh root@66.228.34.12

# SSH config location (if using aliases)
~/.ssh/config
```

### System Health Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check TM service status
sudo systemctl status tm-dashboard

# Check all running processes
ps aux | grep -E "(uvicorn|nginx|certbot)"

# Check listening ports
sudo netstat -tlnp | grep -E "(80|443|8000)"

# Check disk usage
du -sh /opt/tm/*
```

### Log Locations
```bash
# TM Dashboard logs
/opt/tm/dashboard/start_server.log
journalctl -u tm-dashboard -f

# Tiger service logs
/opt/tm/tiger/data/logs/satori_tiger.log

# Nginx logs
/var/log/nginx/access.log
/var/log/nginx/error.log

# SSL certificate logs
/var/log/letsencrypt/letsencrypt.log

# System logs
/var/log/syslog
journalctl -f
```

## 🔧 Maintenance Procedures

### Daily Operations
```bash
# Check system health
ssh root@legal-agent-vps "
    systemctl status tm-dashboard --no-pager
    df -h
    free -h
    curl -s https://legal.satori-ai-tech.com/health
"
```

### Weekly Maintenance
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Check SSL certificate expiry (auto-renewal should handle)
sudo certbot certificates

# Review logs for errors
sudo journalctl --since "1 week ago" | grep -i error

# Check disk usage
du -sh /opt/tm/*
```

### Monthly Maintenance
```bash
# Test SSL renewal
sudo certbot renew --dry-run

# Backup TM system
tar -czf /root/tm-backup-$(date +%Y%m%d).tar.gz /opt/tm/

# Review security updates
sudo unattended-upgrades --dry-run

# Performance review
htop  # Check for resource usage patterns
```

### Emergency Procedures

**Dashboard Service Down**:
```bash
# Check status
sudo systemctl status tm-dashboard

# View recent logs
journalctl -u tm-dashboard --since "10 minutes ago"

# Restart service
sudo systemctl restart tm-dashboard

# If persistent issues, check port conflicts
sudo netstat -tlnp | grep 8000
```

**SSL Certificate Issues**:
```bash
# Check certificate status
sudo certbot certificates

# Manual renewal
sudo certbot renew --force-renewal

# If nginx fails to start
sudo nginx -t  # Check configuration
sudo systemctl restart nginx
```

**High Resource Usage**:
```bash
# Check processes
htop

# Check disk space
df -h

# Clean up old logs if needed
sudo journalctl --rotate
sudo journalctl --vacuum-time=30d

# Clean up old TM outputs
find /opt/tm/outputs -name "*.json" -mtime +30 -delete
```

## 🚀 Performance Optimization

### System Tuning
```bash
# Check current limits
ulimit -a

# Optimize for file processing
echo "fs.file-max = 65536" >> /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

### TM Service Optimization
```bash
# Tiger service: Process multiple documents in parallel
cd /opt/tm/tiger && ./run.sh hydrated-json cases/ -o outputs/ --parallel

# Dashboard: Monitor memory usage
journalctl -u tm-dashboard | grep -i memory

# Browser: PDF generation optimization
cd /opt/tm/browser && ./benchmark.sh
```

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

**Issue**: Dashboard not accessible via HTTPS
```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check SSL certificate
sudo certbot certificates

# Check if port 8000 is running
sudo netstat -tlnp | grep 8000
```

**Issue**: SSL certificate expired
```bash
# Check expiry
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Restart nginx
sudo systemctl restart nginx
```

**Issue**: Tiger service not processing documents
```bash
# Check Tiger service directly
cd /opt/tm/tiger && ./run.sh info

# Check Python virtual environment
ls -la venv/

# Check log permissions
ls -la data/logs/

# Fix permissions if needed
chmod 755 data/logs/
```

**Issue**: High memory usage
```bash
# Check memory usage
free -h

# Check largest processes
ps aux --sort=-%mem | head -10

# Restart TM services if needed
sudo systemctl restart tm-dashboard
```

### Debug Mode Activation
```bash
# Enable TM debug logging
export DEBUG_MODE=true

# Dashboard debug mode
cd /opt/tm/dashboard && DEBUG=true ./start.sh

# View detailed logs
journalctl -u tm-dashboard -f --no-pager
```

## 📊 Monitoring & Alerts

### Health Check Endpoints
```bash
# TM system health
curl https://legal.satori-ai-tech.com/health

# Dashboard API health
curl https://legal.satori-ai-tech.com/api/health

# SSL certificate check
echo | openssl s_client -servername legal.satori-ai-tech.com -connect legal.satori-ai-tech.com:443 2>/dev/null | openssl x509 -noout -enddate
```

### Automated Monitoring Script
```bash
#!/bin/bash
# Save as /opt/tm/scripts/health_monitor.sh

echo "=== TM System Health Check $(date) ==="

# Check dashboard service
if systemctl is-active --quiet tm-dashboard; then
    echo "✅ Dashboard service running"
else
    echo "❌ Dashboard service DOWN"
fi

# Check HTTPS access
if curl -s https://legal.satori-ai-tech.com/health | grep -q "Healthy"; then
    echo "✅ HTTPS access working"
else
    echo "❌ HTTPS access FAILED"
fi

# Check SSL certificate (days until expiry)
EXPIRY_DATE=$(echo | openssl s_client -servername legal.satori-ai-tech.com -connect legal.satori-ai-tech.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_UNTIL_EXPIRY=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))

if [ $DAYS_UNTIL_EXPIRY -gt 30 ]; then
    echo "✅ SSL certificate valid for $DAYS_UNTIL_EXPIRY days"
else
    echo "⚠️ SSL certificate expires in $DAYS_UNTIL_EXPIRY days"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ Disk usage: ${DISK_USAGE}%"
else
    echo "⚠️ High disk usage: ${DISK_USAGE}%"
fi

echo "=== Health Check Complete ==="
```

## 🔄 Backup & Recovery

### Backup Procedures
```bash
# Complete TM system backup
tar -czf /root/tm-backup-$(date +%Y%m%d-%H%M).tar.gz /opt/tm/

# Configuration backup
tar -czf /root/config-backup-$(date +%Y%m%d).tar.gz /etc/nginx/sites-available/ /etc/letsencrypt/

# Database backup (if applicable)
# Currently TM uses file-based storage, included in system backup

# Upload to remote storage (configure as needed)
# scp /root/tm-backup-*.tar.gz user@backup-server:/backups/
```

### Recovery Procedures
```bash
# Restore TM system from backup
tar -xzf /root/tm-backup-YYYYMMDD-HHMM.tar.gz -C /

# Restore nginx configuration
tar -xzf /root/config-backup-YYYYMMDD.tar.gz -C /

# Restart services
sudo systemctl restart nginx
sudo systemctl restart tm-dashboard

# Verify restoration
curl https://legal.satori-ai-tech.com/health
```

## 📈 Scaling Considerations

### Current Capacity
- **Concurrent Users**: 10-20 (single VPS)
- **Document Processing**: 2-5 minutes per case
- **Storage**: 25GB (thousands of cases)
- **Network**: 1TB/month transfer

### Scale-Up Options
1. **Vertical Scaling**: Upgrade to larger Linode plan
2. **Horizontal Scaling**: Additional VPS instances
3. **Service Separation**: Dedicated VPS per TM service

### Performance Monitoring
```bash
# Monitor resource usage over time
sar -u 1 10    # CPU usage
sar -r 1 10    # Memory usage
sar -d 1 10    # Disk I/O

# Network monitoring
iftop          # Real-time network usage
```

## 🔐 Security Best Practices

### Applied Security Measures
- ✅ SSL/TLS encryption (Let's Encrypt)
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Regular security updates (unattended-upgrades)
- ✅ SSH key-based authentication
- ✅ Firewall configuration (ufw)
- ✅ Session-based dashboard authentication

### Security Maintenance
```bash
# Check for security updates
sudo apt list --upgradable | grep -i security

# Update security packages
sudo unattended-upgrades

# Check failed login attempts
sudo journalctl -u ssh --since "24 hours ago" | grep "Failed"

# Review nginx access logs for suspicious activity
sudo tail -f /var/log/nginx/access.log | grep -E "(40[0-9]|50[0-9])"
```

### Incident Response
1. **Suspicious Activity**: Review logs, block IPs if needed
2. **SSL Compromise**: Force certificate renewal
3. **Service Compromise**: Stop services, investigate, restore from backup
4. **Data Breach**: Isolate system, preserve logs, assess scope

---

## 📞 Support Information

**System Administrator**: Claude (Dr. Spock)  
**Architecture**: Subdomain-based client isolation  
**Current Version**: TM v1.9.2  
**Demo Server**: https://legal.satori-ai-tech.com/  
**SSH Access**: `ssh root@legal-agent-vps`  

**Emergency Contacts**:
- Technical Issues: Review this bible and troubleshooting section
- SSL Issues: Let's Encrypt auto-renewal should handle
- VPS Issues: Linode support dashboard

**Key Files to Remember**:
- TM System: `/opt/tm/`
- Nginx Config: `/etc/nginx/sites-available/tm-legal-demo`
- SSL Certs: `/etc/letsencrypt/live/legal.satori-ai-tech.com/`
- Service Logs: `journalctl -u tm-dashboard -f`

This bible contains all knowledge needed to maintain, troubleshoot, and scale the TM legal document processing platform. Keep it updated as the system evolves.