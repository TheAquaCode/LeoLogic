"""
File System Monitoring
"""

import time
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .state import state
from .file_processor import process_file


class FileHandler(FileSystemEventHandler):
    def __init__(self, folder_id):
        self.folder_id = folder_id
        super().__init__()
    
    def on_created(self, event):
        if not event.is_directory:
            with state.lock:
                state.processing_queue.append({
                    "file_path": event.src_path,
                    "folder_id": self.folder_id
                })
            print(f"📥 New file detected: {event.src_path}")


def start_watching(folder_id: int, folder_path: str):
    """Start watching a folder for new files"""
    if folder_id in state.observers:
        return
    handler = FileHandler(folder_id)
    observer = Observer()
    observer.schedule(handler, folder_path, recursive=False)
    observer.start()
    state.observers[folder_id] = observer
    print(f"👀 Watching folder: {folder_path}")


def stop_watching(folder_id: int):
    """Stop watching a folder"""
    if folder_id in state.observers:
        state.observers[folder_id].stop()
        state.observers[folder_id].join()
        del state.observers[folder_id]


def process_queue_worker():
    """Background worker that processes files from the queue"""
    while True:
        if state.processing_queue:
            with state.lock:
                item = state.processing_queue.pop(0)
            process_file(item["file_path"], item["folder_id"])
        time.sleep(1)


def start_queue_worker():
    """Start the background queue processing thread"""
    t = Thread(target=process_queue_worker, daemon=True)
    t.start()
