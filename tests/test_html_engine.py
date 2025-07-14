"""
Tests for the HTML engine and PDF service.
"""

import unittest
from unittest.mock import MagicMock, patch
from monkey.core.html_engine import HtmlEngine
from monkey.core.pdf_service import PdfService

class TestHtmlEngine(unittest.TestCase):
    """
    Tests for the HTML engine.
    """

    def test_render_template(self):
        """
        Tests that the HTML engine can render a template.
        """
        html_engine = HtmlEngine("monkey/templates/html")
        context = {
            "case_information": {
                "court_type": "UNITED STATES DISTRICT COURT",
                "court_district": "Eastern District of New York",
                "case_number": "1:25-cv-01987",
            },
            "plaintiff": {
                "name": "Eman Youssef",
                "address": {
                    "city_state_zip": "Queens, NY"
                }
            },
            "defendants": [
                {"name": "EQUIFAX INFORMATION SERVICES LLC"}
            ],
            "factual_background": {
                "summary": "This is a summary.",
                "events": [
                    {"description": "Event 1"},
                    {"description": "Event 2"}
                ]
            },
            "causes_of_action": [
                {
                    "title": "VIOLATION OF THE FCRA",
                    "allegations": [
                        {"description": "Allegation 1"},
                        {"description": "Allegation 2"}
                    ]
                }
            ],
            "filing_details": {
                "date": "January 1, 2025"
            },
            "plaintiff_counsel": {
                "name": "John Doe",
                "firm": "Doe & Associates",
                "address": "123 Main St, New York, NY 10001",
                "phone": "555-555-5555",
                "email": "john.doe@example.com"
            }
        }
        html = html_engine.render_template("fcra/complaint.html", context)
        self.assertIn("UNITED STATES DISTRICT COURT", html)
        self.assertIn("Eman Youssef", html)
        self.assertIn("EQUIFAX INFORMATION SERVICES LLC", html)

    @patch("monkey.core.pdf_service.PdfService")
    def test_render_to_pdf(self, mock_pdf_service):
        """
        Tests that the PDF service can render a PDF.
        """
        pdf_service = mock_pdf_service()
        pdf_service.render_to_pdf.return_value = b"PDF"
        pdf = pdf_service.render_to_pdf("<html></html>")
        self.assertEqual(pdf, b"PDF")

if __name__ == "__main__":
    unittest.main()
