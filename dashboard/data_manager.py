import os
from datetime import datetime
from typing import List
from .models import Case, FileMetadata, CaseStatus, FileProcessingResult, FileProcessingStatus, CaseProgress

class DataManager:
    def __init__(self, case_directory: str, output_directory: str):
        self.case_directory = case_directory
        self.output_directory = output_directory
        self.cases: List[Case] = []
        self.scan_cases()

    def scan_cases(self):
        """Scans the case directory and updates the list of cases."""
        print(f"Scanning directory: {self.case_directory}")
        updated_cases = []
        for folder_name in os.listdir(self.case_directory):
            folder_path = os.path.join(self.case_directory, folder_name)
            if os.path.isdir(folder_path):
                case = self._create_case_from_folder(folder_path, folder_name)
                updated_cases.append(case)
        self.cases = updated_cases
        print(f"Scan complete. Found {len(self.cases)} cases.")

    def _create_case_from_folder(self, folder_path: str, folder_name: str) -> Case:
        """Creates a Case object from a folder path with smart state recovery."""
        files = []
        last_updated = datetime.fromtimestamp(os.path.getmtime(folder_path))
        for item_name in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item_name)
            if os.path.isfile(item_path):
                # Skip internal manifest files and system files
                if (item_name == 'processing_manifest.txt' or 
                    item_name.startswith('.') or 
                    item_name.lower().endswith('.ds_store')):
                    continue
                    
                file_stat = os.stat(item_path)
                file_last_modified = datetime.fromtimestamp(file_stat.st_mtime)
                if file_last_modified > last_updated:
                    last_updated = file_last_modified
                
                files.append(FileMetadata(
                    name=item_name,
                    path=item_path,
                    last_modified=file_last_modified,
                    size_bytes=file_stat.st_size
                ))
        
        # Smart state recovery: infer progress from existing output files
        progress = CaseProgress()  # Defaults: synced=True, others=False
        status = CaseStatus.NEW
        hydrated_json_path = None
        file_processing_results = []
        
        # Debug logging
        print(f"Processing case {folder_name}: initial status = {status}")
        
        try:
            # Check if case has been processed (look for case-specific output directory)
            case_output_dir = os.path.join(self.output_directory, folder_name)
            if os.path.exists(case_output_dir):
                # Look for generated JSON files in the case directory
                for output_file in os.listdir(case_output_dir):
                    # Match pattern like "hydrated_FCRA_{case_id}_..."
                    if output_file.endswith('.json') and 'hydrated' in output_file.lower():
                        hydrated_json_path = os.path.join(case_output_dir, output_file)
                        # If JSON exists, case has been processed
                        progress.classified = True
                        progress.extracted = True
                        status = CaseStatus.PENDING_REVIEW
                        
                        # Infer file processing results from successful completion
                        for file_meta in files:
                            if file_meta.name.lower().endswith(('.pdf', '.docx', '.txt')):
                                file_processing_results.append(
                                    FileProcessingResult(
                                        name=file_meta.name,
                                        status=FileProcessingStatus.SUCCESS,
                                        processed_at=datetime.fromtimestamp(os.path.getmtime(hydrated_json_path)),
                                        processing_time_seconds=0.5  # Estimated
                                    )
                                )
                        
                        # Check for generated complaint
                        complaint_html_path = os.path.join(case_output_dir, f"complaint_{folder_name}.html")
                        if os.path.exists(complaint_html_path):
                            progress.reviewed = True
                            progress.generated = True
                            status = CaseStatus.COMPLETE
                            
                        break
            
            # Also check main output directory for command-line generated files
            if not hydrated_json_path and os.path.exists(self.output_directory):
                for output_file in os.listdir(self.output_directory):
                    # Match pattern like "hydrated_FCRA_{case_id}_..." in main output dir
                    if (output_file.endswith('.json') and 'hydrated' in output_file.lower() and 
                        folder_name.lower() in output_file.lower()):
                        hydrated_json_path = os.path.join(self.output_directory, output_file)
                        # If JSON exists, case has been processed
                        progress.classified = True
                        progress.extracted = True
                        status = CaseStatus.PENDING_REVIEW
                        
                        # Infer file processing results from successful completion
                        for file_meta in files:
                            if file_meta.name.lower().endswith(('.pdf', '.docx', '.txt')):
                                file_processing_results.append(
                                    FileProcessingResult(
                                        name=file_meta.name,
                                        status=FileProcessingStatus.SUCCESS,
                                        processed_at=datetime.fromtimestamp(os.path.getmtime(hydrated_json_path)),
                                        processing_time_seconds=0.5  # Estimated
                                    )
                                )
                        break
        except Exception as e:
            # Ensure variables are always set even if file processing fails
            print(f"Error processing case {folder_name}: {e}")
            # Keep defaults: status = CaseStatus.NEW, hydrated_json_path = None, etc.
        
        return Case(
            id=folder_name,
            name=folder_name.replace('_', ' ').title(),
            files=files,
            last_updated=last_updated,
            status=status,
            progress=progress,
            hydrated_json_path=hydrated_json_path,
            file_processing_results=file_processing_results
        )

    def get_all_cases(self) -> List[Case]:
        return self.cases

    def get_case_by_id(self, case_id: str) -> Case | None:
        for case in self.cases:
            if case.id == case_id:
                return case
        return None

    def update_case_status(self, case_id: str, status: CaseStatus):
        case = self.get_case_by_id(case_id)
        if case:
            case.status = status
            print(f"Updated status for case '{case_id}' to '{status.value}'")
        else:
            print(f"Could not find case '{case_id}' to update status.")
    
    def initialize_file_processing_results(self, case_id: str):
        """Initialize file processing results for all files in a case."""
        case = self.get_case_by_id(case_id)
        if case:
            # Create processing results for all files
            case.file_processing_results = [
                FileProcessingResult(name=file.name, status=FileProcessingStatus.PENDING)
                for file in case.files
                if file.name.lower().endswith(('.pdf', '.docx', '.txt'))  # Only process certain file types
            ]
    
    def update_file_processing_status(self, case_id: str, filename: str, status: FileProcessingStatus, 
                                     error_message: str = None, processing_time: float = None):
        """Update the processing status of a specific file."""
        case = self.get_case_by_id(case_id)
        if case:
            for result in case.file_processing_results:
                if result.name == filename:
                    result.status = status
                    result.processed_at = datetime.now()
                    result.error_message = error_message
                    result.processing_time_seconds = processing_time
                    print(f"Updated file '{filename}' status to '{status.value}' for case '{case_id}'")
                    return
            print(f"File '{filename}' not found in processing results for case '{case_id}'")

