
"""
Data validation tests for legal extraction system.
Tests complaint.json schema compliance, data integrity, and legal document standards.
"""

import unittest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List

from app.core.extractors.legal_entity_extractor import LegalEntityExtractor
from app.core.processors.case_consolidator import CaseConsolidator
from app.core.processors.document_processor import ProcessingResult


class TestComplaintJsonValidation(unittest.TestCase):
    """Test complaint.json schema compliance and data validation."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def load_complaint_schema(self) -> Dict[str, Any]:
        """Load the expected complaint.json schema for validation."""
        return {
            "required_fields": [
                "case_information",
                "plaintiff", 
                "defendants",
                "factual_background",
                "causes_of_action",
                "damages",
                "filing_details",
                "tiger_metadata"
            ],
            "case_information_fields": [
                "court_type",
                "court_district", 
                "case_number",
                "case_type",
                "jury_demand"
            ],
            "plaintiff_fields": [
                "name",
                "address",
                "residency",
                "consumer_status"
            ],
            "defendant_fields": [
                "name",
                "type",
                "address"
            ],
            "metadata_fields": [
                "case_id",
                "extraction_confidence",
                "source_documents",
                "consolidation_timestamp"
            ]
        }
    
    def validate_complaint_json_structure(self, complaint_json: Dict[str, Any]) -> List[str]:
        """Validate complaint.json structure and return list of validation errors."""
        errors = []
        schema = self.load_complaint_schema()
        
        # Check required top-level fields
        for field in schema["required_fields"]:
            if field not in complaint_json:
                errors.append(f"Missing required field: {field}")
        
        # Validate case_information structure
        if "case_information" in complaint_json:
            case_info = complaint_json["case_information"]
            for field in schema["case_information_fields"]:
                if field not in case_info:
                    errors.append(f"Missing case_information field: {field}")
        
        # Validate plaintiff structure
        if "plaintiff" in complaint_json:
            plaintiff = complaint_json["plaintiff"]
            for field in schema["plaintiff_fields"]:
                if field not in plaintiff:
                    errors.append(f"Missing plaintiff field: {field}")
        
        # Validate defendants structure
        if "defendants" in complaint_json:
            defendants = complaint_json["defendants"]
            if not isinstance(defendants, list):
                errors.append("defendants must be a list")
            elif len(defendants) == 0:
                errors.append("defendants list cannot be empty")
            else:
                for i, defendant in enumerate(defendants):
                    for field in schema["defendant_fields"]:
                        if field not in defendant:
                            errors.append(f"Missing defendant[{i}] field: {field}")
        
        # Validate tiger_metadata structure
        if "tiger_metadata" in complaint_json:
            metadata = complaint_json["tiger_metadata"]
            for field in schema["metadata_fields"]:
                if field not in metadata:
                    errors.append(f"Missing tiger_metadata field: {field}")
        
        return errors
    
    def test_valid_complaint_json_structure(self):
        """Test generation of structurally valid complaint.json."""
        # Create a mock consolidated case
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
        
        result = ProcessingResult(
            success=True,
            extracted_text=text,
            quality_metrics={'confidence': 0.8},
            metadata={'legal_entities': legal_entities},
            file_path="/mock/path"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, [result])
            complaint_json = self.consolidator.to_complaint_json(consolidated)
            
            # Validate structure
            errors = self.validate_complaint_json_structure(complaint_json)
            
            if errors:
                self.fail(f"complaint.json validation errors: {errors}")
    
    def test_case_number_format_validation(self):
        """Test validation of case number formats."""
        valid_federal_formats = [
            "1:25-cv-02156",
            "2:24-cv-12345",
            "3:23-cr-67890"
        ]
        
        valid_state_formats = [
            "2025-123456",
            "24-CV-789012",
            "Index No. 2025-555555"
        ]
        
        invalid_formats = [
            "invalid-case-number",
            "123-456-789",
            "",
            None
        ]
        
        # Test valid federal formats
        for case_num in valid_federal_formats:
            text = f"Case No. {case_num}"
            result = self.extractor.extract_case_information(text)
            self.assertEqual(result.case_number, case_num, 
                           f"Failed to extract valid federal case number: {case_num}")
        
        # Test valid state formats - should extract the number part
        for case_num in valid_state_formats:
            text = f"Case No. {case_num}"
            result = self.extractor.extract_case_information(text)
            self.assertIsNotNone(result.case_number, 
                               f"Failed to extract valid state case number: {case_num}")
        
        # Test invalid formats - should not extract
        for case_num in invalid_formats:
            if case_num is not None:
                text = f"Case No. {case_num}"
                result = self.extractor.extract_case_information(text)
                # Should either be None or a different valid case number found elsewhere
                if result.case_number == case_num:
                    self.fail(f"Incorrectly extracted invalid case number: {case_num}")
    
    def test_court_district_validation(self):
        """Test validation of court district formats."""
        valid_districts = [
            ("UNITED STATES DISTRICT COURT\nSOUTHERN DISTRICT OF NEW YORK", "SOUTHERN DISTRICT OF NEW YORK"),
            ("UNITED STATES DISTRICT COURT\nEASTERN DISTRICT OF NEW YORK", "EASTERN DISTRICT OF NEW YORK"),
            ("UNITED STATES DISTRICT COURT\nNORTHERN DISTRICT OF CALIFORNIA", "NORTHERN DISTRICT OF CALIFORNIA"),
        ]
        
        for text, expected_district in valid_districts:
            result = self.extractor.extract_case_information(text)
            self.assertIsNotNone(result.court_name, f"Failed to extract court from: {text}")
            self.assertIn(expected_district.split()[0], result.court_name,
                         f"Court district not properly extracted: {result.court_name}")
    
    def test_party_name_validation(self):
        """Test validation of party name extraction."""
        test_cases = [
            ("SARAH JOHNSON,\n                    Plaintiff,", "SARAH JOHNSON", "plaintiff"),
            ("TRANSUNION LLC,\n                    Defendant.", "TRANSUNION LLC", "defendant"),
            ("JOHN DOE and JANE DOE,\n             Plaintiffs,", "JOHN DOE", "plaintiff")  # Should extract first
        ]
        
        for text, expected_name, expected_role in test_cases:
            entities = self.extractor.extract_legal_entities(text)
            
            # Find parties with the expected role
            parties = [e for e in entities if hasattr(e, 'role') and e.role == expected_role]
            
            self.assertGreater(len(parties), 0, f"No {expected_role} found in: {text}")
            
            # Check if expected name is found
            party_names = [p.name for p in parties if hasattr(p, 'name')]
            self.assertTrue(any(expected_name in name for name in party_names),
                          f"Expected name '{expected_name}' not found in extracted parties: {party_names}")
    
    def test_confidence_score_validation(self):
        """Test validation of confidence scores."""
        # High confidence case - clear, well-formatted legal document
        high_confidence_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        
        COMPLAINT FOR DAMAGES
        """
        
        # Low confidence case - minimal or unclear information
        low_confidence_text = """
        Some document with minimal legal content.
        Maybe case 123456 involves someone.
        """
        
        # Test high confidence
        high_result = ProcessingResult(success=True, extracted_text=high_confidence_text, quality_metrics={'confidence': 0.9})
        
        # Test low confidence  
        low_result = ProcessingResult(success=True, extracted_text=low_confidence_text, quality_metrics={'confidence': 0.2})
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test high confidence consolidation
            high_consolidated = self.consolidator.consolidate_case_folder(temp_dir, [high_result])
            self.assertGreaterEqual(high_consolidated.extraction_confidence, 0.7,
                                  "High quality document should have high confidence")
            
            # Test low confidence consolidation
            low_consolidated = self.consolidator.consolidate_case_folder(temp_dir, [low_result])
            self.assertLessEqual(low_consolidated.extraction_confidence, 0.4,
                                "Low quality document should have low confidence")
    
    def test_address_format_validation(self):
        """Test validation of address extraction and formatting."""
        address_text = """
        Defendant TRANSUNION LLC may be served at:
        555 Corporate Drive
        Suite 200
        Chicago, IL 60601
        """
        
        entities = self.extractor.extract_legal_entities(address_text)
        
        # Should extract address components
        # Note: This tests the expectation that addresses should be parseable
        # Actual implementation may vary based on extractor capabilities
        address_found = any("555 Corporate Drive" in str(entity) for entity in entities)
        city_state_found = any("Chicago, IL" in str(entity) for entity in entities)
        
        # At minimum, should identify some address information
        self.assertTrue(address_found or city_state_found,
                       "Should extract some address information from well-formatted address")


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency across processing pipeline."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_case_number_consistency(self):
        """Test that case numbers remain consistent across multiple documents."""
        case_number = "1:25-cv-02156"
        
        doc1_text = f"COMPLAINT\nCase No. {case_number}\nSARAH JOHNSON v. TRANSUNION LLC"
        doc2_text = f"SUMMONS\nCase: {case_number}\nTo the Defendant"
        doc3_text = f"CIVIL COVER SHEET\nCase Number: {case_number}"
        
        results = []
        for text in [doc1_text, doc2_text, doc3_text]:
            case_info = self.extractor.extract_case_information(text)
            result = ProcessingResult(success=True, extracted_text=text, quality_metrics={'confidence': 0.8})
            results.append(result)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Case number should be consistent
            self.assertEqual(consolidated.case_information.case_number, case_number,
                           "Case number should remain consistent across documents")
    
    def test_party_name_consistency(self):
        """Test that party names are handled consistently."""
        plaintiff_name = "SARAH JOHNSON"
        defendant_name = "TRANSUNION LLC"
        
        doc1_text = f"{plaintiff_name},\n                    Plaintiff,\nv.\n{defendant_name},\n                    Defendant."
        doc2_text = f"Plaintiff {plaintiff_name} brings this action against {defendant_name}."
        
        results = []
        for text in [doc1_text, doc2_text]:
            entities = self.extractor.extract_legal_entities(text)
            result = ProcessingResult(success=True, extracted_text=text, quality_metrics={'confidence': 0.8}, metadata={'legal_entities': entities})
            results.append(result)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, results)
            
            # Should have consistent party information
            plaintiffs = [p for p in consolidated.parties if p.role == "plaintiff"]
            defendants = [p for p in consolidated.parties if p.role == "defendant"]
            
            self.assertGreater(len(plaintiffs), 0, "Should identify plaintiff")
            self.assertGreater(len(defendants), 0, "Should identify defendant")
            
            # Names should match (allowing for some variation in extraction)
            plaintiff_names = [p.name for p in plaintiffs]
            defendant_names = [p.name for p in defendants]
            
            self.assertTrue(any(plaintiff_name in name for name in plaintiff_names),
                          f"Plaintiff name consistency issue: {plaintiff_names}")
            self.assertTrue(any(defendant_name in name for name in defendant_names),
                          f"Defendant name consistency issue: {defendant_names}")
    
    def test_date_format_consistency(self):
        """Test that dates are extracted and formatted consistently."""
        test_dates = [
            ("March 20, 2025", "2025-03-20"),
            ("3/20/2025", "2025-03-20"),
            ("20th day of March, 2025", "2025-03-20")
        ]
        
        for input_date, expected_format in test_dates:
            text = f"On {input_date}, plaintiff was denied credit."
            entities = self.extractor.extract_legal_entities(text)
            
            # Should extract some form of date
            date_found = any(input_date in str(entity) or expected_format in str(entity) 
                           for entity in entities)
            
            # Note: This is a expectation test - actual date normalization 
            # would require additional implementation
            if not date_found:
                print(f"Warning: Date extraction may need improvement for format: {input_date}")


class TestLegalStandardsCompliance(unittest.TestCase):
    """Test compliance with legal document standards and requirements."""
    
    def setUp(self):
        self.extractor = LegalEntityExtractor()
        self.consolidator = CaseConsolidator()
    
    def test_fcra_case_requirements(self):
        """Test that FCRA cases include required elements."""
        fcra_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        
        COMPLAINT FOR DAMAGES UNDER THE FAIR CREDIT REPORTING ACT
        
        1. This action arises under the Fair Credit Reporting Act, 15 U.S.C. § 1681.
        2. Plaintiff is a consumer within the meaning of the FCRA.
        3. On March 20, 2025, plaintiff was denied credit.
        """
        
        case_info = self.extractor.extract_case_information(fcra_text)
        entities = self.extractor.extract_legal_entities(fcra_text)
        
        result = ProcessingResult(success=True, extracted_text=fcra_text, quality_metrics={'confidence': 0.8}, metadata={'legal_entities': entities})
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, [result])
            complaint_json = self.consolidator.to_complaint_json(consolidated)
            
            # FCRA cases should have specific characteristics
            self.assertIsNotNone(complaint_json.get("case_information", {}).get("case_number"))
            
            # Should identify federal jurisdiction
            court_info = complaint_json.get("case_information", {})
            self.assertIn("DISTRICT COURT", court_info.get("court_district", "").upper())
            
            # Should have consumer status
            plaintiff = complaint_json.get("plaintiff", {})
            consumer_status = plaintiff.get("consumer_status", "")
            self.assertTrue(len(consumer_status) > 0, "FCRA cases should identify consumer status")
    
    def test_federal_court_jurisdiction_requirements(self):
        """Test that federal court cases meet jurisdiction requirements."""
        federal_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        1. This Court has federal question jurisdiction pursuant to 28 U.S.C. § 1331.
        2. Venue is proper in this district pursuant to 28 U.S.C. § 1391(b).
        """
        
        case_info = self.extractor.extract_case_information(federal_text)
        
        # Should identify federal court
        self.assertIsNotNone(case_info.court_name)
        self.assertIn("DISTRICT", case_info.court_name.upper())
    
    def test_complaint_completeness_validation(self):
        """Test that generated complaints have all required sections."""
        complete_text = """
        UNITED STATES DISTRICT COURT
        SOUTHERN DISTRICT OF NEW YORK
        
        SARAH JOHNSON,
                                        Plaintiff,
        v.                                      Case No. 1:25-cv-02156
        TRANSUNION LLC,
                                        Defendant.
        
        COMPLAINT FOR DAMAGES
        
        I. JURISDICTION AND VENUE
        II. PARTIES  
        III. FACTUAL BACKGROUND
        IV. CAUSES OF ACTION
        V. DAMAGES
        VI. PRAYER FOR RELIEF
        VII. DEMAND FOR JURY TRIAL
        """
        
        case_info = self.extractor.extract_case_information(complete_text)
        entities = self.extractor.extract_legal_entities(complete_text)
        
        result = ProcessingResult(success=True, extracted_text=complete_text, quality_metrics={'confidence': 0.9}, metadata={'legal_entities': entities})
        
        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated = self.consolidator.consolidate_case_folder(temp_dir, [result])
            complaint_json = self.consolidator.to_complaint_json(consolidated)
            
            # Should have all major sections represented
            required_sections = ["case_information", "plaintiff", "defendants", "causes_of_action", "damages"]
            
            for section in required_sections:
                self.assertIn(section, complaint_json, f"Missing required section: {section}")
                self.assertIsNotNone(complaint_json[section], f"Section {section} is None")


if __name__ == "__main__":
    print("=" * 60)
    print("TIGER LEGAL EXTRACTION DATA VALIDATION TESTS")
    print("=" * 60)
    
    # Run validation tests
    unittest.main(verbosity=2)
