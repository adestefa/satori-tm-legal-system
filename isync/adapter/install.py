#!/usr/bin/env python3
"""
TM iSync Adapter Installation Script

This script installs the TM iCloud sync adapter as a macOS service.
It handles directory creation, file copying, service registration, and startup.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration
SERVICE_NAME = "com.tm.isync.adapter"
APP_NAME = "tm-isync-adapter"
INSTALL_DIR = Path.home() / "Library" / "TM-iCloud-Sync"
SERVICE_DIR = Path.home() / "Library" / "LaunchAgents"
LOG_DIR = INSTALL_DIR / "logs"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class InstallationError(Exception):
    """Custom exception for installation errors"""
    pass


class TMiSyncInstaller:
    """Main installer class for TM iSync Adapter"""
    
    def __init__(self, package_dir: Path = None):
        """Initialize installer with package directory"""
        self.package_dir = package_dir or Path.cwd()
        self.service_file = SERVICE_DIR / f"{SERVICE_NAME}.plist"
        self.binary_path = INSTALL_DIR / APP_NAME
        self.config_path = INSTALL_DIR / "config.json"
        self.install_log = LOG_DIR / "install.log"
        
        # Add file logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup file logging for installation"""
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.install_log)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    def check_requirements(self) -> bool:
        """Check system requirements and package contents"""
        logger.info("Checking system requirements...")
        
        # Check macOS version
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            logger.info(f"macOS version: {version}")
        except subprocess.CalledProcessError:
            logger.warning("Could not determine macOS version")
        
        # Check required files in package
        required_files = [APP_NAME, "config.json", "service.plist.template"]
        missing_files = []
        
        for file_name in required_files:
            file_path = self.package_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            raise InstallationError(f"Missing required files: {', '.join(missing_files)}")
        
        # Check if binary is executable
        binary_source = self.package_dir / APP_NAME
        if not os.access(binary_source, os.X_OK):
            logger.warning(f"Binary {APP_NAME} is not executable, fixing permissions...")
            try:
                os.chmod(binary_source, 0o755)
            except OSError as e:
                raise InstallationError(f"Could not make binary executable: {e}")
        
        # Check if service is already installed
        if self.service_file.exists():
            logger.warning(f"Service {SERVICE_NAME} is already installed")
            return False
        
        logger.info("System requirements check passed")
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("Creating installation directories...")
        
        directories = [INSTALL_DIR, LOG_DIR, SERVICE_DIR]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except OSError as e:
                raise InstallationError(f"Could not create directory {directory}: {e}")
    
    def copy_files(self):
        """Copy application files to installation directory"""
        logger.info("Copying application files...")
        
        # Copy binary
        binary_source = self.package_dir / APP_NAME
        try:
            shutil.copy2(binary_source, self.binary_path)
            os.chmod(self.binary_path, 0o755)
            logger.info(f"Copied binary to: {self.binary_path}")
        except (shutil.Error, OSError) as e:
            raise InstallationError(f"Could not copy binary: {e}")
        
        # Copy and validate configuration
        config_source = self.package_dir / "config.json"
        try:
            with open(config_source, 'r') as f:
                config_data = json.load(f)
            
            # Validate configuration
            self._validate_config(config_data)
            
            # Copy configuration
            shutil.copy2(config_source, self.config_path)
            logger.info(f"Copied configuration to: {self.config_path}")
        except (json.JSONDecodeError, KeyError) as e:
            raise InstallationError(f"Invalid configuration file: {e}")
        except (shutil.Error, OSError) as e:
            raise InstallationError(f"Could not copy configuration: {e}")
        
        # Copy installation documentation
        readme_source = self.package_dir / "README.md"
        if readme_source.exists():
            try:
                shutil.copy2(readme_source, INSTALL_DIR / "README.md")
                logger.info("Copied README.md")
            except (shutil.Error, OSError) as e:
                logger.warning(f"Could not copy README: {e}")
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration structure"""
        required_keys = ['icloud_parent_folder', 'local_tm_path', 'sync_interval']
        
        for key in required_keys:
            if key not in config:
                raise InstallationError(f"Missing required configuration key: {key}")
        
        # Validate sync interval
        if not isinstance(config['sync_interval'], int) or config['sync_interval'] < 1:
            raise InstallationError("sync_interval must be a positive integer")
        
        # Validate local path (create if it doesn't exist)
        local_path = Path(config['local_tm_path'])
        if not local_path.exists():
            try:
                local_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created local TM path: {local_path}")
            except OSError as e:
                raise InstallationError(f"Could not create local TM path: {e}")
    
    def create_service(self):
        """Create macOS launchd service"""
        logger.info("Creating macOS service...")
        
        # Load service template
        template_path = self.package_dir / "service.plist.template"
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
        except OSError as e:
            raise InstallationError(f"Could not read service template: {e}")
        
        # Replace placeholders
        import getpass
        service_content = template_content.format(
            service_name=SERVICE_NAME,
            binary_path=self.binary_path,
            config_path=self.config_path,
            log_path=LOG_DIR / "adapter.log",
            error_log_path=LOG_DIR / "adapter.error.log",
            install_dir=INSTALL_DIR,
            home_dir=Path.home(),
            user_name=getpass.getuser()
        )
        
        # Write service file
        try:
            with open(self.service_file, 'w') as f:
                f.write(service_content)
            logger.info(f"Created service file: {self.service_file}")
        except OSError as e:
            raise InstallationError(f"Could not create service file: {e}")
    
    def register_service(self):
        """Register service with launchd"""
        logger.info("Registering service with launchd...")
        
        try:
            # Load the service
            result = subprocess.run(
                ['launchctl', 'load', str(self.service_file)],
                capture_output=True, text=True, check=True
            )
            logger.info("Service registered successfully")
        except subprocess.CalledProcessError as e:
            raise InstallationError(f"Could not register service: {e.stderr}")
    
    def start_service(self):
        """Start the service"""
        logger.info("Starting service...")
        
        try:
            # Start the service
            result = subprocess.run(
                ['launchctl', 'start', SERVICE_NAME],
                capture_output=True, text=True, check=True
            )
            logger.info("Service started successfully")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not start service immediately: {e.stderr}")
            logger.info("Service will start automatically on next login")
    
    def verify_installation(self) -> bool:
        """Verify installation was successful"""
        logger.info("Verifying installation...")
        
        # Check files exist
        files_to_check = [self.binary_path, self.config_path, self.service_file]
        for file_path in files_to_check:
            if not file_path.exists():
                logger.error(f"Missing file: {file_path}")
                return False
        
        # Check service is loaded
        try:
            result = subprocess.run(
                ['launchctl', 'list', SERVICE_NAME],
                capture_output=True, text=True, check=True
            )
            logger.info("Service is registered with launchd")
        except subprocess.CalledProcessError:
            logger.error("Service is not registered with launchd")
            return False
        
        # Test binary execution
        try:
            result = subprocess.run(
                [str(self.binary_path), '-version'],
                capture_output=True, text=True, check=True, timeout=5
            )
            logger.info(f"Binary test successful: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Binary test failed: {e}")
        
        logger.info("Installation verification completed")
        return True
    
    def install(self) -> bool:
        """Perform complete installation"""
        logger.info("Starting TM iSync Adapter installation...")
        
        try:
            # Check requirements
            if not self.check_requirements():
                logger.info("Service already installed, skipping installation")
                return True
            
            # Installation steps
            self.create_directories()
            self.copy_files()
            self.create_service()
            self.register_service()
            self.start_service()
            
            # Verify installation
            if self.verify_installation():
                logger.info("Installation completed successfully!")
                self._print_success_message()
                return True
            else:
                logger.error("Installation verification failed")
                return False
                
        except InstallationError as e:
            logger.error(f"Installation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during installation: {e}")
            return False
    
    def _print_success_message(self):
        """Print success message with next steps"""
        print("\n" + "="*60)
        print("  TM iSync Adapter Installation Successful!")
        print("="*60)
        print(f"Installation directory: {INSTALL_DIR}")
        print(f"Service name: {SERVICE_NAME}")
        print(f"Logs directory: {LOG_DIR}")
        print("\nNext steps:")
        print("1. The service will start automatically on login")
        print("2. Check service status: launchctl list com.tm.isync.adapter")
        print("3. View logs: tail -f ~/Library/TM-iCloud-Sync/logs/adapter.log")
        print("4. Configuration can be modified at:")
        print(f"   {self.config_path}")
        print("\nFor uninstallation, run: python3 uninstall.py")
        print("="*60)


def main():
    """Main installation function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Install TM iSync Adapter as macOS service'
    )
    parser.add_argument(
        '--package-dir', 
        type=Path,
        default=Path.cwd(),
        help='Directory containing installation package (default: current directory)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Check if running as root
    if os.geteuid() == 0:
        logger.error("Do not run this installer as root/sudo")
        sys.exit(1)
    
    # Verify package directory
    if not args.package_dir.exists():
        logger.error(f"Package directory does not exist: {args.package_dir}")
        sys.exit(1)
    
    # Run installation
    installer = TMiSyncInstaller(args.package_dir)
    success = installer.install()
    
    if success:
        sys.exit(0)
    else:
        logger.error("Installation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()