"""
File Organizer Flask Application
"""

from flask import Flask
from flask_cors import CORS
from pathlib import Path
from .models import initialize_models
from .routes import register_routes, load_config
from .file_watcher import start_watching, start_queue_worker
from .state import state


def create_file_organizer_app():
    """Create and configure the file organizer Flask app"""
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration
    load_config()
    
    # Initialize AI models
    initialize_models()
    
    # Start background queue worker
    start_queue_worker()
    
    # Start watching all active folders
    for folder in state.watched_folders:
        if folder.get("status") == "Active" and Path(folder["path"]).exists():
            start_watching(folder["id"], folder["path"])
    
    # Register API routes
    register_routes(app)
    
    return app
