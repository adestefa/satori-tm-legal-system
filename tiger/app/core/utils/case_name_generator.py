"""
Case Name Generator for Tiger Engine
Generates case folder names from legal entity data
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class CaseNameGenerator:
    """
    Generates case folder names from consolidated case data
    """
    
    def __init__(self, max_name_length: int = 50):
        self.max_name_length = max_name_length
        self.logger = logging.getLogger(__name__)
    
    def generate_case_folder_name(self, consolidated_case=None, legal_entities: Dict = None, 
                                 manual_name: str = None) -> str:
        """
        Generate case folder name from various sources
        
        Args:
            consolidated_case: ConsolidatedCase object
            legal_entities: Dictionary of legal entities
            manual_name: Manually specified case name
            
        Returns:
            Case folder name in format: LastName_FirstName_YYYYMMDD
            Fallback: Unknown_Case_YYYYMMDD_HHMMSS
        """
        
        # Use manual name if provided
        if manual_name:
            return self._create_final_name(manual_name)
        
        # Extract from consolidated case
        if consolidated_case and consolidated_case.plaintiff:
            plaintiff_name = self._extract_name_from_plaintiff(consolidated_case.plaintiff)
            if plaintiff_name:
                return self._create_final_name(plaintiff_name)
        
        # Extract from legal entities
        if legal_entities:
            plaintiff_name = self._extract_name_from_legal_entities(legal_entities)
            if plaintiff_name:
                return self._create_final_name(plaintiff_name)
        
        # Fallback to timestamp-based name
        return self._create_fallback_name()
    
    def _extract_name_from_plaintiff(self, plaintiff: Dict[str, Any]) -> Optional[str]:
        """Extract name from plaintiff dictionary"""
        try:
            name = plaintiff.get('name', '')
            if name:
                return self._parse_name_to_last_first(name)
        except Exception as e:
            self.logger.warning(f"Failed to extract name from plaintiff: {e}")
        return None
    
    def _extract_name_from_legal_entities(self, legal_entities: Dict) -> Optional[str]:
        """Extract plaintiff name from legal entities data"""
        try:
            # Look for plaintiff in various possible locations
            plaintiff_sources = [
                legal_entities.get('plaintiff', {}),
                legal_entities.get('plaintiffs', []),
                legal_entities.get('parties', {}).get('plaintiffs', [])
            ]
            
            for source in plaintiff_sources:
                if isinstance(source, dict) and source.get('name'):
                    return self._parse_name_to_last_first(source['name'])
                elif isinstance(source, list) and source:
                    # Take first plaintiff if multiple
                    first_plaintiff = source[0]
                    if isinstance(first_plaintiff, dict) and first_plaintiff.get('name'):
                        return self._parse_name_to_last_first(first_plaintiff['name'])
                    elif isinstance(first_plaintiff, str):
                        return self._parse_name_to_last_first(first_plaintiff)
            
            # Fallback: look for any person names in entities
            entities = legal_entities.get('entities', {})
            if entities and 'persons' in entities:
                persons = entities['persons']
                if persons and len(persons) > 0:
                    first_person = persons[0]
                    if isinstance(first_person, dict) and first_person.get('name'):
                        return self._parse_name_to_last_first(first_person['name'])
                    elif isinstance(first_person, str):
                        return self._parse_name_to_last_first(first_person)
                        
        except Exception as e:
            self.logger.warning(f"Failed to extract name from legal entities: {e}")
        
        return None
    
    def _parse_name_to_last_first(self, full_name: str) -> str:
        """
        Parse full name into LastName_FirstName format
        
        Examples:
            "Eman Youssef" -> "Youssef_Eman"
            "John Q. Smith" -> "Smith_John"
            "Mary Jane Watson-Parker" -> "Watson-Parker_Mary"
        """
        if not full_name or not full_name.strip():
            return ""
        
        # Clean the name
        name = self._clean_name_text(full_name.strip())
        
        # Split into parts
        name_parts = name.split()
        
        if len(name_parts) == 1:
            # Single name - use as last name
            return self.sanitize_name_for_filesystem(name_parts[0])
        elif len(name_parts) == 2:
            # First Last
            first, last = name_parts
            return f"{self.sanitize_name_for_filesystem(last)}_{self.sanitize_name_for_filesystem(first)}"
        else:
            # Multiple names - first name is first, last name is last
            first = name_parts[0]
            last = name_parts[-1]
            return f"{self.sanitize_name_for_filesystem(last)}_{self.sanitize_name_for_filesystem(first)}"
    
    def _clean_name_text(self, name: str) -> str:
        """Clean name text of common legal document artifacts"""
        # Remove common titles and suffixes
        name = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|III|IV)\b\.?', '', name, flags=re.IGNORECASE)
        
        # Remove plaintiff/defendant labels
        name = re.sub(r'\b(Plaintiff|Defendant)s?\b', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def sanitize_name_for_filesystem(self, name: str) -> str:
        """
        Make name safe for file system use
        
        - Remove or replace special characters
        - Limit length
        - Ensure valid filename
        """
        if not name:
            return "Unknown"
        
        # Replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        
        # Replace spaces and other characters with underscores
        sanitized = re.sub(r'[\s\-\.]+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Ensure it's not empty
        if not sanitized:
            return "Unknown"
        
        # Limit length
        if len(sanitized) > self.max_name_length:
            sanitized = sanitized[:self.max_name_length].rstrip('_')
        
        return sanitized
    
    def _create_final_name(self, base_name: str) -> str:
        """Create final case folder name with date stamp"""
        today = datetime.now().strftime("%Y%m%d")
        sanitized_name = self.sanitize_name_for_filesystem(base_name)
        
        # If the base_name already has date format, don't add another
        if re.search(r'_\d{8}$', sanitized_name):
            return sanitized_name
        
        return f"{sanitized_name}_{today}"
    
    def _create_fallback_name(self) -> str:
        """Create fallback name when no plaintiff name can be extracted"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"Unknown_Case_{timestamp}"
    
    def extract_case_names_from_batch(self, extraction_results: List) -> Dict[str, List]:
        """
        Group extraction results by detected case names
        
        Args:
            extraction_results: List of extraction results
            
        Returns:
            Dictionary mapping case names to lists of results
        """
        case_groups = {}
        
        for result in extraction_results:
            # Try to extract case name from this result
            if hasattr(result, 'legal_entities') and result.legal_entities:
                case_name = self.generate_case_folder_name(legal_entities=result.legal_entities)
            else:
                case_name = self._create_fallback_name()
            
            if case_name not in case_groups:
                case_groups[case_name] = []
            
            case_groups[case_name].append(result)
        
        return case_groups
    
    def validate_case_name(self, case_name: str) -> bool:
        """
        Validate that a case name is suitable for use as a folder name
        
        Args:
            case_name: Proposed case name
            
        Returns:
            True if valid, False otherwise
        """
        if not case_name or not case_name.strip():
            return False
        
        # Check for problematic characters
        if re.search(r'[<>:"/\\|?*]', case_name):
            return False
        
        # Check length
        if len(case_name) > self.max_name_length + 10:  # Allow for date suffix
            return False
        
        # Check if it would create a valid directory
        try:
            Path(case_name)
            return True
        except (OSError, ValueError):
            return False