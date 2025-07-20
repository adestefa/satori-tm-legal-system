# VPS Production Deployment - Remaining Work Plan
**Date**: July 20, 2025  
**Current Status**: Core application deployed and functional ✅  
**Target**: Complete production-ready HTTPS deployment

## Overview

The Tiger-Monkey legal document processing system is successfully deployed and operational on the VPS at `66.228.34.12:8000`. All core functionality has been verified including document processing, generation, and web interface. The remaining work focuses on SSL certificates and production domain configuration.

## Phase 1: SSL Certificate Setup (High Priority)

### 1.1 Let's Encrypt Certificate Installation
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate  
sudo certbot certonly --standalone -d legal.satori-ai-tech.com

# Expected output location: /etc/letsencrypt/live/legal.satori-ai-tech.com/
```

### 1.2 Nginx Reverse Proxy Configuration
**File**: `/etc/nginx/sites-available/tm-legal`
```nginx
server {
    listen 80;
    server_name legal.satori-ai-tech.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name legal.satori-ai-tech.com;
    
    ssl_certificate /etc/letsencrypt/live/legal.satori-ai-tech.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/legal.satori-ai-tech.com/privkey.pem;
    
    # SSL Security Headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    # Tenant routing for /mallon/
    location /mallon/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Tenant-ID mallon;
    }
    
    # Root application access
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 1.3 SSL Certificate Auto-Renewal
```bash
# Test renewal process
sudo certbot renew --dry-run

# Add cron job for automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Phase 2: Domain Configuration (High Priority)

### 2.1 DNS Updates
**Action Required**: Update DNS records to point `legal.satori-ai-tech.com` to VPS IP
```
A Record: legal.satori-ai-tech.com → 66.228.34.12
```

### 2.2 Tenant Routing Implementation  
**File**: `/opt/tm/dashboard/main.py` (modify if needed)
```python
# Add tenant middleware for /mallon/ routing
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    if request.url.path.startswith("/mallon/"):
        request.state.tenant_id = "mallon"
        # Strip /mallon/ prefix for internal routing
        request.scope["path"] = request.url.path[7:]  # Remove "/mallon"
    
    response = await call_next(request)
    return response
```

### 2.3 Production URL Configuration
**Update**: Dashboard configuration to handle HTTPS and domain routing
- Modify WebSocket connections to use WSS protocol
- Update API base URLs for production domain
- Configure CORS settings for HTTPS access

## Phase 3: Security Verification (Medium Priority)

### 3.1 SSL/TLS Testing
```bash
# Test SSL certificate installation
curl -I https://legal.satori-ai-tech.com

# Verify SSL security rating
# Use: https://www.ssllabs.com/ssltest/
```

### 3.2 Security Headers Validation
**Expected Headers**:
- `Strict-Transport-Security: max-age=63072000`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-Forwarded-Proto: https`

### 3.3 Access Control Testing
```bash
# Verify HTTP to HTTPS redirect
curl -I http://legal.satori-ai-tech.com

# Test tenant routing
curl -I https://legal.satori-ai-tech.com/mallon/

# Verify WebSocket connections over WSS
# Test via Dashboard web interface
```

## Phase 4: Monitoring and Maintenance (Low Priority)

### 4.1 Certificate Renewal Monitoring
```bash
# Add monitoring script for certificate expiry
cat > /opt/tm/scripts/check-ssl.sh << 'EOF'
#!/bin/bash
CERT_FILE="/etc/letsencrypt/live/legal.satori-ai-tech.com/fullchain.pem"
EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_UNTIL_EXPIRY=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))

if [ $DAYS_UNTIL_EXPIRY -lt 30 ]; then
    echo "WARNING: SSL certificate expires in $DAYS_UNTIL_EXPIRY days"
    exit 1
fi
echo "SSL certificate valid for $DAYS_UNTIL_EXPIRY more days"
EOF

chmod +x /opt/tm/scripts/check-ssl.sh
```

### 4.2 System Health Monitoring
- Add SSL certificate monitoring to existing health checks
- Monitor HTTPS response times and availability
- Verify tenant routing functionality in production

## Implementation Timeline

### Immediate (Day 1)
1. ✅ **Complete**: Core application deployment and functionality verification
2. **Next**: SSL certificate installation with Let's Encrypt
3. **Next**: Nginx reverse proxy configuration with HTTPS redirect

### Short Term (Day 2-3)  
1. DNS updates to point domain to VPS
2. Tenant routing implementation and testing
3. SSL security verification and testing

### Medium Term (Week 1)
1. Certificate auto-renewal setup and verification  
2. Security headers and HTTPS enforcement testing
3. Production monitoring and alerting setup

## Success Criteria

### SSL Implementation Success
- [ ] HTTPS access working: `https://legal.satori-ai-tech.com`
- [ ] HTTP to HTTPS redirect functional  
- [ ] SSL Labs rating: A or A+
- [ ] Certificate auto-renewal configured and tested

### Tenant Routing Success
- [ ] Mallon tenant access: `https://legal.satori-ai-tech.com/mallon/`
- [ ] WebSocket connections working over WSS
- [ ] Dashboard functionality preserved under HTTPS
- [ ] API endpoints responding correctly via HTTPS

### Security Verification Success
- [ ] All security headers present and correct
- [ ] SSL certificate chain properly configured
- [ ] HSTS header enforcing HTTPS-only access
- [ ] No mixed content warnings in browser

## Risk Mitigation

### Potential Issues
1. **Certificate Generation**: Domain may not resolve during Let's Encrypt validation
   - **Mitigation**: Ensure DNS is updated before certificate request
   - **Fallback**: Use standalone mode if domain not yet pointing to VPS

2. **WebSocket Connections**: WSS connections may fail with proxy configuration
   - **Mitigation**: Test WebSocket upgrade headers in Nginx config
   - **Fallback**: Direct connection configuration if proxy issues occur

3. **Tenant Routing**: URL rewriting may break existing functionality  
   - **Mitigation**: Thorough testing of all Dashboard features under /mallon/ path
   - **Fallback**: Direct domain access until routing issues resolved

### Rollback Plan
If HTTPS deployment fails:
1. Disable Nginx proxy configuration
2. Direct access via IP:port (66.228.34.12:8000) remains functional
3. Core TM system continues operating normally
4. Retry SSL configuration with corrected settings

## Current System State

**Verified Working**:
- ✅ Tiger document processing (ML models, quality scoring)
- ✅ Monkey document generation (templates, creditor addresses)  
- ✅ Dashboard web interface (authentication, WebSocket, API)
- ✅ Browser PDF service (Node.js, Puppeteer ready)
- ✅ Cross-platform utility scripts
- ✅ Git repository synchronization
- ✅ Systemd service management

**Ready for Production**: Core functionality complete, SSL setup is final step for production deployment.

---

**Next Action**: Execute Phase 1 SSL certificate setup to complete production-ready HTTPS deployment.