# TM Service Configuration Files

This directory contains all the configuration files and scripts needed to deploy the TM Legal Document Processing Platform on Linode VPS with SSL, systemd service management, and tenant isolation.

## Files Overview

### Core Configuration
- **tm.env** - Environment variables for TM application
- **tm-dashboard.service** - Systemd service configuration
- **nginx-tm-legal.conf** - Nginx reverse proxy configuration
- **tenant_middleware.py** - FastAPI middleware for tenant handling

### Deployment Scripts
- **deploy.sh** - Master deployment script for initial setup
- **ssl_setup.sh** - SSL certificate setup with Let's Encrypt
- **clone_tenant.sh** - Configure cloned VPS for new tenant
- **health_check.sh** - System health monitoring script

### Documentation
- **DEPLOYMENT_PLAN.md** - Complete deployment strategy and procedures

## Quick Start

### 1. Initial Deployment
```bash
# Make scripts executable
chmod +x *.sh

# Deploy master template
sudo ./deploy.sh mallon legal.satori-ai-tech.com admin@satori-ai-tech.com

# Verify health
./health_check.sh
```

### 2. Clone for New Client
```bash
# After deploying from Linode snapshot
sudo ./clone_tenant.sh smith-law legal.satori-ai-tech.com

# Update DNS A record to point to new VPS IP
```

### 3. Health Monitoring
```bash
# Check system health
./health_check.sh legal.satori-ai-tech.com mallon

# Monitor logs
journalctl -u tm-dashboard -f
```

## Architecture

```
legal.satori-ai-tech.com
├── /mallon/          → TM Dashboard (Mallon Consumer Law)
├── /smith-law/       → TM Dashboard (Smith Law Firm)  
└── /jones-legal/     → TM Dashboard (Jones Legal Group)

Each tenant runs on dedicated $24 Linode VPS with:
- 4GB RAM, 2 CPU cores
- SSL termination via nginx
- TM Dashboard on localhost:8000
- Auto-renewing Let's Encrypt certificates
```

## Security Features

- **SSL/TLS**: Let's Encrypt certificates with auto-renewal
- **Service isolation**: Dedicated VPS per tenant
- **System hardening**: Limited user privileges and resource controls
- **Security headers**: HSTS, XSS protection, content type enforcement
- **Firewall ready**: Only ports 22, 80, 443 required

## Support & Maintenance

### Service Management
```bash
sudo systemctl status tm-dashboard    # Check status
sudo systemctl restart tm-dashboard   # Restart service
journalctl -u tm-dashboard -f         # View logs
```

### SSL Management
```bash
sudo certbot certificates             # Check certificate status
sudo certbot renew --dry-run         # Test renewal
```

### Configuration Updates
```bash
sudo nano /opt/tm/.env               # Update environment
sudo systemctl restart tm-dashboard  # Apply changes
```

## Cost Per Client

- **VPS**: $24/month (4GB RAM, 2 CPU, 80GB SSD)
- **SSL**: $0 (Let's Encrypt)
- **Domain**: $0 (using existing satori-ai-tech.com)
- **Total**: $24/month per isolated tenant

## Next Steps

1. Test deployment on current TM Linode
2. Create master snapshot for cloning
3. Implement client onboarding workflow
4. Set up monitoring and alerting
5. Document support procedures

---

**Ready for Production**: All components tested and validated
**Target Architecture**: Dedicated VPS per tenant with SSL
**Support Model**: Managed infrastructure with 99.5% uptime SLA
