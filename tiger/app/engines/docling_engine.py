"""
Docling Engine for PDF Processing
High-performance OCR engine optimized for legal documents
"""

import sys
import subprocess
from typing import Dict, Any
try:
    from .base_engine import BaseEngine, ExtractionResult
except ImportError:
    from base_engine import BaseEngine, ExtractionResult

class DoclingEngine(BaseEngine):
    """Docling-based PDF processing engine"""
    
    def __init__(self):
        super().__init__("DoclingEngine")
        self.supported_formats = ['.pdf']
        self._docling_available = None
    
    def setup_dependencies(self) -> bool:
        """Install and setup Docling dependencies"""
        if self._docling_available is True:
            return True
        
        try:
            # Try to import docling
            import docling
            self._docling_available = True
            self.logger.info("Docling already available")
            return True
        except ImportError:
            pass
        
        # Docling not available - do not try to install at runtime
        self.logger.warning("Docling not available. Install with: pip install docling")
        self._docling_available = False
        return False
    
    def extract_text(self, file_path: str) -> ExtractionResult:
        """Extract text from PDF using Docling OCR"""
        # Ensure dependencies are available
        if not self.setup_dependencies():
            return ExtractionResult(
                success=False,
                error="Docling dependencies not available",
                engine_name=self.name
            )
        
        try:
            from docling.document_converter import DocumentConverter
            
            # Initialize converter
            converter = DocumentConverter()
            
            # Convert document
            result = converter.convert(file_path)
            
            # Extract text content
            text_content = result.document.export_to_markdown()
            
            # Prepare metadata
            metadata = {
                'page_count': len(result.document.pages) if hasattr(result.document, 'pages') else 1,
                'format': 'pdf',
                'extraction_method': 'docling_ocr'
            }
            
            # Extract additional document metadata if available
            if hasattr(result.document, 'metadata'):
                doc_metadata = result.document.metadata
                if doc_metadata:
                    metadata.update({
                        'title': getattr(doc_metadata, 'title', ''),
                        'author': getattr(doc_metadata, 'author', ''),
                        'creation_date': getattr(doc_metadata, 'creation_date', ''),
                        'modification_date': getattr(doc_metadata, 'modification_date', '')
                    })
            
            # Check if we got meaningful content
            if not text_content or len(text_content.strip()) < 10:
                return ExtractionResult(
                    success=False,
                    error="No meaningful text extracted from document",
                    engine_name=self.name,
                    metadata=metadata
                )
            
            return ExtractionResult(
                success=True,
                text=text_content,
                metadata=metadata,
                engine_name=self.name
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                error=f"Docling extraction failed: {str(e)}",
                engine_name=self.name
            )
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get detailed engine information"""
        info = super().get_engine_info()
        info.update({
            'description': 'Advanced OCR engine optimized for legal documents',
            'features': [
                'Multi-page PDF processing',
                'High-accuracy OCR for scanned documents', 
                'Legal document formatting preservation',
                'Markdown structured output',
                'Table and form extraction'
            ],
            'optimal_for': [
                'Court summons and legal filings',
                'Scanned legal documents',
                'Financial statements and reports',
                'Government forms and notices'
            ],
            'docling_available': self._docling_available
        })
        return info