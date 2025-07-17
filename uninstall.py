#!/usr/bin/env python3
"""
TM iSync Adapter Uninstallation Script

This script completely removes the TM iCloud sync adapter from macOS.
It handles service unregistration, file cleanup, and directory removal.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List

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


class UninstallationError(Exception):
    """Custom exception for uninstallation errors"""
    pass


class TMiSyncUninstaller:
    """Main uninstaller class for TM iSync Adapter"""
    
    def __init__(self, preserve_logs: bool = False):
        """Initialize uninstaller"""
        self.preserve_logs = preserve_logs
        self.service_file = SERVICE_DIR / f"{SERVICE_NAME}.plist"
        self.binary_path = INSTALL_DIR / APP_NAME
        self.config_path = INSTALL_DIR / "config.json"
        
        # Files and directories to remove
        self.files_to_remove = [
            self.binary_path,
            self.config_path,
            INSTALL_DIR / "README.md",
            INSTALL_DIR / "service.plist",
            self.service_file
        ]
        
        if not preserve_logs:
            self.files_to_remove.extend([
                LOG_DIR / "install.log",
                LOG_DIR / "adapter.log",
                LOG_DIR / "adapter.error.log"
            ])
    
    def check_service_status(self) -> bool:
        """Check if service is currently running"""
        try:
            result = subprocess.run(
                ['launchctl', 'list', SERVICE_NAME],
                capture_output=True, text=True, check=True
            )
            logger.info("Service is currently loaded")
            return True
        except subprocess.CalledProcessError:
            logger.info("Service is not loaded")
            return False
    
    def stop_service(self) -> bool:
        """Stop the running service"""
        logger.info("Stopping service...")
        
        try:
            # Stop the service
            result = subprocess.run(
                ['launchctl', 'stop', SERVICE_NAME],
                capture_output=True, text=True, check=True
            )
            logger.info("Service stopped successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not stop service (may not be running): {e.stderr}")
            return False
    
    def unload_service(self) -> bool:
        """Unload service from launchd"""
        logger.info("Unloading service from launchd...")
        
        if not self.service_file.exists():
            logger.info("Service file not found, nothing to unload")
            return True
        
        try:
            # Unload the service
            result = subprocess.run(
                ['launchctl', 'unload', str(self.service_file)],
                capture_output=True, text=True, check=True
            )
            logger.info("Service unloaded successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not unload service: {e.stderr}")
            return False
    
    def remove_files(self) -> List[str]:
        """Remove application files and directories"""
        logger.info("Removing application files...")
        
        removed_files = []
        
        for file_path in self.files_to_remove:
            if file_path.exists():
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        removed_files.append(str(file_path))
                        logger.info(f"Removed file: {file_path}")
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        removed_files.append(str(file_path))
                        logger.info(f"Removed directory: {file_path}")
                except OSError as e:
                    logger.error(f"Could not remove {file_path}: {e}")
        
        return removed_files
    
    def remove_directories(self) -> List[str]:
        """Remove empty directories"""
        logger.info("Removing empty directories...")
        
        removed_dirs = []
        directories_to_check = [LOG_DIR, INSTALL_DIR]
        
        for directory in directories_to_check:
            if directory.exists() and directory.is_dir():
                try:
                    # Only remove if directory is empty or contains only hidden files
                    contents = list(directory.iterdir())
                    visible_contents = [f for f in contents if not f.name.startswith('.')]
                    
                    if not visible_contents:
                        if contents:  # Remove hidden files first
                            for hidden_file in contents:
                                if hidden_file.name.startswith('.'):
                                    hidden_file.unlink()
                                    logger.info(f"Removed hidden file: {hidden_file}")
                        
                        directory.rmdir()
                        removed_dirs.append(str(directory))
                        logger.info(f"Removed empty directory: {directory}")
                    else:
                        logger.info(f"Directory not empty, preserving: {directory}")
                except OSError as e:
                    logger.warning(f"Could not remove directory {directory}: {e}")
        
        return removed_dirs
    
    def verify_removal(self) -> bool:
        """Verify that all components have been removed"""
        logger.info("Verifying removal...")
        
        remaining_items = []
        
        # Check for remaining files
        for file_path in self.files_to_remove:
            if file_path.exists():
                remaining_items.append(str(file_path))
        
        # Check if service is still loaded
        if self.check_service_status():
            remaining_items.append(f"Service {SERVICE_NAME} still loaded")
        
        if remaining_items:
            logger.warning(f"Some items could not be removed: {remaining_items}")
            return False
        else:
            logger.info("All components successfully removed")
            return True
    
    def create_uninstall_log(self, removed_files: List[str], removed_dirs: List[str]):
        """Create a log of what was removed"""
        try:
            # Create log in user's Documents directory
            documents_dir = Path.home() / "Documents"
            log_file = documents_dir / "tm-isync-uninstall.log"
            
            with open(log_file, 'w') as f:
                f.write(f"TM iSync Adapter Uninstallation Log\n")
                f.write(f"{'=' * 50}\n")
                f.write(f"Uninstalled on: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
                f.write(f"Service name: {SERVICE_NAME}\n\n")
                
                if removed_files:
                    f.write("Removed files:\n")
                    for file_path in removed_files:
                        f.write(f"  - {file_path}\n")
                    f.write("\n")
                
                if removed_dirs:
                    f.write("Removed directories:\n")
                    for dir_path in removed_dirs:
                        f.write(f"  - {dir_path}\n")
                    f.write("\n")
                
                f.write("Uninstallation completed successfully.\n")
            
            logger.info(f"Uninstall log created: {log_file}")
        except Exception as e:
            logger.warning(f"Could not create uninstall log: {e}")
    
    def uninstall(self) -> bool:
        """Perform complete uninstallation"""
        logger.info("Starting TM iSync Adapter uninstallation...")
        
        try:
            # Check if service is installed
            if not self.service_file.exists() and not self.binary_path.exists():
                logger.info("TM iSync Adapter is not installed")
                return True
            
            # Uninstallation steps
            self.stop_service()
            self.unload_service()
            removed_files = self.remove_files()
            removed_dirs = self.remove_directories()
            
            # Verify removal
            if self.verify_removal():
                logger.info("Uninstallation completed successfully!")
                self.create_uninstall_log(removed_files, removed_dirs)
                self._print_success_message()
                return True
            else:
                logger.error("Uninstallation verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error during uninstallation: {e}")
            return False
    
    def _print_success_message(self):
        """Print success message with summary"""
        print("\n" + "="*60)
        print("  TM iSync Adapter Uninstallation Complete!")
        print("="*60)
        print("All components have been successfully removed:")
        print("- Service unloaded from launchd")
        print("- Application files deleted")
        print("- Configuration files removed")
        if not self.preserve_logs:
            print("- Log files deleted")
        else:
            print("- Log files preserved")
        print("\nThe adapter is now completely uninstalled from your system.")
        print("="*60)


def main():
    """Main uninstallation function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Uninstall TM iSync Adapter from macOS'
    )
    parser.add_argument(
        '--preserve-logs',
        action='store_true',
        help='Keep log files during uninstallation'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force uninstallation without confirmation'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Check if running as root
    if os.geteuid() == 0:
        logger.error("Do not run this uninstaller as root/sudo")
        sys.exit(1)
    
    # Confirmation prompt unless forced
    if not args.force:
        print("This will completely remove TM iSync Adapter from your system.")
        response = input("Are you sure you want to continue? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("Uninstallation cancelled.")
            sys.exit(0)
    
    # Run uninstallation
    uninstaller = TMiSyncUninstaller(preserve_logs=args.preserve_logs)
    success = uninstaller.uninstall()
    
    if success:
        sys.exit(0)
    else:
        logger.error("Uninstallation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()