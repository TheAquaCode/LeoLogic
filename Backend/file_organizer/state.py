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
        self.bart_classifier = None  # BART-MNLI classifier for fast classification
        self.processing_stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "by_type": {}
        }
        # Per-folder processing progress state: { folder_id: { total, completed, failed, in_progress } }
        self.processing_progress = {}


state = FileOrganizerState()