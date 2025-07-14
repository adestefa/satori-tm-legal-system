"""
Core Output Management System for Monkey

Handles the organization, storage, and metadata of all generated documents.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class OutputManager:
    """
    Manages the output of generated documents, including file organization,
    metadata, and reporting.
    """

    def __init__(self, output_dir: Optional[str] = None):
        if output_dir:
            self.base_path = Path(output_dir)
        else:
            self.base_path = Path("outputs") / "monkey"
        
        self.processed_path = self.base_path / "processed"
        self.failed_path = self.base_path / "failed"
        self.reports_path = self.base_path / "reports"
        self.metadata_path = self.base_path / "metadata"
        self._setup_directories()
        self.logger = logging.getLogger(__name__)

    def _setup_directories(self):
        """Create the necessary output directories if they don't exist."""
        for path in [self.processed_path, self.failed_path, self.reports_path, self.metadata_path]:
            path.mkdir(parents=True, exist_ok=True)

    def save_output(self, document_name: str, content: str, success: bool, metadata: Optional[Dict[str, Any]] = None, overwrite_policy: str = "version"):
        """
        Saves the output of a document generation process.

        Args:
            document_name: The name of the document (e.g., "complaint.docx").
            content: The content of the document to save.
            success: A boolean indicating whether the generation was successful.
            metadata: Optional metadata to save alongside the document.
            overwrite_policy: The file overwrite policy ('version', 'overwrite', 'error').
            
        Returns:
            The actual file path where the document was saved, or None if failed.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        if success:
            output_path = self.processed_path / today / document_name
        else:
            output_path = self.failed_path / today / document_name
        
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            if overwrite_policy == "error":
                self.logger.error(f"File already exists: {output_path}")
                return
            elif overwrite_policy == "version":
                version = 1
                while output_path.with_name(f"{output_path.stem}_v{version}{output_path.suffix}").exists():
                    version += 1
                output_path = output_path.with_name(f"{output_path.stem}_v{version}{output_path.suffix}")
        
        try:
            self.logger.info(f"Attempting to save file to: {output_path}")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info(f"Successfully saved output to {output_path}")

            if metadata:
                self.save_metadata(document_name, metadata, success)
                
            return str(output_path)

        except IOError as e:
            self.logger.error(f"Error saving output to {output_path}: {e}")
            return None

    def save_metadata(self, document_name: str, metadata: Dict[str, Any], success: bool):
        """
        Saves metadata for a generated document.

        Args:
            document_name: The name of the document.
            metadata: The metadata to save.
            success: A boolean indicating whether the generation was successful.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        metadata_path = self.metadata_path / today / f"{document_name}.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        metadata["generation_date"] = datetime.now().isoformat()
        metadata["success"] = success

        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            self.logger.info(f"Successfully saved metadata to {metadata_path}")
        except IOError as e:
            self.logger.error(f"Error saving metadata to {metadata_path}: {e}")

    def generate_report(self, report_name: str, report_data: Dict[str, Any]):
        """
        Generates a report of the output management process.

        Args:
            report_name: The name of the report.
            report_data: The data to include in the report.
        """
        report_path = self.reports_path / f"{report_name}.json"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
            self.logger.info(f"Successfully generated report to {report_path}")
        except IOError as e:
            self.logger.error(f"Error generating report to {report_path}: {e}")

    def get_stats(self) -> Dict[str, int]:
        """
        Gets statistics about the output.

        Returns:
            A dictionary with the number of processed and failed documents.
        """
        processed_count = len(list(self.processed_path.glob("**/*")))
        failed_count = len(list(self.failed_path.glob("**/*")))
        return {"processed": processed_count, "failed": failed_count}

    def list_files(self, directory: str) -> list:
        """
        Lists the files in a given output directory.

        Args:
            directory: The directory to list files from.

        Returns:
            A list of files in the directory.
        """
        dir_path = self.base_path / directory
        return list(dir_path.glob('**/*'))

    def clear_output(self):
        """Clears the output directories."""
        for path in [self.processed_path, self.failed_path, self.reports_path, self.metadata_path]:
            for f in path.glob('**/*'):
                f.unlink()
