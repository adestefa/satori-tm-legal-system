#!/usr/bin/env python3
"""
Unit tests for the Legal Validators
Tests FCRA, Completeness, and Timeline validators
"""

import unittest
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.legal_validators.legal_validators import (
    FCRAValidator,
    CompletenessValidator,
    TimelineValidator,
    LegalValidatorSuite
)


class TestFCRAValidator(unittest.TestCase):
    """Test cases for FCRAValidator"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = FCRAValidator()
        
        # Valid FCRA case data
        self.valid_fcra_case = {
            'defendants': [
                {'name': 'Experian Information Solutions, Inc.'},
                {'name': 'Capital One Bank'}
            ],
            'timeline': [
                {
                    'date': '2024-07-15',
                    'event': 'Client disputed credit report errors with credit bureaus'
                },
                {
                    'date': '2024-06-01',
                    'event': 'Credit application denied due to erroneous information'
                }
            ]
        }
        
        # Invalid FCRA case data
        self.invalid_fcra_case = {
            'defendants': [
                {'name': 'Random Company LLC'}
            ],
            'timeline': [
                {
                    'date': '2024-07-15',
                    'event': 'Generic business meeting occurred'
                }
            ]
        }
    
    def test_valid_fcra_case(self):
        """Test validation of valid FCRA case"""
        errors = self.validator.validate(self.valid_fcra_case)
        self.assertEqual(len(errors), 0, f"Valid FCRA case should pass validation, but got errors: {errors}")
    
    def test_missing_credit_bureau(self):
        """Test detection of missing credit bureau defendant"""
        case_data = {
            'defendants': [
                {'name': 'Capital One Bank'}  # Has furnisher but no credit bureau
            ],
            'timeline': [
                {
                    'date': '2024-07-15',
                    'event': 'Client disputed credit report errors'
                },
                {
                    'date': '2024-06-01',
                    'event': 'Credit application denied'
                }
            ]
        }
        
        errors = self.validator.validate(case_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('credit bureau' in error.lower() for error in errors))
    
    def test_missing_furnisher(self):
        """Test detection of missing furnisher defendant"""
        case_data = {
            'defendants': [
                {'name': 'Experian Information Solutions, Inc.'}  # Has credit bureau but no furnisher
            ],
            'timeline': [
                {
                    'date': '2024-07-15',
                    'event': 'Client disputed credit report errors'
                },
                {
                    'date': '2024-06-01',
                    'event': 'Credit application denied'
                }
            ]
        }
        
        errors = self.validator.validate(case_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('furnisher' in error.lower() for error in errors))
    
    def test_missing_dispute_evidence(self):
        """Test detection of missing dispute evidence"""
        case_data = {
            'defendants': [
                {'name': 'Experian Information Solutions, Inc.'},
                {'name': 'Capital One Bank'}
            ],
            'timeline': [
                {
                    'date': '2024-06-01',
                    'event': 'Credit application denied'
                }
            ]
        }
        
        errors = self.validator.validate(case_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('dispute' in error.lower() for error in errors))
    
    def test_missing_adverse_action(self):
        """Test detection of missing adverse action"""
        case_data = {
            'defendants': [
                {'name': 'Experian Information Solutions, Inc.'},
                {'name': 'Capital One Bank'}
            ],
            'timeline': [
                {
                    'date': '2024-07-15',
                    'event': 'Client disputed credit report errors'
                }
            ]
        }
        
        errors = self.validator.validate(case_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('adverse action' in error.lower() for error in errors))
    
    def test_credit_bureau_name_variations(self):
        """Test recognition of various credit bureau name formats"""
        test_cases = [
            'Experian Information Solutions, Inc.',
            'EXPERIAN INFO SOLUTIONS',
            'TransUnion LLC',
            'TRANSUNION',
            'Equifax Information Services LLC',
            'EQUIFAX'
        ]
        
        for bureau_name in test_cases:
            case_data = {
                'defendants': [
                    {'name': bureau_name},
                    {'name': 'Capital One Bank'}
                ],
                'timeline': [
                    {'date': '2024-07-15', 'event': 'Client disputed credit report'},
                    {'date': '2024-06-01', 'event': 'Credit denied'}
                ]
            }
            
            errors = self.validator.validate(case_data)
            self.assertEqual(len(errors), 0, f"Should recognize {bureau_name} as credit bureau")
    
    def test_furnisher_name_variations(self):
        """Test recognition of various furnisher name formats"""
        test_cases = [
            'Capital One Bank',
            'Chase Credit Card Services',
            'Wells Fargo Financial',
            'Credit Union of America',
            'American Express Centurion Bank'
        ]
        
        for furnisher_name in test_cases:
            case_data = {
                'defendants': [
                    {'name': 'Experian Information Solutions, Inc.'},
                    {'name': furnisher_name}
                ],
                'timeline': [
                    {'date': '2024-07-15', 'event': 'Client disputed credit report'},
                    {'date': '2024-06-01', 'event': 'Credit denied'}
                ]
            }
            
            errors = self.validator.validate(case_data)
            self.assertEqual(len(errors), 0, f"Should recognize {furnisher_name} as furnisher")


class TestCompletenessValidator(unittest.TestCase):
    """Test cases for CompletenessValidator"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = CompletenessValidator()
        
        # Complete case data
        self.complete_case = {
            'plaintiff': {
                'name': 'Jane Doe',
                'address': {
                    'street': '123 Main Street',
                    'city_state_zip': 'New York, NY 10001'
                }
            },
            'defendants': [
                {'name': 'Experian Information Solutions, Inc.'},
                {'name': 'Capital One Bank'}
            ],
            'case_information': {
                'jurisdiction': 'Southern District of New York',
                'case_number': '1:24-cv-12345'
            },
            'timeline': [
                {'date': '2024-07-15', 'event': 'First event'},
                {'date': '2024-08-01', 'event': 'Second event'}
            ]
        }
    
    def test_complete_case(self):
        """Test validation of complete case"""
        errors = self.validator.validate(self.complete_case)
        self.assertEqual(len(errors), 0, f"Complete case should pass validation, but got errors: {errors}")
    
    def test_missing_plaintiff_name(self):
        """Test detection of missing plaintiff name"""
        case_data = self.complete_case.copy()
        case_data['plaintiff'] = {'address': {'street': '123 Main St', 'city_state_zip': 'NY, NY 10001'}}
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('plaintiff name' in error.lower() for error in errors))
    
    def test_missing_plaintiff_address(self):
        """Test detection of missing plaintiff address"""
        case_data = self.complete_case.copy()
        case_data['plaintiff'] = {'name': 'Jane Doe'}
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('plaintiff address' in error.lower() for error in errors))
    
    def test_incomplete_plaintiff_address(self):
        """Test detection of incomplete plaintiff address"""
        case_data = self.complete_case.copy()
        case_data['plaintiff']['address'] = {'street': '123 Main St'}  # Missing city/state
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('city/state' in error.lower() for error in errors))
    
    def test_missing_defendants(self):
        """Test detection of missing defendants"""
        case_data = self.complete_case.copy()
        case_data['defendants'] = []
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('no defendants' in error.lower() for error in errors))
    
    def test_defendant_missing_name(self):
        """Test detection of defendant without name"""
        case_data = self.complete_case.copy()
        case_data['defendants'] = [
            {'name': 'Experian Information Solutions, Inc.'},
            {'role': 'defendant'}  # Missing name
        ]
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('defendant #2' in error.lower() for error in errors))
    
    def test_missing_jurisdiction(self):
        """Test detection of missing jurisdiction"""
        case_data = self.complete_case.copy()
        case_data['case_information'] = {'case_number': '1:24-cv-12345'}
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('jurisdiction' in error.lower() for error in errors))
    
    def test_missing_case_number(self):
        """Test detection of missing case number"""
        case_data = self.complete_case.copy()
        case_data['case_information'] = {'jurisdiction': 'Southern District of New York'}
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('case number' in error.lower() for error in errors))
    
    def test_missing_timeline(self):
        """Test detection of missing timeline"""
        case_data = self.complete_case.copy()
        case_data['timeline'] = []
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('timeline' in error.lower() for error in errors))
    
    def test_insufficient_timeline_events(self):
        """Test detection of insufficient timeline events"""
        case_data = self.complete_case.copy()
        case_data['timeline'] = [{'date': '2024-07-15', 'event': 'Only one event'}]
        
        errors = self.validator.validate(case_data)
        self.assertTrue(any('multiple events' in error.lower() for error in errors))


class TestTimelineValidator(unittest.TestCase):
    """Test cases for TimelineValidator"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = TimelineValidator()
        
        # Valid timeline
        self.valid_timeline = [
            {'date': '2024-06-01', 'event': 'Credit application submitted'},
            {'date': '2024-06-15', 'event': 'Credit denied due to credit report'},
            {'date': '2024-07-01', 'event': 'Disputed errors with credit bureaus'},
            {'date': '2024-08-01', 'event': 'Filed legal complaint'}
        ]
    
    def test_valid_timeline(self):
        """Test validation of valid timeline"""
        case_data = {'timeline': self.valid_timeline}
        errors = self.validator.validate(case_data)
        self.assertEqual(len(errors), 0, f"Valid timeline should pass validation, but got errors: {errors}")
    
    def test_future_date_detection(self):
        """Test detection of future dates"""
        future_year = datetime.now().year + 1
        timeline = [
            {'date': '2024-06-01', 'event': 'Past event'},
            {'date': f'{future_year}-06-01', 'event': 'Future event'}
        ]
        
        case_data = {'timeline': timeline}
        errors = self.validator.validate(case_data)
        self.assertTrue(any('future date' in error.lower() for error in errors))
    
    def test_implausibly_old_date(self):
        """Test detection of implausibly old dates"""
        timeline = [
            {'date': '1850-06-01', 'event': 'Very old event'},
            {'date': '2024-06-01', 'event': 'Recent event'}
        ]
        
        case_data = {'timeline': timeline}
        errors = self.validator.validate(case_data)
        self.assertTrue(any('implausibly old' in error.lower() for error in errors))
    
    def test_chronological_order_violation(self):
        """Test detection of chronological order violations"""
        timeline = [
            {'date': '2024-08-01', 'event': 'Later event'},
            {'date': '2024-06-01', 'event': 'Earlier event'}  # Out of order
        ]
        
        case_data = {'timeline': timeline}
        errors = self.validator.validate(case_data)
        self.assertTrue(any('chronological order' in error.lower() for error in errors))
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        timeline = [
            {'date': 'not-a-date', 'event': 'Event with bad date'},
            {'date': '2024-06-01', 'event': 'Event with good date'}
        ]
        
        case_data = {'timeline': timeline}
        errors = self.validator.validate(case_data)
        self.assertTrue(any('invalid date format' in error.lower() for error in errors))
    
    def test_date_relationship_validation(self):
        """Test validation of logical date relationships"""
        # Filing before disputes is illogical
        timeline = [
            {'date': '2024-08-01', 'event': 'Filed legal complaint'},
            {'date': '2024-08-15', 'event': 'Disputed credit report errors'}  # After filing
        ]
        
        case_data = {'timeline': timeline}
        errors = self.validator.validate(case_data)
        self.assertTrue(any('complaint filed before' in error.lower() for error in errors))
    
    def test_multiple_date_formats(self):
        """Test parsing of multiple date formats"""
        timeline = [
            {'date': '2024-06-01', 'event': 'ISO format'},
            {'date': '06/15/2024', 'event': 'US format'},
            {'date': 'July 1, 2024', 'event': 'Long format'},
            {'date': 'Aug 15, 2024', 'event': 'Short month format'}
        ]
        
        case_data = {'timeline': timeline}
        errors = self.validator.validate(case_data)
        
        # Should not have chronological order errors if dates are parsed correctly
        chronological_errors = [e for e in errors if 'chronological order' in e.lower()]
        self.assertEqual(len(chronological_errors), 0, f"Should parse multiple date formats correctly")
    
    def test_empty_timeline(self):
        """Test handling of empty timeline"""
        case_data = {'timeline': []}
        errors = self.validator.validate(case_data)
        # Empty timeline should not cause errors in TimelineValidator (handled by CompletenessValidator)
        self.assertEqual(len(errors), 0)
    
    def test_timeline_with_missing_dates(self):
        """Test handling of timeline events without dates"""
        timeline = [
            {'date': '2024-06-01', 'event': 'Event with date'},
            {'event': 'Event without date'},  # No date field
            {'date': '2024-08-01', 'event': 'Another event with date'}
        ]
        
        case_data = {'timeline': timeline}
        errors = self.validator.validate(case_data)
        
        # Should not cause errors (events without dates are skipped)
        self.assertEqual(len(errors), 0)


class TestLegalValidatorSuite(unittest.TestCase):
    """Test cases for LegalValidatorSuite orchestrator"""
    
    def setUp(self):
        """Set up test environment"""
        self.suite = LegalValidatorSuite()
        
        # Comprehensive valid case
        self.valid_case = {
            'plaintiff': {
                'name': 'Jane Doe',
                'address': {
                    'street': '123 Main Street',
                    'city_state_zip': 'New York, NY 10001'
                }
            },
            'defendants': [
                {'name': 'Experian Information Solutions, Inc.'},
                {'name': 'Capital One Bank'}
            ],
            'case_information': {
                'jurisdiction': 'Southern District of New York',
                'case_number': '1:24-cv-12345'
            },
            'timeline': [
                {'date': '2024-06-01', 'event': 'Credit application denied'},
                {'date': '2024-07-15', 'event': 'Disputed errors with credit bureaus'},
                {'date': '2024-08-01', 'event': 'Filed legal complaint'}
            ]
        }
        
        # Comprehensive invalid case
        self.invalid_case = {
            'plaintiff': {'name': 'Jane Doe'},  # Missing address
            'defendants': [{'name': 'Random Company'}],  # Not FCRA-related
            'case_information': {},  # Missing jurisdiction and case number
            'timeline': [
                {'date': '2024-08-01', 'event': 'Filed complaint'},
                {'date': '2024-06-01', 'event': 'Earlier event'}  # Out of order
            ]
        }
    
    def test_valid_case_passes_all_validators(self):
        """Test that valid case passes all validators"""
        result = self.suite.validate_complaint(self.valid_case)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertIn('FCRAValidator', result['validator_results'])
        self.assertIn('CompletenessValidator', result['validator_results'])
        self.assertIn('TimelineValidator', result['validator_results'])
    
    def test_invalid_case_fails_multiple_validators(self):
        """Test that invalid case fails multiple validators"""
        result = self.suite.validate_complaint(self.invalid_case)
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
        
        # Should have errors from multiple validators
        failed_validators = [name for name, errors in result['validator_results'].items() if errors]
        self.assertGreater(len(failed_validators), 1)
    
    def test_validator_error_aggregation(self):
        """Test that errors from all validators are aggregated"""
        result = self.suite.validate_complaint(self.invalid_case)
        
        # Total errors should be sum of individual validator errors
        total_individual_errors = sum(
            len(errors) for errors in result['validator_results'].values()
        )
        
        self.assertEqual(len(result['errors']), total_individual_errors)
    
    def test_individual_validator_results_tracked(self):
        """Test that individual validator results are tracked"""
        result = self.suite.validate_complaint(self.invalid_case)
        
        # Each validator should have results
        expected_validators = ['FCRAValidator', 'CompletenessValidator', 'TimelineValidator']
        
        for validator_name in expected_validators:
            self.assertIn(validator_name, result['validator_results'])
            self.assertIsInstance(result['validator_results'][validator_name], list)
    
    def test_partial_failure_handling(self):
        """Test handling when some validators pass and others fail"""
        # Case that passes completeness but fails FCRA requirements
        partial_case = {
            'plaintiff': {
                'name': 'Jane Doe',
                'address': {
                    'street': '123 Main Street',
                    'city_state_zip': 'New York, NY 10001'
                }
            },
            'defendants': [{'name': 'Random Non-FCRA Company'}],  # Not FCRA-related
            'case_information': {
                'jurisdiction': 'Southern District of New York',
                'case_number': '1:24-cv-12345'
            },
            'timeline': [
                {'date': '2024-06-01', 'event': 'Some event'},
                {'date': '2024-07-15', 'event': 'Another event'}
            ]
        }
        
        result = self.suite.validate_complaint(partial_case)
        
        self.assertFalse(result['is_valid'])
        
        # CompletenessValidator should pass
        self.assertEqual(len(result['validator_results']['CompletenessValidator']), 0)
        
        # FCRAValidator should fail
        self.assertGreater(len(result['validator_results']['FCRAValidator']), 0)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios with realistic case data"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.suite = LegalValidatorSuite()
    
    def test_realistic_fcra_case_scenario(self):
        """Test validation of realistic FCRA case"""
        realistic_case = {
            'case_summary': {
                'case_number': '1:24-cv-12345',
                'jurisdiction': 'United States District Court for the Southern District of New York',
                'confidence': 85.5
            },
            'plaintiff': {
                'name': 'Jane Doe',
                'address': {
                    'street': '123 Oak Avenue',
                    'city_state_zip': 'Brooklyn, NY 11201'
                },
                'confidence': 0.95,
                'sources': ['complaint.pdf', 'attorney_notes.docx']
            },
            'defendants': [
                {
                    'name': 'EQUIFAX INFORMATION SERVICES LLC',
                    'confidence': 0.92,
                    'sources': ['complaint.pdf', 'summons.pdf']
                },
                {
                    'name': 'EXPERIAN INFORMATION SOLUTIONS, INC.',
                    'confidence': 0.91,
                    'sources': ['complaint.pdf']
                },
                {
                    'name': 'CAPITAL ONE BANK (USA), N.A.',
                    'confidence': 0.89,
                    'sources': ['complaint.pdf', 'adverse_action_letter.pdf']
                }
            ],
            'case_information': {
                'jurisdiction': 'Southern District of New York',
                'case_number': '1:24-cv-12345'
            },
            'timeline': [
                {
                    'date': '2024-03-15',
                    'event': 'Credit application submitted to Capital One',
                    'source': 'adverse_action_letter.pdf'
                },
                {
                    'date': '2024-03-18',
                    'event': 'Credit application denied due to adverse credit information',
                    'source': 'adverse_action_letter.pdf'
                },
                {
                    'date': '2024-04-01',
                    'event': 'Client disputed inaccurate information with Equifax and Experian',
                    'source': 'attorney_notes.docx'
                },
                {
                    'date': '2024-04-30',
                    'event': 'Credit bureaus completed reinvestigation without correction',
                    'source': 'attorney_notes.docx'
                },
                {
                    'date': '2024-05-15',
                    'event': 'Client sent second dispute to credit reporting agencies',
                    'source': 'attorney_notes.docx'
                },
                {
                    'date': '2024-07-01',
                    'event': 'Filed FCRA complaint in federal court',
                    'source': 'complaint.pdf'
                }
            ]
        }
        
        result = self.suite.validate_complaint(realistic_case)
        
        # Should pass all validators
        self.assertTrue(result['is_valid'], f"Realistic FCRA case should pass validation. Errors: {result['errors']}")
        self.assertEqual(len(result['errors']), 0)
        
        # Verify each validator passed
        for validator_name, errors in result['validator_results'].items():
            self.assertEqual(len(errors), 0, f"{validator_name} should pass for realistic case")
    
    def test_problematic_case_scenario(self):
        """Test validation of case with multiple issues"""
        problematic_case = {
            'plaintiff': {
                'name': '',  # Missing name
                'address': {'street': '123 Main St'}  # Incomplete address
            },
            'defendants': [
                {'role': 'defendant'},  # Missing name
                {'name': 'Generic Corp'}  # Not FCRA-related
            ],
            'case_information': {
                'case_number': ''  # Missing case number
            },
            'timeline': [
                {'date': '2025-12-01', 'event': 'Future event'},  # Future date
                {'date': '2024-08-01', 'event': 'Filed complaint'},
                {'date': '2024-06-01', 'event': 'Earlier event but listed later'}  # Out of order
            ]
        }
        
        result = self.suite.validate_complaint(problematic_case)
        
        # Should fail validation
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 5)  # Should have many errors
        
        # Each validator should find issues
        for validator_name, errors in result['validator_results'].items():
            self.assertGreater(len(errors), 0, f"{validator_name} should find issues in problematic case")


if __name__ == '__main__':
    unittest.main()