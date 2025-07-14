"""
Document Validators for Beaver
Validates complaint data and generated documents for legal compliance
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from satori_schema.hydrated_json_schema import HydratedJSON

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validation process"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    score: float = 0.0  # Validation score 0-100
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class DocumentValidator:
    """Validates legal document data and formatting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Required fields for different document types
        self.required_fields = {
            'complaint': {
                'case_information': ['court_district'],
                'plaintiff': ['name'],
                'defendants': [],  # At least one defendant required
                'causes_of_action': []  # At least one cause required
            }
        }
    
    def validate_complaint_data(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate complaint JSON data from Tiger using unified schema
        
        Args:
            data: Complaint data dictionary
            
        Returns:
            ValidationResult with validation status and issues
        """
        errors = []
        warnings = []
        
        try:
            # First, validate against the unified schema
            HydratedJSON.model_validate(data)
            
            # Additional Beaver-specific validation
            self._validate_beaver_specific_requirements(data, errors, warnings)
            
            # Calculate validation score
            score = self._calculate_validation_score(data, errors, warnings)
            
            is_valid = len(errors) == 0
            
            self.logger.info(f"Validation complete: {is_valid}, Score: {score:.1f}, Errors: {len(errors)}, Warnings: {len(warnings)}")
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                score=score
            )
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                score=0.0
            )
    
    def _validate_beaver_specific_requirements(self, data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate Beaver-specific requirements beyond schema validation"""
        
        # Check for template compatibility
        self._validate_template_compatibility(data, errors, warnings)
        
        # Check for document generation readiness
        self._validate_generation_readiness(data, errors, warnings)
        
        # Validate legacy format compatibility
        self._validate_legacy_compatibility(data, errors, warnings)
    
    def _validate_template_compatibility(self, data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate compatibility with Beaver templates"""
        
        # Check if data structure supports template variables
        parties = data.get('parties', {})
        
        # Check plaintiff information for template variables
        plaintiff = parties.get('plaintiff', {})
        if plaintiff.get('name') and len(plaintiff['name'].split()) < 2:
            warnings.append("Plaintiff name may be incomplete for template generation")
        
        # Check defendants for template compatibility
        defendants = parties.get('defendants', [])
        for i, defendant in enumerate(defendants):
            if not defendant.get('short_name') and defendant.get('name'):
                warnings.append(f"Defendant {i+1}: Missing short name for template use")
        
        # Check causes of action formatting
        causes = data.get('causes_of_action', [])
        for i, cause in enumerate(causes):
            if not cause.get('count'):
                warnings.append(f"Cause of action {i+1}: Missing count number for template")
    
    def _validate_generation_readiness(self, data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate readiness for document generation"""
        
        # Check if all required template sections are present
        required_for_generation = [
            ('case_information', 'court_district'),
            ('parties.plaintiff', 'name'),
            ('causes_of_action', None)  # Must be non-empty array
        ]
        
        for section_path, field in required_for_generation:
            if '.' in section_path:
                section, subsection = section_path.split('.', 1)
                section_data = data.get(section, {}).get(subsection, {})
            else:
                section_data = data.get(section_path, {})
            
            if field:
                if not section_data.get(field):
                    errors.append(f"Required for generation: {section_path}.{field}")
            else:
                if not section_data:
                    errors.append(f"Required for generation: {section_path} must be non-empty")
    
    def _validate_legacy_compatibility(self, data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate compatibility with legacy complaint.json format"""
        
        # Check for format version
        metadata = data.get('metadata', {})
        format_version = metadata.get('format_version')
        
        if not format_version:
            warnings.append("Missing format version - assuming legacy format")
        elif format_version != "3.0":
            warnings.append(f"Format version {format_version} may not be fully compatible")
        
        # Check for legacy field names that might cause confusion
        if 'plaintiff' in data and 'parties' in data:
            warnings.append("Both 'plaintiff' and 'parties.plaintiff' found - using 'parties.plaintiff'")
        
        if 'defendants' in data and 'parties' in data:
            warnings.append("Both 'defendants' and 'parties.defendants' found - using 'parties.defendants'")
    
    def _validate_structure(self, data: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate top-level data structure for hydrated JSON - LEGACY METHOD"""
        
        # This method is kept for legacy compatibility but main validation is done by schema
        # Check if this is new format (has 'parties' section) or legacy format
        
        if 'parties' in data:
            # New hydrated JSON format - minimal validation since schema handles it
            parties = data.get('parties', {})
            if not parties.get('plaintiff'):
                warnings.append("Missing plaintiff in parties section")
            if not parties.get('defendants'):
                warnings.append("Missing defendants in parties section")
        else:
            # Legacy format - validate old structure
            required_sections = ['case_information', 'plaintiff', 'defendants', 'causes_of_action']
            
            for section in required_sections:
                if section not in data:
                    errors.append(f"Missing required section: {section}")
                elif not data[section]:
                    if section == 'defendants':
                        errors.append("At least one defendant is required")
                    else:
                        errors.append(f"Section '{section}' is empty")
        
        # Validate case_information
        case_info = data.get('case_information', {})
        for field in ['court_type', 'court_district', 'case_number']:
            if not case_info.get(field):
                if field == 'case_number':
                    warnings.append(f"Missing recommended field: case_information.{field}")
                else:
                    errors.append(f"Missing required field: case_information.{field}")
        
        # Validate plaintiff
        plaintiff = data.get('plaintiff', {})
        if not plaintiff.get('name'):
            errors.append("Missing required field: plaintiff.name")
        
        # Check for plaintiff address
        if not plaintiff.get('address'):
            warnings.append("Missing plaintiff address information")
        else:
            address = plaintiff['address']
            if not address.get('street') or not address.get('city_state_zip'):
                warnings.append("Incomplete plaintiff address information")
        
        # Validate causes_of_action
        self._validate_causes_of_action_hydrated(data.get('causes_of_action', []), errors, warnings)
        
        # Check for Tiger metadata
        if 'tiger_metadata' not in data:
            warnings.append("Missing Tiger metadata - document may not be from Tiger extraction")
    
    def _validate_case_information(self, case_info: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate case information section"""
        
        # Required fields
        if not case_info.get('court_district'):
            errors.append("Court district is required")
        
        # Recommended fields
        if not case_info.get('case_number'):
            warnings.append("Case number not provided - will need to be added manually")
        
        if not case_info.get('court_type'):
            warnings.append("Court type not specified")
        
        # Validate court district format
        court_district = case_info.get('court_district', '')
        if court_district and 'district' not in court_district.lower():
            warnings.append("Court district may not be properly formatted")
    
    def _validate_plaintiff(self, plaintiff: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate plaintiff information"""
        
        # Required fields
        if not plaintiff.get('name'):
            errors.append("Plaintiff name is required")
        
        # Recommended fields
        if not plaintiff.get('address'):
            warnings.append("Plaintiff address not provided")
        
        if not plaintiff.get('consumer_status'):
            warnings.append("Consumer status not specified - using default")
        
        # Validate name format
        name = plaintiff.get('name', '')
        if name and len(name.split()) < 2:
            warnings.append("Plaintiff name appears incomplete (first and last name recommended)")
    
    def _validate_defendants(self, defendants: List[Dict[str, Any]], errors: List[str], warnings: List[str]):
        """Validate defendants list"""
        
        if not defendants:
            errors.append("At least one defendant is required")
            return
        
        for i, defendant in enumerate(defendants):
            prefix = f"Defendant {i+1}"
            
            # Required fields
            if not defendant.get('name'):
                errors.append(f"{prefix}: Name is required")
            
            # Recommended fields
            if not defendant.get('type'):
                warnings.append(f"{prefix}: Entity type not specified")
            
            if not defendant.get('address'):
                warnings.append(f"{prefix}: Address not provided")
            
            # Validate name format
            name = defendant.get('name', '')
            if name and name.endswith(','):
                warnings.append(f"{prefix}: Name has trailing comma")
    
    def _validate_causes_of_action(self, causes: List[Dict[str, Any]], errors: List[str], warnings: List[str]):
        """Validate causes of action"""
        
        if not causes:
            warnings.append("No causes of action specified - using default FCRA violation")
            return
        
        for i, cause in enumerate(causes):
            prefix = f"Cause {i+1}"
            
            if not cause.get('title'):
                errors.append(f"{prefix}: Title is required")
            
            if not cause.get('allegations'):
                warnings.append(f"{prefix}: No allegations specified")
            elif len(cause['allegations']) == 0:
                warnings.append(f"{prefix}: No allegations provided")

    def _validate_causes_of_action_hydrated(self, causes: List[Dict[str, Any]], errors: List[str], warnings: List[str]):
        """Validate causes of action in hydrated JSON format"""
        
        if not causes:
            warnings.append("No causes of action specified - using default FCRA violation")
            return
        
        for i, cause in enumerate(causes):
            prefix = f"Cause {i+1}"
            
            if not cause.get('title'):
                errors.append(f"{prefix}: Title is required")
            
            # Check allegations
            allegations = cause.get('allegations', [])
            if not allegations:
                warnings.append(f"{prefix}: No allegations specified")
            else:
                for j, allegation in enumerate(allegations):
                    if not allegation.get('statute'):
                        warnings.append(f"{prefix}, Allegation {j+1}: Missing statute reference")
                    if not allegation.get('description'):
                        warnings.append(f"{prefix}, Allegation {j+1}: Missing description")
    
    def _validate_damages(self, damages: Dict[str, Any], errors: List[str], warnings: List[str]):
        """Validate damages section"""
        
        if not damages:
            warnings.append("No damages information provided - using default language")
            return
        
        if not damages.get('summary') and not damages.get('denials'):
            warnings.append("No specific damage details provided")
        
        # Validate denial information
        denials = damages.get('denials', [])
        for i, denial in enumerate(denials):
            prefix = f"Denial {i+1}"
            
            if not denial.get('date'):
                warnings.append(f"{prefix}: Date not provided")
            
            if not denial.get('creditor') and not denial.get('application_for'):
                warnings.append(f"{prefix}: Incomplete denial information")
    
    def _calculate_validation_score(self, data: Dict[str, Any], errors: List[str], warnings: List[str]) -> float:
        """Calculate overall validation score (0-100)"""
        
        if errors:
            return 0.0  # Cannot be valid with errors
        
        # Start with base score
        score = 100.0
        
        # Deduct for warnings
        score -= len(warnings) * 5
        
        # Bonus for completeness
        bonus_fields = [
            ('case_information', 'case_number'),
            ('plaintiff', 'address'),
            ('plaintiff', 'phone'),
            ('plaintiff', 'email'),
            ('factual_background', 'summary'),
            ('factual_background', 'events'),
            ('damages', 'denials')
        ]
        
        present_bonus_fields = 0
        for section, field in bonus_fields:
            if section in data and data[section].get(field):
                present_bonus_fields += 1
        
        completeness_bonus = (present_bonus_fields / len(bonus_fields)) * 20
        score += completeness_bonus
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))
    
    def validate_document_format(self, document_content: str, document_type: str = 'complaint') -> ValidationResult:
        """
        Validate generated document format and content
        
        Args:
            document_content: Generated document text
            document_type: Type of document (complaint, summons, etc.)
            
        Returns:
            ValidationResult for document format
        """
        errors = []
        warnings = []
        
        try:
            if not document_content or not document_content.strip():
                errors.append("Document content is empty")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings, score=0.0)
            
            # Check for required document elements
            if document_type == 'complaint':
                self._validate_complaint_format(document_content, errors, warnings)
            
            # Calculate format score
            score = self._calculate_format_score(document_content, errors, warnings)
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                score=score
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Format validation failed: {str(e)}"],
                warnings=[],
                score=0.0
            )
    
    def _validate_complaint_format(self, content: str, errors: List[str], warnings: List[str]):
        """Validate complaint document format"""
        
        content_upper = content.upper()
        
        # Required elements
        required_elements = [
            'UNITED STATES DISTRICT COURT',
            'COMPLAINT',
            'PLAINTIFF',
            'DEFENDANT'
        ]
        
        for element in required_elements:
            if element not in content_upper:
                errors.append(f"Missing required element: {element}")
        
        # Recommended elements
        recommended_elements = [
            'JURISDICTION',
            'VENUE',
            'PARTIES',
            'FACTUAL BACKGROUND',
            'CAUSES OF ACTION',
            'DAMAGES',
            'PRAYER FOR RELIEF'
        ]
        
        for element in recommended_elements:
            if element not in content_upper:
                warnings.append(f"Missing recommended section: {element}")
        
        # Check for proper case number format
        import re
        case_number_pattern = r'\d+:\d+-cv-\d+'
        if not re.search(case_number_pattern, content):
            warnings.append("Case number not found or improperly formatted")
        
        # Check for proper date format
        date_pattern = r'[A-Z][a-z]+ \d{1,2}, \d{4}'
        if not re.search(date_pattern, content):
            warnings.append("Date not found or improperly formatted")
    
    def _calculate_format_score(self, content: str, errors: List[str], warnings: List[str]) -> float:
        """Calculate document format score"""
        
        if errors:
            return 0.0
        
        score = 100.0
        score -= len(warnings) * 10
        
        # Bonus for proper formatting indicators
        if 'UNITED STATES DISTRICT COURT' in content:
            score += 5
        if 'Respectfully submitted' in content:
            score += 5
        if content.count('\n\n') >= 10:  # Proper paragraph spacing
            score += 5
        
        return max(0.0, min(100.0, score))