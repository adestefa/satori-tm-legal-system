"""
Document Processor - Main processing orchestrator for Satori Tiger service
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Use absolute imports
from app.config.settings import config
from app.engines.docling_engine import DoclingEngine
from app.engines.docx_engine import DocxEngine
from app.engines.text_engine import TextEngine
from app.engines.base_engine import BaseEngine
from app.core.validators import QualityValidator
from app.core.extractors.text_extractor import TextExtractor
from app.core.extractors.date_extractor import EnhancedDateExtractor
from app.core.event_broadcaster import ProcessingEventBroadcaster

logger = logging.getLogger(__name__)

class ProcessingResult:
    """Standardized result object for document processing"""
    
    def __init__(self, 
                 file_path: str,
                 success: bool = False,
                 extracted_text: str = "",
                 quality_metrics: Dict[str, Any] = None,
                 metadata: Dict[str, Any] = None,
                 processing_time: float = 0.0,
                 engine_used: str = "",
                 error: str = None,
                 extracted_dates: List[Dict[str, Any]] = None):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.success = success
        self.extracted_text = extracted_text
        self.quality_metrics = quality_metrics or {}
        self.metadata = metadata or {}
        self.processing_time = processing_time
        self.engine_used = engine_used
        self.error = error
        self.extracted_dates = extracted_dates or []
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'success': self.success,
            'extracted_text': self.extracted_text,
            'quality_metrics': self.quality_metrics,
            'metadata': self.metadata,
            'processing_time': self.processing_time,
            'engine_used': self.engine_used,
            'error': self.error,
            'extracted_dates': self.extracted_dates,
            'timestamp': self.timestamp
        }

class BatchProcessingResult:
    """Result object for batch processing operations"""
    
    def __init__(self):
        self.results: List[ProcessingResult] = []
        self.summary = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'warnings': 0,
            'total_processing_time': 0.0,
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        self.processing_errors: List[str] = []
    
    def add_result(self, result: ProcessingResult):
        """Add a processing result"""
        self.results.append(result)
        self.summary['total_files'] += 1
        self.summary['total_processing_time'] += result.processing_time
        
        if result.success:
            self.summary['successful'] += 1
            if result.quality_metrics.get('warnings', []):
                self.summary['warnings'] += 1
        else:
            self.summary['failed'] += 1
    
    def finalize(self):
        """Finalize batch processing"""
        self.summary['end_time'] = datetime.now().isoformat()
        self.summary['success_rate'] = (
            self.summary['successful'] / max(self.summary['total_files'], 1) * 100
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert batch result to dictionary"""
        return {
            'summary': self.summary,
            'results': [result.to_dict() for result in self.results],
            'processing_errors': self.processing_errors
        }

class DocumentProcessor:
    """Main document processing orchestrator"""
    
    def __init__(self, custom_config=None, event_broadcaster: ProcessingEventBroadcaster = None):
        self.config = custom_config or config
        self.logger = logging.getLogger(__name__)
        self.event_broadcaster = event_broadcaster
        
        # Initialize engines
        self.engines: Dict[str, BaseEngine] = {
            'pdf': DoclingEngine(),
            'docx': DocxEngine(),
            'txt': TextEngine()
        }
        
        # Initialize quality validator and extractors
        self.quality_validator = QualityValidator(self.config)
        self.text_extractor = TextExtractor()
        self.date_extractor = EnhancedDateExtractor()
        
        # Ensure data directories exist
        self.config.ensure_directories()
        
        # Setup engines
        self._setup_engines()
        
        # Case context for event broadcasting
        self.current_case_id = None
    
    def _setup_engines(self):
        """Setup all processing engines"""
        for engine_name, engine in self.engines.items():
            try:
                if engine.setup_dependencies():
                    self.logger.info(f"{engine_name} engine ready")
                else:
                    self.logger.warning(f"{engine_name} engine setup failed")
            except Exception as e:
                self.logger.error(f"Failed to setup {engine_name} engine: {e}")
    
    def set_case_context(self, case_id: str):
        """Set case context for event broadcasting"""
        self.current_case_id = case_id
    
    def get_engine_for_file(self, file_path: str) -> Optional[BaseEngine]:
        """Get appropriate engine for file type"""
        file_ext = Path(file_path).suffix.lower()
        
        for engine in self.engines.values():
            if engine.can_process(file_path):
                return engine
        
        return None
    
    def _determine_document_type(self, file_path: str) -> str:
        """Determine document type from filename for enhanced date extraction"""
        filename = os.path.basename(file_path).lower()
        
        # Common legal document type patterns
        if any(term in filename for term in ['denial', 'adverse_action', 'adverse-action']):
            return 'denial_letter'
        elif any(term in filename for term in ['dispute', 'challenge']):
            return 'dispute_correspondence'
        elif any(term in filename for term in ['notice', 'notification']):
            return 'notice_letter'
        elif any(term in filename for term in ['application', 'request']):
            return 'application_document'
        elif any(term in filename for term in ['summons', 'complaint']):
            return 'legal_filing'
        elif any(term in filename for term in ['statement', 'account']):
            return 'account_statement'
        elif any(term in filename for term in ['correspondence', 'letter']):
            return 'correspondence'
        else:
            return 'unknown'
    
    def process_document(self, file_path: str, output_dir: str = None) -> ProcessingResult:
        """Process a single document"""
        start_time = datetime.now()
        file_name = os.path.basename(file_path)
        
        # Broadcast file processing start
        if self.event_broadcaster and self.current_case_id:
            self.event_broadcaster.broadcast_file_start(self.current_case_id, file_name)
        
        # Validate file exists
        if not os.path.exists(file_path):
            error = "File not found"
            if self.event_broadcaster and self.current_case_id:
                self.event_broadcaster.broadcast_file_error(self.current_case_id, file_name, error)
            return ProcessingResult(
                file_path=file_path,
                success=False,
                error=error,
                processing_time=0.0
            )
        
        # Get appropriate engine
        engine = self.get_engine_for_file(file_path)
        if not engine:
            error = f"No engine available for file type: {Path(file_path).suffix}"
            if self.event_broadcaster and self.current_case_id:
                self.event_broadcaster.broadcast_file_error(self.current_case_id, file_name, error)
            return ProcessingResult(
                file_path=file_path,
                success=False,
                error=error,
                processing_time=0.0
            )
        
        try:
            # Extract text using engine
            extraction_result = engine.process_document(file_path)
            
            if not extraction_result.success:
                error = extraction_result.error
                if self.event_broadcaster and self.current_case_id:
                    self.event_broadcaster.broadcast_file_error(self.current_case_id, file_name, error)
                return ProcessingResult(
                    file_path=file_path,
                    success=False,
                    error=error,
                    engine_used=engine.name,
                    processing_time=extraction_result.processing_time
                )
            
            # Validate quality
            quality_metrics = self.quality_validator.validate_extraction(
                file_path, extraction_result.text
            )
            
            # Extract dates with enhanced date extractor
            document_type = self._determine_document_type(file_path)
            extracted_dates = self.date_extractor.extract_dates_from_text(
                extraction_result.text, document_type
            )
            
            # Convert dates to dictionaries for JSON serialization
            dates_data = [date.to_dict() for date in extracted_dates]
            
            # Calculate total processing time
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = ProcessingResult(
                file_path=file_path,
                success=True,
                extracted_text=extraction_result.text,
                quality_metrics=quality_metrics,
                metadata=extraction_result.metadata,
                processing_time=total_time,
                engine_used=engine.name,
                extracted_dates=dates_data
            )
            
            # Save outputs if output directory specified
            if output_dir:
                self._save_processing_outputs(result, output_dir)
            
            # Broadcast success
            if self.event_broadcaster and self.current_case_id:
                self.event_broadcaster.broadcast_file_success(
                    self.current_case_id, 
                    file_name, 
                    {
                        "quality_score": quality_metrics.get("quality_score", 0),
                        "text_length": len(extraction_result.text),
                        "engine_used": engine.name,
                        "processing_time": total_time,
                        "dates_extracted": len(dates_data)
                    }
                )
            
            self.logger.info(f"Successfully processed {file_path}")
            return result
            
        except Exception as e:
            error = str(e)
            if self.event_broadcaster and self.current_case_id:
                self.event_broadcaster.broadcast_file_error(self.current_case_id, file_name, error)
            self.logger.error(f"Failed to process {file_path}: {e}")
            return ProcessingResult(
                file_path=file_path,
                success=False,
                error=error,
                engine_used=engine.name if engine else "unknown",
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def process_directory(self, input_dir: str, output_dir: str = None) -> BatchProcessingResult:
        """Process all supported documents in a directory"""
        batch_result = BatchProcessingResult()
        
        if not os.path.exists(input_dir):
            batch_result.processing_errors.append("Input directory not found")
            batch_result.finalize()
            return batch_result
        
        # Find all supported files
        supported_files = []
        for ext in self.config.processing.supported_formats:
            supported_files.extend(Path(input_dir).rglob(f"*{ext}"))
        
        self.logger.info(f"Found {len(supported_files)} files to process")
        
        # Process each file
        for file_path in supported_files:
            try:
                result = self.process_document(str(file_path), output_dir)
                batch_result.add_result(result)
            except Exception as e:
                error_msg = f"Failed to process {file_path}: {e}"
                self.logger.error(error_msg)
                batch_result.processing_errors.append(error_msg)
                
                # Add failed result
                failed_result = ProcessingResult(
                    file_path=str(file_path),
                    success=False,
                    error=str(e)
                )
                batch_result.add_result(failed_result)
        
        batch_result.finalize()
        
        # Save batch summary if output directory specified
        if output_dir:
            self._save_batch_summary(batch_result, output_dir)
        
        return batch_result
    
    def _save_processing_outputs(self, result: ProcessingResult, output_dir: str):
        """Save processing outputs to files"""
        try:
            from app.output.handlers import OutputManager
        except ImportError:
            from output.handlers import OutputManager
        
        output_manager = OutputManager(self.config)
        if output_dir:
            output_manager.base_output_dir = Path(output_dir)
        output_manager.save_processing_result(result)
    
    def _save_batch_summary(self, batch_result: BatchProcessingResult, output_dir: str):
        """Save batch processing summary"""
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        
        summary_file = os.path.join(output_dir, "batch_processing_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(batch_result.to_dict(), f, indent=2, default=str)
        
        self.logger.info(f"Batch summary saved to {summary_file}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status"""
        engine_info = {}
        for name, engine in self.engines.items():
            engine_info[name] = engine.get_engine_info()
        
        return {
            'service_name': self.config.service_name,
            'version': self.config.version,
            'engines': engine_info,
            'supported_formats': self.config.processing.supported_formats,
            'quality_thresholds': self.config.quality.__dict__,
            'data_directories': {k: str(v) for k, v in self.config.get_data_dirs().items()}
        }