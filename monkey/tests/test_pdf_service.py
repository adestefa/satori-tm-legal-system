
"""
Tests for the PdfService.
"""
import asyncio
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import base64

from monkey.core.pdf_service import PdfService

class TestPdfService(unittest.TestCase):

    @patch('aiohttp.ClientSession')
    def test_render_to_pdf_mocked(self, MockClientSession):
        """
        Verify that the PdfService can render HTML to PDF using a mocked
        Chrome DevTools Protocol connection.
        """
        # Mock the response from the /json/version endpoint
        mock_ws_url = "ws://localhost:9222/devtools/browser/123"
        mock_version_response = AsyncMock()
        mock_version_response.json.return_value = {"webSocketDebuggerUrl": mock_ws_url}
        
        # Mock the websocket connection
        mock_ws = AsyncMock()
        
        # Create a sample PDF in base64
        pdf_content = b"%PDF-1.4\n..."
        b64_pdf_content = base64.b64encode(pdf_content).decode('utf-8')

        # Set up the sequence of responses from the websocket
        mock_ws.receive_json.side_effect = [
            {"result": {"browserContextId": "abc"}},  # createBrowserContext
            {"result": {"targetId": "def"}},          # createTarget
            {"result": {"sessionId": "ghi"}},         # attachToTarget
            {"result": {}},                           # Page.enable
            {"result": {}},                           # Page.setDocumentContent
            {"result": {"data": b64_pdf_content}},    # Page.printToPDF
            {"result": {}},                           # Target.closeTarget
            {"result": {}},                           # Target.disposeBrowserContext
        ]

        # Set up the context managers
        mock_session_instance = MockClientSession.return_value.__aenter__.return_value
        mock_session_instance.get.return_value.__aenter__.return_value = mock_version_response
        mock_session_instance.ws_connect.return_value.__aenter__.return_value = mock_ws

        # Run the test
        service = PdfService()
        html_content = "<h1>Hello</h1>"
        
        async def run():
            return await service.render_to_pdf(html_content)

        result_pdf = asyncio.run(run())

        self.assertEqual(result_pdf, pdf_content)
        # Verify that ws_connect was called with the correct URL
        mock_session_instance.__aenter__.return_value.ws_connect.assert_called_with(mock_ws_url, max_msg_size=0)


if __name__ == '__main__':
    unittest.main()
