from flask import Flask
from flask_cors import CORS
from .models import initialize_models
from .routes import register_routes, load_config
from .file_watcher import start_all_watchers
from pathlib import Path
import json
from config.settings import DATA_DIR


def create_file_organizer_app():
    """Create and configure the file organizer Flask app"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize AI models
    initialize_models()
    
    # Load configuration
    load_config()
    
    # Initialize history file if it doesn't exist
    HISTORY_FILE = DATA_DIR / "file_history.json"
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)
        print("📝 Initialized history file")
    
    # Register API routes
    register_routes(app)
    
    # Start file watchers
    start_all_watchers()
    
    print("📡 File Organizer API ready")
    print("Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/settings/auto-organize")
    print("  POST /api/settings/auto-organize")
    print("  GET  /api/history")
    print("  GET  /api/history/stats")
    print("  GET  /api/watched-folders")
    print("  POST /api/watched-folders")
    print("  POST /api/watched-folders/<id>/toggle")
    print("  GET  /api/categories")
    print("  POST /api/categories")
    print("  POST /api/process-folder/<id>")
    print("  POST /api/upload-and-process")
    print("  POST /api/rag/search")
    print("  GET  /api/stats")
    
    return app