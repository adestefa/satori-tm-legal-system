"""
Legal Entity Extractor for Tiger Engine
Specialized extraction of legal entities, case information, and structured legal data
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LegalEntity:
    """Represents a legal entity extracted from documents"""
    entity_type: str  # 'court', 'party', 'attorney', 'case_number', etc.
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None  # 'plaintiff', 'defendant', 'counsel', etc.
    confidence: float = 0.0
    source_text: Optional[str] = None

@dataclass
class CaseInformation:
    """Structured case information"""
    case_number: Optional[str] = None
    court_name: Optional[str] = None
    court_district: Optional[str] = None
    case_type: Optional[str] = None
    filing_date: Optional[str] = None
    jury_demand: Optional[bool] = None

class LegalEntityExtractor:
    """Extract legal entities and case information from legal documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Setup regex patterns for legal entity extraction"""
        
        # Case number patterns
        self.case_number_patterns = [
            r'\b\d{1,2}:\d{2}-cv-\d{4,6}\b',  # Federal format: 1:25-cv-01987
            r'\b\d{4}-\d{6}\b',                # State format: 2025-123456
            r'Case\s+No\.?\s*:?\s*([A-Z0-9:\-\.]+)',
            r'Civil\s+Action\s+No\.?\s*:?\s*([A-Z0-9:\-\.]+)',
            r'BC\d{6}',                        # California BC format
        ]
        
        # Court patterns
        self.court_patterns = [
            r'UNITED\s+STATES\s+DISTRICT\s+COURT',
            r'U\.S\.\s+DISTRICT\s+COURT',
            r'SUPERIOR\s+COURT\s+OF\s+[A-Z\s]+',
            r'([A-Z\s]+)\s+DISTRICT\s+COURT',
            r'COURT\s+OF\s+[A-Z\s]+',
        ]
        
        # District patterns  
        self.district_patterns = [
            r'(EASTERN|WESTERN|NORTHERN|SOUTHERN|CENTRAL|MIDDLE)\s+DISTRICT\s+OF\s+([A-Z]{2,15}(?:\s+[A-Z]{2,15})?)',
            r'DISTRICT\s+OF\s+([A-Z]{2,15}(?:\s+[A-Z]{2,15})?)',
            r'COUNTY\s+OF\s+([A-Z]{2,15}(?:\s+[A-Z]{2,15})?)',
        ]
        
        # Legal roles patterns
        self.role_patterns = {
            'plaintiff': [r'Plaintiff[s]?[,:]?', r'PLAINTIFF[S]?[,:]?'],
            'defendant': [r'Defendant[s]?[,:]?', r'DEFENDANT[S]?[,:]?'],
            'attorney': [r'Attorney[s]?\s+for', r'Counsel\s+for', r'Esq\.?'],
            'judge': [r'Judge', r'JUDGE', r'Hon\.', r'Honorable'],
            'clerk': [r'Clerk\s+of\s+Court', r'CLERK\s+OF\s+COURT'],
        }
        
        # Address patterns
        self.address_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Road|Rd|Lane|Ln|Place|Pl)\b[,\s]*[A-Za-z\s]*[,\s]*[A-Z]{2}\s*\d{5}(?:-\d{4})?',
            r'P\.O\.\s+Box\s+\d+[,\s]*[A-Za-z\s]*[,\s]*[A-Z]{2}\s*\d{5}(?:-\d{4})?',
        ]
        
        # Phone patterns
        self.phone_patterns = [
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\d{3}-\d{3}-\d{4}',
            r'\d{3}\.\d{3}\.\d{4}',
            r'\d{10}',
        ]
        
        # Email patterns
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ]
        
        # Legal document type patterns
        self.document_type_patterns = {
            'summons': [r'SUMMONS\s+IN\s+A\s+CIVIL\s+ACTION', r'SUMMONS'],
            'complaint': [r'COMPLAINT', r'AMENDED\s+COMPLAINT'],
            'motion': [r'MOTION\s+FOR', r'MOTION\s+TO'],
            'order': [r'ORDER', r'JUDGMENT'],
            'cover_sheet': [r'CIVIL\s+COVER\s+SHEET', r'COVER\s+SHEET'],
        }
    
    def extract_case_information(self, text: str) -> CaseInformation:
        """Extract structured case information from document text"""
        case_info = CaseInformation()
        
        # Extract case number
        case_info.case_number = self._extract_case_number(text)
        
        # Extract court information
        court_info = self._extract_court_info(text)
        case_info.court_name = court_info.get('name')
        case_info.court_district = court_info.get('district')
        
        # Extract case type
        case_info.case_type = self._extract_case_type(text)
        
        # Extract jury demand
        case_info.jury_demand = self._extract_jury_demand(text)
        
        # Extract filing date
        case_info.filing_date = self._extract_filing_date(text)
        
        return case_info
    
    def extract_parties(self, text: str) -> List[LegalEntity]:
        """Extract plaintiff and defendant information"""
        parties = []
        
        # Extract plaintiffs
        plaintiffs = self._extract_plaintiffs(text)
        parties.extend(plaintiffs)
        
        # Extract defendants  
        defendants = self._extract_defendants(text)
        parties.extend(defendants)
        
        return parties
    
    def extract_attorneys(self, text: str) -> List[LegalEntity]:
        """Extract attorney/counsel information"""
        attorneys = []
        
        # Look for attorney blocks in common formats
        attorney_patterns = [
            r'Attorney[s]?\s+for.*?(?=\n\n|\n[A-Z]|\Z)',
            r'[A-Z][a-z]+\s+[A-Z][a-z]+(?:,?\s+Esq\.?).*?(?=\n\n|\n[A-Z]|\Z)',
            r'Respectfully\s+submitted[,:]?\s*.*?(?=\n\n|\n[A-Z]|\Z)',
        ]
        
        for pattern in attorney_patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                attorney_block = match.group(0)
                attorney = self._parse_attorney_block(attorney_block)
                if attorney:
                    attorneys.append(attorney)
        
        return attorneys
    
    def extract_legal_entities(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive legal entity information"""
        entities = {
            'case_information': self.extract_case_information(text),
            'parties': self.extract_parties(text),
            'attorneys': self.extract_attorneys(text),
            'addresses': self._extract_addresses(text),
            'phones': self._extract_phone_numbers(text),
            'emails': self._extract_emails(text),
            'document_type': self._classify_document_type(text),
            'legal_indicators': self._extract_legal_indicators(text)
        }
        
        return entities
    
    def _extract_case_number(self, text: str) -> Optional[str]:
        """Extract case number from text"""
        for pattern in self.case_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Return the full match for most patterns, or group 1 for capturing patterns
                return match.group(1) if match.groups() else match.group(0)
        return None
    
    def _extract_court_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract court name and district"""
        court_info = {'name': None, 'district': None}
        
        # Extract court name
        for pattern in self.court_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                court_info['name'] = match.group(0)
                break
        
        # Extract district
        for pattern in self.district_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if match.groups():
                    # Combine direction and state if captured
                    groups = match.groups()
                    if len(groups) >= 2:
                        court_info['district'] = f"{groups[0]} District of {groups[1]}".strip()
                    else:
                        court_info['district'] = groups[0].strip()
                else:
                    # Clean the match to avoid contamination
                    district_text = match.group(0).strip()
                    # Stop at line breaks to avoid capturing subsequent content
                    district_text = district_text.split('\n')[0].strip()
                    court_info['district'] = district_text
                break
        
        return court_info
    
    def _extract_case_type(self, text: str) -> Optional[str]:
        """Determine case type from document content"""
        case_types = {
            'Complaint': [r'COMPLAINT', r'CIVIL\s+COMPLAINT'],
            'Motion': [r'MOTION\s+FOR', r'MOTION\s+TO'],
            'Summons': [r'SUMMONS'],
            'Order': [r'ORDER\s+AND\s+JUDGMENT', r'ORDER'],
        }
        
        for case_type, patterns in case_types.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return case_type
        
        return None
    
    def _extract_jury_demand(self, text: str) -> Optional[bool]:
        """Check for jury demand"""
        jury_patterns = [
            r'JURY\s+TRIAL\s+DEMANDED',
            r'DEMANDS?\s+A\s+JURY\s+TRIAL',
            r'JURY\s+DEMAND:?\s*YES',
            r'CHECK\s+IF\s+JURY\s+TRIAL\s+IS\s+DEMANDED',
        ]
        
        for pattern in jury_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for explicit "NO" 
        no_jury_patterns = [
            r'JURY\s+DEMAND:?\s*NO',
            r'NO\s+JURY\s+TRIAL',
        ]
        
        for pattern in no_jury_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return None
    
    def _extract_filing_date(self, text: str) -> Optional[str]:
        """Extract filing date"""
        date_patterns = [
            r'Date[d]?:?\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})',
            r'Filed:?\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_plaintiffs(self, text: str) -> List[LegalEntity]:
        """Extract plaintiff information"""
        plaintiffs = []
        
        # Look for plaintiff section patterns
        plaintiff_patterns = [
            r'([A-Z][a-z]+\s[A-Z][a-z]+),?\s*Plaintiff[s]?',
            r'Plaintiff[s]?[,:]?\s*([A-Z][a-z]+\s[A-Z][a-z]+)',
            r'([A-Z][A-Z\s]+),?\s*Plaintiff[s]?',
            r'Plaintiff[s]?[,:]?\s*([A-Z][A-Z\s]+)',
        ]
        
        for pattern in plaintiff_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                if name and len(name) > 2:
                    plaintiff = LegalEntity(
                        entity_type='party',
                        name=name,
                        role='plaintiff',
                        confidence=0.8,
                        source_text=match.group(0)
                    )
                    plaintiffs.append(plaintiff)
        
        return plaintiffs
    
    def _extract_defendants(self, text: str) -> List[LegalEntity]:
        """Extract defendant information"""
        defendants = []
        
        # Look for defendant section patterns
        defendant_patterns = [
            r'([A-Z][A-Z\s,\.&]+),?\s*Defendant[s]?',
            r'Defendant[s]?[,:]?\s*([A-Z][A-Z\s,\.&]+)',
        ]
        
        for pattern in defendant_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                if name and len(name) > 2:
                    defendant = LegalEntity(
                        entity_type='party',
                        name=name,
                        role='defendant', 
                        confidence=0.8,
                        source_text=match.group(0)
                    )
                    defendants.append(defendant)
        
        return defendants
    
    def _parse_attorney_block(self, attorney_block: str) -> Optional[LegalEntity]:
        """Parse attorney information from text block"""
        lines = attorney_block.strip().split('\n')
        
        name = None
        firm = None
        address_parts = []
        phone = None
        email = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for name (usually first non-empty line or after "Respectfully submitted")
            if not name and re.search(r'^[A-Z][a-z]+\s+[A-Z]\.?\s+[A-Z][a-z]+', line):
                name = re.sub(r',?\s*Esq\.?', '', line).strip()
            
            # Look for firm name
            elif 'LLC' in line or 'PLLC' in line or 'Law' in line or 'Attorney' in line:
                firm = line
            
            # Look for phone
            elif re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', line):
                phone = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', line).group(0)
            
            # Look for email
            elif '@' in line:
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
                if email_match:
                    email = email_match.group(0)
            
            # Collect address parts
            elif re.search(r'\d+\s+[A-Za-z]', line) or re.search(r'[A-Z]{2}\s+\d{5}', line):
                address_parts.append(line)
        
        if name:
            address = ', '.join(address_parts) if address_parts else None
            
            attorney = LegalEntity(
                entity_type='attorney',
                name=name,
                address=address,
                phone=phone,
                email=email,
                role='counsel',
                confidence=0.9,
                source_text=attorney_block
            )
            return attorney
        
        return None
    
    def _extract_addresses(self, text: str) -> List[str]:
        """Extract all addresses from text"""
        addresses = []
        for pattern in self.address_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                addresses.append(match.group(0).strip())
        return addresses
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phones = []
        for pattern in self.phone_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                phones.append(match.group(0))
        return phones
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        emails = []
        for pattern in self.email_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                emails.append(match.group(0))
        return emails
    
    def _classify_document_type(self, text: str) -> Optional[str]:
        """Classify the type of legal document"""
        for doc_type, patterns in self.document_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return doc_type
        return None
    
    def _extract_legal_indicators(self, text: str) -> Dict[str, Any]:
        """Extract legal document indicators for quality assessment"""
        indicators = {
            'has_case_number': bool(self._extract_case_number(text)),
            'has_court_header': any(re.search(p, text, re.IGNORECASE) for p in self.court_patterns),
            'has_parties': bool(re.search(r'Plaintiff|Defendant', text, re.IGNORECASE)),
            'has_attorney_info': bool(re.search(r'Attorney|Counsel|Esq', text, re.IGNORECASE)),
            'has_legal_citations': bool(re.search(r'\d+\s+U\.S\.C\.\s+§\s+\d+', text)),
            'document_structure_score': self._calculate_structure_score(text),
        }
        
        return indicators
    
    def _calculate_structure_score(self, text: str) -> float:
        """Calculate document structure quality score"""
        score = 0.0
        
        # Check for legal document structure elements
        structure_elements = [
            (r'UNITED STATES DISTRICT COURT', 20),
            (r'Plaintiff[s]?.*v\..*Defendant[s]?', 15),
            (r'Case No\.', 10),
            (r'COMPLAINT|SUMMONS', 15),
            (r'Respectfully submitted', 10),
            (r'Attorney for', 10),
            (r'/s/', 5),  # Electronic signature
            (r'Date:', 5),
            (r'\(\d{3}\)\s*\d{3}-\d{4}', 5),  # Phone number
            (r'@.*\.com', 5),  # Email
        ]
        
        for pattern, points in structure_elements:
            if re.search(pattern, text, re.IGNORECASE):
                score += points
        
        # Normalize to 0-100 scale
        return min(score, 100.0)

def extract_legal_entities_from_text(text: str) -> Dict[str, Any]:
    """
    Convenience function to extract legal entities from text
    
    Args:
        text: Document text to analyze
        
    Returns:
        Dictionary containing extracted legal entity information
    """
    extractor = LegalEntityExtractor()
    return extractor.extract_legal_entities(text)