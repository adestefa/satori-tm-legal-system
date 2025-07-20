import time
import asyncio
import threading
from datetime import datetime
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .data_manager import DataManager

class CaseChangeHandler(FileSystemEventHandler):
    def __init__(self, data_manager: DataManager, connection_manager=None):
        self.data_manager = data_manager
        self.connection_manager = connection_manager
        # Add event queuing and throttling to prevent message corruption
        self.event_queue = deque()
        self.queue_lock = threading.Lock()
        self.last_broadcast_time = 0
        self.broadcast_interval = 0.5  # Minimum 500ms between broadcasts
        self.batch_timer = None

    def on_any_event(self, event):
        # This is a simple approach. A more robust solution would handle
        # specific events (on_created, on_deleted, on_modified) to avoid
        # full re-scans on every minor change. For now, this is sufficient.
        print(f"Detected file system event: {event.event_type} on {event.src_path}")
        self.data_manager.scan_cases()
        
        # Add event to queue instead of immediate broadcast to prevent race conditions
        if self.connection_manager:
            event_data = {
                "type": "file_system_change",
                "event_type": event.event_type,
                "path": event.src_path,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "is_directory": event.is_directory,
                    "src_path": event.src_path
                }
            }
            
            # Queue the event instead of immediate broadcast
            self._queue_event(event_data)

    def _queue_event(self, event_data):
        """Queue file system events and batch broadcast them to prevent WebSocket message corruption"""
        with self.queue_lock:
            self.event_queue.append(event_data)
            
            # Cancel any existing timer
            if self.batch_timer and self.batch_timer.is_alive():
                return  # Timer already running, let it handle the batch
            
            # Start new batch timer
            self.batch_timer = threading.Timer(self.broadcast_interval, self._batch_broadcast)
            self.batch_timer.daemon = True
            self.batch_timer.start()

    def _batch_broadcast(self):
        """Broadcast queued events in a single batch to prevent race conditions"""
        events_to_broadcast = []
        
        with self.queue_lock:
            # Get all queued events
            while self.event_queue:
                events_to_broadcast.append(self.event_queue.popleft())
        
        if not events_to_broadcast:
            return
        
        # Create batched event data
        if len(events_to_broadcast) == 1:
            # Single event - send as-is
            batched_event = events_to_broadcast[0]
        else:
            # Multiple events - batch them
            batched_event = {
                "type": "file_system_batch",
                "event_count": len(events_to_broadcast),
                "timestamp": datetime.now().isoformat(),
                "events": events_to_broadcast
            }
        
        # Use thread-safe broadcast
        def broadcast_in_thread():
            try:
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the broadcast
                loop.run_until_complete(self.connection_manager.broadcast_event(batched_event))
                loop.close()
                print(f"Successfully broadcast {len(events_to_broadcast)} file system events")
            except Exception as e:
                print(f"Failed to broadcast file system event batch: {e}")
        
        # Start the broadcast in a separate thread
        thread = threading.Thread(target=broadcast_in_thread)
        thread.daemon = True
        thread.start()
        
        # Update last broadcast time
        self.last_broadcast_time = time.time()


class FileWatcher:
    def __init__(self, directory: str, data_manager: DataManager, connection_manager=None):
        self.observer = Observer()
        self.directory = directory
        self.data_manager = data_manager
        self.connection_manager = connection_manager

    def start(self):
        event_handler = CaseChangeHandler(self.data_manager, self.connection_manager)
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()
        print(f"File watcher started on directory: {self.directory}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        print("File watcher stopped.")
