# TM Legal Document Processing Platform
# Production Deployment Plan for Linode VPS with SSL and Tenant Isolation

## Overview

This deployment plan sets up the TM Legal Document Processing Platform on Linode VPS with:
- Native SSL via Let's Encrypt (no Docker)
- Tenant isolation via URL paths (legal.satori-ai-tech.com/mallon/)
- Systemd service management
- Nginx reverse proxy
- Auto-renewing SSL certificates

## Architecture

```
Internet → Nginx (SSL termination) → TM Dashboard (Python/FastAPI) → Tiger/Monkey Services
         |                         |
         SSL Cert                  Port 8000
         Let's Encrypt            (localhost only)
```

## Deployment Workflow

### Phase 1: Initial Setup (Master Template)

1. **DNS Configuration**
   ```bash
   # Create A record
   legal.satori-ai-tech.com → your-linode-ip
   ```

2. **Deploy Master Template**
   ```bash
   cd /path/to/service_config
   chmod +x *.sh
   sudo ./deploy.sh mallon legal.satori-ai-tech.com admin@satori-ai-tech.com
   ```

3. **Verify Deployment**
   ```bash
   # Check services
   sudo systemctl status tm-dashboard nginx
   
   # Test SSL endpoint
   curl -k https://legal.satori-ai-tech.com/mallon/
   ```

4. **Create Linode Snapshot**
   - Take snapshot of configured VPS
   - Name: "TM-Legal-Platform-v1.9-SSL"

### Phase 2: Client Deployment (Clone & Configure)

1. **Deploy New VPS from Snapshot**
   - Create new $24 Linode from snapshot
   - Get new IP address

2. **Configure for New Client**
   ```bash
   sudo ./clone_tenant.sh smith-law legal.satori-ai-tech.com
   ```

3. **Update DNS**
   ```bash
   # Update A record to new VPS IP
   legal.satori-ai-tech.com → new-linode-ip
   ```

4. **Verify New Tenant**
   ```bash
   curl -k https://legal.satori-ai-tech.com/smith-law/
   ```

## File Structure

```
/opt/tm/                          # TM application directory
├── .env                          # Environment configuration
├── dashboard/                    # FastAPI dashboard
├── tiger/                        # Document analysis
├── monkey/                       # Document generation
├── shared-schema/               # Common data models
├── outputs/                     # Generated documents
├── test-data/                   # Case files
└── logs/                        # Application logs

/etc/systemd/system/
└── tm-dashboard.service         # Systemd service

/etc/nginx/sites-available/
└── tm-legal                     # Nginx configuration

/etc/letsencrypt/live/legal.satori-ai-tech.com/
├── fullchain.pem               # SSL certificate
└── privkey.pem                 # SSL private key
```

## Security Features

### SSL Configuration
- **TLS 1.2/1.3 only** - Modern encryption protocols
- **HSTS headers** - Force HTTPS connections
- **OCSP stapling** - Certificate validation optimization
- **Auto-renewal** - Systemd timer handles certificate renewal

### System Security
- **Dedicated user** - TM runs as 'tm' user with limited privileges
- **Protected file system** - Read-only system directories
- **Resource limits** - Memory and file descriptor limits
- **Security headers** - XSS, CSRF, and clickjacking protection

### Network Security
- **Localhost only** - TM dashboard only listens on 127.0.0.1:8000
- **Nginx proxy** - SSL termination and security headers
- **Firewall ready** - Only ports 22, 80, 443 need to be open

## Service Management

### Start/Stop/Restart
```bash
# TM Dashboard
sudo systemctl start tm-dashboard
sudo systemctl stop tm-dashboard  
sudo systemctl restart tm-dashboard

# Nginx
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
```

### Monitoring
```bash
# Service status
sudo systemctl status tm-dashboard nginx

# Real-time logs
journalctl -u tm-dashboard -f
journalctl -u nginx -f

# SSL certificate status
sudo certbot certificates
```

### Configuration Updates
```bash
# Update TM environment
sudo nano /opt/tm/.env
sudo systemctl restart tm-dashboard

# Update Nginx
sudo nano /etc/nginx/sites-available/tm-legal
sudo nginx -t
sudo systemctl reload nginx
```

## Performance & Scaling

### Resource Usage (Per Tenant)
- **CPU**: 1-2 cores for document processing
- **RAM**: 1-2GB for ML models and caching  
- **Storage**: 10-20GB for cases and outputs
- **Network**: Minimal (upload/download only)

### Monitoring Points
- TM dashboard response time (< 500ms)
- Document processing time (2-30 seconds)
- SSL certificate expiry (auto-renewed)
- Disk space usage (case files and outputs)

## Client Onboarding Process

### New Client Steps
1. **Provision VPS**: Deploy from master snapshot
2. **Configure tenant**: Run clone_tenant.sh with client name
3. **DNS update**: Point legal.satori-ai-tech.com to new IP
4. **SSL verification**: Test https://legal.satori-ai-tech.com/client-name/
5. **Training**: Provide client with access credentials and training

### Estimated Timeline
- **VPS deployment**: 5 minutes
- **Tenant configuration**: 2 minutes  
- **DNS propagation**: 5-60 minutes
- **SSL verification**: 1 minute
- **Total**: 15-70 minutes per client

## Cost Analysis (Per Client)

### Linode VPS ($24/month)
- 4GB RAM, 2 CPU cores
- 80GB SSD storage
- 4TB transfer
- Dedicated isolation

### Additional Costs
- **Domain/DNS**: $0 (using existing satori-ai-tech.com)
- **SSL certificates**: $0 (Let's Encrypt)
- **Support overhead**: ~1 hour/month per client

### Total Cost Per Client
- **Monthly**: $24 VPS + minimal support overhead
- **Annual**: $288 + domain renewal ($15)

## Backup & Disaster Recovery

### Automated Backups
- **Linode snapshots**: Weekly automatic snapshots
- **Case data**: Sync to external storage (optional)
- **Configuration**: Version controlled in Git

### Recovery Procedures
- **Hardware failure**: Deploy from latest snapshot
- **Configuration corruption**: Restore from Git + re-run deploy.sh
- **Certificate expiry**: Auto-renewal handles this
- **Data loss**: Restore from Linode snapshot

## Support & Maintenance

### Regular Maintenance
- **System updates**: Monthly security patches
- **Certificate renewal**: Automatic (verify monthly)
- **Log rotation**: Configured via systemd
- **Performance monitoring**: Check resource usage

### Troubleshooting
```bash
# Common issues
sudo systemctl status tm-dashboard  # Service not running
sudo nginx -t                      # Nginx config error
sudo certbot certificates          # SSL issues
df -h                              # Disk space
free -h                            # Memory usage
```

## Next Steps

### Immediate Actions
1. Test deployment on current TM Linode
2. Verify SSL endpoint functionality
3. Create master snapshot for cloning
4. Document client onboarding process

### Future Enhancements
1. **Monitoring dashboard** - Grafana + Prometheus
2. **Automated client provisioning** - API-driven VPS deployment  
3. **Backup automation** - Scheduled off-site backups
4. **Load balancing** - Multiple regions for performance
5. **White-label domains** - client.law domains instead of subdomains

---

**Deployment Status**: Ready for implementation
**Target Go-Live**: After testing and validation
**Support Model**: Managed service with 99.5% uptime SLA
