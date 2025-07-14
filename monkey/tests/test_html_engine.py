"""
Tests for the HtmlEngine.
"""
import unittest
from monkey.core.html_engine import HtmlEngine

class TestHtmlEngine(unittest.TestCase):

    def test_render_template(self):
        """
        Verify that the HtmlEngine can render a simple template.
        """
        engine = HtmlEngine()
        data = {"title": "Test Title", "name": "World"}
        rendered_html = engine.render_template("test_template.html", data)

        self.assertIn("<title>Test Title</title>", rendered_html)
        self.assertIn("<h1>Hello, World!</h1>", rendered_html)

if __name__ == '__main__':
    unittest.main()
