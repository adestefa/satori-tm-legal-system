#!/usr/bin/env python3
"""
Test cases for hydrated JSON support in Beaver Document Builder
Tests the enhanced document builder functionality with hydrated JSON format
"""

import json
import unittest
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from beaver.core.document_builder import BeaverDocumentBuilder
from beaver.core.validators import DocumentValidator

class TestHydratedJsonSupport(unittest.TestCase):
    """Test hydrated JSON support in document builder"""
    
    def setUp(self):
        """Set up test environment"""
        self.builder = BeaverDocumentBuilder()
        self.validator = DocumentValidator()
        
        # Sample hydrated JSON data
        self.hydrated_data = {
            "case_information": {
                "court_type": "UNITED STATES DISTRICT COURT",
                "court_district": "Eastern District of New York",
                "case_number": "1:25-cv-01987",
                "case_type": "Complaint",
                "jury_demand": True
            },
            "plaintiff": {
                "name": "John Doe",
                "address": {
                    "street": "123 Main Street",
                    "city_state_zip": "Queens, NY 11101",
                    "country": "USA"
                },
                "phone": "(555) 123-4567",
                "email": "john.doe@example.com",
                "residency_details": "Client lives in Queens",
                "consumer_status": "Individual 'consumer' within the meaning of both the FCRA and applicable state FCRA"
            },
            "plaintiff_counsel": {
                "name": "Attorney Smith",
                "firm": "Smith & Associates",
                "address": "456 Legal Avenue, New York, NY 10001",
                "phone": "(555) 987-6543",
                "email": "attorney@smithlaw.com"
            },
            "defendants": [
                {"name": "EQUIFAX INFORMATION SERVICES LLC", "type": "Consumer Reporting Agency"},
                {"name": "TRANS UNION LLC", "type": "Consumer Reporting Agency"},
                {"name": "TD BANK, N.A.", "type": "Furnisher of Information"}
            ],
            "factual_background": {
                "summary": "Plaintiff disputed fraudulent charges with defendant TD Bank, who failed to reasonably investigate.",
                "events": [
                    {"date": "2024-07-15", "description": "$7,500 in fraudulent charges occurred"},
                    {"date": "2024-07-20", "description": "Plaintiff filed police report"}
                ]
            },
            "causes_of_action": [
                {
                    "title": "FIRST CAUSE OF ACTION - VIOLATION OF THE FCRA",
                    "against_defendant_types": ["Consumer Reporting Agency", "Furnisher of Information"],
                    "allegations": [
                        {
                            "statute": "15 U.S.C. § 1681i",
                            "description": "Failure to conduct reasonable reinvestigations of the Plaintiff's multiple disputes.",
                            "applies_to_type": "Consumer Reporting Agency"
                        },
                        {
                            "statute": "15 U.S.C. § 1681s-2(b)",
                            "description": "Failure to conduct reasonable reinvestigations after receiving notice from CRAs.",
                            "applies_to_type": "Furnisher of Information"
                        }
                    ]
                }
            ],
            "damages": {
                "summary": "The erroneous information caused damage to reputation, adverse impact on credit rating, denial of credit.",
                "injunctive_relief_sought": True,
                "denials": [
                    {
                        "creditor": "Capital One",
                        "application_for": "Credit Card",
                        "date": "2024-08-01",
                        "reasons": ["Credit history"],
                        "reported_by_cra": "Equifax",
                        "credit_score": "650"
                    }
                ]
            },
            "filing_details": {
                "date": "2025-01-15"
            }
        }
    
    def test_hydrated_json_validation(self):
        """Test that the validator properly handles hydrated JSON format"""
        # Test validation
        result = self.validator.validate_complaint_data(self.hydrated_data)
        
        # Should be valid with no errors
        self.assertTrue(result.is_valid, f"Validation failed with errors: {result.errors}")
        self.assertEqual(len(result.errors), 0, f"Unexpected errors: {result.errors}")
        self.assertGreaterEqual(result.score, 80.0, f"Score too low: {result.score}")
    
    def test_hydrated_json_document_generation(self):
        """Test that the document builder properly handles hydrated JSON format"""
        # Generate document
        result = self.builder.build_complaint_package(self.hydrated_data)
        
        # Verify success
        self.assertTrue(result.success, f"Document generation failed: {result.errors}")
        self.assertIsNotNone(result.package, "Document package is None")
        self.assertIsNotNone(result.package.complaint, "Complaint document is None")
        
        # Verify content includes key elements from hydrated JSON
        content = result.package.complaint
        self.assertIn(self.hydrated_data['plaintiff']['name'], content, "Plaintiff name not found in document")
        self.assertIn(self.hydrated_data['case_information']['court_district'].upper(), content, "Court district not found")
        self.assertIn(self.hydrated_data['case_information']['case_number'], content, "Case number not found")
        
        # Verify causes of action are included
        for cause in self.hydrated_data['causes_of_action']:
            self.assertIn(cause['title'], content, f"Cause of action '{cause['title']}' not found")
    
    def test_structured_address_handling(self):
        """Test that structured address format is properly handled"""
        # Generate document
        result = self.builder.build_complaint_package(self.hydrated_data)
        
        # Verify success
        self.assertTrue(result.success, f"Document generation failed: {result.errors}")
        
        # Check that address components are accessible
        template_vars = self.builder._prepare_template_variables(self.hydrated_data)
        plaintiff_address = template_vars['plaintiff']['address']
        
        self.assertIsInstance(plaintiff_address, dict, "Address should remain as dict")
        self.assertIn('street', plaintiff_address, "Street component missing")
        self.assertIn('city_state_zip', plaintiff_address, "City/state/zip component missing")
    
    def test_causes_of_action_processing(self):
        """Test that causes of action are properly processed"""
        template_vars = self.builder._prepare_template_variables(self.hydrated_data)
        causes = template_vars['causes_of_action']
        
        # Should have at least one cause
        self.assertGreater(len(causes), 0, "No causes of action found")
        
        # Each cause should have required structure
        for cause in causes:
            self.assertIn('title', cause, "Cause missing title")
            self.assertIn('against_defendant_types', cause, "Cause missing defendant types")
            self.assertIn('allegations', cause, "Cause missing allegations")
            
            # Each allegation should be formatted as a string for template use
            for allegation in cause.get('allegations', []):
                self.assertIsInstance(allegation, str, "Allegation should be formatted as string for template")
                # Check that formatted allegation contains statute reference
                self.assertRegex(allegation, r'15 U\.S\.C\. §', "Allegation should contain statute reference")
    
    def test_damages_processing(self):
        """Test that damages information is properly processed"""
        template_vars = self.builder._prepare_template_variables(self.hydrated_data)
        damages = template_vars['damages']
        
        # Should have damages information
        self.assertIsInstance(damages, dict, "Damages should be a dict")
        self.assertIn('summary', damages, "Damages missing summary")
        
        # Should process denials
        denials = damages.get('denials', [])
        self.assertGreater(len(denials), 0, "No denials found")
        
        for denial in denials:
            # Required fields should be present (even if empty)
            self.assertIn('creditor', denial, "Denial missing creditor")
            self.assertIn('application_for', denial, "Denial missing application_for")
            self.assertIn('date', denial, "Denial missing date")
    
    def test_ny_specific_fields(self):
        """Test that NY-specific fields are properly handled"""
        # Add NY FCRA cause
        ny_data = self.hydrated_data.copy()
        ny_data['causes_of_action'].append({
            "title": "SECOND CAUSE OF ACTION - VIOLATION OF THE NY FCRA",
            "against_defendant_types": ["Consumer Reporting Agency"],
            "allegations": [
                {
                    "statute": "N.Y. GBL § 380-j(a)(3)",
                    "description": "Reporting erroneous information when they knew it was inaccurate."
                }
            ]
        })
        
        # Generate document
        result = self.builder.build_complaint_package(ny_data)
        
        # Verify success
        self.assertTrue(result.success, f"Document generation failed: {result.errors}")
        
        # Verify NY FCRA content is included
        content = result.package.complaint
        self.assertIn("NY FCRA", content, "NY FCRA reference not found")
        self.assertIn("N.Y. GBL", content, "NY statute reference not found")
    
    def test_incomplete_hydrated_json(self):
        """Test handling of incomplete hydrated JSON"""
        # Remove some optional fields
        incomplete_data = self.hydrated_data.copy()
        del incomplete_data['plaintiff_counsel']
        del incomplete_data['factual_background']['events']
        
        # Should still validate and generate
        validation_result = self.validator.validate_complaint_data(incomplete_data)
        self.assertTrue(validation_result.is_valid, "Should be valid even with missing optional fields")
        
        generation_result = self.builder.build_complaint_package(incomplete_data)
        self.assertTrue(generation_result.success, "Should generate even with missing optional fields")

if __name__ == '__main__':
    unittest.main()