from threading import Lock
import json
from pathlib import Path
from datetime import datetime
from config.settings import DATA_DIR, CONFIG_FILE

CACHE_FILE = DATA_DIR / "processed_files_cache.json"

class FileOrganizerState:
    def __init__(self):
        self.watched_folders = []
        self.categories = []
        self.observers = {}
        self.lock = Lock()
        self.processing_queue = []
        self.ollama_client = None
        self.whisper_model = None
        self.is_initialized = False
        self.bart_classifier = None
        
        # Default to False as requested
        self.auto_organize = False 
        
        self.processing_stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "by_type": {}
        }
        self.processing_progress = {}
        
        # Cache to track processed files
        self.processed_cache = self._load_cache()

    def _load_cache(self):
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_cache(self):
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.processed_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def update_file_status(self, file_path, status, mtime, settings_hash):
        with self.lock:
            self.processed_cache[str(file_path)] = {
                "mtime": mtime,
                "settings_hash": settings_hash,
                "status": status
            }
            self.save_cache()

    def update_folder_activity(self, folder_id):
        """Update the last activity timestamp for a watched folder"""
        if not folder_id: return
        with self.lock:
            for folder in self.watched_folders:
                if folder['id'] == folder_id:
                    folder['last_activity_timestamp'] = datetime.now().timestamp()

    def save_to_disk(self):
        """Persist current configuration (folders/categories) to disk"""
        try:
            config = {
                'watched_folders': self.watched_folders,
                'categories': self.categories,
                'auto_organize': self.auto_organize
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config state: {e}")

state = FileOrganizerState()