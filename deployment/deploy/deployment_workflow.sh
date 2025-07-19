# 1. Create client-specific configuration
cp legal.config.template.json clients/lawfirm-abc/legal.config.json
# Edit with firm-specific values

# 2. Run deployment configuration
python3 deploy_configure.py clients/lawfirm-abc/legal.config.json

# 3. Clone Linode instance
# 4. Upload configured TM to new instance
# 5. Install systemd services and nginx config
sudo cp deploy/tm-dashboard.service /etc/systemd/system/
sudo cp deploy/nginx.conf /etc/nginx/sites-available/tm-lawfirm-abc
sudo systemctl enable tm-dashboard
sudo systemctl start tm-dashboard