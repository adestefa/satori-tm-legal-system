#!/usr/bin/env python3
"""
Comprehensive test script for Tiger Legal Extraction System.
Includes functionality, performance, and integration testing.
"""

import unittest
import time
import tempfile
import os
import sys

from app.core.extractors.legal_entity_extractor import LegalEntityExtractor
from app.core.processors.case_consolidator import CaseConsolidator
from app.engines.base_engine import ExtractionResult


class TestLegalExtractionPerformance(unittest.TestCase):
    """Performance tests for legal extraction system."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_extraction_speed(self):
        """Test extraction speed for typical legal documents."""
        legal_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        
        COMPLAINT FOR DAMAGES
        """ * 10  # Make it longer for realistic testing
        
        start_time = time.time()
        result = self.extractor.extract_case_information(legal_text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should process quickly
        self.assertLess(processing_time, 1.0, "Extraction should take less than 1 second")
        self.assertIsNotNone(result.case_number)
        
        print(f"Extraction time: {processing_time:.3f}s for {len(legal_text)} chars")
    
    def test_batch_processing_performance(self):
        """Test performance of processing multiple documents."""
        documents = []
        for i in range(5):
            doc = f"""
            UNITED STATES DISTRICT COURT
            SOUTHERN DISTRICT OF NEW YORK
            
            CASE {i}: JOHN DOE {i},
                                            Plaintiff,
            v.                                      Case No. 1:25-cv-{i:05d}
            DEFENDANT CORP {i},
                                            Defendant.
            """
            documents.append(doc)
        
        # Test batch processing
        start_time = time.time()
        
        results = []
        for i, text in enumerate(documents):
            case_info = self.extractor.extract_case_information(text)
            entities = self.extractor.extract_legal_entities(text)
            
            result = ExtractionResult(success=True, text=text)
            result.extracted_text = text
            result.file_path = f"test_doc_{i}.txt"
            results.append(result)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process all documents quickly
        docs_per_second = len(documents) / processing_time
        
        self.assertGreater(docs_per_second, 2, "Should process at least 2 documents per second")
        print(f"Batch processing: {docs_per_second:.1f} docs/sec")
        
        # Test consolidation performance
        with tempfile.TemporaryDirectory() as temp_dir:
            start_time = time.time()
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            end_time = time.time()
            
            consolidation_time = end_time - start_time
            self.assertLess(consolidation_time, 2.0, "Consolidation should take less than 2 seconds")
            print(f"Consolidation time: {consolidation_time:.3f}s for {len(results)} documents")
    
    def test_large_document_processing(self):
        """Test processing of large documents."""
        # Process a large document (without memory monitoring)
        large_text = "Legal document content. " * 10000  # ~250KB
        
        start_time = time.time()
        case_info = self.extractor.extract_case_information(large_text)
        entities = self.extractor.extract_legal_entities(large_text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(processing_time, 5.0, "Large document should process within 5 seconds")
        self.assertIsNotNone(case_info)
        self.assertIsInstance(entities, dict)
        
        print(f"Large document processing: {processing_time:.3f}s for {len(large_text)} chars")


class TestLegalExtractionAccuracy(unittest.TestCase):
    """Accuracy tests for legal extraction system."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
    
    def test_case_number_accuracy(self):
        """Test accuracy of case number extraction."""
        test_cases = [
            ("Case No. 1:25-cv-02156", "1:25-cv-02156"),
            ("Civil Action No. 2:24-cv-12345", "2:24-cv-12345"),
            ("Case Number: 1:25-cv-02156", "1:25-cv-02156"),
            ("Docket No. 3:23-cv-67890", "3:23-cv-67890")
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.extractor.extract_case_information(text)
                self.assertEqual(result.case_number, expected, 
                               f"Failed to extract {expected} from '{text}'")
    
    def test_court_detection_accuracy(self):
        """Test accuracy of court detection."""
        test_cases = [
            "UNITED STATES DISTRICT COURT\nSOUTHERN DISTRICT OF NEW YORK",
            "UNITED STATES DISTRICT COURT\nEASTERN DISTRICT OF NEW YORK", 
            "UNITED STATES DISTRICT COURT\nNORTHERN DISTRICT OF CALIFORNIA"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = self.extractor.extract_case_information(text)
                self.assertIsNotNone(result.court_name, f"Failed to detect court in: {text}")
                self.assertIn("DISTRICT COURT", result.court_name)
    
    def test_entity_extraction_completeness(self):
        """Test completeness of entity extraction."""
        complex_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON and MICHAEL JOHNSON,
                                        Plaintiffs,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC, EXPERIAN LLC,
        and EQUIFAX INC.,
                                        Defendants.
        
        COMPLAINT FOR DAMAGES UNDER THE FCRA
        
        Plaintiff was denied credit on March 15, 2025.
        """
        
        case_info = self.extractor.extract_case_information(complex_text)
        entities = self.extractor.extract_legal_entities(complex_text)
        
        # Should extract key information
        self.assertEqual(case_info.case_number, "1:25-cv-02156")
        self.assertIsNotNone(case_info.court_name)
        
        # Should extract entities
        self.assertIsInstance(entities, dict)
        
        # Should have some entities extracted
        total_entities = sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in entities.values())
        self.assertGreater(total_entities, 0, "Should extract entities from complex document")


class TestLegalExtractionRobustness(unittest.TestCase):
    """Robustness tests for edge cases and error conditions."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_malformed_input_handling(self):
        """Test handling of malformed or unusual input."""
        test_cases = [
            "",  # Empty string
            " ",  # Whitespace only
            "No legal content here",  # Non-legal content
            "CASE NO. INVALID-123-ABC",  # Invalid case number format
            "Court: Some Random Court Name",  # Non-standard court
        ]
        
        for text in test_cases:
            with self.subTest(text=repr(text)):
                try:
                    case_info = self.extractor.extract_case_information(text)
                    entities = self.extractor.extract_legal_entities(text)
                    
                    # Should not crash and should return valid objects
                    self.assertIsNotNone(case_info)
                    self.assertIsInstance(entities, dict)
                    
                except Exception as e:
                    self.fail(f"Extraction failed on input {repr(text)}: {e}")
    
    def test_large_input_handling(self):
        """Test handling of very large inputs."""
        # Create a 1MB text document
        large_text = "This is legal content. " * 50000  # ~1MB
        
        try:
            start_time = time.time()
            case_info = self.extractor.extract_case_information(large_text)
            entities = self.extractor.extract_legal_entities(large_text)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            self.assertLess(processing_time, 10.0, "Large document should process within 10 seconds")
            
            # Should return valid results
            self.assertIsNotNone(case_info)
            self.assertIsInstance(entities, dict)
            
        except Exception as e:
            self.fail(f"Failed to process large document: {e}")
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        unicode_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        José María González,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        ACME CORP™,
                                        Defendant.
        
        Filing date: March 15th, 2025 — Important case
        """
        
        try:
            case_info = self.extractor.extract_case_information(unicode_text)
            entities = self.extractor.extract_legal_entities(unicode_text)
            
            # Should handle unicode correctly
            self.assertEqual(case_info.case_number, "1:25-cv-02156")
            self.assertIsInstance(entities, dict)
            
        except Exception as e:
            self.fail(f"Failed to process unicode text: {e}")


def run_comprehensive_tests():
    """Run all comprehensive tests and print results."""
    print("🐅 TIGER LEGAL EXTRACTION - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestLegalExtractionPerformance,
        TestLegalExtractionAccuracy,
        TestLegalExtractionRobustness
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2, buffer=False)
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    success_count = result.testsRun - len(result.failures) - len(result.errors)
    success_rate = (success_count / result.testsRun * 100) if result.testsRun > 0 else 0
    total_time = end_time - start_time
    
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {success_count} ✅")
    print(f"Failures: {len(result.failures)} ❌")
    print(f"Errors: {len(result.errors)} 🚨")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! Tiger system is performing exceptionally well.")
    elif success_rate >= 75:
        print("\n✅ GOOD! Tiger system is working well with minor issues.")
    else:
        print("\n⚠️ ATTENTION NEEDED! Some tests are failing.")
    
    return success_rate >= 75


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)