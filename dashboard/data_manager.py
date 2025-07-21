import os
import json
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
        
        # Smart state recovery from manifest file
        progress = CaseProgress()
        status = CaseStatus.NEW
        hydrated_json_path = None
        file_processing_results = []
        file_status_dict = {}  # Track latest status for each file
        
        manifest_path = os.path.join(folder_path, 'processing_manifest.txt')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if not parts:
                            continue
                        
                        # Check for overall case status
                        if parts[0] == 'CASE_STATUS' and len(parts) > 1:
                            try:
                                status_str = parts[1].strip()
                                # Map manifest status values to enum values
                                status_map = {
                                    'PENDING_REVIEW': CaseStatus.PENDING_REVIEW,
                                    'COMPLETE': CaseStatus.COMPLETE,
                                    'PROCESSING': CaseStatus.PROCESSING,
                                    'ERROR': CaseStatus.ERROR,
                                    'NEW': CaseStatus.NEW
                                }
                                status = status_map.get(status_str, CaseStatus.NEW)
                                if status_str not in status_map:
                                    print(f"CRITICAL: Unknown status '{status_str}' in manifest. Defaulting to NEW.")
                            except Exception as e:
                                print(f"CRITICAL: Failed to parse status '{parts[1]}': {e}. Defaulting to NEW.")
                                pass # Keep default status if invalid
                        # Check for per-file status
                        elif len(parts) >= 2:
                            filename, file_status_str = parts[0], parts[1]
                            status_map = {
                                'success': FileProcessingStatus.SUCCESS,
                                'error': FileProcessingStatus.ERROR,
                                'processing': FileProcessingStatus.PROCESSING
                            }
                            file_status = status_map.get(file_status_str, FileProcessingStatus.PENDING)
                            # Keep only the latest status for each file
                            file_status_dict[filename] = FileProcessingResult(name=filename, status=file_status)
                
                # Convert file status dictionary to list with latest status only
                file_processing_results = list(file_status_dict.values())
                
                # Update progress based on final status
                if status == CaseStatus.PENDING_REVIEW:
                    progress.classified = True
                    progress.extracted = True
                elif status == CaseStatus.COMPLETE:
                    progress.classified = True
                    progress.extracted = True
                    progress.reviewed = True
                    progress.generated = True

            except Exception as e:
                print(f"Error parsing manifest for {folder_name}: {e}")

        # Find hydrated JSON path regardless of status
        case_output_dir = os.path.join(self.output_directory, folder_name)
        if os.path.exists(case_output_dir):
            for output_file in os.listdir(case_output_dir):
                if output_file.endswith('.json') and 'hydrated' in output_file.lower():
                    hydrated_json_path = os.path.join(case_output_dir, output_file)
                    break
        
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
        case_id = case_id.lower()
        for case in self.cases:
            if case.id.lower() == case_id:
                return case
        return None

    def update_case_status(self, case_id: str, status: CaseStatus):
        case = self.get_case_by_id(case_id)
        if case:
            case.status = status
            # The manifest is the single source of truth. No need to write a separate status file.
            print(f"Updated status for case '{case_id}' to '{status.value}' in memory.")
        else:
            print(f"Could not find case '{case_id}' to update status.")
    
    def initialize_file_processing_results(self, case_id: str):
        case = self.get_case_by_id(case_id)
        if case:
            case.file_processing_results = [
                FileProcessingResult(name=file.name, status=FileProcessingStatus.PENDING)
                for file in case.files
                if file.name.lower().endswith(('.pdf', '.docx', '.txt'))
            ]
    
    def update_file_processing_status(self, case_id: str, filename: str, status: FileProcessingStatus, 
                                     error_message: str = None, processing_time: float = None):
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