#!/usr/bin/env python3
"""
Banana Template Generator

A scaffolding tool to auto-generate a Jinja2 HTML template from a Pydantic schema
and a corresponding JSON data file.
"""

import argparse
import json
import importlib.util
import sys
from pathlib import Path
from pydantic import BaseModel
from typing import Any, List, Dict, get_origin, get_args

# Ensure the project root is in the path to allow for module imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_schema_class(file_path: str, class_name: str) -> Any:
    """Dynamically loads a Pydantic model class from a Python file."""
    module_name = Path(file_path).stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not load spec for module {module_name} from {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

def generate_html_for_model(model_class: Any, data: Dict[str, Any], prefix: str = "") -> str:
    """Recursively generates HTML for a Pydantic model and its data."""
    html_parts = []
    
    for field_name, field_info in model_class.model_fields.items():
        field_value = data.get(field_name)
        jinja_variable = f"{prefix}{field_name}" if prefix else field_name
        field_title = field_name.replace('_', ' ').title()

        if field_value is None:
            continue

        # Check for nested Pydantic models
        field_type = field_info.annotation
        origin_type = get_origin(field_type)
        
        if hasattr(field_type, 'model_fields'): # Nested BaseModel
            html_parts.append(f"<div class='nested-object'>")
            html_parts.append(f"    <h3>{field_title}</h3>")
            html_parts.append(generate_html_for_model(field_type, field_value, prefix=f"{jinja_variable}."))
            html_parts.append(f"</div>")
        elif origin_type is list and hasattr(get_args(field_type)[0], 'model_fields'): # List of BaseModels
            item_model_class = get_args(field_type)[0]
            item_variable = f"{field_name[:-1]}" if field_name.endswith('s') else 'item'
            
            html_parts.append(f"<div class='list-object'>")
            html_parts.append(f"    <h3>{field_title}</h3>")
            html_parts.append(f"    {{% for {item_variable} in {jinja_variable} %}}")
            html_parts.append(f"    <div class='list-item'>")
            html_parts.append(generate_html_for_model(item_model_class, field_value[0], prefix=f"{item_variable}."))
            html_parts.append(f"    </div>")
            html_parts.append(f"    {{% endfor %}}")
            html_parts.append(f"</div>")
        elif origin_type is list: # List of simple types
            html_parts.append(f"<div class='simple-list'>")
            html_parts.append(f"    <h4>{field_title}</h4>")
            html_parts.append(f"    <ul>")
            html_parts.append(f"        {{% for item in {jinja_variable} %}}")
            html_parts.append(f"        <li>{{{{ item }}}}</li>")
            html_parts.append(f"        {{% endfor %}}")
            html_parts.append(f"    </ul>")
            html_parts.append(f"</div>")
        else: # Simple field
            html_parts.append(f"<p><strong>{field_title}:</strong> {{{{ {jinja_variable} }}}}</p>")

    return "\n".join(html_parts)

def create_final_html(content: str, title: str) -> str:
    """Wraps the generated content in a full HTML document with styles."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} Template</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        h1 {{ font-size: 2em; }}
        h2 {{ font-size: 1.75em; }}
        h3 {{ font-size: 1.5em; }}
        h4 {{ font-size: 1.25em; }}
        .container {{
            background-color: #ffffff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .nested-object, .list-object, .simple-list {{
            border-left: 3px solid #3498db;
            padding-left: 20px;
            margin-top: 20px;
            margin-bottom: 20px;
        }}
        .list-item {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #fdfdfd;
        }}
        p {{ margin: 10px 0; }}
        strong {{ color: #2980b9; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{{{{ {title.lower().replace(' ', '_')}.document_title or "{title}" }}}}</h1>
        {content}
    </div>
</body>
</html>
"""

def main():
    """Main function to generate the template."""
    parser = argparse.ArgumentParser(description="Generate a Jinja2 HTML template from a Pydantic schema.")
    parser.add_argument("--schema-file", required=True, help="Path to the Python schema file.")
    parser.add_argument("--schema-class", required=True, help="Name of the Pydantic class in the schema file.")
    parser.add_argument("--json-file", required=True, help="Path to the hydrated JSON data file.")
    parser.add_argument("--output-file", required=True, help="Path to save the generated HTML template.")
    
    args = parser.parse_args()

    try:
        print(f"🍌 Loading schema class '{args.schema_class}' from '{args.schema_file}'...")
        schema_class = load_schema_class(args.schema_file, args.schema_class)
        
        print(f"🍌 Loading and validating JSON data from '{args.json_file}'...")
        with open(args.json_file, 'r') as f:
            json_data = json.load(f)
        
        # Validate data against the schema
        validated_data = schema_class(**json_data)
        
        print("🍌 Generating HTML content...")
        generated_content = generate_html_for_model(schema_class, validated_data.model_dump())
        
        print("🍌 Creating final HTML document...")
        final_html = create_final_html(generated_content, args.schema_class)
        
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(final_html)
            
        print(f"✅ Successfully generated template at: {output_path}")

    except Exception as e:
        print(f"❌ An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
