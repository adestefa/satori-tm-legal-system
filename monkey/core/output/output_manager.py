"""
Satori Beaver Output Manager
Handles the creation and organization of output files and directories.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

from .version_manager import VersionManager

class OutputManager:
    """Manages the saving of generated documents and metadata."""

    def __init__(self, base_output_dir: str, use_versioned_subdirs: bool = True):
        """
        Initialize the OutputManager.

        Args:
            base_output_dir (str): The root directory for all outputs.
            use_versioned_subdirs (bool): If True, create a unique versioned 
                                          subdirectory for each package.
        """
        self.base_output_dir = Path(base_output_dir)
        self.use_versioned_subdirs = use_versioned_subdirs
        self.version_manager = VersionManager(scheme='timestamp')
        
        self.package_dir = self.base_output_dir
        if self.use_versioned_subdirs:
            # Create a unique directory for this generation run
            dir_name = self.version_manager.get_versioned_directory('package')
            self.package_dir = self.base_output_dir / dir_name
        
        self.package_dir.mkdir(parents=True, exist_ok=True)

    def save_document(self, content: str, basename: str, extension: str) -> Path:
        """
        Saves a single document to the package directory.

        Args:
            content (str): The content of the document.
            basename (str): The base name for the file (e.g., 'complaint').
            extension (str): The file extension (e.g., 'txt', 'docx').

        Returns:
            Path: The path to the saved file.
        """
        # Note: The VersionManager is not used here to keep filenames predictable
        # within a versioned package directory. Versioning is at the directory level.
        file_path = self.package_dir / f"{basename}.{extension}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return file_path

    def save_metadata(self, metadata: Dict[str, Any], basename: str = 'package_metadata') -> Path:
        """
        Saves the package metadata to a JSON file.

        Args:
            metadata (Dict[str, Any]): The metadata dictionary.
            basename (str): The base name for the metadata file.

        Returns:
            Path: The path to the saved metadata file.
        """
        file_path = self.package_dir / f"{basename}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
        return file_path

    def get_package_directory(self) -> Path:
        """
        Returns the path to the current package directory.
        """
        return self.package_dir

