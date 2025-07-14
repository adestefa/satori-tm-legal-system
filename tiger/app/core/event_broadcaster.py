"""
Event Broadcasting System for Tiger Service
Sends real-time processing events to Dashboard via HTTP/WebSocket
"""

import json
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ProcessingEventBroadcaster:
    """Broadcasts file processing events to dashboard for real-time UI updates"""
    
    def __init__(self, dashboard_url: Optional[str] = None):
        self.dashboard_url = dashboard_url
        self.enabled = dashboard_url is not None
        
        if self.enabled:
            logger.info(f"Event broadcaster enabled for dashboard: {dashboard_url}")
        else:
            logger.info("Event broadcaster disabled - no dashboard URL provided")
    
    def _send_event(self, event_type: str, case_id: str, data: Dict[str, Any]) -> bool:
        """Send event to dashboard via HTTP POST"""
        if not self.enabled:
            return False
        
        try:
            event_payload = {
                "type": event_type,
                "case_id": case_id,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            response = requests.post(
                f"{self.dashboard_url}/api/processing-events",
                json=event_payload,
                timeout=2.0  # Quick timeout to avoid blocking processing
            )
            
            if response.status_code == 200:
                logger.debug(f"Event sent successfully: {event_type} for {case_id}")
                return True
            else:
                logger.warning(f"Failed to send event: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"Error sending event to dashboard: {str(e)}")
            return False
    
    def broadcast_file_start(self, case_id: str, file_name: str) -> bool:
        """Notify dashboard that file processing started"""
        return self._send_event("file_processing_start", case_id, {
            "file_name": file_name,
            "status": "processing"
        })
    
    def broadcast_file_success(self, case_id: str, file_name: str, metadata: Dict[str, Any]) -> bool:
        """Notify dashboard that file processing completed successfully"""
        return self._send_event("file_processing_success", case_id, {
            "file_name": file_name,
            "status": "success",
            "metadata": metadata
        })
    
    def broadcast_file_error(self, case_id: str, file_name: str, error: str) -> bool:
        """Notify dashboard that file processing failed"""
        return self._send_event("file_processing_error", case_id, {
            "file_name": file_name,
            "status": "error",
            "error": error
        })
    
    def broadcast_case_start(self, case_id: str, file_count: int) -> bool:
        """Notify dashboard that case processing started"""
        return self._send_event("case_processing_start", case_id, {
            "file_count": file_count,
            "status": "processing"
        })
    
    def broadcast_case_complete(self, case_id: str, hydrated_json_path: str, quality_score: float) -> bool:
        """Notify dashboard that entire case processing completed"""
        return self._send_event("case_processing_complete", case_id, {
            "status": "complete",
            "hydrated_json_path": hydrated_json_path,
            "quality_score": quality_score
        })
    
    def broadcast_case_error(self, case_id: str, error: str) -> bool:
        """Notify dashboard that case processing failed"""
        return self._send_event("case_processing_error", case_id, {
            "status": "error",
            "error": error
        })