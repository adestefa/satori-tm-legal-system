"""
Comprehensive test suite for Tiger legal extraction capabilities.
Tests legal entity extraction, case consolidation, and document processing.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

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
        self.assertEqual(result.case_number, "2025-123456")
    
    def test_extract_court_southern_district(self):
        """Test extraction of Southern District of New York."""
        text = "UNITED STATES DISTRICT COURT\nSOUTHERN DISTRICT OF NEW YORK"
        result = self.extractor.extract_case_information(text)
        self.assertEqual(result.court_name, "SOUTHERN DISTRICT OF NEW YORK")
    
    def test_extract_parties_simple(self):
        """Test extraction of basic plaintiff and defendant."""
        text = """
        SARAH JOHNSON,
                                        Plaintiff,
        v.
        TRANSUNION LLC,
                                        Defendant.
        """
        entities = self.extractor.extract_legal_entities(text)
        
        parties = [e for e in entities if isinstance(e, Party)]
        self.assertEqual(len(parties), 2)
        
        plaintiff = next((p for p in parties if p.role == "plaintiff"), None)
        defendant = next((p for p in parties if p.role == "defendant"), None)
        
        self.assertIsNotNone(plaintiff)
        self.assertIsNotNone(defendant)
        self.assertEqual(plaintiff.name, "SARAH JOHNSON")
        self.assertEqual(defendant.name, "TRANSUNION LLC")
    
    def test_extract_parties_multiple_defendants(self):
        """Test extraction with multiple defendants."""
        text = """
        JOHN DOE,
                                        Plaintiff,
        v.
        EQUIFAX INC., EXPERIAN LLC,
        and TRANSUNION LLC,
                                        Defendants.
        """
        entities = self.extractor.extract_legal_entities(text)
        parties = [e for e in entities if isinstance(e, Party)]
        
        defendants = [p for p in parties if p.role == "defendant"]
        self.assertEqual(len(defendants), 3)
        
        defendant_names = [d.name for d in defendants]
        self.assertIn("EQUIFAX INC.", defendant_names)
        self.assertIn("EXPERIAN LLC", defendant_names)
        self.assertIn("TRANSUNION LLC", defendant_names)
    
    def test_extract_denial_information(self):
        """Test extraction of credit denial information."""
        text = """
        On March 20, 2025, Plaintiff was denied a mortgage loan
        by First National Bank due to information in credit report.
        """
        entities = self.extractor.extract_legal_entities(text)
        
        # Should extract denial date and creditor
        self.assertTrue(any("March 20, 2025" in str(e) for e in entities))
        self.assertTrue(any("First National Bank" in str(e) for e in entities))


class TestCaseConsolidator(unittest.TestCase):
    
    def setUp(self):
        self.consolidator = CaseConsolidator()
    
    def create_mock_extraction_result(self, text, confidence=0.8, legal_entities=None):
        """Helper to create mock extraction results."""
        result = ExtractionResult(
            success=True,
            text=text,
            confidence=confidence,
            legal_entities=legal_entities or []
        )
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
            
            self.assertEqual(consolidated.case_information.case_number, "1:25-cv-02156")
            self.assertIn("SOUTHERN DISTRICT OF NEW YORK", consolidated.case_information.court_name)
    
    def test_consolidate_multiple_documents_consistent(self):
        """Test consolidation with consistent information across documents."""
        doc1_text = """
        Case No. 1:25-cv-02156
        SARAH JOHNSON v. TRANSUNION LLC
        """
        
        doc2_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        Case: 1:25-cv-02156
        """
        
        results = [
            self.create_mock_extraction_result(doc1_text),
            self.create_mock_extraction_result(doc2_text)
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            self.assertEqual(consolidated.case_information.case_number, "1:25-cv-02156")
            self.assertIn("SOUTHERN DISTRICT OF NEW YORK", consolidated.case_information.court_name)
    
    def test_consolidate_conflicting_information(self):
        """Test consolidation with conflicting case numbers."""
        doc1_text = "Case No. 1:25-cv-02156"
        doc2_text = "Case No. 1:25-cv-99999"
        
        results = [
            self.create_mock_extraction_result(doc1_text),
            self.create_mock_extraction_result(doc2_text)
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Should have warnings about conflicting information
            self.assertTrue(len(consolidated.warnings) > 0)
            
            # Should pick one of the case numbers
            self.assertIsNotNone(consolidated.case_information.case_number)
    
    def test_confidence_calculation(self):
        """Test overall confidence calculation."""
        high_confidence_result = self.create_mock_extraction_result("text1", confidence=0.9)
        low_confidence_result = self.create_mock_extraction_result("text2", confidence=0.3)
        
        results = [high_confidence_result, low_confidence_result]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Should average the confidences
            expected_confidence = (0.9 + 0.3) / 2
            self.assertAlmostEqual(consolidated.extraction_confidence, expected_confidence, places=2)
    
    def test_empty_results(self):
        """Test consolidation with no extraction results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, [])
            
            self.assertEqual(consolidated.extraction_confidence, 0.0)
            self.assertIsNone(consolidated.case_information.case_number)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete legal extraction workflows."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_fcra_case_workflow(self):
        """Test complete FCRA case processing workflow."""
        
        # Mock documents from an FCRA case
        summons_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        
        SUMMONS
        """
        
        denial_letter_text = """
        Dear Ms. Johnson,
        
        We regret to inform you that your mortgage loan application
        has been denied due to information contained in your credit report
        from TransUnion LLC.
        
        Date: March 20, 2025
        First National Bank
        """
        
        attorney_notes_text = """
        CLIENT: Sarah Johnson
        CASE: 1:25-cv-02156 (S.D.N.Y.)
        
        Client was denied mortgage loan by First National Bank
        on March 20, 2025 due to credit report errors.
        Dispute filed with TransUnion but inadequate investigation.
        
        FCRA violation - failure to conduct reasonable investigation.
        """
        
        # Process each document
        results = []
        for text in [summons_text, denial_letter_text, attorney_notes_text]:
            case_info = self.extractor.extract_case_information(text)
            legal_entities = self.extractor.extract_legal_entities(text)
            
            result = ExtractionResult(
                success=True,
                text=text
            )
            result.file_path = "test.txt"
            result.extracted_text = text
            results.append(result)
        
        # Consolidate case
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Verify consolidation results
            self.assertEqual(consolidated.case_information.case_number, "1:25-cv-02156")
            self.assertEqual(consolidated.case_information.court_name, "UNITED STATES DISTRICT COURT")
            
            # Should identify key parties
            self.assertIsNotNone(consolidated.plaintiff)
            self.assertGreater(len(consolidated.defendants), 0)
            
            self.assertIn("SARAH JOHNSON", consolidated.plaintiff['name'])
            self.assertIn("TRANSUNION LLC", consolidated.defendants[0]['name'])
    
    def test_complaint_json_generation(self):
        """Test generation of complaint.json from consolidated case."""
        
        # Create a minimal consolidated case
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock extraction results
            text = """
            UNITED STATES DISTRICT COURT
            SOUTHERN DISTRICT OF NEW YORK
            
            SARAH JOHNSON,
                                            Plaintiff,
            v.                                      Case No. 1:25-cv-02156
            TRANSUNION LLC,
                                            Defendant.
            """
            
            case_info = self.extractor.extract_case_information(text)
            legal_entities = self.extractor.extract_legal_entities(text)
            
            result = ExtractionResult(
                success=True,
                text=text,
                confidence=0.8,
                legal_entities=legal_entities
            )
            
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, [result])
            
            # Generate complaint JSON
            complaint_json = self.consolidator.generate_complaint_json(consolidated)
            
            # Verify JSON structure
            self.assertIn("case_information", complaint_json)
            self.assertIn("plaintiff", complaint_json)
            self.assertIn("defendants", complaint_json)
            self.assertIn("tiger_metadata", complaint_json)
            
            # Verify case information
            case_info = complaint_json["case_information"]
            self.assertEqual(case_info["case_number"], "1:25-cv-02156")
            self.assertIn("SOUTHERN DISTRICT OF NEW YORK", case_info["court_district"])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_malformed_case_numbers(self):
        """Test handling of malformed case numbers."""
        text = "Case No. INVALID-FORMAT-123"
        result = self.extractor.extract_case_information(text)
        
        # Should not extract invalid format
        self.assertIsNone(result.case_number)
    
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
        legal_entities = self.extractor.extract_legal_entities(text)
        
        self.assertIsNone(case_info.case_number)
        self.assertEqual(len(legal_entities), 0)
    
    def test_mixed_document_types(self):
        """Test consolidation with mix of legal and non-legal documents."""
        legal_text = "Case No. 1:25-cv-02156\nSARAH JOHNSON v. TRANSUNION LLC"
        non_legal_text = "Shopping list: milk, bread, eggs"
        
        results = [
            ExtractionResult(success=True, text=legal_text, confidence=0.8),
            ExtractionResult(success=True, text=non_legal_text, confidence=0.1)
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Should still extract legal information
            self.assertEqual(consolidated.case_information.case_number, "1:25-cv-02156")
            
            # Should reflect lower overall confidence due to mixed content
            self.assertLess(consolidated.extraction_confidence, 0.8)


if __name__ == "__main__":
    # Run specific test suites
    loader = unittest.TestLoader()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLegalEntityExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestCaseConsolidator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"LEGAL EXTRACTION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")