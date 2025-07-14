
import unittest
import os
from app.engines.docling_engine import DoclingEngine

class TestProcessSummons(unittest.TestCase):
    def setUp(self):
        self.docling_engine = DoclingEngine()
        self.test_data_dir = 'test-data/sample_case_files/'

    def test_process_summons(self):
        file_path = os.path.join(self.test_data_dir, 'Summons_Experian.pdf')
        result = self.docling_engine.process_document(file_path)
        self.assertTrue(result.success)
        self.assertGreater(len(result.text), 0)

if __name__ == '__main__':
    unittest.main()
