"""
Tests for the Case Review HTML Template.
"""
import json
import unittest
from pathlib import Path
from monkey.core.html_engine import HtmlEngine

class TestCaseReviewTemplate(unittest.TestCase):

    def test_render_case_review_template(self):
        """
        Verify that the HtmlEngine can render the case review template
        with sample data.
        """
        engine = HtmlEngine()
        
        # Load sample JSON data
        json_path = Path(__file__).parent.parent.parent / 'test-data' / 'test-json' / 'hydrated-test-0.json'
        self.assertTrue(json_path.exists(), f"Test JSON file not found at {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Render the template
        rendered_html = engine.render_template("case_review.html", data)

        # Check for some key pieces of information
        self.assertIn(">Step 3: Review Extracted Data</h1>", rendered_html)
        self.assertIn(">Causes of Action</h2>", rendered_html)
        self.assertIn("Eman Youssef", rendered_html)
        self.assertIn("EQUIFAX INFORMATION SERVICES LLC", rendered_html)
        self.assertIn("VIOLATION OF THE FCRA", rendered_html)
        self.assertIn("1:25-cv-01987", rendered_html)

if __name__ == '__main__':
    unittest.main()
