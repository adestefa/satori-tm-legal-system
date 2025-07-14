from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CaseStatus(str, Enum):
    """Represents the overall status of a case."""
    NEW = "New"
    PROCESSING = "Processing"
    PENDING_REVIEW = "Pending Review"
    GENERATING = "Generating"
    COMPLETE = "Complete"
    ERROR = "Error"

class CaseProgress(BaseModel):
    """Represents the granular, step-by-step progress of a case."""
    synced: bool = True  # If the case exists, it's synced.
    classified: bool = False
    extracted: bool = False
    reviewed: bool = False
    generated: bool = False

class FileProcessingStatus(str, Enum):
    """Represents the processing status of an individual file."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"

class FileProcessingResult(BaseModel):
    """Represents the processing result of an individual file."""
    name: str
    status: FileProcessingStatus = FileProcessingStatus.PENDING
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None

class FileMetadata(BaseModel):
    name: str
    path: str
    last_modified: datetime
    size_bytes: int

class Case(BaseModel):
    """The main model representing a single case."""
    id: str # A unique identifier, e.g., the folder name
    name: str
    status: CaseStatus = CaseStatus.NEW
    progress: CaseProgress = CaseProgress()
    files: List[FileMetadata] = []
    last_updated: datetime
    hydrated_json_path: Optional[str] = None
    complaint_html_path: Optional[str] = None
    last_complaint_path: Optional[str] = None
    processing_details: Optional[dict] = None
    file_processing_results: List[FileProcessingResult] = []
    summons_files: List[str] = []