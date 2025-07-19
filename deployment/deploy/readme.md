The Linode clone approach is actually a brilliant solution for your current TM deployment situation, especially given your preference for speed and simplicity over dependencies and bloat.
Current TM Deployment Architecture
Based on the documentation, your current Linode setup appears to be:

Linode $24 VPS
├── Ubuntu/Debian bare metal
├── Python 3.8+ virtual environments
├── systemd services for TM components
├── nginx reverse proxy
├── ML models (Docling) pre-installed
└── Complete file I/O structure intact

Why Linode Clone is Perfect for TM
Advantages of cloning vs. containerization:

Zero Refactoring Required - TM's heavy file I/O system stays exactly as-is
Complete System State - Everything preserved:

Python virtual environments with all dependencies
Pre-trained ML models (Docling, etc.)
systemd service configurations
nginx routing configuration
File permission structures
Database schemas and data


Instant Deployment - Clone creates identical working system in minutes
No Container Overhead - Bare metal performance maintained
Simple Scaling - Need another instance? Clone and update config


No Docker bloat - Bare metal Python on systemd
No React complexity - Your HTML/Tailwind/JS frontend preserved
No dependency hell - Everything pre-baked into the clone
Simple systemd management - Fits your Sensei server patterns
Cost effective - $24/month per client vs. complex orchestration


Benefits of This Approach

Zero Runtime Overhead - All branding hard-coded into HTML/JS
Perfect Performance - No JSON loading or template rendering at runtime
Simple Deployment - One script configures everything
Version Control Friendly - Template sources stay clean
Linode Clone Compatible - Configured instance clones perfectly

Integration Points

Dashboard Settings Page - Pre-populated from legal.config.json
Document Templates - Firm information embedded in Monkey templates
Login Screen - Custom branding and messaging
Nginx Routing - Instance-specific domain configuration
Systemd Services - Custom service names and ports

This gives you the "deploy and forget" simplicity you want while maintaining the performance characteristics you need. Each cloned instance becomes a completely self-contained, firm-branded TM deployment.

Deployment Process Would Be
# 1. Linode UI: Clone existing TM instance
# 2. Boot new instance
# 3. Update instance-specific configs:
#    - nginx server_name
#    - systemd service ports (if needed)
#    - TM dashboard settings (firm info)
# 4. Start services
sudo systemctl start tm-dashboard
sudo systemctl start tm-tiger  
sudo systemctl start tm-monkey
sudo systemctl restart nginx


Excellent plan! Let's design a legal.config.json structure that supports deployment-time configuration injection for optimal performance. Since you prefer hard-coded values for performance and this includes frontend branding, a build-time template substitution approach using Jinja2 makes perfect sense.


Proposed legal.config.json Structure


Template Substitution Strategy
Since performance is key and you want hard-coded values, I recommend a deployment-time Jinja2 substitution approach: deploy_configure.py


Template Structure for Performance
Create a templates/deployment/ directory with Jinja2 templates:
templates/deployment/dashboard_template.html