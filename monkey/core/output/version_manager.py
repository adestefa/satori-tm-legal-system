"""
Satori Beaver Version Manager
Handles versioning of output files.
"""

from datetime import datetime

class VersionManager:
    """Manages file versioning schemes."""

    def __init__(self, scheme: str = 'timestamp'):
        """
        Initialize the VersionManager.

        Args:
            scheme (str): The versioning scheme to use. 
                          Supported: 'timestamp', 'counter'.
        """
        if scheme not in ['timestamp', 'counter']:
            raise ValueError(f"Unsupported versioning scheme: {scheme}")
        self.scheme = scheme
        self.counter = 1

    def get_versioned_filename(self, basename: str, extension: str) -> str:
        """
        Generates a versioned filename.

        Args:
            basename (str): The base name of the file (e.g., 'complaint').
            extension (str): The file extension (e.g., 'docx').

        Returns:
            str: A versioned filename.
        """
        if self.scheme == 'timestamp':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"{basename}_{timestamp}.{extension}"
        
        elif self.scheme == 'counter':
            versioned_name = f"{basename}_v{self.counter}.{extension}"
            self.counter += 1
            return versioned_name
        
        # Fallback for safety, though the constructor should prevent this.
        return f"{basename}.{extension}"

    def get_versioned_directory(self, basename: str) -> str:
        """
        Generates a versioned directory name.

        Args:
            basename (str): The base name for the directory (e.g., 'package').

        Returns:
            str: A versioned directory name.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{basename}_{timestamp}"

