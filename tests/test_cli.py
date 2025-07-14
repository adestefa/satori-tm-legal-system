"""
Tests for the CLI.
"""

import unittest
from unittest.mock import patch
from monkey.cli.enhanced_commands import MonkeyCommands

class TestCli(unittest.TestCase):
    """
    Tests for the CLI.
    """

    @patch("monkey.core.document_builder.BeaverDocumentBuilder")
    def test_build_complaint(self, mock_document_builder):
        """
        Tests that the build-complaint command works.
        """
        # Mock the document builder
        mock_builder = mock_document_builder.return_value
        mock_builder.build_complaint_package.return_value.success = True

        # Run the command
        cli = MonkeyCommands()
        cli.run(["build-complaint", "tests/fixtures/complaint.json", "--format", "html"])

        # Check that the document builder was called with the correct arguments
        mock_builder.build_complaint_package.assert_called_with(
            "tests/fixtures/complaint.json",
            document_types=["complaint"],
            format="html"
        )

    @patch("monkey.core.document_builder.BeaverDocumentBuilder")
    def test_build_complaint_pdf(self, mock_document_builder):
        """
        Tests that the build-complaint command works with the --format pdf option.
        """
        # Mock the document builder
        mock_builder = mock_document_builder.return_value
        mock_builder.build_complaint_package.return_value.success = True

        # Run the command
        cli = MonkeyCommands()
        cli.run(["build-complaint", "tests/fixtures/complaint.json", "--format", "pdf"])

        # Check that the document builder was called with the correct arguments
        mock_builder.build_complaint_package.assert_called_with(
            "tests/fixtures/complaint.json",
            document_types=["complaint"],
            format="pdf"
        )

if __name__ == "__main__":
    unittest.main()
