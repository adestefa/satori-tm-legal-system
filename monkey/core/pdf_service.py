"""
PDF Service for converting HTML to PDF using a headless Chrome instance.
"""
import asyncio
import json
import aiohttp
from typing import Optional

class PdfService:
    def __init__(self, chrome_url: str = "http://localhost:9222"):
        """
        Initializes the PdfService.

        Args:
            chrome_url: The URL of the headless Chrome instance's DevTools endpoint.
        """
        self.chrome_url = chrome_url
        self.browser_ws_url = None

    async def _get_browser_ws_url(self) -> str:
        """
        Gets the WebSocket URL for the browser from the Chrome DevTools endpoint.
        """
        if self.browser_ws_url:
            return self.browser_ws_url

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.chrome_url}/json/version") as resp:
                resp.raise_for_status()
                version_info = await resp.json()
                self.browser_ws_url = version_info["webSocketDebuggerUrl"]
                return self.browser_ws_url

    async def render_to_pdf(self, html_content: str, options: Optional[dict] = None) -> bytes:
        """
        Renders the given HTML content to a PDF.

        Args:
            html_content: The HTML content to render.
            options: PDF print options for the Chrome DevTools Protocol.

        Returns:
            The PDF content as bytes.
        """
        browser_ws_url = await self._get_browser_ws_url()
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(browser_ws_url, max_msg_size=0) as ws:
                # Create a new browser context
                await ws.send_json({"id": 1, "method": "Target.createBrowserContext"})
                response = await ws.receive_json()
                browser_context_id = response["result"]["browserContextId"]

                # Create a new page in the context
                await ws.send_json({"id": 2, "method": "Target.createTarget", "params": {"url": "about:blank", "browserContextId": browser_context_id}})
                response = await ws.receive_json()
                target_id = response["result"]["targetId"]

                # Attach to the new page
                await ws.send_json({"id": 3, "method": "Target.attachToTarget", "params": {"targetId": target_id, "flatten": True}})
                response = await ws.receive_json()
                session_id = response["result"]["sessionId"]

                # Send a command to the page's session
                async def send_command(method, params):
                    command_id = id(method)
                    await ws.send_json({"sessionId": session_id, "id": command_id, "method": method, "params": params})
                    # Wait for the result, but don't block forever
                    # This part might need to be more robust in a real implementation
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            msg_data = json.loads(msg.data)
                            if msg_data.get("id") == command_id:
                                return msg_data.get("result")
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
                    return None


                # Enable the page
                await send_command("Page.enable", {})
                
                # Set the HTML content
                await send_command("Page.setDocumentContent", {"frameId": target_id, "html": html_content})

                # Print to PDF
                print_options = {
                    'printBackground': True,
                    'marginTop': 0.5,
                    'marginBottom': 0.5,
                    'marginLeft': 0.5,
                    'marginRight': 0.5,
                }
                if options:
                    print_options.update(options)
                
                pdf_data = await send_command("Page.printToPDF", print_options)
                
                # Close the target and context
                await send_command("Target.closeTarget", {"targetId": target_id})
                await send_command("Target.disposeBrowserContext", {"browserContextId": browser_context_id})

                if pdf_data and 'data' in pdf_data:
                    import base64
                    return base64.b64decode(pdf_data['data'])
                else:
                    raise Exception("Failed to generate PDF: No data received from Chrome.")
