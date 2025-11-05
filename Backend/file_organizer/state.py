"""
Global State Management
"""

from threading import Lock


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
        self.auto_organize = False
        self.processing_stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "by_type": {}
        }


state = FileOrganizerState()