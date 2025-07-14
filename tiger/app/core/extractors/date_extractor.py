"""
Enhanced Date Extractor - MVP 1 Implementation for Chronological Validation
Extracts dates from legal documents with context awareness for timeline validation
"""

import re
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DateContext(Enum):
    """Types of date contexts in legal documents"""
    DISCOVERY_DATE = "discovery_date"
    DISPUTE_DATE = "dispute_date"
    APPLICATION_DATE = "application_date"
    DENIAL_DATE = "denial_date"
    ADVERSE_ACTION_DATE = "adverse_action_date"
    NOTICE_DATE = "notice_date"
    RESPONSE_DATE = "response_date"
    TRANSACTION_DATE = "transaction_date"
    FILING_DATE = "filing_date"
    DAMAGE_EVENT_DATE = "damage_event_date"
    UNKNOWN = "unknown"

@dataclass
class ExtractedDate:
    """Represents a date extracted from a document with context"""
    raw_text: str                    # Original text containing the date
    parsed_date: Optional[date]      # Parsed date object
    context: DateContext            # Type of date based on surrounding text
    confidence: float               # Confidence score (0.0-1.0)
    source_line: str               # Full line where date was found
    line_number: Optional[int]      # Line number in document
    document_section: Optional[str] # Section of document (if identifiable)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'raw_text': self.raw_text,
            'parsed_date': self.parsed_date.isoformat() if self.parsed_date else None,
            'context': self.context.value,
            'confidence': self.confidence,
            'source_line': self.source_line,
            'line_number': self.line_number,
            'document_section': self.document_section
        }

class EnhancedDateExtractor:
    """Enhanced date extraction with context awareness for legal documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Comprehensive date patterns
        self.date_patterns = [
            # MM/DD/YYYY formats
            (r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b', '%m/%d/%Y'),
            (r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})\b', '%m/%d/%y'),
            
            # YYYY-MM-DD formats (ISO)
            (r'\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b', '%Y/%m/%d'),
            
            # Full month names
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b', '%B %d %Y'),
            
            # Abbreviated month names
            (r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})\b', '%b %d %Y'),
            
            # Day Month Year format
            (r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b', '%d %B %Y'),
            (r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{4})\b', '%d %b %Y'),
        ]
        
        # Context indicators for different types of dates
        self.context_patterns = {
            DateContext.DISCOVERY_DATE: [
                r'discover(ed|y)',
                r'found out',
                r'became aware',
                r'notice(d)?.*error',
                r'realize(d)?.*mistake'
            ],
            DateContext.DISPUTE_DATE: [
                r'dispute(d)?',
                r'contested',
                r'challenge(d)?',
                r'object(ed)?.*to',
                r'sent.*dispute',
                r'filed.*dispute'
            ],
            DateContext.APPLICATION_DATE: [
                r'appli(ed|cation)',
                r'submitted.*application',
                r'filed.*application',
                r'request(ed)?.*credit',
                r'sought.*loan'
            ],
            DateContext.DENIAL_DATE: [
                r'deni(ed|al)',
                r'reject(ed|ion)',
                r'decline(d)?',
                r'refused',
                r'turn(ed)?.*down',
                r'adverse.*action'
            ],
            DateContext.ADVERSE_ACTION_DATE: [
                r'adverse.*action',
                r'notice.*denial',
                r'unfavorable.*decision',
                r'credit.*decision'
            ],
            DateContext.NOTICE_DATE: [
                r'notice.*dat(e|ed)',
                r'notification.*dat(e|ed)',
                r'inform(ed)?.*on',
                r'letter.*dat(e|ed)',
                r'correspondence.*dat(e|ed)'
            ],
            DateContext.RESPONSE_DATE: [
                r'respond(ed)?',
                r'reply.*dat(e|ed)',
                r'answer(ed)?',
                r'response.*receiv(ed)?'
            ],
            DateContext.FILING_DATE: [
                r'fil(ed|ing)',
                r'submit(ted)?.*court',
                r'commenced.*action',
                r'instituted.*proceeding'
            ],
            DateContext.DAMAGE_EVENT_DATE: [
                r'damage.*occur(red)?',
                r'harm.*result(ed)?',
                r'injury.*sustain(ed)?',
                r'loss.*incur(red)?'
            ]
        }
        
        # Common date context keywords for proximity matching
        self.date_keywords = [
            'date', 'dated', 'on', 'as of', 'effective', 'received', 'sent',
            'signed', 'executed', 'issued', 'published', 'processed'
        ]
    
    def extract_dates_from_text(self, text: str, document_type: str = None) -> List[ExtractedDate]:
        """Extract all dates from text with context awareness"""
        extracted_dates = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            dates_in_line = self._extract_dates_from_line(line, line_num, document_type)
            extracted_dates.extend(dates_in_line)
        
        # Post-process to improve context detection
        extracted_dates = self._enhance_context_detection(extracted_dates, text)
        
        # Sort by confidence and parsed date
        extracted_dates.sort(key=lambda x: (x.confidence, x.parsed_date or date.min), reverse=True)
        
        return extracted_dates
    
    def _extract_dates_from_line(self, line: str, line_num: int, document_type: str = None) -> List[ExtractedDate]:
        """Extract dates from a single line with context analysis"""
        extracted_dates = []
        line_clean = line.strip()
        
        if not line_clean:
            return extracted_dates
        
        # Try each date pattern
        for pattern, date_format in self.date_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            
            for match in matches:
                date_text = match.group(0)
                parsed_date = self._parse_date_safely(date_text, date_format)
                
                if parsed_date:
                    context = self._determine_date_context(line, match.start())
                    confidence = self._calculate_confidence(line, match, context, document_type)
                    
                    extracted_date = ExtractedDate(
                        raw_text=date_text,
                        parsed_date=parsed_date,
                        context=context,
                        confidence=confidence,
                        source_line=line_clean,
                        line_number=line_num,
                        document_section=self._identify_document_section(line)
                    )
                    
                    extracted_dates.append(extracted_date)
        
        return extracted_dates
    
    def _parse_date_safely(self, date_text: str, date_format: str) -> Optional[date]:
        """Safely parse date text using multiple strategies"""
        try:
            # Handle different format patterns
            if '%B %d %Y' in date_format or '%b %d %Y' in date_format:
                # Handle "Month DD, YYYY" format
                clean_text = re.sub(r'[,.]', '', date_text)
                return datetime.strptime(clean_text, date_format.replace(',', '')).date()
            elif '%d %B %Y' in date_format or '%d %b %Y' in date_format:
                # Handle "DD Month YYYY" format
                clean_text = re.sub(r'[,.]', '', date_text)
                return datetime.strptime(clean_text, date_format.replace(',', '')).date()
            else:
                # Handle numeric formats
                return datetime.strptime(date_text, date_format).date()
                
        except ValueError as e:
            # Try alternative parsing strategies
            try:
                # Remove common separators and try parsing
                clean_text = re.sub(r'[\/\-\.]', '/', date_text)
                
                # Try MM/DD/YYYY
                if len(clean_text.split('/')) == 3:
                    parts = clean_text.split('/')
                    if len(parts[2]) == 2:  # 2-digit year
                        year = int(parts[2])
                        year = 2000 + year if year < 50 else 1900 + year
                        return date(year, int(parts[0]), int(parts[1]))
                    else:
                        return date(int(parts[2]), int(parts[0]), int(parts[1]))
                        
            except (ValueError, IndexError):
                self.logger.debug(f"Failed to parse date: {date_text}")
                
        return None
    
    def _determine_date_context(self, line: str, date_position: int) -> DateContext:
        """Determine the context of a date based on surrounding text"""
        line_lower = line.lower()
        
        # Check for context patterns in order of specificity
        for context, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    return context
        
        # Check for date-related keywords near the date
        window_start = max(0, date_position - 50)
        window_end = min(len(line), date_position + 50)
        window_text = line[window_start:window_end].lower()
        
        # Look for specific document type indicators
        if any(keyword in window_text for keyword in ['denial', 'adverse action']):
            return DateContext.DENIAL_DATE
        elif any(keyword in window_text for keyword in ['dispute', 'challenge']):
            return DateContext.DISPUTE_DATE
        elif any(keyword in window_text for keyword in ['application', 'applied']):
            return DateContext.APPLICATION_DATE
        elif any(keyword in window_text for keyword in ['notice', 'notification']):
            return DateContext.NOTICE_DATE
        
        return DateContext.UNKNOWN
    
    def _calculate_confidence(self, line: str, match: re.Match, context: DateContext, document_type: str = None) -> float:
        """Calculate confidence score for extracted date"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on context
        if context != DateContext.UNKNOWN:
            confidence += 0.3
        
        # Boost confidence for dates with clear indicators
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in self.date_keywords):
            confidence += 0.1
        
        # Boost confidence based on document type
        if document_type:
            if 'denial' in document_type.lower() and context == DateContext.DENIAL_DATE:
                confidence += 0.2
            elif 'adverse' in document_type.lower() and context == DateContext.ADVERSE_ACTION_DATE:
                confidence += 0.2
        
        # Check date reasonableness (should be within reasonable range)
        date_text = match.group(0)
        if self._is_reasonable_date(date_text):
            confidence += 0.1
        else:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _is_reasonable_date(self, date_text: str) -> bool:
        """Check if a date is reasonable for legal documents"""
        try:
            # Extract year from date text
            year_match = re.search(r'\b(19|20)\d{2}\b', date_text)
            if year_match:
                year = int(year_match.group(0))
                current_year = datetime.now().year
                
                # Reasonable range: 1970 to current year + 1
                return 1970 <= year <= current_year + 1
        except:
            pass
        
        return True  # Default to reasonable if can't determine
    
    def _identify_document_section(self, line: str) -> Optional[str]:
        """Identify which section of the document this line might be from"""
        line_lower = line.lower()
        
        # Common document sections
        if any(header in line_lower for header in ['background', 'factual background']):
            return 'background'
        elif any(header in line_lower for header in ['damages', 'harm', 'injury']):
            return 'damages'
        elif any(header in line_lower for header in ['timeline', 'chronology']):
            return 'timeline'
        elif any(header in line_lower for header in ['dispute', 'investigation']):
            return 'dispute_history'
        elif any(header in line_lower for header in ['discovery', 'notice']):
            return 'discovery'
        
        return None
    
    def _enhance_context_detection(self, extracted_dates: List[ExtractedDate], full_text: str) -> List[ExtractedDate]:
        """Enhance context detection using full document analysis"""
        # This could be expanded to use machine learning or more sophisticated NLP
        # For now, we'll do some basic improvements
        
        for extracted_date in extracted_dates:
            if extracted_date.context == DateContext.UNKNOWN:
                # Try to infer context from document structure
                enhanced_context = self._infer_context_from_document(extracted_date, full_text)
                if enhanced_context != DateContext.UNKNOWN:
                    extracted_date.context = enhanced_context
                    extracted_date.confidence += 0.1
        
        return extracted_dates
    
    def _infer_context_from_document(self, extracted_date: ExtractedDate, full_text: str) -> DateContext:
        """Infer context from broader document analysis"""
        # Look for patterns in the broader document context
        text_lower = full_text.lower()
        
        # If this is near dispute-related text in the document
        if 'dispute' in text_lower and extracted_date.source_line:
            line_lower = extracted_date.source_line.lower()
            if any(word in line_lower for word in ['sent', 'submitted', 'filed']):
                return DateContext.DISPUTE_DATE
        
        # If this is near denial-related text
        if 'denial' in text_lower or 'denied' in text_lower:
            line_lower = extracted_date.source_line.lower()
            if any(word in line_lower for word in ['received', 'dated', 'issued']):
                return DateContext.DENIAL_DATE
        
        return DateContext.UNKNOWN
    
    def extract_timeline_dates(self, text: str, document_type: str = None) -> Dict[str, List[ExtractedDate]]:
        """Extract dates organized by timeline relevance"""
        all_dates = self.extract_dates_from_text(text, document_type)
        
        # Organize dates by context
        timeline_dates = {}
        for date_obj in all_dates:
            context_key = date_obj.context.value
            if context_key not in timeline_dates:
                timeline_dates[context_key] = []
            timeline_dates[context_key].append(date_obj)
        
        # Sort dates within each context by date
        for context in timeline_dates:
            timeline_dates[context].sort(
                key=lambda x: x.parsed_date or date.min
            )
        
        return timeline_dates
    
    def get_best_date_for_context(self, dates: List[ExtractedDate], context: DateContext) -> Optional[ExtractedDate]:
        """Get the best (highest confidence) date for a specific context"""
        context_dates = [d for d in dates if d.context == context]
        if not context_dates:
            return None
        
        # Return highest confidence date
        return max(context_dates, key=lambda x: x.confidence)
    
    def validate_date_chronology(self, dates: List[ExtractedDate]) -> Dict[str, Any]:
        """Validate chronological order of extracted dates"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'timeline': []
        }
        
        # Create timeline of dates
        dated_events = []
        for date_obj in dates:
            if date_obj.parsed_date and date_obj.confidence > 0.5:
                dated_events.append({
                    'date': date_obj.parsed_date,
                    'context': date_obj.context.value,
                    'confidence': date_obj.confidence,
                    'source': date_obj.source_line
                })
        
        # Sort by date
        dated_events.sort(key=lambda x: x['date'])
        validation_result['timeline'] = dated_events
        
        # Check for logical chronological issues
        discovery_dates = [e for e in dated_events if e['context'] == 'discovery_date']
        dispute_dates = [e for e in dated_events if e['context'] == 'dispute_date']
        damage_dates = [e for e in dated_events if e['context'] == 'damage_event_date']
        
        # Validation rules
        if discovery_dates and dispute_dates:
            latest_discovery = max(discovery_dates, key=lambda x: x['date'])
            earliest_dispute = min(dispute_dates, key=lambda x: x['date'])
            
            if latest_discovery['date'] > earliest_dispute['date']:
                validation_result['is_valid'] = False
                validation_result['errors'].append(
                    f"Discovery date ({latest_discovery['date']}) is after dispute date ({earliest_dispute['date']})"
                )
        
        # Check for future dates
        current_date = date.today()
        future_dates = [e for e in dated_events if e['date'] > current_date]
        if future_dates:
            validation_result['warnings'].extend([
                f"Future date found: {e['date']} ({e['context']})" 
                for e in future_dates
            ])
        
        return validation_result