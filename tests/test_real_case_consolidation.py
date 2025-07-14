
import unittest
import os
import tempfile
from app.engines.docling_engine import DoclingEngine
from app.engines.docx_engine import DocxEngine
from app.core.processors.case_consolidator import CaseConsolidator

from app.core.processors.document_processor import ProcessingResult

class TestRealCaseConsolidation(unittest.TestCase):
    def setUp(self):
        self.docling_engine = DoclingEngine()
        self.docx_engine = DocxEngine()
        self.consolidator = CaseConsolidator()
        self.test_data_dir = 'test-data/sample_case_files/'
        self.case_files = [
            'Summons_Experian.pdf',
            'Adverse_Action_Letter_Cap_One.pdf',
            'Atty_Notes.docx'
        ]

    def test_real_case_consolidation(self):
        processing_results = []
        for file_name in self.case_files:
            file_path = os.path.join(self.test_data_dir, file_name)
            if file_name.endswith('.pdf'):
                result = self.docling_engine.process_document(file_path)
            elif file_name.endswith('.docx'):
                result = self.docx_engine.process_document(file_path)
            else:
                continue
            
            if result.success:
                processing_results.append(
                    ProcessingResult(
                        file_path=file_path,
                        success=True,
                        extracted_text=result.text,
                        quality_metrics={'confidence': result.confidence},
                        metadata={'legal_entities': result.legal_entities}
                    )
                )

        self.assertEqual(len(processing_results), len(self.case_files), "Not all files were processed successfully.")

        with tempfile.TemporaryDirectory() as temp_dir:
            consolidated_case = self.consolidator.consolidate_case_folder(temp_dir, processing_results)
            print(consolidated_case)
            
            self.assertIsNotNone(consolidated_case)
            self.assertEqual(len(consolidated_case.source_documents), len(self.case_files))
            self.assertGreater(consolidated_case.extraction_confidence, 0)
            self.assertIsNotNone(consolidated_case.case_information.case_number)
            self.assertIsNotNone(consolidated_case.plaintiff)
            self.assertGreater(len(consolidated_case.defendants), 0)


if __name__ == '__main__':
    unittest.main()
