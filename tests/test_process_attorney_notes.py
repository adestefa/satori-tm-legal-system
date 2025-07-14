
import unittest
import os
from app.engines.docx_engine import DocxEngine

class TestProcessAttorneyNotes(unittest.TestCase):
    def setUp(self):
        self.docx_engine = DocxEngine()
        self.test_data_dir = 'test-data/sample_case_files/'

    def test_process_attorney_notes(self):
        file_path = os.path.join(self.test_data_dir, 'Atty_Notes.docx')
        result = self.docx_engine.process_document(file_path)
        self.assertTrue(result.success)
        self.assertGreater(len(result.text), 0)

if __name__ == '__main__':
    unittest.main()
