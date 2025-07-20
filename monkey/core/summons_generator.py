"""
Summons Generator Module for Tiger-Monkey Legal Document System

This module generates individual summons documents for each defendant using HTML templates
and the headless Chrome approach for PDF generation.

Author: Dr. Spock - Lead Software Architect
Date: 2025-07-10
Version: 1.8.12
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)

class SummonsGenerator:
    """
    Generates individual summons documents for each defendant in a case.
    
    Uses HTML template with Jinja2 rendering, designed for headless Chrome PDF generation.
    Each defendant gets a separate summons document with proper service information.
    """
    
    def __init__(self, template_dir: str = None):
        """
        Initialize the Summons Generator.
        
        Args:
            template_dir: Directory containing summons templates
        """
        self.template_dir = template_dir or os.path.join(
            os.path.dirname(__file__), '..', '..', 'dashboard', 'config'
        )
        self.template_file = "summons_template.html"
        self.creditor_addresses_file = "creditor_addresses.json"
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
        
        # Load creditor addresses
        self.creditor_addresses = self._load_creditor_addresses()
        
    def generate_summons_for_case(self, case_data: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Generate individual summons documents for each defendant in the case.
        
        Args:
            case_data: Hydrated JSON case data from Tiger service
            output_dir: Directory to save generated summons files
            
        Returns:
            List of file paths to generated summons HTML files
        """
        try:
            # Validate input data
            if not self._validate_case_data(case_data):
                raise ValueError("Invalid case data for summons generation")
            
            # Extract defendants list
            defendants = case_data.get('parties', {}).get('defendants', [])
            if not defendants:
                raise ValueError("No defendants found in case data")
            
            # Load summons template
            template = self._load_summons_template()
            
            # Use output_dir directly (it should already point to the summons directory)
            summons_dir = output_dir
            os.makedirs(summons_dir, exist_ok=True)
            
            generated_files = []
            
            # Generate individual summons for each defendant
            for idx, defendant in enumerate(defendants):
                summons_data = self._prepare_summons_data(case_data, defendant, idx)
                
                # Render HTML using Jinja2
                rendered_html = template.render(**summons_data)
                
                # Create filename for this defendant's summons
                defendant_name_clean = self._clean_filename(defendant.get('name', f'defendant_{idx}'))
                filename = f"summons_{defendant_name_clean}.html"
                filepath = os.path.join(summons_dir, filename)
                
                # Write rendered HTML to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                
                generated_files.append(filepath)
                logger.info(f"Generated summons for defendant: {defendant.get('name')} -> {filepath}")
            
            logger.info(f"Successfully generated {len(generated_files)} summons documents")
            return generated_files
            
        except Exception as e:
            logger.error(f"Error generating summons documents: {str(e)}")
            raise
    
    def _validate_case_data(self, case_data: Dict[str, Any]) -> bool:
        """
        Validate that case data contains required fields for summons generation.
        
        Args:
            case_data: Case data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            'case_information',
            'parties'
        ]
        
        for field in required_fields:
            if field not in case_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate case information
        case_info = case_data.get('case_information', {})
        if not case_info.get('case_number') or not case_info.get('court_district'):
            logger.error("Missing case number or court district")
            return False
        
        # Validate parties
        parties = case_data.get('parties', {})
        if not parties.get('plaintiff') or not parties.get('defendants'):
            logger.error("Missing plaintiff or defendants")
            return False
        
        return True
    
    def _load_creditor_addresses(self) -> Dict[str, Any]:
        """
        Load creditor addresses from the configuration file.
        
        Returns:
            Dictionary containing creditor address information
        """
        try:
            creditor_file_path = os.path.join(self.template_dir, self.creditor_addresses_file)
            
            if not os.path.exists(creditor_file_path):
                logger.warning(f"Creditor addresses file not found: {creditor_file_path}")
                return {}
            
            with open(creditor_file_path, 'r', encoding='utf-8') as f:
                creditor_data = json.load(f)
            
            logger.info(f"Loaded {len(creditor_data.get('creditor_addresses', {}))} creditor addresses")
            return creditor_data
            
        except Exception as e:
            logger.error(f"Error loading creditor addresses: {str(e)}")
            return {}
    
    def _find_creditor_address(self, defendant_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a creditor address based on defendant name matching.
        
        Args:
            defendant_name: Name of the defendant to match
            
        Returns:
            Creditor address data if found, None otherwise
        """
        if not self.creditor_addresses or 'creditor_addresses' not in self.creditor_addresses:
            return None
        
        # Normalize defendant name for matching
        defendant_normalized = defendant_name.upper().strip()
        
        # Check each creditor for potential matches
        for creditor_key, creditor in self.creditor_addresses['creditor_addresses'].items():
            creditor_name = creditor.get('legal_name', '').upper().strip()
            creditor_short = creditor.get('short_name', '').upper().strip()
            
            # Direct name match (check both legal name and short name)
            if (creditor_name in defendant_normalized or 
                defendant_normalized in creditor_name or
                creditor_short in defendant_normalized):
                logger.info(f"Found creditor match for '{defendant_name}': {creditor.get('legal_name')}")
                return creditor
            
            # Check for key company identifiers
            key_identifiers = {
                'EXPERIAN': 'EXPERIAN',
                'EQUIFAX': 'EQUIFAX', 
                'TRANS UNION': 'TRANS UNION',
                'TD BANK': 'TD BANK'
            }
            
            for identifier, company in key_identifiers.items():
                if identifier in defendant_normalized and company.upper() in creditor_name:
                    logger.info(f"Found creditor match by identifier '{identifier}' for '{defendant_name}': {creditor.get('name')}")
                    return creditor
        
        logger.info(f"No creditor address found for defendant: {defendant_name}")
        return None
    
    def _load_summons_template(self) -> Template:
        """
        Load the summons HTML template.
        
        Returns:
            Jinja2 Template object
        """
        try:
            template_path = os.path.join(self.template_dir, self.template_file)
            
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Summons template not found: {template_path}")
            
            # Read template file
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Convert placeholder format from [variable] to {{ variable }}
            template_content = self._convert_template_format(template_content)
            
            # Create Jinja2 template
            template = Environment().from_string(template_content)
            return template
            
        except Exception as e:
            logger.error(f"Error loading summons template: {str(e)}")
            raise
    
    def _convert_template_format(self, template_content: str) -> str:
        """
        Convert template from [variable] format to {{ variable }} Jinja2 format.
        
        Args:
            template_content: Raw template content
            
        Returns:
            Converted template content for Jinja2
        """
        # Template variable mappings
        conversions = {
            '[Eastern District of New York]': '{{ court_district }}',
            '[Eman Youssef]': '{{ plaintiff_name }}',
            '[TD Bank, NA, Equifax Information Services, LLC; <br>\n                                Experian Information Solutions, Inc and Trans Union, LLC]': '{{ all_defendants_html }}',
            '[1:25-cv-01987]': '{{ case_number }}',
            '[Defendant Name]': '{{ defendant_name }}',
            '[Defendant Address Line 1]': '{{ defendant_address_line1 }}',
            '[Defendant City, State, ZIP]': '{{ defendant_address_city_state_zip }}',
            '[Kevin Mallon]': '{{ attorney_name }}',
            '[Mallon Consumer Law Group, PLLC]': '{{ firm_name }}',
            '[238 Merritt Drive]': '{{ firm_address_line1 }}',
            '[Oradell NJ 07649]': '{{ firm_address_city_state_zip }}',
            '[(917) 734-6815]': '{{ firm_phone }}',
            '[kmallon@consumerprotectionfirm.com]': '{{ firm_email }}',
            '[BRENNA B. MAHONEY]': '{{ clerk_name }}',
            '[Date]': '{{ service_date }}'
        }
        
        # Apply conversions
        for old_format, new_format in conversions.items():
            template_content = template_content.replace(old_format, new_format)
        
        return template_content
    
    def _prepare_summons_data(self, case_data: Dict[str, Any], defendant: Dict[str, Any], defendant_index: int) -> Dict[str, Any]:
        """
        Prepare template data for a specific defendant's summons.
        
        Args:
            case_data: Full case data
            defendant: Specific defendant data
            defendant_index: Index of defendant in list
            
        Returns:
            Dictionary of template variables
        """
        case_info = case_data.get('case_information', {})
        parties = case_data.get('parties', {})
        plaintiff = parties.get('plaintiff', {})
        defendants = parties.get('defendants', [])
        plaintiff_counsel = case_data.get('plaintiff_counsel', {})
        
        # Generate all defendants string for case caption
        all_defendants_html = self._format_all_defendants_html(defendants)
        
        # Format defendant address - check creditor addresses first
        defendant_address_line1 = 'Address Not Available'
        defendant_address_city_state_zip = ''
        
        # First, try to get address from case data
        defendant_address = defendant.get('address', {})
        if defendant_address.get('street'):
            defendant_address_line1 = defendant_address.get('street')
            defendant_city = defendant_address.get('city', '')
            defendant_state = defendant_address.get('state', '')
            defendant_zip = defendant_address.get('zip_code', '')
            defendant_address_city_state_zip = f"{defendant_city}, {defendant_state} {defendant_zip}".strip()
        else:
            # If no address in case data, check creditor addresses
            creditor_info = self._find_creditor_address(defendant.get('name', ''))
            if creditor_info and creditor_info.get('address'):
                creditor_address = creditor_info['address']
                defendant_address_line1 = creditor_address.get('street', 'Address Not Available')
                defendant_city = creditor_address.get('city', '')
                defendant_state = creditor_address.get('state', '')
                defendant_zip = creditor_address.get('zip_code', '')
                defendant_address_city_state_zip = f"{defendant_city}, {defendant_state} {defendant_zip}".strip()
                logger.info(f"Using creditor address for {defendant.get('name')}: {defendant_address_line1}")
        
        # Format firm address
        firm_address = plaintiff_counsel.get('address', {})
        firm_address_line1 = firm_address.get('street', 'Address Not Available')
        firm_city = firm_address.get('city', '')
        firm_state = firm_address.get('state', '')
        firm_zip = firm_address.get('zip_code', '')
        firm_address_city_state_zip = f"{firm_city}, {firm_state} {firm_zip}".strip()
        
        # Prepare template data
        template_data = {
            # Court information
            'court_district': case_info.get('court_district', 'EASTERN DISTRICT OF NEW YORK'),
            'case_number': case_info.get('case_number', 'Case Number Not Available'),
            
            # Parties information
            'plaintiff_name': plaintiff.get('name', 'Plaintiff Name Not Available'),
            'all_defendants_html': all_defendants_html,
            
            # Specific defendant being served
            'defendant_name': defendant.get('name', 'Defendant Name Not Available'),
            'defendant_address_line1': defendant_address_line1,
            'defendant_address_city_state_zip': defendant_address_city_state_zip,
            
            # Attorney/Firm information
            'attorney_name': plaintiff_counsel.get('name', 'Attorney Name Not Available'),
            'firm_name': plaintiff_counsel.get('firm', 'Firm Name Not Available'),
            'firm_address_line1': firm_address_line1,
            'firm_address_city_state_zip': firm_address_city_state_zip,
            'firm_phone': plaintiff_counsel.get('phone', 'Phone Not Available'),
            'firm_email': plaintiff_counsel.get('email', 'Email Not Available'),
            
            # Service information
            'service_date': datetime.now().strftime('%B %d, %Y'),
            'clerk_name': 'BRENNA B. MAHONEY'  # Default clerk - could be configurable
        }
        
        return template_data
    
    def _format_all_defendants_html(self, defendants: List[Dict[str, Any]]) -> str:
        """
        Format all defendants for the case caption in HTML format.
        
        Args:
            defendants: List of defendant dictionaries
            
        Returns:
            HTML formatted string of all defendants
        """
        defendant_names = []
        for defendant in defendants:
            name = defendant.get('name', 'Unknown Defendant')
            defendant_names.append(name)
        
        # Join with HTML line breaks
        return '<br>\n                                '.join(defendant_names)
    
    def _clean_filename(self, filename: str) -> str:
        """
        Clean filename for file system compatibility.
        
        Args:
            filename: Raw filename
            
        Returns:
            Cleaned filename
        """
        # Remove invalid characters and replace spaces with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        filename = filename.replace(' ', '_').replace(',', '').replace('.', '')
        return filename.lower()

def generate_summons_documents(case_data: Dict[str, Any], output_dir: str) -> List[str]:
    """
    Convenience function to generate summons documents for a case.
    
    Args:
        case_data: Hydrated JSON case data from Tiger service
        output_dir: Directory to save generated summons files
        
    Returns:
        List of file paths to generated summons HTML files
    """
    generator = SummonsGenerator()
    return generator.generate_summons_for_case(case_data, output_dir)

# Future headless Chrome PDF generation function placeholder
def convert_summons_to_pdf(html_file_path: str, pdf_output_path: str) -> bool:
    """
    Future implementation: Convert summons HTML to PDF using headless Chrome.
    
    This function will use headless Chrome (V8 engine) to render HTML and generate
    high-quality PDF documents suitable for court filing.
    
    Args:
        html_file_path: Path to HTML summons file
        pdf_output_path: Path where PDF should be saved
        
    Returns:
        True if successful, False otherwise
    """
    # Placeholder for future implementation
    # Will use puppeteer, playwright, or similar headless Chrome solution
    logger.info(f"PDF conversion placeholder: {html_file_path} -> {pdf_output_path}")
    return False