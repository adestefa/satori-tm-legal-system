# Fresh Linode TM Deployment Guide

## Strategy: Clean Deployment Approach

Instead of migrating the existing production TM instance, we're deploying to a fresh Linode VPS. This approach:

✅ **Preserves current production** - Client access uninterrupted  
✅ **Clean deployment** - No migration complexity or legacy issues  
✅ **Perfect testing environment** - Validate SSL and tenant setup  
✅ **Master template creation** - Ready for client cloning  

## Current Production Status
- **Production TM**: 198.74.59.11 (remains untouched)
- **Client access**: Continues working normally
- **New deployment**: Fresh VPS with SSL and tenant structure

## Deployment Steps

### Step 1: Create Fresh Linode VPS
1. **Linode Dashboard** → Create new VPS
   - **Plan**: Nanode 4GB ($24/month, 2 CPU, 4GB RAM)
   - **Image**: Ubuntu 22.04 LTS
   - **Region**: Choose closest to your location
   - **Root Password**: Create new secure password
   - **Note the IP address**

### Step 2: Initial VPS Setup
```bash
cd /Users/corelogic/satori-dev/TM/deployment/deploy/service_config
chmod +x setup_fresh_vps.sh
./setup_fresh_vps.sh
```

**You'll need to manually update the script with:**
- Your new VPS IP address
- Your new VPS root password

### Step 3: SSH Key Installation
Follow the script output to:
1. Install SSH public key on new VPS
2. Test key-based authentication
3. Disable password authentication

### Step 4: DNS Preparation
**Before SSL deployment**, update your DNS:
```
legal.satori-ai-tech.com → new-vps-ip
```

### Step 5: Complete Deployment
```bash
./deploy_fresh_complete.sh
```

This automatically:
- ✅ Installs all system dependencies
- ✅ Clones TM repository to `/opt/tm/`
- ✅ Installs Tiger, Monkey, and Dashboard services
- ✅ Configures systemd service
- ✅ Sets up SSL with Let's Encrypt
- ✅ Configures nginx reverse proxy
- ✅ Tests all endpoints

## Repository Considerations

### If TM is in Private GitHub Repo
You'll need to setup SSH keys for git access:
```bash
# On the VPS
ssh-keygen -t ed25519 -f ~/.ssh/github_tm
# Add public key to GitHub deploy keys
```

### If TM is Not in Git Yet
You can upload the TM files manually:
```bash
# From your Mac
cd /Users/corelogic/satori-dev
tar -czf TM.tar.gz TM/
scp TM.tar.gz tm-fresh:/opt/
ssh tm-fresh "cd /opt && tar -xzf TM.tar.gz && chown -R tm:tm TM/"
```

## Advantages of Fresh Deployment

### Production Safety
- **Zero downtime** for current client
- **No migration risks** or data corruption
- **Rollback capability** if issues arise
- **Side-by-side testing** before switchover

### Clean Architecture
- **Proper file structure** from the start
- **Correct permissions** and ownership
- **Standard directories** (`/opt/tm/`)
- **Systemd integration** from deployment

### SSL Benefits
- **Native SSL setup** from day one
- **Tenant path structure** properly configured
- **Auto-renewal** working correctly
- **Security headers** properly implemented

## Post-Deployment Tasks

### Testing Checklist
- [ ] `https://legal.satori-ai-tech.com/mallon/` loads
- [ ] TM dashboard fully functional
- [ ] File upload and processing works
- [ ] Document generation works
- [ ] SSL certificate valid and auto-renewing

### Client Migration
Once testing is complete:
1. **Notify client** of brief maintenance window
2. **Update DNS** to point to new VPS
3. **Test client workflow**
4. **Decommission old VPS** after verification

### Master Snapshot
Create Linode snapshot of working SSL deployment:
- **Name**: "TM-Legal-SSL-Master-v1.9"
- **Use for**: All future client deployments

## Cost Impact
- **Development**: +$24/month during setup and testing
- **Production**: $24/month per client (same as planned)
- **Migration**: One-time DNS change (5-60 minutes)

---

**Recommendation**: Proceed with fresh deployment approach for clean, reliable SSL setup.
