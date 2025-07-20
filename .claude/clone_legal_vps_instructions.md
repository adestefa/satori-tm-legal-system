# TM Legal VPS Cloning Instructions

**Purpose**: Clone the GOLD demo server (`legal.satori-ai-tech.com`) to create new client production servers  
**Architecture**: `<client>.legal.satori-ai-tech.com` → dedicated client VPS  
**Date**: July 20, 2025  
**Source**: Demo/Sales GOLD template server  

## 🎯 Overview

This guide provides step-by-step instructions for cloning our production-ready TM legal document processing system from the GOLD demo server to create new client production environments.

### What You're Cloning
- **Source**: `legal.satori-ai-tech.com` (66.228.34.12) - Demo/Sales server
- **Target**: `<client>.legal.satori-ai-tech.com` (new VPS IP) - Client production server
- **Components**: Complete TM system + SSL + Nginx + all configurations

## 📋 Prerequisites Checklist

### Required Information
- [ ] **Client Name**: (e.g., "mallon" for Mallon Consumer Law Group)
- [ ] **New VPS IP**: Assigned IP address of the new Linode VPS
- [ ] **Linode Account Access**: For VPS provisioning and DNS management
- [ ] **SSH Access**: To both source and target VPS instances

### Required Tools
- [ ] SSH client with key-based authentication
- [ ] Linode CLI (optional, for automation)
- [ ] DNS management access (Linode DNS Manager)

## 🚀 Step-by-Step Cloning Process

### Phase 1: VPS Provisioning (15 minutes)

#### 1.1 Create New Linode VPS
1. **Login to Linode Cloud Manager**
2. **Create Linode**:
   - **Plan**: Nanode 1GB ($5/month)
   - **Region**: Same as demo server (for consistency)
   - **Image**: Ubuntu 24.04 LTS
   - **Root Password**: Set secure password
   - **SSH Keys**: Add your public SSH key
3. **Note the assigned IP address** (e.g., 66.228.34.13)
4. **Wait for VPS to boot** (2-3 minutes)

#### 1.2 Configure SSH Access
```bash
# Test SSH access to new VPS
ssh root@<NEW_VPS_IP>

# Add SSH alias for convenience (optional)
echo "Host <client>-legal-vps
    HostName <NEW_VPS_IP>
    User root
    IdentityFile ~/.ssh/id_rsa" >> ~/.ssh/config

# Test alias
ssh <client>-legal-vps
```

### Phase 2: System Preparation (10 minutes)

#### 2.1 Basic System Setup
```bash
# Connect to new VPS
ssh root@<NEW_VPS_IP>

# Update system packages
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv nodejs npm poppler-utils tesseract-ocr tesseract-ocr-eng nginx certbot python3-certbot-nginx git curl wget

# Create TM user (optional, for security)
useradd -m -s /bin/bash tm
usermod -aG sudo tm
```

#### 2.2 Create Directory Structure
```bash
# Create main TM directory
mkdir -p /opt/tm
cd /opt/tm

# Set ownership (if using tm user)
chown -R tm:tm /opt/tm
```

### Phase 3: TM System Deployment (30 minutes)

#### 3.1 Clone TM Repository
```bash
# Clone the complete TM system
git clone https://github.com/adestefa/satori-tm-legal-system.git .

# Ensure we're on the latest version
git checkout main
git pull origin main
```

#### 3.2 Install TM Services
```bash
# Install all TM services using the automated installer
./install_all.sh

# This will:
# - Install shared schema
# - Install Tiger service (ML processing)
# - Install Monkey service (document generation)
# - Install Dashboard service (web interface)
# - Install Browser service (PDF generation)
```

#### 3.3 Verify TM Installation
```bash
# Check virtual environments
ls -la */venv */node_modules

# Test Tiger service
cd tiger && ./run.sh info
cd ..

# Test Monkey service
cd monkey && ./run.sh --help
cd ..

# Test Browser service
cd browser && node pdf-generator.js --test
cd ..
```

### Phase 4: Dashboard Configuration (15 minutes)

#### 4.1 Configure Dashboard Service
```bash
cd dashboard

# Create outputs directory
mkdir -p outputs

# Install missing dependencies (if needed)
./venv/bin/pip install python-multipart

# Configure client-specific settings
cp config/settings.json config/settings.json.backup
```

#### 4.2 Update Client Settings
Edit `/opt/tm/dashboard/config/settings.json`:
```json
{
  "firm_name": "<CLIENT FIRM NAME>",
  "firm_address": {
    "street": "<CLIENT ADDRESS>",
    "city": "<CLIENT CITY>",
    "state": "<CLIENT STATE>",
    "zip_code": "<CLIENT ZIP>"
  },
  "contact_info": {
    "phone": "<CLIENT PHONE>",
    "email": "<CLIENT EMAIL>",
    "website": "<CLIENT WEBSITE>"
  },
  "attorney_info": {
    "name": "<ATTORNEY NAME>",
    "bar_number": "<BAR NUMBER>",
    "admission": "<ADMISSION INFO>"
  }
}
```

#### 4.3 Setup Systemd Service
```bash
# Create systemd service file
cat > /etc/systemd/system/tm-dashboard.service << 'EOF'
[Unit]
Description=TM Legal Document Processing Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/tm/dashboard
Environment=PATH=/opt/tm/dashboard/venv/bin
ExecStart=/opt/tm/dashboard/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable tm-dashboard
systemctl start tm-dashboard

# Verify service is running
systemctl status tm-dashboard
```

### Phase 5: DNS Configuration (5 minutes)

#### 5.1 Add DNS Record
1. **Login to Linode DNS Manager**
2. **Navigate to**: `satori-ai-tech.com` domain
3. **Add A Record**:
   - **Hostname**: `<client>.legal`
   - **IP Address**: `<NEW_VPS_IP>`
   - **TTL**: 300 (5 minutes)
4. **Save changes**

#### 5.2 Verify DNS Propagation
```bash
# Check DNS resolution (may take 5-30 minutes)
nslookup <client>.legal.satori-ai-tech.com

# Should return the new VPS IP address
dig +short <client>.legal.satori-ai-tech.com
```

### Phase 6: SSL Certificate Setup (10 minutes)

#### 6.1 Create SSL Deployment Script
```bash
# Create client-specific SSL script
cat > /opt/tm/deploy_client_ssl.sh << 'EOF'
#!/bin/bash

CLIENT="<client>"
DOMAIN="${CLIENT}.legal.satori-ai-tech.com"
EMAIL="admin@satori-ai-tech.com"

echo "🔒 SSL Setup for $DOMAIN"

# Create temporary HTTP configuration
cat > /etc/nginx/sites-available/tm-client << EOF2
server {
    listen 80;
    server_name ${DOMAIN};
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF2

# Enable temporary configuration
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/tm-client /etc/nginx/sites-enabled/
mkdir -p /var/www/html
nginx -t && systemctl restart nginx

# Request SSL certificate
certbot certonly \
    --webroot \
    -w /var/www/html \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN \
    --non-interactive

# Create full SSL configuration
cat > /etc/nginx/sites-available/tm-client << EOF2
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};
    
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
    
    location /health {
        access_log off;
        return 200 "TM Legal Client Platform Healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF2

# Deploy SSL configuration
nginx -t && systemctl restart nginx

# Enable auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

echo "✅ SSL setup complete for $DOMAIN"
EOF

# Make script executable
chmod +x /opt/tm/deploy_client_ssl.sh
```

#### 6.2 Execute SSL Setup
```bash
# Run the SSL deployment script
cd /opt/tm
./deploy_client_ssl.sh

# Wait for completion (2-3 minutes)
```

### Phase 7: Testing & Verification (15 minutes)

#### 7.1 System Health Checks
```bash
# Test HTTPS access
curl https://<client>.legal.satori-ai-tech.com/health

# Test HTTP redirect
curl -I http://<client>.legal.satori-ai-tech.com/

# Test dashboard access
curl -I https://<client>.legal.satori-ai-tech.com/

# Check SSL certificate
echo | openssl s_client -servername <client>.legal.satori-ai-tech.com -connect <client>.legal.satori-ai-tech.com:443 2>/dev/null | openssl x509 -noout -enddate
```

#### 7.2 TM Service Integration Test
```bash
# Test Tiger processing
cd /opt/tm/tiger
./run.sh hydrated-json ../test-data/sync-test-cases/Rodriguez/ -o ../outputs/

# Test Monkey document generation
cd ../monkey
./run.sh build-complaint ../outputs/hydrated_*.json --all

# Test Browser PDF generation
cd ../browser
node pdf-generator.js ../outputs/complaint.html

# Check all outputs
ls -la ../outputs/
```

#### 7.3 Dashboard Functionality Test
1. **Open Browser**: `https://<client>.legal.satori-ai-tech.com/`
2. **Login**: Use default credentials or client-specific
3. **Upload Test Case**: Try Rodriguez test case
4. **Process Documents**: Verify Tiger → Dashboard → Monkey pipeline
5. **Generate Documents**: Test complaint and summons generation
6. **Download PDFs**: Verify browser service integration

### Phase 8: Client Onboarding (30 minutes)

#### 8.1 Client-Specific Configuration
```bash
# Update firm settings via Dashboard UI
# - Navigate to Settings page
# - Update firm information
# - Configure attorney details
# - Upload client-specific templates (if any)
```

#### 8.2 Data Migration (if applicable)
```bash
# If migrating existing cases from demo server
# Transfer case files to test-data/sync-test-cases/
scp -r /path/to/client/cases root@<NEW_VPS_IP>:/opt/tm/test-data/sync-test-cases/

# Process historical cases
cd /opt/tm/tiger
for case_dir in ../test-data/sync-test-cases/*/; do
    echo "Processing $case_dir"
    ./run.sh hydrated-json "$case_dir" -o ../outputs/
done
```

#### 8.3 Client Training & Handoff
1. **Provide Access Credentials**:
   - HTTPS URL: `https://<client>.legal.satori-ai-tech.com/`
   - Login credentials
   - SSH access (if needed)

2. **Training Materials**:
   - TM user guide
   - Document upload procedures
   - Case processing workflow
   - Troubleshooting contact info

## 🔧 Post-Deployment Configuration

### Optional Enhancements

#### Custom Branding
```bash
# Update Dashboard themes
cd /opt/tm/dashboard/static/themes/
# Modify CSS files for client branding
```

#### Template Customization
```bash
# Add client-specific templates
cd /opt/tm/monkey/templates/
# Upload custom templates via Dashboard UI
```

#### Backup Configuration
```bash
# Setup automated backups
crontab -e

# Add daily backup job
0 2 * * * tar -czf /root/tm-backup-$(date +\%Y\%m\%d).tar.gz /opt/tm/
```

## 🚨 Troubleshooting Common Issues

### SSL Certificate Problems
```bash
# Check certificate status
sudo certbot certificates

# Manual renewal if auto-renewal fails
sudo certbot renew --force-renewal

# Check nginx configuration
sudo nginx -t
```

### Dashboard Service Issues
```bash
# Check service status
systemctl status tm-dashboard

# View logs
journalctl -u tm-dashboard -f

# Restart service
systemctl restart tm-dashboard
```

### DNS Propagation Delays
```bash
# Check current DNS status
nslookup <client>.legal.satori-ai-tech.com

# Use alternative DNS servers for testing
nslookup <client>.legal.satori-ai-tech.com 8.8.8.8
```

### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Optimize if needed
systemctl restart tm-dashboard
systemctl restart nginx
```

## 📊 Success Verification Checklist

### Technical Verification
- [ ] **HTTPS Access**: `https://<client>.legal.satori-ai-tech.com/` loads
- [ ] **SSL Certificate**: Valid and auto-renewing
- [ ] **HTTP Redirect**: HTTP properly redirects to HTTPS
- [ ] **Health Endpoint**: `/health` returns "Healthy"
- [ ] **Dashboard Login**: Authentication works
- [ ] **File Upload**: Can upload and process documents
- [ ] **Document Generation**: Complaint and summons generate successfully
- [ ] **PDF Generation**: Browser service produces PDFs

### Service Verification
- [ ] **Tiger Service**: Processes documents and extracts data
- [ ] **Monkey Service**: Generates court-ready documents
- [ ] **Dashboard Service**: Web interface fully functional
- [ ] **Browser Service**: PDF generation working
- [ ] **Nginx Proxy**: HTTPS proxy working correctly
- [ ] **SSL Auto-renewal**: Certbot timer active

### Client Verification
- [ ] **Firm Settings**: Client information configured
- [ ] **Template Upload**: Client-specific templates (if any)
- [ ] **Test Case**: End-to-end processing successful
- [ ] **User Training**: Client can operate system
- [ ] **Documentation**: Client has access instructions

## 🎯 Quick Reference Commands

### Essential Management Commands
```bash
# SSH to client VPS
ssh root@<NEW_VPS_IP>

# Check TM dashboard status
systemctl status tm-dashboard

# View dashboard logs
journalctl -u tm-dashboard -f

# Test HTTPS access
curl https://<client>.legal.satori-ai-tech.com/health

# Restart services
systemctl restart tm-dashboard nginx

# Check SSL certificate
certbot certificates

# View nginx configuration
cat /etc/nginx/sites-available/tm-client
```

### Emergency Recovery
```bash
# If dashboard is down
systemctl restart tm-dashboard

# If HTTPS is down
nginx -t && systemctl restart nginx

# If SSL expired
certbot renew --force-renewal

# Full system restart
reboot
```

## 📞 Support Information

**Documentation**: Refer to `/opt/tm/.claude/server_bible.md` for detailed management  
**Demo Server**: `https://legal.satori-ai-tech.com/` (for reference)  
**Client Template**: This guide for all future client deployments  

**Cost**: $5/month per client VPS  
**Deployment Time**: ~90 minutes total  
**Maintenance**: Minimal (automated SSL renewal, systemd service management)  

---

**Total Deployment Time**: ~90 minutes  
**Monthly Cost**: $5 per client  
**Maintenance**: Automated (SSL renewal, service monitoring)  
**Scalability**: Unlimited clients using this pattern  

This process creates a complete, isolated TM legal document processing environment for each client with professional HTTPS access and automated maintenance.