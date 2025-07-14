
import unittest
import os
from app.engines.text_engine import TextEngine

class TestProcessTextFile(unittest.TestCase):
    def setUp(self):
        self.text_engine = TextEngine()
        self.test_data_dir = 'test-data/sample_case_files/'

    def test_process_text_file(self):
        file_path = os.path.join(self.test_data_dir, 'notes.txt')
        result = self.text_engine.process_document(file_path)
        self.assertTrue(result.success)
        self.assertGreater(len(result.text), 0)

if __name__ == '__main__':
    unittest.main()
