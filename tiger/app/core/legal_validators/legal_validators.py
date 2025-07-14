"""
Specialized Legal Validators for Tiger Engine
Validates legal sufficiency and consistency of complaint.json data
"""

import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """Abstract base class for all legal validators"""
    
    @abstractmethod
    def validate(self, complaint_data: Dict[str, Any]) -> List[str]:
        """
        Validate complaint data and return list of error/warning messages
        
        Args:
            complaint_data: Complete complaint.json data as dictionary
            
        Returns:
            List of error/warning messages (empty list means validation passes)
        """
        pass


class FCRAValidator(BaseValidator):
    """Validates Fair Credit Reporting Act case requirements"""
    
    # Known credit bureaus
    CREDIT_BUREAUS = {
        'experian', 'transunion', 'equifax',
        'experian information solutions',
        'transunion llc',
        'equifax information services'
    }
    
    # Known furnisher indicators
    FURNISHER_INDICATORS = {
        'bank', 'credit', 'financial', 'capital', 'lending',
        'mortgage', 'card', 'union', 'fund', 'services'
    }
    
    def validate(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate FCRA case requirements"""
        errors = []
        
        try:
            # Check for credit bureau defendants
            if not self._has_credit_bureau_defendant(complaint_data):
                errors.append("FCRA case missing credit bureau defendant (Experian, TransUnion, or Equifax)")
            
            # Check for furnisher defendant
            if not self._has_furnisher_defendant(complaint_data):
                errors.append("FCRA case missing furnisher defendant (bank, creditor, or data furnisher)")
            
            # Check for dispute evidence in timeline
            if not self._has_dispute_evidence(complaint_data):
                errors.append("FCRA case missing dispute evidence in timeline")
            
            # Check for adverse action event
            if not self._has_adverse_action(complaint_data):
                errors.append("FCRA case missing adverse action event (credit denial, rate increase, etc.)")
                
        except Exception as e:
            logger.error(f"Error in FCRAValidator: {e}")
            errors.append(f"FCRA validation error: {str(e)}")
        
        return errors
    
    def _has_credit_bureau_defendant(self, complaint_data: Dict[str, Any]) -> bool:
        """Check if case includes credit bureau as defendant"""
        defendants = complaint_data.get('defendants', [])
        
        for defendant in defendants:
            defendant_name = defendant.get('name', '').lower()
            
            # Check against known credit bureaus
            for bureau in self.CREDIT_BUREAUS:
                if bureau in defendant_name:
                    return True
        
        return False
    
    def _has_furnisher_defendant(self, complaint_data: Dict[str, Any]) -> bool:
        """Check if case includes furnisher as defendant"""
        defendants = complaint_data.get('defendants', [])
        
        for defendant in defendants:
            defendant_name = defendant.get('name', '').lower()
            
            # Check against furnisher indicators
            for indicator in self.FURNISHER_INDICATORS:
                if indicator in defendant_name:
                    return True
        
        return False
    
    def _has_dispute_evidence(self, complaint_data: Dict[str, Any]) -> bool:
        """Check timeline for dispute evidence"""
        timeline = complaint_data.get('timeline', [])
        
        dispute_keywords = [
            'dispute', 'disputed', 'disputing', 'reinvestigation',
            'investigation', 'challenged', 'contested', 'complaint',
            'correction', 'error', 'inaccurate', 'incorrect'
        ]
        
        for event in timeline:
            event_text = event.get('event', '').lower()
            
            for keyword in dispute_keywords:
                if keyword in event_text:
                    return True
        
        return False
    
    def _has_adverse_action(self, complaint_data: Dict[str, Any]) -> bool:
        """Check timeline for adverse action evidence"""
        timeline = complaint_data.get('timeline', [])
        
        adverse_keywords = [
            'denied', 'denial', 'rejected', 'declined', 'adverse action',
            'rate increase', 'higher rate', 'unfavorable terms',
            'credit limit', 'reduced limit', 'closed account'
        ]
        
        for event in timeline:
            event_text = event.get('event', '').lower()
            
            for keyword in adverse_keywords:
                if keyword in event_text:
                    return True
        
        return False


class CompletenessValidator(BaseValidator):
    """Validates completeness of critical complaint information"""
    
    def validate(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate completeness of complaint data"""
        errors = []
        
        try:
            # Validate plaintiff information
            errors.extend(self._validate_plaintiff(complaint_data))
            
            # Validate defendants
            errors.extend(self._validate_defendants(complaint_data))
            
            # Validate case information
            errors.extend(self._validate_case_information(complaint_data))
            
            # Validate timeline
            errors.extend(self._validate_timeline_presence(complaint_data))
            
        except Exception as e:
            logger.error(f"Error in CompletenessValidator: {e}")
            errors.append(f"Completeness validation error: {str(e)}")
        
        return errors
    
    def _validate_plaintiff(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate plaintiff information completeness"""
        errors = []
        
        plaintiff = complaint_data.get('plaintiff', {})
        
        # Check plaintiff name
        if not plaintiff.get('name'):
            errors.append("Missing plaintiff name")
        
        # Check plaintiff address
        address = plaintiff.get('address', {})
        if not address:
            errors.append("Missing plaintiff address")
        else:
            if not address.get('street'):
                errors.append("Missing plaintiff street address")
            if not address.get('city_state_zip') and not (address.get('city') and address.get('state')):
                errors.append("Missing plaintiff city/state information")
        
        return errors
    
    def _validate_defendants(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate defendants information completeness"""
        errors = []
        
        defendants = complaint_data.get('defendants', [])
        
        if not defendants:
            errors.append("No defendants specified")
            return errors
        
        for i, defendant in enumerate(defendants):
            if not defendant.get('name'):
                errors.append(f"Missing name for defendant #{i+1}")
        
        return errors
    
    def _validate_case_information(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate case information completeness"""
        errors = []
        
        case_info = complaint_data.get('case_information', {})
        
        if not case_info.get('jurisdiction'):
            errors.append("Missing court jurisdiction")
        
        if not case_info.get('case_number'):
            errors.append("Missing case number")
        
        return errors
    
    def _validate_timeline_presence(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate timeline information presence"""
        errors = []
        
        timeline = complaint_data.get('timeline', [])
        
        if not timeline:
            errors.append("Missing timeline events")
        elif len(timeline) < 2:
            errors.append("Timeline should include multiple events to establish case chronology")
        
        return errors


class TimelineValidator(BaseValidator):
    """Validates logical consistency in case timeline"""
    
    def validate(self, complaint_data: Dict[str, Any]) -> List[str]:
        """Validate timeline logical consistency"""
        errors = []
        
        try:
            timeline = complaint_data.get('timeline', [])
            
            if not timeline:
                return errors  # No timeline to validate
            
            # Validate individual event dates
            errors.extend(self._validate_event_dates(timeline))
            
            # Validate chronological order
            errors.extend(self._validate_chronological_order(timeline))
            
            # Validate date relationships
            errors.extend(self._validate_date_relationships(timeline))
            
        except Exception as e:
            logger.error(f"Error in TimelineValidator: {e}")
            errors.append(f"Timeline validation error: {str(e)}")
        
        return errors
    
    def _validate_event_dates(self, timeline: List[Dict[str, Any]]) -> List[str]:
        """Validate individual event dates are plausible"""
        errors = []
        
        current_year = datetime.now().year
        earliest_plausible_year = 1900
        
        for i, event in enumerate(timeline):
            date_str = event.get('date', '')
            
            if not date_str:
                continue  # Skip events without dates
            
            try:
                # Try to parse the date
                parsed_date = self._parse_date(date_str)
                
                if parsed_date:
                    # Check if date is in the future
                    if parsed_date > datetime.now():
                        errors.append(f"Timeline event #{i+1} has future date: {date_str}")
                    
                    # Check if date is implausibly old
                    if parsed_date.year < earliest_plausible_year:
                        errors.append(f"Timeline event #{i+1} has implausibly old date: {date_str}")
                        
            except Exception as e:
                errors.append(f"Timeline event #{i+1} has invalid date format: {date_str}")
        
        return errors
    
    def _validate_chronological_order(self, timeline: List[Dict[str, Any]]) -> List[str]:
        """Validate events are in chronological order"""
        errors = []
        
        parsed_events = []
        
        # Parse all events with valid dates
        for i, event in enumerate(timeline):
            date_str = event.get('date', '')
            
            if date_str:
                try:
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        parsed_events.append((i, parsed_date, event))
                except:
                    pass  # Skip unparseable dates
        
        # Check chronological order
        for i in range(1, len(parsed_events)):
            prev_idx, prev_date, prev_event = parsed_events[i-1]
            curr_idx, curr_date, curr_event = parsed_events[i]
            
            if curr_date < prev_date:
                errors.append(f"Timeline events #{prev_idx+1} and #{curr_idx+1} are out of chronological order")
        
        return errors
    
    def _validate_date_relationships(self, timeline: List[Dict[str, Any]]) -> List[str]:
        """Validate logical relationships between dates"""
        errors = []
        
        # Look for specific event types and their logical relationships
        dispute_dates = []
        adverse_action_dates = []
        filing_dates = []
        
        for i, event in enumerate(timeline):
            date_str = event.get('date', '')
            event_text = event.get('event', '').lower()
            
            if not date_str:
                continue
            
            try:
                parsed_date = self._parse_date(date_str)
                if not parsed_date:
                    continue
                
                # Categorize events
                if any(keyword in event_text for keyword in ['dispute', 'disputed', 'reinvestigation']):
                    dispute_dates.append((i, parsed_date))
                
                if any(keyword in event_text for keyword in ['denied', 'adverse action', 'rejected']):
                    adverse_action_dates.append((i, parsed_date))
                
                if any(keyword in event_text for keyword in ['filed', 'filing', 'complaint filed']):
                    filing_dates.append((i, parsed_date))
                    
            except:
                continue
        
        # Validate that disputes typically come before filing
        if dispute_dates and filing_dates:
            latest_dispute = max(dispute_dates, key=lambda x: x[1])
            earliest_filing = min(filing_dates, key=lambda x: x[1])
            
            if latest_dispute[1] > earliest_filing[1]:
                errors.append("Legal complaint filed before credit report disputes were completed")
        
        return errors
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using multiple formats"""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try regex-based parsing for more flexible formats
        try:
            # Match patterns like "July 15, 2024" or "15 July 2024"
            month_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
            
            # Pattern: Month Day, Year
            match = re.search(rf'{month_pattern}\s+(\d{{1,2}}),?\s+(\d{{4}})', date_str.lower())
            if match:
                month_str, day_str, year_str = match.groups()
                
                # Convert month name to number
                month_num = self._month_name_to_number(month_str)
                if month_num:
                    return datetime(int(year_str), month_num, int(day_str))
            
        except:
            pass
        
        return None
    
    def _month_name_to_number(self, month_str: str) -> Optional[int]:
        """Convert month name to number"""
        months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        return months.get(month_str.lower())


class LegalValidatorSuite:
    """Orchestrates all legal validators"""
    
    def __init__(self):
        self.validators = [
            FCRAValidator(),
            CompletenessValidator(),
            TimelineValidator()
        ]
        self.logger = logging.getLogger(__name__)
    
    def validate_complaint(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all legal validators on complaint data
        
        Args:
            complaint_data: Complete complaint.json data as dictionary
            
        Returns:
            Dictionary with validation results and any errors/warnings
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'validator_results': {}
        }
        
        try:
            for validator in self.validators:
                validator_name = validator.__class__.__name__
                
                self.logger.info(f"Running {validator_name}")
                
                validator_errors = validator.validate(complaint_data)
                validation_results['validator_results'][validator_name] = validator_errors
                
                if validator_errors:
                    self.logger.warning(f"{validator_name} found {len(validator_errors)} issues")
                    validation_results['errors'].extend(validator_errors)
                    validation_results['is_valid'] = False
                else:
                    self.logger.info(f"{validator_name} passed")
            
            # Log summary
            if validation_results['is_valid']:
                self.logger.info("All legal validators passed")
            else:
                self.logger.warning(f"Legal validation failed with {len(validation_results['errors'])} errors")
                
        except Exception as e:
            self.logger.error(f"Error in legal validation suite: {e}")
            validation_results['errors'].append(f"Validation suite error: {str(e)}")
            validation_results['is_valid'] = False
        
        return validation_results