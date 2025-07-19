#!/usr/bin/env python3
"""
TM Deployment Configuration Script
Injects client-specific branding into TM application files
"""

import json
import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime

class TMDeploymentConfigurator:
    def __init__(self, config_file="legal.config.json", template_dir="templates/deployment"):
        self.config_file = config_file
        self.template_dir = template_dir
        self.config = self.load_config()
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
    def load_config(self):
        """Load configuration from legal.config.json"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def configure_dashboard_branding(self):
        """Update dashboard HTML templates with firm branding"""
        
        # Main dashboard template
        dashboard_template = self.jinja_env.get_template("dashboard.html.j2")
        dashboard_output = dashboard_template.render(**self.config)
        
        with open("dashboard/static/themes/light/index.html", "w") as f:
            f.write(dashboard_output)
            
        # Login page template
        login_template = self.jinja_env.get_template("login.html.j2") 
        login_output = login_template.render(**self.config)
        
        with open("dashboard/static/login/index.html", "w") as f:
            f.write(login_output)
            
        print("✅ Dashboard branding configured")
    
    def configure_firm_settings(self):
        """Update dashboard settings with firm information"""
        
        settings_data = {
            "name": self.config["firm"]["name"],
            "address": f"{self.config['firm']['address']['street']}\n{self.config['firm']['address']['city']}, {self.config['firm']['address']['state']} {self.config['firm']['address']['zip_code']}",
            "phone": self.config["firm"]["contact"]["phone"],
            "email": self.config["firm"]["contact"]["email"]
        }
        
        # Create settings directory if it doesn't exist
        os.makedirs("dashboard/config", exist_ok=True)
        
        with open("dashboard/config/settings.json", "w") as f:
            json.dump(settings_data, f, indent=2)
            
        print("✅ Firm settings configured")
    
    def configure_document_templates(self):
        """Update legal document templates with firm information"""
        
        # FCRA Complaint template
        complaint_template = self.jinja_env.get_template("complaint_fcra.html.j2")
        complaint_output = complaint_template.render(**self.config)
        
        with open("monkey/templates/html/fcra/complaint.html", "w") as f:
            f.write(complaint_output)
            
        print("✅ Document templates configured")
    
    def copy_branding_assets(self):
        """Copy client-specific branding assets"""
        
        client_id = self.config["deployment"]["instance_id"].split("-")[1]
        source_dir = f"branding/{client_id}"
        target_dir = f"dashboard/static/branding/{client_id}"
        
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
            print(f"✅ Branding assets copied for {client_id}")
        else:
            print(f"⚠️  No branding assets found for {client_id}")
    
    def configure_nginx(self):
        """Generate nginx configuration for this instance"""
        
        nginx_template = self.jinja_env.get_template("nginx.conf.j2")
        nginx_output = nginx_template.render(**self.config)
        
        with open("deploy/nginx.conf", "w") as f:
            f.write(nginx_output)
            
        print("✅ Nginx configuration generated")
    
    def configure_systemd(self):
        """Generate systemd service files"""
        
        systemd_template = self.jinja_env.get_template("tm-dashboard.service.j2")
        systemd_output = systemd_template.render(**self.config)
        
        with open("deploy/tm-dashboard.service", "w") as f:
            f.write(systemd_output)
            
        print("✅ Systemd service files generated")
    
    def deploy(self):
        """Run complete deployment configuration"""
        
        print(f"🚀 Configuring TM for {self.config['firm']['name']}")
        print(f"📅 Deployment: {datetime.now().isoformat()}")
        
        self.configure_firm_settings()
        self.configure_dashboard_branding() 
        self.configure_document_templates()
        self.copy_branding_assets()
        self.configure_nginx()
        self.configure_systemd()
        
        print("✅ TM deployment configuration complete!")
        print(f"🌐 Instance URL: {self.config['application']['instance_url']}")

if __name__ == "__main__":
    import sys
    
    config_file = sys.argv[1] if len(sys.argv) > 1 else "legal.config.json"
    
    configurator = TMDeploymentConfigurator(config_file)
    configurator.deploy()