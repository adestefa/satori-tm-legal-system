"""
Base Engine for Document Processing
Abstract base class for all document processing engines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)

class ExtractionResult:
    """Standardized result object for document extraction"""
    
    def __init__(self, 
                 success: bool,
                 text: str = "",
                 metadata: Dict[str, Any] = None,
                 processing_time: float = 0.0,
                 engine_name: str = "",
                 error: str = None,
                 file_path: str = "",
                 confidence: float = 0.0,
                 legal_entities: List[Any] = None):
        self.success = success
        self.text = text
        self.metadata = metadata or {}
        self.processing_time = processing_time
        self.engine_name = engine_name
        self.error = error
        self.text_length = len(text) if text else 0
        self.file_path = file_path
        self.confidence = confidence
        self.legal_entities = legal_entities or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'text': self.text,
            'text_length': self.text_length,
            'metadata': self.metadata,
            'processing_time': self.processing_time,
            'engine_name': self.engine_name,
            'error': self.error
        }

class BaseEngine(ABC):
    """Abstract base class for document processing engines"""
    
    def __init__(self, name: str):
        self.name = name
        self.supported_formats: List[str] = []
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    @abstractmethod
    def extract_text(self, file_path: str) -> ExtractionResult:
        """Extract text from document - must be implemented by subclasses"""
        pass
    
    def can_process(self, file_path: str) -> bool:
        """Check if this engine can process the given file"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats
    
    def validate_file(self, file_path: str) -> tuple[bool, str]:
        """Validate file before processing"""
        if not Path(file_path).exists():
            return False, "File does not exist"
        
        if not self.can_process(file_path):
            return False, f"Unsupported format. Supported: {self.supported_formats}"
        
        # Check file size (100MB default limit)
        file_size = Path(file_path).stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            return False, f"File too large: {file_size / 1024 / 1024:.1f}MB > {max_size / 1024 / 1024}MB"
        
        return True, ""
    
    def process_document(self, file_path: str) -> ExtractionResult:
        """Main processing method with validation and timing"""
        start_time = time.time()
        
        # Validate file
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            return ExtractionResult(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time,
                engine_name=self.name
            )
        
        self.logger.info(f"Processing {file_path} with {self.name}")
        self.logger.info(f"File validation successful: {is_valid}")
        
        try:
            # Extract text using engine-specific implementation
            result = self.extract_text(file_path)
            result.processing_time = time.time() - start_time
            result.engine_name = self.name
            
            self.logger.info(f"Successfully processed {file_path} - {result.text_length} characters extracted")
            self.logger.info(f"Extraction result: {result.to_dict()}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process {file_path}: {str(e)}", exc_info=True)
            return ExtractionResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time,
                engine_name=self.name
            )
    
    @abstractmethod
    def setup_dependencies(self) -> bool:
        """Setup engine dependencies - must be implemented by subclasses"""
        pass
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            'name': self.name,
            'supported_formats': self.supported_formats,
            'class': self.__class__.__name__
        }