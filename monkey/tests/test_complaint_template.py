"""
Tests for the FCRA Complaint HTML Template.
"""
import json
import unittest
from pathlib import Path
from monkey.core.html_engine import HtmlEngine

class TestComplaintTemplate(unittest.TestCase):

    def test_render_complaint_template(self):
        """
        Verify that the HtmlEngine can render the FCRA complaint template
        with sample data.
        """
        engine = HtmlEngine()
        
        # Load sample JSON data
        json_path = Path(__file__).parent.parent.parent / 'test-data' / 'test-json' / 'hydrated-test-0.json'
        self.assertTrue(json_path.exists(), f"Test JSON file not found at {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Render the template
        rendered_html = engine.render_template("fcra/complaint.html", data)

        # Check for some key pieces of information
        self.assertIn("UNITED STATES DISTRICT COURT", rendered_html)
        self.assertIn("Eastern District of New York", rendered_html)
        self.assertIn("1:25-cv-01987", rendered_html)
        self.assertIn("Eman Youssef", rendered_html)
        self.assertIn("EQUIFAX INFORMATION SERVICES LLC", rendered_html)
        self.assertIn("VIOLATION OF THE FCRA", rendered_html)

if __name__ == '__main__':
    unittest.main()
