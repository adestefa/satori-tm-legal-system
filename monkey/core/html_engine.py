"""
HTML Engine for rendering Jinja2 templates.
"""
import jinja2
from pathlib import Path

class HtmlEngine:
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            # Default to the 'templates/html' directory within the monkey service
            template_dir = Path(__file__).parent.parent / 'templates'
        
        self.template_dir = template_dir
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        self._add_custom_filters()

    def render_template(self, template_name: str, data: dict) -> str:
        """
        Renders a Jinja2 template with the given data.
        """
        template = self.env.get_template(template_name)
        return template.render(data)

    def list_templates(self, pattern: str = None) -> list:
        """
        Lists available templates.
        """
        templates = self.env.list_templates()
        if pattern:
            return [t for t in templates if pattern in t]
        return templates

    def get_template_info(self, template_name: str) -> dict:
        """
        Gets information about a template.
        """
        try:
            source, filename, uptodate = self.env.loader.get_source(self.env, template_name)
            return {
                'name': template_name,
                'path': filename,
                'size': Path(filename).stat().st_size,
                'valid': True,
                'error': None
            }
        except jinja2.TemplateNotFound:
            return {
                'name': template_name,
                'path': None,
                'size': None,
                'valid': False,
                'error': 'Template not found'
            }
        except Exception as e:
            return {
                'name': template_name,
                'path': None,
                'size': None,
                'valid': False,
                'error': str(e)
            }

    def validate_template(self, template_name: str) -> bool:
        """
        Validates a template.
        """
        try:
            self.env.get_template(template_name)
            return True
        except jinja2.TemplateNotFound:
            return False

    def _add_custom_filters(self):
        """
        Adds custom filters to the Jinja2 environment.
        """
        # Placeholder for custom filters like sequential_numbering
        pass