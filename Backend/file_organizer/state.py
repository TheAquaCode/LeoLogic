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
        self.bart_classifier = None
        self.is_initialized = False


state = FileOrganizerState()
