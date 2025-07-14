"""
Template Engine for Beaver Document Builder
Handles Jinja2 template loading and rendering for legal documents
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

class TemplateEngine:
    """Jinja2-based template engine for legal document generation"""
    
    def __init__(self, template_dir: str = None):
        """
        Initialize template engine
        
        Args:
            template_dir: Path to template directory (defaults to beaver/templates)
        """
        if template_dir is None:
            template_dir = str(Path(__file__).parent.parent / "templates")
            
        self.template_dir = Path(template_dir)
        self.logger = logging.getLogger(__name__)
        
        # Setup Jinja2 environment
        self.loader = FileSystemLoader(str(self.template_dir))
        self.env = Environment(
            loader=self.loader,
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self._register_custom_filters()
        
        self.logger.info(f"Template engine initialized with directory: {self.template_dir}")
    
    def _register_custom_filters(self):
        """Register custom Jinja2 filters for legal document formatting"""
        
        def upper_legal(text: str) -> str:
            """Convert to uppercase for legal document headers"""
            if not text:
                return ""
            return str(text).upper()
        
        def format_case_number(case_number: str) -> str:
            """Format case number consistently"""
            if not case_number:
                return ""
            # Ensure proper case number format (X:YY-cv-NNNNN)
            return str(case_number).strip()
        
        def format_court_district(district: str) -> str:
            """Format court district names according to federal court standards"""
            if not district or district.strip() == "":
                return "EASTERN DISTRICT OF NEW YORK"  # Default
            
            # Normalize input
            normalized = district.strip().upper()
            
            # Handle common variations and ensure "OF" is included
            district_patterns = {
                # New York districts
                "EASTERN DISTRICT NEW YORK": "EASTERN DISTRICT OF NEW YORK",
                "EASTERN DISTRICT OF NEW YORK": "EASTERN DISTRICT OF NEW YORK", 
                "SOUTHERN DISTRICT NEW YORK": "SOUTHERN DISTRICT OF NEW YORK",
                "SOUTHERN DISTRICT OF NEW YORK": "SOUTHERN DISTRICT OF NEW YORK",
                "WESTERN DISTRICT NEW YORK": "WESTERN DISTRICT OF NEW YORK",
                "WESTERN DISTRICT OF NEW YORK": "WESTERN DISTRICT OF NEW YORK", 
                "NORTHERN DISTRICT NEW YORK": "NORTHERN DISTRICT OF NEW YORK",
                "NORTHERN DISTRICT OF NEW YORK": "NORTHERN DISTRICT OF NEW YORK",
                
                # Common abbreviations
                "EDNY": "EASTERN DISTRICT OF NEW YORK",
                "SDNY": "SOUTHERN DISTRICT OF NEW YORK", 
                "WDNY": "WESTERN DISTRICT OF NEW YORK",
                "NDNY": "NORTHERN DISTRICT OF NEW YORK"
            }
            
            # Check exact matches first
            if normalized in district_patterns:
                return district_patterns[normalized]
            
            # Pattern-based correction for "[DIRECTION] DISTRICT [STATE]" format
            import re
            pattern = r'^(EASTERN|SOUTHERN|WESTERN|NORTHERN)\s+DISTRICT\s+(NEW\s+YORK|NY)$'
            match = re.match(pattern, normalized)
            if match:
                direction = match.group(1)
                return f"{direction} DISTRICT OF NEW YORK"
            
            # Fallback: if contains "DISTRICT" but no "OF", try to add it
            if "DISTRICT" in normalized and "OF" not in normalized:
                # Simple pattern: "[DIRECTION] DISTRICT [STATE]" → "[DIRECTION] DISTRICT OF [STATE]"
                parts = normalized.split()
                if len(parts) >= 3 and "DISTRICT" in parts:
                    district_idx = parts.index("DISTRICT")
                    if district_idx < len(parts) - 1:  # There's something after "DISTRICT"
                        # Insert "OF" after "DISTRICT"
                        parts.insert(district_idx + 1, "OF")
                        return " ".join(parts)
            
            # Final fallback: return as-is if no pattern matches
            return normalized
        
        def format_address(address) -> str:
            """Format address dict or string into legal document format"""
            if not address:
                return ""
            
            # Handle string input
            if isinstance(address, str):
                return address.strip()
            
            # Handle dict input
            if isinstance(address, dict):
                parts = []
                if address.get('street'):
                    parts.append(address['street'])
                if address.get('city_state_zip'):
                    parts.append(address['city_state_zip'])
                elif address.get('city') and address.get('state'):
                    city_state = f"{address['city']}, {address['state']}"
                    if address.get('zip'):
                        city_state += f" {address['zip']}"
                    parts.append(city_state)
                    
                return '\n'.join(parts)
            
            # Fallback for other types
            return str(address)
        
        def format_date(date_str: str, format_type: str = 'legal') -> str:
            """Format dates for legal documents"""
            if not date_str:
                return datetime.now().strftime('%B %d, %Y')
            
            try:
                if isinstance(date_str, str):
                    # Simple date parsing without dateutil dependency
                    import re
                    # Try to parse "Month DD, YYYY" format
                    if re.match(r'[A-Z][a-z]+ \d{1,2}, \d{4}', date_str):
                        return date_str  # Already in correct format
                    # Try other common formats
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d') if '-' in date_str else datetime.now()
                else:
                    date_obj = date_str
                    
                if format_type == 'legal':
                    return date_obj.strftime('%B %d, %Y')
                elif format_type == 'short':
                    return date_obj.strftime('%m/%d/%Y')
                else:
                    return date_obj.strftime('%B %d, %Y')
            except:
                return datetime.now().strftime('%B %d, %Y')
        
        def legal_list(items: List[str], conjunction: str = 'and') -> str:
            """Format lists for legal documents (e.g., 'A, B, and C')"""
            if not items:
                return ""
            
            items = [str(item).strip() for item in items if item]
            
            if len(items) == 1:
                return items[0]
            elif len(items) == 2:
                return f"{items[0]} {conjunction} {items[1]}"
            else:
                return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"
        
        # Register all filters
        self.env.filters['upper_legal'] = upper_legal
        self.env.filters['format_case_number'] = format_case_number
        self.env.filters['format_court_district'] = format_court_district
        self.env.filters['format_address'] = format_address
        self.env.filters['format_date'] = format_date
        self.env.filters['legal_list'] = legal_list
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a template with given variables
        
        Args:
            template_name: Name of template file (e.g., 'fcra/complaint.jinja2')
            variables: Template variables
            
        Returns:
            Rendered template content
        """
        try:
            template = self.env.get_template(template_name)
            
            # Add standard variables
            enhanced_vars = self._add_standard_variables(variables)
            
            rendered = template.render(**enhanced_vars)
            
            self.logger.info(f"Successfully rendered template: {template_name}")
            return rendered
            
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            raise TemplateRenderError(f"Failed to render {template_name}: {e}")
    
    def _add_standard_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Add standard variables available to all templates"""
        enhanced = variables.copy()
        
        enhanced.update({
            'generation_date': datetime.now().strftime('%B %d, %Y'),
            'generation_timestamp': datetime.now().isoformat(),
            'beaver_version': '1.1.2',
            'current_year': datetime.now().year
        })
        
        return enhanced
    
    def list_templates(self, pattern: str = None) -> List[str]:
        """
        List available templates
        
        Args:
            pattern: Optional pattern to filter templates
            
        Returns:
            List of template names
        """
        templates = []
        
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith('.jinja2'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.template_dir)
                    if pattern is None or pattern in rel_path:
                        templates.append(rel_path)
        
        return sorted(templates)
    
    def validate_template(self, template_name: str) -> bool:
        """
        Validate that a template exists and can be loaded
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            True if template is valid
        """
        try:
            self.env.get_template(template_name)
            return True
        except Exception as e:
            self.logger.error(f"Template validation failed for {template_name}: {e}")
            return False
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get information about a template
        
        Args:
            template_name: Name of template
            
        Returns:
            Template information dictionary
        """
        template_path = self.template_dir / template_name
        
        info = {
            'name': template_name,
            'path': str(template_path),
            'exists': template_path.exists(),
            'size': template_path.stat().st_size if template_path.exists() else 0,
            'modified': datetime.fromtimestamp(template_path.stat().st_mtime).isoformat() if template_path.exists() else None
        }
        
        if template_path.exists():
            try:
                # Try to parse template to check for syntax errors
                template = self.env.get_template(template_name)
                info['valid'] = True
                info['error'] = None
            except Exception as e:
                info['valid'] = False
                info['error'] = str(e)
        else:
            info['valid'] = False
            info['error'] = 'Template file not found'
        
        return info

class TemplateRenderError(Exception):
    """Exception raised when template rendering fails"""
    pass