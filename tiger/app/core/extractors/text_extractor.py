"""
Text Extractor - Utility functions for text processing and analysis
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

class TextExtractor:
    """Advanced text extraction and analysis utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities and structured data from text"""
        entities = {
            'names': self._extract_names(text),
            'addresses': self._extract_addresses(text),
            'phone_numbers': self._extract_phone_numbers(text),
            'emails': self._extract_emails(text),
            'dates': self._extract_dates(text),
            'case_numbers': self._extract_case_numbers(text),
            'legal_entities': self._extract_legal_entities(text),
            'monetary_amounts': self._extract_monetary_amounts(text)
        }
        
        return entities
    
    def _extract_names(self, text: str) -> List[str]:
        """Extract potential person names"""
        # Pattern for capitalized names (simple approach)
        name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        names = re.findall(name_pattern, text)
        
        # Filter out common legal terms that might match the pattern
        legal_terms = {
            'United States', 'District Court', 'Civil Action', 'Federal Rules',
            'Credit Reporting', 'Fair Credit', 'Consumer Protection', 'Legal Services'
        }
        
        filtered_names = [name for name in names if name not in legal_terms]
        return list(set(filtered_names))  # Remove duplicates
    
    def _extract_addresses(self, text: str) -> List[str]:
        """Extract addresses from text"""
        address_patterns = [
            r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Circle|Court|Ct)(?:\s+(?:Apt|Suite|Unit)\s*\w+)?\b',
            r'P\.O\.\s+Box\s+\d+',
            r'\d+\s+\w+\s+\w+\s+(?:Street|Avenue|Road|Drive|Lane|Boulevard)',
        ]
        
        addresses = []
        for pattern in address_patterns:
            addresses.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(addresses))
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\b\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b',
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\b\d{10}\b'
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    phones.append(''.join(match))
                else:
                    phones.append(match)
        
        # Format phone numbers consistently
        formatted_phones = []
        for phone in phones:
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10:
                formatted_phones.append(f"({digits[:3]}) {digits[3:6]}-{digits[6:]}")
        
        return list(set(formatted_phones))
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        date_patterns = [
            r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
            r'\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(dates))
    
    def _extract_case_numbers(self, text: str) -> List[str]:
        """Extract legal case numbers"""
        case_patterns = [
            r'\b\d{1,2}[-\.:]\d{2,4}[-\.:]\w{2,6}[-\.:]\d{4,6}\b',
            r'\bNo\.\s*\d+[-\.:]\d+[-\.:]\w+[-\.:]\d+',
            r'\bCase\s+No\.\s*\d+[-\.:]\d+[-\.:]\w+[-\.:]\d+',
            r'\bCivil\s+Action\s+No\.\s*\d+[-\.:]\d+[-\.:]\w+[-\.:]\d+'
        ]
        
        case_numbers = []
        for pattern in case_patterns:
            case_numbers.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(case_numbers))
    
    def _extract_legal_entities(self, text: str) -> List[str]:
        """Extract legal entity names"""
        entity_patterns = [
            r'\b\w+(?:\s+\w+)*\s+LLC\b',
            r'\b\w+(?:\s+\w+)*\s+Inc\.?\b',
            r'\b\w+(?:\s+\w+)*\s+Corp\.?\b',
            r'\b\w+(?:\s+\w+)*\s+Corporation\b',
            r'\b\w+(?:\s+\w+)*\s+Company\b',
            r'\b\w+(?:\s+\w+)*\s+L\.P\.\b',
            r'\b\w+(?:\s+\w+)*\s+Bank\b',
            r'\b\w+(?:\s+\w+)*\s+Credit\s+Union\b'
        ]
        
        entities = []
        for pattern in entity_patterns:
            entities.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(entities))
    
    def _extract_monetary_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from text"""
        money_patterns = [
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            r'\b\d{1,3}(?:,\d{3})*\.\d{2}\s*dollars?\b',
            r'\$\d+(?:\.\d{2})?'
        ]
        
        amounts = []
        for pattern in money_patterns:
            amounts.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(amounts))
    
    def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity and readability"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Basic metrics
        word_count = len(words)
        sentence_count = len(sentences)
        char_count = len(text)
        
        # Averages
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        avg_chars_per_word = char_count / max(word_count, 1)
        
        # Complexity indicators
        long_words = len([w for w in words if len(w) > 6])
        long_word_ratio = long_words / max(word_count, 1)
        
        # Legal document complexity indicators
        legal_jargon_count = self._count_legal_jargon(text)
        technical_terms_count = self._count_technical_terms(text)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'character_count': char_count,
            'avg_words_per_sentence': avg_words_per_sentence,
            'avg_chars_per_word': avg_chars_per_word,
            'long_word_ratio': long_word_ratio,
            'legal_jargon_count': legal_jargon_count,
            'technical_terms_count': technical_terms_count,
            'complexity_score': self._calculate_complexity_score(
                avg_words_per_sentence, long_word_ratio, legal_jargon_count
            )
        }
    
    def _count_legal_jargon(self, text: str) -> int:
        """Count legal jargon terms"""
        legal_terms = [
            'whereas', 'heretofore', 'hereinafter', 'aforementioned', 'pursuant',
            'notwithstanding', 'jurisdiction', 'litigation', 'plaintiff', 'defendant',
            'respondent', 'petitioner', 'allegation', 'complaint', 'summons',
            'subpoena', 'deposition', 'affidavit', 'stipulation', 'injunction'
        ]
        
        count = 0
        text_lower = text.lower()
        for term in legal_terms:
            count += text_lower.count(term)
        
        return count
    
    def _count_technical_terms(self, text: str) -> int:
        """Count technical/financial terms"""
        technical_terms = [
            'credit report', 'fico', 'equifax', 'experian', 'transunion',
            'adverse action', 'fcra', 'fdcpa', 'dispute', 'investigation',
            'verification', 'liability', 'damages', 'settlement', 'arbitration'
        ]
        
        count = 0
        text_lower = text.lower()
        for term in technical_terms:
            count += text_lower.count(term)
        
        return count
    
    def _calculate_complexity_score(self, avg_words_per_sentence: float, 
                                   long_word_ratio: float, legal_jargon_count: int) -> float:
        """Calculate text complexity score (0-100)"""
        # Base score from sentence length (longer sentences = more complex)
        sentence_score = min(avg_words_per_sentence * 2, 40)
        
        # Score from word complexity
        word_score = min(long_word_ratio * 100, 30)
        
        # Score from legal jargon density
        jargon_score = min(legal_jargon_count * 2, 30)
        
        return min(sentence_score + word_score + jargon_score, 100)
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[Tuple[str, int]]:
        """Extract key phrases from text"""
        # Simple approach: find most common multi-word phrases
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Generate bigrams and trigrams
        phrases = []
        for i in range(len(words) - 1):
            phrases.append(' '.join(words[i:i+2]))  # bigrams
        for i in range(len(words) - 2):
            phrases.append(' '.join(words[i:i+3]))  # trigrams
        
        # Filter out common phrases and count
        common_phrases = {'of the', 'in the', 'to the', 'for the', 'on the', 'at the'}
        filtered_phrases = [p for p in phrases if p not in common_phrases and len(p) > 5]
        
        # Return most common phrases
        phrase_counts = Counter(filtered_phrases)
        return phrase_counts.most_common(max_phrases)