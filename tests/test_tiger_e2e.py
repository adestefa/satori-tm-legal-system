import unittest
import json
import os

class TestTigerE2E(unittest.TestCase):

    def setUp(self):
        # Path to the generated complaint.json (relative to project root)
        self.json_path = 'data/output/sample_case_files_complaint.json'
        
        # Check if the test file exists, if not use alternate path
        if not os.path.exists(self.json_path):
            # Alternative path for generated complaint files
            alt_path = 'data/output/processed/sample_case_files_complaint.json'
            if os.path.exists(alt_path):
                self.json_path = alt_path
            else:
                self.skipTest(f"Test complaint.json not found at {self.json_path} or {alt_path}. Generate it first with: ./satori-tiger case-extract test-data/sample_case_files/ --complaint-json")
        
        with open(self.json_path, 'r') as f:
            self.complaint_data = json.load(f)

    def test_case_information(self):
        case_info = self.complaint_data.get('case_information', {})
        self.assertEqual(case_info.get('court_type'), 'UNITED STATES DISTRICT COURT')
        self.assertEqual(case_info.get('court_district'), 'Eastern District of New York')
        self.assertEqual(case_info.get('case_number'), '1.25-cv-01987')
        self.assertTrue(case_info.get('jury_demand'))

    def test_plaintiff_info(self):
        plaintiff = self.complaint_data.get('plaintiff', {})
        self.assertEqual(plaintiff.get('name'), 'Eman Youssef')
        self.assertEqual(plaintiff.get('address', {}).get('street'), '123 Main St')
        self.assertEqual(plaintiff.get('phone'), '(555) 555-5555')
        self.assertEqual(plaintiff.get('email'), 'eman.youssef@example.com')
        self.assertEqual(plaintiff.get('residency'), 'State of New York')

    def test_plaintiff_counsel_info(self):
        counsel = self.complaint_data.get('plaintiff_counsel', {})
        self.assertNotEqual(counsel, {}, "Plaintiff counsel should not be empty")
        self.assertEqual(counsel.get('name'), 'K. Mallon')
        self.assertEqual(counsel.get('firm'), 'Consumer Protection Firm, P.C.')

    def test_defendants_info(self):
        defendants = self.complaint_data.get('defendants', [])
        self.assertEqual(len(defendants), 4)
        expected_names = ['Equifax Information Services, LLC', 'Experian Information Solutions, Inc.', 'Trans Union, LLC', 'TD Bank, N.A.']
        extracted_names = [d.get('name') for d in defendants]
        self.assertCountEqual(extracted_names, expected_names)

    def test_factual_background(self):
        background = self.complaint_data.get('factual_background', {})
        self.assertGreater(len(background.get('events', [])), 1)
        self.assertIn('Atty_Notes.docx', background.get('additional_notes', ''))

    def test_damages_denials(self):
        denials = self.complaint_data.get('damages', {}).get('denials', [])
        self.assertEqual(len(denials), 3)
        for denial in denials:
            self.assertNotEqual(denial.get('creditor'), 'Proportion of balances to credit limits on bank')

if __name__ == '__main__':
    unittest.main()
