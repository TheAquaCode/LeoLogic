"""
File System Watcher & Scanner
Monitors folders for new files based on configured frequency.
"""

import time
import threading
import os
import stat
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config.settings import load_user_settings, get_settings_hash
from .state import state
from .file_processor import process_file
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Global scanner control
scanner_thread = None
stop_scanner = threading.Event()

def is_hidden(path_obj):
    """Check if file is hidden"""
    if path_obj.name.startswith('.'): return True
    if os.name == 'nt':
        try:
            attrs = path_obj.stat().st_file_attributes
            if attrs & stat.FILE_ATTRIBUTE_HIDDEN: return True
        except: pass
    return False

class FileHandler(FileSystemEventHandler):
    """Handle Real-time file system events"""
    
    def __init__(self, folder_id: int):
        self.folder_id = folder_id
        self.processing_delay = 1.0
        self.pending_files = {}
    
    def on_created(self, event):
        if event.is_directory: return
        self._queue_file(event.src_path)
    
    def on_modified(self, event):
        if event.is_directory: return
        self._queue_file(event.src_path)

    def _queue_file(self, file_path):
        if not state.auto_organize: return
        self.pending_files[file_path] = time.time()
    
    def process_pending_files(self):
        if not state.auto_organize:
            self.pending_files.clear()
            return
        
        current_time = time.time()
        files_to_process = []
        
        for file_path, timestamp in list(self.pending_files.items()):
            if current_time - timestamp >= self.processing_delay:
                files_to_process.append(file_path)
                del self.pending_files[file_path]
        
        current_settings_hash = get_settings_hash()
        
        for file_path in files_to_process:
            if should_process_file(file_path, current_settings_hash):
                try:
                    process_file(file_path, self.folder_id)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

def should_process_file(file_path: str, current_settings_hash: str) -> bool:
    """
    Determine if a file should be processed based on cache and settings.
    """
    path_obj = Path(file_path)
    if not path_obj.exists(): return False
        
    settings = load_user_settings() or {}
    
    # Check hidden
    if settings.get('skipHiddenFiles', True) and is_hidden(path_obj):
        return False

    str_path = str(file_path)
    current_mtime = path_obj.stat().st_mtime
    
    cached = state.processed_cache.get(str_path)
    
    if not cached: return True
        
    if cached.get('mtime', 0) != current_mtime: return True
    if cached.get('settings_hash') != current_settings_hash: return True
        
    return False

def start_watching(folder_id: int, folder_path: str):
    """Start real-time watchdog for a folder"""
    if folder_id in state.observers: return
    if not Path(folder_path).exists(): return
    
    event_handler = FileHandler(folder_id)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    state.observers[folder_id] = {
        "observer": observer,
        "handler": event_handler
    }
    
    def processing_loop():
        while folder_id in state.observers and not stop_scanner.is_set():
            event_handler.process_pending_files()
            time.sleep(0.5)
    
    threading.Thread(target=processing_loop, daemon=True).start()

def stop_watching(folder_id: int):
    if folder_id not in state.observers: return
    data = state.observers[folder_id]
    data["observer"].stop()
    data["observer"].join()
    del state.observers[folder_id]

def stop_all_watchers():
    for folder_id in list(state.observers.keys()):
        stop_watching(folder_id)

def start_all_watchers():
    settings = load_user_settings() or {}
    frequency = settings.get('scanFrequency', 'Hourly')
    
    stop_scanner.set()
    if scanner_thread:
        # scanner_thread.join(timeout=2) # Avoid blocking main thread too long
        pass
    stop_all_watchers()
    stop_scanner.clear()

    if not state.auto_organize: return
    if frequency == 'Manual': return

    if frequency == 'Real-time':
        for folder in state.watched_folders:
            if folder.get("status") == "Active":
                start_watching(folder["id"], folder["path"])
    else:
        interval_map = {'Every 5 minutes': 300, 'Hourly': 3600, 'Daily': 86400}
        interval = interval_map.get(frequency, 3600)
        
        global scanner_thread_obj
        scanner_thread_obj = threading.Thread(target=periodic_scan_loop, args=(interval,), daemon=True)
        scanner_thread_obj.start()

def periodic_scan_loop(interval):
    while not stop_scanner.is_set():
        if state.auto_organize:
            run_scan_pass()
        for _ in range(int(interval)):
            if stop_scanner.is_set(): break
            time.sleep(1)

def run_scan_pass():
    settings_hash = get_settings_hash()
    for folder in state.watched_folders:
        if folder.get("status") != "Active": continue
        path = Path(folder["path"])
        if not path.exists(): continue
        
        for file_path in path.iterdir():
            if file_path.is_file():
                if should_process_file(str(file_path), settings_hash):
                    try:
                        process_file(str(file_path), folder["id"])
                    except: pass