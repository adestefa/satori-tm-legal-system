import time
import asyncio
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .data_manager import DataManager

class CaseChangeHandler(FileSystemEventHandler):
    def __init__(self, data_manager: DataManager, connection_manager=None):
        self.data_manager = data_manager
        self.connection_manager = connection_manager

    def on_any_event(self, event):
        # This is a simple approach. A more robust solution would handle
        # specific events (on_created, on_deleted, on_modified) to avoid
        # full re-scans on every minor change. For now, this is sufficient.
        print(f"Detected file system event: {event.event_type} on {event.src_path}")
        self.data_manager.scan_cases()
        
        # Broadcast file system event via WebSocket
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
            
            # Use a thread-safe approach to broadcast the event
            import threading
            import asyncio
            
            def broadcast_in_thread():
                try:
                    # Create a new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Run the broadcast
                    loop.run_until_complete(self.connection_manager.broadcast_event(event_data))
                    loop.close()
                except Exception as e:
                    print(f"Failed to broadcast file system event: {e}")
            
            # Start the broadcast in a separate thread
            thread = threading.Thread(target=broadcast_in_thread)
            thread.daemon = True
            thread.start()


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
