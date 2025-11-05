"""
File System Watcher
Monitors folders for new files and processes them automatically
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .state import state
from .file_processor import process_file
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FileHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, folder_id: int):
        self.folder_id = folder_id
        self.processing_delay = 1.0  # Wait 1 second before processing
        self.pending_files = {}
    
    def on_created(self, event):
        """Handle file creation"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        logger.info(f"New file detected: {file_path}")
        
        # Add to pending queue with timestamp
        self.pending_files[file_path] = time.time()
    
    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        # Update timestamp if already pending
        if file_path in self.pending_files:
            self.pending_files[file_path] = time.time()
    
    def process_pending_files(self):
        # Check if auto-organize is enabled
        if not state.auto_organize:
            # Clear pending files if auto-organize is disabled
            self.pending_files.clear()
            return
        
        # Check if this folder is active
        folder = next((f for f in state.watched_folders if f["id"] == self.folder_id), None)
        if not folder or folder.get("status") != "Active":
            # Don't process if folder is paused or not found
            self.pending_files.clear()
            return
        
        current_time = time.time()
        files_to_process = []
        
        for file_path, timestamp in list(self.pending_files.items()):
            if current_time - timestamp >= self.processing_delay:
                files_to_process.append(file_path)
                del self.pending_files[file_path]
        
        for file_path in files_to_process:
            if Path(file_path).exists():
                try:
                    process_file(file_path, self.folder_id)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}", exc_info=True)


def start_watching(folder_id: int, folder_path: str):
    """Start watching a folder for new files"""
    if folder_id in state.observers:
        logger.warning(f"Already watching folder {folder_id}")
        return
    
    if not Path(folder_path).exists():
        logger.error(f"Folder does not exist: {folder_path}")
        return
    
    event_handler = FileHandler(folder_id)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    state.observers[folder_id] = {
        "observer": observer,
        "handler": event_handler
    }
    
    logger.info(f"Watching folder: {folder_path}")
    
    # Start processing loop in background
    def processing_loop():
        while folder_id in state.observers:
            event_handler.process_pending_files()
            time.sleep(0.5)
    
    from threading import Thread
    thread = Thread(target=processing_loop, daemon=True)
    thread.start()


def stop_watching(folder_id: int):
    """Stop watching a folder"""
    if folder_id not in state.observers:
        return
    
    observer_data = state.observers[folder_id]
    observer_data["observer"].stop()
    observer_data["observer"].join()
    
    del state.observers[folder_id]
    logger.info(f"Stopped watching folder {folder_id}")


def start_all_watchers():
    """Start watching all active folders"""
    for folder in state.watched_folders:
        if folder.get("status") == "Active":
            start_watching(folder["id"], folder["path"])
