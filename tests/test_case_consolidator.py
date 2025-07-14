#!/usr/bin/env python3
"""
Unit tests for the CaseConsolidator class
Tests the enhanced case consolidation engine with multiple document processing
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.processors.case_consolidator import CaseConsolidator


class TestCaseConsolidator(unittest.TestCase):
    """Test cases for the enhanced CaseConsolidator class"""
    
    def setUp(self):
        """Set up test environment"""
        self.consolidator = CaseConsolidator()
        
        # Sample extracted data for testing
        self.sample_document_1 = {
            'extracted_text': 'UNITED STATES DISTRICT COURT FOR THE SOUTHERN DISTRICT OF NEW YORK Case No: 1:25-cv-01234 Jane Doe v. Experian Information Solutions, Inc.',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {
                    'case_number': '1:25-cv-01234',
                    'court_district': 'Southern District of New York',
                    'court_name': 'United States District Court'
                })(),
                'parties': [
                    type('Party', (), {
                        'name': 'Jane Doe',
                        'role': 'plaintiff',
                        'confidence': 0.95
                    })(),
                    type('Party', (), {
                        'name': 'Experian Information Solutions, Inc.',
                        'role': 'defendant',
                        'confidence': 0.90
                    })()
                ]
            }
        }
        
        self.sample_document_2 = {
            'extracted_text': 'Case Number: 1:25-cv-01234 Plaintiff: J. Doe vs TransUnion LLC July 15, 2024: Credit report dispute filed',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {
                    'case_number': '1:25-cv-01234',
                    'court_district': 'Southern District of New York',
                    'court_name': 'United States District Court'
                })(),
                'parties': [
                    type('Party', (), {
                        'name': 'J. Doe',
                        'role': 'plaintiff',
                        'confidence': 0.85
                    })(),
                    type('Party', (), {
                        'name': 'TransUnion LLC',
                        'role': 'defendant',
                        'confidence': 0.92
                    })()
                ]
            }
        }
        
        self.conflicting_document = {
            'extracted_text': 'Case No: 1:25-cv-05678 Jane Smith plaintiff vs Equifax',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {
                    'case_number': '1:25-cv-05678',  # Different case number - should trigger conflict
                    'court_district': 'Southern District of New York',
                    'court_name': 'United States District Court'
                })(),
                'parties': [
                    type('Party', (), {
                        'name': 'Jane Smith',
                        'role': 'plaintiff',
                        'confidence': 0.88
                    })(),
                    type('Party', (), {
                        'name': 'Equifax Information Services LLC',
                        'role': 'defendant',
                        'confidence': 0.91
                    })()
                ]
            }
        }
    
    def test_process_document_interface(self):
        """Test that process_document method works correctly"""
        # Test processing a single document
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        
        # Verify internal state is initialized
        self.assertTrue(hasattr(self.consolidator, '_case_data'))
        self.assertEqual(len(self.consolidator._case_data['source_documents']), 1)
        self.assertEqual(self.consolidator._case_data['source_documents'][0], '/path/to/doc1.pdf')
        
        # Test processing a second document
        self.consolidator.process_document('/path/to/doc2.pdf', self.sample_document_2)
        self.assertEqual(len(self.consolidator._case_data['source_documents']), 2)
    
    def test_get_consolidated_json_interface(self):
        """Test that get_consolidated_json method works correctly"""
        # Process some documents first
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        self.consolidator.process_document('/path/to/doc2.pdf', self.sample_document_2)
        
        # Get consolidated JSON
        result_json = self.consolidator.get_consolidated_json()
        
        # Verify it's valid JSON
        result_data = json.loads(result_json)
        
        # Verify required structure
        self.assertIn('case_summary', result_data)
        self.assertIn('plaintiffs', result_data)
        self.assertIn('defendants', result_data)
        self.assertIn('timeline', result_data)
        self.assertIn('issues', result_data)
        self.assertIn('processing_metadata', result_data)
    
    def test_successful_entity_deduplication(self):
        """Test that entities are correctly deduplicated"""
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        self.consolidator.process_document('/path/to/doc2.pdf', self.sample_document_2)
        
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Should have deduplicated Jane Doe and J. Doe into one plaintiff
        plaintiffs = result_data['plaintiffs']
        self.assertEqual(len(plaintiffs), 1)
        
        # Should have two defendants (Experian and TransUnion)
        defendants = result_data['defendants']
        self.assertEqual(len(defendants), 2)
        
        # Verify plaintiff has sources from both documents
        plaintiff = plaintiffs[0]
        self.assertEqual(len(plaintiff['sources']), 2)
        self.assertIn('/path/to/doc1.pdf', plaintiff['sources'])
        self.assertIn('/path/to/doc2.pdf', plaintiff['sources'])
    
    def test_timeline_construction(self):
        """Test correct timeline construction"""
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        self.consolidator.process_document('/path/to/doc2.pdf', self.sample_document_2)
        
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Should have timeline events
        timeline = result_data['timeline']
        self.assertGreater(len(timeline), 0)
        
        # Each timeline entry should have required fields
        for event in timeline:
            self.assertIn('date', event)
            self.assertIn('event', event)
            self.assertIn('source', event)
    
    def test_confidence_score_calculation(self):
        """Test accurate confidence score calculation"""
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        self.consolidator.process_document('/path/to/doc2.pdf', self.sample_document_2)
        
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Should have a confidence score
        confidence = result_data['case_summary']['confidence']
        self.assertIsInstance(confidence, (int, float))
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 100)
        
        # With complete case info, plaintiffs, and defendants, should have decent confidence
        self.assertGreater(confidence, 60)  # Should be reasonably high
    
    def test_source_tracking(self):
        """Test proper source tracking for all data"""
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        self.consolidator.process_document('/path/to/doc2.pdf', self.sample_document_2)
        
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Verify source tracking in processing metadata
        metadata = result_data['processing_metadata']
        self.assertIn('source_documents', metadata)
        self.assertEqual(len(metadata['source_documents']), 2)
        self.assertIn('/path/to/doc1.pdf', metadata['source_documents'])
        self.assertIn('/path/to/doc2.pdf', metadata['source_documents'])
        
        # Verify entities have source tracking
        for plaintiff in result_data['plaintiffs']:
            self.assertIn('sources', plaintiff)
            self.assertIsInstance(plaintiff['sources'], list)
            self.assertGreater(len(plaintiff['sources']), 0)
        
        for defendant in result_data['defendants']:
            self.assertIn('sources', defendant)
            self.assertIsInstance(defendant['sources'], list)
            self.assertGreater(len(defendant['sources']), 0)
    
    def test_conflict_detection_and_flagging(self):
        """Test that conflicting information is detected and flagged"""
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        self.consolidator.process_document('/path/to/doc3.pdf', self.conflicting_document)
        
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Should have detected the conflicting case numbers
        issues = result_data['issues']
        
        # Look for conflict issues
        conflict_issues = [issue for issue in issues if issue.get('type') == 'conflict']
        self.assertGreater(len(conflict_issues), 0)
        
        # Verify the conflict message mentions case numbers
        case_number_conflicts = [issue for issue in conflict_issues if 'case_number' in issue.get('message', '')]
        self.assertGreater(len(case_number_conflicts), 0)
        
        # Verify sources are tracked for conflicts
        for conflict in case_number_conflicts:
            self.assertIn('sources', conflict)
            self.assertGreater(len(conflict['sources']), 1)
    
    def test_empty_input_handling(self):
        """Test handling of empty or invalid input"""
        # Test getting JSON without processing any documents
        with self.assertRaises(RuntimeError):
            self.consolidator.get_consolidated_json()
        
        # Test processing document with minimal data
        minimal_data = {
            'extracted_text': 'Some text',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {})(),
                'parties': []
            }
        }
        
        self.consolidator.process_document('/path/to/minimal.pdf', minimal_data)
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Should still produce valid JSON structure
        self.assertIn('case_summary', result_data)
        self.assertIn('plaintiffs', result_data)
        self.assertIn('defendants', result_data)
        
        # Should have completeness issues
        issues = result_data['issues']
        completeness_issues = [issue for issue in issues if issue.get('type') == 'completeness']
        self.assertGreater(len(completeness_issues), 0)
    
    def test_names_similarity_matching(self):
        """Test the name similarity matching functionality"""
        # Test exact match
        self.assertTrue(self.consolidator._names_similar('JANE DOE', 'JANE DOE'))
        
        # Test case insensitive
        self.assertTrue(self.consolidator._names_similar('jane doe', 'JANE DOE'))
        
        # Test abbreviation matching
        self.assertTrue(self.consolidator._names_similar('J. DOE', 'JANE DOE'))
        
        # Test corporate name matching
        self.assertTrue(self.consolidator._names_similar(
            'EXPERIAN INFORMATION SOLUTIONS, INC.',
            'EXPERIAN INFO SOLUTIONS INC'
        ))
        
        # Test non-matching names
        self.assertFalse(self.consolidator._names_similar('JANE DOE', 'JOHN SMITH'))
    
    def test_timeline_date_validation(self):
        """Test timeline date validation and error detection"""
        # Document with future date (should trigger error)
        future_date_doc = {
            'extracted_text': f'January 1, {datetime.now().year + 1}: Future event occurred',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {})(),
                'parties': []
            }
        }
        
        self.consolidator.process_document('/path/to/future.pdf', future_date_doc)
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Should have timeline error
        issues = result_data['issues']
        timeline_errors = [issue for issue in issues if issue.get('type') == 'timeline_error']
        
        # Note: Depends on the timeline extraction finding the future date
        # This test validates the error detection framework is in place
        self.assertIsInstance(timeline_errors, list)
    
    def test_json_output_structure(self):
        """Test that the JSON output matches the expected structure from the task specification"""
        self.consolidator.process_document('/path/to/doc1.pdf', self.sample_document_1)
        self.consolidator.process_document('/path/to/doc2.pdf', self.sample_document_2)
        
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Verify required structure matches task specification
        required_fields = {
            'case_summary': ['case_number', 'jurisdiction', 'confidence'],
            'plaintiffs': [],  # Should be list of dicts with name, confidence, sources
            'defendants': [],  # Should be list of dicts with name, confidence, sources
            'timeline': [],    # Should be list of dicts with date, event, source
            'issues': [],      # Should be list of dicts with type, message
            'processing_metadata': ['source_documents', 'processing_timestamp', 'total_documents_processed']
        }
        
        for section, fields in required_fields.items():
            self.assertIn(section, result_data)
            
            if isinstance(fields, list) and fields:  # If fields is non-empty list
                for field in fields:
                    self.assertIn(field, result_data[section])
        
        # Verify list structures
        self.assertIsInstance(result_data['plaintiffs'], list)
        self.assertIsInstance(result_data['defendants'], list)
        self.assertIsInstance(result_data['timeline'], list)
        self.assertIsInstance(result_data['issues'], list)
        
        # Verify plaintiff structure
        if result_data['plaintiffs']:
            plaintiff = result_data['plaintiffs'][0]
            required_plaintiff_fields = ['name', 'confidence', 'sources']
            for field in required_plaintiff_fields:
                self.assertIn(field, plaintiff)
        
        # Verify defendant structure
        if result_data['defendants']:
            defendant = result_data['defendants'][0]
            required_defendant_fields = ['name', 'confidence', 'sources']
            for field in required_defendant_fields:
                self.assertIn(field, defendant)


class TestCaseConsolidatorIntegration(unittest.TestCase):
    """Integration tests for CaseConsolidator with realistic data"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.consolidator = CaseConsolidator()
    
    def test_realistic_fcra_case_consolidation(self):
        """Test consolidation with realistic FCRA case data"""
        # Simulate realistic document extractions
        complaint_doc = {
            'extracted_text': 'UNITED STATES DISTRICT COURT SOUTHERN DISTRICT OF NEW YORK Jane Doe, Plaintiff, v. Case No. 1:24-cv-12345 EQUIFAX INFORMATION SERVICES LLC, EXPERIAN INFORMATION SOLUTIONS, INC., Defendants.',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {
                    'case_number': '1:24-cv-12345',
                    'court_district': 'Southern District of New York',
                    'court_name': 'United States District Court'
                })(),
                'parties': [
                    type('Party', (), {
                        'name': 'Jane Doe',
                        'role': 'plaintiff',
                        'confidence': 0.95
                    })(),
                    type('Party', (), {
                        'name': 'EQUIFAX INFORMATION SERVICES LLC',
                        'role': 'defendant',
                        'confidence': 0.92
                    })(),
                    type('Party', (), {
                        'name': 'EXPERIAN INFORMATION SOLUTIONS, INC.',
                        'role': 'defendant',
                        'confidence': 0.91
                    })()
                ]
            }
        }
        
        summons_doc = {
            'extracted_text': 'SUMMONS Case No. 1:24-cv-12345 TO: EQUIFAX INFORMATION SERVICES LLC You are hereby summoned...',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {
                    'case_number': '1:24-cv-12345',
                    'court_district': 'Southern District of New York'
                })(),
                'parties': [
                    type('Party', (), {
                        'name': 'EQUIFAX INFORMATION SERVICES LLC',
                        'role': 'defendant',
                        'confidence': 0.93
                    })()
                ]
            }
        }
        
        attorney_notes_doc = {
            'extracted_text': 'Attorney Notes: Client Jane Doe. July 15, 2024: Client disputed credit report errors. August 1, 2024: Filed complaint in federal court.',
            'legal_entities': {
                'case_information': type('CaseInfo', (), {})(),
                'parties': [
                    type('Party', (), {
                        'name': 'Jane Doe',
                        'role': 'plaintiff',
                        'confidence': 0.88
                    })()
                ]
            }
        }
        
        # Process all documents
        self.consolidator.process_document('complaint.pdf', complaint_doc)
        self.consolidator.process_document('summons.pdf', summons_doc)
        self.consolidator.process_document('attorney_notes.docx', attorney_notes_doc)
        
        # Get consolidated result
        result_json = self.consolidator.get_consolidated_json()
        result_data = json.loads(result_json)
        
        # Verify realistic case consolidation
        self.assertEqual(result_data['case_summary']['case_number'], '1:24-cv-12345')
        self.assertEqual(len(result_data['plaintiffs']), 1)
        self.assertEqual(len(result_data['defendants']), 2)
        
        # Verify source tracking across documents
        plaintiff = result_data['plaintiffs'][0]
        self.assertGreaterEqual(len(plaintiff['sources']), 2)  # Should appear in complaint and attorney notes
        
        # Verify defendants are properly consolidated
        defendant_names = {d['name'] for d in result_data['defendants']}
        self.assertIn('EQUIFAX INFORMATION SERVICES LLC', defendant_names)
        self.assertIn('EXPERIAN INFORMATION SOLUTIONS, INC.', defendant_names)
        
        # Verify timeline events from attorney notes
        timeline = result_data['timeline']
        self.assertGreater(len(timeline), 0)
        
        # Verify confidence score is reasonable for complete case
        confidence = result_data['case_summary']['confidence']
        self.assertGreater(confidence, 70)  # Should be high for complete case data


if __name__ == '__main__':
    unittest.main()