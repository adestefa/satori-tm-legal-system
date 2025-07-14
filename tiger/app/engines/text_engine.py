"""
Text Engine for Plain Text Document Processing
Handles .txt files with basic text extraction
"""

import logging
from pathlib import Path
from typing import Dict, Any
from .base_engine import BaseEngine, ExtractionResult

logger = logging.getLogger(__name__)

class TextEngine(BaseEngine):
    """Engine for processing plain text (.txt) files"""
    
    def __init__(self):
        super().__init__("TextEngine")
        self.supported_formats = ['.txt', '.md']
        
    def is_available(self) -> bool:
        """Text engine is always available"""
        return True
        
    def setup_dependencies(self) -> bool:
        """No setup required for text files"""
        logger.info("TextEngine initialized successfully")
        return True
        
    def extract_text(self, file_path: str) -> ExtractionResult:
        """
        Extract text from plain text file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            ExtractionResult with extracted text
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return ExtractionResult(success=True, text=text)
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            'name': self.name,
            'supported_formats': self.supported_formats,
            'description': 'Plain text file processor',
            'features': [
                'UTF-8 encoding support',
                'Latin-1 fallback encoding',
                'Line and character counting',
                'Fast processing'
            ],
            'dependencies': ['built-in'],
            'available': self.is_available()
        }