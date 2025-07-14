"""
Damage Extractor Module

Extracts and categorizes damages from attorney notes DAMAGES section.
Supports structured damage parsing with evidence tracking.
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DamageItem:
    """Represents a single damage claim extracted from attorney notes"""
    category: str           # "credit_denial", "existing_credit", "employment", "housing", "emotional", "time_resources"
    type: str              # "auto_loan", "credit_card", "limit_reduction", etc.
    entity: str            # "Wells Fargo", "Citibank", etc.
    date: str              # "April 20, 2025" or "Unknown"
    evidence_available: bool # True if denial letter/documentation mentioned
    description: str       # Full damage description
    selected: bool = False # For review interface (default unselected)
    amount: Optional[str] = None  # Optional damage amount if specified

class DamageExtractor:
    """Extracts structured damages from attorney notes DAMAGES section"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_damage_patterns()
    
    def _setup_damage_patterns(self):
        """Define regex patterns for different damage types"""
        self.damage_patterns = {
            # Credit Application Denials
            r'Denied Auto Loan:\s*(.+?),\s*(.+?)\.\s*(.*)': ('credit_denial', 'auto_loan'),
            r'Denied Car Loan:\s*(.+?),\s*(.+?)\.\s*(.*)': ('credit_denial', 'auto_loan'),
            r'Denied Credit Card:\s*(.+?),\s*(.+?)\.\s*(.*)': ('credit_denial', 'credit_card'),
            r'Denied Mortgage:\s*(.+?),\s*(.+?)\.\s*(.*)': ('credit_denial', 'mortgage'),
            r'Denied Personal Loan:\s*(.+?),\s*(.+?)\.\s*(.*)': ('credit_denial', 'personal_loan'),
            r'Denied Store Credit:\s*(.+?),\s*(.+?)\.\s*(.*)': ('credit_denial', 'store_credit'),
            r'Denied Loan:\s*(.+?),\s*(.+?)\.\s*(.*)': ('credit_denial', 'loan_general'),
            
            # Existing Credit Impacts
            r'Credit Limit Reduction:\s*(.+?),\s*(.+?)\.\s*(.*)': ('existing_credit', 'limit_reduction'),
            r'Interest Rate Increase:\s*(.+?),\s*(.+?)\.\s*(.*)': ('existing_credit', 'rate_increase'),
            r'Account Closure:\s*(.+?),\s*(.+?)\.\s*(.*)': ('existing_credit', 'account_closure'),
            r'Unfavorable Terms:\s*(.+?),\s*(.+?)\.\s*(.*)': ('existing_credit', 'unfavorable_terms'),
            
            # Employment Issues
            r'Employment Background Check:\s*(.+?),\s*(.+?)\.\s*(.*)': ('employment', 'background_check'),
            r'Job Offer Withdrawal:\s*(.+?),\s*(.+?)\.\s*(.*)': ('employment', 'job_offer_withdrawal'),
            r'Promotion Denial:\s*(.+?),\s*(.+?)\.\s*(.*)': ('employment', 'promotion_denial'),
            r'Employment Issue:\s*(.+?),\s*(.+?)\.\s*(.*)': ('employment', 'employment_general'),
            
            # Housing Issues
            r'Rental Application Denial:\s*(.+?),\s*(.+?)\.\s*(.*)': ('housing', 'rental_denial'),
            r'Rental Denial:\s*(.+?),\s*(.+?)\.\s*(.*)': ('housing', 'rental_denial'),
            r'Increased Security Deposit:\s*(.+?),\s*(.+?)\.\s*(.*)': ('housing', 'increased_deposit'),
            r'Housing Issue:\s*(.+?),\s*(.+?)\.\s*(.*)': ('housing', 'housing_general'),
        }
        
        # Special patterns for non-structured damages
        self.special_patterns = {
            r'Emotional Distress:\s*(.*)': ('emotional', 'emotional_distress'),
            r'Time and Resources:\s*(.*)': ('time_resources', 'time_and_resources'),
            r'Significant emotional distress.*': ('emotional', 'emotional_distress'),
            r'Time wasted.*': ('time_resources', 'time_wasted'),
            r'Frustration.*': ('emotional', 'frustration'),
        }
        
        # Evidence indicators
        self.evidence_indicators = [
            'denial letter', 'have denial letter', 'letter attached',
            'documentation available', 'have documentation', 'have letter',
            'copy available', 'denial notice', 'written denial'
        ]
    
    def extract_damages(self, attorney_notes_text: str) -> List[DamageItem]:
        """
        Extract structured damages from attorney notes DAMAGES section
        
        Args:
            attorney_notes_text: Full text of attorney notes
            
        Returns:
            List of DamageItem objects representing extracted damages
        """
        damages = []
        
        try:
            # Extract DAMAGES section
            damage_section = self._extract_damages_section(attorney_notes_text)
            if not damage_section:
                self.logger.warning("No DAMAGES section found in attorney notes")
                return damages
            
            self.logger.info(f"Found DAMAGES section with {len(damage_section.split(chr(10)))} lines")
            
            # Parse each damage line
            for line_num, line in enumerate(damage_section.split('\n'), 1):
                line = line.strip()
                if not line or not line.startswith('-'):
                    continue
                
                # Remove leading dash and whitespace
                damage_text = line[1:].strip()
                if not damage_text:
                    continue
                
                damage = self._parse_damage_line(damage_text, line_num)
                if damage:
                    damages.append(damage)
                    self.logger.debug(f"Extracted damage: {damage.category}/{damage.type} - {damage.entity}")
                else:
                    self.logger.warning(f"Could not parse damage line {line_num}: {damage_text}")
            
            self.logger.info(f"Successfully extracted {len(damages)} damages")
            return damages
            
        except Exception as e:
            self.logger.error(f"Error extracting damages: {str(e)}")
            return damages
    
    def _extract_damages_section(self, text: str) -> Optional[str]:
        """Extract the DAMAGES: section from attorney notes"""
        # Look for DAMAGES: section (case insensitive)
        match = re.search(r'DAMAGES:\s*([\s\S]*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Alternative pattern: look for DAMAGES section without colon
        match = re.search(r'DAMAGES\s*\n([\s\S]*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _parse_damage_line(self, damage_text: str, line_num: int = 0) -> Optional[DamageItem]:
        """
        Parse individual damage line into structured DamageItem
        
        Args:
            damage_text: Text of damage line (without leading dash)
            line_num: Line number for debugging
            
        Returns:
            DamageItem object or None if parsing failed
        """
        # Try structured patterns first
        for pattern, (category, damage_type) in self.damage_patterns.items():
            match = re.match(pattern, damage_text, re.IGNORECASE)
            if match:
                entity = match.group(1).strip()
                date = match.group(2).strip()
                evidence_text = match.group(3).strip() if len(match.groups()) >= 3 else ""
                
                # Check for evidence indicators
                evidence_available = self._has_evidence_indicators(evidence_text)
                
                return DamageItem(
                    category=category,
                    type=damage_type,
                    entity=entity,
                    date=date,
                    evidence_available=evidence_available,
                    description=damage_text,
                    selected=False
                )
        
        # Try special patterns for non-structured damages
        for pattern, (category, damage_type) in self.special_patterns.items():
            match = re.match(pattern, damage_text, re.IGNORECASE)
            if match:
                description = match.group(1).strip() if match.group(1) else damage_text
                
                return DamageItem(
                    category=category,
                    type=damage_type,
                    entity="N/A",
                    date="N/A",
                    evidence_available=False,
                    description=description,
                    selected=False
                )
        
        # Fallback: create generic damage item
        self.logger.debug(f"Using fallback parsing for line {line_num}: {damage_text}")
        return self._create_fallback_damage(damage_text)
    
    def _has_evidence_indicators(self, text: str) -> bool:
        """Check if text contains evidence availability indicators"""
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.evidence_indicators)
    
    def _create_fallback_damage(self, damage_text: str) -> DamageItem:
        """Create a generic damage item when specific parsing fails"""
        # Try to categorize based on keywords
        text_lower = damage_text.lower()
        
        if any(word in text_lower for word in ['denied', 'denial', 'rejected', 'decline']):
            category = 'credit_denial'
            damage_type = 'unspecified_denial'
        elif any(word in text_lower for word in ['emotional', 'distress', 'stress', 'anxiety', 'frustration']):
            category = 'emotional'
            damage_type = 'emotional_distress'
        elif any(word in text_lower for word in ['time', 'hours', 'cost', 'expense', 'resource']):
            category = 'time_resources'
            damage_type = 'time_and_resources'
        elif any(word in text_lower for word in ['limit', 'reduction', 'decrease', 'increase', 'rate']):
            category = 'existing_credit'
            damage_type = 'credit_impact'
        elif any(word in text_lower for word in ['job', 'employment', 'work', 'background']):
            category = 'employment'
            damage_type = 'employment_issue'
        elif any(word in text_lower for word in ['rental', 'housing', 'apartment', 'lease']):
            category = 'housing'
            damage_type = 'housing_issue'
        else:
            category = 'other'
            damage_type = 'unspecified'
        
        evidence_available = self._has_evidence_indicators(damage_text)
        
        return DamageItem(
            category=category,
            type=damage_type,
            entity="Unspecified",
            date="Unspecified",
            evidence_available=evidence_available,
            description=damage_text,
            selected=False
        )
    
    def categorize_damages(self, damages: List[DamageItem]) -> Dict[str, List[DamageItem]]:
        """
        Categorize damages into groups for easier review
        
        Args:
            damages: List of DamageItem objects
            
        Returns:
            Dictionary with category names as keys and lists of damages as values
        """
        categorized = {
            'credit_denials': [],
            'existing_credit_impacts': [],
            'employment_issues': [],
            'housing_issues': [],
            'emotional_distress': [],
            'time_and_resources': [],
            'other': []
        }
        
        category_mapping = {
            'credit_denial': 'credit_denials',
            'existing_credit': 'existing_credit_impacts',
            'employment': 'employment_issues',
            'housing': 'housing_issues',
            'emotional': 'emotional_distress',
            'time_resources': 'time_and_resources'
        }
        
        for damage in damages:
            category_key = category_mapping.get(damage.category, 'other')
            categorized[category_key].append(damage)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def get_damage_summary(self, damages: List[DamageItem]) -> Dict[str, int]:
        """
        Get summary statistics for extracted damages
        
        Args:
            damages: List of DamageItem objects
            
        Returns:
            Dictionary with damage counts by category
        """
        categorized = self.categorize_damages(damages)
        summary = {}
        
        for category, items in categorized.items():
            summary[category] = len(items)
            evidence_count = sum(1 for item in items if item.evidence_available)
            summary[f"{category}_with_evidence"] = evidence_count
        
        summary['total_damages'] = len(damages)
        summary['total_with_evidence'] = sum(1 for damage in damages if damage.evidence_available)
        
        return summary