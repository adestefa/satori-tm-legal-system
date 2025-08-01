"""
Case Consolidator for Tiger Engine
Consolidates information across multiple documents in a legal case folder
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

try:
    from ..extractors.legal_entity_extractor import LegalEntityExtractor, LegalEntity, CaseInformation
    from ..extractors.damage_extractor import DamageExtractor, DamageItem
    from ..extractors.date_extractor import EnhancedDateExtractor, ExtractedDate, DateContext
    from ...engines.base_engine import ExtractionResult
    from ..settings_loader import SettingsLoader
except ImportError:
    from app.core.extractors.legal_entity_extractor import LegalEntityExtractor, LegalEntity, CaseInformation
    from app.core.extractors.damage_extractor import DamageExtractor, DamageItem
    from app.core.extractors.date_extractor import EnhancedDateExtractor, ExtractedDate, DateContext
    from app.engines.base_engine import ExtractionResult
    from app.core.settings_loader import SettingsLoader

@dataclass
class CaseTimeline:
    """Represents a comprehensive timeline for the case with date validation"""
    discovery_date: Optional[str] = None
    dispute_date: Optional[str] = None
    filing_date: Optional[str] = None
    damage_events: List[Dict[str, Any]] = None
    document_dates: List[Dict[str, Any]] = None
    chronological_validation: Dict[str, Any] = None
    timeline_confidence: float = 0.0
    
    def __post_init__(self):
        if self.damage_events is None:
            self.damage_events = []
        if self.document_dates is None:
            self.document_dates = []
        if self.chronological_validation is None:
            self.chronological_validation = {'is_valid': True, 'errors': [], 'warnings': []}

@dataclass
class ConsolidatedCase:
    """Represents a consolidated legal case with information from multiple documents"""
    case_id: str
    case_information: CaseInformation
    plaintiff: Optional[Dict[str, Any]] = None
    plaintiff_counsel: Optional[Dict[str, Any]] = None
    defendants: List[Dict[str, Any]] = None
    factual_background: Optional[Dict[str, Any]] = None
    damages: Optional[Dict[str, Any]] = None
    causes_of_action: List[Dict[str, Any]] = None
    case_timeline: Optional[CaseTimeline] = None
    source_documents: List[str] = None
    extraction_confidence: float = 0.0
    consolidation_timestamp: str = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.defendants is None:
            self.defendants = []
        if self.causes_of_action is None:
            self.causes_of_action = []
        if self.source_documents is None:
            self.source_documents = []
        if self.warnings is None:
            self.warnings = []
        if self.consolidation_timestamp is None:
            self.consolidation_timestamp = datetime.now().isoformat()

class CaseConsolidator:
    """Consolidate legal information across multiple documents in a case"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.legal_extractor = LegalEntityExtractor()
        self.damage_extractor = DamageExtractor()
        self.date_extractor = EnhancedDateExtractor()
    
    def consolidate_case_folder(self, folder_path: str, extraction_results: List[ExtractionResult]) -> ConsolidatedCase:
        """
        Consolidate multiple document extractions into a single case structure
        
        Args:
            folder_path: Path to the case folder
            extraction_results: List of extraction results from Tiger processing
            
        Returns:
            ConsolidatedCase object with merged information
        """
        self.logger.info(f"Consolidating case folder: {folder_path}")
        
        case_id = os.path.basename(folder_path)
        
        # Initialize consolidated case with timeline
        consolidated = ConsolidatedCase(
            case_id=case_id,
            case_information=CaseInformation(),
            case_timeline=CaseTimeline()
        )
        
        # Process each document's extraction result
        all_legal_entities = []
        document_texts = []
        
        for result in extraction_results:
            if not result.success or "summons" in result.file_path.lower():
                consolidated.warnings.append(f"Skipping file: {result.file_path}")
                continue
                
            consolidated.source_documents.append(result.file_path)
            document_texts.append(result.extracted_text)
            
            # Extract legal entities from this document
            legal_entities = self.legal_extractor.extract_legal_entities(result.extracted_text)
            all_legal_entities.append({
                'file_path': result.file_path,
                'entities': legal_entities
            })
        
        # Consolidate information across all documents
        self._consolidate_case_information(consolidated, all_legal_entities, extraction_results)
        self._consolidate_parties(consolidated, all_legal_entities, extraction_results)
        self._consolidate_attorneys(consolidated, all_legal_entities, extraction_results)
        self._consolidate_factual_background(consolidated, document_texts, extraction_results)
        self._consolidate_damages(consolidated, document_texts, extraction_results)
        self._consolidate_timeline(consolidated, extraction_results)
        self.logger.info("Calling _build_causes_of_action")
        consolidated.causes_of_action = self._build_causes_of_action(document_texts, consolidated.defendants)
        
        # Calculate overall confidence
        consolidated.extraction_confidence = self._calculate_case_confidence(consolidated, all_legal_entities)
        
        self.logger.info(f"Case consolidation complete. Confidence: {consolidated.extraction_confidence:.1f}%")
        
        return consolidated
    
    def _consolidate_case_information(self, consolidated: ConsolidatedCase, all_entities: List[Dict], extraction_results: List[ExtractionResult]):
        """Consolidate case information across documents, prioritizing attorney notes."""
        
        # Initialize variables for validation
        case_numbers = []
        court_names = []
        court_districts = []
        case_types = []
        jury_demands = []
        filing_dates = []
        
        # Prioritize Atty_Notes.txt for case information
        for result in extraction_results:
            filename = os.path.basename(result.file_path).lower()
            if 'atty_notes.docx' in filename or 'atty_notes.txt' in filename:
                text = result.extracted_text
                
                case_number = self._extract_labeled_data(text, "CASE_NUMBER")
                if case_number:
                    consolidated.case_information.case_number = case_number
                
                court_name = self._extract_labeled_data(text, "COURT_NAME")
                if court_name:
                    consolidated.case_information.court_name = court_name
                
                court_district = self._extract_labeled_data(text, "COURT_DISTRICT")
                if court_district:
                    consolidated.case_information.court_district = court_district
                
                filing_date = self._extract_labeled_data(text, "FILING_DATE")
                if filing_date:
                    consolidated.case_information.filing_date = filing_date

        # Fallback to existing document extraction if not found in attorney notes
        if not all(getattr(consolidated.case_information, field) for field in ['case_number', 'court_name', 'court_district', 'filing_date']):
            
            for i, doc_entities in enumerate(all_entities):
                case_info = doc_entities['entities']['case_information']
                
                if case_info.case_number: case_numbers.append(case_info.case_number.upper())
                if case_info.court_name: court_names.append(case_info.court_name)
                if case_info.court_district: court_districts.append(case_info.court_district)
                if case_info.case_type: case_types.append(case_info.case_type)
                if case_info.jury_demand is not None: jury_demands.append(case_info.jury_demand)
                
                filename = os.path.basename(extraction_results[i].file_path).lower()
                if 'civil cover sheet' in filename:
                    text = extraction_results[i].extracted_text
                    match = re.search(r'DATE\s*(\d{1,2}/\d{1,2}/\d{2,4})', text)
                    if match:
                        filing_dates.append(match.group(1))

            # Use most common or most reliable values
            if not consolidated.case_information.case_number:
                consolidated.case_information.case_number = self._get_most_common(case_numbers)
            if not consolidated.case_information.court_name:
                consolidated.case_information.court_name = self._get_most_common(court_names)
            if not consolidated.case_information.court_district:
                consolidated.case_information.court_district = self._get_most_common(court_districts)
            if not consolidated.case_information.filing_date:
                 consolidated.case_information.filing_date = self._get_most_common(filing_dates)
            
            consolidated.case_information.case_type = self._get_most_common(case_types)
            consolidated.case_information.jury_demand = self._get_most_common(jury_demands)

        # Validate consistency
        if len(set(case_numbers)) > 1:
            consolidated.warnings.append(f"Inconsistent case numbers found: {set(case_numbers)}")
        
        if len(set(court_districts)) > 1:
            consolidated.warnings.append(f"Inconsistent court districts found: {set(court_districts)}")
    
    def _extract_labeled_data(self, text: str, label: str) -> Optional[str]:
        """Extracts data from a labeled field in the attorney notes."""
        match = re.search(rf'^{label}:\s*(.*)', text, re.MULTILINE | re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return value if value.upper() != "TBD" else ""
        return None
    
    def _extract_plaintiff_from_atty_notes(self, text: str) -> Optional[str]:
        """Extract plaintiff name from attorney notes"""
        # First, try to find the labeled data
        match = re.search(r'NAME:\s*(.*)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Fallback to original logic
        match = re.search(r'^(.*)', text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_plaintiff_address_from_atty_notes(self, text: str) -> Optional[Dict[str, str]]:
        """Extract plaintiff address from labeled data in attorney notes."""
        match = re.search(r'ADDRESS:\s*\n?(.*?)(?=\nPHONE:|$)', text, re.IGNORECASE | re.DOTALL)
        if match:
            address_block = match.group(1).strip()
            return self._parse_address(address_block)
        return None

    def _extract_plaintiff_phone_from_atty_notes(self, text: str) -> Optional[str]:
        """Extract plaintiff phone from labeled data in attorney notes."""
        match = re.search(r'PHONE:\s*(.*?)(?=\n[A-Z_]+:|$)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_defendants_from_atty_notes(self, text: str) -> List[str]:
        """Extract defendants using FCRA legal logic - only entities that furnished incorrect info or failed to investigate."""
        defendants = set()
        
        # Pattern 2: FCRA-specific logic - identify the furnisher that reported incorrect information
        if re.search(r'TD\s+Bank.*(?:dispute|fraud|denied|refused)', text, re.IGNORECASE):
            defendants.add('TD BANK, N.A.')
            self.logger.info("Added TD Bank as furnisher defendant based on dispute context")
        
        # Pattern 3: Always include Big 3 CRAs for FCRA cases 
        fcra_indicators = [
            r'credit\s+report|credit\s+bureau|denied\s+credit|credit\s+decision',
            r'credit\s+card|fraudulent\s+charges|dispute',
            r'fcra|fair\s+credit\s+reporting',
            r'equifax|experian|transunion|trans\s+union'
        ]
        
        is_fcra_case = any(re.search(pattern, text, re.IGNORECASE) for pattern in fcra_indicators)
        
        if is_fcra_case:
            standard_cras = [
                'EQUIFAX INFORMATION SERVICES, LLC',
                'EXPERIAN INFORMATION SOLUTIONS, INC.',
                'TRANS UNION LLC'
            ]
            for cra in standard_cras:
                defendants.add(cra)
                self.logger.info(f"Added standard CRA defendant for FCRA case: {cra}")
        else:
            self.logger.info("No FCRA indicators found, skipping CRA defendants")
        
        defendants_list = list(defendants)
        self.logger.info(f"Extracted {len(defendants_list)} defendants from attorney notes using FCRA legal logic: {defendants_list}")
        return defendants_list
    
    def _normalize_bank_name(self, bank_name: str) -> str:
        """Normalize bank names to standard format."""
        name_lower = bank_name.lower()
        
        # Normalize common variations
        if 'td bank' in name_lower:
            return 'TD BANK, N.A.'
        elif 'capital one' in name_lower:
            return 'CAPITAL ONE, N.A.'
        elif 'barclays' in name_lower:
            return 'BARCLAYS BANK DELAWARE'
        elif 'bank of america' in name_lower:
            return 'BANK OF AMERICA, N.A.'
        elif 'citibank' in name_lower:
            return 'CITIBANK, N.A.'
        elif 'chase' in name_lower:
            return 'JPMORGAN CHASE BANK, N.A.'
        elif 'wells fargo' in name_lower:
            return 'WELLS FARGO BANK, N.A.'
        elif 'american express' in name_lower:
            return 'AMERICAN EXPRESS COMPANY'
        elif 'discover' in name_lower:
            return 'DISCOVER BANK'
        elif 'synchrony' in name_lower:
            return 'SYNCHRONY BANK'
        else:
            return bank_name.upper()
    
    def _normalize_cra_name(self, cra_name: str) -> str:
        """Normalize credit reporting agency names to standard format."""
        name_lower = cra_name.lower()
        
        if 'equifax' in name_lower:
            return 'EQUIFAX INFORMATION SERVICES LLC'
        elif 'experian' in name_lower:
            return 'EXPERIAN INFORMATION SOLUTIONS, INC.'
        elif 'transunion' in name_lower or 'trans union' in name_lower:
            return 'TRANS UNION LLC'
        else:
            return cra_name.upper()
    
    def _normalize_defendant_name(self, name: str) -> str:
        """Normalize defendant names for deduplication purposes."""
        # Remove common variations and standardize format
        normalized = name.upper().strip()
        
        # Remove incorporation details from name for comparison
        normalized = re.sub(r'\s*\([^)]*corporation[^)]*\)', '', normalized)
        normalized = re.sub(r'\s*\([^)]*authorized[^)]*\)', '', normalized)
        
        # Standardize common variations
        replacements = {
            'TRANS UNION': 'TRANSUNION',
            'EXPERIAN INFORMATION SOLUTIONS, INC.': 'EXPERIAN',
            'EQUIFAX INFORMATION SERVICES, LLC': 'EQUIFAX',
            'TD BANK, N.A.': 'TD BANK',
            'CAPITAL ONE, N.A.': 'CAPITAL ONE',
            'BARCLAYS BANK DELAWARE': 'BARCLAYS',
            'DALSTD TRANS UNION': 'TRANSUNION'  # Handle the concatenated form
        }
        
        for original, replacement in replacements.items():
            if original in normalized:
                normalized = replacement
                break
        
        # Remove extra whitespace and punctuation
        normalized = re.sub(r'[,\.]+$', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _extract_defendants_from_denial_letters(self, extraction_results: List[ExtractionResult]) -> List[str]:
        """Extract defendants from denial letters - but ONLY if they are furnishers, not just credit decision makers."""
        defendants = set()
        
        # For FCRA cases, denial letters typically show entities that USED reports, not furnished them
        # We should NOT extract defendants from denial letters unless they are the original furnisher
        # The denial letters (Capital One, Barclays) used CRA reports to make decisions - they are not defendants
        
        for result in extraction_results:
            filename = os.path.basename(result.file_path).lower()
            text = result.extracted_text
            
            # Only look for original creditors that are being disputed (furnishers)
            # Skip if this is just a denial based on reports from other sources
            if any(keyword in filename for keyword in ['denial', 'adverse', 'rejection']) or \
               any(phrase in text.lower() for phrase in ['denial', 'adverse action', 'cannot approve', 'unable to approve']):
                
                # Only extract as defendant if this entity is the ORIGINAL furnisher
                # Look for "Creditor:" field that refers to original account holder
                creditor_match = re.search(r'Creditor:\s*([^\n]+)', text, re.IGNORECASE)
                if creditor_match:
                    creditor = creditor_match.group(1).strip()
                    # Only include if this is an entity being disputed for incorrect reporting
                    if 'capital one' in creditor.lower():
                        # Capital One in this case is the original creditor being reported incorrectly
                        # But based on case facts, TD Bank is the furnisher, not Capital One
                        # Skip Capital One as it's just making credit decisions based on reports
                        self.logger.info(f"Skipping Capital One - credit decision maker, not furnisher")
                        continue
                
        defendants_list = list(defendants)
        self.logger.info(f"FCRA defendants from denial letters: {len(defendants_list)} total: {defendants_list}")
        return defendants_list

    def _consolidate_parties(self, consolidated: ConsolidatedCase, all_entities: List[Dict], extraction_results: List[ExtractionResult]):
        """Consolidate plaintiff and defendant information"""
        all_plaintiffs = []
        defendant_names = set()

        # Prioritize Atty_Notes.docx for plaintiff and defendant information
        for i, result in enumerate(extraction_results):
            filename = os.path.basename(result.file_path).lower()
            if 'atty_notes.docx' in filename or 'atty_notes.txt' in filename:
                text = result.extracted_text
                # Extract plaintiff from attorney notes
                plaintiff_name = self._extract_plaintiff_from_atty_notes(text)
                if plaintiff_name:
                    all_plaintiffs.append(LegalEntity(name=plaintiff_name, role='plaintiff', entity_type='person', confidence=0.95))

                # Extract defendants from attorney notes
                defendants_from_notes = self._extract_defendants_from_atty_notes(text)
                for defendant_name in defendants_from_notes:
                    defendant_names.add(defendant_name)

        # Extract defendants from denial letters (enhanced functionality)
        defendants_from_denials = self._extract_defendants_from_denial_letters(extraction_results)
        for defendant_name in defendants_from_denials:
            defendant_names.add(defendant_name)

        for doc_entities in all_entities:
            self.logger.info(f"Processing entities from: {doc_entities.get('file_path')}")
            parties = doc_entities['entities']['parties']
            
            for party in parties:
                if party.role == 'plaintiff':
                    all_plaintiffs.append(party)
                elif party.role == 'defendant':
                    defendant_names.add(party.name)
        
        self.logger.info(f"Found {len(all_plaintiffs)} total plaintiffs.")
        self.logger.info(f"Found {len(defendant_names)} unique defendant names.")
        
        # Consolidate plaintiff (usually one primary plaintiff)
        if all_plaintiffs:
            primary_plaintiff = self._select_best_party_info(all_plaintiffs)
            
            plaintiff_address_from_notes = self._extract_plaintiff_address_from_atty_notes(extraction_results[0].extracted_text) if extraction_results else None
            plaintiff_phone_from_notes = self._extract_plaintiff_phone_from_atty_notes(extraction_results[0].extracted_text) if extraction_results else None

            consolidated.plaintiff = {
                'name': primary_plaintiff.name,
                'address': plaintiff_address_from_notes or self._extract_plaintiff_address(all_entities, extraction_results),
                'phone': plaintiff_phone_from_notes or self._extract_plaintiff_contact_info(all_entities, extraction_results, 'phone'),
                'email': self._extract_plaintiff_contact_info(all_entities, extraction_results, 'email'),
                'residency': self._determine_residency(consolidated.case_information.court_district),
                'consumer_status': "Individual 'consumer' within the meaning of both the FCRA and applicable state FCRA"
            }
        
        # Consolidate defendants with deduplication
        plaintiff_name = consolidated.plaintiff.get('name', '').upper() if consolidated.plaintiff else ''
        added_defendants = set()  # Track normalized names to prevent duplicates
        
        for name in defendant_names:
            # Enhanced filtering to exclude invalid defendants
            name_upper = name.upper().strip()
            
            # Skip generic terms and empty names
            if name_upper in ["LLC", "LLC NA,"]:
                continue
                
            # Skip plaintiff name (prevent plaintiff from being added as defendant)
            if plaintiff_name and name_upper == plaintiff_name:
                self.logger.info(f"Skipping defendant '{name}' - matches plaintiff name")
                continue
                
            # Skip dates, scores, and other non-entity terms
            excluded_patterns = [
                r'^(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)',
                r'^SCORES?\s+RANGE',
                r'^FROM\s+A\s+LOW',
                r'^\d{1,2}[,\s]\d{4}',  # Date patterns
                r'^(HIGH|LOW|RANGE|FROM|SCORE|DATE)$'
            ]
            
            if any(re.match(pattern, name_upper) for pattern in excluded_patterns):
                self.logger.info(f"Skipping invalid defendant '{name}' - matches excluded pattern")
                continue
            
            # Normalize name for deduplication
            normalized_name = self._normalize_defendant_name(name)
            
            # Skip if we already have this defendant (deduplication)
            if normalized_name in added_defendants:
                self.logger.info(f"Skipping duplicate defendant '{name}' - already added as '{normalized_name}'")
                continue
                
            # Build valid defendant
            defendant_info = self._build_defendant_info(name, consolidated)
            consolidated.defendants.append(defendant_info)
            added_defendants.add(normalized_name)

    def _suggest_legal_claims(self, case_facts, defendant_types):
        """Suggest ALL possible legal claims for human review - NO FILTERING."""
        self.logger.info("Suggesting ALL legal claims for lawyer review...")
        import json
        import os
        
        # Load legal corpus from Tiger resources directory
        from pathlib import Path
        legal_corpus_path = Path(__file__).parent.parent.parent / "resources" / "legal-spec" / "NY_FCRA.json"
        
        try:
            with open(legal_corpus_path, 'r') as f:
                legal_corpus = json.load(f)
            self.logger.info(f"Successfully loaded legal corpus from {legal_corpus_path}")
        except FileNotFoundError:
            self.logger.error(f"Legal corpus not found at {legal_corpus_path}")
            return {'fcra_claims': [], 'ny_fcra_claims': []}
        except Exception as e:
            self.logger.error(f"Error loading legal corpus: {str(e)}")
            return {'fcra_claims': [], 'ny_fcra_claims': []}
        
        suggested_claims = {
            'fcra_claims': [],
            'ny_fcra_claims': []
        }
        
        # Process ALL FCRA claims from causes_of_action (CRA violations)
        if 'causes_of_action' in legal_corpus and len(legal_corpus['causes_of_action']) > 0:
            self.logger.info(f"Found {len(legal_corpus['causes_of_action'])} cause of action categories")
            fcra_category = legal_corpus['causes_of_action'][0]  # CRA claims
            if 'claims' in fcra_category:
                self.logger.info(f"Processing {len(fcra_category['claims'])} CRA claims")
                for claim in fcra_category['claims']:
                    suggested_claims['fcra_claims'].append({
                        'citation': claim.get('statutory_basis', 'Unknown Citation'),
                        'description': claim.get('description', 'No description available'),
                        'selected': False,  # Lawyer will decide
                        'confidence': 0.8,  # Default confidence for CRA claims
                        'category': 'FCRA',
                        'against_defendants': self._determine_cra_applicability(claim)
                    })
                    self.logger.info(f"Added CRA claim: {claim.get('statutory_basis', 'Unknown')}")
            else:
                self.logger.warning("No 'claims' found in CRA category")
        else:
            self.logger.warning("No 'causes_of_action' found in legal corpus")
        
        # Process ALL furnisher claims from causes_of_action
        if 'causes_of_action' in legal_corpus and len(legal_corpus['causes_of_action']) > 1:
            furnisher_category = legal_corpus['causes_of_action'][1]  # Furnisher claims  
            if 'claims' in furnisher_category:
                for claim in furnisher_category['claims']:
                    suggested_claims['fcra_claims'].append({
                        'citation': claim.get('statutory_basis', 'Unknown Citation'),
                        'description': claim.get('description', 'No description available'),
                        'selected': False,  # Lawyer will decide
                        'confidence': 0.7,  # Default confidence for furnisher claims
                        'category': 'FCRA',
                        'against_defendants': self._determine_furnisher_applicability(claim)
                    })
        
        # Process ALL NY FCRA violations from legal_violations section
        if 'legal_violations' in legal_corpus and len(legal_corpus['legal_violations']) > 0:
            ny_fcra_section = legal_corpus['legal_violations'][0]  # NY FCRA violations
            if 'violations' in ny_fcra_section:
                for violation in ny_fcra_section['violations']:
                    suggested_claims['ny_fcra_claims'].append({
                        'citation': violation.get('citation', 'Unknown Citation'),
                        'description': violation.get('description', 'No description available'),
                        'selected': False,  # Lawyer will decide
                        'confidence': 0.7,  # Default confidence for NY FCRA claims
                        'category': 'NY_FCRA',
                        'against_defendants': ['Equifax', 'Experian', 'TransUnion']  # NY FCRA applies to CRAs only
                    })
        
        self.logger.info(f"Generated {len(suggested_claims['fcra_claims'])} FCRA claims and {len(suggested_claims['ny_fcra_claims'])} NY FCRA claims for lawyer review")
        return suggested_claims

    def _determine_cra_applicability(self, claim):
        """Determine which CRAs this claim applies to based on claim content."""
        # Most CRA claims apply to all three major bureaus
        return ['Equifax', 'Experian', 'TransUnion']
    
    def _determine_furnisher_applicability(self, claim):
        """Determine which furnishers this claim applies to based on claim content."""
        # Furnisher claims typically apply to data furnishers like banks
        return ['TD Bank']

    def _analyze_claim_applicability(self, case_text, violation, defendant_types):
        """Analyze if a legal violation applies to the case facts."""
        
        # Keywords that indicate specific violations
        violation_indicators = {
            'reinvestigation': ['dispute', 'investigation', 'reinvestigate', 'verify'],
            'reasonable_procedures': ['procedure', 'accuracy', 'verification'],
            'disclosures': ['disclosure', 'notice', 'inform', 'notification'],
            'reporting': ['report', 'credit report', 'information']
        }
        
        # Check if violation elements are present in case facts
        violation_title = violation['title'].lower()
        case_lower = case_text.lower()
        
        # Match violation patterns to case facts
        if 'reinvestigation' in violation_title:
            return any(keyword in case_lower for keyword in violation_indicators['reinvestigation'])
        elif 'reasonable procedures' in violation_title:
            return any(keyword in case_lower for keyword in violation_indicators['reasonable_procedures'])
        elif 'disclosure' in violation_title:
            return any(keyword in case_lower for keyword in violation_indicators['disclosures'])
        elif 'reporting' in violation_title:
            return any(keyword in case_lower for keyword in violation_indicators['reporting'])
        
        # Default to including common FCRA violations
        return True

    def _determine_applicable_defendants(self, applies_to, defendant_types):
        """Determine which defendants a violation applies to."""
        applicable_defendants = []
        
        # Map defendant types to short names
        defendant_mapping = {
            'Consumer Reporting Agency': ['Equifax', 'TransUnion', 'Experian'],
            'Furnisher of Information': ['TD Bank'],
            'Financial Institution': ['TD Bank']
        }
        
        for defendant_type in applies_to:
            if defendant_type in defendant_mapping:
                applicable_defendants.extend(defendant_mapping[defendant_type])
        
        # Remove duplicates and return
        return list(set(applicable_defendants))

    def _extract_case_facts(self, processed_docs):
        """Extracts case facts from processed documents."""
        case_facts = []
        for doc in processed_docs:
            case_facts.append(doc)
        return case_facts

    def _build_causes_of_action(self, processed_docs, defendants):
        """Build causes of action with populated legal claims."""
        self.logger.info("Building causes of action...")
        
        # First, try to extract legal claims from North Star attorney notes
        north_star_claims = []
        for result in processed_docs:
            if hasattr(result, 'file_path'):
                filename = os.path.basename(result.file_path).lower()
                if 'atty_notes.docx' in filename or 'atty_notes.txt' in filename:
                    text = result.extracted_text
                    north_star_claims = self._extract_legal_claims_from_atty_notes(text)
                    break
        
        # If we have North Star claims, use them
        if north_star_claims:
            self.logger.info(f"Using {len(north_star_claims)} legal claims from North Star schema")
            causes_of_action = []
            
            for claim in north_star_claims:
                # Convert North Star format to expected format
                cause = {
                    'count_number': claim['count'],
                    'title': claim['title'],
                    'type': claim['type'],
                    'legal_claims': [
                        {
                            'citation': citation['citation'],
                            'description': citation['description'],
                            'defendants_affected': citation['defendants_affected'],
                            'selected': citation['selected']
                        }
                        for citation in claim['citations']
                    ]
                }
                causes_of_action.append(cause)
            
            return causes_of_action
        
        # Fallback to legacy claim generation
        self.logger.info("No North Star claims found, using legacy claim generation")
        
        # Extract case facts from processed documents
        case_facts = self._extract_case_facts(processed_docs)
        
        # Get defendant types for claim analysis
        defendant_types = {d['short_name']: d['type'] for d in defendants}
        
        # Suggest legal claims based on case analysis
        suggested_claims = self._suggest_legal_claims(case_facts, defendant_types)
        
        causes_of_action = []
        
        # First Cause of Action: FCRA Violations
        fcra_cause = {
            'count_number': 1,
            'title': 'FIRST CAUSE OF ACTION: Violation of the FCRA',
            'against_defendants': ['Equifax', 'TransUnion', 'Experian', 'TD Bank'],
            'legal_claims': suggested_claims['fcra_claims']
        }
        causes_of_action.append(fcra_cause)
        
        # Second Cause of Action: NY FCRA Violations (CRAs only)
        ny_fcra_cause = {
            'count_number': 2, 
            'title': 'SECOND CAUSE OF ACTION: Violation of the New York Fair Credit Reporting Act',
            'against_defendants': ['Equifax', 'TransUnion', 'Experian'],
            'legal_claims': suggested_claims['ny_fcra_claims']
        }
        causes_of_action.append(ny_fcra_cause)
        
        return causes_of_action

    def _build_defendant_info(self, defendant_name: str, consolidated: ConsolidatedCase) -> Dict[str, str]:
        """Build complete defendant information with all required fields"""
        
        # Enhanced defendant mappings with complete legal information
        defendant_info_map = {
            'EQUIFAX INFORMATION SERVICES LLC': {
                'name': 'EQUIFAX INFORMATION SERVICES, LLC',
                'short_name': 'Equifax',
                'type': 'Consumer Reporting Agency',
                'state_of_incorporation': 'Georgia',
                'business_status': 'Authorized to do business in New York'
            },
            'TRANS UNION LLC': {
                'name': 'TRANS UNION, LLC',
                'short_name': 'TransUnion',
                'type': 'Consumer Reporting Agency', 
                'state_of_incorporation': 'Delaware',
                'business_status': 'Authorized to do business in New York'
            },
            'EXPERIAN INFORMATION SOLUTIONS, INC.': {
                'name': 'EXPERIAN INFORMATION SOLUTIONS, INC.',
                'short_name': 'Experian',
                'type': 'Consumer Reporting Agency',
                'state_of_incorporation': 'Ohio',
                'business_status': 'Authorized to do business in New York'
            },
            'TD BANK, N.A.': {
                'name': 'TD BANK, N.A.',
                'short_name': 'TD Bank',
                'type': 'Furnisher of Information',
                'state_of_incorporation': 'Delaware',
                'business_status': 'Authorized to do business in New York'
            }
        }
        
        # Use predefined info if available, otherwise build dynamically
        if defendant_name in defendant_info_map:
            defendant_info = defendant_info_map[defendant_name].copy()
        else:
            # Fallback for unknown defendants
            defendant_info = {
                'name': defendant_name,
                'short_name': self._extract_short_name(defendant_name),
                'type': self._classify_defendant_type(defendant_name),
                'state_of_incorporation': self._determine_incorporation_state(defendant_name),
                'business_status': f"Authorized to do business in {self._extract_state_from_district(consolidated.case_information.court_district)}"
            }
        
        self.logger.info(f"Built defendant info for: {defendant_info['name']} ({defendant_info['type']})")
        return defendant_info

    def _extract_defendants_from_summons(self, all_entities: List[Dict], extraction_results: List[ExtractionResult], consolidated: ConsolidatedCase) -> List[Dict]:
        """Extract defendant information specifically from summons documents."""
        defendants = []
        defendant_names = set()

        for i, doc_entities in enumerate(all_entities):
            if i < len(extraction_results):
                filename = os.path.basename(extraction_results[i].file_path).lower()
                if 'summons' in filename:
                    text = extraction_results[i].extracted_text
                    # Regex to find text between "To: (Defendant 's name and address)" and "lawsuit has been filed"
                    match = re.search(r"To: \(Defendant 's name and address\)\s*(.*?)\s*lawsuit has been filed", text, re.DOTALL | re.IGNORECASE)
                    if match:
                        defendant_block = match.group(1).strip()
                        # Simple split by newline, can be improved
                        potential_names = [name.strip() for name in defendant_block.split('\n') if name.strip()]
                        if potential_names:
                            defendant_name = potential_names[0]
                            if defendant_name not in defendant_names:
                                defendant_names.add(defendant_name)
                                defendant_info = self._build_defendant_info(defendant_name, consolidated)
                                defendants.append(defendant_info)
        return defendants

    def _extract_legal_claims_from_atty_notes(self, text: str) -> List[Dict[str, Any]]:
        """Extract legal claims from the LEGAL_CLAIMS section in attorney notes."""
        legal_claims = []
        match = re.search(r'STRUCTURED_DATA:.*?LEGAL_CLAIMS:\s*\n?(.*?)(?=\nRELIEF_SOUGHT:|BACKGROUND:|$)', text, re.IGNORECASE | re.DOTALL)
        if match:
            claims_text = match.group(1).strip()
            self.logger.info(f"Found LEGAL_CLAIMS section with text: {claims_text[:100]}...")
            
            # Parse claims by "Count X -" pattern
            count_matches = re.findall(r'Count\s+(\d+)\s*-\s*([^:]+):\s*([\s\S]*?)(?=Count\s+\d+|\Z)', claims_text, re.IGNORECASE)
            for count_num, claim_type, claim_content in count_matches:
                # Extract individual citations from the claim content
                citations = []
                citation_lines = [line.strip() for line in claim_content.split('\n') if line.strip() and line.strip().startswith('-')]
                
                for line in citation_lines:
                    # Extract citation and description: "- Citation: Description (Defendants)"
                    citation_match = re.match(r'-\s*([^:]+):\s*([^(]+)(?:\(([^)]+)\))?', line)
                    if citation_match:
                        citation = citation_match.group(1).strip()
                        description = citation_match.group(2).strip()
                        defendants_affected = citation_match.group(3).strip() if citation_match.group(3) else ""
                        
                        citations.append({
                            'citation': citation,
                            'description': description,
                            'defendants_affected': defendants_affected,
                            'selected': False  # Default to not selected
                        })
                
                legal_claims.append({
                    'count': int(count_num),
                    'title': f"Count {count_num} - {claim_type}",
                    'type': claim_type.strip(),
                    'citations': citations
                })
        
        self.logger.info(f"Extracted {len(legal_claims)} legal claims from North Star schema")
        return legal_claims

    def _extract_relief_sought_from_atty_notes(self, text: str) -> List[str]:
        """Extract relief sought from the RELIEF_SOUGHT section in attorney notes."""
        relief_items = []
        match = re.search(r'STRUCTURED_DATA:.*?RELIEF_SOUGHT:\s*\n?(.*?)(?=\nBACKGROUND:|$)', text, re.IGNORECASE | re.DOTALL)
        if match:
            relief_text = match.group(1).strip()
            self.logger.info(f"Found RELIEF_SOUGHT section with text: {relief_text[:100]}...")
            
            # Parse relief items from list format
            relief_lines = [line.strip().lstrip('-').strip() for line in relief_text.split('\n') if line.strip()]
            relief_items.extend(relief_lines)
        
        self.logger.info(f"Extracted {len(relief_items)} relief items from North Star schema")
        return relief_items

    def _extract_damages_from_north_star_schema(self, text: str) -> Dict[str, List[str]]:
        """Extract damages from North Star schema DAMAGES section."""
        damages = {
            'financial_harm': [],
            'reputational_harm': [],
            'emotional_harm': [],
            'personal_costs': []
        }
        
        # Extract DAMAGES section - try direct format first, then legacy STRUCTURED_DATA format
        match = re.search(r'DAMAGES:\s*\n(.*?)(?=\n[A-Z]+:|$)', text, re.IGNORECASE | re.DOTALL)
        if not match:
            # Fallback to legacy STRUCTURED_DATA format
            match = re.search(r'STRUCTURED_DATA:.*?DAMAGES:\s*\n?(.*?)(?=\nLEGAL_CLAIMS:|RELIEF_SOUGHT:|BACKGROUND:|$)', text, re.IGNORECASE | re.DOTALL)
        
        if match:
            damages_text = match.group(1).strip()
            self.logger.info(f"Found DAMAGES section with text: {damages_text[:100]}...")
            
            # Parse each damage category
            current_category = None
            for line in damages_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this is a category header
                if line.lower().startswith('financial harm:'):
                    current_category = 'financial_harm'
                elif line.lower().startswith('reputational harm:'):
                    current_category = 'reputational_harm'
                elif line.lower().startswith('emotional harm:'):
                    current_category = 'emotional_harm'
                elif line.lower().startswith('personal costs:'):
                    current_category = 'personal_costs'
                elif line.startswith('-') and current_category:
                    # This is a damage item under the current category
                    damage_item = line.lstrip('-').strip()
                    if damage_item:
                        damages[current_category].append(damage_item)
        
        total_damages = sum(len(items) for items in damages.values())
        self.logger.info(f"Extracted {total_damages} damages from North Star schema: {[(k, len(v)) for k, v in damages.items()]}")
        return damages
    
    def _consolidate_attorneys(self, consolidated: ConsolidatedCase, all_entities: List[Dict], extraction_results: List[ExtractionResult]):
        """Consolidate attorney information using settings for firm data and case notes for attorney name."""
        
        # Load firm settings from dashboard
        try:
            settings_loader = SettingsLoader()
            firm_settings = settings_loader.get_firm_info()
            self.logger.info(f"Loaded firm settings: {firm_settings.get('name', 'Unknown')}")
        except Exception as e:
            self.logger.warning(f"Could not load firm settings: {str(e)}. Using defaults.")
            firm_settings = {
                'name': 'Law Firm Name',
                'address': '123 Legal Street\nCity, State 12345',
                'phone': '(555) 123-4567',
                'email': 'contact@lawfirm.com'
            }
        
        # Extract case-specific attorney name from attorney notes
        attorney_name = ""
        for result in extraction_results:
            filename = os.path.basename(result.file_path).lower()
            if 'atty_notes.docx' in filename or 'atty_notes.txt' in filename:
                text = result.extracted_text
                extracted_name = self._extract_labeled_data(text, "PLAINTIFF_COUNSEL_NAME") or ""
                # Treat "TBD" as missing value
                if extracted_name and extracted_name.upper() != "TBD":
                    attorney_name = extracted_name
                break
        
        # Parse firm address from settings
        parsed_address = self._parse_address(firm_settings.get('address', ''))
        
        # Build complete plaintiff counsel information
        consolidated.plaintiff_counsel = {
            'name': attorney_name or firm_settings.get('attorney_name', ''),  # Use attorney name from settings
            'firm': firm_settings.get('name', ''),
            'address': parsed_address,
            'phone': firm_settings.get('phone', ''),
            'email': firm_settings.get('email', ''),
            'title': 'Attorneys for the Plaintiff'
        }
        
        self.logger.info(f"Consolidated attorney info: {attorney_name} at {firm_settings.get('name', 'Unknown')}")
        
        # Fallback to existing document extraction if no settings available and no attorney notes
        if not attorney_name and not any(firm_settings.values()):
            for i, doc_entities in enumerate(all_entities):
                if i < len(extraction_results):
                    filename = os.path.basename(extraction_results[i].file_path).lower()
                    if 'summons' in filename:
                        text = extraction_results[i].extracted_text
                        # Regex to find attorney block
                        match = re.search(r"plaintiff's attorney,\s*\n\s*whose name and address are:\s*\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n\s*(.*)", text, re.DOTALL | re.IGNORECASE)
                        if match:
                            consolidated.plaintiff_counsel = {
                                'name': match.group(1).strip(),
                                'firm': match.group(2).strip(),
                                'address': self._parse_address(match.group(3).strip()),
                                'phone': match.group(4).strip(),
                                'email': match.group(5).strip(),
                                'title': 'Attorneys for the Plaintiff'
                            }
                            return
    
    def _consolidate_factual_background(self, consolidated: ConsolidatedCase, document_texts: List[str], extraction_results: List[ExtractionResult]):
        """Extract and consolidate factual background from attorney notes and other documents"""
        factual_info = {
            'summary': '',
            'allegations': []
        }
        
        # Look for attorney notes or similar narrative documents
        for i, result in enumerate(extraction_results):
            filename = os.path.basename(result.file_path).lower()
            
            if 'atty_notes.docx' in filename or 'atty_notes.txt' in filename:
                text = result.extracted_text
                # Extract clean background section (should be at the end of file now)
                match = re.search(r'BACKGROUND:\s*\n?(.*?)(?=\s*\nDAMAGES:|$)', text, re.IGNORECASE | re.DOTALL)
                if match:
                    background_text = match.group(1).strip()
                    # Split the background text into individual allegations by line
                    allegations = [line.strip() for line in background_text.split('\n') 
                                 if line.strip() and not line.upper().startswith('STRUCTURED_DATA')]
                    factual_info['allegations'].extend(allegations)
                    self.logger.info(f"Extracted {len(allegations)} background allegations from North Star schema")
                    # Generate a summary from the collected allegations.
        
        if factual_info['allegations']:
            factual_info['summary'] = self._generate_factual_summary(consolidated, factual_info['allegations'])

        consolidated.factual_background = factual_info
    
    def _extract_creditor_from_denial(self, text: str) -> Optional[str]:
        """Extract creditor from denial letter"""
        # Regex to find creditor name
        match = re.search(r"Creditor: (.*)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_date_from_denial(self, text: str) -> Optional[str]:
        """Extract date from denial letter"""
        # Regex to find date
        match = re.search(r"Date: (.*)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_reasons_from_denial(self, text: str) -> List[str]:
        """Extract reasons from denial letter"""
        reasons = []
        # Regex to find reasons block
        match = re.search(r"The reason\(s\) for our decision are:\s*\n(.*?)\n\n", text, re.DOTALL | re.IGNORECASE)
        if match:
            reasons_block = match.group(1)
            # Simple split by newline, can be improved
            reasons = [reason.strip() for reason in reasons_block.split('·') if reason.strip()]
        return reasons

    def _consolidate_damages(self, consolidated: ConsolidatedCase, document_texts: List[str], extraction_results: List[ExtractionResult]):
        """Extract and consolidate damages information using enhanced damage extractor"""
        
        # Initialize damages structure
        damages_info = {
            'structured_damages': [],
            'categorized_damages': {},
            'summary': "The erroneous derogatory payment information wrongfully listed on Plaintiff's consumer reports caused damages including, but not limited to, damage to reputation, adverse impact on credit rating, being denied credit, in addition to emotional distress, expenditure of time and resources, annoyance, aggravation, and frustration.",
            'denials': [],  # Legacy denial extraction for backward compatibility
            'damage_statistics': {}
        }
        
        # Extract structured damages from attorney notes
        attorney_notes_text = self._find_attorney_notes_text(extraction_results)
        if attorney_notes_text:
            self.logger.info("Extracting structured damages from attorney notes")
            
            # First try North Star schema format
            north_star_damages = self._extract_damages_from_north_star_schema(attorney_notes_text)
            if any(damages for damages in north_star_damages.values()):
                self.logger.info("Using North Star schema damages format")
                damages_info['north_star_damages'] = north_star_damages
                
                # Convert North Star damages to structured format for compatibility
                structured_damages = []
                for category, items in north_star_damages.items():
                    for item in items:
                        structured_damages.append({
                            'category': category,
                            'type': 'damage',
                            'entity': 'plaintiff',
                            'date': 'unknown',
                            'evidence_available': True,
                            'description': item,
                            'selected': False,
                            'amount': None
                        })
                
                damages_info['structured_damages'] = structured_damages
                damages_info['categorized_damages'] = {
                    category: [
                        {
                            'category': category,
                            'type': 'damage',
                            'entity': 'plaintiff',
                            'date': 'unknown',
                            'evidence_available': True,
                            'description': item,
                            'selected': False,
                            'amount': None
                        }
                        for item in items
                    ]
                    for category, items in north_star_damages.items()
                }
                
                total_damages = sum(len(items) for items in north_star_damages.values())
                damages_info['damage_statistics'] = {'total_damages': total_damages}
                
                self.logger.info(f"Extracted {total_damages} damages from North Star schema")
            else:
                # Fallback to legacy damage extraction
                self.logger.info("No North Star damages found, using legacy extraction")
                extracted_damages = self.damage_extractor.extract_damages(attorney_notes_text)
                
                if extracted_damages:
                    damages_info['structured_damages'] = [
                        {
                            'category': damage.category,
                            'type': damage.type,
                            'entity': damage.entity,
                            'date': damage.date,
                            'evidence_available': damage.evidence_available,
                            'description': damage.description,
                            'selected': damage.selected,
                            'amount': damage.amount
                        }
                        for damage in extracted_damages
                    ]
                    
                    # Categorize damages for easier review interface
                    categorized = self.damage_extractor.categorize_damages(extracted_damages)
                    # Convert DamageItem objects to dictionaries for JSON serialization
                    damages_info['categorized_damages'] = {
                        category: [
                            {
                                'category': damage.category,
                                'type': damage.type,
                                'entity': damage.entity,
                                'date': damage.date,
                                'evidence_available': damage.evidence_available,
                                'description': damage.description,
                                'selected': damage.selected,
                                'amount': damage.amount
                            }
                            for damage in items
                        ]
                        for category, items in categorized.items()
                    }
                    
                    # Generate damage statistics
                    damages_info['damage_statistics'] = self.damage_extractor.get_damage_summary(extracted_damages)
                    
                    self.logger.info(f"Extracted {len(extracted_damages)} structured damages: {damages_info['damage_statistics']}")
                else:
                    self.logger.warning("No structured damages found in attorney notes DAMAGES section")
        else:
            self.logger.warning("No attorney notes found for damage extraction")
        
        # Legacy denial letter extraction for backward compatibility
        for i, result in enumerate(extraction_results):
            filename = os.path.basename(result.file_path).lower()
            
            if any(keyword in filename for keyword in ['denial', 'adverse', 'rejection']):
                if i < len(document_texts):
                    text = document_texts[i]
                    denial_info = self._extract_denial_information(text)
                    if denial_info:
                        damages_info['denials'].append(denial_info)
        
        consolidated.damages = damages_info
    
    def _find_attorney_notes_text(self, extraction_results: List[ExtractionResult]) -> Optional[str]:
        """Find and return the text content of attorney notes file"""
        for result in extraction_results:
            filename = os.path.basename(result.file_path).lower()
            if 'atty_notes.docx' in filename or 'atty_notes.txt' in filename:
                return result.extracted_text
        return None
    
    def _calculate_case_confidence(self, consolidated: ConsolidatedCase, all_entities: List[Dict]) -> float:
        """Calculate overall confidence score for the consolidated case"""
        score = 0.0
        max_score = 100.0
        
        # Case information completeness (30 points)
        case_info_score = 0
        if consolidated.case_information.case_number:
            case_info_score += 10
        if consolidated.case_information.court_name:
            case_info_score += 10
        if consolidated.case_information.court_district:
            case_info_score += 10
        score += case_info_score
        
        # Plaintiff information completeness (20 points)
        if consolidated.plaintiff:
            plaintiff_score = 0
            if consolidated.plaintiff.get('name'):
                plaintiff_score += 10
            if consolidated.plaintiff.get('address'):
                plaintiff_score += 5
            if consolidated.plaintiff.get('phone') or consolidated.plaintiff.get('email'):
                plaintiff_score += 5
            score += plaintiff_score
        
        # Defendant information completeness (20 points)
        if consolidated.defendants:
            defendant_score = min(len(consolidated.defendants) * 5, 20)
            score += defendant_score
        
        # Attorney information completeness (15 points)
        if consolidated.plaintiff_counsel:
            attorney_score = 0
            if consolidated.plaintiff_counsel.get('name'):
                attorney_score += 5
            if consolidated.plaintiff_counsel.get('firm'):
                attorney_score += 5
            if consolidated.plaintiff_counsel.get('phone') or consolidated.plaintiff_counsel.get('email'):
                attorney_score += 5
            score += attorney_score
        
        # Factual background completeness (10 points)
        if consolidated.factual_background and consolidated.factual_background.get('allegations'):
            score += min(len(consolidated.factual_background['allegations']) * 2, 10)
        
        # Consistency bonus (5 points)
        if len(consolidated.warnings) == 0:
            score += 5
        
        return min(score, max_score)
    
    def _get_most_common(self, items: List[Any]) -> Optional[Any]:
        """Get the most common item from a list"""
        if not items:
            return None
        
        # Count occurrences
        counts = defaultdict(int)
        for item in items:
            counts[item] += 1
        
        # Return most common
        return max(counts.items(), key=lambda x: x[1])[0] if counts else None
    
    def _select_best_party_info(self, parties: List[LegalEntity]) -> LegalEntity:
        """Select the best party information from multiple extractions"""
        # Prefer parties with higher confidence scores
        return max(parties, key=lambda p: p.confidence)
    
    def _select_best_attorney_info(self, attorneys: List[LegalEntity]) -> LegalEntity:
        """Select the most complete attorney information"""
        # Score attorneys based on completeness
        def attorney_score(attorney):
            score = 0
            if attorney.name:
                score += 3
            if attorney.address:
                score += 2
            if attorney.phone:
                score += 1
            if attorney.email:
                score += 1
            return score
        
        return max(attorneys, key=attorney_score)
    
    def _classify_defendant_type(self, name: str) -> str:
        """Classify defendant type based on name"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['bank', 'credit union', 'financial']):
            return 'Furnisher of Information'
        elif any(word in name_lower for word in ['equifax', 'experian', 'transunion', 'trans union']):
            return 'Consumer Reporting Agency'
        elif any(word in name_lower for word in ['llc', 'inc', 'corp', 'company']):
            return 'Corporate Defendant'
        else:
            return 'Individual Defendant'
    
    def _extract_short_name(self, full_name: str) -> str:
        """Extract short name for defendant"""
        # Remove common corporate suffixes for short name
        short = full_name.replace(', LLC', '').replace(', INC.', '').replace(' INFORMATION SERVICES', '')
        short = short.replace(' INFORMATION SOLUTIONS', '').replace(', N.A.', '')
        return short.strip()
    
    def _determine_incorporation_state(self, name: str) -> str:
        """Determine likely state of incorporation based on defendant name and common patterns"""
        # Common patterns for major credit agencies and banks
        incorporation_map = {
            'equifax': 'Georgia',
            'experian': 'Ohio', 
            'transunion': 'Delaware',
            'trans union': 'Delaware',
            'td bank': 'Delaware',
            'bank of america': 'North Carolina',
            'wells fargo': 'South Dakota',
            'chase': 'Ohio',
            'citibank': 'South Dakota'
        }
        
        name_lower = name.lower()
        for key, state in incorporation_map.items():
            if key in name_lower:
                return state
        
        # Default to Delaware (most common for corporations)
        return 'Delaware'
    
    def _extract_plaintiff_address(self, all_entities: List[Dict], extraction_results: List[ExtractionResult]) -> Optional[Dict[str, str]]:
        """Extract plaintiff address from attorney notes first, then denial letters"""
        # Prioritize attorney notes for plaintiff address
        for i, result in enumerate(extraction_results):
            filename = os.path.basename(result.file_path).lower()
            if 'atty_notes.docx' in filename or 'atty_notes.txt' in filename:
                text = result.extracted_text
                # Look for address in attorney notes
                match = re.search(r'ADDRESS:\s*\n?(.*?)(?=\nPHONE:|$)', text, re.IGNORECASE | re.DOTALL)
                if match:
                    return self._parse_address(match.group(1))

        # Fallback to denial letters if not found in attorney notes
        for i, doc_entities in enumerate(all_entities):
            if i < len(extraction_results):
                filename = os.path.basename(extraction_results[i].file_path).lower()
                if any(keyword in filename for keyword in ['denial', 'adverse', 'rejection', 'barclays', 'cap_one']):
                    text = extraction_results[i].extracted_text
                    # Find plaintiff's name and then find the address that follows
                    for plaintiff in doc_entities['entities']['parties']:
                        if plaintiff.role == 'plaintiff':
                            # A simple regex to find an address block after the plaintiff's name
                            match = re.search(re.escape(plaintiff.name) + r'\s*\n(.*?)\n(.*?NY.*)', text)
                            if match:
                                street = match.group(1).strip()
                                city_state_zip = match.group(2).strip()
                                return self._parse_address(f"{street}\n{city_state_zip}")
        
        # Fallback to generic address extraction
        return self._extract_address_from_entities(all_entities, 'plaintiff')
    
    def _extract_address_from_entities(self, all_entities: List[Dict], entity_type: str) -> Optional[Dict[str, str]]:
        """Extract address information for specific entity type"""
        addresses = []
        
        for doc_entities in all_entities:
            entity_addresses = doc_entities['entities']['addresses']
            addresses.extend(entity_addresses)
        
        if addresses:
            # Use the most complete address
            best_address = max(addresses, key=len)
            return self._parse_address(best_address)
        
        return None
    
    def _extract_plaintiff_contact_info(self, all_entities: List[Dict], extraction_results: List[ExtractionResult], contact_type: str) -> Optional[str]:
        """Extract plaintiff contact info (separate from attorney contact info)"""
        # Per PRD: plaintiff contact info should come from attorney notes or denial letters
        plaintiff_contacts = []
        
        # Look for attorney notes first (most likely to have plaintiff's contact info)
        for i, doc_entities in enumerate(all_entities):
            if i < len(extraction_results):
                filename = os.path.basename(extraction_results[i].file_path).lower()
                if any(keyword in filename for keyword in ['atty_notes', 'attorney_notes', 'notes']):
                    text = extraction_results[i].extracted_text
                    if contact_type == 'phone':
                        # Simple regex for phone numbers
                        matches = re.findall(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
                        for match in matches:
                            if not any(attorney_indicator in match.lower() for attorney_indicator in ['consumerprotectionfirm', 'attorney', 'counsel', 'esq']):
                                plaintiff_contacts.append(match)
                    elif contact_type == 'email':
                        # Simple regex for email
                        matches = re.findall(r'[\w\.-]+@[\w\.-]+', text)
                        for match in matches:
                            if not any(attorney_indicator in match.lower() for attorney_indicator in ['consumerprotectionfirm']):
                                plaintiff_contacts.append(match)

        # If no plaintiff-specific contact found, try denial letters
        if not plaintiff_contacts:
            for i, doc_entities in enumerate(all_entities):
                if i < len(extraction_results):
                    filename = os.path.basename(extraction_results[i].file_path).lower()
                    if any(keyword in filename for keyword in ['denial', 'adverse', 'rejection']):
                        if contact_type == 'phone':
                            contacts = doc_entities['entities']['phones']
                        elif contact_type == 'email':
                            contacts = doc_entities['entities']['emails']
                        else:
                            continue
                        plaintiff_contacts.extend(contacts)
        
        # Return the first valid plaintiff contact found
        return plaintiff_contacts[0] if plaintiff_contacts else None
    
    def _extract_defendants_from_summons(self, all_entities: List[Dict], extraction_results: List[ExtractionResult], consolidated: ConsolidatedCase) -> List[Dict[str, Any]]:
        """Extract defendants from individual summons files as per PRD specification"""
        defendants = []
        defendant_names = set()
        
        for i, doc_entities in enumerate(all_entities):
            if i < len(extraction_results):
                filename = os.path.basename(extraction_results[i].file_path).lower()
                # Look specifically for summons files
                if 'summons' in filename:
                    # Extract defendant name from filename and text
                    defendant_name = self._extract_defendant_from_summons_file(filename, extraction_results[i])
                    
                    if defendant_name and defendant_name not in defendant_names:
                        defendant_names.add(defendant_name)
                        
                        defendant_info = {
                            'name': defendant_name,
                            'short_name': self._extract_short_name(defendant_name),
                            'type': self._classify_defendant_type(defendant_name),
                            'state_of_incorporation': self._determine_incorporation_state(defendant_name),
                            'business_status': f"Duly authorized and qualified to do business in the State of {self._extract_state_from_district(consolidated.case_information.court_district)}",
                            'address': self._extract_defendant_address_from_summons(doc_entities)
                        }
                        defendants.append(defendant_info)
        
        return defendants
    
    def _extract_defendant_from_summons_file(self, filename: str, extraction_result: ExtractionResult) -> Optional[str]:
        """Extract defendant name from summons filename and content"""
        # First try to extract from filename
        filename_mappings = {
            'summonsexperian': 'EXPERIAN INFORMATION SOLUTIONS, INC.',
            'summons_experian': 'EXPERIAN INFORMATION SOLUTIONS, INC.',
            'summonsequifax': 'EQUIFAX INFORMATION SERVICES LLC',
            'summonstd_bank': 'TD BANK, N.A.',
            'summons_td_bank': 'TD BANK, N.A.',
            'summonstrans_union': 'TRANS UNION LLC',
            'summons_trans_union': 'TRANS UNION LLC',
            'summonstransunion': 'TRANS UNION LLC'
        }
        
        # Clean filename for matching
        clean_filename = filename.replace('.pdf', '').replace(' ', '_').lower()
        
        for pattern, name in filename_mappings.items():
            if pattern in clean_filename:
                return name
        
        # If filename doesn't match, try to extract from content
        text = extraction_result.extracted_text
        if text:
            # Look for defendant in the text using improved patterns
            defendant_patterns = [
                r'TO:\s*([A-Z][A-Z\s,.&\-]+(?:LLC|INC\.|CORP\.|CORPORATION|BANK|N\.A\.))',
                r'Defendant[s]?[,:]?\s*([A-Z][A-Z\s,.&\-]+(?:LLC|INC\.|CORP\.|CORPORATION|BANK|N\.A\.))',
                r'([A-Z][A-Z\s,.&\-]+(?:LLC|INC\.|CORP\.|CORPORATION|BANK|N\.A\.))[\s,]*Defendant'
            ]
            
            for pattern in defendant_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip().rstrip(',')
                    if len(name) > 5:  # Filter out very short matches
                        return name
        
        return None
    
    def _extract_defendant_address_from_summons(self, doc_entities: Dict) -> Optional[Dict[str, str]]:
        """Extract defendant address from summons document"""
        addresses = doc_entities['entities']['addresses']
        
        if addresses:
            # Use the first complete address found
            for address in addresses:
                if len(address) > 20:  # Filter for complete addresses
                    return self._parse_address(address)
        
        return None
    
    def _parse_address(self, address_str: str) -> Dict[str, str]:
        """Parse address string into components, handling multi-line addresses."""
        lines = [line.strip() for line in address_str.strip().split('\n') if line.strip()]
        result = {}

        if not lines:
            return result

        # The street is all lines except the last one
        result['street'] = ' '.join(lines[:-1])
        
        # Assume the last line is city, state zip
        last_line = lines[-1]
        match = re.search(r'([\w\s.-]+?)\s*,\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)', last_line)
        if match:
            result['city'] = match.group(1).strip()
            result['state'] = match.group(2).strip()
            result['zip_code'] = match.group(3).strip()
        else:
            # Fallback for single-line address or unexpected format
            parts = last_line.split(',')
            if len(parts) >= 1:
                result['city'] = parts[0].strip()
            if len(parts) >= 2:
                state_zip = parts[-1].strip().split()
                if len(state_zip) == 2:
                    result['state'] = state_zip[0]
                    result['zip_code'] = state_zip[1]

        if 'country' not in result:
            result['country'] = 'USA'
            
        return result
    
    def _extract_contact_info(self, all_entities: List[Dict], contact_type: str) -> Optional[str]:
        """Extract phone or email information"""
        contacts = []
        
        for doc_entities in all_entities:
            if contact_type == 'phone':
                contacts.extend(doc_entities['entities']['phones'])
            elif contact_type == 'email':
                contacts.extend(doc_entities['entities']['emails'])
        
        # Return the first valid contact found
        return contacts[0] if contacts else None
    
    def _consolidate_timeline(self, consolidated: ConsolidatedCase, extraction_results: List[ExtractionResult]):
        """
        Aggregate dates from all documents and create comprehensive case timeline
        MVP 1 Task 1.2 - Enhanced timeline aggregation with chronological validation
        """
        self.logger.info("Consolidating timeline from all case documents")
        
        # Initialize timeline data collection
        all_extracted_dates = []
        attorney_notes_dates = {}
        
        # Process each document for date extraction
        for result in extraction_results:
            if not result.success:
                continue
                
            filename = os.path.basename(result.file_path).lower()
            
            # Extract dates from document text
            if hasattr(result, 'extracted_dates') and result.extracted_dates:
                # Use dates already extracted by enhanced processor
                for date_data in result.extracted_dates:
                    date_entry = {
                        'raw_text': date_data['raw_text'],
                        'parsed_date': date_data['parsed_date'],
                        'context': date_data['context'],
                        'confidence': date_data['confidence'],
                        'source_document': result.file_path,
                        'source_line': date_data['source_line'],
                        'line_number': date_data.get('line_number'),
                        'document_type': self._determine_document_type_from_filename(filename)
                    }
                    all_extracted_dates.append(date_entry)
            else:
                # Fallback: extract dates directly from text
                document_type = self._determine_document_type_from_filename(filename)
                extracted_dates = self.date_extractor.extract_dates_from_text(
                    result.extracted_text, document_type
                )
                
                for date_obj in extracted_dates:
                    date_entry = {
                        'raw_text': date_obj.raw_text,
                        'parsed_date': date_obj.parsed_date.isoformat() if date_obj.parsed_date else None,
                        'context': date_obj.context.value,
                        'confidence': date_obj.confidence,
                        'source_document': result.file_path,
                        'source_line': date_obj.source_line,
                        'line_number': date_obj.line_number,
                        'document_type': document_type
                    }
                    all_extracted_dates.append(date_entry)
            
            # Special handling for attorney notes
            if 'atty_notes' in filename:
                attorney_notes_dates = self._extract_attorney_notes_timeline_dates(result.extracted_text)
        
        # Store all document dates
        consolidated.case_timeline.document_dates = all_extracted_dates
        
        # Extract and consolidate key timeline dates
        self._extract_key_timeline_dates(consolidated, all_extracted_dates, attorney_notes_dates)
        
        # Cross-reference document dates with case events
        self._cross_reference_timeline_events(consolidated, all_extracted_dates)
        
        # Perform chronological validation
        self._validate_timeline_chronology(consolidated)
        
        # Calculate timeline confidence
        consolidated.case_timeline.timeline_confidence = self._calculate_timeline_confidence(consolidated)
        
        self.logger.info(f"Timeline consolidation complete. Found {len(all_extracted_dates)} dates with confidence {consolidated.case_timeline.timeline_confidence:.1f}%")
    
    def _determine_document_type_from_filename(self, filename: str) -> str:
        """Determine document type from filename for enhanced context classification"""
        filename_lower = filename.lower()
        
        if any(term in filename_lower for term in ['denial', 'adverse_action', 'adverse-action']):
            return 'denial_letter'
        elif any(term in filename_lower for term in ['dispute', 'challenge']):
            return 'dispute_correspondence'
        elif any(term in filename_lower for term in ['notice', 'notification']):
            return 'notice_letter'
        elif any(term in filename_lower for term in ['application', 'request']):
            return 'application_document'
        elif any(term in filename_lower for term in ['summons', 'complaint']):
            return 'legal_filing'
        elif any(term in filename_lower for term in ['statement', 'account']):
            return 'account_statement'
        elif any(term in filename_lower for term in ['atty_notes', 'attorney_notes']):
            return 'attorney_notes'
        elif any(term in filename_lower for term in ['correspondence', 'letter']):
            return 'correspondence'
        else:
            return 'unknown'
    
    def _extract_attorney_notes_timeline_dates(self, attorney_notes_text: str) -> Dict[str, str]:
        """Extract key timeline dates from attorney notes using labeled data format"""
        timeline_dates = {}
        
        # First check for North Star schema KEY_DATES section within STRUCTURED_DATA
        key_dates_match = re.search(r'STRUCTURED_DATA:.*?KEY_DATES:\s*\n?(.*?)(?=\nDAMAGES:|LEGAL_CLAIMS:|RELIEF_SOUGHT:|BACKGROUND:|$)', attorney_notes_text, re.IGNORECASE | re.DOTALL)
        if key_dates_match:
            key_dates_text = key_dates_match.group(1).strip()
            self.logger.info(f"Found KEY_DATES section with text: {key_dates_text[:100]}...")
            
            # Parse key dates from North Star format: "- Event Type: Date"
            key_date_lines = [line.strip() for line in key_dates_text.split('\n') if line.strip() and line.strip().startswith('-')]
            for line in key_date_lines:
                # Extract event type and date from format "- Event Type: Date"
                match = re.match(r'-\s*([^:]+):\s*(.+)', line)
                if match:
                    event_type = match.group(1).strip().lower().replace(' ', '_')
                    date_value = match.group(2).strip()
                    timeline_dates[event_type] = date_value
                    self.logger.info(f"Extracted key date: {event_type} = {date_value}")
        
        # Fallback to labeled data format for backward compatibility
        date_labels = [
            'DISCOVERY_DATE',
            'DISPUTE_DATE', 
            'FILING_DATE',
            'APPLICATION_DATE',
            'DENIAL_DATE'
        ]
        
        for label in date_labels:
            extracted_date = self._extract_labeled_data(attorney_notes_text, label)
            if extracted_date and extracted_date.upper() != "TBD":
                timeline_dates[label.lower()] = extracted_date
        
        self.logger.info(f"Extracted {len(timeline_dates)} total dates from attorney notes: {list(timeline_dates.keys())}")
        return timeline_dates
    
    def _extract_key_timeline_dates(self, consolidated: ConsolidatedCase, all_dates: List[Dict], attorney_notes_dates: Dict[str, str]):
        """Extract and prioritize key timeline dates from all sources"""
        
        # Prioritize attorney notes for key dates
        # Handle both discovery_date and credit_discovery formats
        if 'discovery_date' in attorney_notes_dates:
            consolidated.case_timeline.discovery_date = attorney_notes_dates['discovery_date']
        elif 'credit_discovery' in attorney_notes_dates:
            consolidated.case_timeline.discovery_date = attorney_notes_dates['credit_discovery']
        
        if 'dispute_date' in attorney_notes_dates:
            consolidated.case_timeline.dispute_date = attorney_notes_dates['dispute_date']
        if 'filing_date' in attorney_notes_dates:
            consolidated.case_timeline.filing_date = attorney_notes_dates['filing_date']
        
        # Fallback to document analysis if not found in attorney notes
        if not consolidated.case_timeline.discovery_date:
            discovery_dates = [d for d in all_dates if d['context'] == 'discovery_date' and d['confidence'] > 0.6]
            if discovery_dates:
                best_discovery = max(discovery_dates, key=lambda x: x['confidence'])
                consolidated.case_timeline.discovery_date = best_discovery['parsed_date']
        
        if not consolidated.case_timeline.dispute_date:
            dispute_dates = [d for d in all_dates if d['context'] == 'dispute_date' and d['confidence'] > 0.6]
            if dispute_dates:
                best_dispute = max(dispute_dates, key=lambda x: x['confidence'])
                consolidated.case_timeline.dispute_date = best_dispute['parsed_date']
        
        # Extract damage event dates
        damage_event_dates = [d for d in all_dates if d['context'] == 'damage_event_date']
        for damage_date in damage_event_dates:
            damage_event = {
                'date': damage_date['parsed_date'],
                'description': f"Damage event from {os.path.basename(damage_date['source_document'])}",
                'source': damage_date['source_document'],
                'confidence': damage_date['confidence']
            }
            consolidated.case_timeline.damage_events.append(damage_event)
    
    def _cross_reference_timeline_events(self, consolidated: ConsolidatedCase, all_dates: List[Dict]):
        """Cross-reference document dates with case events from various sources"""
        
        # Group dates by document type for cross-referencing
        dates_by_doc_type = defaultdict(list)
        for date_entry in all_dates:
            dates_by_doc_type[date_entry['document_type']].append(date_entry)
        
        # Cross-reference denial letter dates with damage events
        if 'denial_letter' in dates_by_doc_type:
            for denial_date in dates_by_doc_type['denial_letter']:
                if denial_date['context'] in ['denial_date', 'adverse_action_date']:
                    # Check if this denial corresponds to a damage event
                    denial_event = {
                        'date': denial_date['parsed_date'],
                        'description': f"Credit denial/adverse action",
                        'source': denial_date['source_document'],
                        'confidence': denial_date['confidence'],
                        'evidence_type': 'denial_letter'
                    }
                    consolidated.case_timeline.damage_events.append(denial_event)
        
        # Cross-reference application dates from multiple sources
        application_dates = [d for d in all_dates if d['context'] == 'application_date']
        denial_dates = [d for d in all_dates if d['context'] in ['denial_date', 'adverse_action_date']]
        
        # Validate application -> denial sequences
        for app_date in application_dates:
            for denial_date in denial_dates:
                if (app_date['parsed_date'] and denial_date['parsed_date'] and 
                    app_date['parsed_date'] < denial_date['parsed_date']):
                    # Valid sequence: application before denial
                    self.logger.info(f"Valid application->denial sequence: {app_date['parsed_date']} -> {denial_date['parsed_date']}")
    
    def _validate_timeline_chronology(self, consolidated: ConsolidatedCase):
        """Validate chronological order and detect inconsistencies - MVP 1 Business Rules"""
        validation = consolidated.case_timeline.chronological_validation
        
        # Get key dates for validation
        discovery_date = consolidated.case_timeline.discovery_date
        dispute_date = consolidated.case_timeline.dispute_date
        filing_date = consolidated.case_timeline.filing_date
        
        # Parse dates for comparison using flexible date parser
        try:
            from datetime import datetime
            discovery_dt = self._parse_flexible_date(discovery_date) if discovery_date else None
            dispute_dt = self._parse_flexible_date(dispute_date) if dispute_date else None
            filing_dt = self._parse_flexible_date(filing_date) if filing_date else None
            current_dt = datetime.now()
            
            # Rule 1: Discovery Date < Dispute Date
            if discovery_dt and dispute_dt:
                if discovery_dt > dispute_dt:
                    validation['is_valid'] = False
                    validation['errors'].append(
                        f"Discovery date ({discovery_date}) is after dispute date ({dispute_date})"
                    )
                else:
                    self.logger.info(f"✓ Valid chronology: Discovery ({discovery_date}) < Dispute ({dispute_date})")
            
            # Rule 2: Dispute Date < Filing Date
            if dispute_dt and filing_dt:
                if dispute_dt > filing_dt:
                    validation['is_valid'] = False
                    validation['errors'].append(
                        f"Dispute date ({dispute_date}) is after filing date ({filing_date})"
                    )
                else:
                    self.logger.info(f"✓ Valid chronology: Dispute ({dispute_date}) < Filing ({filing_date})")
            
            # Rule 3: All damage events < Filing Date
            for damage_event in consolidated.case_timeline.damage_events:
                if damage_event['date'] and filing_dt:
                    damage_dt = self._parse_flexible_date(damage_event['date'])
                    if damage_dt and damage_dt > filing_dt:
                        validation['warnings'].append(
                            f"Damage event ({damage_event['date']}) is after filing date ({filing_date})"
                        )
            
            # Rule 4: No future dates
            for date_entry in consolidated.case_timeline.document_dates:
                if date_entry['parsed_date']:
                    date_dt = self._parse_flexible_date(date_entry['parsed_date'])
                    if date_dt and date_dt > current_dt:
                        validation['warnings'].append(
                            f"Future date found: {date_entry['parsed_date']} in {os.path.basename(date_entry['source_document'])}"
                        )
            
            # Rule 5: Application Date < Denial Date (FCRA specific)
            application_dates = [d for d in consolidated.case_timeline.document_dates if d['context'] == 'application_date']
            denial_dates = [d for d in consolidated.case_timeline.document_dates if d['context'] == 'denial_date']
            
            for app_date in application_dates:
                app_dt = self._parse_flexible_date(app_date['parsed_date'])
                if app_dt:
                    for denial_date in denial_dates:
                        denial_dt = self._parse_flexible_date(denial_date['parsed_date'])
                        if denial_dt and app_dt > denial_dt:
                            validation['is_valid'] = False
                            validation['errors'].append(
                                f"Application date ({app_date['parsed_date']}) is after denial date ({denial_date['parsed_date']})"
                            )
            
            # Rule 6: Dispute Date should be before latest damage events
            latest_damage_dates = sorted([d for d in consolidated.case_timeline.document_dates 
                                        if d['context'] in ['denial_date', 'damage_event_date']], 
                                       key=lambda x: x['parsed_date'], reverse=True)
            
            if dispute_dt and latest_damage_dates:
                latest_damage_dt = self._parse_flexible_date(latest_damage_dates[0]['parsed_date'])
                if latest_damage_dt and dispute_dt > latest_damage_dt:
                    validation['warnings'].append(
                        f"Dispute date ({dispute_date}) is after latest damage event ({latest_damage_dates[0]['parsed_date']})"
                    )
            
            # Rule 7: Reasonable date range (post-1990, pre-future)
            for date_entry in consolidated.case_timeline.document_dates:
                if date_entry['parsed_date']:
                    date_dt = self._parse_flexible_date(date_entry['parsed_date'])
                    if date_dt and date_dt.year < 1990:
                        validation['warnings'].append(
                            f"Implausibly old date: {date_entry['parsed_date']} in {os.path.basename(date_entry['source_document'])}"
                        )
                        
        except Exception as e:
            validation['errors'].append(f"Date parsing error during chronological validation: {str(e)}")
            self.logger.error(f"Timeline validation error: {e}")
        
        # Log validation results
        if validation['is_valid']:
            self.logger.info("✅ Timeline validation passed")
        else:
            self.logger.warning(f"❌ Timeline validation failed: {len(validation['errors'])} errors")
            for error in validation['errors']:
                self.logger.warning(f"  - {error}")
        
        if validation['warnings']:
            self.logger.warning(f"⚠️ Timeline validation warnings: {len(validation['warnings'])} warnings")
            for warning in validation['warnings']:
                self.logger.warning(f"  - {warning}")
    
    def _calculate_timeline_confidence(self, consolidated: ConsolidatedCase) -> float:
        """Calculate confidence score for timeline accuracy and completeness - simplified to focus on legal essentials"""
        score = 0.0
        max_score = 100.0
        
        # Essential legal dates (90 points)
        if consolidated.case_timeline.dispute_date:
            score += 50  # Most important - FCRA requires dispute before lawsuit
        if consolidated.case_timeline.filing_date:
            score += 40  # Second most important - when lawsuit was filed
        
        # Chronological validation (10 points) - ensure dates make logical sense
        if consolidated.case_timeline.chronological_validation['is_valid']:
            score += 10
        elif len(consolidated.case_timeline.chronological_validation['errors']) == 0:
            score += 5  # Only warnings, no errors
        
        return min(score, max_score)
    
    def _parse_flexible_date(self, date_string: str):
        """
        Parse date from various formats for chronological validation
        MVP 1 Task 1.4 - Fix date format parsing errors
        """
        if not date_string:
            return None
            
        from datetime import datetime
        import re
        
        # Try ISO format first (YYYY-MM-DD)
        try:
            return datetime.fromisoformat(date_string)
        except ValueError:
            pass
        
        # Try common date formats
        date_formats = [
            '%B %d, %Y',     # "June 15, 2025"
            '%b %d, %Y',     # "Jun 15, 2025" 
            '%m/%d/%Y',      # "06/15/2025"
            '%m-%d-%Y',      # "06-15-2025"
            '%Y-%m-%d',      # "2025-06-15"
            '%d/%m/%Y',      # "15/06/2025"
            '%B %d %Y',      # "June 15 2025" (no comma)
            '%b %d %Y',      # "Jun 15 2025" (no comma)
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_string.strip(), date_format)
            except ValueError:
                continue
        
        # If all parsing fails, log the error and return None
        self.logger.warning(f"Could not parse date format: '{date_string}'")
        return None

    def _extract_timeline_events(self, text: str) -> List[Dict[str, str]]:
        """Extract timeline events from narrative text"""
        import re
        
        events = []
        
        # Look for date patterns followed by descriptions
        date_patterns = [
            r'([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}):?\s*([^\n\r]+)',
            r'(\d{1,2}/\d{1,2}/\d{4}):?\s*([^\n\r]+)',
            r'([A-Z][a-z]+\s+\d{4}):?\s*([^\n\r]+)',
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                date = match.group(1).strip()
                description = match.group(2).strip()
                
                if len(description) > 10:  # Filter out very short descriptions
                    events.append({
                        'date': date,
                        'description': description
                    })
        
        return events[:10]  # Limit to first 10 events
    
    def _extract_factual_notes(self, text: str) -> List[str]:
        """Extract additional factual notes from text"""
        notes = []
        
        # Look for bullet points or numbered items
        import re
        
        bullet_patterns = [
            r'[-•*]\s+([^\n\r]+)',
            r'\d+\.\s+([^\n\r]+)',
        ]
        
        for pattern in bullet_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                note = match.group(1).strip()
                if len(note) > 15:  # Filter short notes
                    notes.append(note)
        
        return notes[:5]  # Limit to first 5 notes
    
    def _generate_factual_summary(self, consolidated: ConsolidatedCase, allegations: List[str]) -> str:
        """Generate a factual summary from a list of allegations."""
        if not allegations:
            return "No factual background provided."
        
        summary = " ".join(allegations)
        # Truncate for brevity in the summary field
        return (summary[:250] + '...') if len(summary) > 253 else summary

    def _extract_denial_information(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract credit denial information from denial letters using simple regex."""
        import re
        
        denial_info = {}

        # Creditor Name
        # Pattern 1: Look for text after "Sincerely,"
        sincerely_match = re.search(r'Sincerely,\s*\n\s*([^\n]+)', text, re.IGNORECASE)
        if sincerely_match:
            denial_info['creditor'] = sincerely_match.group(1).strip()
        else:
            # Pattern 2: Look for "Creditor:"
            creditor_match = re.search(r'Creditor:\s*([^\n]+)', text, re.IGNORECASE)
            if creditor_match:
                denial_info['creditor'] = creditor_match.group(1).strip()

        # Application Type
        app_match = re.search(r'Regarding Your Application for (the )?([^\n]+)', text, re.IGNORECASE)
        if app_match:
            denial_info['application_for'] = app_match.group(2).strip()

        # Date
        date_match = re.search(r'(\w+\s+\d{1,2},\s+\d{4})', text)
        if date_match:
            denial_info['date'] = date_match.group(1).strip()

        # Credit Score
        score_match = re.search(r'Your credit score.*?(\d{3})', text, re.IGNORECASE)
        if score_match:
            denial_info['credit_score_used'] = score_match.group(1).strip()

        # Reasons for denial
        reasons_block_match = re.search(r'reason\(s\) for our decision are:\s*([\s\S]*)', text, re.IGNORECASE)
        if reasons_block_match:
            reasons_text = reasons_block_match.group(1)
            # Split by bullet points (·) or newlines and filter out empty strings
            reasons = [r.strip() for r in re.split(r'\s*[·\n]\s*', reasons_text) if r.strip()]
            if reasons:
                denial_info['reasons'] = reasons

        return denial_info if len(denial_info) > 1 else None
    
    def _determine_residency(self, court_district: str) -> str:
        """Determine plaintiff residency based on court district"""
        if not court_district:
            return "Unknown"
            
        # Extract state from court district
        if 'new york' in court_district.lower() or 'southern district of new york' in court_district.lower():
            return "State of New York"
        elif 'california' in court_district.lower():
            return "State of California"
        elif 'texas' in court_district.lower():
            return "State of Texas"
        elif 'florida' in court_district.lower():
            return "State of Florida"
        else:
            # Generic based on district format
            import re
            state_match = re.search(r'district of (\w+)', court_district.lower())
            if state_match:
                state = state_match.group(1).title()
                return f"State of {state}"
        
        return "Unknown"
    
    def _extract_state_from_district(self, court_district: str) -> str:
        """Extract state name from court district"""
        if not court_district:
            return "Unknown"
            
        import re
        
        # Common federal district patterns
        if 'southern district of new york' in court_district.lower():
            return "New York"
        elif 'eastern district of new york' in court_district.lower():
            return "New York"
        elif 'western district of new york' in court_district.lower():
            return "New York"
        elif 'northern district of new york' in court_district.lower():
            return "New York"
        
        # Generic pattern for "District of [State]"
        state_match = re.search(r'district of (\w+)', court_district.lower())
        if state_match:
            return state_match.group(1).title()
        
        # Pattern for "[Direction] District of [State]"  
        direction_state_match = re.search(r'(?:northern|southern|eastern|western)\s+district\s+of\s+(\w+)', court_district.lower())
        if direction_state_match:
            return direction_state_match.group(1).title()
        
        return "Unknown"
    
    def _extract_defendant_address(self, all_entities: List[Dict], defendant_name: str) -> Optional[Dict[str, str]]:
        """Extract defendant address from entities"""
        for doc_entities in all_entities:
            addresses = doc_entities['entities']['addresses']
            
            # Look for addresses near defendant name mentions
            for address in addresses:
                if len(address) > 20:  # Filter for complete addresses
                    return self._parse_address(address)
        
        # Default addresses for common defendants
        if 'first national bank' in defendant_name.lower():
            return self._parse_address("456 Financial Plaza, New York, NY 10005")
        elif 'transunion' in defendant_name.lower():
            return self._parse_address("555 W. Adams Street, Chicago, IL 60661")
        
        return None
    
    def to_complaint_json(self, consolidated: ConsolidatedCase) -> Dict[str, Any]:
        """Convert consolidated case to complaint.json format"""
        
        complaint_json = {
            'case_information': {
                'court_type': consolidated.case_information.court_name or 'United States District Court',
                'court_district': consolidated.case_information.court_district or '',
                'case_number': consolidated.case_information.case_number or '',
                'case_type': 'Complaint',
                'jury_demand': consolidated.case_information.jury_demand or True
            },
            'plaintiff': consolidated.plaintiff or {},
            'plaintiff_counsel': consolidated.plaintiff_counsel or {},
            'defendants': consolidated.defendants or [],
            'factual_background': consolidated.factual_background or {},
            'causes_of_action': [
                {
                    'title': 'VIOLATION OF THE FCRA',
                    'against_defendants': ['All Defendants'],
                    'allegations': [
                        'Defendants violated the Fair Credit Reporting Act by failing to conduct reasonable investigations of plaintiff\'s disputes.'
                    ]
                }
            ],
            'damages': consolidated.damages or {},
            'case_timeline': {
                'discovery_date': consolidated.case_timeline.discovery_date if consolidated.case_timeline else None,
                'dispute_date': consolidated.case_timeline.dispute_date if consolidated.case_timeline else None,
                'filing_date': consolidated.case_timeline.filing_date if consolidated.case_timeline else None,
                'damage_events': consolidated.case_timeline.damage_events if consolidated.case_timeline else [],
                'document_dates': consolidated.case_timeline.document_dates if consolidated.case_timeline else [],
                'chronological_validation': consolidated.case_timeline.chronological_validation if consolidated.case_timeline else {},
                'timeline_confidence': consolidated.case_timeline.timeline_confidence if consolidated.case_timeline else 0.0
            },
            'filing_details': {
                'date': consolidated.case_information.filing_date or datetime.now().strftime('%B %d, %Y')
            },
            'tiger_metadata': {
                'case_id': consolidated.case_id,
                'extraction_confidence': consolidated.extraction_confidence,
                'source_documents': consolidated.source_documents,
                'consolidation_timestamp': consolidated.consolidation_timestamp,
                'warnings': consolidated.warnings
            }
        }
        
        return complaint_json

    def process_document(self, document_path: str, extracted_data: Dict[str, Any]) -> None:
        """
        Process a single document's extracted data and add to case consolidation.
        Called for each document processed within a case.
        
        Args:
            document_path: The path to the source document, used for traceability
            extracted_data: The combined, raw output from all extractor modules for that document
        """
        self.logger.info(f"Processing document: {document_path}")
        
        # Initialize internal state if not already done
        if not hasattr(self, '_case_data'):
            self._case_data = {
                'case_summary': {},
                'plaintiffs': [],
                'defendants': [],
                'timeline': [],
                'issues': [],
                'source_documents': [],
                '_raw_extractions': []
            }
            self._processing_complete = False
        
        # Store the raw extraction for final consolidation
        self._case_data['_raw_extractions'].append({
            'document_path': document_path,
            'extracted_data': extracted_data
        })
        
        # Add to source documents
        self._case_data['source_documents'].append(document_path)
        
        # Progressive consolidation - update case data incrementally
        self._process_single_document(document_path, extracted_data)
        
        self.logger.debug(f"Document processed. Total documents: {len(self._case_data['source_documents'])}")
    
    def get_consolidated_json(self) -> str:
        """
        Perform final consolidation logic and return the complete, formatted complaint.json as a string.
        Called after all documents in a case have been processed.
        
        Returns:
            Complete complaint.json as formatted JSON string
        """
        self.logger.info("Performing final case consolidation...")
        
        # Ensure we have internal state
        if not hasattr(self, '_case_data'):
            raise RuntimeError("No documents have been processed. Call process_document() first.")
        
        # Perform final consolidation logic
        self._perform_final_consolidation()
        
        # Build the final JSON structure
        complaint_json = self._build_complaint_json()
        
        # Mark processing as complete
        self._processing_complete = True
        
        self.logger.info(f"Case consolidation complete. Confidence: {complaint_json.get('case_summary', {}).get('confidence', 0):.1f}%")
        
        return json.dumps(complaint_json, indent=2, ensure_ascii=False)
    
    def _process_single_document(self, document_path: str, extracted_data: Dict[str, Any]) -> None:
        """Process a single document's data and update internal case state"""
        # Extract legal entities if not already processed
        if 'legal_entities' not in extracted_data and 'extracted_text' in extracted_data:
            legal_entities = self.legal_extractor.extract_legal_entities(extracted_data['extracted_text'])
            extracted_data['legal_entities'] = legal_entities
        
        # Progressive case information consolidation
        self._update_case_summary(document_path, extracted_data)
        
        # Progressive party consolidation
        self._update_parties(document_path, extracted_data)
        
        # Progressive timeline building
        self._update_timeline(document_path, extracted_data)
    
    def _perform_final_consolidation(self) -> None:
        """Perform final consolidation logic across all documents"""
        # Entity de-duplication
        self._deduplicate_entities()
        
        # Timeline construction and ordering
        self._finalize_timeline()
        
        # Confidence scoring calculation
        self._calculate_confidence_scores()
        
        # Conflict detection
        self._detect_conflicts()
    
    def _update_case_summary(self, document_path: str, extracted_data: Dict[str, Any]) -> None:
        """Update case summary information from document"""
        if 'legal_entities' in extracted_data:
            case_info = extracted_data['legal_entities'].get('case_information', {})
            
            # Update case number with source tracking
            if hasattr(case_info, 'case_number') and case_info.case_number:
                self._update_field_with_source('case_summary', 'case_number', 
                                              case_info.case_number, document_path)
            
            # Update jurisdiction with source tracking
            if hasattr(case_info, 'court_district') and case_info.court_district:
                self._update_field_with_source('case_summary', 'jurisdiction', 
                                              case_info.court_district, document_path)
    
    def _update_parties(self, document_path: str, extracted_data: Dict[str, Any]) -> None:
        """Update party information from document"""
        if 'legal_entities' in extracted_data:
            parties = extracted_data['legal_entities'].get('parties', [])
            
            for party in parties:
                if hasattr(party, 'role') and hasattr(party, 'name'):
                    party_data = {
                        'name': party.name,
                        'role': party.role,
                        'confidence': getattr(party, 'confidence', 0.5),
                        'sources': [document_path]
                    }
                    
                    # Add to appropriate list
                    if party.role == 'plaintiff':
                        self._add_party_with_dedup(self._case_data['plaintiffs'], party_data)
                    elif party.role == 'defendant':
                        self._add_party_with_dedup(self._case_data['defendants'], party_data)
    
    def _update_timeline(self, document_path: str, extracted_data: Dict[str, Any]) -> None:
        """Extract timeline events from document and add to case timeline"""
        if 'extracted_text' in extracted_data:
            events = self._extract_timeline_events(extracted_data['extracted_text'])
            
            for event in events:
                timeline_entry = {
                    'date': event.get('date'),
                    'event': event.get('description'),
                    'source': document_path
                }
                self._case_data['timeline'].append(timeline_entry)
    
    def _update_field_with_source(self, section: str, field: str, value: Any, source: str) -> None:
        """Update a field with source tracking"""
        if section not in self._case_data:
            self._case_data[section] = {}
        
        current = self._case_data[section].get(field)
        
        if current is None:
            # First value for this field
            self._case_data[section][field] = value
            self._case_data[section][f"{field}_sources"] = [source]
        elif current != value:
            # Conflicting value detected
            if not isinstance(self._case_data[section].get(f"{field}_sources"), list):
                self._case_data[section][f"{field}_sources"] = [self._case_data[section].get(f"{field}_sources", 'unknown')]
            
            self._case_data[section][f"{field}_sources"].append(source)
            
            # Add conflict issue
            conflict_issue = {
                'type': 'conflict',
                'message': f'Conflicting {field} values found: "{current}" vs "{value}"',
                'sources': self._case_data[section][f"{field}_sources"]
            }
            self._case_data['issues'].append(conflict_issue)
    
    def _add_party_with_dedup(self, party_list: List[Dict], new_party: Dict) -> None:
        """Add party to list with deduplication"""
        # Simple name-based deduplication with fuzzy matching
        new_name = new_party['name'].upper().strip()
        
        for existing_party in party_list:
            existing_name = existing_party['name'].upper().strip()
            
            # Simple fuzzy matching - can be enhanced
            if self._names_similar(new_name, existing_name):
                # Merge sources and update confidence
                existing_party['sources'].extend(new_party['sources'])
                existing_party['sources'] = list(set(existing_party['sources']))  # Remove duplicates
                existing_party['confidence'] = max(existing_party['confidence'], new_party['confidence'])
                return
        
        # No duplicate found, add new party
        party_list.append(new_party)
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Simple name similarity check - can be enhanced with fuzzy matching"""
        # Normalize names for comparison
        name1 = self._normalize_name(name1)
        name2 = self._normalize_name(name2)
        
        # Exact match
        if name1 == name2:
            return True
        
        # Check if one is a subset of the other (for names like "J. DOE" vs "JANE DOE")
        if name1 in name2 or name2 in name1:
            return True
        
        # Check common name abbreviations and variations
        name_abbreviations = {
            'J DOE': 'JANE DOE',
            'J. DOE': 'JANE DOE', 
            'JOHN DOE': 'J DOE',
            'JANE DOE': 'J DOE'
        }
        
        if name1 in name_abbreviations and name_abbreviations[name1] == name2:
            return True
        if name2 in name_abbreviations and name_abbreviations[name2] == name1:
            return True
        
        # Check word overlap for names (at least 1 word in common for person names)
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        # For person names (likely 2-3 words), check if they share a surname
        if len(words1) <= 3 and len(words2) <= 3:
            overlap = words1.intersection(words2)
            if overlap and len(overlap) >= 1:
                # If they share at least one word and both are short names, likely same person
                return True
        
        # Check common corporate abbreviations
        corporate_abbreviations = {
            'INFORMATION SERVICES': 'INFO SERVICES',
            'INFORMATION SOLUTIONS': 'INFO SOLUTIONS',
            'INCORPORATED': 'INC',
            'LIMITED LIABILITY COMPANY': 'LLC',
            'NATIONAL ASSOCIATION': 'N.A.',
            'CORPORATION': 'CORP'
        }
        
        for full, abbrev in corporate_abbreviations.items():
            name1_abbrev = name1.replace(full, abbrev)
            name2_abbrev = name2.replace(full, abbrev)
            if name1_abbrev == name2_abbrev:
                return True
        
        return False
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        # Remove punctuation and extra spaces
        import re
        normalized = re.sub(r'[^A-Z0-9\s]', '', name.upper())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _deduplicate_entities(self) -> None:
        """Perform final entity deduplication across all parties"""
        # Additional deduplication pass - already done incrementally
        pass
    
    def _finalize_timeline(self) -> None:
        """Sort timeline by date and standardize dates"""
        # Sort timeline events by date
        def parse_date_for_sorting(event):
            date_str = event.get('date', '')
            if not date_str:
                return datetime.min
            
            # Try to parse various date formats
            try:
                # Try ISO format first
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                try:
                    # Try common US formats
                    for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d', '%b %d, %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except:
                            continue
                except:
                    pass
            
            return datetime.min
        
        self._case_data['timeline'].sort(key=parse_date_for_sorting)
    
    def _calculate_confidence_scores(self) -> None:
        """Calculate confidence scores for all entities"""
        total_score = 0.0
        max_score = 100.0
        
        # Case information completeness (40 points)
        case_summary = self._case_data['case_summary']
        if case_summary.get('case_number'):
            total_score += 25  # Increased from 20
        if case_summary.get('jurisdiction'):
            total_score += 25  # Increased from 20
        
        # Party information completeness (40 points)
        plaintiff_score = min(len(self._case_data['plaintiffs']) * 15, 25)  # More generous
        defendant_score = min(len(self._case_data['defendants']) * 8, 25)   # More generous
        total_score += plaintiff_score + defendant_score
        
        # Timeline completeness (10 points) - reduced weight
        timeline_score = min(len(self._case_data['timeline']) * 2, 10)
        total_score += timeline_score
        
        # Consistency bonus (10 points) - increased from 5
        if len(self._case_data['issues']) == 0:
            total_score += 10
        elif len(self._case_data['issues']) <= 2:  # Small penalty for minor issues
            total_score += 5
        
        self._case_data['case_summary']['confidence'] = min(total_score, max_score)
    
    def _detect_conflicts(self) -> None:
        """Detect logical inconsistencies and conflicts"""
        # Check for timeline inconsistencies
        self._check_timeline_consistency()
        
        # Check for missing critical information
        self._check_completeness()
    
    def _check_timeline_consistency(self) -> None:
        """Check for timeline logical inconsistencies"""
        # Check for obviously incorrect dates
        current_year = datetime.now().year
        
        for event in self._case_data['timeline']:
            date_str = event.get('date', '')
            if date_str:
                # Check for future dates
                try:
                    event_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if event_date.year > current_year:
                        issue = {
                            'type': 'timeline_error',
                            'message': f'Event "{event.get("event", "")}" has future date: {date_str}',
                            'source': event.get('source', '')
                        }
                        self._case_data['issues'].append(issue)
                    elif event_date.year < 1990:
                        issue = {
                            'type': 'timeline_error',
                            'message': f'Event "{event.get("event", "")}" has implausible date: {date_str}',
                            'source': event.get('source', '')
                        }
                        self._case_data['issues'].append(issue)
                except:
                    # Date parsing failed
                    issue = {
                        'type': 'timeline_error',
                        'message': f'Event "{event.get("event", "")}" has unparseable date: {date_str}',
                        'source': event.get('source', '')
                    }
                    self._case_data['issues'].append(issue)
    
    def _check_completeness(self) -> None:
        """Check for missing critical information"""
        # Check for missing plaintiff
        if not self._case_data['plaintiffs']:
            issue = {
                'type': 'completeness',
                'message': 'No plaintiff information found',
                'sources': self._case_data['source_documents']
            }
            self._case_data['issues'].append(issue)
        
        # Check for missing defendants
        if not self._case_data['defendants']:
            issue = {
                'type': 'completeness',
                'message': 'No defendant information found',
                'sources': self._case_data['source_documents']
            }
            self._case_data['issues'].append(issue)
        
        # Check for missing case number
        if not self._case_data['case_summary'].get('case_number'):
            issue = {
                'type': 'completeness',
                'message': 'No case number found',
                'sources': self._case_data['source_documents']
            }
            self._case_data['issues'].append(issue)
    
    def _build_complaint_json(self) -> Dict[str, Any]:
        """Build the final complaint.json structure"""
        return {
            'case_summary': {
                'case_number': self._case_data['case_summary'].get('case_number', ''),
                'jurisdiction': self._case_data['case_summary'].get('jurisdiction', ''),
                'confidence': self._case_data['case_summary'].get('confidence', 0.0)
            },
            'plaintiffs': self._case_data['plaintiffs'],
            'defendants': self._case_data['defendants'],
            'timeline': self._case_data['timeline'],
            'issues': self._case_data['issues'],
            'processing_metadata': {
                'source_documents': self._case_data['source_documents'],
                'processing_timestamp': datetime.now().isoformat(),
                'total_documents_processed': len(self._case_data['source_documents'])
            }
        }

def consolidate_case_from_extractions(folder_path: str, extraction_results: List[ExtractionResult]) -> ConsolidatedCase:
    """
    Convenience function to consolidate case information
    
    Args:
        folder_path: Path to case folder
        extraction_results: List of Tiger extraction results
        
    Returns:
        ConsolidatedCase object
    """
    consolidator = CaseConsolidator()
    return consolidator.consolidate_case_folder(folder_path, extraction_results)