"""
Tests to verify that the Monkey schema can successfully parse a sample Tiger JSON file.
"""
import json
import unittest
from pathlib import Path
from pydantic import ValidationError

from monkey.core.schemas.legal_document import LegalDocument

class TestSchemaCompatibility(unittest.TestCase):

    def test_parse_hydrated_json(self):
        """
        Verify that the LegalDocument schema can parse the 'hydrated-test-0.json' file.
        """
        # Construct the absolute path to the test JSON file
        # This assumes the test is run from the root of the project.
        json_path = Path(__file__).parent.parent.parent / 'test-data' / 'test-json' / 'hydrated-test-0.json'
        
        self.assertTrue(json_path.exists(), f"Test JSON file not found at {json_path}")

        with open(json_path, 'r') as f:
            data = json.load(f)

        try:
            LegalDocument.model_validate(data)
        except ValidationError as e:
            self.fail(f"Schema validation failed: {e}")

if __name__ == '__main__':
    unittest.main()
