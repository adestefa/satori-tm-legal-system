"""
Output Formatters for Satori Tiger service
Different output formats for processed documents
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime

class BaseFormatter(ABC):
    """Base class for output formatters"""
    
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """Format data to string output"""
        pass
    
    @abstractmethod
    def get_extension(self) -> str:
        """Get file extension for this format"""
        pass

class TextFormatter(BaseFormatter):
    """Plain text formatter for extracted content"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format processing result as plain text"""
        lines = []
        
        # Header
        lines.append("SATORI TIGER DOCUMENT EXTRACTION")
        lines.append("=" * 50)
        lines.append(f"File: {data.get('file_name', 'Unknown')}")
        lines.append(f"Processed: {data.get('timestamp', 'Unknown')}")
        lines.append(f"Engine: {data.get('engine_used', 'Unknown')}")
        lines.append(f"Success: {data.get('success', False)}")
        lines.append("")
        
        # Quality metrics if available
        quality = data.get('quality_metrics', {})
        if quality:
            lines.append("QUALITY METRICS")
            lines.append("-" * 20)
            lines.append(f"Quality Score: {quality.get('quality_score', 0)}/100")
            lines.append(f"Text Length: {quality.get('text_length', 0)} characters")
            lines.append(f"Compression Ratio: {quality.get('compression_ratio', 0):.4f}")
            lines.append(f"Passes Threshold: {quality.get('passes_threshold', False)}")
            
            warnings = quality.get('warnings', [])
            if warnings:
                lines.append(f"Warnings: {len(warnings)}")
                for warning in warnings[:3]:  # Show first 3 warnings
                    lines.append(f"  - {warning}")
            lines.append("")
        
        # Extracted text
        if data.get('success', False) and data.get('extracted_text'):
            lines.append("EXTRACTED TEXT")
            lines.append("=" * 50)
            lines.append(data['extracted_text'])
        elif data.get('error'):
            lines.append("ERROR")
            lines.append("-" * 10)
            lines.append(data['error'])
        
        return '\n'.join(lines)
    
    def get_extension(self) -> str:
        return 'txt'

class JSONFormatter(BaseFormatter):
    """JSON formatter for structured data"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format processing result as JSON"""
        # Create a clean copy without circular references
        clean_data = {
            'satori_tiger_result': {
                'file_info': {
                    'file_path': data.get('file_path', ''),
                    'file_name': data.get('file_name', ''),
                    'processed_timestamp': data.get('timestamp', '')
                },
                'processing': {
                    'success': data.get('success', False),
                    'engine_used': data.get('engine_used', ''),
                    'processing_time': data.get('processing_time', 0.0),
                    'error': data.get('error', None)
                },
                'quality_metrics': data.get('quality_metrics', {}),
                'metadata': data.get('metadata', {}),
                'extracted_text': data.get('extracted_text', '') if data.get('success', False) else None,
                'extracted_dates': data.get('extracted_dates', [])
            }
        }
        
        return json.dumps(clean_data, indent=2, default=str)
    
    def get_extension(self) -> str:
        return 'json'

class MarkdownFormatter(BaseFormatter):
    """Markdown formatter for readable reports"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format processing result as Markdown"""
        lines = []
        
        # Header
        lines.append(f"# Document Processing Report")
        lines.append(f"**File:** {data.get('file_name', 'Unknown')}")
        lines.append(f"**Processed:** {data.get('timestamp', 'Unknown')}")
        lines.append(f"**Engine:** {data.get('engine_used', 'Unknown')}")
        lines.append(f"**Status:** {'✅ Success' if data.get('success', False) else '❌ Failed'}")
        lines.append("")
        
        # Quality Assessment
        quality = data.get('quality_metrics', {})
        if quality:
            lines.append("## Quality Assessment")
            lines.append("")
            
            score = quality.get('quality_score', 0)
            if score >= 80:
                score_emoji = "🟢"
            elif score >= 60:
                score_emoji = "🟡"
            else:
                score_emoji = "🔴"
            
            lines.append(f"**Quality Score:** {score_emoji} {score}/100")
            lines.append(f"**Text Length:** {quality.get('text_length', 0):,} characters")
            lines.append(f"**Compression Ratio:** {quality.get('compression_ratio', 0):.4f}")
            lines.append(f"**Quality Threshold:** {'✅ Passed' if quality.get('passes_threshold', False) else '⚠️ Review Needed'}")
            lines.append("")
            
            # Legal indicators
            legal_indicators = quality.get('legal_indicators', {})
            if legal_indicators:
                lines.append("### Legal Content Analysis")
                lines.append("")
                
                if legal_indicators.get('court_document', False):
                    lines.append("- ✅ Court document detected")
                if legal_indicators.get('case_number', False):
                    lines.append("- ✅ Case number found")
                if legal_indicators.get('summons', False):
                    lines.append("- ✅ Summons document")
                if legal_indicators.get('complaint', False):
                    lines.append("- ✅ Complaint document")
                
                # Counts
                entity_count = legal_indicators.get('legal_entities', {}).get('count', 0)
                address_count = legal_indicators.get('addresses', {}).get('count', 0)
                phone_count = legal_indicators.get('phone_numbers', {}).get('count', 0)
                
                if entity_count > 0:
                    lines.append(f"- 🏢 {entity_count} legal entities found")
                if address_count > 0:
                    lines.append(f"- 📍 {address_count} addresses found")
                if phone_count > 0:
                    lines.append(f"- 📞 {phone_count} phone numbers found")
                
                lines.append("")
            
            # Warnings
            warnings = quality.get('warnings', [])
            if warnings:
                lines.append("### Warnings")
                lines.append("")
                for warning in warnings:
                    if warning.startswith('CRITICAL'):
                        lines.append(f"- 🚨 {warning}")
                    elif warning.startswith('WARNING'):
                        lines.append(f"- ⚠️ {warning}")
                    else:
                        lines.append(f"- ℹ️ {warning}")
                lines.append("")
        
        # Processing details
        lines.append("## Processing Details")
        lines.append("")
        lines.append(f"**Processing Time:** {data.get('processing_time', 0.0):.2f} seconds")
        
        metadata = data.get('metadata', {})
        if metadata:
            lines.append("**Metadata:**")
            for key, value in metadata.items():
                if value:
                    lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        lines.append("")
        
        # Content preview or error
        if data.get('success', False) and data.get('extracted_text'):
            text = data['extracted_text']
            lines.append("## Extracted Content Preview")
            lines.append("")
            lines.append("```")
            # Show first 500 characters
            preview = text[:500] + "..." if len(text) > 500 else text
            lines.append(preview)
            lines.append("```")
        elif data.get('error'):
            lines.append("## Error Details")
            lines.append("")
            lines.append(f"```")
            lines.append(data['error'])
            lines.append("```")
        
        lines.append("")
        lines.append("---")
        lines.append("*Generated by Satori Tiger Document Processing Service*")
        
        return '\n'.join(lines)
    
    def get_extension(self) -> str:
        return 'md'

class HTMLFormatter(BaseFormatter):
    """HTML formatter for web-friendly reports"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """Format processing result as HTML"""
        # Convert markdown to basic HTML
        markdown_content = MarkdownFormatter().format(data)
        
        # Simple markdown to HTML conversion
        html_content = markdown_content.replace('\n', '<br>\n')
        html_content = html_content.replace('# ', '<h1>').replace('<br>\n<h1>', '</h1>\n<h1>')
        html_content = html_content.replace('## ', '<h2>').replace('<br>\n<h2>', '</h2>\n<h2>')
        html_content = html_content.replace('### ', '<h3>').replace('<br>\n<h3>', '</h3>\n<h3>')
        html_content = html_content.replace('**', '<strong>').replace('</strong>', '</strong>')
        html_content = html_content.replace('```', '<pre><code>').replace('</code>', '</code></pre>')
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Satori Tiger Document Report - {data.get('file_name', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 1px solid #ecf0f1; }}
        .success {{ color: #27ae60; }}
        .error {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
    
    def get_extension(self) -> str:
        return 'html'