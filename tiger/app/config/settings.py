"""
Satori Tiger Configuration Management
Centralized configuration for the document parsing service
"""

import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class QualityThresholds:
    """Quality validation thresholds"""
    min_text_length: int = 100
    compression_ratio_min: float = 0.001
    compression_ratio_max: float = 0.1
    min_quality_score: int = 50
    high_quality_threshold: int = 80

@dataclass
class ProcessingConfig:
    """Processing configuration"""
    supported_formats: list = None
    max_file_size_mb: int = 100
    processing_timeout_seconds: int = 300
    batch_size: int = 10
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.pdf', '.docx']

@dataclass
class OutputConfig:
    """Output configuration"""
    base_output_dir: str = "data/output"
    create_subdirs: bool = True
    save_metadata: bool = True
    save_extracted_text: bool = True
    save_quality_report: bool = True
    output_formats: list = None
    
    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ['txt', 'json', 'md']

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    log_dir: str = "data/logs"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_log_size_mb: int = 10
    backup_count: int = 5

class SatoriConfig:
    """Main configuration class for Satori Tiger service"""
    
    def __init__(self, config_file: str = None):
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_file = config_file
        
        # Core configurations
        self.quality = QualityThresholds()
        self.processing = ProcessingConfig()
        self.output = OutputConfig()
        self.logging = LoggingConfig()
        
        # Service metadata
        self.service_name = "Satori Tiger Document Parser"
        self.version = "1.9.0"
        self.author = "Satori Development Team"
        
        # Load custom config if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Environment variable overrides
        self.load_from_env()
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON/YAML file"""
        import json
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update configurations from file
            for section, values in config_data.items():
                if hasattr(self, section):
                    config_obj = getattr(self, section)
                    for key, value in values.items():
                        if hasattr(config_obj, key):
                            setattr(config_obj, key, value)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'SATORI_MIN_TEXT_LENGTH': ('quality', 'min_text_length', int),
            'SATORI_MIN_QUALITY_SCORE': ('quality', 'min_quality_score', int),
            'SATORI_OUTPUT_DIR': ('output', 'base_output_dir', str),
            'SATORI_LOG_LEVEL': ('logging', 'level', str),
            'SATORI_MAX_FILE_SIZE': ('processing', 'max_file_size_mb', int),
            'SATORI_PROCESSING_TIMEOUT': ('processing', 'processing_timeout_seconds', int),
        }
        
        for env_var, (section, attr, type_func) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = type_func(os.environ[env_var])
                    setattr(getattr(self, section), attr, value)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid value for {env_var}")
    
    def get_data_dirs(self) -> Dict[str, Path]:
        """Get standardized data directory paths"""
        base = self.base_dir / "data"
        return {
            'input': base / "input",
            'output': base / "output", 
            'temp': base / "temp",
            'logs': base / "logs",
            'processed': base / "output" / "processed",
            'failed': base / "output" / "failed",
            'reports': base / "output" / "reports"
        }
    
    def ensure_directories(self):
        """Create necessary directories"""
        dirs = self.get_data_dirs()
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'service_name': self.service_name,
            'version': self.version,
            'quality': self.quality.__dict__,
            'processing': self.processing.__dict__,
            'output': self.output.__dict__,
            'logging': self.logging.__dict__
        }
    
    def save_config(self, output_file: str):
        """Save current configuration to file"""
        import json
        with open(output_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

# Global configuration instance
config = SatoriConfig()