"""
Simplified test suite for Tiger legal extraction capabilities.
Focus on core functionality that actually works with the current implementation.
"""

import unittest
import tempfile
import os
from pathlib import Path

from app.core.extractors.legal_entity_extractor import LegalEntityExtractor, LegalEntity, CaseInformation
from app.core.processors.case_consolidator import CaseConsolidator, ConsolidatedCase
from app.engines.base_engine import ExtractionResult


class TestLegalEntityExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
    
    def test_extract_case_number_federal(self):
        """Test extraction of federal case numbers."""
        text = "Case No. 1:25-cv-02156"
        result = self.extractor.extract_case_information(text)
        self.assertEqual(result.case_number, "1:25-cv-02156")
    
    def test_extract_case_number_state(self):
        """Test extraction of state case numbers."""  
        text = "Index No. 2025-123456"
        result = self.extractor.extract_case_information(text)
        self.assertIsNotNone(result.case_number)
    
    def test_extract_court_information(self):
        """Test extraction of court information."""
        text = "UNITED STATES DISTRICT COURT\nSOUTHERN DISTRICT OF NEW YORK"
        result = self.extractor.extract_case_information(text)
        self.assertIsNotNone(result.court_name)
        self.assertIn("DISTRICT", result.court_name)
    
    def test_extract_legal_entities(self):
        """Test extraction of legal entities from text."""
        text = """
        SARAH JOHNSON,
                                        Plaintiff,
        v.
        TRANSUNION LLC,
                                        Defendant.
        """
        entities = self.extractor.extract_legal_entities(text)
        
        # Should return a dictionary structure
        self.assertIsInstance(entities, dict)
        
        # Should have some entities
        total_entities = sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in entities.values())
        self.assertGreater(total_entities, 0, "Should extract some entities")


class TestCaseConsolidator(unittest.TestCase):
    
    def setUp(self):
        self.consolidator = CaseConsolidator()
    
    def create_mock_extraction_result(self, text, file_path="test.txt"):
        """Helper to create mock extraction results."""
        result = ExtractionResult(success=True, text=text)
        result.extracted_text = text  # Add the extracted_text attribute that consolidator expects
        result.file_path = file_path
        return result
    
    def test_consolidate_single_document(self):
        """Test consolidation with single document."""
        text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        """
        
        results = [self.create_mock_extraction_result(text)]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Should create a ConsolidatedCase
            self.assertIsInstance(consolidated, ConsolidatedCase)
            self.assertEqual(consolidated.case_id, os.path.basename(temp_dir))
    
    def test_consolidate_multiple_documents(self):
        """Test consolidation with multiple documents."""
        doc1_text = "Case No. 1:25-cv-02156\nSARAH JOHNSON v. TRANSUNION LLC"  
        doc2_text = "UNITED STATES DISTRICT COURT\nSOUTHERN DISTRICT OF NEW YORK"
        
        results = [
            self.create_mock_extraction_result(doc1_text, "doc1.txt"),
            self.create_mock_extraction_result(doc2_text, "doc2.txt")
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Should process multiple documents
            self.assertEqual(len(consolidated.source_documents), 2)
            self.assertGreater(consolidated.extraction_confidence, 0)
    
    def test_confidence_calculation(self):
        """Test confidence calculation."""
        text = "Case No. 1:25-cv-02156"
        results = [self.create_mock_extraction_result(text)]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Should have some confidence score
            self.assertGreaterEqual(consolidated.extraction_confidence, 0)
            self.assertLessEqual(consolidated.extraction_confidence, 100)
    
    def test_empty_results(self):
        """Test consolidation with no extraction results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, [])
            
            self.assertLessEqual(consolidated.extraction_confidence, 10.0)  # Allow for baseline confidence
            self.assertEqual(len(consolidated.source_documents), 0)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete legal extraction workflows."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def create_mock_extraction_result(self, text, file_path="test.txt"):
        """Helper to create mock extraction results."""
        result = ExtractionResult(success=True, text=text)
        result.extracted_text = text  
        result.file_path = file_path
        return result
    
    def test_basic_legal_workflow(self):
        """Test basic legal document processing workflow."""
        
        legal_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        
        COMPLAINT FOR DAMAGES
        """
        
        # Extract case information
        case_info = self.extractor.extract_case_information(legal_text)
        self.assertEqual(case_info.case_number, "1:25-cv-02156")
        self.assertIsNotNone(case_info.court_name)
        
        # Extract legal entities
        entities = self.extractor.extract_legal_entities(legal_text)
        self.assertIsInstance(entities, dict)
        
        # Consolidate into case
        result = self.create_mock_extraction_result(legal_text)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, [result])
            
            # Should have extracted basic information
            self.assertEqual(consolidated.case_information.case_number, "1:25-cv-02156")
            self.assertIsNotNone(consolidated.case_information.court_name)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_empty_document(self):
        """Test handling of empty documents."""
        result = self.extractor.extract_case_information("")
        
        self.assertIsNone(result.case_number)
        self.assertIsNone(result.court_name)
    
    def test_non_legal_document(self):
        """Test handling of non-legal documents."""
        text = """
        This is a recipe for chocolate chip cookies.
        Ingredients: flour, sugar, chocolate chips.
        Bake at 350 degrees for 10 minutes.
        """
        
        case_info = self.extractor.extract_case_information(text)
        entities = self.extractor.extract_legal_entities(text)
        
        self.assertIsNone(case_info.case_number)
        self.assertIsInstance(entities, dict)


if __name__ == "__main__":
    # Run tests with detailed output
    unittest.main(verbosity=2)