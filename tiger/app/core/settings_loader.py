"""
Settings Loader for Tiger Service
Loads firm-level configuration from dashboard settings
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "firm": {
        "name": "Law Firm Name",
        "address": "123 Legal Street\nCity, State 12345",
        "phone": "(555) 123-4567",
        "email": "contact@lawfirm.com"
    },
    "document": {
        "default_court": "UNITED STATES DISTRICT COURT",
        "default_district": "EASTERN DISTRICT OF NEW YORK"
    },
    "system": {
        "auto_save": True,
        "data_retention": 90
    }
}

class SettingsLoader:
    """Load and manage dashboard settings for Tiger service"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize settings loader
        
        Args:
            project_root: Path to TM project root. If None, auto-detects.
        """
        self.logger = logging.getLogger(__name__)
        
        if project_root is None:
            # Auto-detect project root from current file location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Navigate up from tiger/app/core/ to TM/
            self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        else:
            self.project_root = project_root
            
        self.settings_file = os.path.join(
            self.project_root, 
            "dashboard", 
            "config", 
            "settings.json"
        )
        
        self.logger.info(f"Settings loader initialized. Settings file: {self.settings_file}")
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from dashboard config file
        
        Returns:
            Dictionary containing firm and system settings
        """
        if not os.path.exists(self.settings_file):
            self.logger.warning(f"Settings file not found at {self.settings_file}. Using defaults.")
            return DEFAULT_SETTINGS.copy()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Validate and merge with defaults
            merged_settings = self._merge_with_defaults(settings)
            
            self.logger.info(f"Settings loaded successfully from {self.settings_file}")
            return merged_settings
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in settings file: {str(e)}. Using defaults.")
            return DEFAULT_SETTINGS.copy()
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}. Using defaults.")
            return DEFAULT_SETTINGS.copy()
    
    def get_firm_info(self) -> Dict[str, str]:
        """
        Get firm information for attorney signature block
        
        Returns:
            Dictionary containing firm name, address, phone, email
        """
        settings = self.load_settings()
        return settings.get('firm', DEFAULT_SETTINGS['firm']).copy()
    
    def get_document_defaults(self) -> Dict[str, str]:
        """
        Get document generation defaults
        
        Returns:
            Dictionary containing default court and district
        """
        settings = self.load_settings()
        return settings.get('document', DEFAULT_SETTINGS['document']).copy()
    
    def _merge_with_defaults(self, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user settings with defaults to ensure all required fields exist
        
        Args:
            user_settings: Settings loaded from file
            
        Returns:
            Complete settings dictionary with defaults for missing fields
        """
        merged = DEFAULT_SETTINGS.copy()
        
        # Deep merge for nested dictionaries
        for section_key, section_value in user_settings.items():
            if section_key in merged and isinstance(section_value, dict):
                merged[section_key].update(section_value)
            else:
                merged[section_key] = section_value
        
        return merged
    
    def _parse_address(self, address_string: str) -> Dict[str, str]:
        """
        Parse address string into components for structured data
        
        Args:
            address_string: Multi-line address string
            
        Returns:
            Dictionary with street, city, state, zip components
        """
        if not address_string:
            return {
                "street": "",
                "city": "",
                "state": "",
                "zip": "",
                "full": ""
            }
        
        lines = [line.strip() for line in address_string.strip().split('\n') if line.strip()]
        
        if not lines:
            return {
                "street": "",
                "city": "",
                "state": "",
                "zip": "",
                "full": address_string
            }
        
        # Simple parsing logic
        if len(lines) == 1:
            # Single line address
            return {
                "street": "",
                "city": "",
                "state": "",
                "zip": "",
                "full": lines[0]
            }
        
        # Multi-line address
        street = lines[0] if len(lines) > 1 else ""
        last_line = lines[-1] if lines else ""
        
        # Try to parse city, state, zip from last line
        import re
        match = re.search(r'(.*?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)', last_line)
        
        if match:
            city = match.group(1).strip()
            state = match.group(2).strip()
            zip_code = match.group(3).strip()
        else:
            # Fallback if parsing fails
            city = last_line
            state = ""
            zip_code = ""
        
        return {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code,
            "full": address_string
        }

# Convenience function for external use
def load_firm_settings(project_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load firm settings
    
    Args:
        project_root: Path to TM project root
        
    Returns:
        Dictionary containing firm settings
    """
    loader = SettingsLoader(project_root)
    return loader.get_firm_info()

def load_document_defaults(project_root: Optional[str] = None) -> Dict[str, str]:
    """
    Convenience function to load document defaults
    
    Args:
        project_root: Path to TM project root
        
    Returns:
        Dictionary containing document defaults
    """
    loader = SettingsLoader(project_root)
    return loader.get_document_defaults()