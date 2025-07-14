"""
Beaver Document Builder
Main orchestrator for generating legal documents from Tiger's complaint.json
"""

import json
import logging
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from .validators import DocumentValidator
from .output_manager import OutputManager
from .html_engine import HtmlEngine
from .pdf_service import PdfService
from .quality_validator import QualityValidator

logger = logging.getLogger(__name__)

@dataclass
class DocumentPackage:
    """Container for generated legal documents"""
    complaint: str
    complaint_pdf: Optional[str] = None
    summons: Optional[str] = None
    cover_sheet: Optional[str] = None
    exhibits: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'complaint': self.complaint,
            'complaint_pdf': self.complaint_pdf,
            'summons': self.summons,
            'cover_sheet': self.cover_sheet,
            'exhibits': self.exhibits or [],
            'metadata': self.metadata or {}
        }

@dataclass
class GenerationResult:
    """Result of document generation"""
    success: bool
    package: Optional[DocumentPackage] = None
    errors: List[str] = None
    warnings: List[str] = None
    generation_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class MonkeyDocumentBuilder:
    """Main document builder for generating legal documents"""
    
    def __init__(self, template_dir: str = None, output_manager: OutputManager = None, html_engine: HtmlEngine = None, pdf_service: PdfService = None, quality_validator: QualityValidator = None):
        """
        Initialize document builder
        
        Args:
            template_dir: Path to template directory
            output_manager: Instance of OutputManager
            html_engine: Instance of HtmlEngine
            pdf_service: Instance of PdfService
            quality_validator: Instance of QualityValidator
        """
        self.validator = DocumentValidator()
        self.output_manager = output_manager or OutputManager()
        self.html_engine = html_engine or HtmlEngine()
        self.pdf_service = pdf_service or PdfService()
        self.quality_validator = quality_validator or QualityValidator()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Monkey Document Builder initialized")
        
        # Check for browser PDF service availability
        self.browser_pdf_available = self._check_browser_pdf_service()
    
    def _check_browser_pdf_service(self) -> bool:
        """Check if browser PDF service is available"""
        try:
            browser_service_path = Path(__file__).parent.parent.parent / "browser" / "print.py"
            return browser_service_path.exists()
        except Exception:
            return False
    
    def _generate_pdf_from_html(self, html_file_path: str) -> Optional[str]:
        """Generate PDF from HTML file using browser service"""
        if not self.browser_pdf_available:
            self.logger.warning("Browser PDF service not available")
            return None
            
        try:
            browser_service_path = Path(__file__).parent.parent.parent / "browser" / "print.py"
            pdf_file_path = html_file_path.replace('.html', '.pdf')
            
            # Call browser PDF service
            result = subprocess.run([
                sys.executable, str(browser_service_path), 'single', html_file_path, pdf_file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and Path(pdf_file_path).exists():
                self.logger.info(f"PDF generated successfully: {pdf_file_path}")
                return pdf_file_path
            else:
                self.logger.error(f"PDF generation failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("PDF generation timed out")
            return None
        except Exception as e:
            self.logger.error(f"PDF generation error: {str(e)}")
            return None
    
    def build_complaint_package(self, complaint_json: Union[str, Dict[str, Any]], 
                              document_types: List[str] = None,
                              format: str = 'html',
                              template_override: Optional[str] = None,
                              with_pdf: bool = False) -> GenerationResult:
        """
        Build complete document package from complaint JSON
        
        Args:
            complaint_json: Either JSON string or parsed dict from Tiger
            document_types: List of document types to generate ['complaint', 'summons', 'cover_sheet']
            format: The output format ('html' or 'pdf')
            template_override: Custom template to use
            with_pdf: Generate PDF version of complaint using browser service
            
        Returns:
            GenerationResult with document package or errors
        """
        start_time = datetime.now()
        
        try:
            # Parse input if string
            if isinstance(complaint_json, str):
                if Path(complaint_json).exists():
                    # It's a file path
                    with open(complaint_json, 'r') as f:
                        data = json.load(f)
                else:
                    # It's JSON string
                    data = json.loads(complaint_json)
            else:
                data = complaint_json.copy()
            
            self.logger.info(f"Building document package for case: {data.get('tiger_metadata', {}).get('case_id', 'Unknown')}")
            
            # Validate input data
            validation_result = self.validator.validate_complaint_data(data)
            if not validation_result.is_valid:
                return GenerationResult(
                    success=False,
                    errors=[f"Validation failed: {error}" for error in validation_result.errors],
                    generation_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Default document types
            if document_types is None:
                document_types = ['complaint']
            
            # Generate documents
            package = DocumentPackage(complaint="")
            warnings = []
            
            # Generate complaint (required)
            if 'complaint' in document_types:
                complaint_result = self._generate_complaint(data, format, template_override)
                if complaint_result.success:
                    package.complaint = complaint_result.content
                    
                    # Generate PDF if requested and HTML was generated
                    if with_pdf and format == 'html' and hasattr(complaint_result, 'file_path'):
                        pdf_path = self._generate_pdf_from_html(complaint_result.file_path)
                        if pdf_path:
                            package.complaint_pdf = pdf_path
                            self.logger.info("Complaint PDF generated successfully")
                        else:
                            warnings.append("PDF generation failed - HTML document available for manual printing")
                else:
                    return GenerationResult(
                        success=False,
                        errors=complaint_result.errors,
                        generation_time=(datetime.now() - start_time).total_seconds()
                    )
            
            # Generate summons (optional)
            if 'summons' in document_types:
                summons_result = self._generate_summons(data, format)
                if summons_result.success:
                    package.summons = summons_result.content
                else:
                    warnings.extend([f"Summons generation failed: {error}" for error in summons_result.errors])
            
            # Generate cover sheet (optional)
            if 'cover_sheet' in document_types:
                cover_result = self._generate_cover_sheet(data, format)
                if cover_result.success:
                    package.cover_sheet = cover_result.content
                else:
                    warnings.extend([f"Cover sheet generation failed: {error}" for error in cover_result.errors])
            
            # Add metadata
            package.metadata = self._generate_metadata(data, document_types)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Document package generated successfully in {generation_time:.2f} seconds")
            
            return GenerationResult(
                success=True,
                package=package,
                warnings=warnings,
                generation_time=generation_time
            )
            
        except Exception as e:
            self.logger.error(f"Error building document package: {e}")
            return GenerationResult(
                success=False,
                errors=[f"Document generation failed: {str(e)}"],
                generation_time=(datetime.now() - start_time).total_seconds()
            )

    def _generate_complaint(self, data: Dict[str, Any], format: str, template_override: Optional[str] = None) -> 'DocumentGenerationResult':
        """Generate FCRA complaint document"""
        try:
            # Determine case type and template
            if template_override:
                template_name = template_override
            else:
                template_name = self._get_complaint_template(data)
            
            self.logger.info(f"Rendering template: {template_name}")
            # Prepare template variables
            template_vars = self._prepare_template_variables(data)
            self.logger.info(f"Template variables: {json.dumps(template_vars, indent=2)}")
            
            # Render template
            html = self.html_engine.render_template(template_name, template_vars)
            
            file_path = None
            
            if format == 'pdf':
                content = asyncio.run(self.pdf_service.render_to_pdf(html))
            else:
                content = html
                
                # Save HTML content to file for browser service integration
                case_id = data.get('tiger_metadata', {}).get('case_id', 'unknown')
                output_dir = Path(self.output_manager.base_path) / "html_temp"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = output_dir / f"complaint_{case_id}.html"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                self.logger.info(f"HTML file saved for browser service: {file_path}")

            return DocumentGenerationResult(success=True, content=content, file_path=str(file_path) if file_path else None)
            
        except Exception as e:
            self.logger.error(f"Error generating complaint: {e}")
            return DocumentGenerationResult(success=False, errors=[str(e)])
    
    def _generate_summons(self, data: Dict[str, Any], format: str) -> 'DocumentGenerationResult':
        """Generate summons document"""
        try:
            template_name = "fcra/summons.jinja2"
            template_vars = self._prepare_template_variables(data)
            
            html = self.html_engine.render_template(template_name, template_vars)

            if format == 'pdf':
                content = asyncio.run(self.pdf_service.render_to_pdf(html))
            else:
                content = html

            return DocumentGenerationResult(success=True, content=content)
            
        except Exception as e:
            self.logger.error(f"Error generating summons: {e}")
            return DocumentGenerationResult(success=False, errors=[str(e)])
    
    def _generate_cover_sheet(self, data: Dict[str, Any], format: str) -> 'DocumentGenerationResult':
        """Generate civil cover sheet"""
        try:
            template_name = "fcra/cover_sheet.jinja2"
            template_vars = self._prepare_template_variables(data)
            
            html = self.html_engine.render_template(template_name, template_vars)

            if format == 'pdf':
                content = asyncio.run(self.pdf_service.render_to_pdf(html))
            else:
                content = html

            return DocumentGenerationResult(success=True, content=content)
            
        except Exception as e:
            self.logger.error(f"Error generating cover sheet: {e}")
            return DocumentGenerationResult(success=False, errors=[str(e)])
    
    def _get_complaint_template(self, data: Dict[str, Any]) -> str:
        """Determine which complaint template to use"""
        doc_type = data.get("case_information", {}).get("document_type", "FCRA").lower()
        return f"html/{doc_type}/complaint.html"
    
    def _prepare_template_variables(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare variables for template rendering from hydrated JSON"""
        return {'hydratedjson': data}
    
    def _post_process_complaint(self, content: str, data: Dict[str, Any]) -> str:
        """Post-process complaint content for formatting and cleanup"""
        
        # Clean up extra whitespace and line breaks
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            cleaned_lines.append(line)
        
        # Join lines and normalize spacing
        content = '\n'.join(cleaned_lines)
        
        # Remove excessive blank lines (more than 2 consecutive)
        import re
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _generate_metadata(self, data: Dict[str, Any], document_types: List[str]) -> Dict[str, Any]:
        """Generate metadata for document package"""
        
        tiger_metadata = data.get('tiger_metadata', {})
        
        metadata = {
            'generation_timestamp': datetime.now().isoformat(),
            'beaver_version': '1.1.2',
            'document_types': document_types,
            'source_case_id': tiger_metadata.get('case_id'),
            'source_confidence': tiger_metadata.get('extraction_confidence'),
            'source_documents': tiger_metadata.get('source_documents', []),
            'case_information': {
                'case_number': data.get('case_information', {}).get('case_number'),
                'court_district': data.get('case_information', {}).get('court_district'),
                'plaintiff_name': data.get('plaintiff', {}).get('name'),
                'defendant_count': len(data.get('defendants', []))
            }
        }
        
        return metadata
    
    def preview_complaint(self, complaint_json: Union[str, Dict[str, Any]], 
                         lines: int = 50) -> str:
        """
        Generate preview of complaint document
        
        Args:
            complaint_json: Complaint data
            lines: Number of lines to include in preview
            
        Returns:
            Preview text
        """
        try:
            result = self.build_complaint_package(complaint_json, ['complaint'])
            
            if not result.success:
                return f"Error generating preview: {'; '.join(result.errors)}"
            
            content_lines = result.package.complaint.split('\n')
            preview_lines = content_lines[:lines]
            
            preview = '\n'.join(preview_lines)
            
            if len(content_lines) > lines:
                preview += f"\n\n... [Preview truncated. Full document has {len(content_lines)} lines]"
            
            return preview
            
        except Exception as e:
            return f"Error generating preview: {str(e)}"

@dataclass
class DocumentGenerationResult:
    """Result of individual document generation"""
    success: bool
    content: str = ""
    file_path: Optional[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []