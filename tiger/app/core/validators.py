"""
Quality Validator - Advanced quality assessment for legal document extraction
"""

import os
import re
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class QualityValidator:
    """Advanced quality validation for legal document extraction"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Legal pattern definitions
        self.legal_patterns = {
            'court_references': [
                r'\bUNITED STATES DISTRICT COURT\b',
                r'\bCOURT\b',
                r'\bCIVIL ACTION\b',
                r'\bCASE NO\b',
                r'\bCASE NUMBER\b'
            ],
            'case_numbers': [
                r'\d{1,2}[-:\.]\d{2,4}[-:\.]\w{2,6}[-:\.]\d{4,6}',
                r'\d{4}-\w{2,6}-\d{4,6}',
                r'No\.\s*\d+[-:\.]\d+[-:\.]\w+[-:\.]\d+'
            ],
            'legal_entities': [
                r'\b\w+\s+LLC\b',
                r'\b\w+\s+INC\b',
                r'\b\w+\s+CORP\b',
                r'\b\w+\s+CORPORATION\b',
                r'\b\w+\s+COMPANY\b',
                r'\b\w+\s+L\.P\.\b'
            ],
            'addresses': [
                r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Circle|Court|Ct)\b',
                r'P\.O\.\s+Box\s+\d+',
                r'\d+\s+\w+\s+\w+\s+(?:Street|Avenue|Road|Drive)',
            ],
            'phone_numbers': [
                r'\b\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b',
                r'\b\d{3}-\d{3}-\d{4}\b',
                r'\(\d{3}\)\s*\d{3}-\d{4}'
            ],
            'emails': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'dates': [
                r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
                r'\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
            ]
        }
        
        # Checklist for Readiness Score based on extraction_mapping.md
        self.readiness_checklist = {
            'case_information': {
                'points': 30,
                'fields': {
                    'court_type': {'patterns': [r'UNITED STATES DISTRICT COURT'], 'found': False},
                    'court_district': {'patterns': [r'EASTERN DISTRICT OF NEW YORK'], 'found': False},
                    'case_number': {'patterns': [r'1:25-cv-01987'], 'found': False},
                    'jury_demand': {'patterns': [r'THE PLAINTIFF DEMANDS A JURY TRIAL'], 'found': False}
                }
            },
            'plaintiff': {
                'points': 25,
                'fields': {
                    'name': {'patterns': [r'EMAN YOUSSEF'], 'found': False},
                    'address': {'patterns': [r'238 Merritt Drive'], 'found': False},
                    'residency': {'patterns': [r'State of New York, and borough of Manhattan'], 'found': False}
                }
            },
            'defendants': {
                'points': 25,
                'fields': {
                    'name': {'patterns': [r'TD BANK, N.A.', r'EQUIFAX INFORMATION SERVICES, LLC', r'EXPERIAN INFORMATION SOLUTIONS, INC.', r'TRANS UNION, LLC'], 'found': False},
                    'address': {'patterns': [r'1550 Peachtree Street'], 'found': False}
                }
            },
            'legal_violations': {
                'points': 20,
                'fields': {
                    'fcra_1681eb': {'patterns': [r'15 U\.S\.C\.\s+§\s+1681s-2\(b\)'], 'found': False},
                    'fcra_1681ia': {'patterns': [r'15 U\.S\.C\.\s+§\s+1681i'], 'found': False}
                }
            }
        }
    
    def validate_extraction(self, file_path: str, extracted_text: str) -> Dict[str, Any]:
        """Perform comprehensive quality validation"""
        file_size = os.path.getsize(file_path)
        text_length = len(extracted_text.strip())
        compression_ratio = text_length / file_size if file_size > 0 else 0
        
        # Legal document indicators
        legal_indicators = self._analyze_legal_indicators(extracted_text)
        
        # Quality scoring
        quality_score = self._calculate_quality_score(
            text_length, compression_ratio, legal_indicators
        )
        
        # Quality validation
        passes_threshold = self._passes_quality_threshold(text_length, compression_ratio)
        
        # Generate warnings
        warnings = self._generate_warnings(text_length, compression_ratio, legal_indicators)
        
        # Content analysis
        content_analysis = self._analyze_content_structure(extracted_text)
        
        # Readiness score
        readiness_score = self._calculate_readiness_score(extracted_text)
        
        return {
            'file_size_bytes': file_size,
            'text_length': text_length,
            'compression_ratio': compression_ratio,
            'quality_score': quality_score,
            'readiness_score': readiness_score,
            'passes_threshold': passes_threshold,
            'legal_indicators': legal_indicators,
            'content_analysis': content_analysis,
            'warnings': warnings,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_readiness_score(self, text: str) -> float:
        """Calculate a score based on the presence of key legal data."""
        score = 0
        for category, data in self.readiness_checklist.items():
            category_score = 0
            for field, field_data in data['fields'].items():
                field_data['found'] = False # Reset found status
                for pattern in field_data['patterns']:
                    if re.search(pattern, text, re.IGNORECASE):
                        field_data['found'] = True
                        break
            
            if all(field['found'] for field in data['fields'].values()):
                category_score = data['points']
            else:
                # Award partial points
                found_fields = sum(1 for field in data['fields'].values() if field['found'])
                total_fields = len(data['fields'])
                category_score = (found_fields / total_fields) * data['points']

            score += category_score
            
        return min(score, 100)
    
    def _analyze_legal_indicators(self, text: str) -> Dict[str, Any]:
        """Analyze legal document indicators using pattern matching"""
        text_upper = text.upper()
        indicators = {}
        
        for category, patterns in self.legal_patterns.items():
            matches = []
            total_matches = 0
            
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
                total_matches += len(found)
            
            indicators[category] = {
                'count': total_matches,
                'matches': matches[:5] if matches else [],  # Limit to first 5 matches
                'found': total_matches > 0
            }
        
        # Specific boolean indicators for backward compatibility
        indicators['court_document'] = indicators['court_references']['found']
        indicators['summons'] = 'SUMMONS' in text_upper
        indicators['complaint'] = 'COMPLAINT' in text_upper
        indicators['case_number'] = indicators['case_numbers']['found']
        
        return indicators
    
    def _analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document content structure"""
        lines = text.split('\n')
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Character analysis
        uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        digit_ratio = sum(1 for c in text if c.isdigit()) / max(len(text), 1)
        
        # Structure analysis
        structure_analysis = {
            'line_count': len(lines),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'average_line_length': sum(len(line) for line in lines) / max(len(lines), 1),
            'average_word_length': sum(len(word) for word in words) / max(len(words), 1),
            'uppercase_ratio': uppercase_ratio,
            'digit_ratio': digit_ratio,
            'empty_lines': len([line for line in lines if not line.strip()]),
            'paragraph_breaks': text.count('\n\n')
        }
        
        # Document type hints
        structure_analysis['structure_hints'] = self._get_structure_hints(text, structure_analysis)
        
        return structure_analysis
    
    def _get_structure_hints(self, text: str, structure: Dict[str, Any]) -> List[str]:
        """Get hints about document structure and type"""
        hints = []
        
        # Formatting hints
        if structure['uppercase_ratio'] > 0.3:
            hints.append("High uppercase content (typical of legal headers)")
        
        if structure['paragraph_breaks'] > 5:
            hints.append("Well-structured document with clear paragraphs")
        
        if structure['line_count'] > 100:
            hints.append("Long document (detailed legal content)")
        
        # Content type hints
        if 'WHEREAS' in text.upper():
            hints.append("Contract or legal agreement language detected")
        
        if any(phrase in text.upper() for phrase in ['PLAINTIFF', 'DEFENDANT', 'RESPONDENT']):
            hints.append("Litigation document indicators found")
        
        if any(phrase in text.upper() for phrase in ['CREDIT REPORT', 'ADVERSE ACTION', 'DENIAL']):
            hints.append("Credit-related document detected")
        
        if 'ATTORNEY' in text.upper() or 'LAW' in text.upper():
            hints.append("Legal professional involvement indicated")
        
        return hints
    
    def _calculate_quality_score(self, text_length: int, compression_ratio: float, 
                                legal_indicators: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)"""
        score = 0
        
        # Text length scoring (0-30 points)
        if text_length >= 3000:
            score += 30
        elif text_length >= 2000:
            score += 25
        elif text_length >= 1000:
            score += 20
        elif text_length >= 500:
            score += 15
        elif text_length >= 200:
            score += 10
        elif text_length >= 100:
            score += 5
        
        # Compression ratio scoring (0-20 points)
        optimal_min = self.config.quality.compression_ratio_min
        optimal_max = self.config.quality.compression_ratio_max
        
        if optimal_min <= compression_ratio <= optimal_max:
            score += 20
        elif compression_ratio < optimal_min:
            # Too low - extraction might have failed
            score += max(0, 10 - (optimal_min - compression_ratio) * 500)
        else:
            # Too high - might indicate formatting issues
            score += max(0, 15 - (compression_ratio - optimal_max) * 100)
        
        # Legal indicators scoring (0-50 points)
        if legal_indicators.get('court_document', False):
            score += 15
        
        if legal_indicators.get('summons', False) or legal_indicators.get('complaint', False):
            score += 10
        
        if legal_indicators.get('case_number', False):
            score += 10
        
        # Count-based indicators
        entity_count = legal_indicators.get('legal_entities', {}).get('count', 0)
        address_count = legal_indicators.get('addresses', {}).get('count', 0)
        phone_count = legal_indicators.get('phone_numbers', {}).get('count', 0)
        email_count = legal_indicators.get('emails', {}).get('count', 0)
        date_count = legal_indicators.get('dates', {}).get('count', 0)
        
        score += min(entity_count * 2, 6)  # Up to 6 points for entities
        score += min(address_count * 2, 4)  # Up to 4 points for addresses
        score += min(phone_count * 1, 3)    # Up to 3 points for phones
        score += min(email_count * 1, 2)    # Up to 2 points for emails
        score += min(date_count * 1, 3)     # Up to 3 points for dates
        
        return min(score, 100)
    
    def _passes_quality_threshold(self, text_length: int, compression_ratio: float) -> bool:
        """Check if extraction meets minimum quality thresholds"""
        return (
            text_length >= self.config.quality.min_text_length and
            self.config.quality.compression_ratio_min <= compression_ratio <= 
            self.config.quality.compression_ratio_max
        )
    
    def _generate_warnings(self, text_length: int, compression_ratio: float, 
                          legal_indicators: Dict[str, Any]) -> List[str]:
        """Generate quality warnings"""
        warnings = []
        
        # Text length warnings
        if text_length < 50:
            warnings.append("CRITICAL: Very short text extracted - likely extraction failure")
        elif text_length < 200:
            warnings.append("WARNING: Short text extracted - verify completeness")
        elif text_length < 500:
            warnings.append("INFO: Moderate text length - ensure all content captured")
        
        # Compression ratio warnings
        if compression_ratio < 0.001:
            warnings.append("CRITICAL: Extremely low compression ratio - extraction likely failed")
        elif compression_ratio < 0.002:
            warnings.append("WARNING: Low compression ratio - minimal text extracted")
        elif compression_ratio > 0.1:
            warnings.append("WARNING: High compression ratio - possible OCR errors or repetitive text")
        elif compression_ratio > 0.05:
            warnings.append("INFO: Above-optimal compression ratio - review for accuracy")
        
        # Legal content warnings
        if not legal_indicators.get('court_document', False):
            warnings.append("INFO: No court document indicators found")
        
        if not legal_indicators.get('case_number', False):
            warnings.append("INFO: No case number detected")
        
        if legal_indicators.get('addresses', {}).get('count', 0) == 0:
            warnings.append("INFO: No addresses found - verify if expected")
        
        if (legal_indicators.get('phone_numbers', {}).get('count', 0) == 0 and 
            legal_indicators.get('emails', {}).get('count', 0) == 0):
            warnings.append("INFO: No contact information found")
        
        return warnings
    
    def generate_quality_report(self, validation_results: List[Dict[str, Any]]) -> str:
        """Generate a formatted quality report"""
        if not validation_results:
            return "No validation results to report."
        
        report_lines = [
            "# SATORI TIGER QUALITY VALIDATION REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Documents Analyzed: {len(validation_results)}",
            "",
        ]
        
        # Summary statistics
        total_score = sum(r.get('quality_score', 0) for r in validation_results)
        avg_score = total_score / len(validation_results)
        high_quality = len([r for r in validation_results if r.get('quality_score', 0) >= 80])
        passed_threshold = len([r for r in validation_results if r.get('passes_threshold', False)])
        
        report_lines.extend([
            "## SUMMARY STATISTICS",
            f"Average Quality Score: {avg_score:.1f}/100",
            f"High Quality Documents (≥80): {high_quality}/{len(validation_results)}",
            f"Passed Quality Threshold: {passed_threshold}/{len(validation_results)}",
            f"Success Rate: {(passed_threshold/len(validation_results)*100):.1f}%",
            "",
        ])
        
        # Warning summary
        all_warnings = []
        for result in validation_results:
            all_warnings.extend(result.get('warnings', []))
        
        if all_warnings:
            warning_counts = {}
            for warning in all_warnings:
                warning_type = warning.split(':')[0] if ':' in warning else 'INFO'
                warning_counts[warning_type] = warning_counts.get(warning_type, 0) + 1
            
            report_lines.extend([
                "## WARNING SUMMARY",
                *[f"{wtype}: {count} occurrences" for wtype, count in warning_counts.items()],
                "",
            ])
        
        return '\n'.join(report_lines)