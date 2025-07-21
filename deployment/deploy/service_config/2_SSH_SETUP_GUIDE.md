# TM VPS SSH Setup and SSL Upgrade Guide

This guide walks through securing the TM VPS with SSH keys and upgrading to SSL configuration.

## Current VPS Details
- **IP**: 198.74.59.11
- **User**: root
- **Password**: Croot2160key$
- **TM Location**: /home/deploy/satori-tm-legal-system/
- **Target Domain**: legal.satori-ai-tech.com/mallon/

## Phase 1: Secure SSH Setup

### Step 1: Generate SSH Keys (LOCAL MACHINE)
```bash
cd /Users/corelogic/satori-dev/TM/deployment/deploy/service_config
chmod +x setup_ssh_keys.sh
./setup_ssh_keys.sh
```

This script will:
- Generate new ED25519 SSH key pair
- Create SSH config entry for "tm-legal" host
- Display public key to copy to VPS

### Step 2: Install Public Key on VPS (MANUAL)
1. **Connect with password (last time)**:
   ```bash
   ssh root@198.74.59.11
   # Password: Croot2160key$
   ```

2. **Setup SSH key authentication**:
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   nano ~/.ssh/authorized_keys
   # Paste the public key from Step 1
   chmod 600 ~/.ssh/authorized_keys
   ```

3. **Test key-based connection**:
   ```bash
   exit
   ssh tm-legal  # Should connect without password
   ```

4. **Disable password authentication**:
   ```bash
   nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   systemctl restart sshd
   ```

## Phase 2: VPS Migration and Setup

### Step 3: Upload Configuration Files
```bash
# From LOCAL machine
scp *.sh tm.env tm-dashboard.service nginx-tm-legal.conf tm-legal:/tmp/
```

### Step 4: Run VPS Upgrade Script
```bash
# On VPS
ssh tm-legal
cd /tmp
chmod +x *.sh
sudo ./vps_upgrade_phase1.sh
```

This script will:
- Update system packages
- Install nginx, certbot, and dependencies
- Create TM user and proper directory structure
- Migrate TM from `/home/deploy/satori-tm-legal-system/` to `/opt/tm/`
- Create systemd service configuration
- Setup environment variables with secure session secret

### Step 5: Verify TM Service
```bash
# Test TM service
sudo systemctl start tm-dashboard
sudo systemctl status tm-dashboard
journalctl -u tm-dashboard -f

# Test local access
curl http://127.0.0.1:8000
```

## Phase 3: SSL Configuration

### Step 6: DNS Setup (FIRST!)
**CRITICAL**: Update DNS before running SSL setup
```bash
# Update A record
legal.satori-ai-tech.com → 198.74.59.11
```

### Step 7: Run SSL Setup
```bash
# On VPS
sudo ./ssl_setup.sh
```

This will:
- Configure nginx with SSL
- Obtain Let's Encrypt certificate
- Setup auto-renewal
- Configure reverse proxy for /mallon/ path

### Step 8: Verify SSL Deployment
```bash
# Test endpoints
curl -k https://legal.satori-ai-tech.com/health
curl -k https://legal.satori-ai-tech.com/mallon/

# Check certificate
./health_check.sh legal.satori-ai-tech.com mallon
```

## Security Checklist

### SSH Security
- [ ] SSH keys generated and installed
- [ ] Password authentication disabled
- [ ] SSH config created for easy connection
- [ ] Can connect with `ssh tm-legal`

### System Security
- [ ] TM runs as dedicated 'tm' user
- [ ] Proper file permissions set
- [ ] Systemd service configured with security settings
- [ ] Environment variables secured

### SSL Security
- [ ] Let's Encrypt certificate installed
- [ ] Auto-renewal configured
- [ ] Security headers enabled
- [ ] HTTPS redirect working

## Post-Deployment Tasks

### Service Management
```bash
# Service status
sudo systemctl status tm-dashboard nginx

# Restart services
sudo systemctl restart tm-dashboard
sudo systemctl reload nginx

# View logs
journalctl -u tm-dashboard -f
journalctl -u nginx -f
```

### Monitoring
```bash
# Health check
./health_check.sh

# SSL certificate status
sudo certbot certificates

# System resources
free -h
df -h
```

### Create Master Snapshot
Once everything is working:
1. Login to Linode dashboard
2. Create snapshot of VPS
3. Name: "TM-Legal-SSL-Master-v1.9"
4. Use for cloning new client instances

## Troubleshooting

### SSH Issues
```bash
# Debug SSH connection
ssh -v tm-legal

# Check SSH service
sudo systemctl status sshd
```

### Service Issues
```bash
# Check TM service
sudo systemctl status tm-dashboard
journalctl -u tm-dashboard --no-pager

# Check file permissions
ls -la /opt/tm/
sudo chown -R tm:tm /opt/tm/
```

### SSL Issues
```bash
# Test nginx config
sudo nginx -t

# Check certificate
sudo certbot certificates
openssl x509 -in /etc/letsencrypt/live/legal.satori-ai-tech.com/cert.pem -text -noout
```

## File Locations After Migration

```
/opt/tm/                          # TM application root
├── .env                          # Environment variables
├── dashboard/                    # FastAPI application
├── tiger/                        # Document analysis
├── monkey/                       # Document generation
├── shared-schema/               # Common models
├── outputs/                     # Generated documents
├── test-data/                   # Case files
├── logs/                        # Application logs
└── config/                      # Configuration files

/etc/systemd/system/
└── tm-dashboard.service         # Service definition

/etc/nginx/sites-available/
└── tm-legal                     # Nginx configuration
```

## Success Criteria

### Phase 1 Complete When:
- [x] SSH key authentication working
- [x] Can connect with `ssh tm-legal`
- [x] Password authentication disabled
- [x] TM migrated to `/opt/tm/`
- [x] TM service starts successfully

### Phase 2 Complete When:
- [x] SSL certificate installed
- [x] `https://legal.satori-ai-tech.com/mallon/` loads
- [x] Auto-renewal configured
- [x] Health check passes
- [x] Ready for snapshot creation

---

**Next Step**: Run the SSH setup script and begin the secure deployment process.
